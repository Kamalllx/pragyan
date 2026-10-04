"""MongoDB persistence with a transparent local-JSON fallback (offline still works).

Database: `pragyan_ai` (configurable). Collections:
  jobs            one document per video job (inputs, plan, storyboard, spec, outputs, metrics, events)
  steering_packs  reusable generic "steering" settings — curated + learned from good runs
  error_memory    Manim error signature -> fix that worked (self-healing gets better over time)
  feedback        ratings + notes
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings

log = logging.getLogger("pragyan.db")


def now() -> datetime:
    return datetime.now(timezone.utc)


def _jsonable(o: Any) -> Any:
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_jsonable(v) for v in o]
    return o


class _LocalCollection:
    """Tiny subset of the Mongo API backed by a JSON file."""

    def __init__(self, path: Path):
        self.path = path
        self._lock = asyncio.Lock()
        self._docs: dict[str, dict] = {}
        if path.exists():
            try:
                self._docs = {d["_id"]: d for d in json.loads(path.read_text("utf8"))}
            except Exception:
                self._docs = {}

    def _flush(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([_jsonable(d) for d in self._docs.values()], ensure_ascii=False), "utf8")

    @staticmethod
    def _match(doc: dict, q: dict) -> bool:
        for k, v in q.items():
            cur: Any = doc
            for part in k.split("."):
                cur = cur.get(part) if isinstance(cur, dict) else None
            if isinstance(v, dict) and "$in" in v:
                if cur not in v["$in"]:
                    return False
            elif cur != v:
                return False
        return True

    async def insert_one(self, doc: dict):
        async with self._lock:
            self._docs[doc["_id"]] = doc
            self._flush()

    async def find_one(self, q: dict, projection: dict | None = None):
        for d in self._docs.values():
            if self._match(d, q):
                return dict(d)
        return None

    async def find(self, q: dict | None = None, *, sort: str | None = None, desc: bool = True, limit: int = 100, projection: dict | None = None):
        docs = [dict(d) for d in self._docs.values() if self._match(d, q or {})]
        if sort:
            docs.sort(key=lambda d: str(d.get(sort, "")), reverse=desc)
        if projection:
            drop = [k for k, v in projection.items() if v == 0]
            for d in docs:
                for k in drop:
                    d.pop(k, None)
        return docs[:limit]

    async def update_one(self, q: dict, update: dict, upsert: bool = False):
        async with self._lock:
            target = next((d for d in self._docs.values() if self._match(d, q)), None)
            if target is None:
                if not upsert:
                    return
                target = {**{k: v for k, v in q.items() if "." not in k}}
                self._docs[target["_id"]] = target
            for k, v in update.get("$set", {}).items():
                cur = target
                parts = k.split(".")
                for p in parts[:-1]:
                    cur = cur.setdefault(p, {})
                cur[parts[-1]] = v
            for k, v in update.get("$push", {}).items():
                arr = target.setdefault(k, [])
                if isinstance(v, dict) and "$each" in v:
                    arr.extend(v["$each"])
                    if "$slice" in v:
                        target[k] = arr[v["$slice"] :] if v["$slice"] < 0 else arr[: v["$slice"]]
                else:
                    arr.append(v)
            for k, v in update.get("$inc", {}).items():
                target[k] = target.get(k, 0) + v
            self._flush()

    async def delete_one(self, q: dict):
        async with self._lock:
            for k, d in list(self._docs.items()):
                if self._match(d, q):
                    del self._docs[k]
                    break
            self._flush()


class _MongoCollection:
    def __init__(self, col):
        self.col = col

    async def insert_one(self, doc: dict):
        await self.col.insert_one(doc)

    async def find_one(self, q: dict, projection: dict | None = None):
        return await self.col.find_one(q, projection)

    async def find(self, q: dict | None = None, *, sort: str | None = None, desc: bool = True, limit: int = 100, projection: dict | None = None):
        cur = self.col.find(q or {}, projection)
        if sort:
            cur = cur.sort(sort, -1 if desc else 1)
        return await cur.limit(limit).to_list(length=limit)

    async def update_one(self, q: dict, update: dict, upsert: bool = False):
        await self.col.update_one(q, update, upsert=upsert)

    async def delete_one(self, q: dict):
        await self.col.delete_one(q)


class Database:
    def __init__(self):
        self.mode = "unconnected"
        self.jobs: Any = None
        self.steering: Any = None
        self.errors: Any = None
        self.feedback: Any = None

    async def connect(self):
        if settings.mongodb_uri:
            try:
                from pymongo import AsyncMongoClient

                client = AsyncMongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=8000, tz_aware=True)
                await client.admin.command("ping")
                db = client[settings.mongodb_db]
                self.jobs = _MongoCollection(db["jobs"])
                self.steering = _MongoCollection(db["steering_packs"])
                self.errors = _MongoCollection(db["error_memory"])
                self.feedback = _MongoCollection(db["feedback"])
                await db["jobs"].create_index("created_at")
                await db["error_memory"].create_index("signature")
                self.mode = f"mongodb:{settings.mongodb_db}"
                log.info("Connected to MongoDB (%s)", settings.mongodb_db)
                return
            except Exception as e:  # pragma: no cover - network dependent
                log.warning("MongoDB unavailable (%s) — falling back to local JSON store", e)
        base = settings.storage_dir / "localdb"
        self.jobs = _LocalCollection(base / "jobs.json")
        self.steering = _LocalCollection(base / "steering_packs.json")
        self.errors = _LocalCollection(base / "error_memory.json")
        self.feedback = _LocalCollection(base / "feedback.json")
        self.mode = "local-json"


db = Database()


_NUM = re.compile(r"\d+")
_QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")


def error_signature(err: str) -> str:
    """Normalise an error so similar failures share a key (line numbers, names stripped)."""
    lines = [l.strip() for l in err.strip().splitlines() if l.strip()]
    tail = next((l for l in reversed(lines) if re.match(r"^[A-Za-z_.]*(Error|Exception)\b", l)), lines[-1] if lines else "")
    tail = _QUOTED.sub("'…'", tail)
    tail = _NUM.sub("N", tail)
    return tail[:200]
