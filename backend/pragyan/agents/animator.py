"""Manim pipeline: coder -> static check -> render -> (fixer + error memory) loop -> vision check.

Self-healing gets better over time: every error that a fix resolves is stored in MongoDB
(`error_memory`, keyed by a normalised signature) and replayed to the fixer next time.
"""
from __future__ import annotations

import asyncio
import difflib
import re
from pathlib import Path

from .. import llm, prompts
from ..config import settings
from ..db import db, error_signature, now
from ..engines import manim_runner, media
from ..engines.manim_kit import KIT_API_DOC
from ..spec import FrameCheck, ManimCode
from .base import AgentRun, Ctx

_render_sem: asyncio.Semaphore | None = None


def _sem() -> asyncio.Semaphore:
    global _render_sem
    if _render_sem is None:
        _render_sem = asyncio.Semaphore(2)
    return _render_sem


async def _recall(sig: str, error: str) -> tuple[str, int]:
    """Fetch fixes that worked for the same (or similar) error before."""
    hits: list[dict] = []
    try:
        hits = await db.errors.find({"signature": sig}, sort="count", limit=2)
        if not hits:
            cands = await db.errors.find({}, sort="count", limit=60)
            ratio = lambda d: difflib.SequenceMatcher(None, d.get("signature", ""), sig).ratio()
            hits = [d for d in sorted(cands, key=ratio, reverse=True)[:2] if ratio(d) > 0.55]
    except Exception:
        return "", 0
    if not hits:
        return "", 0
    lines = ["KNOWN FIXES FROM PAST RUNS (errors like this were solved by):"]
    for h in hits:
        lines.append(f"- error: {h['signature']}\n  fix: {h.get('fix_note', '')}\n  example change:\n{h.get('diff', '')[:700]}")
    return "\n".join(lines) + "\n", len(hits)


async def _remember(sig: str, error: str, bad: str, good: str, note: str):
    diff = "\n".join(list(difflib.unified_diff(bad.splitlines(), good.splitlines(), lineterm="", n=1))[2:40])
    try:
        existing = await db.errors.find_one({"signature": sig})
        if existing:
            await db.errors.update_one({"_id": existing["_id"]}, {"$inc": {"count": 1}, "$set": {"fix_note": note or existing.get("fix_note", ""), "diff": diff or existing.get("diff", ""), "updated_at": now()}})
        else:
            import uuid

            await db.errors.insert_one({"_id": uuid.uuid4().hex[:12], "signature": sig, "error": error[-1200:], "fix_note": note, "diff": diff, "count": 1, "created_at": now()})
    except Exception:
        pass


def _beats_brief(beats: list[dict], timings: list[dict], total: float) -> str:
    rows = []
    for i, (b, t) in enumerate(zip(beats, timings)):
        rows.append(f"BEAT {i + 1}: starts at {t['start']:.1f}s (constant START_{i + 1}), narration until {t['end']:.1f}s\n  narration: \"{b['narration']}\"\n  show: {b['visual']}")
    return "\n".join(rows) + f"\nTOTAL = {total:.1f}s\n(START_1..START_{len(beats)} and TOTAL are predefined float constants you can pass to sync().)"


def _with_timing(code: str, timings: list[dict], total: float) -> str:
    """Predefine the timing constants the coder is told about, so `sync(self, START_2)` always resolves."""
    consts = "".join(f"START_{i + 1} = {t['start']:.2f}\n" for i, t in enumerate(timings)) + f"TOTAL = {total:.2f}\n"
    head, _, body = code.partition("\n\n")
    return f"{head}\n{consts}\n{body}"


