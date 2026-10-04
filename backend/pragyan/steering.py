"""Steering packs: reusable *generic* direction — never the content itself.

A pack says *how* a kind of video should be made (arc, visual vocabulary, pacing,
theme, narration rules). Packs are YAML files (steering/core, steering/packs,
steering/learned) mirrored into MongoDB, plus packs learned from highly-rated jobs.

kind:
  core     always applied (global craft rules)
  pack     one primary pack is chosen per job (best match)
  overlay  stacked on top when matched (e.g. audience=kid, revision mode)
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import llm
from .config import settings
from .db import db, now

log = logging.getLogger("pragyan.steering")

_EMB_CACHE: dict[str, list[float]] = {}


def _read_yaml_dir(d: Path, source: str) -> list[dict]:
    out = []
    if not d.exists():
        return out
    for p in sorted(d.glob("*.y*ml")):
        try:
            doc = yaml.safe_load(p.read_text("utf8")) or {}
            doc.setdefault("id", p.stem)
            doc["source"] = source
            doc["path"] = str(p.relative_to(settings.steering_dir.parent))
            out.append(doc)
        except Exception as e:
            log.warning("bad steering file %s: %s", p, e)
    return out


async def load_all() -> list[dict]:
    packs: dict[str, dict] = {}
    for sub, src in (("core", "core"), ("packs", "curated"), ("learned", "learned")):
        for p in _read_yaml_dir(settings.steering_dir / sub, src):
            packs[p["id"]] = p
    try:
        for p in await db.steering.find({}, limit=500):
            p = dict(p)
            p["id"] = p.pop("_id")
            p.setdefault("source", "db")
            if p["id"] not in packs or p.get("source") in ("learned", "user"):
                packs[p["id"]] = p
    except Exception:
        pass
    return [p for p in packs.values() if p.get("enabled", True)]


async def sync_to_db():
    """Mirror file packs into MongoDB so the UI/db always has the full catalogue."""
    for p in await load_all():
        if p.get("source") in ("core", "curated", "learned"):
            doc = {k: v for k, v in p.items() if k != "id"}
            doc["updated_at"] = now()
            await db.steering.update_one({"_id": p["id"]}, {"$set": doc}, upsert=True)


async def _emb(text: str) -> list[float] | None:
    key = hashlib.sha1(text.encode()).hexdigest()
    if key in _EMB_CACHE:
        return _EMB_CACHE[key]
    try:
        e = (await llm.embed([text]))[0]
        _EMB_CACHE[key] = e
        return e
    except Exception:
        return None


@dataclass
class Profile:
    packs: list[dict] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)
    arc: list[str] = field(default_factory=list)
    prefer: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)
    narration_rules: list[str] = field(default_factory=list)
    tone: str = ""
    do: list[str] = field(default_factory=list)
    dont: list[str] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "packs": [{"id": p["id"], "name": p.get("name", p["id"]), "kind": p.get("kind", "pack"), "score": round(self.scores.get(p["id"], 0), 2)} for p in self.packs],
            "settings": self.settings,
            "arc": self.arc,
            "prefer": self.prefer,
            "avoid": self.avoid,
        }

    def as_prompt(self, include_arc: bool = True) -> str:
        parts = []
        if include_arc and self.arc:
            parts.append("RECOMMENDED ARC (adapt, don't copy blindly):\n" + "\n".join(f"- {a}" for a in self.arc))
        if self.prefer:
            parts.append("PREFERRED VISUALS: " + ", ".join(self.prefer))
        if self.avoid:
            parts.append("AVOID VISUALS: " + ", ".join(self.avoid))
        if self.tone:
            parts.append(f"NARRATION TONE: {self.tone}")
        if self.narration_rules:
            parts.append("NARRATION RULES:\n" + "\n".join(f"- {r}" for r in self.narration_rules))
        if self.do:
            parts.append("DO:\n" + "\n".join(f"- {r}" for r in self.do))
        if self.dont:
            parts.append("DON'T:\n" + "\n".join(f"- {r}" for r in self.dont))
        return "\n\n".join(parts)


def _as_text(x: Any) -> str:
    if isinstance(x, dict):  # YAML turns "a: b" list items into dicts
        return "; ".join(f"{k}: {v}" for k, v in x.items())
    return str(x)


def _uniq(xs: list[Any]) -> list[str]:
    seen, out = set(), []
    for x in map(_as_text, xs):
        k = x.strip().lower()
        if k and k not in seen:
            seen.add(k)
            out.append(x.strip())
    return out


def _rule_score(p: dict, intent: dict, query: str) -> float:
    m = p.get("match", {}) or {}
    s = 0.0
    if intent.get("intent") in (m.get("intents") or []):
        s += 3
    if intent.get("domain") in (m.get("domains") or []):
        s += 2
    if intent.get("audience_level") in (m.get("audiences") or []):
        s += 2.5
    q = query.lower()
    hits = sum(1 for k in (m.get("keywords") or []) if re.search(rf"\b{re.escape(k.lower())}", q))
    s += min(2.0, hits * 0.6)
    return s


async def select(intent: dict, query: str, forced: list[str] | None = None) -> Profile:
    packs = await load_all()
    core = [p for p in packs if p.get("kind") == "core"]
    cands = [p for p in packs if p.get("kind", "pack") == "pack"]
    overlays = [p for p in packs if p.get("kind") == "overlay"]

    qv = await _emb(f"{intent.get('intent')} {intent.get('domain')} {intent.get('topic', '')}. {query[:600]}")
    scores: dict[str, float] = {}
    for p in cands + overlays:
        s = _rule_score(p, intent, query)
        if qv is not None and p.get("description"):
            pv = await _emb(p["description"])
            if pv is not None:
                s += 3.0 * max(0.0, llm.cosine(qv, pv) - 0.35)
        s += float(p.get("priority", 0)) / 100.0
        if p.get("source") == "learned":
            s += 0.4 * float(p.get("rating", 4) - 3)
        scores[p["id"]] = s

    chosen: list[dict] = list(core)
    if forced:
        chosen += [p for p in packs if p["id"] in forced and p not in chosen]
    else:
        ranked = sorted(cands, key=lambda p: scores.get(p["id"], 0), reverse=True)
        if ranked:
            chosen.append(ranked[0])
        chosen += [o for o in overlays if scores.get(o["id"], 0) >= 2.5]

    prof = Profile(packs=chosen, scores=scores)
    # Merge: later (more specific) packs override settings; lists accumulate.
    for p in chosen:
        prof.settings.update({k: v for k, v in (p.get("settings") or {}).items() if v is not None})
        if p.get("arc") and p.get("kind", "pack") == "pack":
            prof.arc = [_as_text(a) for a in p["arc"]]
        vis = p.get("visuals") or {}
        prof.prefer += vis.get("prefer") or []
        prof.avoid += vis.get("avoid") or []
        nar = p.get("narration") or {}
        if nar.get("tone"):
            prof.tone = nar["tone"]
        prof.narration_rules += nar.get("rules") or []
        rules = p.get("rules") or {}
        prof.do += rules.get("do") or []
        prof.dont += rules.get("dont") or []
    prof.prefer = _uniq(prof.prefer)
    prof.avoid = [a for a in _uniq(prof.avoid) if a not in prof.prefer]
    prof.narration_rules = _uniq(prof.narration_rules)
    prof.do = _uniq(prof.do)
    prof.dont = _uniq(prof.dont)
    return prof


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48] or "pack"


async def save_pack(pack: dict, *, to_file: bool = True) -> dict:
    pid = pack.get("id") or slugify(pack.get("name", "pack"))
    pack["id"] = pid
    if to_file:
        sub = "learned" if pack.get("source") == "learned" else "packs"
        path = settings.steering_dir / sub / f"{pid}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        body = {k: v for k, v in pack.items() if k not in ("path", "_id", "updated_at", "created_at")}
        path.write_text(yaml.safe_dump(body, sort_keys=False, allow_unicode=True), "utf8")
    doc = {k: v for k, v in pack.items() if k != "id"}
    doc["updated_at"] = now()
    await db.steering.update_one({"_id": pid}, {"$set": doc}, upsert=True)
    return pack


async def delete_pack(pid: str):
    await db.steering.delete_one({"_id": pid})
    for sub in ("learned", "packs"):
        p = settings.steering_dir / sub / f"{pid}.yaml"
        if p.exists():
            p.unlink()
