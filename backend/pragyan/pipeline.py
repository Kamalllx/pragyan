"""The orchestrator: ingest → understand → steer → think → storyboard → design ∥ narrate ∥ animate → review → render.

Every step is an agent the UI can watch. The pipeline is built to *always* finish:
schema repair, soft lint, Manim fix loops with error memory, and deterministic fallbacks.
"""
from __future__ import annotations

import asyncio
import json
import logging
import math
import time
from pathlib import Path
from typing import Any

from . import steering
from .agents import animator, critic, director, editor, knowledge, understand
from .agents.base import AgentRun, Ctx, JobCancelled
from .config import settings
from .db import db, now
from .engines import media, remotion_runner
from .engines.tts import Narrator
from .spec import Outline

log = logging.getLogger("pragyan.pipeline")

FPS = 30
T = 18  # transition frames
LEAD = 9  # silence before narration starts in each scene
TAIL = 10
MIN_SECONDS = {"title": 4.5, "kinetic": 4.0, "quote": 5.0, "summary": 5.5, "quiz": 9.0, "stats": 5.0, "chart": 6.0, "code": 7.0, "diagram": 6.0}
HOLD = {"code": 1.2, "chart": 0.8, "diagram": 0.8, "summary": 0.5, "title": 0.4, "quiz": 0.8, "equation": 0.6}
TRANSITION = {
    "title": "dip", "kinetic": "rise", "diagram": "zoom", "comparison": "wipe", "orbit3d": "zoom", "cards3d": "slide",
    "timeline": "slide", "equation": "dip", "steps": "rise", "stats": "push", "chart": "rise", "code": "slide",
    "quote": "dip", "summary": "rise", "quiz": "wipe", "manim": "dip", "definition": "slide", "bullets": "slide", "image": "zoom",
}
THEME_BY_DOMAIN = {"mathematics": "chalk", "physics": "cosmos", "computer_science": "neon", "history": "solar", "biology": "solar", "business_product": "midnight", "language_arts": "paper"}
SCALE = {"draft": 0.5, "standard": 1.0, "high": 1.0}

RUNNING: dict[str, tuple[asyncio.Task, Ctx]] = {}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _jsonable(x: Any) -> Any:
    if hasattr(x, "model_dump"):
        return x.model_dump(by_alias=True)
    if isinstance(x, Path):
        return str(x)
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_jsonable(v) for v in x]
    return x


def _scene_public(s: dict) -> dict:
    keys = ("index", "id", "chapter", "purpose", "type", "status", "visual", "segments", "timed", "durationInFrames", "audio_url", "fallback", "manim", "critic", "tts_engine", "audio_seconds")
    return {k: s.get(k) for k in keys if k in s}


async def _persist(ctx: Ctx, **extra):
    await ctx.save(data=_jsonable(ctx.data), scenes=[_jsonable(_scene_public(s) | {"authoring": s.get("authoring"), "brief": s.get("brief")}) for s in ctx.scenes], metrics=ctx.metrics, **extra)


def _resolve_settings(ctx: Ctx, intent, profile: steering.Profile) -> dict:
    o, p = ctx.options, profile.settings
    lang = (o.get("language") or "en")[:2]
    theme = o.get("theme") or p.get("theme") or THEME_BY_DOMAIN.get(intent.domain, "cosmos")
    voice = o.get("voice") or (p.get("voice") if lang == "en" else None)
    return {
        "theme": theme,
        "background": o.get("background") or p.get("background") or "shader",
        "voice": voice,
        "language": lang,
        "speed": float(p.get("speed") or 1.0),
        "captions": bool(o.get("captions", True)),
        "quiz": bool(o.get("quiz") if o.get("quiz") is not None else p.get("quiz", False)),
        "quality": o.get("quality", "standard"),
        "manim": p.get("manim", "allow") if o.get("allow_manim", True) else "avoid",
    }