async def animate(ctx: Ctx, scene: dict, *, theme: str, quality: str, timings: list[dict], total: float, parent: str) -> dict:
    """Returns {'ok', 'video', 'code', 'attempts', 'transparent'}."""
    idx = scene["index"]
    workdir = ctx.dir / "manim" / f"scene_{idx + 1:02d}"
    beats = scene["authoring"]["beats"]
    transparent = theme != "paper"
    brief = _beats_brief(beats, timings, total)
    system = prompts.MANIM_CODER.replace("{kit_doc}", KIT_API_DOC)
    result = {"ok": False, "video": None, "code": "", "attempts": 0, "transparent": transparent}

    async with AgentRun(ctx, "animator", f"Manim Animator {idx + 1:02d}", parent=parent, detail=scene["authoring"].get("title", "")) as a:
        user = f"SCENE PURPOSE: {scene['purpose']}\nTITLE LABEL: {scene['authoring'].get('title', '')}\n\nTIMELINE:\n{brief}\n\nWrite the scene."
        gen = await llm.structured(ManimCode, system, user, model=settings.model_code, temperature=0.35, on_stats=a.stats, on_repair=a.repair)
        code = _with_timing(manim_runner.normalise(gen.code), timings, total)
        last_error = ""
        prev_code = ""
        critic_used = False
        seen: dict = {}
        for attempt in range(1, settings.manim_attempts + 2):
            ctx.check_cancel()
            ctx.metrics["manim"]["attempts"] += 1
            result["attempts"] = attempt
            problem = manim_runner.static_check(code)
            if problem:
                last_error = problem
                a.log(f"attempt {attempt}: static check — {problem}", level="warn")
            else:
                a.log(f"attempt {attempt}: rendering ({quality})…")
                async with _sem():
                    r = await manim_runner.render(code, workdir, theme=theme, quality=quality, transparent=transparent)
                if r.ok:
                    a.log(f"rendered in {r.seconds:.1f}s")
                    if last_error and prev_code and not last_error.startswith("VisualIssue"):
                        await _remember(error_signature(last_error), last_error, prev_code, code, gen.notes)
                        a.log("stored fix in error memory", level="info")
                    # Vision self-check on the clip (one corrective round max).
                    issue = None if critic_used or not ctx.options.get("critic", True) else await _check_clip(ctx, a, r.video, total)
                    if issue and attempt <= settings.manim_attempts:
                        critic_used = True
                        last_error = f"VisualIssue: {issue}"
                        a.log(f"critic: {issue}", level="warn")
                    else:
                        result.update(ok=True, video=r.video, code=code)
                        break
                else:
                    last_error = r.error
                    a.log(f"attempt {attempt} failed: {error_signature(r.error)}", level="warn")
            if attempt > settings.manim_attempts:
                break
            # ---- fixer --------------------------------------------------------
            sig = error_signature(last_error)
            memory, hits = await _recall(sig, last_error)
            if hits:
                ctx.metrics["manim"]["memory_hits"] += 1
                a.log(f"error memory: {hits} similar past fix(es) recalled")
            # Point at the exact failing line, and call out a repeated failure explicitly —
            # small models otherwise "fix" by returning the same line.
            hint = ""
            m_line = re.search(r"line (\d+)", last_error)
            if m_line:
                ln = int(m_line.group(1))
                lines = code.splitlines()
                if 0 < ln <= len(lines):
                    hint += f"\nFAILING LINE {ln}:  {lines[ln - 1].strip()}\n"
            if sig == seen.get("sig"):
                hint += "\nYOUR PREVIOUS FIX DID NOT WORK — the same error happened again. Rewrite the failing statement a DIFFERENT way (e.g. split it into two statements, call methods like .next_to() instead of passing them as keyword arguments, or remove the feature).\n"
            seen["sig"] = sig
            async with AgentRun(ctx, "fixer", "Error Resolver", parent=a.id, detail=sig[:60]) as fx:
                ctx.metrics["manim"]["fixes"] += 1
                fixed = await llm.structured(
                    ManimCode,
                    "You are an expert Manim CE debugger. Return only JSON.\n\n" + KIT_API_DOC,
                    prompts.MANIM_FIXER.format(error=last_error[-2000:] + hint, memory=memory, code=code),
                    model=settings.model_code,
                    temperature=0.2,
                    on_stats=fx.stats,
                    on_repair=fx.repair,
                )
                prev_code, code = code, _with_timing(manim_runner.normalise(fixed.code), timings, total)
                gen = fixed
                fx.done(fixed.notes[:120] or "patched")
        if result["ok"]:
            # Hold the last frame so the clip covers the narration.
            clip = Path(result["video"])
            dur = await media.duration(clip)
            if dur and dur < total - 0.2:
                ext = clip.with_name(f"scene_ext{clip.suffix}")
                try:
                    await media.extend_video(clip, ext, total - dur + 0.3, transparent)
                    result["video"] = ext
                except Exception as e:
                    a.log(f"could not extend clip: {e}", level="warn")
            a.done(f"ok after {result['attempts']} attempt(s)")
        else:
            a.done(f"failed after {result['attempts']} attempts — falling back")
    return result


async def _check_clip(ctx: Ctx, a: AgentRun, video: Path, total: float) -> str | None:
    frames = []
    for frac in (0.55, 0.92):
        out = video.with_name(f"check_{int(frac * 100)}.png")
        f = await media.frame_at(video, max(0.2, total * frac), out)
        if f:
            frames.append(f)
    if not frames:
        return None
    try:
        issues = []
        for f in frames:
            r = await llm.structured(FrameCheck, prompts.MANIM_CRITIC, "Judge this frame.", images=[f], model=settings.model_vision, temperature=0.0, on_stats=a.stats)
            ctx.metrics["critic"]["checked"] += 1
            if r.text_cut_off or r.overlapping or r.score <= 4:
                issues.append(r.notes or ("text cut off" if r.text_cut_off else "overlapping elements"))
        return "; ".join(issues) if issues else None
    except Exception:
        return None
