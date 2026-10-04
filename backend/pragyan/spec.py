"""Pydantic schemas.

Two layers for every visual:
  * an *authoring* schema the LLM fills — each on-screen item carries its own
    narration line, so audio and visuals are aligned by construction;
  * a converter to the renderer's Visual + ordered narration segments
    (segment 0 = scene intro, segment k = item k — see motion/src/motion useCues).
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Job inputs
# ---------------------------------------------------------------------------
Theme = Literal["cosmos", "midnight", "chalk", "paper", "neon", "solar"]
Background = Literal["shader", "aurora", "grid", "particles", "stars", "plain"]


class JobOptions(BaseModel):
    target_seconds: int = 75
    audience: Optional[str] = None  # auto when None
    theme: Optional[Theme] = None  # auto (steering) when None
    background: Optional[Background] = None
    voice: Optional[str] = None
    language: str = "en"
    captions: bool = True
    quiz: Optional[bool] = None
    quality: Literal["draft", "standard", "high"] = "standard"
    critic: bool = True  # vision self-review loop
    allow_manim: bool = True
    steering_ids: list[str] = []  # force specific packs


# ---------------------------------------------------------------------------
# Understanding
# ---------------------------------------------------------------------------
Intent = Literal[
    "explain_concept",
    "solve_problem",
    "summarize_document",
    "compare",
    "how_to",
    "story_history",
    "product_pitch",
    "code_walkthrough",
    "revision_notes",
]
Domain = Literal[
    "mathematics", "physics", "chemistry", "biology", "computer_science", "engineering",
    "economics_finance", "history", "geography", "business_product", "language_arts", "general",
]
AgentName = Literal["explainer", "solver", "researcher", "visualizer", "coder", "quizmaster", "data_analyst"]


class ImageReading(BaseModel):
    description: str
    transcribed_text: str = ""
    contains_problem: bool = False
    subject_guess: str = ""


class IntentAnalysis(BaseModel):
    intent: Intent
    topic: str = Field(description="Short topic title, 2-8 words")
    domain: Domain
    key_question: str = Field(description="The single question the video must answer")
    audience_level: Literal["kid", "school", "undergrad", "expert", "general"]
    subtopics: list[str] = Field(default_factory=list, max_length=8)
    needs_solving: bool
    needs_math: bool
    needs_code: bool
    needs_data: bool
    tone: str = Field(description="e.g. curious and warm, crisp and confident")
    agents: list[AgentName] = Field(description="Specialist agents to spawn")
    reasoning: str = Field(description="One or two sentences on why")


class KeyTerm(BaseModel):
    term: str
    meaning: str


class ConceptBrief(BaseModel):
    hook_question: str
    intuition: str
    analogy: str
    core_idea: str
    formal_statement: str = ""
    formula_latex: str = ""
    mechanism_steps: list[str] = Field(min_length=2, max_length=7, description="cause-and-effect chain, 3-6 short steps")
    key_terms: list[KeyTerm] = Field(default_factory=list, max_length=6)
    example: str = ""
    misconceptions: list[str] = Field(default_factory=list, max_length=4)
    real_world: list[str] = Field(default_factory=list, max_length=4)
    numbers: list[str] = Field(default_factory=list, max_length=5, description="Memorable quantitative facts, if any")
    takeaways: list[str] = Field(min_length=2, max_length=6)


class SolutionStep(BaseModel):
    title: str
    explanation: str
    latex: str = ""


class Solution(BaseModel):
    problem_restatement: str
    given: list[str] = Field(default_factory=list)
    find: str
    approach: str
    steps: list[SolutionStep] = Field(min_length=1, max_length=8)
    final_answer: str
    final_answer_latex: str = ""
    verification_code: str = Field(
        default="",
        description="Python using sympy/math that prints the final answer for independent checking; empty if not computable",
    )


class Research(BaseModel):
    """Digest of supplied documents / images."""

    title: str
    summary: str
    key_points: list[str] = Field(min_length=2, max_length=10)
    facts_and_figures: list[str] = Field(default_factory=list, max_length=8)
    timeline: list[str] = Field(default_factory=list, max_length=8)
    quotes: list[str] = Field(default_factory=list, max_length=3)


# ---------------------------------------------------------------------------
# Storyboard
# ---------------------------------------------------------------------------
VisualType = Literal[
    "title", "kinetic", "bullets", "definition", "equation", "steps", "diagram", "comparison",
    "stats", "chart", "code", "quote", "image", "timeline", "orbit3d", "cards3d", "manim", "summary", "quiz",
]


class OutlineScene(BaseModel):
    purpose: str = Field(description="What this scene must achieve, one sentence")
    chapter: str = Field(description="2-3 word human-readable chapter title in Title Case, e.g. 'The Setup', 'Finding Limits'")
    visual: VisualType
    brief: str = Field(description="Concrete content for the scene: facts, items, equations, what is shown")
    seconds: int = Field(ge=4, le=40)


class Outline(BaseModel):
    title: str
    logline: str
    scenes: list[OutlineScene] = Field(min_length=3, max_length=14)


# ---------------------------------------------------------------------------
# Authoring schemas (LLM-facing). `narration` = what the voice says while that item is on screen.
# ---------------------------------------------------------------------------
class _Narrated(BaseModel):
    narration: str


class ATitle(BaseModel):
    eyebrow: str = Field(description="tiny label above the title, 2-4 words")
    title: str = Field(description="max 8 words")
    subtitle: str = Field(description="max 16 words")
    narration: str


class AKineticLine(_Narrated):
    text: str = Field(description="max 6 words")


class AKinetic(BaseModel):
    lines: list[AKineticLine] = Field(min_length=2, max_length=4)
    emphasis: list[str] = Field(default_factory=list, description="1-3 single words from the lines to highlight")


class ABulletItem(_Narrated):
    title: str = Field(description="max 6 words")
    detail: str = Field(default="", description="max 14 words")


class ABullets(BaseModel):
    heading: str
    intro: str = Field(description="narration before the first item")
    items: list[ABulletItem] = Field(min_length=2, max_length=5)


class ADefinition(BaseModel):
    term: str
    definition: str = Field(description="max 28 words")
    analogy: str = Field(default="", description="max 20 words")
    narration: str = Field(description="narration for term + definition")
    analogy_narration: str = ""


class AEqStep(_Narrated):
    latex: str = Field(description="KaTeX-compatible LaTeX, no $ signs")
    note: str = Field(default="", description="max 6 words")


class AEquation(BaseModel):
    heading: str
    intro: str
    steps: list[AEqStep] = Field(min_length=1, max_length=6)


class AStep(_Narrated):
    title: str = Field(description="max 6 words")
    detail: str = Field(default="", description="max 18 words")
    latex: str = Field(default="", description="optional KaTeX expression, no $")


class ASteps(BaseModel):
    heading: str
    intro: str
    steps: list[AStep] = Field(min_length=2, max_length=7)
    answer: str = ""
    answer_narration: str = ""


class ANode(_Narrated):
    id: str
    label: str = Field(description="max 3 words")
    sub: str = Field(default="", description="max 4 words")


class AEdge(BaseModel):
    from_: str = Field(alias="from")
    to: str
    label: str = ""

    model_config = {"populate_by_name": True}


class ADiagram(BaseModel):
    heading: str
    intro: str
    nodes: list[ANode] = Field(min_length=2, max_length=8)
    edges: list[AEdge] = Field(min_length=1, max_length=12)
    direction: Literal["LR", "TB"] = "LR"


class ASide(_Narrated):
    title: str
    points: list[str] = Field(min_length=1, max_length=4)


class AComparison(BaseModel):
    heading: str
    intro: str = ""
    left: ASide
    right: ASide
    verdict: str = ""
    verdict_narration: str = ""


class AStat(_Narrated):
    value: float
    prefix: str = ""
    suffix: str = ""
    label: str = Field(description="max 8 words")
    decimals: int = 0


class AStats(BaseModel):
    heading: str
    intro: str
    stats: list[AStat] = Field(min_length=1, max_length=4)


class AChart(BaseModel):
    heading: str
    kind: Literal["bar", "line"]
    labels: list[str] = Field(min_length=2, max_length=10)
    values: list[float] = Field(min_length=2, max_length=10)
    unit: str = ""
    caption: str = ""
    narration: str


class ACode(BaseModel):
    heading: str
    language: str
    code: str = Field(description="max 16 short lines")
    highlight_lines: list[int] = Field(default_factory=list)
    caption: str = ""
    narration: str


class AQuote(BaseModel):
    text: str
    attribution: str = ""
    narration: str


class AEvent(_Narrated):
    date: str
    title: str = Field(description="max 5 words")
    detail: str = Field(default="", description="max 10 words")


class ATimeline(BaseModel):
    heading: str
    intro: str
    events: list[AEvent] = Field(min_length=2, max_length=6)


class ASatellite(_Narrated):
    label: str = Field(description="max 2 words")


class AOrbit(BaseModel):
    center: str = Field(description="max 3 words")
    intro: str
    satellites: list[ASatellite] = Field(min_length=3, max_length=6)
    caption: str = ""


class ACard(_Narrated):
    title: str = Field(description="max 5 words")
    body: str = Field(description="max 16 words")


class ACards(BaseModel):
    heading: str
    intro: str
    cards: list[ACard] = Field(min_length=2, max_length=4)


class ATakeaway(_Narrated):
    text: str = Field(description="max 9 words")


class ASummary(BaseModel):
    heading: str
    intro: str
    takeaways: list[ATakeaway] = Field(min_length=2, max_length=5)


class AQuiz(BaseModel):
    question: str
    options: list[str] = Field(min_length=3, max_length=4)
    answer_index: int
    explanation: str = Field(description="max 20 words")
    question_narration: str
    options_narration: str = Field(description="short line inviting the viewer to pick")
    explanation_narration: str


class AImageNote(_Narrated):
    label: str
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)


class AImage(BaseModel):
    caption: str
    intro: str
    annotations: list[AImageNote] = Field(default_factory=list, max_length=4)


class AManimBeat(BaseModel):
    narration: str
    visual: str = Field(description="what the animation shows during this narration")


class AManim(BaseModel):
    title: str = Field(description="tiny label, 2-4 words")
    beats: list[AManimBeat] = Field(min_length=1, max_length=5)


AUTHORING: dict[str, type[BaseModel]] = {
    "title": ATitle, "kinetic": AKinetic, "bullets": ABullets, "definition": ADefinition,
    "equation": AEquation, "steps": ASteps, "diagram": ADiagram, "comparison": AComparison,
    "stats": AStats, "chart": AChart, "code": ACode, "quote": AQuote, "timeline": ATimeline,
    "orbit3d": AOrbit, "cards3d": ACards, "summary": ASummary, "quiz": AQuiz, "image": AImage, "manim": AManim,
}


def to_visual(vtype: str, a: BaseModel, *, image_src: str | None = None) -> tuple[dict, list[str]]:
    """Convert an authoring object into (renderer visual dict, ordered narration segments)."""
    if vtype == "title":
        return {"type": "title", "eyebrow": a.eyebrow, "title": a.title, "subtitle": a.subtitle}, [a.narration]
    if vtype == "kinetic":
        return {"type": "kinetic", "lines": [l.text for l in a.lines], "emphasis": a.emphasis}, ["", *[l.narration for l in a.lines]]
    if vtype == "bullets":
        return (
            {"type": "bullets", "heading": a.heading, "items": [{"title": i.title, "detail": i.detail} for i in a.items]},
            [a.intro, *[i.narration for i in a.items]],
        )
    if vtype == "definition":
        v = {"type": "definition", "term": a.term, "definition": a.definition}
        segs = [a.narration]
        if a.analogy:
            v["analogy"] = a.analogy
            segs = ["", a.narration, a.analogy_narration or f"Think of it like this: {a.analogy}"]
        else:
            segs = ["", a.narration]
        return v, segs
    if vtype == "equation":
        return (
            {"type": "equation", "heading": a.heading, "steps": [{"latex": s.latex, "note": s.note} for s in a.steps]},
            [a.intro, *[s.narration for s in a.steps]],
        )
    if vtype == "steps":
        segs = [a.intro, *[s.narration for s in a.steps]]
        v = {"type": "steps", "heading": a.heading, "steps": [{"title": s.title, "detail": s.detail, "latex": s.latex} for s in a.steps]}
        if a.answer:
            v["answer"] = a.answer
            ans = a.answer.strip()
            segs.append(a.answer_narration or (ans if ans.endswith((".", "!", "?")) else ans + "."))
        return v, segs
    if vtype == "diagram":
        return (
            {
                "type": "diagram",
                "heading": a.heading,
                "nodes": [{"id": n.id, "label": n.label, "sub": n.sub} for n in a.nodes],
                "edges": [{"from": e.from_, "to": e.to, "label": e.label} for e in a.edges],
                "direction": a.direction,
            },
            [a.intro, *[n.narration for n in a.nodes]],
        )
    if vtype == "comparison":
        segs = [a.intro, a.left.narration, a.right.narration]
        if a.verdict:
            segs.append(a.verdict_narration or a.verdict)
        return (
            {
                "type": "comparison",
                "heading": a.heading,
                "left": {"title": a.left.title, "points": a.left.points},
                "right": {"title": a.right.title, "points": a.right.points},
                "verdict": a.verdict,
            },
            segs,
        )
    if vtype == "stats":
        return (
            {
                "type": "stats",
                "heading": a.heading,
                "stats": [{"value": s.value, "prefix": s.prefix, "suffix": s.suffix, "label": s.label, "decimals": s.decimals} for s in a.stats],
            },
            [a.intro, *[s.narration for s in a.stats]],
        )
    if vtype == "chart":
        n = min(len(a.labels), len(a.values))
        return (
            {"type": "chart", "heading": a.heading, "kind": a.kind, "labels": a.labels[:n], "values": a.values[:n], "unit": a.unit, "caption": a.caption},
            [a.narration],
        )
    if vtype == "code":
        return (
            {"type": "code", "heading": a.heading, "language": a.language, "code": a.code, "highlightLines": a.highlight_lines, "caption": a.caption},
            [a.narration],
        )
    if vtype == "quote":
        return {"type": "quote", "text": a.text, "attribution": a.attribution}, [a.narration]
    if vtype == "timeline":
        return (
            {"type": "timeline", "heading": a.heading, "events": [{"date": e.date, "title": e.title, "detail": e.detail} for e in a.events]},
            [a.intro, *[e.narration for e in a.events]],
        )
    if vtype == "orbit3d":
        return (
            {"type": "orbit3d", "center": a.center, "satellites": [s.label for s in a.satellites], "caption": a.caption},
            [a.intro, *[s.narration for s in a.satellites]],
        )
    if vtype == "cards3d":
        return (
            {"type": "cards3d", "heading": a.heading, "cards": [{"title": c.title, "body": c.body} for c in a.cards]},
            [a.intro, *[c.narration for c in a.cards]],
        )
    if vtype == "summary":
        return (
            {"type": "summary", "heading": a.heading, "takeaways": [t.text for t in a.takeaways]},
            [a.intro, *[t.narration for t in a.takeaways]],
        )
    if vtype == "quiz":
        idx = min(max(0, a.answer_index), len(a.options) - 1)
        return (
            {"type": "quiz", "question": a.question, "options": a.options, "answerIndex": idx, "explanation": a.explanation},
            [a.question_narration, a.options_narration, a.explanation_narration],
        )
    if vtype == "manim":
        # The clip is rendered later by the Animator; until then the scene is a placeholder.
        return {"type": "manim", "src": "", "title": a.title}, [b.narration for b in a.beats]
    if vtype == "image":
        return (
            {"type": "image", "src": image_src or "", "caption": a.caption, "annotations": [{"x": n.x, "y": n.y, "label": n.label} for n in a.annotations]},
            [a.intro, *[n.narration for n in a.annotations]],
        )
    raise ValueError(f"unknown visual {vtype}")


# ---------------------------------------------------------------------------
# Critic + steering distillation
# ---------------------------------------------------------------------------
class CriticIssue(BaseModel):
    scene_index: int
    severity: Literal["minor", "major"]
    problem: str
    fix: str


class CriticReport(BaseModel):
    overall: int = Field(ge=1, le=10)
    issues: list[CriticIssue] = Field(default_factory=list)


class FrameCheck(BaseModel):
    score: int = Field(ge=1, le=10)
    text_cut_off: bool
    overlapping: bool
    empty_or_blank: bool
    notes: str


class SteeringDraft(BaseModel):
    name: str
    description: str
    intents: list[Intent] = Field(min_length=1, max_length=3)
    domains: list[Domain] = Field(min_length=1, max_length=6)
    keywords: list[str]
    theme: Theme
    arc: list[str] = Field(min_length=3, max_length=10, description="Generic scene beats with visual type, e.g. 'hook: kinetic'")
    narration_rules: list[str] = Field(min_length=2, max_length=6)
    do: list[str] = Field(min_length=2, max_length=6)
    dont: list[str] = Field(min_length=1, max_length=5)


class ManimCode(BaseModel):
    code: str
    notes: str = ""
