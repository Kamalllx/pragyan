"""Drive motion/scripts/render.mjs and stream its JSON-lines progress."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Callable

from ..config import settings


class RenderError(RuntimeError):
    pass


async def _run(args: list[str], on_event: Callable[[dict], None] | None) -> list[dict]:
    script = settings.motion_dir / "scripts" / "render.mjs"
    proc = await asyncio.create_subprocess_exec(
        settings.node_bin, str(script), *args,
        cwd=str(settings.motion_dir), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, limit=2**22,
    )
    events: list[dict] = []
    err_tail: list[str] = []

    async def read_err():
        assert proc.stderr
        async for line in proc.stderr:
            err_tail.append(line.decode("utf8", "replace").rstrip())
            del err_tail[:-40]

    t = asyncio.create_task(read_err())
    assert proc.stdout
    async for raw in proc.stdout:
        line = raw.decode("utf8", "replace").strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(ev)
        if on_event:
            on_event(ev)
    await proc.wait()
    await t
    errs = [e["error"] for e in events if "error" in e]
    if proc.returncode != 0 or errs:
        raise RenderError((errs[0] if errs else "\n".join(err_tail))[-2000:])
    return events


async def render_video(spec_path: Path, out: Path, *, scale: float = 1.0, on_event=None, gl: str = "angle") -> Path:
    args = ["--props", str(spec_path), "--out", str(out), "--scale", str(scale), "--gl", gl]
    if settings.render_concurrency:
        args += ["--concurrency", str(settings.render_concurrency)]
    await _run(args, on_event)
    return out


async def render_stills(spec_path: Path, frames: list[int], out_dir: Path, *, scale: float = 0.5, gl: str = "angle") -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    events = await _run(["--props", str(spec_path), "--stills", ",".join(str(f) for f in frames), "--still-dir", str(out_dir), "--scale", str(scale), "--gl", gl], None)
    return [Path(e["output"]) for e in events if e.get("stage") == "still"]


async def render_film(out: Path, on_event=None) -> Path:
    await _run(["--composition", "PragyanFilm", "--out", str(out)], on_event)
    return out
