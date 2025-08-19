```python
from manim import *

class SineIntroduction(Scene):
    """
    An animation introducing the concept of the sine function using the unit circle.
    This scene is designed for beginners, with clear labels, slow animations,
    and a step-by-step explanation.
    """
    def construct(self):
        # Set a consistent color scheme
        self.camera.background_color = "#1E1E1E" # Dark grey background
        angle_color = GREEN
        opposite_color = RED
        hypotenuse_color = YELLOW
        text_color = WHITE

        # --- SCENE 1: TITLE ---
        # Display the main title of the animation
        title = Text("Introduction to Sine", font_size=48, color=text_color)
        self.play(Write(title))
        self.wait(1)
        # Move the title to the top to make space for the main content
        self.play(title.animate.to_edge(UP))

        # --- SCENE 2: SETUP AXES AND UNIT CIRCLE ---
        # Create a coordinate system (axes)
        axes = Axes(
            x_range=[-1.5, 1.5, 1],
            y_range=[-1.5, 1.5, 1],
            axis_config={"color": BLUE},
            x_length=6,
            y_length=6
        ).add_coordinates()

        # Create a unit circle (radius = 1) on the axes
        # The radius is calculated based on the axes' coordinate system for accuracy
        unit_circle = Circle(
            radius=axes.c2p(1, 0)[0] - axes.c2p(0, 0)[0], 
            color=WHITE
        )
        
        # Animate the creation of the axes and the circle
        self.play(Create(axes), Create(unit_circle))
        self.wait(1)

        # --- SCENE 3: CREATE THE DYNAMIC TRIANGLE ---
        # Use a ValueTracker to easily animate the angle theta
        theta_tracker = ValueTracker(PI / 4) # Start at 45 degrees (PI/4 radians)

        # This point P will always be on the circle, determined by the angle theta
        point_p = always_redraw(
            lambda: axes.c2p(np.cos(theta_tracker.get_value()), np.sin(theta_tracker.get_value()))
        )

        # The radius line (hypotenuse of our triangle)
        radius_line = always_redraw(
            lambda: Line(axes.c2p(0, 0), point_p.get_center(), color=hypotenuse_color)
        )
        # Label for the hypotenuse, which is always 1 on a unit circle
        hypotenuse_label = MathTex("1", color=hypotenuse_color).add_updater(
            lambda m: m.move_to(radius_line.get_center() + UP * 0.3 + LEFT * 0.3)
        )

        # The vertical line (opposite side of the triangle)
        opposite_line = always_redraw(
            lambda: axes.get_vertical_line(point_p.get_center(), color=opposite_color)
        )
        # Label for the opposite side
        opposite_label = MathTex("\\sin(\\theta)", color=opposite_color).add_updater(
            lambda m: m.next_to(opposite_line, RIGHT, buff=0.1)
        )

        # The arc representing the angle theta
        angle_arc = always_redraw(
            lambda: Arc(radius=0.4, start_angle=0, angle=theta_tracker.get_value(), color=angle_color)
        )
        # Label for the angle theta
        theta_label = MathTex("\\theta", color=angle_color).add_updater(
            lambda m: m.next_to(angle_arc, RIGHT, buff=0.1)
        )

        # Group all triangle components and labels for easier animation
        triangle_group = VGroup(radius_line, opposite_line, angle_arc)
        labels_group = VGroup(hypotenuse_label, opposite_label, theta_label)

        # Animate the creation of the triangle and its labels
        self.play(Create(triangle_group), Write(labels_group))
        self.wait(2)

        # --- SCENE 4: DEFINE SINE ---
        # Display the mathematical definition of sine (SOH CAH TOA)
        sine_formula = MathTex(
            "\\sin(\\theta) = \\frac{\\text{Opposite}}{\\text{Hypotenuse}}",
            font_size=36
        ).to_edge(RIGHT, buff=1).shift(UP*1.5)
        self.play(Write(sine_formula))
        self.wait(1)

        # Show how the formula simplifies for a unit circle (Hypotenuse = 1)
        sine_formula_simplified = MathTex(
            "\\sin(\\theta) = \\frac{\\sin(\\theta)}{1} = \\sin(\\theta)",
            font_size=36
        ).next_to(sine_formula, DOWN, buff=0.5)
        
        # Animate the transformation, highlighting the key insight
        self.play(
            TransformMatchingTex(sine_formula.copy(), sine_formula_simplified),
            Indicate(opposite_line, color=opposite_color),
            Indicate(hypotenuse_label, color=hypotenuse_color)
        )
        self.wait(2)

        # --- SCENE 5: ANIMATE THE ANGLE ---
        # Animate the angle changing and show the sine value updating in real-time
        self.play(theta_tracker.animate.set_value(PI / 2), run_time=3) # Animate to 90 degrees
        self.wait(1)
        self.play(theta_tracker.animate.set_value(5 * PI / 6), run_time=3) # Animate to 150 degrees
        self.wait(2)

        # --- SCENE 6: CONCLUSION ---
        # Clean up the scene by fading out all elements except the title
        self.play(
            FadeOut(axes), FadeOut(unit_circle), FadeOut(triangle_group),
            FadeOut(labels_group), FadeOut(sine_formula), FadeOut(sine_formula_simplified)
        )

        # Display the final summary message
        conclusion_text = Text(
            "Sine is the vertical height of a point\non the unit circle.",
            font_size=36,
            text_align=CENTER,
            line_spacing=1.2