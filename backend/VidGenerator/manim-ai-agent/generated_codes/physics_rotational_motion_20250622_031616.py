from manim import *

class RotationalMotionScene(Scene):
    """
    An engaging and educational animation for beginners about the basics of rotational motion.
    This scene explains rotation, angular velocity, and torque with clear visuals and simple language.
    """
    def construct(self):
        # Set a consistent theme for the scene
        self.camera.background_color = "#0d1117" # Dark background for better contrast

        # --- 1. Title Introduction ---
        title = Text("Understanding Rotational Motion", font_size=40)
        title.to_edge(UP, buff=0.8)
        
        self.play(Write(title))
        self.wait(1.5)
        self.play(FadeOut(title))
        self.wait(0.5)

        # --- 2. What is Rotation? ---
        intro_text = Text("Rotation is movement around a central point or axis.", font_size=28)

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix

        intro_text.shift(DOWN * 1.5)  # Auto-spacing fix
        intro_text.to_edge(UP)

        # Visual representation of rotation
        center_point = Dot(point=ORIGIN, radius=0.1, color=YELLOW)
        rotating_object = Dot(point=RIGHT * 2, color=BLUE)
        radius_line = Line(center_point.get_center(), rotating_object.get_center(), color=WHITE)
        path = Circle(radius=2, color=GRAY, stroke_opacity=0.5)

        rotation_group = VGroup(center_point, radius_line, rotating_object)
        
        self.play(Write(intro_text))
        self.play(Create(path), Create(center_point))
        self.play(Create(rotating_object), Create(radius_line))
        self.wait(1)

        # Animate the rotation
        self.play(
            Rotate(rotation_group, angle=2 * PI, about_point=ORIGIN, rate_func=linear, run_time=4)
        )
        self.wait(1)
        
        # Clear the screen for the next concept
        self.play(FadeOut(intro_text), FadeOut(rotation_group), FadeOut(path))
        self.wait(0.5)

        # --- 3. Angular Velocity (ω) ---
        concept_title_omega = Text("Angular Velocity (ω)", font_size=36).to_edge(UP)
        concept_desc_omega = Text("This measures how fast an object rotates.", font_size=24).next_to(concept_title_omega, DOWN, buff=0.5)

        self.play(Write(concept_title_omega))
        self.play(FadeIn(concept_desc_omega))
        self.wait(1)

        # Create two disks to compare speeds
        disk1 = VGroup(Circle(radius=1.2, color=BLUE), Text("Low ω", font_size=24)).move_to(LEFT * 3)
        disk2 = VGroup(Circle(radius=1.2, color=RED), Text("High ω", font_size=24)).move_to(RIGHT * 3)
        
        self.play(Create(disk1), Create(disk2))
        self.wait(1)

        # Animate rotation at different speeds
        self.play(
            Rotate(disk1, angle=PI, run_time=3, rate_func=linear),
            Rotate(disk2, angle=4 * PI, run_time=3, rate_func=linear)
        )
        self.wait(1.5)

        # Clear the screen
        self.play(FadeOut(concept_title_omega), FadeOut(concept_desc_omega), FadeOut(disk1), FadeOut(disk2))
        self.wait(0.5)

        # --- 4. Torque (τ) ---
        concept_title_torque = Text("Torque (τ)", font_size=36).to_edge(UP)
        concept_desc_torque = Text("A twisting force that causes rotation.", font_size=24).next_to(concept_title_torque, DOWN, buff=0.5)

        self.play(Write(concept_title_torque))
        self.play(FadeIn(concept_desc_torque))
        self.wait(1)

        # Door and hinge analogy for Torque
        hinge = Dot(LEFT * 3 + DOWN * 1, color=YELLOW)
        door = Rectangle(height=3, width=1.5, color=WHITE).next_to(hinge, RIGHT, buff=0)
        door_group = VGroup(door, hinge)

        # Force labels and arrows
        force_label_1 = MathTex("F", font_size=36).next_to(door, RIGHT, buff=0.2)
        force_arrow_1 = Arrow(force_label_1.get_center() + LEFT*0.5, door.get_right() + LEFT*0.5, buff=0.1, color=GREEN)
        
        force_label_2 = MathTex("F", font_size=36).next_to(hinge, RIGHT, buff=0.2)
        force_arrow_2 = Arrow(force_label_2.get_center() + LEFT*0.5, hinge.get_center() + RIGHT*0.5, buff=0.1, color=RED)

        explanation1 = Text("Applying force far from the hinge is effective.", font_size=24).to_edge(DOWN)
        explanation2 = Text("Applying force close to the hinge is ineffective.", font_size=24).to_edge(DOWN)

        self.play(Create(door_group))
        self.wait(1)

        # Demonstrate effective torque
        self.play(Create(force_arrow_1), Write(force_label_1))
        self.play(Write(explanation1))
        self.play(Rotate(door, angle=PI/3, about_point=hinge.get_center(), run_time=2))
        self.wait(1)
        self.play(Rotate(door, angle=-PI/3, about_point=hinge.get_center(), run_time=1.5))
        self.play(FadeOut(force_arrow_1), FadeOut(force_label_1), FadeOut(explanation1))
        self.wait(0.5)

        # Demonstrate ineffective torque
        self.play(Create(force_arrow_2), Write(force_label_2))
        self.play(Write(explanation2))
        self.play(Rotate(door, angle=PI/12, about_point=hinge.get_center(), run_time=2))
        self.wait(1)
        self.play(Rotate(door, angle=-PI/12, about_point=hinge.get_center(), run_time=1.5))
        self.wait(1)

        # Clear the screen
        self.play(FadeOut(concept_title_torque), FadeOut(concept_desc_torque), FadeOut(door_group), FadeOut(force_arrow_2), FadeOut(force_label_2), FadeOut(explanation2))
        self.wait(0.5)

        # --- 5. Summary ---
        summary_title = Text("Key Takeaways", font_size=40).to_edge(UP)
        
        line1 = Text("1. Rotation is motion around an axis.", font_size=28)
        line2 = Text("2. Angular Velocity (ω) is the speed of rotation.", font_size=28)
        line3 = Text("3. Torque (τ) is a twisting force that causes rotation.", font_size=28)
        
        summary_group = VGroup(line1, line2, line3).arrange(DOWN, buff=0.8).move_to(ORIGIN)

        self.play(Write(summary_title))
        self.wait(1)
        
        self.play(FadeIn(summary_group[0], shift=DOWN))
        self.wait(1)
        self.play(FadeIn(summary_group[1], shift=DOWN))
        self.wait(1)
        self.play(FadeIn(summary_group[2], shift=DOWN))
        
        # Final wait to let the viewer read the summary
        self.wait(3)