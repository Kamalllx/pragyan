from manim import *
import numpy as np

class ProjectileMotionScene(Scene):
    """
    An animation explaining the principles of projectile motion under constant gravity.
    This scene visualizes the decomposition of velocity vectors, the constant horizontal
    velocity, the changing vertical velocity due to acceleration, and the resulting
    parabolic trajectory.
    """
    def construct(self):
        # -----------------------------------------------------------------
        # 1. Title and Scene Setup
        # -----------------------------------------------------------------
        
        # Display the title of the animation
        title = Text("Projectile Motion with Gravity", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Create a coordinate system for reference
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 6, 1],
            x_length=10,
            y_length=6,
            axis_config={"color": BLUE},
        ).add_coordinates()
        axes_labels = axes.get_axis_labels(x_label="x (m)", y_label="y (m)")
        
        # Position the axes on the screen
        scene_setup = VGroup(axes, axes_labels)
        self.play(Create(scene_setup))
        self.wait(1)

        # -----------------------------------------------------------------
        # 2. Initial Velocity and Vector Components
        # -----------------------------------------------------------------

        # Define initial parameters for the projectile
        initial_pos = axes.c2p(0, 0)
        v0 = 8.0  # Initial speed
        theta = 60 * DEGREES  # Launch angle

        # Calculate initial velocity components
        v0_x = v0 * np.cos(theta)
        v0_y = v0 * np.sin(theta)

        # Create the initial velocity vector and its components
        v_vec = Arrow(initial_pos