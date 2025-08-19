from manim import *

class EducationalContentExplained(Scene):
    """
    An animation explaining the core principles of creating
    effective educational content, designed for beginners.
    """
    def construct(self):
        # Set a consistent theme
        self.camera.background_color = "#F0F0F0"
        main_color = "#003366"  # A deep blue for text
        accent_color = "#FF6347" # A tomato red for highlights

        # 1. Title Introduction
        title = Text(
            "What Makes Great Educational Content?",
            font_size=36,
            color=main_color
        ).to_edge(UP)
        
        self.play(Write(title))
        self.wait(1)

        # 2. Introduce the three core principles
        clarity_text = Text("Clarity", font_size=28, color=BLACK)
        structure_text = Text("Structure", font_size=28, color=BLACK)
        engagement_text = Text("Engagement", font_size=28, color=BLACK)

        principles = VGroup(clarity_text, structure_text, engagement_text).arrange(RIGHT, buff=1.5)
        principles.shift(UP * 1.5)

        self.play(FadeIn(principles, shift=DOWN))
        self.wait(1)

        # 3. Explain each principle one by one

        # --- Clarity ---
        self.play(Indicate(clarity_text, color=accent_color))
        
        # Visual for clarity: a simple, clear diagram
        clear_circle = Circle(radius=0.5, color=BLUE, fill_opacity=0.5)
        clear_label = Text("A Circle", font_size=24, color=main_color).next_to(clear_circle, DOWN, buff=0.3)
        clear_group = VGroup(clear_circle, clear_label).shift(LEFT * 3 + DOWN * 1)

        # Explanation text for clarity
        clarity_explanation = Text(
            "Content should be simple\nand easy to understand.",
            font_size=24,
            color=main_color,
            text_align="center"
        ).next_to(clear_group, RIGHT, buff=1.0)

        self.play(Create(clear_group))
        self.play(Write(clarity_explanation))
        self.wait(2)

        # Fade out clarity elements to make space for the next point
        self.play(FadeOut(clear_group), FadeOut(clarity_explanation))
        self.wait(0.5)

        # --- Structure ---
        self.play(Indicate(structure_text, color=accent_color))

        # Visual for structure: a logical flow
        step1 = Text("1. Start", font_size=24, color=main_color)
        step2 = Text("2. Middle", font_size=24, color=main_color)
        step3 = Text("3. End", font_size=24, color=main_color)
        
        structure_visual = VGroup(step1, step2, step3).arrange(DOWN, buff=0.8).shift(LEFT * 3 + DOWN * 1)
        
        arrow1 = Arrow(step1.get_bottom(), step2.get_top(), buff=0.2, color=accent_color)
        arrow2 = Arrow(step2.get_bottom(), step3.get_top(), buff=0.2, color=accent_color)
        arrows = VGroup(arrow1, arrow2)

        # Explanation text for structure
        structure_explanation = Text(
            "Information is presented\nin a logical order.",
            font_size=24,
            color=main_color,
            text_align="center"
        ).next_to(structure_visual, RIGHT, buff=1.0)

        self.play(Write(structure_visual))
        self.play(Create(arrows))
        self.play(Write(structure_explanation))
        self.wait(2)

        # Fade out structure elements
        self.play(FadeOut(structure_visual), FadeOut(arrows), FadeOut(structure_explanation))
        self.wait(0.5)

        # --- Engagement ---
        self.play(Indicate(engagement_text, color=accent_color))

        # Visual for engagement: a lightbulb turning on
        bulb_base = Rectangle(width=0.5, height=0.3, color=GRAY).shift(DOWN * 0.6)
        bulb_glass = Circle(radius=0.5, color=YELLOW_D).above(bulb_base, buff=-0.1)
        lightbulb = VGroup(bulb_glass, bulb_base).shift(LEFT * 3 + DOWN * 0.5)
        
        rays = VGroup(
            Line(UP, UP * 1.5),
            Line(RIGHT, RIGHT * 1.5),
            Line(LEFT, LEFT * 1.5),
            Line(UP + RIGHT, (UP + RIGHT) * 1.5),
            Line(UP + LEFT, (UP + LEFT) * 1.5)
        ).move_to(lightbulb.get_center())
        rays.set_color(YELLOW)

        # Explanation text for engagement
        engagement_explanation = Text(
            "Keeps the learner interested\nand focused.",
            font_size=24,
            color=main_color,
            text_align="center"
        ).next_to(lightbulb, RIGHT, buff=1.0)

        self.play(FadeIn(lightbulb))
        self.play(Create(rays))
        self.play(Write(engagement_explanation))
        self.wait(2)

        # Fade out engagement elements and the principles list
        self.play(FadeOut(lightbulb), FadeOut(rays), FadeOut(engagement_explanation), FadeOut(principles))
        self.wait(1)

        # 4. Summary
        summary_title = Text("In Short:", font_size=32, color=main_color)
        
        summary_point1 = Text("• Be Clear", font_size=28, color=BLACK)
        summary_point2 = Text("• Be Structured", font_size=28, color=BLACK)
        summary_point3 = Text("• Be Engaging", font_size=28, color=BLACK)

        summary_group = VGroup(
            summary_title,
            summary_point1,
            summary_point2,
            summary_point3
        ).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        
        summary_group.move_to(ORIGIN)

        # Position the title above the points
        summary_title.next_to(VGroup(summary_point1, summary_point2, summary_point3), UP, buff=0.8)

        self.play(FadeOut(title)) # Remove original title
        self.play(Write(summary_group))
        
        # Final wait
        self.wait(2)