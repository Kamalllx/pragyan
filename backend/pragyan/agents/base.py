"""Job context + agent run bookkeeping (every agent is visible live in the UI graph)."""
from __future__ import annotations

import itertools
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..config import settings
from ..db import db, now
from ..events import bus

_counter = itertools.count(1)


@dataclass
class Ctx:
    job_id: str
    dir: Path
    prompt: str
    options: dict
    files: list[dict] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)  # understanding, steering, knowledge, outline ...
    scenes: list[dict] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=lambda: {"timings": {}, "llm": {"calls": 0, "tokens": 0, "seconds": 0.0}, "manim": {"attempts": 0, "fixes": 0, "fallbacks": 0, "memory_hits": 0}, "critic": {"checked": 0, "revised": 0}})
    cancelled: bool = False

    # -- events -------------------------------------------------------------
    def emit(self, type_: str, **data):
        return bus.publish(self.job_id, type_, **data)

    async def save(self, **fields):
        fields["updated_at"] = now()
        await db.jobs.update_one({"_id": self.job_id}, {"$set": fields})

    def url(self, p: Path) -> str:
        rel = Path(p).resolve().relative_to(settings.storage_dir.resolve()).as_posix()
        return f"{settings.public_base}/media/{rel}"

    def rel(self, p: Path) -> str:
        return "/media/" + Path(p).resolve().relative_to(settings.storage_dir.resolve()).as_posix()

    def stage(self, name: str, progress: float, label: str = ""):
        self.data["stage"] = name
        self.emit("stage", stage=name, progress=progress, label=label)

    def check_cancel(self):
        if self.cancelled:
            raise JobCancelled()


class JobCancelled(Exception):
    pass


class AgentRun:
    """async with AgentRun(ctx, "solver", "Solver", parent="orchestrator") as a: ..."""

    def __init__(self, ctx: Ctx, kind: str, label: str, *, parent: str | None = "orchestrator", detail: str = "", agent_id: str | None = None):
        self.ctx = ctx
        self.kind = kind
        self.label = label
        self.parent = parent
        self.detail = detail
        self.id = agent_id or f"{kind}-{next(_counter)}"
        self.t0 = 0.0
        self.result_summary = ""

    async def __aenter__(self) -> "AgentRun":
        self.t0 = time.perf_counter()
        self.ctx.emit("agent.spawn", agent=self.id, kind=self.kind, label=self.label, parent=self.parent, detail=self.detail)
        return self

    async def __aexit__(self, et, ev, tb):
        dt = round(time.perf_counter() - self.t0, 1)
        if et is None:
            self.ctx.emit("agent.done", agent=self.id, seconds=dt, summary=self.result_summary)
        elif et.__name__ == "JobCancelled":
            self.ctx.emit("agent.error", agent=self.id, seconds=dt, error="cancelled")
        else:
            self.ctx.emit("agent.error", agent=self.id, seconds=dt, error=f"{et.__name__}: {str(ev)[:300]}", trace="".join(traceback.format_exception(et, ev, tb))[-1500:])
        return False

    def log(self, msg: str, **data):
        self.ctx.emit("agent.log", agent=self.id, message=msg, **data)

    def stats(self, s: dict):
        m = self.ctx.metrics["llm"]
        m["calls"] += 1
        m["tokens"] += s.get("tokens", 0)
        m["seconds"] += s.get("seconds", 0)
        self.ctx.emit("agent.llm", agent=self.id, **s)

    def repair(self, err: str):
        self.ctx.emit("agent.log", agent=self.id, message=f"self-repair: {err}", level="warn")

    def done(self, summary: str):
        self.result_summary = summary
