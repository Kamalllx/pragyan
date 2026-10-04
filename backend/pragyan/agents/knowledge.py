"""Explainer (pedagogy brief) and Solver (+ independent sympy verification loop)."""
from __future__ import annotations

import re

from pydantic import BaseModel

from .. import llm, prompts
from ..config import settings
from ..engines import sandbox
from ..spec import ConceptBrief, IntentAnalysis, Solution
from .base import AgentRun, Ctx
from .understand import material_summary


async def explain(ctx: Ctx, intent: IntentAnalysis, ingested: dict, research=None) -> ConceptBrief:
    async with AgentRun(ctx, "explainer", "Explainer", detail=intent.topic) as a:
        user = (
            f"TOPIC: {intent.topic}\nKEY QUESTION: {intent.key_question}\nAUDIENCE: {intent.audience_level}\n"
            f"SUBTOPICS: {', '.join(intent.subtopics)}\nUSER REQUEST: {ctx.prompt}\n"
        )
        if research is not None:
            user += f"\nSOURCE DIGEST (stay faithful to it):\n{research.model_dump_json()}\n"
        elif ingested.get("readings"):
            user += f"\nMATERIAL:\n{material_summary(ingested, 2000)}\n"
        b = await llm.structured(ConceptBrief, prompts.EXPLAINER, user, temperature=0.5, on_stats=a.stats, on_repair=a.repair)
        a.log(f"Analogy: {b.analogy}")
        a.done(f"{len(b.mechanism_steps)} mechanism steps · {len(b.takeaways)} takeaways")
        return b


class _Agree(BaseModel):
    agree: bool
    reason: str


def _nums(s: str) -> list[float]:
    out = []
    for m in re.findall(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", s.replace(",", "")):
        try:
            out.append(float(m))
        except ValueError:
            pass
    return out


async def _judge(answer: str, output: str, on_stats) -> tuple[bool, str]:
    a, o = _nums(answer), _nums(output)
    if a and o and any(abs(x - y) <= 1e-6 + 1e-3 * abs(x) for x in a[:3] for y in o):
        return True, "numeric match"
    norm = lambda s: re.sub(r"[\s*]", "", s.lower())
    if norm(answer) and norm(answer) in norm(output):
        return True, "symbolic match"
    r = await llm.structured(
        _Agree,
        "You compare a claimed answer with a program's printed output. Decide whether they are mathematically equivalent.",
        f"CLAIMED ANSWER: {answer}\nPROGRAM OUTPUT: {output}",
        temperature=0.0,
        on_stats=on_stats,
    )
    return r.agree, r.reason


async def solve(ctx: Ctx, intent: IntentAnalysis, ingested: dict) -> tuple[Solution, dict]:
    async with AgentRun(ctx, "solver", "Solver", detail=intent.topic) as a:
        problem = ctx.prompt
        mat = material_summary(ingested, 2500)
        user = f"PROBLEM / REQUEST:\n{problem}\n\n" + (f"MATERIAL (e.g. the photographed problem):\n{mat}\n" if mat else "")
        verification: dict = {"status": "unverified", "attempts": 0}
        feedback = ""
        sol: Solution | None = None
        for attempt in range(3):
            msg = user if not feedback else user + "\n\n" + prompts.SOLVER_RETRY.format(feedback=feedback)
            a.log("thinking…" if attempt == 0 else f"re-solving (attempt {attempt + 1})")
            sol = await llm.structured(
                Solution, prompts.SOLVER, msg, think=settings.solver_think and attempt == 0, temperature=0.2, on_stats=a.stats, on_repair=a.repair
            )
            verification["attempts"] = attempt + 1
            if not sol.verification_code.strip():
                verification.update(status="unverified", note="no verification code")
                break
            async with AgentRun(ctx, "verifier", "Verifier", parent=a.id, detail="sympy check") as v:
                ok, out = await sandbox.run_python(sol.verification_code)
                v.log(f"output: {out[:200]}")
                if not ok:
                    feedback = f"verification code crashed: {out}"
                    v.done("code error")
                    continue
                agree, why = await _judge(sol.final_answer + " " + sol.final_answer_latex, out, v.stats)
                verification.update(output=out[:400], reason=why)
                if agree:
                    verification["status"] = "verified"
                    v.done(f"verified ✓ ({why})")
                    break
                feedback = f"program printed {out!r} but you claimed {sol.final_answer!r} ({why})"
                v.done("mismatch")
        else:
            verification["status"] = "disputed"
        assert sol is not None
        a.done(f"answer: {sol.final_answer[:60]} · {verification['status']}")
        return sol, verification
