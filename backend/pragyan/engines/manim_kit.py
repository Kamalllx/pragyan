"""Source of `pragyan_kit.py`, copied next to every generated Manim scene.

A small, opinionated helper layer: it gives a 9B coder model high-level, hard-to-misuse
building blocks (themed text, safe-area fitting, narration sync) so generated scenes
look on-brand and fail less.
"""

KIT_TEMPLATE = r'''
from manim import *
import numpy as np

# ---- theme (injected per job) ----
BG = "{bg}"
TEXT = "{text}"
MUTED = "{muted}"
ACCENT = "{accent}"
ACCENT2 = "{accent2}"
GOOD = "{good}"
BAD = "{bad}"
FONT = "{font}"
TRANSPARENT = {transparent}

if not TRANSPARENT:
    config.background_color = BG

# Keep clear of the caption band at the bottom of the final video.
SAFE_W = config.frame_width - 1.4
SAFE_H = config.frame_height - 2.6
SAFE_CENTER = UP * 0.55


def T(text, size=36, color=None, weight=NORMAL, slant=NORMAL):
    """Themed plain text (never use Tex for prose)."""
    return Text(str(text), font=FONT, font_size=size, color=color or TEXT, weight=weight, slant=slant)


def M(tex, size=52, color=None):
    """Themed maths. Pass raw LaTeX without $ signs."""
    return MathTex(tex, font_size=size, color=color or TEXT)


def fit(mob, w=None, h=None):
    """Scale a mobject down (never up) so it fits the safe area."""
    w = w or SAFE_W
    h = h or SAFE_H
    if mob.width > w:
        mob.scale_to_fit_width(w)
    if mob.height > h:
        mob.scale_to_fit_height(h)
    return mob


def place(mob, where=None):
    """Fit and centre a mobject in the caption-safe area."""
    fit(mob)
    mob.move_to(where if where is not None else SAFE_CENTER)
    return mob


def headline(scene, text, size=34):
    """Small accent label pinned to the top-left. Returns the mobject."""
    t = T(text.upper(), size=size * 0.6, color=ACCENT, weight=BOLD)
    t.to_edge(UP, buff=0.5)
    scene.play(FadeIn(t, shift=RIGHT * 0.2), run_time=0.6)
    return t


def make_axes(x_range=(-5, 5, 1), y_range=(-3, 3, 1), x_length=9, y_length=5, x_label="x", y_label="y"):
    ax = Axes(
        x_range=list(x_range),
        y_range=list(y_range),
        x_length=x_length,
        y_length=y_length,
        axis_config={{"color": MUTED, "stroke_width": 2, "include_tip": True, "tip_length": 0.2}},
    )
    labels = ax.get_axis_labels(MathTex(x_label, color=MUTED, font_size=32), MathTex(y_label, color=MUTED, font_size=32))
    group = VGroup(ax, labels)
    place(group)
    return ax, labels


def _visible_range(ax, f, x_range):
    """Largest x-interval where f stays inside the axes' y-range, so curves never shoot off-frame."""
    x0, x1 = (x_range[0], x_range[1]) if x_range is not None else (ax.x_range[0], ax.x_range[1])
    y0, y1 = ax.y_range[0], ax.y_range[1]
    xs = np.linspace(x0, x1, 400)
    ok = []
    for x in xs:
        try:
            y = float(f(x))
            ok.append(y0 - 1e-9 <= y <= y1 + 1e-9 and np.isfinite(y))
        except Exception:
            ok.append(False)
    best, cur = None, None
    for x, good in zip(xs, ok):
        if good:
            cur = (cur[0], x) if cur else (x, x)
            if best is None or cur[1] - cur[0] > best[1] - best[0]:
                best = cur
        else:
            cur = None
    return best if best and best[1] > best[0] else (x0, x1)


def plot(ax, f, x_range=None, color=None, width=5):
    lo, hi = _visible_range(ax, f, x_range)
    kw = {{"color": color or ACCENT, "stroke_width": width, "x_range": [lo, hi]}}
    return ax.plot(f, **kw)


def glow_dot(point, color=None, r=0.09):
    c = color or ACCENT
    return VGroup(
        Dot(point, radius=r * 3.2, color=c, fill_opacity=0.12),
        Dot(point, radius=r * 2.0, color=c, fill_opacity=0.25),
        Dot(point, radius=r, color=c),
    )


def derive(scene, latex_steps, size=56, hold=0.8, run_time=1.2):
    """Morph through a chain of equations, matching shared symbols."""
    cur = place(M(latex_steps[0], size))
    scene.play(Write(cur), run_time=run_time)
    scene.wait(hold)
    for tex in latex_steps[1:]:
        nxt = place(M(tex, size))
        scene.play(TransformMatchingTex(cur, nxt), run_time=run_time)
        scene.wait(hold)
        cur = nxt
    return cur


def highlight(scene, mob, color=None, run_time=1.0):
    scene.play(Circumscribe(mob, color=color or ACCENT, fade_out=True), run_time=run_time)


def arrow_label(start, end, text, color=None):
    a = Arrow(start, end, buff=0.1, color=color or ACCENT2, stroke_width=4)
    t = T(text, size=26, color=color or ACCENT2).next_to(a, UP, buff=0.1)
    return VGroup(a, t)


def sync(scene, t):
    """Wait until the scene clock reaches t seconds (keeps animation in step with narration)."""
    now = scene.renderer.time
    if t - now > 0.04:
        scene.wait(t - now)


def clear(scene, run_time=0.6):
    if scene.mobjects:
        scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=run_time)
'''

KIT_API_DOC = """Helpers available via `from pragyan_kit import *` (already imported):
- Colours: BG, TEXT, MUTED, ACCENT, ACCENT2, GOOD, BAD (hex strings). Constants SAFE_W, SAFE_H, SAFE_CENTER.
- T(text, size=36, color=None, weight=NORMAL) -> Text   # all prose
- M(latex, size=52, color=None) -> MathTex                # all maths, raw LaTeX, no $
- fit(mob) / place(mob, where=None)                        # keep inside caption-safe area; place() also centres
- headline(scene, text)                                    # small accent label, top centre
- make_axes(x_range=(-5,5,1), y_range=(-3,3,1), x_length=9, y_length=5, x_label="x", y_label="y") -> (ax, labels)  # NOT yet added to scene
- plot(ax, f, x_range=None, color=None) -> graph           # f is a python lambda
- glow_dot(point, color=None) -> VGroup
- derive(scene, [latex1, latex2, ...], size=56)            # animated equation chain, returns last MathTex
- highlight(scene, mob)                                    # circumscribe
- arrow_label(start, end, text) -> VGroup
- sync(scene, t)                                           # wait until t seconds — call before each narration beat
- clear(scene)                                             # fade everything out
"""
