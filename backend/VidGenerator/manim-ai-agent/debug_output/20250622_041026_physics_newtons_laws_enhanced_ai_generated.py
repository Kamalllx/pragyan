from manim import *

class NewtonsLawsOfMotion(Scene):
    def construct(self):
        # Set a background color
        self.camera.background_color = "#0E1A25"

        # --- Title Introduction ---
        title = Text("Newton's Laws of Motion", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # --- Newton's First Law: Inertia ---
        law1_title = Text("1. The Law of Inertia", font_size=36).next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(law1_title, shift=DOWN))
        self.wait(1)

        # Visual Demonstration for Law 1
        ball = Circle(radius=0.5, color=BLUE, fill_opacity=1).move_to(LEFT * 4 + DOWN * 1)
        ball_label = Text("At Rest", font_size=24).next_to(ball, DOWN)
        
        explanation1 = Text("An object at rest stays at rest...", font_size=24).to_edge(DOWN, buff=1.0)
        self.play(Create(ball), Write(ball_label))
        self.play(Write(explanation1))
        self.wait(2)

        force_arrow = Arrow(start=LEFT, end=RIGHT, color=YELLOW).next_to(ball, LEFT, buff=0.1)
        force_label = MathTex("F", font_size=36, color=YELLOW).next_to(force_arrow, LEFT)
        
        explanation2 = Text("...unless acted on by a force.", font_size=24).next_to(explanation1, DOWN, buff=0.2)
        self.play(Create(force_arrow), Write(force_label))
        self.play(Write(explanation2))
        self.wait(1)

        self.play(ball.animate.shift(RIGHT * 8), run_time=3)
        self.wait(2)

        # Cleanup for next scene
        law1_group = VGroup(law1_title, ball, ball_label, explanation1, explanation2, force_arrow, force_label)
        self.play(FadeOut(law1_group))

        # --- Newton's Second Law: F = ma ---
        law2_title = Text("2. Force, Mass, and Acceleration", font_size=36).next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(law2_title, shift=DOWN))
        self.wait(1)

        # Visual Demonstration for Law 2
        formula = MathTex("F = m \\times a", font_size=48).to_edge(DOWN, buff=1.0)
        
        # Objects
        small_mass = Rectangle(width=1.0, height=1.0, color=GREEN, fill_opacity=1).move_to(LEFT * 4 + UP * 0.5)
        small_mass_label = MathTex("m").next_to(small_mass, DOWN)
        
        large_mass = Rectangle(width=2.0, height=2.0, color=ORANGE, fill_opacity=1).move_to(LEFT * 4 + DOWN * 2.0)
        large_mass_label = MathTex("M", font_size=48).next_to(large_mass, DOWN)

        mass_group = VGroup(small_mass, small_mass_label, large_mass, large_mass_label)

        # Forces
        force1 = Arrow(start=LEFT, end=RIGHT, color=YELLOW).next_to(small_mass, LEFT)
        force1_label = MathTex("F").next_to(force1, LEFT)
        
        force2 = Arrow(start=LEFT, end=RIGHT, color=YELLOW).next_to(large_mass, LEFT)
        force2_label = MathTex("F").next_to(force2, LEFT)

        force_group = VGroup(force1, force1_label, force2, force2_label)

        self.play(Write(formula))
        self.play(Create(mass_group))
        self.wait(1)
        self.play(Create(force_group))
        self.wait(1)

        # Animate acceleration
        self.play(
            small_mass.animate.shift(RIGHT * 6),
            large_mass.animate.shift(RIGHT * 2),
            run_time=3
        )
        self.wait(2)

        # Cleanup
        law2_group = VGroup(law2_title, formula, mass_group, force_group)
        self.play(FadeOut(law2_group))

        # --- Newton's Third Law: Action-Reaction ---
        law3_title = Text("3. Action and Reaction", font_size=36).next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(law3_title, shift=DOWN))
        self.wait(1)

        # Visual Demonstration for Law 3
        rocket_body = Polygon([-1, -1.5, 0], [1, -1.5, 0], [0, 1.5, 0], color=WHITE, fill_opacity=1)
        rocket = VGroup(rocket_body).move_to(ORIGIN).scale(0.8)

        action_arrow = Arrow(start=rocket.get_bottom(), end=rocket.get_bottom() + DOWN, color=RED, buff=0.1)
        action_label = Text("Action", font_size=24, color=RED).next_to(action_arrow, DOWN)
        
        reaction_arrow = Arrow(start=rocket.get_center(), end=rocket.get_center() + UP, color=CYAN)
        reaction_label = Text("Reaction", font_size=24, color=CYAN).next_to(reaction_arrow, UP)

        explanation3 = Text("For every action, there is an equal and opposite reaction.", font_size=24).to_edge(DOWN, buff=1.0)

        self.play(Create(rocket))
        self.play(Write(explanation3))
        self.wait(1)

        self.play(
            Create(action_arrow), Write(action_label),
            Create(reaction_arrow), Write(reaction_label)
        )
        self.wait(1)

        self.play(
            rocket.animate.shift(UP * 2),
            VGroup(action_arrow, action_label).animate.shift(UP * 2),
            VGroup(reaction_arrow, reaction_label).animate.shift(UP * 2),
            run_time=2
        )
        self.wait(2)

        # Cleanup
        law3_group = VGroup(law3_title, rocket, action_arrow, action_label, reaction_arrow, reaction_label, explanation3)
        self.play(FadeOut(law3_group))
        self.play(FadeOut(title))

        # --- Summary ---
        summary_title = Text("In Summary:", font_size=48)
        
        law1_summary = Text("1. Objects resist changes in motion.", font_size=32)
        law2_summary = MathTex("2. F = ma", font_size=36)
        law3_summary = Text("3. Action equals Reaction.", font_size=32)

        summary_group = VGroup(summary_title, law1_summary, law2_summary, law3_summary)
        summary_group.arrange(DOWN, buff=0.8).move_to(ORIGIN)

        self.play(Write(summary_group))
        self.wait(2)