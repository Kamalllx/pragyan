"""Creative Director (storyboard) + Scene Designers (one agent per scene)."""
from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

from .. import llm, prompts
from ..spec import AUTHORING, Outline, OutlineScene, to_visual
from ..steering import Profile
from .base import AgentRun, Ctx
from .understand import compact

WPS = 2.3  # effective spoken words per second incl. pauses (measured on Kokoro)


def _words(s: str) -> int:
    return len((s or "").split())


LANGUAGES = {"en": "English", "hi": "Hindi (Devanagari script)", "es": "Spanish", "fr": "French", "it": "Italian", "pt": "Portuguese", "ja": "Japanese", "zh": "Mandarin Chinese"}


def language_rule(lang: str) -> str:
    lang = (lang or "en")[:2]
    if lang == "en":
        return ""
    name = LANGUAGES.get(lang, lang)
    return (
        f"\n\nLANGUAGE: write ALL narration and ALL on-screen text in {name}. "
        "Keep LaTeX, code, numbers and proper nouns as they are. JSON keys stay in English."
    )


# ---------------------------------------------------------------------------
# Storyboard
# ---------------------------------------------------------------------------
def _outline_problems(o: Outline, *, target: int, allowed: set[str], quiz: bool, has_image: bool) -> str | None:
    probs = []
    types = [s.visual for s in o.scenes]
    for i in range(1, len(types)):
        if types[i] == types[i - 1]:
            probs.append(f"scenes {i} and {i + 1} both use '{types[i]}' — consecutive scenes must use different visuals")
    bad = [t for t in types if t not in allowed]
    if bad:
        probs.append(f"these visuals are not allowed for this video: {sorted(set(bad))}")
    if types[0] not in ("title", "kinetic", "quote"):
        probs.append("the first scene must be a hook: title or kinetic")
    if "image" in types and not has_image:
        probs.append("'image' requires an uploaded image; none was supplied")
    if quiz and "quiz" in types and types[-1] != "quiz":
        probs.append("the quiz scene must be the last scene")
    total = sum(s.seconds for s in o.scenes)
    if total < target * 0.75 or total > target * 1.25:
        probs.append(f"total seconds is {total}, but the target is {target}; adjust scene count/seconds to fit")
    if len(o.scenes) > max_scenes(target):
        probs.append(f"too many scenes ({len(o.scenes)}) for {target} s — use at most {max_scenes(target)}")
    thin = [i + 1 for i, s in enumerate(o.scenes) if len(s.brief.split()) < 8]
    if thin:
        probs.append(f"scenes {thin} have a vague brief — put the actual content (facts, items, equations) in the brief")
    return "; ".join(probs) or None


async def storyboard(ctx: Ctx, intent, profile: Profile, knowledge: dict) -> Outline:
    opts = ctx.options
    target = int(opts.get("target_seconds") or profile.settings.get("target_seconds") or 75)
    quiz = bool(opts.get("quiz") if opts.get("quiz") is not None else profile.settings.get("quiz", False))
    manim_pref = profile.settings.get("manim", "allow")
    allowed = set(AUTHORING.keys())
    if not opts.get("allow_manim", True) or manim_pref == "avoid":
        allowed.discard("manim")
    if not quiz:
        allowed.discard("quiz")
    has_image = any(f.get("kind") == "image" for f in ctx.files)
    if not has_image:
        allowed.discard("image")
    allowed -= set(a for a in profile.avoid if a in allowed and a not in ("title", "summary"))

    async with AgentRun(ctx, "director", "Creative Director", detail="storyboarding", agent_id="director") as a:
        n_scenes = max(4, min(12, round(target / 9.5)))
        user = (
            f"VIDEO TYPE: {intent.intent} · DOMAIN: {intent.domain} · AUDIENCE: {intent.audience_level}\n"
            f"TOPIC: {intent.topic}\nKEY QUESTION: {intent.key_question}\nUSER REQUEST: {ctx.prompt}\n"
            f"TARGET: {int(target * 0.85)} seconds of narration in total (about {int(target * 0.85 * WPS)} spoken words), roughly {n_scenes} scenes.\n"
            f"ALLOWED VISUALS: {', '.join(sorted(allowed))}\n"
            f"{'End with a quiz scene.' if quiz else 'No quiz.'} "
            f"{'Use manim for 1-2 scenes where maths must move.' if 'manim' in allowed and manim_pref == 'prefer' else ''}"
            f"{'An image was uploaded; you may use one image scene.' if has_image else ''}\n\n"
            f"STEERING:\n{profile.as_prompt()}{language_rule(opts.get('language', 'en')).replace('ALL narration and ALL on-screen text', 'chapter titles')}\n\n"
            f"KNOWLEDGE (use these facts; do not invent new ones):\n{compact(knowledge)[:9000]}"
        )
        tries = {"n": 0}

        def validate(o: Outline):
            tries["n"] += 1
            if tries["n"] >= 3:  # last round: accept, deterministic repair handles the rest
                return None
            return _outline_problems(o, target=target, allowed=allowed, quiz=quiz, has_image=has_image)

        o = await llm.structured(Outline, prompts.DIRECTOR, user, temperature=0.55, attempts=3, validate=validate, on_stats=a.stats, on_repair=a.repair)
        o = _repair_outline(o, allowed, quiz, max_scenes(target))
        for i, s in enumerate(o.scenes):
            a.log(f"{i + 1:02d} · {s.visual:<10} · {s.chapter} — {s.purpose}")
        a.done(f"{len(o.scenes)} scenes · ~{sum(s.seconds for s in o.scenes)} s · “{o.title}”")
        return o


