from manim import *

class UniversalGravitationScene(Scene):
    """
    An intermediate-level animation explaining Newton's Law of Universal Gravitation.
    This scene covers the core concepts, the mathematical formula, and demonstrates
    how force changes with mass and distance.
    """
    def construct(self):
        # 1. Title Introduction
        # The title is created and positioned at the top edge of the frame.
        title = Text("The Law of Universal Gravitation", font_size=36)
        title.to_edge(UP)

        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        self.wait(0.5)

        # 2. Main Educational Content: Visual Demonstration
        # Create two masses (circles) and position them.
        mass1 = Circle(radius=0.5, color=BLUE, fill_opacity=0.8).shift(LEFT * 2.5)
        mass2 = Circle(radius=0.3, color=YELLOW, fill_opacity=0.8).shift(RIGHT * 2.5)
        
        # Create labels for the masses using MathTex for proper formatting.
        m1_label = MathTex("m_1", font_size=32).next_to(mass1, DOWN, buff=0.3)
        m2_label = MathTex("m_2", font_size=32).next_to(mass2, DOWN, buff=0.3)

        # Group the masses and their labels for easier management.
        mass_group = VGroup(mass1, mass2, m1_label, m2_label)
        mass_group.move_to(ORIGIN).shift(UP * 1.5)

        self.play(FadeIn(mass_group, scale=0.5))
        self.wait(1)

        # Draw a line representing the distance 'r' between the centers.
        distance_line = DashedLine(mass1.get_center(), mass2.get_center(), color=WHITE)
        r_label = MathTex("r", font_size=32).next_to(distance_line, DOWN, buff=0.3)
        
        self.play(Create(distance_line), Write(r_label))
        self.wait(1)

        # 3. Key Concepts with Explanations
        # Display the formula for Universal Gravitation.
        formula = MathTex(
            "F", "=", "G", r"\frac{m_1 m_2}{r^2}",
            font_size=48
        )
        formula.to_edge(DOWN, buff=1.0)
        
        self.play(Write(formula))
        self.wait(1)

        # Show the force vectors.
        force1 = Arrow(mass1.get_center(), mass2.get_center(), buff=mass2.radius, color=RED, max_tip_length_to_length_ratio=0.15)
        force2 = Arrow(mass2.get_center(), mass1.get_center(), buff=mass1.radius, color=RED, max_tip_length_to_length_ratio=0.15)
        force_group = VGroup(force1, force2)
        
        self.play(Create(force_group))
        self.wait(1)

        # Explain each part of the formula.
        explanation_group = VGroup(
            Text("F: Gravitational Force", font_size=24),
            Text("G: Gravitational Constant", font_size=24),
            Text("m₁, m₂: Masses of the objects", font_size=24),
            Text("r: Distance between centers", font_size=24)
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_edge(LEFT, buff=0.5)

        # Animate the explanation appearing while highlighting the corresponding formula part.
        self.play(FadeIn(explanation_group[0], shift=UP))
        self.play(Indicate(formula[0]))
        self.wait(0.5)
        self.play(FadeIn(explanation_group[1], shift=UP))
        self.play(Indicate(formula[2]))
        self.wait(0.5)
        self.play(FadeIn(explanation_group[2], shift=UP))
        self.play(Indicate(formula[3][2:5])) # Highlight m1*m2
        self.wait(0.5)
        self.play(FadeIn(explanation_group[3], shift=UP))
        self.play(Indicate(formula[3][6])) # Highlight r
        self.wait(2)

        # Clear explanations for the next section.
        self.play(FadeOut(explanation_group))
        self.wait(0.5)

        # 4. Examples or Applications
        # Demonstration 1: Effect of increasing mass.
        demo_title1 = Text("Force increases with mass", font_size=28).move_to(formula.get_center())
        self.play(Transform(formula, demo_title1))
        self.wait(1)

        # Store original state for reset.
        original_mass2 = mass2.copy()
        original_m2_label = m2_label.copy()
        
        # Animate the change in mass and force.
        self.play(
            mass2.animate.scale(1.5),
            m2_label.animate.next_to(mass2, DOWN, buff=0.3).scale(1.5),
            force1.animate.put_start_and_end_on(mass1.get_center(), mass2.get_center() + RIGHT * 0.3),
            force2.animate.put_start_and_end_on(mass2.get_center() + RIGHT * 0.3, mass1.get_center()),
            run_time=2
        )
        self.wait(2)

        # Reset for the next demonstration.
        self.play(
            Transform(mass2, original_mass2),
            Transform(m2_label, original_m2_label),
            force1.animate.put_start_and_end_on(mass1.get_center(), mass1.get_center() + RIGHT * 5),
            force2.animate.put_start_and_end_on(mass1.get_center() + RIGHT * 5, mass1.get_center()),
            run_time=1.5
        )
        self.wait(1)

        # Demonstration 2: Effect of increasing distance.
        demo_title2 = Text("Force decreases with distance (Inverse Square Law)", font_size=28).move_to(formula.get_center())
        self.play(Transform(formula, demo_title2))
        self.wait(1)

        # Animate the change in distance and force.
        self.play(
            VGroup(mass2, m2_label).animate.shift(RIGHT * 1.5),
            distance_line.animate.put_start_and_end_on(mass1.get_center(), mass2.get_center() + RIGHT * 1.5),
            r_label.animate.next_to(distance_line, DOWN, buff=0.3).shift(RIGHT * 0.75),
            force1.animate.set_length(force1.get_length() * 0.4),
            force2.animate.set_length(force2.get_length() * 0.4),
            run_time=2
        )
        self.wait(2)

        # 5. Summary and Conclusion
        # Fade out all elements to prepare for the summary.
        self.play(
            FadeOut(mass_group),
            FadeOut(force_group),
            FadeOut(distance_line),
            FadeOut(r_label),
            FadeOut(formula)
        )
        self.wait(0.5)

        # Create a summary VGroup with key takeaways.
        summary_title = Text("Key Takeaways", font_size=32).to_edge(UP, buff=0.8)
        summary_points = VGroup(
            Text("• Gravitational force is always attractive.", font_size=28),
            Text("• Stronger with more mass.", font_size=28),
            Text("• Weaker with more distance.", font_size=28)
        ).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        
        summary_group = VGroup(summary_title, summary_points).move_to(ORIGIN)

        self.play(Write(summary_group))
        self.wait(3)

        # End of the scene.
        self.play(FadeOut(summary_group))
        self.wait(2)