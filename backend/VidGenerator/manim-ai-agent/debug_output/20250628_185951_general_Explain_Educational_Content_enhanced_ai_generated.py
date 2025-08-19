from manim import *

class PythagoreanTheoremScene(Scene):
    """
    An intermediate-level Manim scene explaining the Pythagorean Theorem.
    This scene follows best practices for educational content, including clear
    visuals, mathematical examples, and proper layout management.
    """
    def construct(self):
        # -----------------------------------------------------------------
        # 1. Title Introduction
        # -----------------------------------------------------------------
        # Position the title at the top edge of the frame.
        title = Text("The Pythagorean Theorem", font_size=48)
        title.to_edge(UP)

        self.play(Write(title))
        self.wait(1)

        # -----------------------------------------------------------------
        # 2. Main Educational Content: The Right-Angled Triangle
        # -----------------------------------------------------------------
        # Define the vertices for a right-angled triangle.
        # Using a 3-4-5 ratio for simplicity.
        triangle_vertices = [
            ORIGIN,          # Vertex at (0,0)
            RIGHT * 4,       # Vertex at (4,0)
            UP * 3           # Vertex at (0,3)
        ]
        triangle = Polygon(*triangle_vertices, color=BLUE, fill_opacity=0.2)
        triangle.move_to(LEFT * 2.5)

        # Create labels for the sides 'a', 'b', and 'c' (hypotenuse).
        label_a = MathTex("a", "=", "3").next_to(triangle.get_sides()[2], LEFT, buff=0.3)
        label_b = MathTex("b", "=", "4").next_to(triangle.get_sides()[0], DOWN, buff=0.3)
        label_c = MathTex("c", "?").next_to(triangle.get_sides()[1], UP + RIGHT, buff=0.1)

        # Group the triangle and its labels for easier management.
        triangle_group = VGroup(triangle, label_a, label_b, label_c)

        self.play(Create(triangle))
        self.play(Write(label_a), Write(label_b), Write(label_c))
        self.wait(1)

        # -----------------------------------------------------------------
        # 3. Key Concepts: The Formula
        # -----------------------------------------------------------------
        # Display the core formula of the theorem.
        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=60)
        formula.next_to(triangle_group, RIGHT, buff=1.0)

        self.play(Write(formula))
        self.wait(2)

        # Indicate the connection between the labels and the formula.
        self.play(Indicate(label_a), Indicate(formula[0]))
        self.play(Indicate(label_b), Indicate(formula[2]))
        self.play(Indicate(label_c), Indicate(formula[4]))
        self.wait(1)

        # -----------------------------------------------------------------
        # 4. Visual Demonstration: The Squares of the Sides
        # -----------------------------------------------------------------
        # Create squares on each side to visually represent a², b², and c².
        square_a = Square(side_length=3, color=GREEN, fill_opacity=0.5)
        square_a.next_to(triangle.get_sides()[2], LEFT, buff=0)

        square_b = Square(side_length=4, color=YELLOW, fill_opacity=0.5)
        square_b.next_to(triangle.get_sides()[0], DOWN, buff=0)

        # The hypotenuse square needs to be rotated and positioned correctly.
        hypotenuse_line = Line(triangle_vertices[1], triangle_vertices[2])
        square_c = Square(side_length=5, color=RED, fill_opacity=0.5)
        square_c.move_to(hypotenuse_line.get_center())
        square_c.rotate(hypotenuse_line.get_angle())

        # Add area labels inside the squares.
        area_a_label = MathTex("a^2", "=", "9").move_to(square_a.get_center())
        area_b_label = MathTex("b^2", "=", "16").move_to(square_b.get_center())
        area_c_label = MathTex("c^2", "=", "25").move_to(square_c.get_center())

        # Animate the creation of the squares and their area labels.
        self.play(
            FadeOut(label_a, label_b, label_c),
            FadeOut(formula),
            triangle_group.animate.shift(RIGHT * 2.5).scale(0.8)
        )
        self.wait(0.5)

        self.play(Create(square_a), Write(area_a_label))
        self.play(Create(square_b), Write(area_b_label))
        self.wait(1)
        self.play(Create(square_c), Write(area_c_label))
        self.wait(2)

        # Show the addition of the areas.
        sum_text = MathTex("9", "+", "16", "=", "25", font_size=48)
        sum_text.to_edge(DOWN, buff=1.0)
        
        # Create copies to transform into the sum equation.
        a_copy = area_a_label.copy()
        b_copy = area_b_label.copy()
        c_copy = area_c_label.copy()

        self.play(
            Transform(a_copy[2], sum_text[0]),
            Transform(b_copy[2], sum_text[2]),
            Transform(c_copy[2], sum_text[4]),
            Write(sum_text[1]),
            Write(sum_text[3])
        )
        self.wait(2)

        # Clean up the screen for the final summary.
        visual_proof_group = VGroup(
            triangle_group, square_a, square_b, square_c,
            area_a_label, area_b_label, area_c_label,
            sum_text, a_copy, b_copy, c_copy
        )
        self.play(FadeOut(visual_proof_group))
        self.wait(1)

        # -----------------------------------------------------------------
        # 5. Summary and Conclusion
        # -----------------------------------------------------------------
        # Provide a concise summary of the theorem's importance.
        summary_text_1 = Text(
            "For any right-angled triangle,",
            font_size=32
        )
        summary_text_2 = Text(
            "the square of the hypotenuse is equal to the sum",
            font_size=32
        )
        summary_text_3 = Text(
            "of the squares of the other two sides.",
            font_size=32
        )
        summary_formula = MathTex("a^2 + b^2 = c^2", font_size=48, color=YELLOW)

        # Group the summary text and arrange it vertically.
        summary_group = VGroup(
            summary_text_1, summary_text_2, summary_text_3, summary_formula
        )
        summary_group.arrange(DOWN, buff=0.5)
        summary_group.move_to(ORIGIN)

        self.play(Write(summary_group))
        self.wait(3)

        # Final fade out.
        self.play(FadeOut(summary_group), FadeOut(title))
        self.wait(2)