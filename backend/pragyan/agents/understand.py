"""Ingest (text / image / PDF / code files), research digest, and intent analysis."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .. import llm, prompts
from ..config import settings
from ..spec import ImageReading, IntentAnalysis, Research
from .base import AgentRun, Ctx

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
TEXT_EXT = {".txt", ".md", ".py", ".js", ".ts", ".tsx", ".java", ".c", ".cpp", ".go", ".rs", ".json", ".csv", ".html", ".css", ".sql", ".yaml", ".yml", ".tex"}


def _prep_image(p: Path) -> Path:
    """Downscale huge images so the vision model is fast and within context."""
    try:
        from PIL import Image

        im = Image.open(p)
        if max(im.size) > 1600:
            im.thumbnail((1600, 1600))
            out = p.with_name(p.stem + "_vlm.png")
            im.convert("RGB").save(out)
            return out
    except Exception:
        pass
    return p


async def ingest(ctx: Ctx) -> dict:
    readings: list[dict] = []
    docs: list[dict] = []
    for f in ctx.files:
        p = Path(f["path"])
        ext = p.suffix.lower()
        if ext in IMAGE_EXT:
            async with AgentRun(ctx, "vision", "Vision Reader", parent="ingest", detail=p.name) as a:
                a.log(f"Reading image {p.name} with {settings.model_vision}")
                r = await llm.structured(
                    ImageReading,
                    prompts.INGEST_IMAGE,
                    f"User request: {ctx.prompt or '(none — infer from the image)'}\nDescribe and transcribe this image.",
                    images=[_prep_image(p)],
                    model=settings.model_vision,
                    temperature=0.1,
                    on_stats=a.stats,
                    on_repair=a.repair,
                )
                d = r.model_dump() | {"file": p.name, "url": ctx.url(p)}
                readings.append(d)
                a.done(f"{'problem' if r.contains_problem else 'image'} · {r.subject_guess}")
        elif ext == ".pdf":
            async with AgentRun(ctx, "reader", "Document Reader", parent="ingest", detail=p.name) as a:
                from pypdf import PdfReader

                reader = PdfReader(str(p))
                text = "\n".join((pg.extract_text() or "") for pg in reader.pages[:40])
                text = re.sub(r"\n{3,}", "\n\n", text)
                docs.append({"file": p.name, "pages": len(reader.pages), "text": text[:24000]})
                a.done(f"{len(reader.pages)} pages · {len(text):,} chars")
        elif ext in TEXT_EXT:
            async with AgentRun(ctx, "reader", "Document Reader", parent="ingest", detail=p.name) as a:
                text = p.read_text("utf8", errors="replace")
                docs.append({"file": p.name, "pages": 1, "text": text[:24000], "code": ext not in {".txt", ".md"}})
                a.done(f"{len(text):,} chars")
    return {"readings": readings, "docs": docs}


def material_summary(ingested: dict, limit: int = 3500) -> str:
    parts = []
    for r in ingested.get("readings", []):
        parts.append(f"[IMAGE {r['file']}] {r['description']}\nText in image: {r['transcribed_text'][:1200]}")
    for d in ingested.get("docs", []):
        parts.append(f"[DOCUMENT {d['file']}, {d['pages']} pages]\n{d['text'][:limit]}")
    return "\n\n".join(parts)


async def research(ctx: Ctx, ingested: dict) -> Research | None:
    if not ingested.get("docs") and not ingested.get("readings"):
        return None
    async with AgentRun(ctx, "researcher", "Researcher", detail="digesting material") as a:
        material = material_summary(ingested, limit=14000)
        r = await llm.structured(
            Research,
            prompts.RESEARCH,
            f"USER REQUEST: {ctx.prompt}\n\nMATERIAL:\n{material}",
            temperature=0.2,
            on_stats=a.stats,
            on_repair=a.repair,
        )
        a.done(f"{len(r.key_points)} key points · {len(r.facts_and_figures)} figures")
        return r


async def analyse_intent(ctx: Ctx, ingested: dict) -> IntentAnalysis:
    async with AgentRun(ctx, "intent", "Intent Analyst", detail="what video should this be?") as a:
        opts = ctx.options
        hints = []
        if opts.get("audience"):
            hints.append(f"Audience is fixed by the user: {opts['audience']}")
        if ingested.get("docs"):
            hints.append("User attached document(s).")
        if any(r.get("contains_problem") for r in ingested.get("readings", [])):
            hints.append("An attached image contains a problem to solve.")
        user = (
            f"USER REQUEST:\n{ctx.prompt or '(no text — see material)'}\n\n"
            f"ATTACHED MATERIAL:\n{material_summary(ingested, 2500) or '(none)'}\n\n"
            f"HINTS: {' '.join(hints) or 'none'}\nTarget length: about {opts.get('target_seconds', 75)} seconds."
        )
        r = await llm.structured(IntentAnalysis, prompts.INTENT, user, temperature=0.15, on_stats=a.stats, on_repair=a.repair)
        # Deterministic guard-rails on top of the model's judgement.
        agents = set(r.agents)
        if r.needs_solving or r.intent == "solve_problem":
            agents.add("solver")
        if r.intent in ("explain_concept", "how_to", "compare", "story_history", "revision_notes", "code_walkthrough"):
            agents.add("explainer")
        if ingested.get("docs") or ingested.get("readings"):
            agents.add("researcher")
        if r.needs_math and opts.get("allow_manim", True):
            agents.add("visualizer")
        if r.needs_code:
            agents.add("coder")
        if opts.get("audience"):
            r.audience_level = opts["audience"]
        r.agents = sorted(agents)
        a.log(r.reasoning)
        a.done(f"{r.intent} · {r.domain} · {r.audience_level}")
        return r


def compact(obj) -> str:
    if obj is None:
        return ""
    if hasattr(obj, "model_dump"):
        obj = obj.model_dump()
    return json.dumps(obj, ensure_ascii=False)
