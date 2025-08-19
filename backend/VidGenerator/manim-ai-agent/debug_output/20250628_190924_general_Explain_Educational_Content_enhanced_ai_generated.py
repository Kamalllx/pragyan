from manim import *

class PythagoreanTheoremScene(Scene):
    """
    An intermediate-level Manim scene explaining the Pythagorean Theorem.
    This scene introduces the theorem, provides a visual proof using areas,
    and demonstrates a numerical example.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("The Pythagorean Theorem", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # 2. Main Educational Content: The Triangle and Theorem
        # Define triangle vertices for a 3-4-5 triangle scaled down
        # Base = 4 units, Height = 3 units
        triangle_vertices = [
            ORIGIN,          # Vertex at (0,0,0)
            RIGHT * 4,       # Vertex at (4,0,0)
            UP * 3,          # Vertex at (0,3,0)
        ]
        triangle = Polygon(*triangle_vertices, color=BLUE, fill_opacity=0.5)
        triangle.move_to(ORIGIN).shift(DOWN * 0.5)

        # Labels for the sides
        label_a = MathTex("a", color=YELLOW).next_to(triangle.get_sides()[2], LEFT, buff=0.3)
        label_b = MathTex("b", color=ORANGE).next_to(triangle.get_sides()[0], DOWN, buff=0.3)
        label_c = MathTex("c", color=RED).next_to(triangle.get_sides()[1], UP + RIGHT, buff=0.2)

        # Right angle marker
        right_angle = Square(side_length=0.4, color=WHITE, stroke_width=2)
        right_angle.move_to(triangle.get_vertices()[0], aligned_edge=DL)

        triangle_group = VGroup(triangle, label_a, label_b, label_c, right_angle)

        self.play(Create(triangle_group))
        self.wait(1)

        # State the theorem formula
        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=48)
        formula.next_to(triangle, DOWN, buff=1.0)
        # Color-code the formula to match the sides
        formula[0].set_color(YELLOW)
        formula[2].set_color(ORANGE)
        formula[4].set_color(RED)

        self.play(Write(formula))
        self.wait(2)

        # 3. Visual Demonstration with Squares
        # Fade out the formula to make space
        self.play(FadeOut(formula))

        # Create squares on each side
        square_a = Square(side_length=3, color=YELLOW, fill_opacity=0.6)
        square_b = Square(side_length=4, color=ORANGE, fill_opacity=0.6)
        square_c = Square(side_length=5, color=RED, fill_opacity=0.6)

        # Position the squares next to their corresponding sides
        square_a.next_to(triangle.get_sides()[2], LEFT, buff=0)
        square_b.next_to(triangle.get_sides()[0], DOWN, buff=0)
        
        # Position and rotate the hypotenuse square
        hypotenuse_vector = triangle.get_vertices()[1] - triangle.get_vertices()[2]
        angle = np.arctan2(hypotenuse_vector[1], hypotenuse_vector[0])
        square_c.rotate(angle)
        square_c.move_to(triangle.get_sides()[1].get_center())

        # Area labels
        area_a_label = MathTex("a^2", font_size=48, color=BLACK).move_to(square_a)
        area_b_label = MathTex("b^2", font_size=48, color=BLACK).move_to(square_b)
        area_c_label = MathTex("c^2", font_size=48, color=BLACK).move_to(square_c)

        squares_group = VGroup(square_a, square_b, square_c)
        area_labels_group = VGroup(area_a_label, area_b_label, area_c_label)

        # Animate the squares and their area labels
        self.play(
            FadeOut(label_a, label_b, label_c),
            Create(squares_group)
        )
        self.play(Write(area_labels_group))
        self.wait(1)

        # Show the relationship between areas
        area_equation = MathTex("Area(a^2) + Area(b^2) = Area(c^2)").to_edge(DOWN, buff=0.5)
        self.play(Write(area_equation))
        self.play(
            Indicate(VGroup(square_a, area_a_label)),
            Indicate(VGroup(square_b, area_b_label)),
        )
        self.play(Indicate(VGroup(square_c, area_c_label)))
        self.wait(2)

        # Clean up for the next section
        self.play(FadeOut(squares_group, area_labels_group, area_equation, triangle_group))

        # 4. Numerical Example
        example_title = Text("Numerical Example", font_size=36).to_edge(UP, buff=1.5)
        self.play(FadeIn(example_title))

        # Define the problem
        problem = MathTex("a = 3", ", \\quad ", "b = 4", ", \\quad ", "c = ?", font_size=42)
        problem.next_to(example_title, DOWN, buff=0.8)
        problem[0].set_color(YELLOW)
        problem[2].set_color(ORANGE)
        problem[4].set_color(RED)

        self.play(Write(problem))
        self.wait(1)

        # Show the calculation steps
        calc_step1 = MathTex("a^2 + b^2 = c^2", font_size=42)
        calc_step2 = MathTex("3^2 + 4^2 = c^2", font_size=42)
        calc_step3 = MathTex("9 + 16 = c^2", font_size=42)
        calc_step4 = MathTex("25 = c^2", font_size=42)
        calc_step5 = MathTex("c = \\sqrt{25} = 5", font_size=42)

        # Color code the final answer
        calc_step5[0].set_color(RED)
        calc_step5[2].set_color(RED)

        calculations = VGroup(calc_step1, calc_step2, calc_step3, calc_step4, calc_step5)
        calculations.arrange(DOWN, buff=0.5).next_to(problem, DOWN, buff=0.8)

        for step in calculations:
            self.play(Write(step))
            self.wait(0.5)
        
        self.wait(2)

        # 5. Summary and Conclusion
        self.play(
            FadeOut(title),
            FadeOut(example_title),
            FadeOut(problem),
            FadeOut(calculations)
        )

        summary_text = Text(
            "The theorem is a cornerstone of geometry,\n"
            "used in construction, navigation, and more.",
            font_size=32,
            text_align="CENTER"
        )
        summary_text.move_to(ORIGIN)

        final_formula = MathTex("a^2 + b^2 = c^2", font_size=60).next_to(summary_text, DOWN, buff=1.0)
        final_formula[0].set_color(YELLOW)
        final_formula[2].set_color(ORANGE)
        final_formula[4].set_color(RED)

        self.play(Write(summary_text))
        self.play(FadeIn(final_formula))

        self.wait(3)
        self.play(FadeOut(summary_text), FadeOut(final_formula))
        self.wait(2)