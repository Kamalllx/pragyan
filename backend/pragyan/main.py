"""Pragyan AI — local API server.

  uvicorn pragyan.main:app --port 8000
"""
from __future__ import annotations

import asyncio
import json
import logging
import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from . import llm, pipeline, steering
from .agents.base import Ctx
from .agents.distiller import distill
from .config import settings
from .db import db, now
from .engines import tts
from .events import bus
from .spec import JobOptions
from .theme import THEME_NOTES, THEMES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("pragyan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    try:
        await steering.sync_to_db()
    except Exception as e:
        log.warning("steering sync failed: %s", e)
    # Jobs that were mid-flight when the server stopped can't resume; mark them.
    try:
        for j in await db.jobs.find({"status": "running"}, limit=50, projection={"_id": 1}):
            await db.jobs.update_one({"_id": j["_id"]}, {"$set": {"status": "failed", "error": "server restarted during the job"}})
    except Exception:
        pass
    log.info("Pragyan AI ready · db=%s · models=%s/%s", db.mode, settings.model_reason, settings.model_vision)
    yield


app = FastAPI(title="Pragyan AI", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")] + ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
settings.storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(settings.storage_dir)), name="media")

LIST_PROJECTION = {"events": 0, "scenes": 0, "spec": 0, "data.knowledge": 0, "data.ingested": 0}


def _clean(doc: dict | None) -> dict | None:
    if not doc:
        return doc
    out = json.loads(json.dumps(doc, default=str))
    out["id"] = out.pop("_id", None)
    return out


# ---------------------------------------------------------------------------
# jobs
# ---------------------------------------------------------------------------
@app.post("/api/jobs")
async def create_job(prompt: str = Form(""), options: str = Form("{}"), files: list[UploadFile] = File(default=[])):
    try:
        opts = JobOptions.model_validate(json.loads(options or "{}"))
    except Exception as e:
        raise HTTPException(400, f"bad options: {e}")
    if not prompt.strip() and not files:
        raise HTTPException(400, "Give Pragyan a prompt, a question, an image or a document.")
    job_id = uuid.uuid4().hex[:10]
    jdir = settings.jobs_dir / job_id / "inputs"
    jdir.mkdir(parents=True, exist_ok=True)
    saved = []
    for f in files:
        name = Path(f.filename or "file").name
        dest = jdir / name
        with dest.open("wb") as out:
            shutil.copyfileobj(f.file, out)
        ext = dest.suffix.lower()
        kind = "image" if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"} else "pdf" if ext == ".pdf" else "text"
        saved.append({"name": name, "kind": kind, "path": str(dest), "url": "/media/" + dest.relative_to(settings.storage_dir).as_posix(), "size": dest.stat().st_size})
    doc = {
        "_id": job_id,
        "created_at": now(),
        "updated_at": now(),
        "status": "queued",
        "stage": "queued",
        "title": (prompt.strip()[:80] or (saved[0]["name"] if saved else "Untitled")),
        "input": {"prompt": prompt.strip(), "options": opts.model_dump(), "files": saved},
        "events": [],
    }
    await db.jobs.insert_one(doc)
    asyncio.create_task(pipeline.run_job(job_id))
    return {"id": job_id}


@app.get("/api/jobs")
async def list_jobs(limit: int = 60):
    docs = await db.jobs.find({}, sort="created_at", limit=limit, projection=LIST_PROJECTION)
    return [_clean(d) for d in docs]


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    doc = await db.jobs.find_one({"_id": job_id}, {"events": 0})
    if not doc:
        raise HTTPException(404, "job not found")
    out = _clean(doc)
    out["running"] = job_id in pipeline.RUNNING
    return out


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    pipeline.cancel(job_id)
    await db.jobs.delete_one({"_id": job_id})
    shutil.rmtree(settings.jobs_dir / job_id, ignore_errors=True)
    return {"ok": True}


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    return {"ok": pipeline.cancel(job_id)}


@app.get("/api/jobs/{job_id}/events")
async def job_events(job_id: str, after: int = 0):
    doc = await db.jobs.find_one({"_id": job_id}, {"events": 1, "status": 1})
    if not doc:
        raise HTTPException(404, "job not found")
    bus.seed(job_id, doc.get("events") or [])

    async def gen():
        q = bus.subscribe(job_id)
        try:
            for ev in bus.history(job_id):
                if ev.get("seq", 0) > after:
                    yield {"event": "message", "data": json.dumps(ev, default=str)}
            while True:
                try:
                    ev = await asyncio.wait_for(q.get(), timeout=15)
                    yield {"event": "message", "data": json.dumps(ev, default=str)}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "{}"}
        finally:
            bus.unsubscribe(job_id, q)

    return EventSourceResponse(gen())


class RegenerateBody(BaseModel):
    instruction: str = ""
    visual_type: str | None = None


class UpdateSceneBody(BaseModel):
    visual: dict | None = None
    segments: list[str] | None = None


class RerenderBody(BaseModel):
    theme: str | None = None
    background: str | None = None
    captions: bool | None = None
    quality: str | None = None