def max_scenes(target: int) -> int:
    """Every scene carries ~1.5 s of fixed cost (lead-in, transition, hold), so short films need few scenes."""
    return max(4, min(14, round(target / 8.5)))


def _repair_outline(o: Outline, allowed: set[str], quiz: bool, limit: int = 14) -> Outline:
    """Deterministic last-mile fixes so a slightly-off storyboard never blocks the job."""
    scenes = [s for s in o.scenes if s.visual in allowed or s.visual in ("title", "summary")]
    if not scenes or scenes[0].visual not in ("title", "kinetic", "quote"):
        scenes.insert(0, OutlineScene(purpose="Hook the viewer", chapter="Intro", visual="title", brief=f"{o.title}. {o.logline}", seconds=6))
    quizzes = [s for s in scenes if s.visual == "quiz"]
    scenes = [s for s in scenes if s.visual != "quiz"]
    if quiz:
        scenes.append(quizzes[0] if quizzes else OutlineScene(purpose="Check understanding", chapter="Quiz", visual="quiz", brief=f"One multiple-choice question testing the key idea of: {o.logline}", seconds=12))
    # break up consecutive duplicates by swapping with the next different scene
    for i in range(1, len(scenes)):
        if scenes[i].visual == scenes[i - 1].visual:
            for j in range(i + 1, len(scenes)):
                if scenes[j].visual != scenes[i].visual and scenes[j].visual != "quiz":
                    scenes[i], scenes[j] = scenes[j], scenes[i]
                    break
    for s in scenes:
        ch = s.chapter.strip()
        if not ch or ch.lower() in ("hook", "recap", "check", "intro"):
            words = re.sub(r"[^\w\s'-]", "", s.purpose).split()
            ch = " ".join(words[:3]).title() if words else s.visual.title()
        if "_" in ch or ch.islower() or re.match(r"^(step|scene)\s*\d+$", ch, re.I):
            ch = re.sub(r"[_\-]+", " ", ch).strip().title()
        s.chapter = ch[:28]
    # Too many scenes for the runtime: drop the shortest middle scenes (keep the hook, the ending and the quiz).
    while len(scenes) > limit:
        middle = [k for k in range(1, len(scenes) - 1) if scenes[k].visual not in ("quiz", "summary")]
        if not middle:
            break
        scenes.pop(min(middle, key=lambda k: scenes[k].seconds))
    o.scenes = scenes[:14]
    return o


# ---------------------------------------------------------------------------
# Scene design
# ---------------------------------------------------------------------------
LIMITS = {"title": 9, "heading": 9, "item_title": 7, "detail": 18, "label": 4}


def _narration_words(d: dict) -> int:
    n = 0
    for k, v in d.items():
        if isinstance(v, str) and ("narration" in k or k == "intro"):
            n += _words(v)
        elif isinstance(v, dict):
            n += _narration_words(v)
        elif isinstance(v, list):
            n += sum(_narration_words(x) for x in v if isinstance(x, dict))
    return n


