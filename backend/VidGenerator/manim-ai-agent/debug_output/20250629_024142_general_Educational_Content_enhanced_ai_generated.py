from manim import *

class EducationalContentScene(Scene):
    """
    An animation explaining the key principles of good educational content,
    designed for beginners and following best practices for clarity and layout.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("What Makes Good Educational Content?", font_size=36)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.wait(1)

        # --- Principle 1: Clarity ---
        clarity_title = Text("1. Clarity is Key", font_size=28).next_to(title, DOWN, buff=1.0)
        self.play(FadeIn(clarity_title, shift=DOWN))
        self.wait(1)

        # Create a messy, overlapping group of objects
        messy_circle = Circle(radius=0.8, color=BLUE).shift(LEFT * 0.2)
        messy_square = Square(side_length=1.5, color=RED).shift(RIGHT * 0.2)
        messy_text = Text("Data", font_size=24).shift(UP * 0.1)
        messy_group = VGroup(messy_circle, messy_square, messy_text).move_to(ORIGIN).shift(DOWN*1.5)

        # Create a clear, organized version of the same objects
        clear_circle = Circle(radius=0.6, color=BLUE)
        clear_square = Square(side_length=1.2, color=RED)
        clear_text = Text("Data", font_size=24)
        clear_group = VGroup(clear_circle, clear_square, clear_text).arrange(RIGHT, buff=1.2)
        clear_group.move_to(messy_group.get_center())

        self.play(Create(messy_group))
        self.wait(1)
        self.play(Transform(messy_group, clear_group))
        self.wait(2)

        # Fade out the first principle to make space for the next
        self.play(FadeOut(clarity_title), FadeOut(messy_group))
        self.wait(1)

        # --- Principle 2: Simplicity ---
        simplicity_title = Text("2. Start with Simple Ideas", font_size=28).next_to(title, DOWN, buff=1.0)
        self.play(FadeIn(simplicity_title, shift=DOWN))
        self.wait(1)

        # Demonstrate breaking down a concept (Pythagorean Theorem)
        triangle = Polygon([-2, -1, 0], [2, -1, 0], [-2, 1, 0], color=WHITE)
        side_a = Text("a", font_size=24).next_to(triangle.get_vertices()[0] - [0, 1, 0], LEFT, buff=0.2)
        side_b = Text("b", font_size=24).next_to(triangle.get_vertices()[1] - [1, 0, 0], DOWN, buff=0.2)
        side_c = Text("c", font_size=24).next_to(triangle.get_center() + [0, 0.2, 0], UP, buff=0.2)
        
        triangle_group = VGroup(triangle, side_a, side_b, side_c).move_to(LEFT * 3)
        
        formula = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=48).next_to(triangle_group, RIGHT, buff=1.5)

        self.play(Create(triangle_group))
        self.wait(1)
        self.play(Write(formula))
        self.wait(1)

        # Highlight the connection between formula and visual
        self.play(Indicate(VGroup(side_a, formula[0])))
        self.wait(0.5)
        self.play(Indicate(VGroup(side_b, formula[2])))
        self.wait(0.5)
        self.play(Indicate(VGroup(side_c, formula[4])))
        self.wait(2)

        self.play(FadeOut(simplicity_title), FadeOut(triangle_group), FadeOut(formula))
        self.wait(1)

        # --- Principle 3: Visuals Enhance Understanding ---
        visuals_title = Text("3. Use Supporting Visuals", font_size=28).next_to(title, DOWN, buff=1.0)
        self.play(FadeIn(visuals_title, shift=DOWN))
        self.wait(1)

        # Show text first, then the visual
        explanation_text = Text(
            "The radius is the distance\nfrom the center of a circle\nto any point on its edge.",
            font_size=24,
            line_spacing=1.2
        ).move_to(LEFT * 3)

        # Create the visual aid
        circle_visual = Circle(radius=1.2, color=YELLOW)
        center_dot = Dot(circle_visual.get_center())
        radius_line = Line(circle_visual.get_center(), circle_visual.get_right(), color=YELLOW)
        radius_label = MathTex("r").next_to(radius_line, DOWN, buff=0.2)
        visual_group = VGroup(circle_visual, center_dot, radius_line, radius_label).next_to(explanation_text, RIGHT, buff=1.5)

        self.play(Write(explanation_text))
        self.wait(1)
        self.play(Create(visual_group))
        self.wait(2)

        self.play(FadeOut(visuals_title), FadeOut(explanation_text), FadeOut(visual_group))
        self.wait(1)

        # --- Principle 4: Structure ---
        structure_title = Text("4. Provide a Clear Structure", font_size=28).next_to(title, DOWN, buff=1.0)
        self.play(FadeIn(structure_title, shift=DOWN))
        self.wait(1)

        # Create a structured list
        point1 = Text("1. Introduce the topic", font_size=24)
        point2 = Text("2. Explain the core concepts", font_size=24)
        point3 = Text("3. Provide a summary", font_size=24)
        
        structured_list = VGroup(point1, point2, point3).arrange(
            DOWN, buff=0.8, aligned_edge=LEFT
        ).move_to(ORIGIN).shift(DOWN*0.5)

        self.play(Write(point1))
        self.wait(1)
        self.play(Write(point2))
        self.wait(1)
        self.play(Write(point3))
        self.wait(2)

        # --- Summary ---
        self.play(
            FadeOut(title),
            FadeOut(structure_title),
            FadeOut(structured_list)
        )
        self.wait(1)

        summary_title = Text("In Summary: Create Effective Learning", font_size=36).to_edge(UP)
        
        # Key takeaways
        key_clarity = Text("Clarity", font_size=28)
        key_simplicity = Text("Simplicity", font_size=28)
        key_visuals = Text("Visuals", font_size=28)
        key_structure = Text("Structure", font_size=28)

        summary_group = VGroup(key_clarity, key_simplicity, key_visuals, key_structure).arrange(DOWN, buff=1.0).move_to(ORIGIN)

        self.play(Write(summary_title))
        self.wait(1)
        self.play(FadeIn(summary_group, lag_ratio=0.5))
        self.wait(2)

        # Final fade out
        self.play(FadeOut(summary_title), FadeOut(summary_group))
        self.wait(2)