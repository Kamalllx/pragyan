from manim import *

class NewtonsLawsScene(Scene):
    def construct(self):
        # 1. Title Introduction
        title = Text("Newton's Laws of Motion", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)

        # --- Newton's First Law ---
        first_law_title = Text("Newton's First Law: The Law of Inertia", font_size=36).to_edge(UP)
        first_law_text = Text(
            "An object at rest stays at rest, and an object in motion stays in motion\n"
            "with the same speed and in the same direction unless acted upon by a net force.",
            font_size=24,
            line_spacing=0.8
        ).next_to(first_law_title, DOWN, buff=0.5)

        self.play(Write(first_law_title))
        self.play(FadeIn(first_law_text))
        self.wait(3)

        # Visual Demonstration 1: Object at Rest
        ball_rest = Circle(radius=0.5, color=BLUE, fill_opacity=1).shift(LEFT * 3)
        label_rest = Text("At Rest (Net Force = 0)", font_size=24).next_to(ball_rest, DOWN, buff=0.5)
        rest_group = VGroup(ball_rest, label_rest)

        self.play(Create(ball_rest), Write(label_rest))
        self.wait(2)

        # Visual Demonstration 2: Object in Motion
        ball_motion = Circle(radius=0.5, color=GREEN, fill_opacity=1).shift(RIGHT * 3)
        label_motion = Text("Constant Velocity (Net Force = 0)", font_size=24).next_to(ball_motion, DOWN, buff=0.5)
        motion_group = VGroup(ball_motion, label_motion)

        self.play(Create(ball_motion), Write(label_motion))
        self.play(Indicate(motion_group))
        self.wait(2)

        self.play(FadeOut(first_law_title, first_law_text, rest_group, motion_group))
        self.wait(1)

        # --- Newton's Second Law ---
        second_law_title = Text("Newton's Second Law: Force and Acceleration", font_size=36).to_edge(UP)
        second_law_formula = MathTex("F_{net} = m \\times a", font_size=48).next_to(second_law_title, DOWN, buff=0.7)
        second_law_text = Text(
            "The acceleration of an object is directly proportional to the net force\n"
            "acting on it and inversely proportional to its mass.",
            font_size=24,
            line_spacing=0.8
        ).next_to(second_law_formula, DOWN, buff=0.7)

        self.play(Write(second_law_title))
        self.play(Write(second_law_formula))
        self.play(FadeIn(second_law_text))
        self.wait(3)

        # Visual Demonstration
        box = Rectangle(width=1.5, height=1, color=ORANGE, fill_opacity=1).shift(DOWN * 1.5)
        mass_label = MathTex("m").move_to(box.get_center())
        box_group = VGroup(box, mass_label)

        # Scenario 1: Small Force -> Small Acceleration
        force1 = Arrow(start=box.get_left() + LEFT*2, end=box.get_left(), buff=0.1, color=YELLOW)
        force1_label = MathTex("F_{small}").next_to(force1, LEFT)
        accel1 = Arrow(start=box.get_right(), end=box.get_right() + RIGHT*0.5, buff=0.1, color=RED)
        accel1_label = MathTex("a_{small}").next_to(accel1, RIGHT)

        self.play(FadeIn(box_group), Create(force1), Write(force1_label))
        self.play(Create(accel1), Write(accel1_label))
        self.wait(2)

        # Scenario 2: Large Force -> Large Acceleration
        force2 = Arrow(start=box.get_left() + LEFT*3, end=box.get_left(), buff=0.1, color=YELLOW, max_tip_length_to_length_ratio=0.2)
        force2_label = MathTex("F_{LARGE}").next_to(force2, LEFT)
        accel2 = Arrow(start=box.get_right(), end=box.get_right() + RIGHT*2, buff=0.1, color=RED, max_tip_length_to_length_ratio=0.2)
        accel2_label = MathTex("a_{LARGE}").next_to(accel2, RIGHT)

        self.play(
            Transform(force1, force2),
            Transform(force1_label, force2_label),
            Transform(accel1, accel2),
            Transform(accel1_label, accel2_label)
        )
        self.wait(3)

        self.play(FadeOut(second_law_title, second_law_formula, second_law_text, box_group, force1, force1_label, accel1, accel1_label))
        self.wait(1)

        # --- Newton's Third Law ---
        third_law_title = Text("Newton's Third Law: Action-Reaction", font_size=36).to_edge(UP)
        third_law_text = Text(
            "For every action, there is an equal and opposite reaction.",
            font_size=24
        ).next_to(third_law_title, DOWN, buff=0.5)
        third_law_formula = MathTex("F_{AB} = -F_{BA}", font_size=48).next_to(third_law_text, DOWN, buff=0.8)

        self.play(Write(third_law_title))
        self.play(FadeIn(third_law_text))
        self.play(Write(third_law_formula))
        self.wait(3)

        # Visual Demonstration: Two boxes pushing each other
        box_A = Rectangle(width=1.5, height=1.5, color=BLUE, fill_opacity=1).shift(LEFT * 1.5)
        label_A = Text("A").move_to(box_A.get_center())
        group_A = VGroup(box_A, label_A)

        box_B = Rectangle(width=1.5, height=1.5, color=PURPLE, fill_opacity=1).shift(RIGHT * 1.5)
        label_B = Text("B").move_to(box_B.get_center())
        group_B = VGroup(box_B, label_B)

        # Action-Reaction Force Pair
        force_AB = Arrow(start=box_A.get_right(), end=box_B.get_left(), buff=0.1, color=GREEN)
        label_AB = MathTex("F_{AB}").next_to(force_AB, UP, buff=0.2)
        
        force_BA = Arrow(start=box_B.get_left(), end=box_A.get_right(), buff=0.1, color=RED)
        label_BA = MathTex("F_{BA}").next_to(force_BA, DOWN, buff=0.2)

        action_reaction_group = VGroup(group_A, group_B, force_AB, label_AB, force_BA, label_BA).shift(DOWN * 1)

        self.play(FadeIn(action_reaction_group))
        self.wait(2)
        self.play(
            group_A.animate.shift(LEFT * 1),
            group_B.animate.shift(RIGHT * 1)
        )
        self.wait(3)

        self.play(FadeOut(third_law_title, third_law_text, third_law_formula, action_reaction_group))
        self.wait(1)

        # --- Summary ---
        summary_title = Text("Summary: Newton's Three Laws", font_size=40).to_edge(UP)
        
        law1_summary = Text("1. Inertia: Objects resist changes in motion.", font_size=28)
        law2_summary = Text("2. Force: F = ma", font_size=28)
        law3_summary = Text("3. Action-Reaction: Forces come in equal and opposite pairs.", font_size=28)

        summary_group = VGroup(law1_summary, law2_summary, law3_summary).arrange(DOWN, buff=0.8).next_to(summary_title, DOWN, buff=1.0)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_group, shift=UP))
        self.wait(4)

        self.play(FadeOut(summary_title, summary_group))
        self.wait(2)