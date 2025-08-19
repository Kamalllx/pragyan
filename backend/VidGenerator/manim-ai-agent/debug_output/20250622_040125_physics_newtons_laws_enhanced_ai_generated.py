from manim import *

class NewtonsLawsAnimation(Scene):
    def construct(self):
        # Set a background color
        self.camera.background_color = "#0E1A33"

        # --- Title Scene ---
        title = Text("Newton's Laws of Motion", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        self.wait(0.5)

        # --- Newton's First Law: Inertia ---
        law1_title = Text("Newton's First Law: Inertia", font_size=36).to_edge(UP)
        law1_text = Text(
            "An object at rest stays at rest, and an object in motion stays in motion\n"
            "with the same speed and in the same direction unless acted upon by a force.",
            font_size=24,
            line_spacing=0.8
        ).next_to(law1_title, DOWN, buff=0.5)

        self.play(Write(law1_title))
        self.play(FadeIn(law1_text, shift=DOWN))
        self.wait(2)

        # Visual Demonstration for Law 1
        ground = Line(LEFT * 6, RIGHT * 6, color=GRAY).shift(DOWN * 2)
        ball = Circle(radius=0.4, color=BLUE, fill_opacity=1).move_to(LEFT * 4 + DOWN * 1.6)
        
        # Part 1: Object at rest
        rest_text = Text("At Rest", font_size=24).next_to(ball, DOWN, buff=0.5)
        self.play(Create(ground), Create(ball), Write(rest_text))
        self.wait(1)
        self.play(Indicate(ball))
        self.wait(1)

        # Part 2: Object in motion
        force_arrow = Arrow(start=LEFT, end=RIGHT, color=YELLOW).next_to(ball, LEFT, buff=0.1)
        motion_text = Text("In Motion (Constant Velocity)", font_size=24).move_to(rest_text.get_center())
        
        self.play(Create(force_arrow))
        self.wait(0.5)
        self.play(
            FadeOut(force_arrow),
            ball.animate.shift(RIGHT * 8),
            Transform(rest_text, motion_text),
            run_time=3
        )
        self.wait(1)

        law1_group = VGroup(law1_title, law1_text, ground, ball, rest_text)
        self.play(FadeOut(law1_group))
        self.wait(1)

        # --- Newton's Second Law: F = ma ---
        law2_title = Text("Newton's Second Law: F = ma", font_size=36).to_edge(UP)
        law2_text = Text(
            "The acceleration of an object is directly proportional to the net force\n"
            "acting on it and inversely proportional to its mass.",
            font_size=24,
            line_spacing=0.8
        ).next_to(law2_title, DOWN, buff=0.5)
        
        formula = MathTex("F", "=", "m", "a", font_size=48).next_to(law2_text, DOWN, buff=0.8)
        formula[0].set_color(YELLOW) # Force
        formula[2].set_color(BLUE)   # Mass
        formula[3].set_color(RED)    # Acceleration

        self.play(Write(law2_title))
        self.play(FadeIn(law2_text, shift=DOWN))
        self.play(Write(formula))
        self.wait(2)

        # Visual Demonstration for Law 2
        box = Rectangle(width=1.5, height=1.5, color=BLUE, fill_opacity=1).shift(DOWN * 1)
        box_mass_label = MathTex("m", font_size=36, color=WHITE).move_to(box.get_center())
        ground2 = Line(LEFT * 6, RIGHT * 6, color=GRAY).shift(DOWN * 1.75)

        self.play(Create(ground2), Create(box), Write(box_mass_label))
        self.wait(1)

        # Small force -> small acceleration
        force1 = Arrow(start=LEFT*2, end=LEFT*1, color=YELLOW, buff=0).next_to(box, LEFT)
        accel1 = Arrow(start=ORIGIN, end=RIGHT*0.5, color=RED).next_to(box, UP)
        force1_label = MathTex("F", color=YELLOW).next_to(force1, LEFT)
        accel1_label = MathTex("a", color=RED).next_to(accel1, UP)

        self.play(Create(force1), Create(force1_label))
        self.wait(0.5)
        self.play(Create(accel1), Create(accel1_label))
        self.wait(1.5)

        # Large force -> large acceleration
        force2 = Arrow(start=LEFT*3, end=LEFT*1, color=YELLOW, buff=0).next_to(box, LEFT)
        accel2 = Arrow(start=ORIGIN, end=RIGHT*1.5, color=RED).next_to(box, UP)
        force2_label = MathTex("2F", color=YELLOW).next_to(force2, LEFT)
        accel2_label = MathTex("2a", color=RED).next_to(accel2, UP)

        self.play(
            Transform(force1, force2),
            Transform(force1_label, force2_label),
            Transform(accel1, accel2),
            Transform(accel1_label, accel2_label)
        )
        self.wait(2)

        law2_group = VGroup(law2_title, law2_text, formula, ground2, box, box_mass_label, force1, force1_label, accel1, accel1_label)
        self.play(FadeOut(law2_group))
        self.wait(1)

        # --- Newton's Third Law: Action-Reaction ---
        law3_title = Text("Newton's Third Law: Action-Reaction", font_size=36).to_edge(UP)
        law3_text = Text(
            "For every action, there is an equal and opposite reaction.",
            font_size=24
        ).next_to(law3_title, DOWN, buff=0.5)

        self.play(Write(law3_title))
        self.play(FadeIn(law3_text, shift=DOWN))
        self.wait(2)

        # Visual Demonstration for Law 3 (Rocket)
        rocket_body = Polygon([-1, -1.5, 0], [1, -1.5, 0], [1, 1, 0], [-1, 1, 0], color=WHITE, fill_opacity=1)
        rocket_tip = Triangle(color=RED, fill_opacity=1).scale(1).stretch_to_fit_width(2).move_to(rocket_body.get_top(), aligned_edge=DOWN)
        rocket = VGroup(rocket_body, rocket_tip).move_to(ORIGIN).shift(DOWN * 0.5)

        # Action Force (Gas pushing down)
        action_arrow = Arrow(rocket.get_bottom(), rocket.get_bottom() + DOWN * 1.5, color=ORANGE, buff=0)
        action_label = Text("Action (Gas Push)", font_size=24).next_to(action_arrow, DOWN)

        # Reaction Force (Rocket pushing up)
        reaction_arrow = Arrow(rocket.get_center(), rocket.get_center() + UP * 1.5, color=CYAN, buff=0)
        reaction_label = Text("Reaction (Rocket Moves)", font_size=24).next_to(reaction_arrow, UP)

        self.play(Create(rocket))
        self.wait(1)
        self.play(
            Create(action_arrow),
            Create(reaction_arrow),
            Write(action_label),
            Write(reaction_label)
        )
        self.wait(1)
        
        # Animate rocket launch
        rocket_group = VGroup(rocket, action_arrow, reaction_arrow, action_label, reaction_label)
        self.play(rocket_group.animate.shift(UP * 2), run_time=2)
        self.wait(1)

        law3_group = VGroup(law3_title, law3_text, rocket_group)
        self.play(FadeOut(law3_group))
        self.wait(1)

        # --- Summary Scene ---
        summary_title = Text("Summary: Newton's Three Laws", font_size=40).to_edge(UP)
        
        summary1 = Text("1. Inertia: Objects resist changes in motion.", font_size=28)
        summary2 = Text("2. Force = Mass × Acceleration (F=ma)", font_size=28)
        summary3 = Text("3. Action-Reaction: Forces come in equal and opposite pairs.", font_size=28)

        summary_group = VGroup(summary1, summary2, summary3).arrange(DOWN, buff=0.8).next_to(summary_title, DOWN, buff=1.0)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_group, lag_ratio=0.5))
        
        self.wait(2)