async def narrate(ctx: Ctx, scene: dict, narrator: Narrator):
    i = scene["index"]
    scene["status"] = "narrating"
    ctx.emit("scene.update", scene=_scene_public(scene))
    pauses = {2: 3.2} if scene["type"] == "quiz" else None
    out = ctx.dir / "audio" / f"scene_{i + 1:02d}.wav"
    # Pacing safety net: the Film Editor owns length; this only nudges scenes it could not cut (max 1.05x).
    words = sum(len((t or "").split()) for t in scene["segments"])
    budget = scene.get("budget_words") or words
    speed = narrator.speed * min(1.05, max(1.0, (words / max(1, budget * 1.3)) ** 0.5))
    scene["speed"] = round(speed, 3)
    sa = await narrator.synth_scene_async(scene["segments"], out, pauses, speed)
    lead = LEAD + (8 if scene["type"] == "title" else 0)
    fr = lambda t: lead + int(round(t * FPS))
    scene["timed"] = [
        {"text": s.text, "start": fr(s.start), "end": fr(s.end), "words": [{"w": w, "s": fr(a), "e": fr(b)} for w, a, b in s.words]}
        for s in sa.segments
    ]
    audio_frames = math.ceil(sa.seconds * FPS)
    hold = int(HOLD.get(scene["type"], 0.25) * FPS)
    dur = lead + audio_frames + TAIL + T + hold
    dur = max(dur, int(MIN_SECONDS.get(scene["type"], 4.0) * FPS) + T)
    scene.update(
        audio_path=str(sa.path) if sa.path else None,
        audio_url=ctx.url(sa.path) if sa.path else None,
        audio_seconds=round(sa.seconds, 2),
        audio_lead=lead,
        durationInFrames=dur,
        tts_engine=sa.engine,
    )


def compose(ctx: Ctx) -> dict:
    st = ctx.data["settings"]
    scenes = []
    last_t = None
    for s in ctx.scenes:
        tr = TRANSITION.get(s["type"], "dip")
        if tr == last_t:
            tr = {"dip": "rise", "rise": "slide", "slide": "dip", "zoom": "dip", "wipe": "dip", "push": "dip"}.get(tr, "dip")
        last_t = tr
        scenes.append(
            {
                "id": s["id"],
                "durationInFrames": s["durationInFrames"],
                "audio": s.get("audio_url"),
                "audioOffset": s.get("audio_lead", LEAD),
                "segments": s.get("timed", []),
                "transition": tr,
                "chapter": s.get("chapter", ""),
                "visual": s["visual"],
            }
        )
    return {
        "meta": {
            "title": ctx.data.get("outline", {}).get("title", "Pragyan"),
            "fps": FPS,
            "width": 1920,
            "height": 1080,
            "theme": st["theme"],
            "background": st["background"],
            "captions": st["captions"],
            "watermark": True,
            "language": st.get("language", "en"),
        },
        "transitionFrames": T,
        "scenes": scenes,
    }


def scene_starts(spec: dict) -> list[int]:
    t, out = 0, []
    for s in spec["scenes"]:
        out.append(t)
        t += s["durationInFrames"] - spec.get("transitionFrames", T)
    return out


async def design_into(ctx: Ctx, scene: dict, outline: Outline, profile: steering.Profile, know: dict, *, revise: str = "", direction: str = "", forced_type: str | None = None):
    """Phase 1: the scene designer fills the visual + narration lines."""
    i = scene["index"]
    ctx.check_cancel()
    scene["status"] = "designing"
    ctx.emit("scene.update", scene=_scene_public(scene))
    d = await director.design_scene(ctx, i, outline, profile, know, revise=revise, direction=direction, forced_type=forced_type, prev=scene if (revise or direction) else None)
    scene.update(type=d["type"], authoring=d.get("authoring"), visual=d["visual"], segments=d["segments"], fallback=d.get("fallback", False))
    scene["status"] = "designed"
    ctx.emit("scene.update", scene=_scene_public(scene))


