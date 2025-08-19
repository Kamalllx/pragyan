from manim import *

class NewtonsLaws(Scene):
    def construct(self):
        """
        An animation explaining Newton's Three Laws of Motion for beginners.
        """
        # Set a consistent theme
        self.camera.background_color = "#0d1117"

        # --- Title Introduction ---
        title = Text("Newton's Laws of Motion", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP).scale(0.8))
        self.wait(0.5)

        # --- Newton's First Law: Law of Inertia ---
        self.show_first_law()

        # --- Newton's Second Law: F = ma ---
        self.show_second_law()

        # --- Newton's Third Law: Action-Reaction ---
        self.show_third_law()

        # --- Summary ---
        self.show_summary()

        self.wait(2)

    def show_first_law(self):
        """
        Visualizes Newton's First Law of Motion.
        """
        # --- Law Title ---
        law1_title = Text("1. The Law of Inertia", font_size=36).to_edge(UP, buff=1.5)
        self.play(FadeIn(law1_title))
        self.wait(1)

        # --- Part 1: Object at Rest ---
        ball_rest = Circle(radius=0.5, color=BLUE, fill_opacity=1).shift(LEFT * 3)
        label_rest = Text("An object at rest...", font_size=24).next_to(ball_rest, DOWN, buff=0.5)
        group_rest = VGroup(ball_rest, label_rest)

        self.play(Create(ball_rest), Write(label_rest))
        self.wait(1.5)
        self.play(Indicate(ball_rest))
        self.wait(1)

        # --- Part 2: Object in Motion ---
        ball_motion = Circle(radius=0.5, color=GREEN, fill_opacity=1).shift(RIGHT * 3)
        label_motion = Text("...stays in motion.", font_size=24).next_to(ball_motion, DOWN, buff=0.5)
        group_motion = VGroup(ball_motion, label_motion)

        self.play(Create(ball_motion), Write(label_motion))
        self.wait(1)
        self.play(ball_motion.animate.shift(UP * 2), run_time=2, rate_func=linear)
        self.wait(1)

        # --- Part 3: Unbalanced Force ---
        force_arrow = Arrow(start=LEFT, end=RIGHT, color=YELLOW).next_to(ball_rest, LEFT, buff=0.1)
        force_label = MathTex(r"\vec{F}", font_size=36, color=YELLOW).next_to(force_arrow, UP, buff=0.2)
        force_group = VGroup(force_arrow, force_label)
        
        explanation = Text("...unless a force acts on it.", font_size=24).shift(DOWN * 2.5)
        self.play(Write(explanation))
        self.play(FadeIn(force_group))
        self.play(
            force_group.animate.shift(RIGHT * 1.5),
            ball_rest.animate.shift(RIGHT * 1.5),
            run_time=1
        )
        self.play(ball_rest.animate.shift(RIGHT * 3), run_time=1.5)
        self.wait(1)

        # --- Cleanup ---
        self.play(
            FadeOut(law1_title),
            FadeOut(group_rest),
            FadeOut(group_motion.move_to(RIGHT * 3)), # Reset position for fadeout
            FadeOut(force_group),
            FadeOut(explanation)
        )
        self.wait(0.5)

    def show_second_law(self):
        """
        Visualizes Newton's Second Law of Motion.
        """
        # --- Law Title and Formula ---
        law2_title = Text("2. Force, Mass, and Acceleration", font_size=36).to_edge(UP, buff=1.5)
        formula = MathTex("F = m \\times a", font_size=48)
        VGroup(law2_title, formula).arrange(DOWN, buff=0.5)
        
        self.play(Write(law2_title))
        self.play(FadeIn(formula))
        self.wait(2)
        self.play(formula.animate.to_edge(UP, buff=2.5))

        # --- Demonstration ---
        # Setup scene
        ground = Line(start=LEFT * 6, end=RIGHT * 6, color=GRAY).shift(DOWN * 2)
        box1 = Rectangle(width=1, height=1, color=ORANGE, fill_opacity=1).move_to(LEFT * 4 + DOWN * 1.5)
        box2 = Rectangle(width=2, height=1, color=ORANGE, fill_opacity=1).move_to(RIGHT * 2 + DOWN * 1.5)
        
        label_m1 = MathTex("m").next_to(box1, UP)
        label_m2 = MathTex("2m").next_to(box2, UP)
        
        self.play(Create(ground), Create(box1), Create(box2), Write(label_m1), Write(label_m2))
        self.wait(1)

        # Apply same force to both
        force1 = Arrow(start=LEFT, end=RIGHT, color=RED).scale(1.5).next_to(box1, LEFT)
        force2 = Arrow(start=LEFT, end=RIGHT, color=RED).scale(1.5).next_to(box2, LEFT)
        force_label = MathTex(r"\vec{F}").next_to(force1, UP)
        
        explanation = Text("Same force, different mass...", font_size=24).shift(DOWN * 3)
        self.play(Write(explanation))
        self.play(FadeIn(force1), FadeIn(force2), Write(force_label))
        self.wait(1)

        # Animate the result
        # Smaller mass (box1) accelerates more
        self.play(
            box1.animate.shift(RIGHT * 4),
            label_m1.animate.shift(RIGHT * 4),
            force1.animate.shift(RIGHT * 4),
            # Larger mass (box2) accelerates less
            box2.animate.shift(RIGHT * 2),
            label_m2.animate.shift(RIGHT * 2),
            force2.animate.shift(RIGHT * 2),
            run_time=2
        )
        result_text = Text("...results in different acceleration.", font_size=24).move_to(explanation)
        self.play(Transform(explanation, result_text))
        self.wait(2)

        # --- Cleanup ---
        self.play(
            FadeOut(law2_title),
            FadeOut(formula),
            FadeOut(ground),
            FadeOut(box1), FadeOut(box2),
            FadeOut(label_m1), FadeOut(label_m2),
            FadeOut(force1), FadeOut(force2),
            FadeOut(force_label),
            FadeOut(explanation)
        )
        self.wait(0.5)

    def show_third_law(self):
        """
        Visualizes Newton's Third Law of Motion.
        """
        # --- Law Title ---
        law3_title = Text("3. Action and Reaction", font_size=36).to_edge(UP, buff=1.5)
        self.play(Write(law3_title))
        self.wait(1)

        # --- Rocket Example ---
        rocket_body = Polygon([-0.5, -1, 0], [0.5, -1, 0], [0, 1, 0], color=WHITE, fill_opacity=1)
        fin1 = Polygon([0.5, -0.5, 0], [0.8, -1, 0], [0.5, -1, 0], color=RED, fill_opacity=1)
        fin2 = Polygon([-0.5, -0.5, 0], [-0.8, -1, 0], [-0.5, -1, 0], color=RED, fill_opacity=1)
        rocket = VGroup(rocket_body, fin1, fin2).move_to(ORIGIN)

        self.play(Create(rocket))
        self.wait(1)

        # Action Force (Gas pushing down)
        action_arrow = Arrow(start=ORIGIN, end=DOWN * 1.5, color=YELLOW).next_to(rocket, DOWN, buff=0)
        action_label = Text("Action (Gas pushed down)", font_size=24).next_to(action_arrow, DOWN)
        
        # Reaction Force (Rocket pushed up)
        reaction_arrow = Arrow(start=ORIGIN, end=UP * 1.5, color=CYAN).next_to(rocket, UP, buff=0)
        reaction_label = Text("Reaction (Rocket pushed up)", font_size=24).next_to(reaction_arrow, UP)

        explanation = MathTex(r"F_{action} = -F_{reaction}", font_size=36).shift(DOWN * 3)

        self.play(
            Write(explanation),
            GrowArrow(action_arrow), Write(action_label),
            GrowArrow(reaction_arrow), Write(reaction_label)
        )
        self.wait(2)

        # Animate the launch
        self.play(
            rocket.animate.shift(UP * 3),
            FadeOut(reaction_arrow), FadeOut(reaction_label),
            FadeOut(action_arrow), FadeOut(action_label),
            run_time=2
        )
        self.wait(1)

        # --- Cleanup ---
        self.play(
            FadeOut(law3_title),
            FadeOut(rocket),
            FadeOut(explanation)
        )
        self.wait(0.5)

    def show_summary(self):
        """
        Displays a final summary of the three laws.
        """
        summary_title = Text("In Summary:", font_size=40).to_edge(UP, buff=1.5)

        law1_summary = Text("1. Objects resist changes in motion (Inertia).", font_size=28)
        law2_summary = Text("2. More force or less mass means more acceleration.", font_size=28)
        law3_summary = Text("3. Every action has an equal and opposite reaction.", font_size=28)

        summary_group = VGroup(law1_summary, law2_summary, law3_summary).arrange(DOWN, buff=0.8)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_group, shift=UP))
        self.wait(3)