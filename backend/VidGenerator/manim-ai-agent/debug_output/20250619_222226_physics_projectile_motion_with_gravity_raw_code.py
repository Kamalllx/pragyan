```python
from manim import *

class ProjectileMotionScene(Scene):
    """
    An animation explaining the physics of projectile motion under gravity.
    This scene breaks down the velocity components, shows the effect of gravity,
    and traces the parabolic trajectory of a projectile.
    """
    def construct(self):
        # --------------------------------------------------------------------
        # 1. Title and Introduction
        # --------------------------------------------------------------------
        title = Text("Projectile Motion with Gravity", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # --------------------------------------------------------------------
        # 2. Scene Setup (Axes and Ground)
        # --------------------------------------------------------------------
        # Create axes for our 2D world
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 6, 1],
            x_length=10,
            y_length=6,
            axis_config={"color": BLUE},
        ).add_coordinates()
        
        # Add labels to the axes
        x_label = axes.get_x_axis_label("x (m)")
        y_label = axes.get_y_axis_label("y (m)", edge=LEFT)
        axes_labels = VGroup(x_label, y_label)

        self.play(Create(axes), Write(axes_labels))
        self.play(title.animate.scale(0.7).to_corner(UP + RIGHT))
        self.wait(0.5)

        # --------------------------------------------------------------------
        # 3. Initial Velocity Vector and Components
        # --------------------------------------------------------------------
        # Define initial parameters
        v0 = 8.0  # Initial speed
        angle = 60 * DEGREES  # Launch angle
        g = 9.8  # Acceleration due to gravity

        # Create the initial velocity vector
        v0_vector = Vector([v0 * np.cos(angle), v0 * np.sin(angle)], color=YELLOW).shift(axes.c2p(0, 0))
        v0_label = MathTex("{\\vec{v}}_0", color=YELLOW).next_to(v0_vector.get_end(), UR, buff=0.1)

        self.play(GrowArrow(v0_vector), Write(v0_label))
        self.wait(1)

        # Decompose the vector into x and y components
        vx_vector = Vector([v0 * np.cos(angle), 0], color=GREEN).shift(axes.c2p(0, 0))
        vy_vector = Vector([0, v0 * np.sin(angle)], color=RED).shift(axes.c2p(v0 * np.cos(angle), 0))
        
        # Dashed lines to show decomposition
        dashed_lines = DashedLine(
            start=v0_vector.get_end(),
            end=vx_vector.get_end(),
            color=WHITE,
            stroke_width=2
        )

        self.play(Transform(v0_vector.copy(), vx_vector), Create(dashed_lines))
        self.play(Transform(v0_vector.copy(), vy_vector))
        self.wait(0.5)

        # Show formulas for the components
        vx_formula = MathTex("v_{0x} = v_0 \\cos(\\theta)", color=GREEN).to_corner(DR).shift(LEFT*2 + UP)
        vy_formula = MathTex("v_{0y} = v_0 \\sin(\\theta)", color=RED).next_to(vx_formula, UP)
        
        self.play(Write(vx_formula), Write(vy_formula))
        self.wait(2)
        
        # Group and fade out component vectors and formulas
        components_group = VGroup(vx_vector, vy_vector, dashed_lines, vx_formula, vy_formula)
        self.play(FadeOut(components_group))

        # --------------------------------------------------------------------
        # 4. Introducing Gravity
        # --------------------------------------------------------------------
        # Show the constant downward acceleration due to gravity
        gravity_text = Text("Force of Gravity:", font_size=28).to_corner(DR).shift(LEFT*2 + UP*1.5)
        gravity_vector = Vector([0, -1.5], color=ORANGE).next_to(gravity_text, DOWN, buff=0.2)
        gravity_label = MathTex("{\\vec{a}} = [0, -g]", color=ORANGE).next_to(gravity_vector, RIGHT)
        gravity_group = VGroup(gravity_text, gravity_vector, gravity_label)

        self.play(Write(gravity_group))
        self.wait(2)
        self.play(FadeOut(gravity_group))

        # --------------------------------------------------------------------
        # 5. The Trajectory Animation
        # --------------------------------------------------------------------
        # Define the parametric equations of motion
        x_t = lambda t: v0 * np.cos(angle) * t
        y_t = lambda t: v0 * np.sin(angle) * t - 0.5 * g * t**2
        
        # Calculate total time of flight to set the t_max for the curve
        time_of_flight = (2 * v0 * np.sin(angle)) / g

        # Create the parabolic trajectory path
        trajectory = axes.plot_parametric_curve(
            lambda t: [x_t(t), y_t(t)],
            t_range=[0, time_of_flight],
            color=CYAN,
            stroke_width=3
        )
        
        # Create the projectile (a dot)
        projectile = Dot(point=axes.c2p(0, 0), color=YELLOW, radius=0.1)

        # Create a velocity vector that will update with the projectile
        velocity_vector = Vector([0,0], color=YELLOW) # Initialized at origin
        velocity_vector.add_updater(
            lambda mob: mob.put_start_and_end_on(
                projectile.get_center(),
                projectile.get_center() + np.array([
                    v0 * np.cos(angle),
                    v0 * np.sin(angle) - g * projectile.time_tracker.get_value(),
                    0
                ]) * 0.3 # Scale vector for visualization
            )
        )
        
        # Add a time tracker to the projectile to use in the updater
        projectile.time_tracker = ValueTracker(0)

        self.play(FadeIn(projectile, velocity_vector))
        self.wait(0.5)
        
        # Animate the projectile moving along the path
        self.play(
            MoveAlongPath(projectile, trajectory),
            projectile.time_tracker.animate.set_value(time_of_flight),
            Create(trajectory),
            run_time=4,
            rate_func=linear
        )
        
        # Remove the updater so the vector stops moving
        velocity_vector.clear_updaters()
        self.wait(1)

        # --------------------------------------------------------------------
        # 6. Summary and Conclusion
        # --------------------------------------------------------------------
        # Fade out everything except the title and trajectory
        final_elements = VGroup(projectile, velocity_vector, v0_vector, v0_label, axes, axes_labels)
        self.play(FadeOut(final_elements))

        # Create a summary box
        summary_box = SurroundingRectangle(trajectory, buff=0.5, color=WHITE)
        summary_text = VGroup(
            Text("Key Concepts:", font_size=32, weight=BOLD),
            Text("• Horizontal motion: Constant velocity", font_size=28),
            Text("• Vertical motion: Constant acceleration (-g)", font_size=28),
            Text("• Path: A parabola", font_size=28, color=CYAN)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(summary_box, DOWN, buff=0.3)

        self.play(Create(summary_box))
        self.play(Write(summary_text))
        self.wait(3)

        # Final fade out
        self.play(
            FadeOut(title),
            FadeOut(trajectory),
            FadeOut(summary_box),
            FadeOut(summary_text)
        )
        self.wait(1)
```