def _lint(vtype: str, a: BaseModel, budget: int = 0) -> list[str]:
    p: list[str] = []
    d = a.model_dump(by_alias=True)
    if budget:
        nw = _narration_words(d)
        # Only gross overruns bounce back here; the Film Editor trims the rest in one pass.
        if nw > budget * 1.8 + 8:
            p.append(f"narration totals {nw} words but this scene's budget is {budget}; cut every narration line to fit (aim for {budget} words)")

    def chk(val: str, limit: int, where: str):
        if _words(val) > limit:
            p.append(f"{where} is {_words(val)} words (max {limit}): shorten '{val[:50]}'")

    def latex_ok(tex: str, where: str):
        if "$" in tex:
            p.append(f"{where}: remove $ signs from LaTeX")
        if tex.count("{") != tex.count("}"):
            p.append(f"{where}: unbalanced braces in LaTeX '{tex[:40]}'")

    if "heading" in d:
        chk(d["heading"], LIMITS["heading"], "heading")
    if vtype == "title":
        chk(d["title"], LIMITS["title"], "title")
        chk(d["subtitle"], 18, "subtitle")
    for key in ("items", "steps", "cards", "events"):
        for i, it in enumerate(d.get(key, []) or []):
            if "title" in it:
                chk(it["title"], LIMITS["item_title"], f"{key}[{i}].title")
            for dk in ("detail", "body"):
                if it.get(dk):
                    chk(it[dk], LIMITS["detail"], f"{key}[{i}].{dk}")
            if it.get("latex"):
                latex_ok(it["latex"], f"{key}[{i}].latex")
            if "narration" in it and _words(it["narration"]) < 3:
                p.append(f"{key}[{i}].narration is missing or too short")
    if vtype == "equation":
        for i, s in enumerate(d["steps"]):
            latex_ok(s["latex"], f"steps[{i}].latex")
    if vtype == "diagram":
        ids = {n["id"] for n in d["nodes"]}
        if len(ids) < 3:
            p.append("a diagram needs at least 3 nodes showing the full flow")
        for e in d["edges"]:
            if e["from"] not in ids or e["to"] not in ids:
                p.append(f"edge {e['from']}->{e['to']} references an unknown node id; valid ids: {sorted(ids)}")
        for n in d["nodes"]:
            chk(n["label"], 4, f"node {n['id']} label")
    if vtype == "chart" and len(d["labels"]) != len(d["values"]):
        p.append("chart labels and values must have the same length")
    if vtype == "quiz" and not (0 <= d["answer_index"] < len(d["options"])):
        p.append("answer_index must point at one of the options (0-based)")
    if vtype == "kinetic":
        for i, l in enumerate(d["lines"]):
            chk(l["text"], 7, f"lines[{i}].text")
    if vtype == "code":
        lines = d["code"].splitlines()
        if len(lines) > 18:
            p.append(f"code has {len(lines)} lines (max 16)")
        if any(len(l) > 70 for l in lines):
            p.append("some code lines are longer than 70 characters; wrap or shorten")
    if vtype == "orbit3d":
        for s in d["satellites"]:
            chk(s["label"], 3, "satellite label")
    return p


def _trim_words(s: str, n: int) -> str:
    w = (s or "").split()
    return s if len(w) <= n else " ".join(w[:n])


