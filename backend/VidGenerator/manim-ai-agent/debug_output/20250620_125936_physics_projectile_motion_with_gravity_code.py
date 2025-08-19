```python
# Manim Community v0.17.3

from manim import *

class ProjectileMotion(Scene):
    """
    An animation explaining the basics of projectile motion.
    It breaks down the motion into horizontal and vertical components
    and then combines them to show the resulting parabolic trajectory.
    """
    def construct(self):
        # -----------------------------------------------------------------
        # 1. Title Scene
        # -----------------------------------------------------------------
        title = Text("Projectile Motion", font_size=72)
        subtitle = Text("Analyzing motion in two dimensions", font_size=36).next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=DOWN))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        self.wait(1)

        # -----------------------------------------------------------------
        # 2. Setup the Scene with Axes
        # -----------------------------------------------------------------
        # Use a smaller camera frame to focus on the relevant area
        self.camera.frame.set(width=16).move_to(RIGHT * 3)

        # Create axes with labels
        axes = Axes(
            x_range=[0, 12, 2],
            y_range=[0, 6, 2],
            x_length=10,
            y_length=5,
            axis_config={"color": BLUE},
            x_axis_config={"numbers_to_include": np.arange(2, 12, 2)},
            y_axis_config={"numbers_to_include": np.arange(2, 7, 2)},
        ).add_coordinates()
        
        x_label = axes.get_x_axis_label(Tex("x (distance, m)"), edge=DOWN, direction=DOWN)
        y_label = axes.get_y_axis_label(Tex("y (height, m)"), edge=LEFT, direction=LEFT)
        
        scene_setup = VGroup(axes, x_label, y_label)
        self.play(Create(scene_setup))
        self.wait(1)

        # -----------------------------------------------------------------
        # 3. Decompose Initial Velocity
        # -----------------------------------------------------------------
        intro_text = Text("Let's launch a projectile!", font_size=36).to_corner(UR)
        self.play(Write(intro_text))

        # Initial velocity parameters
        v0 = 10
        angle = 60 * DEGREES
        g = 9.8

        # Initial velocity vector
        v_vec = Arrow(
            start=axes.c2p(0, 0),
            end=axes.c2p(v0 * np.cos(angle) / 4, v0 * np.sin(angle) / 4),
            buff=0,
            color=YELLOW,
        )
        v_label = MathTex("v_0", color=YELLOW).next_to(v_vec.get_end(), UR, buff=0.1)

        self.play(GrowArrow(v_vec), Write(v_label))
        self.wait(1)

        # Decompose into components
        decomp_text = Text("We analyze the horizontal (x) and vertical (y) components separately.", font_size=30).to_corner(UR)
        
        vx_vec = DashedLine(
            start=axes.c2p(0, 0),
            end=v_vec.get_end() * [1, 0, 0] + v_vec.get_start() * [0, 1, 1],
            color=RED
        )
        vx_label = MathTex("v_x", color=RED).next_to(vx_vec, DOWN)
        
        vy_vec = DashedLine(
            start=vx_vec.get_end(),
            end=v_vec.get_end(),
            color=GREEN
        )
        vy_label = MathTex("v_y", color=GREEN).next_to(vy_vec, RIGHT)

        self.play(ReplacementTransform(intro_text, decomp_text))
        self.play(GrowArrow(vx_vec), GrowArrow(vy_vec))
        self.play(Write(vx_label), Write(vy_label))
        self.wait(3)

        self.play(
            FadeOut(v_vec), FadeOut(v_label),
            FadeOut(vx_vec), FadeOut(vx_label),
            FadeOut(vy_vec), FadeOut(vy_label),
            FadeOut(decomp_text)
        )
        self.wait(1)

        # -----------------------------------------------------------------
        # 4. Horizontal Motion Analysis
        # -----------------------------------------------------------------
        h_title = Text("Horizontal Motion (x-axis)", font_size=36).to_corner(UR)
        h_law = MathTex("a_x = 0", "\\implies", "v_x = \\text{constant}", font_size=36).next_to(h_title, DOWN, align=RIGHT)
        
        self.play(Write(h_title))
        self.play(Write(h_law))

        # Animate constant horizontal velocity
        ball_h = Dot(axes.c2p(0, 0.5), color=RED)
        vx_const_vec = Arrow(start=ball_h.get_center(), end=ball_h.get_center() + RIGHT * 1.5, buff=0, color=RED)
        
        self.play(FadeIn(ball_h), GrowArrow(vx_const_vec))
        self.wait(1)
        self.play(
            ball_h.animate.move_to(axes.c2p(10, 0.5)),
            vx_const_vec.animate.move_to(axes.c2p(10, 0.5) + LEFT * 0.75),
            run_time=3
        )
        self.wait(2)
        self.play(FadeOut(h_title), FadeOut(h_law), FadeOut(ball_h), FadeOut(vx_const_vec))
        self.wait(1)

        # -----------------------------------------------------------------
        # 5. Vertical Motion Analysis
        # -----------------------------------------------------------------
        v_title = Text("Vertical Motion (y-axis)", font_size=36).to_corner(UR)
        v_law = MathTex("a_y = -g \\approx -9.8 \\, \\text{m/s}^2", font_size=36).next_to(v_title, DOWN, align=RIGHT)
        
        self.play(Write(v_title))
        self.play(Write(v_law))

        # Animate vertical motion with gravity
        ball_v = Dot(axes.c2p(0.5, 0), color=GREEN)
        
        # Time to reach the peak
        t_peak = (v0 * np.sin(angle)) / g
        
        # Updaters for velocity and ball position
        time = ValueTracker(0)
        vy_val = lambda t: v0 * np.sin(angle) - g * t
        y_pos = lambda t: (v0 * np.sin(angle)) * t - 0.5 *