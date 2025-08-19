# Manim Community v0.18.0
# To render this animation, run the following command in your terminal:
# manim -pql trig.py BasicTrig

from manim import *

class BasicTrig(Scene):
    """
    A simple, robust Manim animation for beginners explaining basic trigonometry (SOH CAH TOA).
    This animation is designed to be clear, slow-paced, and work reliably on Windows.
    """
    def construct(self):
        # 1. Introduction Title
        title = Text("Basics of Trigonometry", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        self.wait(0.5)

        # 2. Create the coordinate system and triangle
        # Using a number plane helps ground the concept in a familiar context.
        plane = NumberPlane(
            x_range=(0, 7, 1),
            y_range=(0, 5, 1),
            x_length=7,
            y_length=5,
            axis_config={"color": WHITE}
        ).to_edge(DL, buff=0.5)

        # Define the vertices of a simple 3-4-5 right triangle
        A = plane.c2p(0, 0)  # Origin
        B = plane.c2p(4, 0)  # Adjacent vertex
        C = plane.c2p(4, 3)  # Opposite vertex

        # Create the triangle from lines
        line_ab = Line(A, B, color=GREEN) # Adjacent side
        line_bc = Line(B, C, color=RED)   # Opposite side
        line_ca = Line(C, A, color=BLUE)  # Hypotenuse

        # Create the right angle square
        right_angle = Square(side_length=0.3, color=WHITE, stroke_width=2).move_to(B, aligned_edge=DL)

        # Create the angle theta
        theta = Angle(line_ab, line_ca, radius=0.7, other_angle=False)
        theta_label = MathTex(r"\theta", font_size=36).move_to(
            Angle(line_ab, line_ca, radius=1).get_center()
        )

        triangle_group = VGroup(line_ab, line_bc, line_ca, right_angle, theta, theta_label)

        self.play(Create(plane), run_time=2)
        self.play(Create(triangle_group), run_time=2)
        self.wait(1)

        # 3. Label the sides of the triangle
        # Using braces makes the labels clear and distinct.
        brace_adj = Brace(line_ab, direction=DOWN, buff=0.2)
        label_adj = brace_adj.get_text("Adjacent = 4").set_color(GREEN)

        brace_opp = Brace(line_bc, direction=RIGHT, buff=0.2)
        label_opp = brace_opp.get_text("Opposite = 3").set_color(RED)

        brace_hyp = Brace(line_ca, direction=line_ca.get_unit_vector()*(-1), buff=0.2)
        label_hyp = brace_hyp.get_text("Hypotenuse = 5").set_color(BLUE)

        self.play(
            GrowFromCenter(brace_adj),
            Write(label_adj),
            run_time=1.5
        )
        self.play(
            GrowFromCenter(brace_opp),
            Write(label_opp),
            run_time=1.5
        )
        self.play(
            GrowFromCenter(brace_hyp),
            Write(label_hyp),
            run_time=1.5
        )
        self.wait(2)

        # 4. Introduce SOH CAH TOA
        # This mnemonic is central to beginner trigonometry.
        soh_cah_toa = Text("SOH CAH TOA", font_size=48).to_edge(UP)
        self.play(Write(soh_cah_toa))
        self.wait(1)

        # 5. Explain each part step-by-step
        # We create a VGroup for each calculation to animate them in and out smoothly.

        # SOH: Sine = Opposite / Hypotenuse
        sine_formula = MathTex(r"\sin(\theta) = \frac{\text{Opposite}}{\text{Hypotenuse}}", font_size=40)
        sine_formula.to_edge(UR, buff=1)
        sine_calc = MathTex(r"= \frac{3}{5} = 0.6", font_size=40).next_to(sine_formula, DOWN, aligned_edge=LEFT)
        
        # Color-code the formula to match the triangle sides
        sine_formula.get_part_by_tex("Opposite").set_color(RED)
        sine_formula.get_part_by_tex("Hypotenuse").set_color(BLUE)
        sine_calc.get_part_by_tex("3").set_color(RED)
        sine_calc.get_part_by_tex("5").set_color(BLUE)
        
        sine_group = VGroup(sine_formula, sine_calc)

        self.play(Write(sine_formula), run_time=2)
        self.play(Indicate(soh_cah_toa.get_part_by_text("SOH"), color=YELLOW))
        self.play(
            Indicate(label_opp, color=RED),
            Indicate(label_hyp, color=BLUE)
        )
        self.play(Write(sine_calc), run_time=2)
        self.wait(2)

        # CAH: Cosine = Adjacent / Hypotenuse
        cosine_formula = MathTex(r"\cos(\theta) = \frac{\text{Adjacent}}{\text{Hypotenuse}}", font_size=40)
        cosine_formula.to_edge(UR, buff=1)
        cosine_calc = MathTex(r"= \frac{4}{5} = 0.8", font_size=40).next_to(cosine_formula, DOWN, aligned_edge=LEFT)
        
        cosine_formula.get_part_by_tex("Adjacent").set_color(GREEN)
        cosine_formula.get_part_by_tex("Hypotenuse").set_color(BLUE)
        cosine_calc.get_part_by_tex("4").set_color(GREEN)
        cosine_calc.get_part_by_tex("5").set_color(BLUE)

        cosine_group = VGroup(cosine_formula, cosine_calc)

        self.play(ReplacementTransform(sine_group, cosine_group))
        self.play(Indicate(soh_cah_toa.get_part_by_text("CAH"), color=YELLOW))
        self.play(
            Indicate(label_adj, color=GREEN),
            Indicate(label_hyp, color=BLUE)
        )
        self.wait(2)

        # TOA: Tangent = Opposite / Adjacent
        tangent_formula = MathTex(r"\tan(\theta) = \frac{\text{Opposite}}{\text{Adjacent}}", font_size=40)
        tangent_formula.to_edge(UR, buff=1)
        tangent_calc = MathTex(r"= \frac{3}{4} = 0.75", font_size=40).next_to(tangent_formula, DOWN, aligned_edge=LEFT)
        
        tangent_formula.get_part_by_tex("Opposite").set_color(RED)
        tangent_formula.get_part_by_tex("Adjacent").set_color(GREEN)
        tangent_calc.get_part_by_tex("3").set_color(RED)
        tangent_calc.get_part_by_tex("4").set_color(GREEN)

        tangent_group = VGroup(tangent_formula, tangent_calc)

        self.play(ReplacementTransform(cosine_group, tangent_group))
        self.play(Indicate(soh_cah_toa.get_part_by_text("TOA"), color=YELLOW))
        self.play(
            Indicate(label_opp, color=RED),
            Indicate(label_adj, color=GREEN)
        )
        self.wait(2)

        # 6. Final Scene
        # Hold on the final result for a moment before ending.
        self.play(FadeOut(tangent_group))
        self.wait(1)
        
        final_text = Text("Trigonometry relates angles to side lengths!", font_size=36).to_edge(UP, buff=1.5)
        self.play(ReplacementTransform(soh_cah_toa, final_text))

        # End with a 2-second wait as required.
        self.wait(2)