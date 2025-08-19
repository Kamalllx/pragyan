from manim import *

class PythagorasTheoremScene(Scene):
    """
    An animation to explain the Pythagoras Theorem for beginners.
    This scene introduces the theorem, shows a practical example with step-by-step
    calculations, and summarizes the key concept.
    """
    def construct(self):
        # Set a consistent color scheme
        color_a = BLUE
        color_b = GREEN
        color_c = YELLOW

        # 1. Title Introduction
        title = Text("The Pythagorean Theorem", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # 2. Main educational content: Introduce the right-angled triangle
        # Define vertices for the triangle
        v1 = [-2, -1.5, 0]  # Bottom-left vertex
        v2 = [2, -1.5, 0]   # Bottom-right vertex
        v3 = [-2, 1.5, 0]   # Top-left vertex

        # Create the triangle from vertices
        triangle = Polygon(v1, v2, v3, color=WHITE, stroke_width=6)

        # Create the right-angle symbol
        right_angle = Square(side_length=0.4, color=WHITE, stroke_width=4)
        right_angle.move_to(v1 + RIGHT * 0.2 + UP * 0.2)

        # Label the sides
        label_a = MathTex("a", color=color_a, font_size=42).next_to(Line(v1, v3), LEFT, buff=0.4)
        label_b = MathTex("b", color=color_b, font_size=42).next_to(Line(v1, v2), DOWN, buff=0.4)
        label_c = MathTex("c", color=color_c, font_size=42).next_to(Line(v2, v3), UR, buff=0.2)

        # Group the triangle and its labels for easy management
        triangle_group = VGroup(triangle, right_angle, label_a, label_b, label_c)
        triangle_group.move_to(LEFT * 3)

        self.play(Create(triangle_group))
        self.wait(1)

        # 3. State the theorem formula
        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=60)
        formula.set_color_by_tex("a^2", color_a)
        formula.set_color_by_tex("b^2", color_b)
        formula.set_color_by_tex("c^2", color_c)
        formula.next_to(triangle_group, RIGHT, buff=1.0)

        self.play(Write(formula))
        self.wait(2)

        # Explanation text
        explanation = Text("It relates the sides of a right-angled triangle.", font_size=24)
        explanation.next_to(formula, DOWN, buff=0.8)
        self.play(FadeIn(explanation))
        self.wait(2)

        # Fade out the general explanation to make space for the example
        self.play(FadeOut(triangle_group), FadeOut(formula), FadeOut(explanation))
        self.wait(1)

        # 4. Example Application
        # Create a new triangle for the example (a 3-4-5 triangle)
        ex_v1 = [-2, -1, 0]
        ex_v2 = [2, -1, 0] # Base length = 4
        ex_v3 = [-2, 2, 0] # Height = 3

        ex_triangle = Polygon(ex_v1, ex_v2, ex_v3, color=WHITE, stroke_width=6)
        ex_right_angle = Square(side_length=0.4, color=WHITE, stroke_width=4).move_to(ex_v1 + RIGHT * 0.2 + UP * 0.2)

        # Labels with numerical values
        ex_label_a = MathTex("a = 3", color=color_a, font_size=42).next_to(Line(ex_v1, ex_v3), LEFT, buff=0.4)
        ex_label_b = MathTex("b = 4", color=color_b, font_size=42).next_to(Line(ex_v1, ex_v2), DOWN, buff=0.4)
        ex_label_c = MathTex("c = ?", color=color_c, font_size=42).next_to(Line(ex_v2, ex_v3), UR, buff=0.2)

        ex_triangle_group = VGroup(ex_triangle, ex_right_angle, ex_label_a, ex_label_b, ex_label_c)
        ex_triangle_group.move_to(LEFT * 3.5)

        self.play(Create(ex_triangle_group))
        self.wait(1)

        # Step-by-step calculation
        calc_title = Text("Let's find 'c'", font_size=32).to_edge(RIGHT, buff=1.5).shift(UP*2.5)
        
        # Position the calculation steps vertically
        calc_steps = VGroup(
            MathTex("a^2 + b^2 = c^2"),
            MathTex("3^2 + 4^2 = c^2"),
            MathTex("9 + 16 = c^2"),
            MathTex("25 = c^2"),
            MathTex(r"c = \sqrt{25}"),
            MathTex("c = 5")
        ).arrange(DOWN, buff=0.6).next_to(calc_title, DOWN, buff=0.6)

        # Animate each step of the calculation
        self.play(Write(calc_title))
        self.wait(0.5)
        
        self.play(Write(calc_steps[0]))
        self.wait(1)
        
        self.play(Transform(calc_steps[0], calc_steps[1]))
        self.wait(1)

        self.play(Transform(calc_steps[1], calc_steps[2]))
        self.wait(1)

        self.play(Transform(calc_steps[2], calc_steps[3]))
        self.wait(1)

        self.play(Transform(calc_steps[3], calc_steps[4]))
        self.wait(1)

        self.play(Transform(calc_steps[4], calc_steps[5]))
        self.wait(1)

        # Update the triangle with the final answer
        final_c_label = MathTex("c = 5", color=color_c, font_size=42).move_to(ex_label_c)
        self.play(Indicate(calc_steps[5]), Transform(ex_label_c, final_c_label))
        self.wait(2)

        # 5. Summary and Conclusion
        # Clear the example
        self.play(
            FadeOut(ex_triangle_group),
            FadeOut(calc_title),
            FadeOut(calc_steps[0]),
            FadeOut(calc_steps[1]),
            FadeOut(calc_steps[2]),
            FadeOut(calc_steps[3]),
            FadeOut(calc_steps[4]),
            FadeOut(calc_steps[5]),
            FadeOut(ex_label_c)
        )
        self.wait(1)

        # Bring back the main formula for emphasis
        summary_formula = MathTex("a^2 + b^2 = c^2", font_size=70)
        summary_formula.set_color_by_tex("a^2", color_a)
        summary_formula.set_color_by_tex("b^2", color_b)
        summary_formula.set_color_by_tex("c^2", color_c)
        summary_formula.move_to(ORIGIN)

        # Add a concluding remark
        conclusion = Text("A fundamental rule for right-angled triangles!", font_size=28)
        conclusion.next_to(summary_formula, DOWN, buff=1.0)

        self.play(FadeIn(summary_formula, scale=1.2))
        self.play(Write(conclusion))
        self.wait(3)

        # Final fade out
        self.play(FadeOut(title), FadeOut(summary_formula), FadeOut(conclusion))
        self.wait(2)