async def produce_scene(ctx: Ctx, scene: dict, outline: Outline, profile: steering.Profile, know: dict, narrator: Narrator, *, revise: str = "", direction: str = "", forced_type: str | None = None):
    """design → narrate → (manim → fallback). Used for single-scene revisions and edits."""
    await design_into(ctx, scene, outline, profile, know, revise=revise, direction=direction, forced_type=forced_type)
    await finish_scene(ctx, scene, outline, profile, know, narrator)


async def finish_scene(ctx: Ctx, scene: dict, outline: Outline, profile: steering.Profile, know: dict, narrator: Narrator):
    """Phase 3: voice the (edited) narration, then animate Manim scenes against its timings."""
    i = scene["index"]
    ctx.check_cancel()
    await narrate(ctx, scene, narrator)
    if scene["type"] == "manim":
        scene["status"] = "animating"
        ctx.emit("scene.update", scene=_scene_public(scene))
        lead_s = scene["audio_lead"] / FPS
        timings = [{"start": t["start"] / FPS, "end": t["end"] / FPS} for t in scene["timed"]]
        total = (scene["durationInFrames"] - T) / FPS
        res = await animator.animate(ctx, scene, theme=ctx.data["settings"]["theme"], quality=ctx.data["settings"]["quality"], timings=timings, total=total, parent="director")
        scene["manim"] = {"ok": res["ok"], "attempts": res["attempts"], "code": res["code"]}
        if res["ok"]:
            scene["visual"] = {"type": "manim", "src": ctx.url(Path(res["video"])), "transparent": res["transparent"]}
            clip_s = await media.duration(Path(res["video"]))
            scene["durationInFrames"] = max(scene["durationInFrames"], int(clip_s * FPS) + T)
            _ = lead_s
        else:
            ctx.metrics["manim"]["fallbacks"] += 1
            fb = "equation" if any(k in (scene.get("brief") or "").lower() for k in ("=", "equation", "formula", "derivative", "integral")) else "steps"
            ctx.emit("agent.log", agent="director", message=f"scene {i + 1}: Manim failed — redesigning as {fb}", level="warn")
            d = await director.design_scene(ctx, i, outline, profile, know, forced_type=fb)
            scene.update(type=d["type"], authoring=d.get("authoring"), visual=d["visual"], segments=d["segments"], fallback=True)
            await narrate(ctx, scene, narrator)
    scene["status"] = "ready"
    ctx.emit("scene.update", scene=_scene_public(scene))


