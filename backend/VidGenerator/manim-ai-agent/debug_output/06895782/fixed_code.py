
from manim import *

class ProjectileMotionScene(Scene):
    """
    An animation explaining the basics of projectile motion under gravity.
    This scene visualizes the velocity components, the parabolic trajectory,
    and the governing equations.
    """
    def construct(self):
        # Set a consistent color scheme
        GRAVITY_COLOR = ORANGE
        VELOCITY_COLOR = GREEN
        X_VELOCITY_COLOR = BLUE
        Y_VELOCITY_COLOR = RED
        PATH_COLOR = YELLOW
        TEXT_COLOR = WHITE

        # --- 1. Title ---
        # Display the title of the animation
        title = Text("Projectile Motion with Gravity", font_size)