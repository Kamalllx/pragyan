```python
from manim import *

class ProjectileMotionScene(Scene):
    """
    An animation explaining the basics of projectile motion under gravity.
    This scene is designed for beginners, using clear visuals and simple explanations.
    """
    def construct(self):
        # -----------------------------------------------------------------
        # 1. Title and Introduction
        # -----------------------------------------------------------------
        
        # Display the title of the animation
        title = Text("Projectile Motion with Gravity", font_size=48)
        self.play(Write(title))
        self.wait(1)
        
        # Move the title to the top of the screen to make space for the main content
        self.play(title.animate.to_edge(UP).scale(0.8))

        # -----------------------------------------------------------------
        # 2. Scene Setup (Axes, Ground)
        # -----------------------------------------------------------------

        # Create a 2D coordinate system (axes) to represent space
        # x_range: [start, end, step], y_range: [start, end, step]
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 6, 1],
            x_length=9,
            y_length=5.5,
            axis_config={"color": GRAY},
        ).to_edge(DL, buff=0.5)
        
        # Add labels for the axes with units
        axis_labels = axes.get_axis_labels(x_label="x (m)", y_label="y (m)")
        
        # Create a line to represent the ground
        ground = Line(axes.c2p(0, 0), axes.c2p(10, 0), color=WHITE, stroke_width=2)

        # Animate the creation of the axes and ground
        self.play(Create(axes), Create(axis_labels), Create(ground))
        self.wait(0.5)

        # -----------------------------------------------------------------
        # 3. Initial Velocity and its Components
        # -----------------------------------------------------------------

        # Define physical constants for the simulation
        v0_val = 5.5  # Initial speed
        theta = 60 * DEGREES  # Launch angle
        g = 9.8  # Acceleration due to gravity

        # Create the initial velocity vector (v₀)
        v0_vec = Arrow(
            axes.c2p(0, 0),
            axes.c2p(v0_val * np.cos(theta), v0_val * np.sin(theta)),
            buff=0,
            color=GREEN,
            stroke_width=6
        )
        v0_label = MathTex("v_0", color=GREEN).next_to(v0_vec.get_end(), UR, buff=0.1)

        # Animate the appearance of the initial velocity vector
        self.play(GrowArrow(v0_vec), Write(v0_label))
        self.wait(1)

        # Decompose v₀ into its horizontal (v₀x) and vertical (v₀y) components
        v0x_vec = DashedLine(axes.c2p(0, 0), axes.c2p(v0_val * np.cos(theta), 0), color=YELLOW)
        v0y_vec = DashedLine(v0x_vec.get_end(), v0_vec.get_end(), color=YELLOW)
        
        v0x_label = MathTex("v_{0x}", color=YELLOW).next_to(v0x_vec, DOWN)
        v0y_label = MathTex("v_{0y}", color=YELLOW).next_to(v0y_vec, RIGHT)

        # Show the decomposition animation and display the component labels
        self.play(
            TransformFromCopy(v0_vec, VGroup(v0x_vec, v0y_vec)),
            Write(v0x_label),
            Write(v0y_label)
        )
        self.wait(2)

        # Clean up the component vectors and labels to prepare for the next step
        self.play(
            FadeOut(v0x_vec), FadeOut(v0y_vec