async def render_final(ctx: Ctx, spec: dict, base_progress: float = 0.84):
    spec_path = ctx.dir / "spec.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False), "utf8")
    out = ctx.dir / "final.mp4"
    quality = ctx.data["settings"].get("quality", "standard")

    def on_ev(ev: dict):
        if ev.get("stage") == "render":
            p = base_progress + (0.99 - base_progress) * float(ev.get("progress", 0))
            ctx.emit("render.progress", progress=round(float(ev.get("progress", 0)), 3), frames=ev.get("renderedFrames"), overall=round(p, 3))
        elif ev.get("stage") == "bundle":
            ctx.emit("render.progress", progress=0, phase="bundling", cached=ev.get("cached"))

    async with AgentRun(ctx, "renderer", "Renderer", detail=f"Remotion · {quality}") as a:
        t0 = time.perf_counter()
        last: Exception | None = None
        # GPU first (fast); transient media-fetch hiccups get one GPU retry before the slow software fallback.
        for attempt, gl in enumerate(("angle", "angle", "swangle")):
            try:
                await remotion_runner.render_video(spec_path, out, scale=SCALE.get(quality, 1.0), on_event=on_ev, gl=gl)
                last = None
                break
            except remotion_runner.RenderError as e:
                last = e
                a.log(f"render attempt {attempt + 1} ({gl}) failed: {str(e).splitlines()[0][:160]}", level="warn")
        if last:
            raise last
        ctx.metrics["timings"]["render"] = round(time.perf_counter() - t0, 1)
        a.done(f"{out.name} in {ctx.metrics['timings']['render']} s")
    # ---- artefacts ---------------------------------------------------------
    poster = await media.frame_at(out, 2.2, ctx.dir / "poster.jpg", width=1280)
    starts = scene_starts(spec)
    cues = []
    for s, st in zip(spec["scenes"], starts):
        for seg in s.get("segments", []):
            if seg["text"]:
                cues.append(((st + seg["start"]) / FPS, (st + seg["end"]) / FPS, seg["text"]))
    media.write_captions(cues, ctx.dir / "captions.srt", ctx.dir / "captions.vtt")
    lines = [f"# {spec['meta']['title']}", ""]
    for s, st in zip(ctx.scenes, starts):
        mm, ss = divmod(int(st / FPS), 60)
        lines += [f"## {mm:02}:{ss:02} — {s.get('chapter', '')}", "", " ".join(t for t in s.get("segments", []) if t), ""]
    (ctx.dir / "transcript.md").write_text("\n".join(lines), "utf8")
    (ctx.dir / "storyboard.json").write_text(json.dumps({"outline": ctx.data.get("outline"), "scenes": [_jsonable(_scene_public(s)) for s in ctx.scenes]}, ensure_ascii=False, indent=2), "utf8")
    total = (sum(s["durationInFrames"] for s in spec["scenes"]) - T * (len(spec["scenes"]) - 1)) / FPS
    outputs = {
        "video": ctx.rel(out),
        "poster": ctx.rel(poster) if poster else None,
        "srt": ctx.rel(ctx.dir / "captions.srt"),
        "vtt": ctx.rel(ctx.dir / "captions.vtt"),
        "transcript": ctx.rel(ctx.dir / "transcript.md"),
        "storyboard": ctx.rel(ctx.dir / "storyboard.json"),
        "spec": ctx.rel(spec_path),
        "duration": round(total, 1),
        "chapters": [{"t": round(st / FPS, 2), "title": s.get("chapter", "")} for s, st in zip(spec["scenes"], starts)],
        "rendered_at": now().isoformat(),
    }
    ctx.emit("artifact", kind="video", url=outputs["video"], poster=outputs["poster"])
    return outputs


async def _profile_for(ctx: Ctx) -> steering.Profile:
    ids = [p["id"] for p in ctx.data.get("steering", {}).get("packs", [])]
    return await steering.select(ctx.data.get("intent", {}), ctx.prompt, forced=ids or None)


