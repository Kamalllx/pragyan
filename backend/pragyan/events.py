"""Per-job event bus: live SSE fan-out + persisted history (for replay after refresh)."""
from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from typing import Any

from .db import db


class EventBus:
    def __init__(self):
        self._subs: dict[str, set[asyncio.Queue]] = defaultdict(set)
        self._history: dict[str, list[dict]] = defaultdict(list)
        self._seq: dict[str, int] = defaultdict(int)
        self._pending: dict[str, list[dict]] = defaultdict(list)
        self._flushers: dict[str, asyncio.Task] = {}

    def publish(self, job_id: str, type_: str, **data: Any) -> dict:
        self._seq[job_id] += 1
        ev = {"seq": self._seq[job_id], "ts": time.time(), "type": type_, **data}
        self._history[job_id].append(ev)
        if len(self._history[job_id]) > 2000:
            self._history[job_id] = self._history[job_id][-1500:]
        for q in list(self._subs[job_id]):
            try:
                q.put_nowait(ev)
            except asyncio.QueueFull:
                pass
        self._pending[job_id].append(ev)
        if job_id not in self._flushers or self._flushers[job_id].done():
            try:
                self._flushers[job_id] = asyncio.get_running_loop().create_task(self._flush_later(job_id))
            except RuntimeError:
                pass
        return ev

    async def _flush_later(self, job_id: str):
        await asyncio.sleep(1.5)
        batch, self._pending[job_id] = self._pending[job_id], []
        if batch and db.jobs is not None:
            try:
                await db.jobs.update_one({"_id": job_id}, {"$push": {"events": {"$each": batch, "$slice": -600}}})
            except Exception:
                pass

    def history(self, job_id: str) -> list[dict]:
        return list(self._history.get(job_id, []))

    def seed(self, job_id: str, events: list[dict]):
        if not self._history.get(job_id) and events:
            self._history[job_id] = list(events)
            self._seq[job_id] = max((e.get("seq", 0) for e in events), default=0)

    def subscribe(self, job_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=5000)
        self._subs[job_id].add(q)
        return q

    def unsubscribe(self, job_id: str, q: asyncio.Queue):
        self._subs[job_id].discard(q)


bus = EventBus()
