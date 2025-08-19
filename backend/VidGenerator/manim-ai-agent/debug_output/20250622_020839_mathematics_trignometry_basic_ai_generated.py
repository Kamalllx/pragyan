# Manim Community v0.19.0

from manim import *

class BasicTrigonometry(Scene):
    def construct(self):
        # Define colors for consistency
        angle_color = PURE_RED
        hyp_color = PURE_BLUE
        opp_color = PURE_GREEN
        adj_color = YELLOW

        # --- 1. Title Introduction ---
        title = Text("Introduction to Trigonometry", font_size=48)
        subtitle = Text("The study of triangles and their angles", font_size=32).next_to(title, DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        self.wait(1)

        # --- 2. Main Educational Content: The Right-Angled Triangle ---
        intro_text = Text("Trigonometry helps us relate angles and side lengths.", font_size=36).to_edge(UP)
        focus_text = Text("It starts with a special triangle: the right-angled triangle.", font_size=36).next_to(intro_text, DOWN, buff=0.5)
        
        self.play(Write(intro_text))
        self.wait(1)
        self.play(Write(focus_text))
        self.wait(1)

        # Create a right-angled triangle on a coordinate system
        axes = Axes(
            x_range=[0, 7, 1],
            y_range=[0, 5, 1],
            axis_config={"color": GRAY}
        ).add_coordinates()
        
        # Define triangle vertices
        A = axes.coords_to_point(0, 0)
        B = axes.coords_to_point(4, 0)
        C = axes.coords_to_point(4, 3)

        triangle = Polygon(A, B, C, color=WHITE, fill_opacity=0.2)
        
        self.play(FadeOut(intro_text), FadeOut(focus_text))
        self.play(Create(axes), run_time=2)
        self.play(Create(triangle))
        self.wait(1)

        # Label the sides and angle
        right_angle = Square(side_length=0.4, color=angle_color).move_to(B, aligned_edge=DL)
        angle = Angle(Line(B, A), Line(C, A), radius=0.8, color=angle_color)
        angle_label = MathTex(r"\theta", color=angle_color).move_to(
            angle.point_from_proportion(0.5) + 0.3 * RIGHT + 0.1 * UP
        )

        self.play(Create(right_angle))
        self.play(Write(Text("90°", font_size=24).next_to(right_angle, UR, buff=0.1)))
        self.wait(0.5)
        self.play(Create(angle), Write(angle_label))
        self.wait(1)

        # --- 3. Key Concepts: Opposite, Adjacent, Hypotenuse ---
        
        # Label the sides relative to theta
        hyp_brace = Brace(Line(A, C), direction=Line(C,A).copy().rotate(PI/2).get_unit_vector(), color=hyp_color)
        opp_brace = Brace(Line(B, C), direction=RIGHT, color=opp_color)
        adj_brace = Brace(Line(A, B), direction=DOWN, color=adj_color)

        hyp_label = hyp_brace.get_text("Hypotenuse").set_color(hyp_color)
        opp_label = opp_brace.get_text("Opposite").set_color(opp_color)
        adj_label = adj_brace.get_text("Adjacent").set_color(adj_color)

        # Animate labels appearing one by one
        self.play(Create(hyp_brace), Write(hyp_label))
        self.wait(1)
        self.play(Create(opp_brace), Write(opp_label))
        self.wait(1)
        self.play(Create(adj_brace), Write(adj_label))
        self.wait(1)

        triangle_group = VGroup(axes, triangle, right_angle, angle, angle_label, hyp_brace, opp_brace, adj_brace, hyp_label, opp_label, adj_label)
        self.play(triangle_group.animate.scale(0.7).to_edge(LEFT, buff=0.5))
        self.wait(1)

        # Introduce SOH CAH TOA
        sohcahtoa_title = Text("The Trigonometric Ratios", font_size=40).to_edge(UP).shift(RIGHT*3)
        self.play(Write(sohcahtoa_title))

        # Sine
        sine_formula = MathTex(r"\sin(\theta) = \frac{\text{Opposite}}{\text{Hypotenuse}}", font_size=42).next_to(sohcahtoa_title, DOWN, buff=0.7)
        sine_formula.set_color_by_tex("Opposite", opp_color)
        sine_formula.set_color_by_tex("Hypotenuse", hyp_color)
        
        self.play(Write(sine_formula))
        self.play(Indicate(VGroup(opp_label, opp_brace)), Indicate(VGroup(hyp_label, hyp_brace)))
        self.wait(1)

        # Cosine
        cosine_formula = MathTex(r"\cos(\theta) = \frac{\text{Adjacent}}{\text{Hypotenuse}}", font_size=42).next_to(sine_formula, DOWN, buff=0.7)
        cosine_formula.set_color_by_tex("Adjacent", adj_color)
        cosine_formula.set_color_by_tex("Hypotenuse", hyp_color)

        self.play(Write(cosine_formula))
        self.play(Indicate(VGroup(adj_label, adj_brace)), Indicate(VGroup(hyp_label, hyp_brace)))
        self.wait(1)

        # Tangent
        tangent_formula = MathTex(r"\tan(\theta) = \frac{\text{Opposite}}{\text{Adjacent}}", font_size=42).next_to(cosine_formula, DOWN, buff=0.7)
        tangent_formula.set_color_by_tex("Opposite", opp_color)
        tangent_formula.set_color_by_tex("Adjacent", adj_color)

        self.play(Write(tangent_formula))
        self.play(Indicate(VGroup(opp_label, opp_brace)), Indicate(VGroup(adj_label, adj_brace)))
        self.wait(1)

        # Mnemonic
        mnemonic = Text("SOH CAH TOA", font_size=48, color=GOLD).next_to(tangent_formula, DOWN, buff=1)
        self.play(Write(mnemonic))
        self.wait(2)

        # --- 4. Example with Calculation ---
        formulas_group = VGroup(sohcahtoa_title, sine_formula, cosine_formula, tangent_formula, mnemonic)
        self.play(FadeOut(triangle_group), FadeOut(formulas_group))
        self.wait(1)

        example_title = Text("Let's see an example", font_size=40).to_edge(UP)
        self.play(Write(example_title))

        # Create a 3-4-5 triangle
        ax_ex = Axes(x_range=[0, 5, 1], y_range=[0, 4, 1]).add_coordinates()
        A_ex = ax_ex.c2p(0, 0)
        B_ex = ax_ex.c2p(4, 0)
        C_ex = ax_ex.c2p(4, 3)
        
        tri_ex = Polygon(A_ex, B_ex, C_ex, color=WHITE)
        
        # Side length labels
        adj_len = MathTex("4").next_to(Line(A_ex, B_ex), DOWN, buff=0.2).set_color(adj_color)
        opp_len = MathTex("3").next_to(Line(B_ex, C_ex), RIGHT, buff=0.2).set_color(opp_color)
        hyp_len = MathTex("5").next_to(Line(A_ex, C_ex), UP + LEFT, buff=0.1).set_color(hyp_color)
        
        angle_ex = Angle(Line(B_ex, A_ex), Line(C_ex, A_ex), radius=0.6, color=angle_color)
        angle_ex_label = MathTex(r"\theta", color=angle_color).move_to(angle_ex.point_from_proportion(0.5) + 0.2*RIGHT + 0.1*UP)

        example_triangle_group = VGroup(ax_ex, tri_ex, adj_len, opp_len, hyp_len, angle_ex, angle_ex_label).scale(0.9).to_edge(LEFT)
        self.play(Create(example_triangle_group))
        self.wait(1)

        # Step-by-step calculations
        calc_title = Text("Calculations:", font_size=36).next_to(ax_ex, RIGHT, buff=1.5).align_to(ax_ex, UP)
        self.play(Write(calc_title))

        # Sine calculation
        sin_calc_1 = MathTex(r"\sin(\theta) = \frac{\text{Opp}}{\text{Hyp}}", font_size=36).next_to(calc_title, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(sin_calc_1))
        self.wait(0.5)
        sin_calc_2 = MathTex(r"= \frac{3}{5}", font_size=36).next_to(sin_calc_1, RIGHT, buff=0.2)
        sin_calc_2.set_color_by_tex("3", opp_color)
        sin_calc_2.set_color_by_tex("5", hyp_color)
        self.play(Transform(VGroup(opp_len.copy(), hyp_len.copy()), sin_calc_2))
        self.wait(0.5)
        sin_calc_3 = MathTex(r"= 0.6", font_size=36).next_to(sin_calc_2, RIGHT, buff=0.2)
        self.play(Write(sin_calc_3))
        self.wait(1)

        # Cosine calculation
        cos_calc_1 = MathTex(r"\cos(\theta) = \frac{\text{Adj}}{\text{Hyp}}", font_size=36).next_to(sin_calc_1, DOWN, buff=0.7, aligned_edge=LEFT)
        self.play(Write(cos_calc_1))
        self.wait(0.5)
        cos_calc_2 = MathTex(r"= \frac{4}{5}", font_size=36).next_to(cos_calc_1, RIGHT, buff=0.2)
        cos_calc_2.set_color_by_tex("4", adj_color)
        cos_calc_2.set_color_by_tex("5", hyp_color)
        self.play(Transform(VGroup(adj_len.copy(), hyp_len.copy()), cos_calc_2))
        self.wait(0.5)
        cos_calc_3 = MathTex(r"= 0.8", font_size=36).next_to(cos_calc_2, RIGHT, buff=0.2)
        self.play(Write(cos_calc_3))
        self.wait(1)

        # Tangent calculation
        tan_calc_1 = MathTex(r"\tan(\theta) = \frac{\text{Opp}}{\text{Adj}}", font_size=36).next_to(cos_calc_1, DOWN, buff=0.7, aligned_edge=LEFT)
        self.play(Write(tan_calc_1))
        self.wait(0.5)
        tan_calc_2 = MathTex(r"= \frac{3}{4}", font_size=36).next_to(tan_calc_1, RIGHT, buff=0.2)
        tan_calc_2.set_color_by_tex("3", opp_color)
        tan_calc_2.set_color_by_tex("4", adj_color)
        self.play(Transform(VGroup(opp_len.copy(), adj_len.copy()), tan_calc_2))
        self.wait(0.5)
        tan_calc_3 = MathTex(r"= 0.75", font_size=36).next_to(tan_calc_2, RIGHT, buff=0.2)
        self.play(Write(tan_calc_3))
        self.wait(2)

        # --- 5. Summary and Conclusion ---
        calculations_group = VGroup(calc_title, sin_calc_1, sin_calc_2, sin_calc_3, cos_calc_1, cos_calc_2, cos_calc_3, tan_calc_1, tan_calc_2, tan_calc_3)
        self.play(FadeOut(example_title), FadeOut(example_triangle_group), FadeOut(calculations_group))
        self.wait(1)

        summary_title = Text("Key Summary", font_size=48).to_edge(UP)
        self.play(Write(summary_title))

        # Re-show the labeled triangle
        summary_triangle_group = VGroup(triangle, right_angle, angle, angle_label, hyp_brace, opp_brace, adj_brace, hyp_label, opp_label, adj_label).scale(0.8).move_to(LEFT * 3.5)
        summary_triangle_group.remove(axes) # remove axes for cleaner look
        self.play(FadeIn(summary_triangle_group))

        # Re-show the formulas
        summary_formulas = VGroup(
            MathTex(r"\sin(\theta) = \frac{\text{Opposite}}{\text{Hypotenuse}}").set_color_by_tex_to_color_map({"Opposite": opp_color, "Hypotenuse": hyp_color}),
            MathTex(r"\cos(\theta) = \frac{\text{Adjacent}}{\text{Hypotenuse}}").set_color_by_tex_to_color_map({"Adjacent": adj_color, "Hypotenuse": hyp_color}),
            MathTex(r"\tan(\theta) = \frac{\text{Opposite}}{\text{Adjacent}}").set_color_by_tex_to_color_map({"Opposite": opp_color, "Adjacent": adj_color})
        ).arrange(DOWN, buff=0.8, aligned_edge=LEFT).scale(0.9).next_to(summary_triangle_group, RIGHT, buff=1)

        summary_mnemonic = Text("SOH CAH TOA", color=GOLD, font_size=48).next_to(summary_formulas, DOWN, buff=1)

        self.play(Write(summary_formulas))
        self.wait(1)
        self.play(Write(summary_mnemonic))
        self.wait(2)

        final_text = Text("Trigonometry is a powerful tool in math and science!", font_size=36).next_to(summary_mnemonic, DOWN, buff=1.5)
        self.play(FadeIn(final_text))
        self.wait(2)

        # Final fade out
        self.play(FadeOut(summary_title), FadeOut(summary_triangle_group), FadeOut(summary_formulas), FadeOut(summary_mnemonic), FadeOut(final_text))
        self.wait(2)