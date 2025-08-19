from manim import *

class PythagoreanTheoremExample(Scene):
    """
    An animation explaining how to find the hypotenuse of a right-angled
    triangle using the Pythagorean theorem, with a specific example.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("Finding the Hypotenuse", font_size=36)
        title.to_edge(UP, buff=0.8)
        self.play(Write(title))
        self.wait(1)

        # 2. Visualize the Triangle
        # Define vertices to position the triangle on the right side of the screen
        vertex_A = RIGHT * 1 + DOWN * 1.5
        vertex_B = vertex_A + RIGHT * 4
        vertex_C = vertex_A + UP * 3

        # Create the sides of the triangle
        base = Line(vertex_A, vertex_B, color=BLUE)
        altitude = Line(vertex_A, vertex_C, color=RED)
        hypotenuse = Line(vertex_B, vertex_C, color=GREEN)

        # Create labels for vertices
        label_A = MathTex("A").next_to(vertex_A, DOWN + LEFT, buff=0.1)
        label_B = MathTex("B").next_to(vertex_B, DOWN + RIGHT, buff=0.1)
        label_C = MathTex("C").next_to(vertex_C, UP + LEFT, buff=0.1)
        
        # Create labels for side lengths
        base_label = MathTex("Base (AB) = 4 \\text{ cm}", font_size=24).next_to(base, DOWN, buff=0.3)
        altitude_label = MathTex("Altitude (AC) = 3 \\text{ cm}", font_size=24).next_to(altitude, LEFT, buff=0.3)
        hypotenuse_label = MathTex("?", color=YELLOW, font_size=36).next_to(hypotenuse.get_center(), UP + RIGHT, buff=0.2)

        # Create the right-angle symbol
        right_angle = Square(side_length=0.4, color=WHITE, stroke_width=3).move_to(vertex_A + RIGHT * 0.2 + UP * 0.2)

        # Animate the creation of the triangle and its labels
        self.play(Create(VGroup(base, altitude)), Write(VGroup(label_A, label_B, label_C)), run_time=1.5)
        self.play(Create(right_angle))
        self.play(Write(base_label), Write(altitude_label))
        self.play(Create(hypotenuse))
        self.play(FadeIn(hypotenuse_label, shift=UP))
        self.wait(1)

        # 3. Explain the Pythagorean Theorem
        explanation_group = VGroup(
            Text("We use the Pythagorean Theorem:", font_size=28),
            MathTex("a^2 + b^2 = c^2", font_size=32),
            Text("For our triangle, this is:", font_size=28),
            MathTex("AC^2 + AB^2 = BC^2", font_size=32)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).to_edge(LEFT, buff=1.0)

        self.play(Write(explanation_group[0]))
        self.play(Write(explanation_group[1]))
        self.wait(0.5)
        # Indicate which sides correspond to the formula
        self.play(Indicate(altitude), Indicate(base), Indicate(hypotenuse))
        self.play(Write(explanation_group[2]))
        self.play(Write(explanation_group[3]))
        self.wait(1)

        # 4. Show Step-by-Step Calculations
        # Position the first calculation step relative to the explanation
        calc_step = MathTex("3^2 + 4^2 = BC^2").next_to(explanation_group, DOWN, buff=0.8, aligned_edge=LEFT)
        self.play(FadeIn(calc_step, shift=UP))
        self.wait(1)

        # Transform through the calculation steps
        self.play(Transform(calc_step, MathTex("9 + 16 = BC^2").move_to(calc_step, aligned_edge=LEFT)))
        self.wait(1)

        self.play(Transform(calc_step, MathTex("25 = BC^2").move_to(calc_step, aligned_edge=LEFT)))
        self.wait(1)

        self.play(Transform(calc_step, MathTex("BC = \\sqrt{25}").move_to(calc_step, aligned_edge=LEFT)))
        self.wait(1)

        self.play(Transform(calc_step, MathTex("BC = 5").move_to(calc_step, aligned_edge=LEFT)))
        self.wait(1)

        # 5. Display the Final Answer and Summarize
        final_answer_text = MathTex("BC = 5 \\text{ cm}", color=YELLOW)
        final_answer_text.move_to(calc_step, aligned_edge=LEFT)
        result_box = SurroundingRectangle(final_answer_text, buff=0.2, color=GREEN)
        
        self.play(Transform(calc_step, final_answer_text))
        self.play(Create(result_box))
        self.wait(0.5)

        # Update the question mark on the triangle with the final answer
        final_hyp_label = MathTex("5 \\text{ cm}", color=GREEN, font_size=36).move_to(hypotenuse_label.get_center())
        self.play(Transform(hypotenuse_label, final_hyp_label))
        self.wait(1)

        # Display a concluding summary message
        summary = Text("The length of the hypotenuse (BC) is 5 cm.", font_size=28)
        summary.to_edge(DOWN, buff=1.0)
        self.play(Write(summary))

        # Hold the final scene for the viewer
        self.wait(2)