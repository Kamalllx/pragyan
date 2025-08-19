# Manim v0.19.0
from manim import *

class RotationalMotionScene(Scene):
    """
    An engaging and educational animation for beginners about the
    fundamentals of rotational motion in physics.
    """
    def construct(self):
        # Set a consistent background color
        self.camera.background_color = "#0d1117"

        # --- 1. Title Introduction ---
        title = Text("Understanding Rotational Motion", font_size=48)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        self.wait(0.5)

        # --- 2. Linear vs. Rotational Motion ---
        # Create objects for demonstration
        square = Square(side_length=1.5, color=BLUE, fill_opacity=0.7)
        disk = Circle(radius=0.75, color=TEAL, fill_opacity=0.7)
        
        # Create labels
        linear_label = Text("Linear Motion", font_size=24)
        rotational_label = Text("Rotational Motion", font_size=24)

        # Group and position linear motion elements
        linear_group = VGroup(square, linear_label).arrange(DOWN, buff=0.5)
        linear_group.move_to(LEFT * 3.5)

        # Group and position rotational motion elements
        rotational_group = VGroup(disk, rotational_label).arrange(DOWN, buff=0.5)
        rotational_group.move_to(RIGHT * 3.5)

        self.play(FadeIn(linear_group), FadeIn(rotational_group))
        self.wait(1)

        # Animate linear motion
        self.play(
            square.animate.shift(UP * 2),
            run_time=1.5
        )
        self.play(
            square.animate.shift(DOWN * 2),
            run_time=1.5
        )
        self.wait(0.5)

        # Animate rotational motion
        # Add a radius line to make rotation visible
        radius_line = Line(disk.get_center(), disk.get_point_at_angle(0), color=YELLOW)
        self.play(Create(radius_line))
        self.play(
            Rotate(VGroup(disk, radius_line), angle=2 * PI, about_point=disk.get_center(), run_time=3, rate_func=linear)
        )
        self.wait(1)

        # Clear the screen for the next section
        self.play(FadeOut(linear_group), FadeOut(rotational_group), FadeOut(radius_line))
        self.wait(1)

        # --- 3. Key Concepts: Axis and Angular Velocity ---
        concept_title = Text("Key Concepts", font_size=40).to_edge(UP)
        self.play(Write(concept_title))

        # Axis of Rotation
        axis_disk = Circle(radius=1.5, color=BLUE_C)
        axis_dot = Dot(axis_disk.get_center(), color=RED, radius=0.1)
        axis_label = Text("Axis of Rotation", font_size=24).next_to(axis_dot, DOWN, buff=0.5)
        axis_radius = Line(axis_disk.get_center(), axis_disk.get_point_at_angle(PI/4), color=WHITE)
        
        axis_group = VGroup(axis_disk, axis_dot, axis_label, axis_radius).move_to(LEFT * 3.5)

        self.play(FadeIn(axis_group, shift=DOWN))
        self.play(Rotate(VGroup(axis_disk, axis_radius), angle=PI, about_point=axis_dot.get_center(), run_time=2))
        self.wait(1)

        # Angular Velocity (ω)
        omega_symbol = MathTex(r"\omega", font_size=96, color=YELLOW).move_to(RIGHT * 3.5)
        omega_label = Text("Angular Velocity (how fast it spins)", font_size=24).next_to(omega_symbol, DOWN, buff=0.5)
        omega_group = VGroup(omega_symbol, omega_label)

        self.play(Write(omega_group))
        self.play(Indicate(omega_symbol))
        self.wait(2)

        # Clear the screen
        self.play(FadeOut(concept_title), FadeOut(axis_group), FadeOut(omega_group))
        self.wait(1)

        # --- 4. Torque: The Cause of Rotation ---
        torque_title = Text("What Causes Rotation? Torque!", font_size=40).to_edge(UP)
        self.play(Write(torque_title))

        # Create a wrench and bolt system
        bolt = Circle(radius=0.4, color=GRAY, fill_opacity=1).move_to(ORIGIN)
        pivot_dot = Dot(bolt.get_center(), color=BLACK)
        wrench = Rectangle(height=0.6, width=4, color=BLUE_D, fill_opacity=0.8).next_to(bolt, RIGHT, buff=0)
        
        wrench_system = VGroup(bolt, wrench, pivot_dot).move_to(LEFT * 2)
        
        self.play(Create(wrench_system))
        self.wait(1)

        # Apply a force
        force_point = wrench.get_right() + LEFT*0.2
        force_arrow = Arrow(force_point + DOWN*1.5, force_point, buff=0.1, color=RED, max_tip_length_to_length_ratio=0.2)
        force_label = MathTex("F", font_size=48, color=RED).next_to(force_arrow, DOWN, buff=0.2)
        
        self.play(GrowArrow(force_arrow), Write(force_label))
        self.wait(0.5)

        # Animate rotation due to torque
        self.play(
            Rotate(wrench_system, angle=-PI / 6, about_point=bolt.get_center()),
            run_time=1.5
        )
        self.wait(1)

        # Display the torque formula
        torque_formula = MathTex(r"\tau = r \times F", font_size=48).to_edge(RIGHT, buff=1.5)
        torque_explanation = Text("Torque = Lever Arm × Force", font_size=24).next_to(torque_formula, DOWN, buff=0.5)
        formula_group = VGroup(torque_formula, torque_explanation)

        self.play(Write(formula_group))
        self.wait(2)

        # Clear the screen
        self.play(FadeOut(torque_title), FadeOut(wrench_system), FadeOut(force_arrow), FadeOut(force_label), FadeOut(formula_group))
        self.wait(1)

        # --- 5. Summary ---
        summary_title = Text("In Summary:", font_size=40).to_edge(UP)
        
        point1 = Text("• Rotation is spinning around a central axis.", font_size=28)
        point2 = Text("• Angular Velocity (ω) measures the speed of rotation.", font_size=28)
        point3 = Text("• Torque (τ) is a 'twist' or 'turn' that causes rotation.", font_size=28)

        summary_group = VGroup(point1, point2, point3).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        summary_group.move_to(ORIGIN).to_edge(LEFT, buff=1.0)

        self.play(Write(summary_title))
        self.wait(0.5)
        self.play(FadeIn(point1, shift=UP))
        self.wait(1)
        self.play(FadeIn(point2, shift=UP))
        self.wait(1)
        self.play(FadeIn(point3, shift=UP))

        # Final wait to let the viewer read the summary
        self.wait(3)