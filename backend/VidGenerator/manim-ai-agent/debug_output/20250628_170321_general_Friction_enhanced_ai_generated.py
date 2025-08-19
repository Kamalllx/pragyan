from manim import *

class FrictionAnimation(Scene):
    def construct(self):
        # 1. Title Introduction
        title = Text("Understanding Friction", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # 2. Visual Demonstration: Static Friction
        # Setup the ground and the block
        ground = Line([-6, -2, 0], [6, -2, 0], stroke_width=6, color=GRAY)
        block = Rectangle(width=2, height=1, color=BLUE, fill_opacity=0.8)
        block.next_to(ground, UP, buff=0)
        block_label = Text("Block", font_size=24).next_to(block, UP, buff=0.2)
        
        scene_group = VGroup(ground, block, block_label)
        self.play(Create(ground), FadeIn(block), Write(block_label))
        self.wait(1)

        # Introduce forces for static friction
        applied_force_arrow = Arrow(start=block.get_left(), end=block.get_right(), buff=0, color=GREEN)
        applied_force_arrow.shift(LEFT * 2.5)
        applied_force_label = MathTex("F_{applied}", font_size=32, color=GREEN).next_to(applied_force_arrow, LEFT, buff=0.2)

        friction_force_arrow = Arrow(start=block.get_center(), end=block.get_center() + LEFT, buff=0, color=RED)
        friction_force_arrow.next_to(ground, UP, buff=0)
        friction_force_label = MathTex("F_{static}", font_size=32, color=RED).next_to(friction_force_arrow, DOWN, buff=0.2)

        static_explanation = Text("Static friction opposes the applied force, preventing motion.", font_size=28)
        static_explanation.to_edge(DOWN)

        self.play(
            GrowArrow(applied_force_arrow),
            Write(applied_force_label),
            FadeIn(static_explanation)
        )
        self.wait(1)
        self.play(
            GrowArrow(friction_force_arrow),
            Write(friction_force_label)
        )
        self.wait(2)

        # 3. Transition to Kinetic Friction
        kinetic_explanation = Text("When the applied force exceeds max static friction, the block moves.", font_size=28)
        kinetic_explanation.to_edge(DOWN)
        
        # Make applied force larger
        new_applied_force_arrow = Arrow(start=block.get_left(), end=block.get_right(), buff=0, color=GREEN).scale(1.5)
        new_applied_force_arrow.shift(LEFT * 3.5)
        
        # Kinetic friction is smaller than max static friction
        kinetic_friction_arrow = Arrow(start=block.get_center(), end=block.get_center() + LEFT * 0.6, buff=0, color=RED)
        kinetic_friction_arrow.next_to(ground, UP, buff=0)
        kinetic_friction_label = MathTex("F_{kinetic}", font_size=32, color=RED).next_to(kinetic_friction_arrow, DOWN, buff=0.2)

        self.play(
            Transform(applied_force_arrow, new_applied_force_arrow),
            Transform(friction_force_arrow, kinetic_friction_arrow),
            Transform(friction_force_label, kinetic_friction_label),
            FadeOut(static_explanation),
            FadeIn(kinetic_explanation)
        )
        self.wait(1)

        # Animate the block moving
        moving_group = VGroup(block, block_label, applied_force_arrow, friction_force_arrow, friction_force_label, applied_force_label)
        self.play(moving_group.animate.shift(RIGHT * 4), run_time=3)
        self.wait(1)

        # Fade out scene to introduce formulas
        self.play(
            FadeOut(moving_group),
            FadeOut(ground),
            FadeOut(kinetic_explanation),
            FadeOut(title)
        )
        self.wait(1)

        # 4. Key Concepts and Formulas
        formulas_title = Text("Key Formulas", font_size=40).to_edge(UP)
        self.play(Write(formulas_title))

        # Normal Force explanation
        block_center = Rectangle(width=2, height=1, color=BLUE, fill_opacity=0.8).move_to(LEFT * 4)
        weight_arrow = Arrow(block_center.get_bottom(), block_center.get_bottom() + DOWN * 1.5, buff=0, color=YELLOW)
        weight_label = MathTex("W = mg", color=YELLOW, font_size=36).next_to(weight_arrow, DOWN)
        
        normal_arrow = Arrow(block_center.get_top(), block_center.get_top() + UP * 1.5, buff=0, color=ORANGE)
        normal_label = MathTex("N", color=ORANGE, font_size=36).next_to(normal_arrow, UP)
        
        normal_force_group = VGroup(block_center, weight_arrow, weight_label, normal_arrow, normal_label)
        normal_force_group.move_to(LEFT * 3.5)

        self.play(FadeIn(normal_force_group))
        self.wait(1)

        # Friction formulas
        static_formula = MathTex("F_{static} \\le \\mu_s N", font_size=40)
        kinetic_formula = MathTex("F_{kinetic} = \\mu_k N", font_size=40)
        
        formula_group = VGroup(static_formula, kinetic_formula).arrange(DOWN, buff=1.0)
        formula_group.next_to(normal_force_group, RIGHT, buff=1.5)

        self.play(Write(static_formula))
        self.wait(1)
        self.play(Write(kinetic_formula))
        self.wait(2)

        # Explain coefficients
        coeff_s = MathTex("\\mu_s", ": \\text{Coefficient of Static Friction}", font_size=32)
        coeff_k = MathTex("\\mu_k", ": \\text{Coefficient of Kinetic Friction}", font_size=32)
        
        explanation_group = VGroup(coeff_s, coeff_k).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        explanation_group.to_edge(DOWN, buff=1.0)

        self.play(Write(explanation_group))
        self.wait(2)

        # Fade out everything for summary
        self.play(
            FadeOut(formulas_title),
            FadeOut(normal_force_group),
            FadeOut(formula_group),
            FadeOut(explanation_group)
        )
        self.wait(1)

        # 5. Summary
        summary_title = Text("Summary", font_size=40).to_edge(UP)
        
        point1 = Text("• Friction is a force that opposes motion or tendency of motion.", font_size=28)
        point2 = Text("• Static Friction acts on stationary objects.", font_size=28)
        point3 = Text("• Kinetic Friction acts on moving objects.", font_size=28)
        point4 = Text("• Friction depends on the surfaces in contact (μ) and the normal force (N).", font_size=28)

        summary_group = VGroup(point1, point2, point3, point4).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        summary_group.move_to(ORIGIN)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_group, shift=UP))
        
        self.wait(2)