def _guard_idle(job_id: str):
    if job_id in pipeline.RUNNING:
        raise HTTPException(409, "job is busy")


@app.post("/api/jobs/{job_id}/scenes/{index}/regenerate")
async def regenerate_scene(job_id: str, index: int, body: RegenerateBody):
    _guard_idle(job_id)
    asyncio.create_task(pipeline.edit_job(job_id, "regenerate_scene", {"index": index, **body.model_dump()}))
    return {"ok": True}


@app.patch("/api/jobs/{job_id}/scenes/{index}")
async def update_scene(job_id: str, index: int, body: UpdateSceneBody):
    _guard_idle(job_id)
    asyncio.create_task(pipeline.edit_job(job_id, "update_scene", {"index": index, **body.model_dump()}))
    return {"ok": True}


@app.post("/api/jobs/{job_id}/rerender")
async def rerender(job_id: str, body: RerenderBody):
    _guard_idle(job_id)
    asyncio.create_task(pipeline.edit_job(job_id, "rerender", body.model_dump()))
    return {"ok": True}


class FeedbackBody(BaseModel):
    rating: int
    notes: str = ""
    learn: bool = True


@app.post("/api/jobs/{job_id}/feedback")
async def feedback(job_id: str, body: FeedbackBody):
    job = await db.jobs.find_one({"_id": job_id})
    if not job:
        raise HTTPException(404, "job not found")
    await db.jobs.update_one({"_id": job_id}, {"$set": {"rating": body.rating, "feedback": body.notes}})
    await db.feedback.insert_one({"_id": uuid.uuid4().hex[:12], "job_id": job_id, "rating": body.rating, "notes": body.notes, "created_at": now()})
    pack = None
    if body.learn and body.rating >= 4 and job.get("status") == "done":
        ctx = Ctx(job_id=job_id, dir=settings.jobs_dir / job_id, prompt=job["input"]["prompt"], options=job["input"]["options"])
        try:
            pack = await distill(ctx, job, body.rating, body.notes)
        except Exception as e:
            log.warning("distill failed: %s", e)
    return {"ok": True, "learned": pack}


# ---------------------------------------------------------------------------
# steering
# ---------------------------------------------------------------------------
@app.get("/api/steering")
async def list_steering():
    packs = await steering.load_all()
    return sorted([json.loads(json.dumps(p, default=str)) for p in packs], key=lambda p: ({"core": 0, "pack": 1, "overlay": 2}.get(p.get("kind", "pack"), 3), p.get("name", "")))


@app.post("/api/steering")
async def upsert_steering(pack: dict[str, Any]):
    pack.setdefault("source", "user")
    pack.setdefault("kind", "pack")
    return await steering.save_pack(pack)


@app.delete("/api/steering/{pid}")
async def delete_steering(pid: str):
    await steering.delete_pack(pid)
    return {"ok": True}


class PreviewBody(BaseModel):
    prompt: str


@app.post("/api/steering/preview")
async def preview_steering(body: PreviewBody):
    """Dry run: what would Pragyan understand, and which steering would apply?"""
    from .agents import understand

    ctx = Ctx(job_id="preview", dir=settings.storage_dir / "tmp", prompt=body.prompt, options={"target_seconds": 75})
    intent = await understand.analyse_intent(ctx, {"readings": [], "docs": []})
    prof = await steering.select(intent.model_dump(), body.prompt)
    return {"intent": intent.model_dump(), "steering": prof.summary()}


# ---------------------------------------------------------------------------
# system
# ---------------------------------------------------------------------------
@app.get("/api/system")
async def system():
    models = await llm.list_models()
    have = {m["name"] for m in models}
    return {
        "db": db.mode,
        "ollama": bool(models),
        "models": [{"name": m["name"], "size": m.get("size"), "family": m.get("details", {}).get("family")} for m in models],
        "roles": {"reason": settings.model_reason, "code": settings.model_code, "vision": settings.model_vision, "embed": settings.model_embed},
        "roles_ok": all(r in have or f"{r}:latest" in have for r in (settings.model_reason, settings.model_vision)),
        "engines": {
            "kokoro": settings.kokoro_model.exists(),
            "manim": shutil.which("latex") is not None,
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "node": shutil.which("node") is not None,
        },
        "llm_stats": {"calls": llm.LLMStats.calls, "tokens": llm.LLMStats.tokens_out, "repairs": llm.LLMStats.repairs},
        "running": list(pipeline.RUNNING.keys()),
        "themes": [{"id": k, **v, "note": THEME_NOTES.get(k, "")} for k, v in THEMES.items()],
    }


@app.get("/api/voices")
async def voices():
    return {"voices": tts.list_voices(), "default": settings.default_voice}


@app.get("/api/health")
async def health():
    return {"ok": True, "db": db.mode}


@app.post("/api/film/render")
async def render_film():
    """Render the hand-directed Pragyan launch film (motion/src/film)."""
    from .engines import remotion_runner

    out = settings.storage_dir / "film" / "pragyan-film.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    await remotion_runner.render_film(out)
    return {"url": "/media/film/pragyan-film.mp4"}
