"""Turn a highly-rated job into a reusable, generic steering pack (the system learns your taste)."""
from __future__ import annotations

from .. import llm, prompts, steering
from ..spec import SteeringDraft
from .base import AgentRun, Ctx


async def distill(ctx: Ctx, job: dict, rating: int, notes: str = "") -> dict:
    async with AgentRun(ctx, "distiller", "Steering Distiller", parent=None, detail="learning from this video") as a:
        intent = job.get("data", {}).get("intent", {})
        outline = job.get("data", {}).get("outline", {})
        arc = [f"{s.get('chapter')}: {s.get('visual')} - {s.get('purpose')}" for s in outline.get("scenes", [])]
        user = (
            f"VIDEO TYPE: {intent.get('intent')} · DOMAIN: {intent.get('domain')} · AUDIENCE: {intent.get('audience_level')}\n"
            f"THEME USED: {job.get('spec', {}).get('meta', {}).get('theme')}\n"
            f"SCENE ARC THAT WORKED:\n" + "\n".join(arc) + f"\n\nUSER RATING: {rating}/5. USER NOTES: {notes or 'none'}"
        )
        d = await llm.structured(SteeringDraft, prompts.DISTILL, user, temperature=0.3, on_stats=a.stats, on_repair=a.repair)
        pack = {
            "id": f"learned-{steering.slugify(d.name)}",
            "name": d.name,
            "kind": "pack",
            "source": "learned",
            "priority": 45,
            "rating": rating,
            "description": d.description,
            # A learned arc is proven only for the kind of video it came from — pin it to that intent.
            "match": {"intents": [intent.get("intent")] if intent.get("intent") else d.intents, "domains": d.domains, "keywords": d.keywords},
            "settings": {"theme": d.theme, "target_seconds": job.get("options", {}).get("target_seconds", 75)},
            "arc": d.arc,
            "narration": {"rules": d.narration_rules},
            "rules": {"do": d.do, "dont": d.dont},
            "learned_from": job["_id"],
        }
        await steering.save_pack(pack)
        a.done(f"saved steering pack “{d.name}”")
        return pack
