"""ffmpeg/ffprobe helpers + caption/transcript writers."""
from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


async def _run(*args: str) -> tuple[int, str, str]:
    p = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, err = await p.communicate()
    return p.returncode or 0, out.decode("utf8", "replace"), err.decode("utf8", "replace")


async def duration(path: Path) -> float:
    code, out, _ = await _run(FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path))
    try:
        return float(json.loads(out)["format"]["duration"])
    except Exception:
        return 0.0


async def extend_video(src: Path, dst: Path, seconds: float, transparent: bool) -> Path:
    """Hold the last frame so a Manim clip covers its narration."""
    if transparent:
        args = [FFMPEG, "-y", "-loglevel", "error", "-c:v", "libvpx-vp9", "-i", str(src), "-vf", f"tpad=stop_mode=clone:stop_duration={seconds:.2f}",
                "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "30", "-deadline", "realtime", "-cpu-used", "8", "-an", str(dst)]
    else:
        args = [FFMPEG, "-y", "-loglevel", "error", "-i", str(src), "-vf", f"tpad=stop_mode=clone:stop_duration={seconds:.2f}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "veryfast", "-an", str(dst)]
    code, _, err = await _run(*args)
    if code != 0:
        raise RuntimeError(err[-600:])
    return dst


async def frame_at(video: Path, t: float, out: Path, width: int = 960) -> Path | None:
    code, _, _ = await _run(FFMPEG, "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf", f"scale={width}:-2", str(out))
    return out if code == 0 and out.exists() else None


def _ts(sec: float, sep: str = ",") -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"


def write_captions(cues: list[tuple[float, float, str]], srt: Path, vtt: Path):
    srt_lines, vtt_lines = [], ["WEBVTT", ""]
    for i, (a, b, text) in enumerate(cues, 1):
        srt_lines += [str(i), f"{_ts(a)} --> {_ts(b)}", text, ""]
        vtt_lines += [f"{_ts(a, '.')} --> {_ts(b, '.')}", text, ""]
    srt.write_text("\n".join(srt_lines), "utf8")
    vtt.write_text("\n".join(vtt_lines), "utf8")
