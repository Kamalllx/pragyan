```python
# Manim Community v0.19.0
# To render this animation, run the following command in your terminal:
# manim -pql basic_trigonometry.py BasicTrigonometry

from manim import *

class BasicTrigonometry(Scene):
    """
    An educational Manim animation for beginners introducing the basic concepts of trigonometry.
    This animation covers:
    1. The definition of a right-angled triangle and its sides (Opposite, Adjacent, Hypotenuse).
    2. The mnemonic SOH CAH TOA.
    3. The definitions of Sine, Cosine, and Tangent.
    4. A calculated example using a 3-4-5 triangle.
    5. A practical application of finding a missing side length.
    """
    def construct(self):
        # Set a consistent color scheme
        opp_color = BLUE
        adj_color = RED
        hyp_color = YELLOW

        # --- 1. Title Introduction ---
        title = Text("Introduction to Trigonometry", font_size=56)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        self.wait(0.5)

        # --- 2. The Right-Angled Triangle ---
        intro_text = Text("It all starts with a special triangle...", font_size=36).to_edge(UP)
        self.play(Write(intro_text))
        self.wait(1)

        # Define triangle vertices and create the triangle
        A = [-2, -1.5, 0]  # Right angle vertex
        B = [2, -1.5, 0]   # Vertex for angle theta
        C = [-2, 1.5, 0]
        triangle = Polygon(A, B, C, color=WHITE, stroke_width=6)
        
        # Add a right-angle symbol
        right_angle = Square(side_length=0.4, color=WHITE).move_to(A + RIGHT * 0.2 + UP * 0.2)

        # Add the angle theta
        angle_theta = Angle(Line(B, A), Line(B, C), radius=0.7, color=WHITE)
        theta_label = MathTex(r"\theta", font_size=48).move_to(B + LEFT * 1.0 + UP * 0.5)

        triangle_group = VGroup(triangle, right_angle, angle_theta, theta_label)
        self.play(Create(triangle_group), FadeOut(intro_text))
        self.wait(1)

        # Label the sides relative to theta
        side_intro = Text("The sides have special names relative to the angle θ:", font_size=36).to_edge(UP)
        self.play(Write(side_intro))

        # Braces and labels for each side
        hyp_brace = Brace(Line(B, C), direction=UR)
        opp_brace = Brace(Line(A, C), direction=LEFT)
        adj_brace = Brace(Line(A, B), direction=DOWN)

        hyp_label = hyp_brace.get_text("Hypotenuse").set_color(hyp_color)
        opp_label = opp_brace.get_text("Opposite").set_color(opp_color)
        adj_label = adj_brace.get_text("Adjacent").set_color(adj_color)

        self.play(
            Create(opp_brace), Write(opp_label),
            run_time=1.5
        )
        self.wait(0.5)
        self.play(
            Create(adj_brace), Write(adj_label),
            run_time=1.5
        )
        self.wait(0.5)
        self.play(
            Create(hyp_brace), Write(hyp_label),
            run_time=1.5
        )
        self.wait(2)

        side_labels_group = VGroup(hyp_brace, opp_brace, adj_brace, hyp_label, opp_label, adj_label)
        self.play(FadeOut(side_intro), FadeOut(side_labels_group))
        self.wait(1)

        # --- 3. SOH CAH TOA ---
        # Move triangle to the left
        self.play(triangle_group.animate.scale(0.8).to_edge(LEFT, buff=1))
        self.wait(1)

        # Display SOH CAH TOA mnemonic
        sohcahtoa = MathTex(
            r"\text{SOH}", r"\quad", r"\text{CAH}", r"\quad", r"\text{TOA}",
            font_size=60
        ).to_edge(RIGHT, buff=2).shift(UP*2)
        self.play(Write(sohcahtoa))
        self.wait(1)

        # Explain each part
        # The triangle sides are indexed as: 0=AB (Adjacent), 1=BC (Hypotenuse), 2=CA (Opposite)
        adj_side = triangle.get_lines()[0]
        hyp_side = triangle.get_lines()[1]
        opp_side = triangle.get_lines()[2]

        # SOH: Sine
        sin_formula = MathTex(r"\sin(\theta) = \frac{\text{Opposite}}{\text{Hypotenuse}}", font_size=48).next_to(sohcahtoa, DOWN, buff=1)
        sin_formula.set_color_by_tex("Opposite", opp_color)
        sin_formula.set_color_by_tex("Hypotenuse", hyp_color)
        
        self.play(Indicate(sohcahtoa[0]))
        self.play(Write(sin_formula))
        self.play(
            opp_side.animate.set_color(opp_color),
            hyp_side.animate.set_color(hyp_color),
            run_time=1.5
        )
        self.wait(2)
        self.play(
            opp_side.animate.set_color(WHITE),
            hyp_side.animate.set_color(WHITE)
        )