```python
from manim import *

class ProjectileMotion(Scene):
    """
    An animation explaining projectile motion with gravity.
    This scene visualizes the trajectory of a projectile, breaking down its
    velocity into horizontal and vertical components and showing the effect of gravity.
    """
    def construct(self):
        # -----------------------------------------------------------------
        # 1. Title and Scene Setup
        # -----------------------------------------------------------------
        
        # Display the title of the animation
        title = Text("Projectile Motion With Gravity", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        # Create a 2D coordinate system (axes)
        axes = Axes(
            x_range=[0, 10, 1],  # x-axis from 0 to 10 with step 1
            y_range=[0, 6, 1],   # y-axis from 0 to 6 with step 1
            x_length=9,          # Visual length of x-axis
            y_length=5.5,        # Visual length of y-axis
            axis_config={"color": BLUE},
            x_axis_config={"numbers_to_include": np.arange(2, 10, 2)},
            y_axis_config={"numbers_to_include": np.arange(2, 6, 2)},
        ).to_edge(DOWN, buff=0.5).add_coordinates()

        # Add labels to the axes
        x_label = axes.get_x_axis_label("Distance (m)")
        y_label = axes.get_y_axis_label("Height (m)")

        self.play(Create(axes), Write(x_label), Write(y_label))
        self.wait(1)

        # -----------------------------------------------------------------
        # 2. Introduce Initial Velocity and its Components
        # -----------------------------------------------------------------

        # Define physical constants and initial conditions
        # We scale 'g' to make the animation visually appealing
        g = 9.8 / 4 
        v0_val = 5.0
        angle = 60 * DEGREES
        
        # Calculate initial velocity components
        vx0 = v0_val * np.cos(angle)
        vy0 = v0_val * np.sin(angle)

        # Create the initial velocity vector (v0)
        v0_vec = Arrow(axes.c2p(0, 0), axes.c2p(vx0, vy0), buff=0, color=WHITE)
        v0_label = MathTex("v_0").next_to(v0_vec.get_end(), UR, buff=0.1)

        # Create the horizontal component vector (vx)
        vx_vec = Arrow(axes.c2p(0, 0), axes.c2p(vx0, 0), buff=0, color=GREEN)
        vx_label = MathTex("v_x", color=GREEN).next_to(vx_vec.get_end(), DOWN)

        # Create the vertical component vector (vy)
        vy_vec = Arrow(axes.c2p(vx0, 0), axes.c2p(vx0, vy0), buff=0, color=RED)
        vy_label = MathTex("v_y", color=RED).next_to(vy_vec.get_end(), RIGHT)

        # Animate the introduction of velocity and its components
        self.play(GrowArrow(v0_vec), Write(v0_label), run_time=1.5)
        self.wait(0.5)
        self.play(
            TransformFromCopy(v0_vec, vx_vec), Write(vx_label),
            TransformFromCopy(v0_vec, vy_vec), Write(vy_label)
        )
        self.wait(2)
        
        # Group components and fade them out
        components_group = VGroup(v0_vec, v0_label, vx_