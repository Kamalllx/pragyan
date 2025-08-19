from manim import *

class ProjectileMotionScene(Scene):
    def construct(self):
        # 1. Title Introduction
        title = Text("Projectile Motion", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Setup the ground and cannon
        ground = Line(LEFT * 7, RIGHT * 7, color=GREEN).to_edge(DOWN, buff=1.0)
        cannon = VGroup(
            Rectangle(width=1.0, height=0.5, color=GRAY, fill_opacity=1),
            Rectangle(width=1.5, height=0.3, color=GRAY, fill_opacity=1).next_to(Rectangle(width=1.0, height=0.5), UP, buff=0)
        ).move_to(ground.get_start() + UP * 0.4 + RIGHT * 0.75)
        
        self.play(Create(ground), FadeIn(cannon))
        self.wait(1)

        # 2. Main educational content with visual demonstrations
        intro_text = Text("An object thrown into the air is a projectile.", font_size=24).next_to(title, DOWN, buff=0.5)
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # Create the projectile and its path
        projectile = Dot(point=cannon.get_center() + RIGHT * 0.5, color=YELLOW)
        path = ParametricFunction(
            lambda t: np.array([4 * t, -4.9 * t**2 + 6 * t, 0]),
            t_range=np.array([0, 1.22]),
            color=ORANGE
        ).move_to(projectile.get_center(), aligned_edge=LEFT)

        self.play(FadeIn(projectile, scale=0.5))
        self.play(MoveAlongPath(projectile, path), run_time=3)
        self.wait(1)

        # 3. Key concepts with clear explanations
        
        # Decompose initial velocity into components
        concepts_title = Text("Key Concepts", font_size=36).to_edge(UP, buff=1.5)
        self.play(Transform(title, concepts_title), FadeOut(projectile, ground, cannon))
        
        # Create axes and vectors
        axes = Axes(
            x_range=[0, 7, 1],
            y_range=[0, 4, 1],
            x_length=6,
            y_length=3,
            axis_config={"color": BLUE},
        ).to_edge(DOWN, buff=1.0).to_edge(LEFT, buff=1.0)
        
        origin_dot = Dot(axes.c2p(0, 0), color=RED)
        
        # Initial velocity vector
        v_vec = Arrow(axes.c2p(0,0), axes.c2p(3, 2.5), buff=0, color=YELLOW)
        v_label = MathTex("v_0", font_size=32).next_to(v_vec.get_end(), UR, buff=0.1)
        
        # Velocity components
        vx_vec = DashedLine(axes.c2p(0,0), axes.c2p(3, 0), color=GREEN)
        vx_label = MathTex("v_x", font_size=32, color=GREEN).next_to(vx_vec, DOWN, buff=0.2)
        vy_vec = DashedLine(axes.c2p(3,0), axes.c2p(3, 2.5), color=RED)
        vy_label = MathTex("v_y", font_size=32, color=RED).next_to(vy_vec, RIGHT, buff=0.2)

        components_group = VGroup(v_vec, v_label, vx_vec, vx_label, vy_vec, vy_label)
        
        explanation_text = VGroup(
            Text("Motion has two components:", font_size=24),
            Text("1. Horizontal (constant velocity)", font_size=24, color=GREEN),
            Text("2. Vertical (affected by gravity)", font_size=24, color=RED)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).to_edge(RIGHT, buff=1.0).shift(UP*0.5)

        self.play(Create(axes), Create(origin_dot))
        self.play(Write(explanation_text[0]))
        self.wait(1)
        self.play(Create(v_vec), Write(v_label))
        self.wait(1)
        self.play(Create(vx_vec), Write(vx_label), Write(explanation_text[1]))
        self.wait(1)
        self.play(Create(vy_vec), Write(vy_label), Write(explanation_text[2]))
        self.wait(2)

        self.play(FadeOut(axes, origin_dot, components_group, explanation_text))

        # 4. Visualizing motion with gravity
        self.play(FadeIn(ground, cannon, path))
        
        # Create trackers for velocity components
        projectile_tracker = ValueTracker(0)
        
        # The projectile dot that will move
        moving_dot = Dot(color=YELLOW).add_updater(
            lambda m: m.move_to(path.point_from_proportion(projectile_tracker.get_value()))
        )

        # Horizontal velocity vector (constant)
        vx_vector = Arrow(start=ORIGIN, end=RIGHT * 1.0, color=GREEN).add_updater(
            lambda v: v.next_to(moving_dot, UP, buff=0.1)
        )
        vx_text = MathTex("v_x", color=GREEN, font_size=24).add_updater(
            lambda t: t.next_to(vx_vector, UP, buff=0.1)
        )

        # Vertical velocity vector (changes)
        vy_vector = Arrow(start=ORIGIN, end=UP, color=RED).add_updater(
            lambda v: v.put_start_and_end_on(
                moving_dot.get_center(),
                moving_dot.get_center() + UP * (1.22 - 2 * projectile_tracker.get_value() * 1.22)
            )
        )
        vy_text = MathTex("v_y", color=RED, font_size=24).add_updater(
            lambda t: t.next_to(vy_vector, RIGHT, buff=0.1)
        )
        
        # Gravity vector (constant)
        g_vector = Arrow(start=UP*0.5, end=DOWN*0.5, color=BLUE_A).add_updater(
            lambda v: v.move_to(moving_dot.get_center() + LEFT * 1.0)
        )
        g_text = MathTex("g", color=BLUE_A, font_size=24).add_updater(
            lambda t: t.next_to(g_vector, LEFT, buff=0.1)
        )

        self.play(
            FadeIn(moving_dot, vx_vector, vy_vector, g_vector, vx_text, vy_text, g_text)
        )
        self.play(projectile_tracker.animate.set_value(1), run_time=4, rate_func=linear)
        self.wait(2)

        # 5. Summary or conclusion
        self.play(
            FadeOut(title, ground, cannon, path, moving_dot, vx_vector, vy_vector, g_vector, vx_text, vy_text, g_text)
        )
        
        summary_title = Text("Summary", font_size=40).to_edge(UP)
        summary_points = VGroup(
            Text("1. The path of a projectile is a parabola.", font_size=28),
            Text("2. Horizontal motion has constant velocity.", font_size=28),
            Text("3. Vertical motion has constant acceleration (gravity).", font_size=28)
        ).arrange(DOWN, buff=0.8, aligned_edge=LEFT).move_to(ORIGIN)

        self.play(Write(summary_title))
        self.wait(1)
        self.play(FadeIn(summary_points, shift=UP))
        
        self.wait(3)