# ---------------------------------------------------------------------------
# main job
# ---------------------------------------------------------------------------
async def run_job(job_id: str):
    job = await db.jobs.find_one({"_id": job_id})
    ctx = Ctx(job_id=job_id, dir=settings.jobs_dir / job_id, prompt=job["input"]["prompt"], options=job["input"]["options"], files=job["input"].get("files", []))
    ctx.dir.mkdir(parents=True, exist_ok=True)
    RUNNING[job_id] = (asyncio.current_task(), ctx)  # type: ignore[assignment]
    t_job = time.perf_counter()

    def mark(stage: str, t0: float):
        ctx.metrics["timings"][stage] = round(time.perf_counter() - t0, 1)

    try:
        await ctx.save(status="running", started_at=now())
        async with AgentRun(ctx, "orchestrator", "Orchestrator", parent=None, agent_id="orchestrator", detail="Pragyan") as orch:
            # 1 ─ ingest ─────────────────────────────────────────────────────
            t0 = time.perf_counter()
            ctx.stage("ingest", 0.03, "Reading your input")
            async with AgentRun(ctx, "ingest", "Ingest", agent_id="ingest", detail=f"{len(ctx.files)} file(s)") as ing:
                ingested = await understand.ingest(ctx)
                ing.done(f"{len(ingested['readings'])} image(s) · {len(ingested['docs'])} doc(s)")
            ctx.data["ingested"] = {"readings": ingested["readings"], "docs": [{k: v for k, v in d.items() if k != "text"} for d in ingested["docs"]]}
            mark("ingest", t0)

            # 2 ─ understand ────────────────────────────────────────────────
            t0 = time.perf_counter()
            ctx.stage("understand", 0.08, "Recognising intent")
            intent = await understand.analyse_intent(ctx, ingested)
            ctx.data["intent"] = intent.model_dump()
            ctx.emit("understanding", intent=ctx.data["intent"])
            mark("understand", t0)

            # 3 ─ steer ─────────────────────────────────────────────────────
            ctx.stage("steer", 0.12, "Choosing steering packs")
            async with AgentRun(ctx, "steering", "Steering Curator", detail="retrieving generic direction") as sa:
                profile = await steering.select(ctx.data["intent"], ctx.prompt, forced=ctx.options.get("steering_ids") or None)
                ctx.data["steering"] = profile.summary()
                ctx.data["settings"] = _resolve_settings(ctx, intent, profile)
                for p in ctx.data["steering"]["packs"]:
                    sa.log(f"{p['kind']:<7} {p['name']}  (score {p['score']})")
                sa.done(" + ".join(p["name"] for p in ctx.data["steering"]["packs"] if p["kind"] != "core") or "core only")
            ctx.emit("steering", steering=ctx.data["steering"], settings=ctx.data["settings"])
            orch.log(f"plan: spawn {', '.join(intent.agents)}")
            ctx.emit("plan", agents=intent.agents, reasoning=intent.reasoning)
            await _persist(ctx, title=intent.topic, stage="steer")

            # 4 ─ think (specialists in parallel; GPU semaphore keeps it sane) ─
            t0 = time.perf_counter()
            ctx.stage("think", 0.18, "Specialist agents at work")
            know: dict[str, Any] = {}
            research = await understand.research(ctx, ingested) if "researcher" in intent.agents else None
            if research:
                know["research"] = research.model_dump()
            tasks = []
            if "solver" in intent.agents:
                tasks.append(("solver", knowledge.solve(ctx, intent, ingested)))
            if "explainer" in intent.agents or not tasks:
                tasks.append(("explainer", knowledge.explain(ctx, intent, ingested, research)))
            results = await asyncio.gather(*(t for _, t in tasks), return_exceptions=True)
            for (name, _), r in zip(tasks, results):
                if isinstance(r, Exception):
                    orch.log(f"{name} failed: {r}", level="warn")
                    continue
                if name == "solver":
                    sol, ver = r
                    know["solution"] = sol.model_dump()
                    know["verification"] = ver
                    ctx.emit("solution", solution=know["solution"], verification=ver)
                else:
                    know["brief"] = r.model_dump()
                    ctx.emit("brief", brief=know["brief"])
            ctx.data["knowledge"] = know
            mark("think", t0)
            await _persist(ctx, stage="think")

            # 5 ─ storyboard ────────────────────────────────────────────────
            t0 = time.perf_counter()
            ctx.stage("storyboard", 0.3, "Storyboarding")
            outline = await director.storyboard(ctx, intent, profile, know)
            ctx.data["outline"] = outline.model_dump()
            ctx.scenes = [
                {"index": i, "id": f"s{i + 1:02d}", "chapter": s.chapter, "purpose": s.purpose, "brief": s.brief, "type": s.visual, "status": "queued", "budget_words": int(s.seconds * director.WPS)}
                for i, s in enumerate(outline.scenes)
            ]
            ctx.emit("storyboard", outline=ctx.data["outline"], scenes=[_scene_public(s) for s in ctx.scenes])
            mark("storyboard", t0)
            await _persist(ctx, stage="storyboard", title=outline.title)

            # 6 ─ produce scenes (design ∥ narrate ∥ animate) ──────────────────
            t0 = time.perf_counter()
            ctx.stage("produce", 0.38, "Designing, narrating and animating scenes")
            st = ctx.data["settings"]
            narrator = Narrator(voice=st["voice"], language=st["language"], speed=st["speed"])
            ctx.data["settings"]["voice"] = narrator.voice
            done = {"n": 0}
            n_sc = len(ctx.scenes)

            def fallback(s, err):
                orch.log(f"scene {s['index'] + 1} failed ({err}); using fallback", level="warn")
                d = director.fallback_scene(outline.scenes[s["index"]])
                s.update(type=d["type"], visual=d["visual"], segments=d["segments"], fallback=True, authoring=None)

            # 6a design every scene (LLM-bound; the GPU semaphore serialises them)
            async def design_one(s):
                await design_into(ctx, s, outline, profile, know)
                done["n"] += 1
                ctx.emit("stage", stage="produce", progress=round(0.38 + 0.18 * done["n"] / n_sc, 3), label=f"{done['n']}/{n_sc} scenes designed")

            res = await asyncio.gather(*(design_one(s) for s in ctx.scenes), return_exceptions=True)
            for s, r in zip(ctx.scenes, res):
                if isinstance(r, JobCancelled):
                    raise r
                if isinstance(r, Exception):
                    fallback(s, r)

            # 6b the editor cuts narration for time before anything is voiced
            target = float(ctx.options.get("target_seconds") or 75)
            try:
                ctx.metrics["edit"] = await editor.cut_for_time(ctx, ctx.scenes, [s.seconds for s in outline.scenes], target, narrator.speed)
            except Exception as e:
                orch.log(f"editor skipped: {e}", level="warn")

            # 6c voice + animate (TTS on CPU threads, Manim renders overlap with Manim LLM calls)
            done["n"] = 0

            async def finish_one(s):
                await finish_scene(ctx, s, outline, profile, know, narrator)
                done["n"] += 1
                ctx.emit("stage", stage="produce", progress=round(0.56 + 0.18 * done["n"] / n_sc, 3), label=f"{done['n']}/{n_sc} scenes ready")

            res = await asyncio.gather(*(finish_one(s) for s in ctx.scenes), return_exceptions=True)
            for s, r in zip(ctx.scenes, res):
                if isinstance(r, JobCancelled):
                    raise r
                if isinstance(r, Exception):
                    fallback(s, r)
                    await narrate(ctx, s, narrator)
                    s["status"] = "ready"
            mark("produce", t0)
            await _persist(ctx, stage="produce")

            # 7 ─ review (render → inspect → fix) ─────────────────────────────
            spec = compose(ctx)
            spec_path = ctx.dir / "spec.json"
            spec_path.write_text(json.dumps(spec, ensure_ascii=False), "utf8")
            if ctx.options.get("critic", True):
                t0 = time.perf_counter()
                ctx.stage("review", 0.76, "Visual critic reviewing frames")
                try:
                    skip = {s["index"] for s in ctx.scenes if s["type"] == "manim"}
                    problems = await critic.review(ctx, spec, spec_path, skip)
                    if problems:
                        async with AgentRun(ctx, "reviser", "Reviser", detail=f"{len(problems)} scene(s)") as rv:
                            for i, prob in problems.items():
                                s = ctx.scenes[i]
                                if s.get("fallback"):
                                    continue
                                rv.log(f"scene {i + 1}: {prob}")
                                s["critic"] = prob
                                await produce_scene(ctx, s, outline, profile, know, narrator, revise=prob, forced_type=s["type"])
                                ctx.metrics["critic"]["revised"] += 1
                            rv.done(f"revised {len(problems)} scene(s)")
                        spec = compose(ctx)
                except Exception as e:
                    orch.log(f"review skipped: {e}", level="warn")
                mark("review", t0)

            # 8 ─ render ──────────────────────────────────────────────────────
            ctx.stage("render", 0.84, "Rendering final video")
            outputs = await render_final(ctx, spec)
            ctx.metrics["timings"]["total"] = round(time.perf_counter() - t_job, 1)
            orch.done(f"{outputs['duration']} s video in {ctx.metrics['timings']['total']} s")
        quiz = next((s["visual"] for s in ctx.scenes if s["type"] == "quiz"), None)
        await _persist(ctx, status="done", stage="done", spec=spec, outputs=outputs, quiz=quiz, finished_at=now())
        ctx.stage("done", 1.0, "Ready")
        ctx.emit("job.done", outputs=outputs, metrics=ctx.metrics)
    except (JobCancelled, asyncio.CancelledError):
        await ctx.save(status="cancelled", stage="cancelled")
        ctx.emit("job.cancelled")
    except Exception as e:
        log.exception("job %s failed", job_id)
        await _persist(ctx, status="failed", error=f"{type(e).__name__}: {e}")
        ctx.emit("job.failed", error=f"{type(e).__name__}: {str(e)[:500]}")
    finally:
        RUNNING.pop(job_id, None)