async def design_scene(ctx: Ctx, idx: int, outline: Outline, profile: Profile, knowledge: dict, *, revise: str = "", direction: str = "", forced_type: str | None = None, prev: dict | None = None, parent: str = "director") -> dict:
    sc = outline.scenes[idx]
    vtype = forced_type or sc.visual
    model_cls = AUTHORING[vtype]
    words = max(14, int(sc.seconds * WPS))
    async with AgentRun(ctx, "designer", f"Scene Designer {idx + 1:02d}", parent=parent, detail=f"{vtype} · {sc.chapter}") as a:
        system = prompts.DESIGNER.format(vtype=vtype, words=words, extra=prompts.DESIGNER_EXTRA.get(vtype, ""))
        system += "\n\n" + profile.as_prompt(include_arc=False)
        system += language_rule(ctx.options.get("language", "en"))
        before = outline.scenes[idx - 1].purpose if idx > 0 else "(this is the opening)"
        others = "\n".join(f"- scene {j + 1} ({o.visual}): {o.purpose} — {o.brief[:140]}" for j, o in enumerate(outline.scenes) if j != idx)
        after = outline.scenes[idx + 1].purpose if idx + 1 < len(outline.scenes) else "(this is the final scene)"
        user = (
            f"VIDEO: {outline.title} — {outline.logline}\nAUDIENCE: {ctx.data.get('intent', {}).get('audience_level', 'general')}\n"
            f"SCENE {idx + 1}/{len(outline.scenes)} · chapter '{sc.chapter}'\nPURPOSE: {sc.purpose}\nBRIEF: {sc.brief}\n"
            f"PREVIOUS SCENE: {before}\nNEXT SCENE: {after}\n"
            f"OTHER SCENES (they cover this — do NOT repeat their points, analogies or the hook):\n{others}\n\n"
            f"NARRATION BUDGET: about {words} words in total for this scene.\n\n"
            f"KNOWLEDGE (facts you may use):\n{compact(knowledge)[:6000]}"
        )
        if direction:
            current = f"\n\nCURRENT VERSION (for reference only):\n{compact(prev.get('authoring'))}" if prev and prev.get("authoring") else ""
            user += current + "\n\n" + prompts.DIRECT.format(direction=direction)
        elif revise and prev:
            user += f"\n\nCURRENT VERSION:\n{compact(prev.get('authoring'))}\n\n" + prompts.REVISE.format(problem=revise)
        tries = {"n": 0}

        def validate(obj):
            tries["n"] += 1
            probs = _lint(vtype, obj, words)
            # Soft lint: after two rounds we accept and auto-trim instead of failing the job.
            return "; ".join(probs[:6]) if probs and tries["n"] < 3 else None

        try:
            obj = await llm.structured(model_cls, system, user, temperature=0.6, attempts=3, validate=validate, on_stats=a.stats, on_repair=a.repair)
        except llm.LLMError as e:
            a.log(f"design failed ({e}); using fallback layout", level="warn")
            return fallback_scene(sc)
        image_src = next((ctx.url(Path(f["path"])) for f in ctx.files if f.get("kind") == "image"), None)
        visual, segments = to_visual(vtype, obj, image_src=image_src)
        _auto_trim(visual)
        a.done(f"{vtype} · {sum(_words(s) for s in segments)} narration words")
        return {"type": vtype, "authoring": obj.model_dump(by_alias=True), "visual": visual, "segments": segments}


def _auto_trim(v: dict):
    if v["type"] == "stats":
        for s in v["stats"]:
            suf, lab = (s.get("suffix") or "").strip(), (s.get("label") or "").strip()
            # Small models often swap unit and label ("100" + suffix "offline" + label "%").
            if len(lab) <= 2 and len(suf) > 3:
                s["suffix"], s["label"] = lab, suf
            elif len(suf) > 6:
                s["label"] = f"{suf} {lab}".strip()
                s["suffix"] = ""
            if float(s["value"]).is_integer():
                s["decimals"] = 0
            s["decimals"] = min(int(s.get("decimals") or 0), 2)
            if s.get("suffix") and not s["suffix"].startswith((" ", "%", "×", "x", "+")) and len(s["suffix"]) > 1:
                s["suffix"] = " " + s["suffix"]
    if v["type"] == "title":
        v["title"] = _trim_words(v["title"], 10)
    for key in ("items", "steps", "cards", "events"):
        for it in v.get(key, []) or []:
            if "title" in it:
                it["title"] = _trim_words(it["title"], 8)
            for dk in ("detail", "body"):
                if it.get(dk):
                    it[dk] = _trim_words(it[dk], 20)


def fallback_scene(sc: OutlineScene) -> dict:
    """No-LLM fallback: turn the brief into a clean bullets/kinetic scene. The video always completes."""
    sents = [s.strip() for s in re.split(r"(?<=[.!?;])\s+", sc.brief) if len(s.strip()) > 3][:4]
    if len(sents) >= 2:
        items = [{"title": _trim_words(s.rstrip('.'), 6), "detail": ""} for s in sents]
        return {
            "type": "bullets",
            "authoring": None,
            "visual": {"type": "bullets", "heading": _trim_words(sc.chapter, 6), "items": items},
            "segments": [sc.purpose, *sents],
            "fallback": True,
        }
    return {
        "type": "kinetic",
        "authoring": None,
        "visual": {"type": "kinetic", "lines": [_trim_words(sc.chapter, 5), _trim_words(sc.purpose, 6)], "emphasis": []},
        "segments": ["", sc.purpose, sc.brief],
        "fallback": True,
    }
