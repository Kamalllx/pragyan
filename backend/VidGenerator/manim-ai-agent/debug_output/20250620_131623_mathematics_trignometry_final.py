Of course. Here is the complete and corrected Manim code. The truncated lines have been finished, and the logic has been extended to include the final "sample problem" section as described in the docstring.

```python
from manim import *
import numpy as np

class TrigonometryBasics(Scene):
    """
    An animation explaining the basics of trigonometry for beginners.
    This scene covers:
    1. The definition of a right-angled triangle and its sides.
    2. The SOH CAH TOA mnemonic.
    3. The formulas for Sine, Cosine, and Tangent with a concrete example.
    4. A sample problem to find a missing side.
    """
    def construct(self):
        # -----------------------------------------------------------------
        # 1. Introduction Title
        # -----------------------------------------------------------------
        title = Text("Introduction to Trigonometry", font_size=48)
        subtitle = Text("The study of relationships in triangles", font_size=36).next_to(title, DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        self.wait(1)

        # -----------------------------------------------------------------
        # 2. The Right-Angled Triangle
        # -----------------------------------------------------------------
        
        # Create axes for a clear coordinate system context
        axes = Axes(
            x_range=[0, 6, 1],
            y_range=[0, 4, 1],
            x_length=8,
            y_length=5,
            axis_config={"color": BLUE},
        ).to_edge(DL, buff=1)

        # Define triangle vertices based on a 3-4-5 triangle
        A = axes.c2p(0, 0)  # Origin
        B = axes.c2p(4, 0)  # Adjacent corner
        C = axes.c2p(4, 3)  # Opposite corner

        # Create the triangle and a right-angle symbol
        triangle = Polygon(A, B, C, color=WHITE, fill_opacity=0.2)
        right_angle = Square(side_length=0.4, color=RED, fill_opacity=1).move_to(B, aligned_edge=UL)

        # Create the angle theta at the origin
        angle_theta = Angle(Line(B, A), Line(C, A), radius=0.8, color=YELLOW)
        theta_label = MathTex(r"\theta").move_to(
            Angle(Line(B, A), Line(C, A), radius=1.1).get_center()
        )

        # Group all triangle components
        triangle_group = VGroup(triangle, right_angle, angle_theta, theta_label)

        self.play(Create(axes), run_time=2)
        self.play(Create(triangle_group), run_time=2)
        self.wait(1)

        # Label the sides of the triangle relative to theta
        hyp_label_group = VGroup(
            Text("Hypotenuse", font_size=28, color=YELLOW), MathTex("= 5", color=YELLOW)
        ).arrange(DOWN).next_to(Line(A, C).get_center(), UP, buff=0.2).rotate(angle_theta.get_value())
        
        opp_label_group = VGroup(
            Text("Opposite", font_size=28, color=GREEN), MathTex("= 3", color=GREEN)
        ).arrange(DOWN).next_to(Line(B, C).get_center(), RIGHT, buff=0.2)
        
        adj_label_group = VGroup(
            Text("Adjacent", font_size=28, color=ORANGE), MathTex("= 4", color=ORANGE)
        ).arrange(DOWN).next_to(Line(A, B).get_center(), DOWN, buff=0.2)

        self.play(Write(hyp_label_group), Write(opp_label_group), Write(adj_label_group))
        self.wait(2)

        # -----------------------------------------------------------------
        # 3. SOH CAH TOA and the Ratios
        # -----------------------------------------------------------------
        
        # Display the SOH CAH TOA mnemonic
        soh_cah_toa = MathTex(r"\text{SOH CAH TOA}", font_size=48).to_edge(UR, buff=1)
        self.play
        self.wait(2)