# ---------------------------------------------------------------------------
# follow-up edits (human in the loop)
# ---------------------------------------------------------------------------
async def _ctx_from_job(job: dict) -> Ctx:
    ctx = Ctx(job_id=job["_id"], dir=settings.jobs_dir / job["_id"], prompt=job["input"]["prompt"], options=job["input"]["options"], files=job["input"].get("files", []))
    ctx.data = job.get("data", {})
    ctx.metrics = job.get("metrics", ctx.metrics)
    ctx.scenes = []
    for s in job.get("scenes", []):
        s = dict(s)
        if s.get("audio_url"):
            s["audio_lead"] = s.get("audio_lead") or (LEAD + (8 if s.get("type") == "title" else 0))
        ctx.scenes.append(s)
    return ctx


async def edit_job(job_id: str, action: str, payload: dict):
    """action: regenerate_scene | update_scene | rerender"""
    job = await db.jobs.find_one({"_id": job_id})
    ctx = await _ctx_from_job(job)
    RUNNING[job_id] = (asyncio.current_task(), ctx)  # type: ignore[assignment]
    try:
        await ctx.save(status="running", stage="editing")
        async with AgentRun(ctx, "orchestrator", "Orchestrator", parent=None, agent_id="orchestrator", detail=f"edit · {action}") as orch:
            st = ctx.data["settings"]
            if action == "rerender":
                for k in ("theme", "background", "captions", "quality"):
                    if payload.get(k) is not None:
                        st[k] = payload[k]
            narrator = Narrator(voice=st.get("voice"), language=st.get("language", "en"), speed=st.get("speed", 1.0))
            if action in ("regenerate_scene", "update_scene"):
                i = int(payload["index"])
                s = ctx.scenes[i]
                # re-attach audio lead for narrate(); authoring is needed for manim
                s["authoring"] = (job.get("scenes") or [{}])[i].get("authoring") if i < len(job.get("scenes", [])) else None
                outline = Outline.model_validate(ctx.data["outline"])
                if action == "regenerate_scene":
                    profile = await _profile_for(ctx)
                    vt = payload.get("visual_type") or s["type"]
                    outline.scenes[i].visual = vt
                    instr = payload.get("instruction") or "Make this scene clearer and more visual."
                    orch.log(f"scene {i + 1}: {instr}")
                    await produce_scene(ctx, s, outline, profile, ctx.data.get("knowledge", {}), narrator, direction=instr, forced_type=vt)
                else:
                    if payload.get("visual"):
                        s["visual"] = payload["visual"]
                        s["type"] = payload["visual"].get("type", s["type"])
                    if payload.get("segments") is not None:
                        s["segments"] = payload["segments"]
                        await narrate(ctx, s, narrator)
                    s["status"] = "ready"
                    ctx.emit("scene.update", scene=_scene_public(s))
            spec = compose(ctx)
            ctx.stage("render", 0.84, "Re-rendering")
            outputs = await render_final(ctx, spec)
            orch.done("edit applied")
        await _persist(ctx, status="done", stage="done", spec=spec, outputs=outputs)
        ctx.stage("done", 1.0, "Ready")
        ctx.emit("job.done", outputs=outputs, metrics=ctx.metrics)
    except Exception as e:
        log.exception("edit failed")
        await ctx.save(status="done" if job.get("outputs") else "failed", stage="done", error=f"edit failed: {e}")
        ctx.emit("job.failed", error=f"edit failed: {str(e)[:400]}", recoverable=True)
    finally:
        RUNNING.pop(job_id, None)


def cancel(job_id: str) -> bool:
    entry = RUNNING.get(job_id)
    if not entry:
        return False
    task, ctx = entry
    ctx.cancelled = True
    task.cancel()
    return True
