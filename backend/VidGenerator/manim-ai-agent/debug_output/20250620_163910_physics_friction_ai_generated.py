from manim import *

class FrictionAnimation(Scene):
    def construct(self):
        # Set a simple color scheme
        self.camera.background_color = "#F0F0F0"
        box_color = BLUE_D
        force_color = RED_D
        friction_color = GREEN_D
        text_color = BLACK

        # --- 1. Title Introduction (1.5s) ---
        title = Text("Understanding Friction", font_size=60, color=text_color)
        self.play(Write(title), run_time=1)
        self.wait(0.5)
        self.play(FadeOut(title), run_time=0.5)

        # --- 2. Scene Setup (1s) ---
        ground = Line(LEFT * 6, RIGHT * 6, color=GRAY_BROWN, stroke_width=6).shift(DOWN * 2)
        box = Rectangle(width=1.5, height=1, color=box_color, fill_opacity=0.8).next_to(ground, UP, buff=0)
        box.z_index = 1 # Ensure box is on top of arrows
        
        self.play(Create(ground), FadeIn(box), run_time=1)

        # --- 3. Static Friction (3.5s) ---
        # Create force vectors
        push_force_static = Vector([1.5, 0], color=force_color).next_to(box, LEFT, buff=0)
        static_friction_force = Vector([-1.5, 0], color=friction_color).next_to(box, RIGHT, buff=0)
        
        # Create labels for forces and formula
        push_label = Text("Push", font_size=24, color=text_color).next_to(push_force_static, UP, buff=0.1)
        static_friction_label = Text("Static Friction", font_size=24, color=text_color).next_to(static_friction_force, UP, buff=0.1)
        static_formula = MathTex(r"f_s \le \mu_s N", font_size=48, color=text_color).to_edge(UP)

        # Animate static friction
        self.play(
            AnimationGroup(
                GrowArrow(push_force_static),
                GrowArrow(static_friction_force),
                Write(push_label),
                Write(static_friction_label),
                lag_ratio=0.5
            ),
            run_time=1.5
        )
        self.play(Write(static_formula), run_time=1)
        self.play(Indicate(box)) # Show it's not moving
        self.wait(0.5)

        # --- 4. Kinetic Friction (4s) ---
        # Create new vectors and labels for the kinetic phase
        push_force_kinetic = Vector([3, 0], color=force_color).next_to(box, LEFT, buff=0)
        kinetic_friction_force = Vector([-2, 0], color=friction_color).next_to(box, RIGHT, buff=0)
        kinetic_friction_label = Text("Kinetic Friction", font_size=24, color=text_color).next_to(kinetic_friction_force, UP, buff=0.1)
        kinetic_formula = MathTex(r"f_k = \mu_k N", font_size=48, color=text_color).to_edge(UP)

        # Group objects for simultaneous animation
        box_group = VGroup(box, push_force_kinetic, kinetic_friction_force, push_label, kinetic_friction_label)

        # Animate transition to kinetic friction and movement
        self.play(
            Transform(push_force_static, push_force_kinetic),
            Transform(static_friction_force, kinetic_friction_force),
            Transform(static_friction_label, kinetic_friction_label),
            FadeOut(static_formula, shift=UP),
            FadeIn(kinetic_formula, shift=UP),
            run_time=1.5
        )
        
        # Animate the box moving with constant velocity
        self.play(box_group.animate.shift(RIGHT * 4), run_time=2)

        # --- 5. Final Wait (2s) ---
        self.wait(2)