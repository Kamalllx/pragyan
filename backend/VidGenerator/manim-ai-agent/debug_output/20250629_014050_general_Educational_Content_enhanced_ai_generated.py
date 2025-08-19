from manim import *

class EducationalContentScene(Scene):
    """
    An animation explaining the core principles of creating
    good educational content, designed for beginners.
    """
    def construct(self):
        # Set a consistent background color
        self.camera.background_color = "#1E2127"

        # 1. Title Introduction
        title = Text("What is Educational Content?", font_size=48)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.wait(1)

        # 2. Core Definition
        definition = Text(
            "It's information designed to help people learn.",
            font_size=32
        ).next_to(title, DOWN, buff=0.8)

        self.play(FadeIn(definition, shift=DOWN))
        self.wait(2)

        # Visual metaphor for learning
        idea_bulb = VGroup(
            Circle(radius=0.5, color=YELLOW, fill_opacity=1),
            Rectangle(width=0.4, height=0.2, color=WHITE).next_to(Circle(radius=0.5), DOWN, buff=0)
        ).shift(LEFT * 3)
        
        learner_head = Circle(radius=0.8, color=BLUE_C).shift(RIGHT * 3)
        
        explanation_text = Text("Transferring an idea...", font_size=24).next_to(idea_bulb, DOWN)
        learner_text = Text("...to a learner.", font_size=24).next_to(learner_head, DOWN)

        self.play(
            FadeOut(definition),
            Create(idea_bulb),
            Write(explanation_text)
        )
        self.wait(1)
        
        arrow = Arrow(idea_bulb.get_right(), learner_head.get_left(), buff=0.2, color=WHITE)
        self.play(GrowArrow(arrow))
        self.play(Create(learner_head), Write(learner_text))
        self.wait(2)

        # Clear the screen for the next section
        self.play(
            FadeOut(title),
            FadeOut(idea_bulb),
            FadeOut(learner_head),
            FadeOut(arrow),
            FadeOut(explanation_text),
            FadeOut(learner_text)
        )
        self.wait(1)

        # 3. Key Components of Good Educational Content
        components_title = Text("Key Components", font_size=40).to_edge(UP)
        self.play(Write(components_title))
        self.wait(1)

        # Component 1: Clarity
        clarity_icon = Circle(radius=0.5, color=BLUE).move_to(UP * 0.5)
        clarity_handle = Line(clarity_icon.get_corner(DR), clarity_icon.get_corner(DR) + DL * 0.5, color=BLUE)
        magnifying_glass = VGroup(clarity_icon, clarity_handle)
        clarity_label = Text("Clarity", font_size=28).next_to(magnifying_glass, DOWN, buff=0.3)
        clarity_desc = Text("Simple and focused", font_size=24).next_to(clarity_label, DOWN, buff=0.2)
        clarity_group = VGroup(magnifying_glass, clarity_label, clarity_desc)

        # Component 2: Engagement
        engagement_icon = Star(5, outer_radius=0.6, color=YELLOW, fill_opacity=1).move_to(UP * 0.5)
        engagement_label = Text("Engagement", font_size=28).next_to(engagement_icon, DOWN, buff=0.3)
        engagement_desc = Text("Interesting and fun", font_size=24).next_to(engagement_label, DOWN, buff=0.2)
        engagement_group = VGroup(engagement_icon, engagement_label, engagement_desc)

        # Component 3: Structure
        block1 = Rectangle(width=1.2, height=0.4, color=GREEN).move_to(UP * 0.3)
        block2 = Rectangle(width=1.2, height=0.4, color=GREEN).next_to(block1, DOWN, buff=0)
        structure_icon = VGroup(block1, block2)
        structure_label = Text("Structure", font_size=28).next_to(structure_icon, DOWN, buff=0.3)
        structure_desc = Text("Logical and organized", font_size=24).next_to(structure_label, DOWN, buff=0.2)
        structure_group = VGroup(structure_icon, structure_label, structure_desc)

        # Arrange all components
        all_components = VGroup(clarity_group, engagement_group, structure_group).arrange(RIGHT, buff=1.2)
        all_components.next_to(components_title, DOWN, buff=1.0)

        self.play(FadeIn(clarity_group, shift=UP))
        self.wait(1)
        self.play(FadeIn(engagement_group, shift=UP))
        self.wait(1)
        self.play(FadeIn(structure_group, shift=UP))
        self.wait(2)

        # 4. Example: Explaining a Triangle
        self.play(
            FadeOut(components_title),
            FadeOut(all_components)
        )
        self.wait(1)

        example_title = Text("Let's See an Example!", font_size=40).to_edge(UP)
        self.play(Write(example_title))
        
        # Create the triangle and its properties
        triangle = Polygon([-2, -1, 0], [2, -1, 0], [0, 2, 0], color=ORANGE)
        triangle_label = Text("This is a Triangle", font_size=32).next_to(triangle, DOWN, buff=0.5)

        self.play(Create(triangle))
        self.play(Write(triangle_label))
        self.wait(1)

        # Show properties with clarity and structure
        sides_label = Text("It has 3 sides", font_size=28).to_edge(LEFT).shift(UP * 0.5)
        angles_label = Text("It has 3 angles", font_size=28).to_edge(RIGHT).shift(UP * 0.5)

        # Indicate sides
        self.play(Write(sides_label))
        self.play(Indicate(triangle.get_edge(0), color=YELLOW))
        self.play(Indicate(triangle.get_edge(1), color=YELLOW))
        self.play(Indicate(triangle.get_edge(2), color=YELLOW))
        self.wait(1)

        # Indicate angles (vertices)
        self.play(Write(angles_label))
        self.play(Indicate(Dot(triangle.get_vertices()[0]), color=CYAN))
        self.play(Indicate(Dot(triangle.get_vertices()[1]), color=CYAN))
        self.play(Indicate(Dot(triangle.get_vertices()[2]), color=CYAN))
        self.wait(2)

        # 5. Summary
        self.play(
            FadeOut(example_title),
            FadeOut(triangle),
            FadeOut(triangle_label),
            FadeOut(sides_label),
            FadeOut(angles_label)
        )
        self.wait(1)

        summary_title = Text("Summary", font_size=48).to_edge(UP)
        
        summary_text = Text(
            "Good educational content makes learning...",
            font_size=32
        ).next_to(summary_title, DOWN, buff=1.0)

        final_points = VGroup(
            Text("✅ Clear", font_size=36, color=BLUE),
            Text("✅ Engaging", font_size=36, color=YELLOW),
            Text("✅ Structured", font_size=36, color=GREEN)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(summary_text, DOWN, buff=0.8)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_text))
        self.wait(1)
        self.play(Write(final_points[0]))
        self.wait(0.5)
        self.play(Write(final_points[1]))
        self.wait(0.5)
        self.play(Write(final_points[2]))
        
        self.wait(2)