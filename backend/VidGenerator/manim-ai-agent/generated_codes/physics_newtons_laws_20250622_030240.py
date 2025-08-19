from manim import *

class NewtonsLawsAnimation(Scene):
    """
    An engaging and educational animation explaining Newton's Three Laws of Motion
    for beginners in physics.
    """
    def construct(self):
        # Set a consistent theme for the scene
        self.camera.background_color = "#0d1b2a"
        title_color = "#e0e1dd"
        text_color = "#e0e1dd"
        law_color = "#415a77"
        force_color = "#fca311"
        object_color = "#778da9"

        # --- SCENE 1: TITLE ---
        title = Text("Newton's Laws of Motion", font_size=48, color=title_color)
        title.to_edge(UP)

        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        self.wait(0.5)

        # --- SCENE 2: NEWTON'S FIRST LAW ---
        law1_title = Text("1. The Law of Inertia", font_size=36, color=law_color)
        law1_title.to_edge(UP, buff=1.0)

        law1_expl = Text(
            "An object stays at rest or in uniform motion\nunless a force acts on it.",
            font_size=24,
            color=text_color,
            text_align=ORIGIN
        )
        law1_expl.next_to(law1_title, DOWN, buff=0.5)

        self.play(Write(law1_title))
        self.play(FadeIn(law1_expl, shift=DOWN))
        self.wait(1)

        # Visual Demonstration for Law 1
        ground = Line([-6, -2, 0], [6, -2, 0], color=GREY_B)
        ball_at_rest = Circle(radius=0.4, color=object_color, fill_opacity=1).move_to([-4, -1.6, 0])
        rest_label = Text("At Rest", font_size=24, color=text_color).next_to(ball_at_rest, DOWN, buff=0.5)

        self.play(Create(ground))
        self.play(FadeIn(ball_at_rest), Write(rest_label))
        self.wait(1)
        self.play(Indicate(ball_at_rest))
        self.wait(1)

        # Clean up for next part of Law 1
        law1_group = VGroup(law1_title, law1_expl, ground, ball_at_rest, rest_label)
        self.play(FadeOut(law1_group))
        self.wait(0.5)

        # --- SCENE 3: NEWTON'S SECOND LAW ---
        law2_title = Text("2. The Law of Acceleration", font_size=36, color=law_color)
        law2_title.to_edge(UP, buff=1.0)

        law2_formula = MathTex("F", "=", "m", "\\times", "a", font_size=48)
        law2_formula.set_color_by_tex("F", force_color)
        law2_formula.set_color_by_tex("m", object_color)
        law2_formula.set_color_by_tex("a", YELLOW)
        law2_formula.next_to(law2_title, DOWN, buff=0.8)

        self.play(Write(law2_title))
        self.play(Write(law2_formula))
        self.wait(1)

        # Visual Demonstration for Law 2
        block = Rectangle(width=1.5, height=1, color=object_color, fill_opacity=1).move_to([-4, -1, 0])
        mass_label = MathTex("m", font_size=32, color=text_color).move_to(block.get_center())
        block_group = VGroup(block, mass_label)

        force_arrow_small = Arrow(start=LEFT, end=RIGHT, color=force_color, buff=0).scale(0.8)
        force_arrow_small.next_to(block, LEFT, buff=0.2)
        force_label_small = MathTex("F", font_size=32, color=force_color).next_to(force_arrow_small, LEFT)

        accel_label_small = MathTex("a", font_size=32, color=YELLOW).next_to(block, UP)

        self.play(Create(block_group), Create(force_arrow_small), Write(force_label_small))
        self.wait(0.5)
        self.play(
            block_group.animate.shift(RIGHT * 2),

        animate.shift(DOWN * 1.5)  # Auto-spacing fix

        animate.shift(DOWN * 1.5)  # Auto-spacing fix

        animate.shift(DOWN * 1.5)  # Auto-spacing fix
            FadeIn(accel_label_small.copy().next_to(block_group, UP)),
            run_time=2
        )
        self.wait(1)

        force_arrow_large = Arrow(start=LEFT, end=RIGHT, color=force_color, buff=0).scale(1.6)
        force_arrow_large.next_to(block_group, LEFT, buff=0.2)
        force_label_large = MathTex("2F", font_size=32, color=force_color).next_to(force_arrow_large, LEFT)
        accel_label_large = MathTex("2a", font_size=32, color=YELLOW).next_to(block_group, UP)

        self.play(Transform(force_arrow_small, force_arrow_large), Transform(force_label_small, force_label_large))
        self.wait(0.5)
        self.play(
            block_group.animate.shift(RIGHT * 4),
            FadeIn(accel_label_large.copy().next_to(block_group, UP)),
            run_time=1.5
        )
        self.wait(1)

        # Clean up
        law2_group = VGroup(law2_title, law2_formula, block_group, force_arrow_small, force_label_small, force_label_large)
        self.play(FadeOut(law2_group))
        self.wait(0.5)

        # --- SCENE 4: NEWTON'S THIRD LAW ---
        law3_title = Text("3. The Law of Action-Reaction", font_size=36, color=law_color)
        law3_title.to_edge(UP, buff=1.0)

        law3_expl = Text(
            "For every action, there is an equal and opposite reaction.",
            font_size=24,
            color=text_color,
            text_align=ORIGIN
        )
        law3_expl.next_to(law3_title, DOWN, buff=0.5)

        self.play(Write(law3_title))
        self.play(FadeIn(law3_expl, shift=DOWN))
        self.wait(1)

        # Visual Demonstration for Law 3 (Rocket)
        rocket_body = Polygon([-0.5, -1.5, 0], [0.5, -1.5, 0], [0.5, 1, 0], [-0.5, 1, 0], color=object_color, fill_opacity=1)
        rocket_tip = Triangle(color=RED, fill_opacity=1).scale(0.5).stretch_to_fit_height(0.7)
        rocket_tip.next_to(rocket_body, UP, buff=0)
        rocket = VGroup(rocket_body, rocket_tip).move_to(ORIGIN).shift(DOWN * 1)

        # Action Force (Gas pushing down)
        action_arrow = Arrow(rocket.get_bottom(), rocket.get_bottom() + DOWN * 1.5, color=force_color, buff=0.1)
        action_label = Text("Action", font_size=24, color=force_color).next_to(action_arrow, DOWN)

        # Reaction Force (Rocket pushing up)
        reaction_arrow = Arrow(rocket.get_center(), rocket.get_center() + UP * 1.5, color=force_color, buff=0.1)
        reaction_label = Text("Reaction", font_size=24, color=force_color).next_to(reaction_arrow, UP)

        self.play(FadeIn(rocket))
        self.wait(0.5)
        self.play(
            Create(action_arrow),
            Write(action_label),
            Create(reaction_arrow),
            Write(reaction_label)
        )
        self.wait(1)

        # Animate rocket launch
        self.play(
            rocket.animate.shift(UP * 3),
            action_arrow.animate.shift(UP * 3),
            action_label.animate.shift(UP * 3),
            reaction_arrow.animate.shift(UP * 3),
            reaction_label.animate.shift(UP * 3),
            run_time=2
        )
        self.wait(1)

        # Clean up
        law3_group = VGroup(law3_title, law3_expl, rocket, action_arrow, action_label, reaction_arrow, reaction_label)
        self.play(FadeOut(law3_group))
        self.wait(0.5)

        # --- SCENE 5: SUMMARY ---
        summary_title = Text("In Summary", font_size=48, color=title_color)
        summary_title.to_edge(UP)

        law1_summary = Text("1. Inertia: Objects resist changes in motion.", font_size=28, color=text_color)
        law2_summary = MathTex("2. \\text{Force: } F = m \\times a", font_size=28, color=text_color)
        law3_summary = Text("3. Action-Reaction: Forces act in equal, opposite pairs.", font_size=28, color=text_color)

        summary_group = VGroup(law1_summary, law2_summary, law3_summary)
        summary_group.arrange(DOWN, buff=0.8).next_to(summary_title, DOWN, buff=1.0)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_group, lag_ratio=0.5, shift=UP))

        self.wait(3)