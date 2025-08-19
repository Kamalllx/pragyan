from manim import *

class NewtonsLawsScene(Scene):
    """
    An educational Manim animation explaining Newton's Three Laws of Motion
    for beginners in physics.
    """
    def construct(self):
        # Set a consistent theme
        self.camera.background_color = "#0E1A25"

        # --- 1. Title Introduction ---
        title = Text("Newton's Laws of Motion", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # --- 2. Newton's First Law: Inertia ---
        law1_title = Text("1. The Law of Inertia", font_size=36).next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(law1_title, shift=DOWN))
        self.wait(1)

        # Explanation text
        law1_expl = Text(
            "An object at rest stays at rest, and an object in motion stays in motion...",
            font_size=24
        ).next_to(law1_title, DOWN, buff=0.5)
        law1_expl2 = Text(
            "...unless acted upon by an external force.",
            font_size=24
        ).next_to(law1_expl, DOWN, buff=0.2)
        
        self.play(Write(law1_expl))
        self.play(Write(law1_expl2))
        self.wait(2)

        # Visual Demonstration
        ball = Circle(radius=0.5, color=BLUE, fill_opacity=1).move_to(LEFT * 4 + DOWN * 1.5)
        label_rest = Text("At Rest", font_size=24).next_to(ball, DOWN)
        
        self.play(Create(ball), Write(label_rest))
        self.wait(1)

        # Apply a force
        force_arrow = Arrow(start=LEFT, end=RIGHT, color=YELLOW).next_to(ball, LEFT, buff=0.1)
        force_label = MathTex("F", color=YELLOW).next_to(force_arrow, UP)
        
        self.play(Create(force_arrow), Write(force_label))
        self.wait(0.5)
        self.play(ball.animate.shift(RIGHT * 8), run_time=3, rate_func=linear)
        
        label_motion = Text("In Motion", font_size=24).next_to(ball, DOWN)
        self.play(FadeOut(force_arrow, force_label), Transform(label_rest, label_motion))
        self.wait(2)

        # Cleanup for next scene
        self.play(FadeOut(law1_title, law1_expl, law1_expl2, ball, label_rest))
        self.wait(1)

        # --- 3. Newton's Second Law: F = ma ---
        law2_title = Text("2. The Law of Acceleration", font_size=36).next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(law2_title, shift=DOWN))
        self.wait(1)

        # The formula
        formula = MathTex("F", "=", "m", "\\times", "a", font_size=60)
        formula.move_to(ORIGIN + UP * 1.5)
        self.play(Write(formula))
        self.wait(1)

        # Explanation of terms
        f_text = Text("Force", font_size=24).next_to(formula[0], DOWN, buff=0.5)
        m_text = Text("Mass", font_size=24).next_to(formula[2], DOWN, buff=0.5)
        a_text = Text("Acceleration", font_size=24).next_to(formula[4], DOWN, buff=0.5)
        
        explanation_group = VGroup(f_text, m_text, a_text)
        self.play(Write(explanation_group))
        self.wait(2)

        # Visual Demonstration
        ground = Line(start=LEFT * 6, end=RIGHT * 6, color=GRAY).to_edge(DOWN, buff=2)
        block = Rectangle(width=1.5, height=1, color=ORANGE, fill_opacity=1).move_to(LEFT * 4).align_to(ground, DOWN)
        
        self.play(Create(ground), Create(block))
        self.wait(1)

        # Small force -> small acceleration
        force1 = Arrow(start=LEFT, end=RIGHT, color=YELLOW, max_tip_length_to_length_ratio=0.2).scale(0.8).next_to(block, LEFT)
        accel1 = Arrow(start=LEFT, end=RIGHT, color=RED, max_tip_length_to_length_ratio=0.2).scale(0.5).next_to(block, UP)
        accel1_label = MathTex("a", color=RED).next_to(accel1, UP, buff=0.1)

        self.play(Create(force1))
        self.play(Create(accel1), Write(accel1_label))
        self.wait(1.5)

        # Large force -> large acceleration
        force2 = Arrow(start=LEFT, end=RIGHT, color=YELLOW, max_tip_length_to_length_ratio=0.2).scale(1.6).next_to(block, LEFT)
        accel2 = Arrow(start=LEFT, end=RIGHT, color=RED, max_tip_length_to_length_ratio=0.2).scale(1.0).next_to(block, UP)
        accel2_label = MathTex("A", color=RED).next_to(accel2, UP, buff=0.1)

        self.play(Transform(force1, force2), Transform(accel1, accel2), Transform(accel1_label, accel2_label))
        self.wait(2)

        # Cleanup
        self.play(FadeOut(law2_title, formula, explanation_group, ground, block, force1, accel1, accel1_label))
        self.wait(1)

        # --- 4. Newton's Third Law: Action-Reaction ---
        law3_title = Text("3. The Law of Action-Reaction", font_size=36).next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(law3_title, shift=DOWN))
        self.wait(1)

        law3_expl = Text("For every action, there is an equal and opposite reaction.", font_size=24).next_to(law3_title, DOWN, buff=0.5)
        self.play(Write(law3_expl))
        self.wait(2)

        # Visual Demonstration with two boxes
        box_a = Rectangle(width=1.5, height=1.5, color=GREEN, fill_opacity=1).move_to(LEFT * 2)
        box_b = Rectangle(width=1.5, height=1.5, color=PURPLE, fill_opacity=1).move_to(RIGHT * 2)
        label_a = Text("A").move_to(box_a.get_center())
        label_b = Text("B").move_to(box_b.get_center())
        
        boxes = VGroup(box_a, box_b, label_a, label_b)
        self.play(Create(boxes))
        self.wait(1)

        # Action force from A on B
        action_force = Arrow(box_a.get_right(), box_b.get_left(), buff=0.1, color=CYAN)
        action_label = MathTex(r"F_{A \to B}", color=CYAN, font_size=30).next_to(action_force, UP)
        
        # Reaction force from B on A
        reaction_force = Arrow(box_b.get_left(), box_a.get_right(), buff=0.1, color=PINK)
        reaction_label = MathTex(r"F_{B \to A}", color=PINK, font_size=30).next_to(reaction_force, DOWN)

        self.play(box_a.animate.shift(RIGHT), box_b.animate.shift(LEFT))
        self.play(Create(action_force), Write(action_label))
        self.play(Create(reaction_force), Write(reaction_label))
        self.wait(1)
        self.play(Indicate(action_force), Indicate(reaction_force))
        self.wait(2)

        # Cleanup
        self.play(FadeOut(law3_title, law3_expl, boxes, action_force, action_label, reaction_force, reaction_label))
        self.wait(1)

        # --- 5. Summary ---
        summary_title = Text("In Summary", font_size=40).to_edge(UP, buff=1.5)
        
        summary1 = Text("1. Inertia: Objects resist changes in motion.", font_size=28)
        summary2 = Text("2. Acceleration: F = m × a", font_size=28)
        summary3 = Text("3. Action-Reaction: Forces come in equal and opposite pairs.", font_size=28)

        summary_group = VGroup(summary1, summary2, summary3).arrange(DOWN, buff=0.8)
        summary_group.next_to(summary_title, DOWN, buff=1.0)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_group, lag_ratio=0.5, shift=UP))
        self.wait(3)

        # Final Fade Out
        self.play(FadeOut(title), FadeOut(summary_title), FadeOut(summary_group))
        self.wait(2)