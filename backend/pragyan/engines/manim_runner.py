"""Static checks, cheap auto-fixes and sandboxed execution for generated Manim scenes."""
from __future__ import annotations

import ast
import asyncio
import os
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from ..config import settings
from ..theme import THEMES
from .manim_kit import KIT_TEMPLATE

BANNED_MODULES = {"os", "sys", "subprocess", "shutil", "socket", "requests", "urllib", "pathlib", "http", "ctypes", "pickle", "importlib", "builtins"}
BANNED_CALLS = {"open", "eval", "exec", "__import__", "compile", "input", "breakpoint", "globals", "locals"}

# Legacy / hallucinated APIs that small models love -> modern Manim CE.
AUTOFIXES: list[tuple[str, str]] = [
    (r"\bShowCreation\b", "Create"),
    (r"\bTextMobject\b", "Tex"),
    (r"\bTexMobject\b", "MathTex"),
    (r"\bFadeInFrom(Down|Up|Left|Right)?\b", "FadeIn"),
    (r"\bFadeOutAndShift\b", "FadeOut"),
    (r"\bGrowFromCenter\b", "GrowFromCenter"),
    (r"\.get_graph\(", ".plot("),
    (r"\bShowCreationThenDestruction\b", "ShowPassingFlash"),
    (r"\bCONFIG\s*=\s*\{[^}]*\}", ""),
    (r"\bself\.camera\.background_color\s*=.*", ""),
    (r"\bconfig\.background_color\s*=.*", ""),
    (r"\bWHITE\b", "TEXT"),
    (r"(?<![\w.])Text\((.*?)font\s*=\s*['\"][^'\"]*['\"]\s*,?", r"Text(\1"),
]


@dataclass
class ManimResult:
    ok: bool
    video: Path | None
    error: str
    seconds: float
    code: str


def kit_source(theme_name: str, transparent: bool) -> str:
    th = THEMES.get(theme_name, THEMES["cosmos"])
    return KIT_TEMPLATE.format(
        bg=th["bg"], text=th["text"], muted=th["muted"], accent=th["accent"], accent2=th["accent2"],
        good=th["good"], bad=th["bad"], font=th.get("manim_font", "Segoe UI"), transparent="True" if transparent else "False",
    )


def normalise(code: str) -> str:
    code = re.sub(r"^```(?:python)?\s*|\s*```$", "", code.strip(), flags=re.M)
    for pat, rep in AUTOFIXES:
        code = re.sub(pat, rep, code)
    lines = [l for l in code.splitlines() if not re.match(r"^\s*(from manim import|import manim|from pragyan_kit import)", l)]
    code = "\n".join(lines)
    # Rename whatever Scene subclass the model wrote to the expected entry point.
    m = re.search(r"class\s+(\w+)\s*\(\s*\w*Scene\s*\)", code)
    if m and m.group(1) != "PragyanScene":
        code = re.sub(rf"\b{re.escape(m.group(1))}\b", "PragyanScene", code)
    return "from manim import *\nfrom pragyan_kit import *\n\n" + code.strip() + "\n"


def static_check(code: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"SyntaxError: {e.msg} (line {e.lineno}): {(e.text or '').strip()}"
    has_scene = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name.split(".")[0] for a in node.names] if isinstance(node, ast.Import) else [(node.module or "").split(".")[0]]
            bad = [m for m in mods if m in BANNED_MODULES]
            if bad:
                return f"SecurityError: importing {bad[0]} is not allowed in scenes"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
            return f"SecurityError: calling {node.func.id}() is not allowed in scenes"
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return "SecurityError: dunder attribute access is not allowed"
        if isinstance(node, ast.ClassDef) and node.name == "PragyanScene":
            has_scene = True
            if not any(isinstance(b, ast.FunctionDef) and b.name == "construct" for b in node.body):
                return "StructureError: PragyanScene must define construct(self)"
    if not has_scene:
        return "StructureError: define `class PragyanScene(Scene)` with a construct(self) method"
    return None


def summarise_error(stderr: str) -> str:
    """Pull the useful part out of Manim's rich traceback."""
    clean = re.sub(r"\x1b\[[0-9;]*m", "", stderr)
    clean = re.sub(r"[│╭╮╰╯─┃]+", " ", clean)
    lines = [l.rstrip() for l in clean.splitlines() if l.strip()]
    err_idx = max((i for i, l in enumerate(lines) if re.search(r"(Error|Exception)\b", l)), default=len(lines) - 1)
    ctx = lines[max(0, err_idx - 14) : err_idx + 3]
    # Also keep "scene.py:NN" hints for the fixer.
    where = [l.strip() for l in lines if "scene.py" in l][-3:]
    out = "\n".join(where + ["..."] + ctx)
    if "latex" in clean.lower() and ("error" in clean.lower()):
        tex_err = [l for l in lines if l.strip().startswith("!") or "LaTeX Error" in l]
        if tex_err:
            out += "\nLaTeX: " + " | ".join(tex_err[:3])
    return out[-2500:]


async def render(code: str, workdir: Path, *, theme: str, quality: str, transparent: bool, timeout: int | None = None) -> ManimResult:
    workdir = workdir.resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "pragyan_kit.py").write_text(kit_source(theme, transparent), "utf8")
    (workdir / "scene.py").write_text(code, "utf8")
    media = workdir / "media"
    if media.exists():
        shutil.rmtree(media, ignore_errors=True)
    q = {"draft": "l", "standard": "m", "high": "h"}.get(quality, "m")
    args = [settings.python_bin, "-m", "manim", "render", f"-q{q}", "--disable_caching", "--media_dir", str(media), "-o", "scene"]
    if transparent:
        args += ["--transparent", "--format", "webm"]
    args += ["scene.py", "PragyanScene"]
    env = {**os.environ, "PYTHONPATH": str(workdir), "PYTHONIOENCODING": "utf-8", "MIKTEX_ENABLE_INSTALLER": "1"}
    t0 = time.perf_counter()
    proc = await asyncio.create_subprocess_exec(*args, cwd=str(workdir), env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout or settings.manim_timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return ManimResult(False, None, f"TimeoutError: scene took longer than {timeout or settings.manim_timeout}s to render — simplify (fewer objects, shorter run_time, avoid huge loops)", time.perf_counter() - t0, code)
    dt = time.perf_counter() - t0
    vids = [p for p in media.rglob("scene.*") if p.suffix in (".mp4", ".webm", ".mov") and "partial" not in str(p)]
    if proc.returncode == 0 and vids:
        return ManimResult(True, vids[0], "", dt, code)
    text = (err or b"").decode("utf8", "replace") + "\n" + (out or b"").decode("utf8", "replace")
    return ManimResult(False, None, summarise_error(text) or "Unknown Manim failure", dt, code)
