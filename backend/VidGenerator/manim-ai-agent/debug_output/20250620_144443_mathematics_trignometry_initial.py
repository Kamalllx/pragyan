An expert Manim developer who writes EXECUTION-TESTED, ERROR-FREE code.

Here is a complete, execution-ready Manim animation script on the basics of trigonometry.

```python
from manim import *

class TrigonometryIntroduction(Scene):
    """
    An introductory Manim scene explaining the basics of trigonometry,
    covering right-angled triangles, SOH CAH TOA, a worked example,
    and the unit circle.
    """
    def construct(self):
        # --- SCENE 1: INTRODUCTION ---
        self.intro_scene()

        # --- SCENE 2: RIGHT-ANGLED TRIANGLE AND SOH CAH TOA ---
        self.right_triangle_scene()

        # --- SCENE 3: WORKED EXAMPLE ---
        self.example_scene()

        # --- SCENE 4: THE UNIT CIRCLE ---
        self.unit_circle_scene()
        
        # --- SCENE 5: SUMMARY ---
        self.summary_scene()

    def intro_scene(self):
        """Displays the title and a brief introduction to trigonometry."""
        title = Text("Introduction to Trigonometry", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        intro_text = Text(
            "Trigonometry is the study of the relationship\n"
            "between angles and side lengths of triangles.",
            font_size=36,
            line_spacing=1.5,
            text_align=CENTER
        ).next_to(title, DOWN, buff=0.5)
        self.play(Write(intro_text), run_time=3)
        self.wait(2)
        
        self.play(FadeOut(intro_text), FadeOut(title))
        self.wait(1)

    def right_triangle_scene(self):
        """Draws a right-angled triangle and explains the trigonometric ratios."""
        # --- Create the triangle and its components ---
        # Vertices
        A = [-4, -1.5, 0]
        B = [0, -1.5, 0]
        C = [0, 1.5, 0]

        # Mobjects
        triangle = Polygon(A, B, C, color=WHITE)
        right_angle = Square(side_length=0.4, color=RED).move_to(B, aligned_edge=DL)
        angle_theta = Angle(Line(B, A), Line(A, C), radius=0.8, color=YELLOW)
        label_theta = MathTex(r"\theta").move_to(
            Angle(Line(B, A), Line(A, C), radius=1.1).get_center()
        )
        
        triangle_group = VGroup(triangle, right_angle, angle_theta, label_theta)
        
        # --- Animate the triangle creation ---
        scene_title = Text("The Right-Angled Triangle", font_size=40).to_edge(UP)
        self.play(Write(scene_title))
        self.play(Create(triangle))
        self.play(Create(right_angle))
        self.play(Create(angle_theta), Write(label_theta))
        self.wait(2)

        # --- Label the sides ---
        side_AC = Line(A, C)
        side_AB = Line(A, B)
        side_BC = Line(B, C)

        brace_hyp = Brace(side_AC, direction=side_AC.copy().rotate(PI/2).get_unit_vector(), color=BLUE)
        label_hyp = brace_hyp.get_text("Hypotenuse").set_color(BLUE)

        brace_adj = Brace(side_AB, direction=DOWN, color=GREEN)
        label_adj = brace_adj.get_text("Adjacent").set_color(GREEN)

        brace_opp = Brace(side_BC, direction=RIGHT, color=RED)
        label_opp = brace_opp.get_text("Opposite").set_color(RED)
        
        side_labels = VGroup(brace_hyp, label_hyp, brace_adj, label_adj, brace_opp, label_opp)

        self.play(Create(brace_hyp), Write(label_hyp), run_time=1.5)
        self.wait(0.5)
        self.play(Create(brace_adj), Write(label_adj), run_time=1.5)
        self.wait(0.5)
        self.play(Create(brace_opp), Write(label_opp), run_time=1.5)
        self.wait(2)

        # --- Introduce SOH CAH TOA ---
        soh_cah_toa = MathTex(r"\text{SOH CAH TOA}", font_size=60).to_edge(RIGHT, buff=1)
        self.play(Write(soh_cah_toa))
        self.wait(1)

        # Formulas
        formulas = VGroup(
            MathTex(r"\sin(\theta) = \frac{\text{Opposite}}{\text{Hypotenuse}}", font_size=42),
            MathTex(r"\cos(\theta) = \frac{\text{Adjacent}}{\text{Hypotenuse}}", font_size=42),
            MathTex(r"\tan(\theta) = \frac{\text{Opposite}}{\text{Adjacent}}", font_size=42)
        ).arrange(DOWN, buff=0.5).next_to(soh_cah_toa, DOWN, buff=0.5)
        
        # Animate Sine
        self.play(Indicate(soh_cah_toa[0][0:3], color=YELLOW))
        self.play(Write(formulas[0]))
        self.play(Indicate(VGroup(brace_opp, label_opp), color=RED), Indicate(VGroup(brace_hyp, label_hyp), color=BLUE))
        self.wait(2)

        # Animate Cosine
        self.play(Indicate(soh_cah_toa[0][4:7], color=YELLOW))
        self.play(Write(formulas[1]))
        self.play(Indicate(VGroup(brace_adj, label_adj), color=GREEN), Indicate(VGroup(brace_hyp, label_hyp), color=BLUE))
        self.wait(2)

        # Animate Tangent
        self.play(Indicate(soh_cah_toa[0][8:11], color=YELLOW))
        self.play(Write(formulas[2]))
        self.play(Indicate(VGroup(brace_opp, label_opp), color=RED), Indicate(VGroup(brace_adj, label_adj), color=GREEN))
        self.wait(2)

        # --- Cleanup ---
        self.play(
            FadeOut(scene_title), FadeOut(triangle_group), FadeOut(side_labels),
            FadeOut(soh_cah_toa), FadeOut(formulas)
        )
        self.wait(1)

    def example_scene(self):
        """Shows a worked example with a 3-4-5 triangle."""
        # --- Setup scene ---
        example_title = Text("A Worked Example", font_size=48).to_edge(UP)
        self.play(Write(example_title))

        axes = Axes(
            x_range=[0, 5, 1], y_range=[0, 4, 1],
            x_length=8, y_length=5,
            axis_config={"color": BLUE}
        ).add_coordinates().to_edge(LEFT, buff=1)
        self.play(Create(axes))

        # --- Create 3-4-5 triangle ---
        p1 = axes.c2p(0, 0)
        p2 = axes.c2p(4, 0)
        p3 = axes.c2p(4, 3)

        triangle_ex = Polygon(p1, p2, p3, color=WHITE, fill_opacity=0.2)
        label_adj_val = MathTex("4", color=GREEN).next_to(Line(p1, p2), DOWN)
        label_opp_val = MathTex("3", color=RED).next_to(Line