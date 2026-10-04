"""Film Editor: cut narration for time before anything is voiced.

Designers are good at content and bad at counting words. Instead of rejecting their
work over and over (slow on a local model), the editor projects the runtime of the
whole cut and trims only the scenes that overrun their share — the way a real editor
cuts a film to length.
"""
from __future__ import annotations

from pydantic import BaseModel

from .. import llm
from .base import AgentRun, Ctx

EFF_WPS = 2.5  # measured Kokoro rate at speed 1.0 incl. joins (af_heart ~2.6-2.9, deeper voices ~2.2)
GAP = 0.24  # gap between narration segments
SCENE_OVERHEAD = 1.0  # lead-in + tail + hold, seconds
TRANSITION = 0.6  # seconds of overlap between consecutive scenes
QUIZ_PAUSE = 3.2


class _Cut(BaseModel):
    lines: list[str]


EDIT_SYSTEM = """You are the film editor of an explainer video. The narration for one scene runs too long.
Rewrite the lines so the TOTAL is about {target} words.
Rules:
- Return exactly {n} lines, in the same order. Line k must still introduce on-screen item k.
- A line that is empty must stay empty.
- Keep every fact and the meaning; cut filler, repetition and throat-clearing first.
- Spoken words only: no symbols, no LaTeX, no markdown.
- Keep it natural and warm — tighter, not robotic.
- Keep the language of the original lines (do not translate)."""


def _words(s: str) -> int:
    return len((s or "").split())


def projected_seconds(scene: dict, speed: float = 1.0) -> float:
    segs = scene.get("segments") or []
    words = sum(_words(s) for s in segs)
    gaps = GAP * sum(1 for s in segs if s and s.strip())
    extra = QUIZ_PAUSE if scene.get("type") == "quiz" else 0.0
    return words / (EFF_WPS * speed) + gaps + SCENE_OVERHEAD + extra


def projected_total(scenes: list[dict], speed: float = 1.0) -> float:
    return sum(projected_seconds(s, speed) for s in scenes) - TRANSITION * max(0, len(scenes) - 1)


async def cut_for_time(ctx: Ctx, scenes: list[dict], plan_seconds: list[int], target: float, speed: float = 1.0) -> dict:
    """Mutates scene['segments'] in place. Returns a small report for the UI/metrics."""
    before = projected_total(scenes, speed)
    report = {"target": target, "before": round(before, 1), "after": round(before, 1), "cut_scenes": []}
    async with AgentRun(ctx, "editor", "Film Editor", detail=f"target {int(target)} s") as a:
        a.log(f"projected runtime {before:.0f} s for a {target:.0f} s target")
        if before <= target * 1.1:
            a.done(f"on time · {before:.0f} s")
            return report
        total_plan = sum(plan_seconds) or 1
        need = before - target
        # Each scene's fair share of the target, proportional to the storyboard's plan.
        shares = [target * p / total_plan + TRANSITION for p in plan_seconds]
        order = sorted(range(len(scenes)), key=lambda i: projected_seconds(scenes[i], speed) - shares[i], reverse=True)
        for i in order:
            if need <= 0.5:
                break
            s = scenes[i]
            segs = list(s.get("segments") or [])
            over = projected_seconds(s, speed) - shares[i]
            if over < 1.0 or s.get("type") in ("title",) and over < 2.5:
                continue
            words_now = sum(_words(x) for x in segs)
            non_empty = sum(1 for x in segs if x and x.strip())
            floor = 5 * non_empty  # every item still deserves a real sentence
            # Remove what this scene overruns, but never more than the job still needs.
            cut_secs = min(over, need + 1.0)
            target_words = max(floor, int(words_now - cut_secs * EFF_WPS * speed))
            if target_words >= words_now * 0.9:
                continue

            tries = {"n": 0}

            def ok(c: _Cut, n=len(segs), tw=target_words, src=segs, wn=words_now, tries=tries):
                tries["n"] += 1
                if len(c.lines) != n:
                    return f"return exactly {n} lines (you returned {len(c.lines)})"
                for k, (old, new) in enumerate(zip(src, c.lines)):
                    if not (old or "").strip() and (new or "").strip():
                        return f"line {k + 1} must stay empty"
                    if (old or "").strip() and not (new or "").strip():
                        return f"line {k + 1} must not be empty"
                total = sum(_words(x) for x in c.lines)
                if tries["n"] >= 3 and total < wn * 0.9:
                    return None  # last round: any real cut beats no cut
                if total > tw * 1.25 + 3:
                    return f"total is {total} words; cut to about {tw}"
                return None

            try:
                cut = await llm.structured(
                    _Cut,
                    EDIT_SYSTEM.format(target=target_words, n=len(segs)),
                    "LINES:\n" + "\n".join(f"{k + 1}. {x or '(empty)'}" for k, x in enumerate(segs)),
                    temperature=0.3,
                    validate=ok,
                    on_stats=a.stats,
                    on_repair=a.repair,
                )
            except llm.LLMError as e:
                a.log(f"scene {i + 1}: could not cut ({e}); leaving as is", level="warn")
                continue
            lines = [("" if not (o or "").strip() else n.strip()) for o, n in zip(segs, cut.lines)]
            saved = projected_seconds(s, speed)
            s["segments"] = lines
            saved -= projected_seconds(s, speed)
            need -= saved
            if s.get("type") == "manim" and s.get("authoring", {}).get("beats"):
                for b, line in zip(s["authoring"]["beats"], lines):
                    b["narration"] = line
            report["cut_scenes"].append({"scene": i + 1, "words": [words_now, sum(_words(x) for x in lines)], "saved_s": round(saved, 1)})
            a.log(f"scene {i + 1} ({s.get('type')}): {words_now} → {sum(_words(x) for x in lines)} words, −{saved:.1f} s")
            ctx.emit("scene.update", scene={k: s.get(k) for k in ("index", "id", "chapter", "purpose", "type", "status", "visual", "segments")})
        after = projected_total(scenes, speed)
        report["after"] = round(after, 1)
        a.done(f"{before:.0f} s → {after:.0f} s")
    return report
