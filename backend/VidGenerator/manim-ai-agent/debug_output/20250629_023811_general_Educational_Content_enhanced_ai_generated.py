from manim import *

class EducationalContentExplanation(Scene):
    """
    An animation explaining the concept of 'Educational Content' for beginners.
    This scene breaks down the term, provides visual examples, and summarizes the goal.
    """
    def construct(self):
        # Set a consistent theme
        self.camera.background_color = "#1E2127"

        # 1. Title Introduction
        title = Text("What is Educational Content?", font_size=36)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.wait(1)

        # 2. Main Concept: Break down the phrase
        main_phrase = Text("Educational Content", font_size=48).move_to(ORIGIN)
        
        self.play(
            FadeOut(title, shift=DOWN),
            FadeIn(main_phrase, shift=UP)
        )
        self.wait(1)

        # Create a box around the main phrase to highlight it
        box = SurroundingRectangle(main_phrase, buff=0.3, color=BLUE)
        self.play(Create(box))
        self.wait(1)

        # 3. Explain "Content"
        content_title = Text("First, what is 'Content'?", font_size=32)
        content_title.to_edge(UP)

        # Visuals for different types of content
        book_icon = VGroup(
            Rectangle(width=1.5, height=2, color=WHITE, fill_opacity=1, fill_color=DARK_GRAY),
            Line(start=[-0.6, 1, 0], end=[-0.6, -1, 0], color=WHITE),
            Text("Book", font_size=24)
        ).arrange(DOWN, buff=0.3)

        video_icon = VGroup(
            Rectangle(width=2, height=1.5, color=WHITE),
            Polygon(
                [-0.2, 0.3, 0], [-0.2, -0.3, 0], [0.3, 0, 0],
                color=RED, fill_opacity=1
            ),
            Text("Video", font_size=24)
        ).arrange(DOWN, buff=0.3)

        image_icon = VGroup(
            Rectangle(width=2, height=1.5, color=WHITE),
            VGroup(
                Triangle(color=YELLOW).scale(0.2).shift(UP*0.3 + LEFT*0.5),
                Circle(radius=0.2, color=BLUE).shift(UP*0.2 + RIGHT*0.3)
            ),
            Text("Image", font_size=24)
        ).arrange(DOWN, buff=0.3)

        content_group = VGroup(book_icon, video_icon, image_icon).arrange(RIGHT, buff=1.0)
        content_group.move_to(ORIGIN).shift(DOWN * 0.5)
        
        content_explanation = Text("Content is any form of information.", font_size=28)
        content_explanation.next_to(content_group, DOWN, buff=1.0)

        self.play(
            FadeOut(main_phrase, box),
            Write(content_title)
        )
        self.play(FadeIn(content_group, lag_ratio=0.5))
        self.play(Write(content_explanation))
        self.wait(2)

        # 4. Explain "Educational"
        educational_title = Text("Now, what makes it 'Educational'?", font_size=32)
        educational_title.to_edge(UP)

        # Visuals for the learning process
        brain_icon = SVGMobject("brain.svg", color=BLUE_C).scale(0.8)
        lightbulb = SVGMobject("lightbulb.svg", color=YELLOW_C).scale(0.5)
        
        learning_visuals = VGroup(brain_icon, lightbulb).arrange(RIGHT, buff=2.0)
        learning_visuals.move_to(ORIGIN).shift(DOWN * 0.5)
        
        arrow = Arrow(
            start=brain_icon.get_right(),
            end=lightbulb.get_left(),
            buff=0.5,
            color=WHITE
        )

        educational_explanation = Text("It has a goal: to help you learn or understand.", font_size=28)
        educational_explanation.next_to(learning_visuals, DOWN, buff=1.0)

        self.play(
            FadeOut(content_group, content_explanation),
            ReplacementTransform(content_title, educational_title)
        )
        self.play(FadeIn(brain_icon))
        self.play(Create(arrow))
        self.play(FadeIn(lightbulb))
        self.play(Write(educational_explanation))
        self.wait(2)

        # 5. Summary and Conclusion
        summary_title = Text("Putting It All Together", font_size=36)
        summary_title.to_edge(UP)

        # Re-use content icons and learning visuals
        content_icons_small = content_group.copy().scale(0.6).to_edge(LEFT, buff=1.0)
        learning_visuals_small = VGroup(brain_icon, lightbulb).copy().scale(0.6).to_edge(RIGHT, buff=1.0)
        
        summary_arrow = Arrow(
            start=content_icons_small.get_right(),
            end=learning_visuals_small.get_left(),
            buff=0.5,
            color=GREEN
        )

        summary_text = Text(
            "Educational Content uses information (Content)\n"
            "to achieve a learning goal (Educational).",
            font_size=28,
            line_spacing=1.2,
            text_align=CENTER
        ).move_to(ORIGIN).shift(DOWN * 2)

        self.play(
            FadeOut(educational_explanation, learning_visuals, arrow),
            ReplacementTransform(educational_title, summary_title)
        )
        self.play(
            FadeIn(content_icons_small),
            FadeIn(learning_visuals_small),
            Create(summary_arrow)
        )
        self.play(Write(summary_text))
        self.wait(3)

        # Final fade out
        self.play(
            FadeOut(summary_title),
            FadeOut(content_icons_small),
            FadeOut(learning_visuals_small),
            FadeOut(summary_arrow),
            FadeOut(summary_text)
        )
        self.wait(1)

        final_message = Text("The goal is to make learning clear and simple!", font_size=32)
        self.play(Write(final_message))
        self.wait(2)