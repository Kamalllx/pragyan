from manim import *

class PythagoreanTheoremScene(Scene):
    """
    An intermediate-level animation explaining the Pythagorean Theorem,
    including its formula, a visual representation, a numerical example,
    and a summary.
    """
    def construct(self):
        # 1. Title introduction
        title = Text("The Pythagorean Theorem", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # 2. Main educational content with visual demonstrations
        # Define triangle vertices for a right-angled triangle
        A = [-2, -1.5, 0]
        B = [2, -1.5, 0]
        C = [-2, 1.5, 0]

        # Create the triangle and a right-angle marker
        triangle = Polygon(A, B, C, color=BLUE, fill_opacity=0.6)
        right_angle = Square(side_length=0.4, color=WHITE).move_to(A, aligned_edge=DL)
        
        # Label the sides a, b, and c (hypotenuse)
        label_a = MathTex("a", font_size=36).next_to(Line(C, A), LEFT, buff=0.3)
        label_b = MathTex("b", font_size=36).next_to(Line(A, B), DOWN, buff=0.3)
        label_c = MathTex("c", font_size=36).next_to(Line(B, C), UP + RIGHT, buff=0.2)

        # Group all triangle elements for easier positioning
        triangle_group = VGroup(triangle, right_angle, label_a, label_b, label_c)
        triangle_group.move_to(LEFT * 3)

        self.play(Create(triangle_group))
        self.wait(1)

        # 3. Key concepts with clear explanations
        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=48)
        formula.next_to(triangle_group, RIGHT, buff=1.2)
        
        self.play(Write(formula))
        self.wait(1)

        # Indicate the relationship between the sides and the formula parts
        self.play(Indicate(VGroup(label_a, formula[0])))
        self.play(Indicate(VGroup(label_b, formula[2])))
        self.play(Indicate(VGroup(label_c, formula[4])))
        self.wait(2)

        # Clear the screen for the next section
        self.play(FadeOut(triangle_group), FadeOut(formula), FadeOut(title))
        self.wait(1)

        # 4. Examples or applications (Numerical Example)
        example_title = Text("A Practical Example", font_size=36).to_edge(UP)
        self.play(Write(example_title))

        # Create a 3-4-5 triangle for the example
        example_triangle = Polygon(A, B, C, color=GREEN, fill_opacity=0.6)
        
        # Label sides with their values
        val_a = MathTex("a=3").next_to(example_triangle.get_edge_center(LEFT), LEFT, buff=0.3)
        val_b = MathTex("b=4").next_to(example_triangle.get_edge_center(DOWN), DOWN, buff=0.3)
        val_c = MathTex("c=?").next_to(example_triangle.get_edge_center(UP+RIGHT), UP+RIGHT, buff=0.2)
        
        example_tri_group = VGroup(example_triangle, val_a, val_b, val_c).move_to(LEFT * 3.5)

        self.play(FadeIn(example_tri_group))
        self.wait(1)

        # Display the calculation steps one by one
        calc_steps = VGroup(
            MathTex("a^2 + b^2 = c^2"),
            MathTex("3^2 + 4^2 = c^2"),
            MathTex("9 + 16 = c^2"),
            MathTex("25 = c^2"),
            MathTex("c = \\sqrt{25}"),
            MathTex("c = 5")
        ).arrange(DOWN, buff=0.6).next_to(example_tri_group, RIGHT, buff=1.2)

        # Animate the calculation, transforming each step into the next
        self.play(Write(calc_steps[0]))
        self.wait(1)
        for i in range(1, len(calc_steps)):
            self.play(Transform(calc_steps[i-1], calc_steps[i]))
            self.wait(1.5)
        
        # Update the 'c' label on the triangle with the final result
        final_c = MathTex("c=5", color=YELLOW).move_to(val_c.get_center())
        self.play(Transform(val_c, final_c))
        self.wait(2)

        # Clear the screen for the summary
        self.play(FadeOut(example_tri_group), FadeOut(calc_steps[-1]), FadeOut(val_c), FadeOut(example_title))
        self.wait(1)

        # 5. Summary or conclusion
        summary_title = Text("Summary", font_size=40).to_edge(UP)
        
        summary_text = Text(
            "For any right-angled triangle, the square of the hypotenuse (c)\n"
            "is equal to the sum of the squares of the other two sides (a and b).",
            font_size=28,
            text_align=CENTER,
            line_spacing=1.0
        ).scale(0.9)
        
        summary_formula = MathTex("a^2 + b^2 = c^2", font_size=48, color=YELLOW)

        # Group summary elements and arrange them vertically
        summary_group = VGroup(summary_title, summary_text, summary_formula).arrange(DOWN, buff=0.8)
        summary_group.move_to(ORIGIN)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_text))
        self.wait(1)
        self.play(Write(summary_formula))

        self.wait(3)