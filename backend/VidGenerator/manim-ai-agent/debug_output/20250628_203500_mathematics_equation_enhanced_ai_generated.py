from manim import *

class QuadraticEquationSolution(Scene):
    """
    An animation demonstrating the step-by-step solution of a quadratic equation
    using the quadratic formula.
    This scene is designed for intermediate learners and follows best practices
    for clarity, layout, and modern Manim API usage.
    """
    def construct(self):
        # 1. Title Introduction
        title = MathTex(r"\text{Solving Quadratic Equations}", font_size=48)
        title.to_edge(UP, buff=0.8)
        
        # General form of a quadratic equation
        general_form = MathTex(r"ax^2 + bx + c = 0", font_size=36)
        general_form.next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(general_form, shift=DOWN))
        self.wait(2)

        # 2. Introduce the specific example
        example_eq = MathTex(r"x^2 - 5x + 6 = 0", font_size=40)
        example_eq.move_to(ORIGIN).shift(UP * 2.5)

        self.play(Transform(general_form, example_eq))
        self.wait(2)

        # 3. Identify coefficients a, b, and c
        coefficients_text = Text("Step 1: Identify coefficients a, b, c", font_size=28)
        coefficients_text.next_to(example_eq, DOWN, buff=0.8)
        
        a_val = MathTex("a = 1", font_size=36)
        b_val = MathTex("b = -5", font_size=36)
        c_val = MathTex("c = 6", font_size=36)
        
        coeffs_group = VGroup(a_val, b_val, c_val).arrange(RIGHT, buff=1.2)
        coeffs_group.next_to(coefficients_text, DOWN, buff=0.5)

        self.play(Write(coefficients_text))
        self.play(FadeIn(coeffs_group, shift=UP))
        self.wait(2)

        # 4. Introduce the Quadratic Formula
        formula_text = Text("Step 2: Use the Quadratic Formula", font_size=28)
        formula_text.move_to(ORIGIN).shift(DOWN * 0.5)
        
        quadratic_formula = MathTex(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}", font_size=48)
        quadratic_formula.next_to(formula_text, DOWN, buff=0.5)

        # Group previous elements to move them up
        intro_group = VGroup(general_form, coefficients_text, coeffs_group)
        self.play(
            intro_group.animate.shift(UP * 1.5),
            Write(formula_text),
            Write(quadratic_formula)
        )
        self.wait(2)

        # 5. Substitute values into the formula
        step3_text = Text("Step 3: Substitute the values", font_size=24).to_edge(LEFT).shift(UP*1)
        
        # Create the formula with substituted values
        substituted_formula = MathTex(r"x = \frac{-(-5) \pm \sqrt{(-5)^2 - 4(1)(6)}}{2(1)}", font_size=48)
        substituted_formula.move_to(quadratic_formula.get_center())

        self.play(FadeOut(formula_text), FadeIn(step3_text, shift=RIGHT))
        self.play(Transform(quadratic_formula, substituted_formula))
        self.wait(2)

        # 6. Simplify the expression step-by-step
        step4_text = Text("Step 4: Simplify the expression", font_size=24).next_to(step3_text, DOWN, buff=1.0, aligned_edge=LEFT)
        self.play(Write(step4_text))
        self.wait(1)

        # Simplification 1: Resolve signs and squares
        simp_1 = MathTex(r"x = \frac{5 \pm \sqrt{25 - 24}}{2}", font_size=48)
        simp_1.move_to(quadratic_formula.get_center())
        self.play(Transform(quadratic_formula, simp_1))
        self.wait(2)

        # Simplification 2: Simplify inside the square root
        simp_2 = MathTex(r"x = \frac{5 \pm \sqrt{1}}{2}", font_size=48)
        simp_2.move_to(quadratic_formula.get_center())
        self.play(Transform(quadratic_formula, simp_2))
        self.wait(2)

        # Simplification 3: Evaluate the square root
        simp_3 = MathTex(r"x = \frac{5 \pm 1}{2}", font_size=48)
        simp_3.move_to(quadratic_formula.get_center())
        self.play(Transform(quadratic_formula, simp_3))
        self.wait(2)

        # 7. Split into two solutions
        step5_text = Text("Step 5: Calculate the two solutions", font_size=24).next_to(step4_text, DOWN, buff=1.0, aligned_edge=LEFT)
        self.play(Write(step5_text))
        self.wait(1)

        # Create the two branches for x1 and x2
        x1_expr = MathTex(r"x_1 = \frac{5 + 1}{2}", font_size=40)
        x2_expr = MathTex(r"x_2 = \frac{5 - 1}{2}", font_size=40)
        
        solutions_group = VGroup(x1_expr, x2_expr).arrange(RIGHT, buff=2.0)
        solutions_group.move_to(ORIGIN).shift(DOWN * 2.0)

        # Animate the split
        self.play(
            FadeOut(VGroup(intro_group, step3_text, step4_text)),
            quadratic_formula.animate.move_to(ORIGIN).shift(UP*1.5),
            FadeIn(solutions_group, shift=UP)
        )
        self.wait(2)

        # 8. Calculate final answers
        x1_sol_1 = MathTex(r"x_1 = \frac{6}{2}", font_size=40).move_to(x1_expr)
        x1_sol_2 = MathTex(r"x_1 = 3", font_size=40).move_to(x1_expr)
        
        x2_sol_1 = MathTex(r"x_2 = \frac{4}{2}", font_size=40).move_to(x2_expr)
        x2_sol_2 = MathTex(r"x_2 = 2", font_size=40).move_to(x2_expr)

        self.play(Transform(x1_expr, x1_sol_1))
        self.wait(1)
        self.play(Transform(x1_expr, x1_sol_2))
        self.wait(1)

        self.play(Transform(x2_expr, x2_sol_1))
        self.wait(1)
        self.play(Transform(x2_expr, x2_sol_2))
        self.wait(2)

        # 9. Summary
        final_solutions = VGroup(x1_expr, x2_expr)
        solution_box = SurroundingRectangle(final_solutions, buff=0.5, color=GREEN)
        summary_text = Text("The solutions are:", font_size=32).next_to(solution_box, UP, buff=0.5)

        self.play(
            FadeOut(step5_text, quadratic_formula),
            final_solutions.animate.move_to(ORIGIN),
        )
        self.play(
            Write(summary_text),
            Create(solution_box)
        )
        self.wait(3)

        # Final fade out
        self.play(FadeOut(*self.mobjects))
        self.wait(1)