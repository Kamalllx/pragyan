from manim import *

class ProjectileMotionKannada(Scene):
    def construct(self):
        # Set a background color
        self.camera.background_color = "#0d1117"

        # 1. Title Introduction
        title = Text(
            "ಪ್ರಕ್ಷೇಪಕ ಚಲನೆ (Projectile Motion)",
            font="Noto Sans Kannada",
            font_size=40,
            color=BLUE
        )
        title.to_edge(UP, buff=0.8)
        self.play(Write(title))
        self.wait(1)

        # Setup the ground and axes
        ground = Line(LEFT * 7, RIGHT * 7, color=WHITE).shift(DOWN * 3)
        
        # 2. Main Visual Demonstration
        # Define the parabolic path
        path = ParametricFunction(
            lambda t: np.array([t, 2.5 * t - 1.2 * t**2, 0]),
            t_range=np.array([0, 4.16]),
            color=YELLOW
        ).shift(LEFT * 6 + DOWN * 3)

        path_label = Text(
            "ಚಲನೆಯ ಪಥ (Path of Motion)",
            font="Noto Sans Kannada",
            font_size=24,
            color=YELLOW
        ).next_to(path, UP, buff=0.2).shift(RIGHT*2)

        # Create the projectile
        ball = Dot(color=ORANGE, radius=0.15)
        ball.move_to(path.get_start())

        self.play(Create(ground))
        self.play(FadeIn(ball), Create(path))
        self.play(Write(path_label))
        self.wait(1)

        # Animate the motion
        self.play(MoveAlongPath(ball, path), rate_func=linear, run_time=4)
        self.wait(2)

        # Fade out path elements for clarity
        self.play(FadeOut(path_label), FadeOut(ball), FadeOut(path))

        # 3. Key Concepts with Clear Explanations
        # Initial position and projectile
        start_point = ground.get_left() + LEFT * 0.5
        ball.move_to(start_point)

        # Initial Velocity Vector
        initial_velocity_vector = Arrow(
            start_point, start_point + UP * 2 + RIGHT * 2,
            buff=0.1, color=GREEN, max_tip_length_to_length_ratio=0.15
        )
        velocity_label = MathTex("u", "\\text{ (ಆರಂಭಿಕ ವೇಗ)}", font_size=32, color=GREEN)
        velocity_label.next_to(initial_velocity_vector.get_end(), UR, buff=0.2)

        # Angle of Projection
        angle_arc = Angle(
            Line(start_point, start_point + RIGHT),
            Line(start_point, initial_velocity_vector.get_end()),
            radius=0.8, color=RED
        )
        angle_label = MathTex("\\theta", font_size=32, color=RED).next_to(angle_arc, RIGHT, buff=0.2)
        angle_text = Text("ಪ್ರಕ್ಷೇಪಣ ಕೋನ", font="Noto Sans Kannada", font_size=24, color=RED).next_to(angle_label, DOWN, buff=0.2)

        # Gravity
        gravity_vector = Arrow(ORIGIN, DOWN * 1.5, color=WHITE)
        gravity_label = MathTex("g", "\\text{ (ಗುರುತ್ವಾಕರ್ಷಣೆ)}", font_size=32, color=WHITE)
        gravity_group = VGroup(gravity_vector, gravity_label).arrange(DOWN, buff=0.2)
        gravity_group.to_edge(RIGHT, buff=1.0).shift(UP*1.5)

        self.play(FadeIn(ball))
        self.play(Create(initial_velocity_vector), Write(velocity_label))
        self.wait(1)
        self.play(Create(angle_arc), Write(angle_label), Write(angle_text))
        self.wait(1)
        self.play(FadeIn(gravity_group))
        self.wait(2)

        # Clear screen for next section
        self.play(FadeOut(ball, initial_velocity_vector, velocity_label, angle_arc, angle_label, angle_text, gravity_group))

        # 4. Decomposing Motion
        components_title = Text("ವೇಗದ ಘಟಕಗಳು (Velocity Components)", font="Noto Sans Kannada", font_size=32).to_edge(UP, buff=0.8)
        self.play(Transform(title, components_title))

        # Re-draw path and ball
        path.move_to(ORIGIN).shift(DOWN*1.5)
        ball.move_to(path.get_start())
        self.play(Create(path), FadeIn(ball))

        # Velocity vectors (horizontal and vertical)
        vx_vector = Arrow(ball.get_center(), ball.get_center() + RIGHT * 1.5, buff=0.1, color=CYAN)
        vy_vector = Arrow(ball.get_center(), ball.get_center() + UP * 1.5, buff=0.1, color=PINK)
        
        vx_label = MathTex("v_x", color=CYAN, font_size=28).next_to(vx_vector, DOWN)
        vy_label = MathTex("v_y", color=PINK, font_size=28).next_to(vy_vector, LEFT)
        
        vectors = VGroup(vx_vector, vy_vector, vx_label, vy_label)

        # Explanation text
        vx_explanation = Text("ಕ್ಷಿತಿಜೀಯ ವೇಗ (v_x) = ಸ್ಥಿರ", font="Noto Sans Kannada", font_size=24, color=CYAN)
        vy_explanation = Text("ಲಂಬ ವೇಗ (v_y) = ಬದಲಾಗುತ್ತದೆ", font="Noto Sans Kannada", font_size=24, color=PINK)
        explanation_group = VGroup(vx_explanation, vy_explanation).arrange(DOWN, buff=0.5).to_edge(RIGHT, buff=1.0)

        self.play(Create(vectors), Write(explanation_group))
        self.wait(1)

        # Animate the components changing
        def vector_updater(mob, dt):
            # Get the derivative (velocity vector) from the path's function
            t = self.time - start_time
            if t > 4.16: t = 4.16 # Clamp t to the end of the path
            
            dx_dt = 1.0 # from lambda t: np.array([t, ...])
            dy_dt = 2.5 - 2.4 * t # from lambda t: np.array([..., 2.5*t - 1.2*t**2, ...])
            
            ball_pos = ball.get_center()
            
            # Update horizontal vector (constant length)
            new_vx = Arrow(ball_pos, ball_pos + RIGHT * dx_vector_length, buff=0.1, color=CYAN)
            vx_vector.become(new_vx)
            vx_label.next_to(vx_vector, DOWN)

            # Update vertical vector (changing length)
            new_vy = Arrow(ball_pos, ball_pos + UP * dy_dt * 0.6, buff=0.1, color=PINK)
            vy_vector.become(new_vy)
            vy_label.next_to(vy_vector, LEFT)

        dx_vector_length = 1.5
        start_time = self.time
        ball.add_updater(vector_updater)
        
        self.play(MoveAlongPath(ball, path), run_time=4, rate_func=linear)
        ball.clear_updaters()
        self.wait(2)

        # 5. Maximum Height and Range
        self.play(FadeOut(vectors), FadeOut(explanation_group))

        # Maximum Height
        max_height_point = path.get_top()
        max_height_line = DashedLine(
            start_point.get_center() * np.array([1,0,0]) + max_height_point * np.array([0,1,0]),
            max_height_point,
            color=ORANGE
        )
        max_height_label = Text("H - ಗರಿಷ್ಠ ಎತ್ತರ", font="Noto Sans Kannada", font_size=24, color=ORANGE)
        max_height_label.next_to(max_height_line, LEFT, buff=0.2)

        # Range
        range_line = DashedLine(path.get_start(), path.get_end(), color=TEAL)
        range_label = Text("R - ವ್ಯಾಪ್ತಿ", font="Noto Sans Kannada", font_size=24, color=TEAL)
        range_label.next_to(range_line, DOWN, buff=0.2)

        self.play(Create(max_height_line), Write(max_height_label))
        self.wait(1)
        self.play(Create(range_line), Write(range_label))
        self.wait(2)

        # Final Summary
        self.play(FadeOut(*self.mobjects))
        
        summary_title = Text("ಸಾರಾಂಶ (Summary)", font="Noto Sans Kannada", font_size=36, color=BLUE)
        summary_title.to_edge(UP)

        summary_points = VGroup(
            Text("1. ಪ್ರಕ್ಷೇಪಕ ಚಲನೆಯು ಗುರುತ್ವಾಕರ್ಷಣೆಯ ಅಡಿಯಲ್ಲಿನ ಚಲನೆಯಾಗಿದೆ.", font="Noto Sans Kannada", font_size=24),
            Text("2. ಚಲನೆಯ ಪಥವು ಪ್ಯಾರಾಬೋಲಾ (parabola) ಆಕಾರದಲ್ಲಿರುತ್ತದೆ.", font="Noto Sans Kannada", font_size=24),
            Text("3. ಕ್ಷಿತಿಜೀಯ ವೇಗವು ಸ್ಥಿರವಾಗಿರುತ್ತದೆ.", font="Noto Sans Kannada", font_size=24),
            Text("4. ಲಂಬ ವೇಗವು ಗುರುತ್ವಾಕರ್ಷಣೆಯಿಂದಾಗಿ ನಿರಂತರವಾಗಿ ಬದಲಾಗುತ್ತದೆ.", font="Noto Sans Kannada", font_size=24)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        summary_points.next_to(summary_title, DOWN, buff=0.8)

        self.play(Write(summary_title))
        self.play(Write(summary_points))

        self.wait(2)