"""Run the solver's verification snippet (sympy/math) in a locked-down subprocess."""
from __future__ import annotations

import ast
import asyncio
import os
import tempfile
from pathlib import Path

from ..config import settings

ALLOWED = {"sympy", "math", "fractions", "decimal", "itertools", "functools", "statistics", "numpy", "cmath", "random"}


def check(code: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"SyntaxError: {e.msg} line {e.lineno}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in ALLOWED:
                    return f"import {a.name} not allowed"
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED:
                return f"from {node.module} import not allowed"
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"open", "exec", "eval", "__import__", "input", "compile"}:
            return f"{node.func.id}() not allowed"
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return "dunder access not allowed"
    return None


async def run_python(code: str, timeout: int = 25) -> tuple[bool, str]:
    problem = check(code)
    if problem:
        return False, problem
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "verify.py"
        p.write_text(code, "utf8")
        env = {"PATH": os.environ.get("PATH", ""), "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""), "PYTHONIOENCODING": "utf-8"}
        proc = await asyncio.create_subprocess_exec(
            settings.python_bin, "-I", str(p), cwd=d, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return False, "timeout"
    if proc.returncode != 0:
        return False, (err or b"").decode("utf8", "replace")[-800:]
    return True, (out or b"").decode("utf8", "replace").strip()[-800:]
