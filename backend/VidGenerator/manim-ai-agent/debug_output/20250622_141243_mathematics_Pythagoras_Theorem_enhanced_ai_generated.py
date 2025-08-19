from manim import *

class PythagorasTheorem(Scene):
    """
    An animation explaining the Pythagoras Theorem for beginners.
    This scene visually demonstrates the theorem with a right-angled triangle,
    shows the relationship using squares on each side, and provides a
    step-by-step calculation example.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("Pythagoras Theorem", font_size=48)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # 2. Introduce the Right-Angled Triangle
        # Define vertices for a 3-4-5 triangle for easy visualization
        vert_A = [0, 1.5, 0]  # Top vertex
        vert_B = [-2, -1.5, 0] # Bottom-left vertex (right angle)
        vert_C = [2, -1.5, 0]   # Bottom-right vertex

        # Create the triangle from vertices
        triangle = Polygon(vert_B, vert_C, vert_A, color=BLUE)
        
        # Add a square to indicate the 90-degree angle
        right_angle_mark = Square(side_length=0.4, color=WHITE).move_to(vert_B, aligned_edge=UL)

        # Label the sides a, b, and c (hypotenuse)
        side_a_label = MathTex("a", color=ORANGE).next_to(Line(vert_B, vert_A), LEFT, buff=0.3)
        side_b_label = MathTex("b", color=GREEN).next_to(Line(vert_B, vert_C), DOWN, buff=0.3)
        side_c_label = MathTex("c", color=RED).next_to(Line(vert_A, vert_C), UR, buff=0.2)
        
        triangle_group = VGroup(triangle, right_angle_mark, side_a_label, side_b_label, side_c_label)
        triangle_group.move_to(ORIGIN).shift(LEFT * 3)

        self.play(Create(triangle))
        self.play(Create(right_angle_mark))
        self.play(Write(side_a_label), Write(side_b_label), Write(side_c_label))
        self.wait(1)

        # 3. State the Theorem Formula
        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=60)
        formula.set_color_by_tex("a^2", ORANGE)
        formula.set_color_by_tex("b^2", GREEN)
        formula.set_color_by_tex("c^2", RED)
        formula.next_to(triangle_group, RIGHT, buff=1.0)

        explanation = VGroup(
            Text("For any right-angled triangle:", font_size=24),
            formula
        ).arrange(DOWN, buff=0.5).next_to(triangle_group, RIGHT, buff=1.0)

        self.play(Write(explanation))
        self.wait(2)

        # 4. Visual Demonstration with Squares
        # Create squares on each side of the triangle
        square_a = Square(side_length=3, color=ORANGE, fill_opacity=0.7).next_to(Line(vert_B, vert_A), LEFT, buff=0)
        square_b = Square(side_length=4, color=GREEN, fill_opacity=0.7).next_to(Line(vert_B, vert_C), DOWN, buff=0)
        
        # The hypotenuse has length 5 (sqrt(3^2 + 4^2))
        hypotenuse_line = Line(vert_A, vert_C)
        square_c = Square(side_length=5, color=RED, fill_opacity=0.7)
        square_c.move_to(hypotenuse_line.get_center())
        square_c.rotate(hypotenuse_line.get_angle())

        # Animate the squares and their area labels
        area_a_text = MathTex("a^2 = 3^2 = 9").set_color(ORANGE).scale(0.8)
        area_b_text = MathTex("b^2 = 4^2 = 16").set_color(GREEN).scale(0.8)
        area_c_text = MathTex("c^2 = 5^2 = 25").set_color(RED).scale(0.8)

        # Position the area labels inside the squares
        area_a_text.move_to(square_a.get_center())
        area_b_text.move_to(square_b.get_center())
        area_c_text.move_to(square_c.get_center())

        # Clear formula to make space
        self.play(FadeOut(explanation))
        
        # Animate creation of squares and areas
        self.play(Create(square_a), Create(square_b))
        self.play(Write(area_a_text), Write(area_b_text))
        self.wait(1)
        self.play(Create(square_c))
        self.play(Write(area_c_text))
        self.wait(2)

        # Show the final calculation connecting the areas
        proof_text = MathTex("a^2 + b^2", "=", "9 + 16", "=", "25", "=", "c^2", font_size=48)
        proof_text.to_edge(DOWN, buff=1.0)
        proof_text.set_color_by_tex("a^2 + b^2", YELLOW)
        proof_text.set_color_by_tex("c^2", RED)
        
        self.play(Write(proof_text))
        self.wait(3)

        # Fade out everything to prepare for the example
        visual_proof_group = VGroup(triangle_group, square_a, square_b, square_c, area_a_text, area_b_text, area_c_text, proof_text)
        self.play(FadeOut(visual_proof_group))
        self.wait(1)

        # 5. Example Calculation
        example_title = Text("Example: Find the Hypotenuse", font_size=36).to_edge(UP)
        self.play(Transform(title, example_title))

        # New triangle for the example
        ex_triangle = Polygon([-2, -1, 0], [-2, -1+3, 0], [2, -1, 0], color=BLUE)
        ex_right_angle = Square(side_length=0.4, color=WHITE).move_to([-2, -1, 0], aligned_edge=DL)
        ex_side_a = MathTex("a = 3").next_to(ex_triangle.get_left(), LEFT)
        ex_side_b = MathTex("b = 4").next_to(ex_triangle.get_bottom(), DOWN)
        ex_side_c = MathTex("c = ?").next_to(ex_triangle.get_right(), UR, buff=-1.5)
        
        example_visual = VGroup(ex_triangle, ex_right_angle, ex_side_a, ex_side_b, ex_side_c)
        example_visual.move_to(ORIGIN).shift(LEFT * 3)

        self.play(Create(example_visual))
        self.wait(1)

        # Step-by-step calculation
        calc_steps = VGroup(
            MathTex("a^2 + b^2 = c^2"),
            MathTex("3^2 + 4^2 = c^2"),
            MathTex("9 + 16 = c^2"),
            MathTex("25 = c^2"),
            MathTex("\\sqrt{25} = c"),
            MathTex("5 = c")
        ).arrange(DOWN, buff=0.5).next_to(example_visual, RIGHT, buff=1.2)

        self.play(Write(calc_steps[0]))
        self.wait(1)
        for i in range(len(calc_steps) - 1):
            self.play(Transform(calc_steps[i], calc_steps[i+1]))
            self.wait(1.5)
        
        # Highlight the final answer
        final_answer_box = SurroundingRectangle(calc_steps[-1], color=YELLOW)
        self.play(Create(final_answer_box))
        self.wait(2)

        # 6. Summary
        summary_group = VGroup(example_visual, calc_steps[-1], final_answer_box, title)
        self.play(FadeOut(summary_group))
        
        summary_text = Text(
            "The square of the hypotenuse (c) equals\nthe sum of the squares of the other two sides (a and b).",
            font_size=28,
            text_align=CENTER
        )
        final_formula = MathTex("a^2 + b^2 = c^2", font_size=72)
        final_formula.set_color_by_tex("a", ORANGE)
        final_formula.set_color_by_tex("b", GREEN)
        final_formula.set_color_by_tex("c", RED)

        conclusion = VGroup(summary_text, final_formula).arrange(DOWN, buff=0.8).move_to(ORIGIN)
        
        self.play(Write(conclusion))
        self.wait(3)
        
        self.play(FadeOut(conclusion))
        self.wait(2)