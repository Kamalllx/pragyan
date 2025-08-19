from manim import *

class ProjectileMotionScene(Scene):
    """
    An animation explaining the basics of projectile motion for beginners.
    This scene breaks down the motion into its horizontal and vertical components
    and visualizes the parabolic trajectory.
    """
    def construct(self):
        # 1. Title Introduction
        self.show_title()
        
        # 2. Main educational content with visual demonstrations
        self.setup_and_launch()

        # 3. Key concepts with clear explanations
        self.decompose_motion()

        # 4. Examples or applications
        self.show_velocity_vectors()

        # 5. Summary or conclusion
        self.show_summary()

        self.wait(2)

    def show_title(self):
        """Creates and animates the scene title."""
        title = Text("Projectile Motion", font_size=48)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.wait(1)

    def setup_and_launch(self):
        """Sets up the ground, projectile, and animates the basic trajectory."""
        # Create the ground
        ground = Line(LEFT * 7, RIGHT * 7, color=GREEN).shift(DOWN * 3)
        
        # Create the projectile
        ball = Circle(radius=0.15, color=YELLOW, fill_opacity=1)
        ball.move_to(ground.get_start() + UP * 0.15)

        # Introduction text
        intro_text = Text(
            "An object moving through the air under gravity.",
            font_size=24
        ).next_to(self.mobjects[0], DOWN, buff=0.8)

        self.play(Create(ground), FadeIn(intro_text))
        self.play(Create(ball))
        self.wait(1)

        # Define the parabolic path
        # x(t) = v0*cos(theta)*t
        # y(t) = v0*sin(theta)*t - 0.5*g*t^2
        path = self.get_parabolic_path(ball.get_center())
        
        path_label = MathTex(r"\text{Path is a Parabola}", font_size=36)
        path_label.move_to(ORIGIN + UP * 1.5)

        self.play(FadeOut(intro_text))
        self.play(
            MoveAlongPath(ball, path),
            Create(path),
            run_time=3
        )
        self.play(Write(path_label))
        self.wait(2)

        # Store objects for later use
        self.ground = ground
        self.ball_start_pos = ball.get_center()
        
        self.play(FadeOut(path), FadeOut(path_label), FadeOut(ball))

    def decompose_motion(self):
        """Visually separates motion into horizontal and vertical components."""
        # Create a title for this section
        section_title = Text("Motion has two independent parts:", font_size=32).to_edge(UP, buff=1.5)
        self.play(Write(section_title))
        self.wait(1)

        # --- Horizontal Motion ---
        h_title = Text("1. Horizontal Motion", font_size=28).move_to(LEFT * 3.5 + UP * 2)
        h_desc = Text("Constant Speed", font_size=24, color=BLUE).next_to(h_title, DOWN, buff=0.5)
        h_ball = Circle(radius=0.15, color=BLUE, fill_opacity=1).move_to(self.ground.get_start() + UP * 0.15)
        
        self.play(FadeIn(h_title, h_desc, h_ball))
        self.play(h_ball.animate.move_to(self.ground.get_end() + UP * 0.15), run_time=3, rate_func=linear)
        self.wait(1)

        # --- Vertical Motion ---
        v_title = Text("2. Vertical Motion", font_size=28).move_to(RIGHT * 3.5 + UP * 2)
        v_desc = Text("Constant Acceleration (Gravity)", font_size=24, color=RED).next_to(v_title, DOWN, buff=0.5)
        v_ball = Circle(radius=0.15, color=RED, fill_opacity=1).move_to(self.ground.get_center() + UP * 0.15)
        
        self.play(FadeIn(v_title, v_desc, v_ball))
        self.play(
            v_ball.animate.shift(UP * 3), run_time=1.5, rate_func=rate_functions.ease_out_quad
        )
        self.play(
            v_ball.animate.shift(DOWN * 3), run_time=1.5, rate_func=rate_functions.ease_in_quad
        )
        self.wait(2)

        # Group and fade out
        decomposition_group = VGroup(section_title, h_title, h_desc, h_ball, v_title, v_desc, v_ball)
        self.play(FadeOut(decomposition_group))

    def show_velocity_vectors(self):
        """Animates the projectile with its velocity component vectors."""
        # Re-create the ball
        ball = Circle(radius=0.15, color=YELLOW, fill_opacity=1).move_to(self.ball_start_pos)
        
        # Create velocity vectors
        vx_vec = Arrow(start=ball.get_center(), end=ball.get_center() + RIGHT * 1.5, buff=0, color=BLUE, stroke_width=5)
        vy_vec = Arrow(start=ball.get_center(), end=ball.get_center() + UP * 2, buff=0, color=RED, stroke_width=5)
        
        vx_label = MathTex("v_x", color=BLUE, font_size=30).next_to(vx_vec, RIGHT, buff=0.1)
        vy_label = MathTex("v_y", color=RED, font_size=30).next_to(vy_vec, UP, buff=0.1)

        # Group the ball and its vectors
        projectile_group = VGroup(ball, vx_vec, vy_vec, vx_label, vy_label)

        # Add updaters to keep vectors attached to the ball
        vx_vec.add_updater(lambda m: m.move_to(ball.get_center() + RIGHT * 0.75))
        vy_vec.add_updater(lambda m: m.put_start_and_end_on(ball.get_center(), ball.get_center() + vy_vec.get_vector()))
        vx_label.add_updater(lambda m: m.next_to(vx_vec, RIGHT, buff=0.1))
        vy_label.add_updater(lambda m: m.next_to(vy_vec, UP, buff=0.1))

        # Updater for the vertical velocity vector's length and direction
        def vy_updater(m, dt):
            # This is a simplified simulation of gravity's effect
            new_vy_vector = m.get_vector() - DOWN * 2.67 * dt
            m.put_start_and_end_on(m.get_start(), m.get_start() + new_vy_vector)
        
        vy_vec.add_updater(vy_updater)

        path = self.get_parabolic_path(ball.get_center())
        
        self.play(FadeIn(projectile_group))
        self.play(MoveAlongPath(ball, path), run_time=3)
        self.wait(2)

        # Clear updaters and fade out
        projectile_group.clear_updaters()
        self.play(FadeOut(projectile_group), FadeOut(self.ground))

    def show_summary(self):
        """Displays a summary of the key concepts."""
        summary_title = Text("Key Takeaways", font_size=36).to_edge(UP)
        
        point1 = Text("• The path of a projectile is a parabola.", font_size=28)
        point2 = Text("• Horizontal motion has constant velocity.", font_size=28, color=BLUE)
        point3 = Text("• Vertical motion has constant acceleration (gravity).", font_size=28, color=RED)

        summary_points = VGroup(point1, point2, point3).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        summary_points.next_to(summary_title, DOWN, buff=1.0)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_points, shift=UP))
        self.wait(3)

    def get_parabolic_path(self, start_point):
        """Helper function to generate a parabolic Arc."""
        return ArcBetweenPoints(
            start=start_point,
            end=start_point + RIGHT * 12,
            angle=-PI / 2,
            stroke_color=ORANGE
        )