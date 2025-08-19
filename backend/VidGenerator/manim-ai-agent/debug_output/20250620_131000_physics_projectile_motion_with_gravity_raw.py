```python
from manim import *
import math

class ProjectileMotionScene(Scene):
    """
    An animation explaining the basics of projectile motion with gravity.
    This scene visualizes the trajectory, velocity vectors, and key formulae.
    """
    def construct(self):
        # -----------------------------------------------------------------
        # 1. Introduction and Title
        # -----------------------------------------------------------------
        title = Text("Projectile Motion", font_size=48)
        self.play(Write(title))
        self.wait(1)
        
        title_top_left = title.copy().scale(0.7).to_corner(UL)
        self.play(Transform(title, title_top_left))
        
        # -----------------------------------------------------------------
        # 2. Setup the Scene (Axes and Ground)
        # -----------------------------------------------------------------
        # We scale down the physics to fit the screen. 1 Manim unit = 10 meters.
        axes = Axes(
            x_range=[0, 12, 2],  # x represents 0 to 120 meters
            y_range=[0, 8, 2],   # y represents 0 to 80 meters
            x_length=12,
            y_length=7,
            axis_config={"color": BLUE, "include_tip": False}
        ).add_coordinates()

        x_label = axes.get_x_axis_label(Text("Distance (m)", font_size=24))
        y_label = axes.get_y_axis_label(Text("Height (m)", font_size=24).rotate(90 * DEGREES))
        
        scene_setup = VGroup(axes, x_label, y_label)
        self.play(Create(scene_setup))
        self.wait(0.5)

        # -----------------------------------------------------------------
        # 3. Define Physical Parameters and Initial Conditions
        # -----------------------------------------------------------------
        # Physical constants
        g = 9.8  # m/s^2
        
        # Initial conditions
        v0_val = 40.0  # m/s
        theta_val = 60  # degrees
        theta_rad = math.radians(theta_val)

        # Create text for initial conditions
        initial_cond_text = VGroup(
            MathTex(r"v_0 = 40 \, \text{m/s}", font_size=32),
            MathTex(r"\theta = 60^\circ", font_size=32),
            MathTex(r"g = 9.8 \, \text{m/s}^2", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR)

        self.play(Write(initial_cond_text))
        self.wait(1)

        # -----------------------------------------------------------------
        # 4. Decompose Initial Velocity Vector
        # -----------------------------------------------------------------
        # Calculate velocity components
        v_x = v0_val * math.cos(theta_rad)
        v_y = v0_val * math.sin(theta_rad)

        # Create initial velocity vector (scaled for visualization)
        v0_vec = Arrow(
            axes.c2p(0, 0), 
            axes.c2p(v_x / 10, v_y / 10), 
            buff=0, 
            color=YELLOW,
            stroke_width=5
        )
        v0_label = MathTex(r"\vec{v}_0", color=YELLOW).next_to(v0_vec.get_center(), UR, buff=0.1)

        self.play(GrowArrow(v0_vec), Write(v0_label))
        self.wait(1)

        # Show component vectors
        vx_vec = Arrow(axes.c2p(0, 0), axes.c2p(v_x / 10, 0), buff=0, color=RED)
        vy_vec = Arrow(axes.c2p(v_x / 10, 0), axes.c2p(v_x / 10, v_y / 10), buff=0, color=GREEN)
        vx_label = MathTex(r"\vec{v}_x", color=RED).next_to(vx_vec, DOWN)
        vy_label = MathTex(r"\vec{v}_y", color=GREEN).next_to(vy_vec, RIGHT)

        self.play(
            TransformFromCopy(v0_vec, vx_vec),
            TransformFromCopy(v0_vec, vy_vec),
            Write(vx_label),
            Write(vy_label)
        )
        self.wait(1)

        # Display formulae for components
        component_formulae = VGroup(
            MathTex(r"v_x = v_0 \cos(\theta) \approx {:.1f} \, \text{m/s}".format(v_x)),
            MathTex(r"v_y = v_0 \sin(\theta) \approx {:.1f} \, \text{m/s}".format(v_y))
        ).arrange(DOWN, aligned_edge=LEFT).next_to(initial_cond_text, DOWN, buff=0.5, aligned_edge=RIGHT)
        
        self.play(Write(component_formulae))
        self.wait(2)
        
        # Group vectors and labels to fade them out together
        velocity_components = VGroup(v0_vec, v0_label, vx_vec, vy_vec, vx_label, vy_label)
        self.play(FadeOut(velocity_components))

        # -----------------------------------------------------------------
        # 5. The Animation of Motion
        # -----------------------------------------------------------------
        # Define the projectile (a dot)
        dot = Dot(axes.c2p(0, 0), color=ORANGE)

        # Define the trajectory using a parametric function
        # x(t) = v_x * t
        # y(t) = v_y * t - 0.5 * g * t^2
        # We scale the output to fit the axes (divide by 10)
        trajectory = axes.plot(
            lambda t: (v_x * t) / 10,
            lambda t: (v_y * t - 0.5 * g * t**2) / 10,
            t_range=[0, (2 * v_y / g)],
            color=ORANGE
        )

        # Explain the motion
        explanation = Text("Horizontal: Constant Velocity\nVertical: Constant Acceleration", font_size=28).to_edge(DOWN)
        self.play(Write(explanation))
        self.wait(1)

        # Create updaters for the velocity vectors during flight
        current_vx_vec = Arrow(dot.get_center(), dot.get_center() + RIGHT * v_x / 10, buff=0, color=RED, stroke_width=4)
        current_vy_vec = Arrow(dot.get_center(), dot.get_center() + UP * v_y / 10, buff=0, color=GREEN, stroke_width=4)

        # Time tracker
        time = ValueTracker(0)
        total_time = 2 * v_y / g

        # Add updaters to move the dot and vectors
        dot.add_updater(
            lambda m: m.move_to(
                axes.c2p(
                    (v_x * time.get_value()) / 10,
                    (v_y * time.get_value() - 0.5 * g * time.get_value()**2) / 10
                )
            )
        )
        
        current_vx_vec.add_updater(
            lambda m: m.put_start_and_end_on(dot.get_center(), dot.get_center() + RIGHT * v_x / 10)
        )
        
        current_vy_vec.add_updater(
            lambda m: m.put_start_and_end_on(
                dot.get_center(), 
                dot.get_center() + UP * (v_y - g * time.get_value()) / 10
            )
        )

        self.add(dot, current_vx_vec, current_vy_vec)
        self.play(
            Create(trajectory),
            time.animate.set_value(total_time),
            run_time=5,
            rate_func=linear
        )
        
        # Remove updaters after animation is complete
        dot.clear_updaters()
        current_vx_vec.clear_updaters()
        current_vy_vec.clear_updaters()
        self.wait(1)
        self.play(FadeOut(explanation, current_vx_vec, current_vy_vec))

        # -----------------------------------------------------------------
        # 6. Highlight Key Points: Max Height and Range
        # -----------------------------------------------------------------
        # Max Height
        t_peak = v_y / g
        h_max = (v_y**2) / (2 * g)
        peak_point = axes.c2p((v_x * t_peak) / 10, h_max / 10)
        
        h_line = DashedLine(peak_point, axes.c2p(0, h_max / 10), color=YELLOW)
        h_label = MathTex(r"h_{\text{max}} \approx {:.1f} \, \text{m}".format(h_max), color=YELLOW, font_size=32)
        h_label.next_to(h_line, LEFT)

        self.play(Create(h_line), Write(h_label))
        self.wait(1)

        # Range
        range_val = v_x * total_time
        range_point = axes.c2p(range_val / 10, 0)
        
        r_line = DashedLine(axes.c2p(0,0), range_point, color=PINK)
        r_label = MathTex(r"\text{Range} \approx {:.1f} \, \text{m}".format(range_val), color=PINK, font_size=32)
        r_label.next_to(r_line, DOWN)

        self.play(Create(r_line), Write(r_label))
        self.wait(2)

        # -----------------------------------------------------------------
        # 7. Conclusion
        # -----------------------------------------------------------------
        self.play(
            FadeOut(VGroup(axes, x_label, y_label, trajectory, dot, h_line, h_label, r_line, r_label, initial_cond_text, component_formulae))
        )
        
        conclusion_text = VGroup(
            Text("Summary", font_size=40, weight=BOLD),
            Text("Projectile motion combines:", font_size=32),
            Text("1. Constant horizontal velocity.", color=RED, font_size=32),
            Text("2. Constant vertical acceleration (gravity).", color=GREEN, font_size=32)
        ).arrange(DOWN, buff=0.5).move_to(ORIGIN)
        
        self.play(Write(conclusion_text))
        
        # Final wait time as required
        self.wait(2)
```