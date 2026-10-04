"""Visual critic: render one still per scene (when everything has revealed) and judge it with the vision model."""
from __future__ import annotations

import json
from pathlib import Path

from .. import llm, prompts
from ..config import settings
from ..engines import remotion_runner
from ..spec import FrameCheck
from .base import AgentRun, Ctx


def reveal_frames(spec: dict) -> list[int]:
    T = spec.get("transitionFrames", 18)
    t = 0
    out = []
    for s in spec["scenes"]:
        d = s["durationInFrames"]
        segs = s.get("segments") or []
        last_cue = max((g["start"] for g in segs), default=0)
        f = max(last_cue + 36, int(d * 0.72))
        f = min(f, d - T - 4)
        out.append(t + max(10, f))
        t += d - T
    return out


async def review(ctx: Ctx, spec: dict, spec_path: Path, skip: set[int]) -> dict[int, str]:
    """Returns {scene_index: problem} for scenes that need revision."""
    problems: dict[int, str] = {}
    async with AgentRun(ctx, "critic", "Visual Critic", detail="render → inspect") as a:
        frames = reveal_frames(spec)
        targets = [(i, f) for i, f in enumerate(frames) if i not in skip]
        if not targets:
            a.done("nothing to review")
            return problems
        a.log(f"rendering {len(targets)} review stills")
        # Judge the scene, not the captions (mid-sentence caption pages look "cut off" to a critic).
        review_spec = {**spec, "meta": {**spec["meta"], "captions": False}}
        review_path = spec_path.with_name("spec_review.json")
        review_path.write_text(json.dumps(review_spec, ensure_ascii=False), "utf8")
        stills = await remotion_runner.render_stills(review_path, [f for _, f in targets], ctx.dir / "review", scale=0.5)
        by_frame = {int(p.stem.split("-")[-1]): p for p in stills}
        for i, f in targets:
            p = by_frame.get(f)
            if not p:
                continue
            ctx.emit("artifact", kind="review_still", scene=i, url=ctx.url(p))
            try:
                r = await llm.structured(FrameCheck, prompts.FRAME_CRITIC, "Judge this frame.", images=[p], model=settings.model_vision, temperature=0.0, on_stats=a.stats)
            except Exception as e:
                a.log(f"scene {i + 1}: critic failed ({e})", level="warn")
                continue
            ctx.metrics["critic"]["checked"] += 1
            verdict = f"scene {i + 1}: {r.score}/10 — {r.notes}"
            if r.text_cut_off or r.overlapping or r.empty_or_blank or r.score <= 4:
                issue = ", ".join(x for x, flag in (("text is cut off", r.text_cut_off), ("elements overlap", r.overlapping), ("frame looks empty", r.empty_or_blank)) if flag) or r.notes
                problems[i] = f"{issue}. {r.notes}"
                a.log(verdict + " → revise", level="warn")
            else:
                a.log(verdict)
        ctx.data.setdefault("critic", {})["frames"] = {str(i): str(by_frame.get(f, "")) for i, f in targets}
        a.done(f"{len(targets) - len(problems)}/{len(targets)} scenes passed")
    return problems
