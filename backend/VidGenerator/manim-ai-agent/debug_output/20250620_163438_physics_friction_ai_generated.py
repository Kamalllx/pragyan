from manim import *

class KineticFrictionScene(Scene):
    """
    An educational Manim animation explaining the basics of kinetic friction
    for beginners, including a quantitative example.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("Understanding Kinetic Friction", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)

        # Setup the scene: ground and a block
        ground = Line([-6, -2, 0], [6, -2, 0], color=GRAY, stroke_width=6)
        block = Rectangle(width=2, height=1, color=BLUE, fill_opacity=0.8).move_to([-4, -1.5, 0])
        block_label = MathTex("m").move_to(block.get_center())
        block_vgroup = VGroup(block, block_label)

        self.play(Create(ground))
        self.play(FadeIn(block_vgroup))
        self.wait(1)

        # 2. Main educational content: What is Kinetic Friction?
        intro_text = Text("Kinetic friction is a force that opposes motion", font_size=36).to_edge(UP)
        intro_text_2 = Text("when two surfaces are sliding past each other.", font_size=36).next_to(intro_text, DOWN)
        
        self.play(Write(intro_text))
        self.play(Write(intro_text_2))
        self.wait(2)

        # Animate the block moving and show the opposing friction force
        velocity_vector = Arrow(block.get_center(), block.get_center() + RIGHT * 2, buff=0.1, color=GREEN)
        velocity_label = MathTex("\\vec{v}", color=GREEN).next_to(velocity_vector, UP)
        
        friction_vector = Arrow(block.get_center(), block.get_center() + LEFT * 1.5, buff=0.1, color=RED)
        friction_label = MathTex("\\vec{f}_k", color=RED).next_to(friction_vector, UP)

        # Use updaters to keep vectors attached to the block as it moves
        velocity_vector.add_updater(lambda m: m.next_to(block, RIGHT, buff=0.1))
        velocity_label.add_updater(lambda m: m.next_to(velocity_vector, UP))
        friction_vector.add_updater(lambda m: m.next_to(block, LEFT, buff=0.1))
        friction_label.add_updater(lambda m: m.next_to(friction_vector, UP))

        self.play(Create(velocity_vector), Write(velocity_label))
        self.wait(1)
        self.play(Create(friction_vector), Write(friction_label))
        self.wait(1)

        self.play(block_vgroup.animate.shift(RIGHT * 6), run_time=3)
        self.wait(2)

        # Clear updaters and reset scene for explanation
        velocity_vector.clear_updaters()
        velocity_label.clear_updaters()
        friction_vector.clear_updaters()
        friction_label.clear_updaters()
        self.play(FadeOut(intro_text, intro_text_2, velocity_vector, velocity_label, friction_vector, friction_label))
        self.play(block_vgroup.animate.move_to([0, -1.5, 0]))
        self.wait(1)

        # 3. Key Concepts: Forces and the Friction Formula
        forces_title = Text("What determines the force of friction?", font_size=36).to_edge(UP)
        self.play(Write(forces_title))
        self.wait(1)

        # Introduce Normal Force and Gravity vectors
        gravity_vector = Arrow(block.get_center(), block.get_center() + DOWN * 2, buff=0, color=WHITE)
        gravity_label = MathTex("\\vec{F}_g", color=WHITE).next_to(gravity_vector, RIGHT)
        
        normal_vector = Arrow(block.get_center(), block.get_center() + UP * 2, buff=0, color=YELLOW)
        normal_label = MathTex("\\vec{F}_N", color=YELLOW).next_to(normal_vector, RIGHT)

        self.play(Create(gravity_vector), Write(gravity_label))
        self.wait(1)
        self.play(Create(normal_vector), Write(normal_label))
        self.wait(2)

        # Introduce the formula for kinetic friction
        formula = MathTex("f_k", "=", "\\mu_k", "\\cdot", "F_N", font_size=60).to_edge(UP, buff=1.5)
        self.play(Transform(forces_title, formula))
        self.wait(1)

        # Explain formula parts
        fk_desc = Text("Kinetic Friction Force (Newtons, N)", font_size=28).next_to(formula[0], DOWN, buff=0.5)
        mu_k_desc = Text("Coefficient of Kinetic Friction (unitless)", font_size=28).next_to(formula[2], DOWN, buff=0.5)
        FN_desc = Text("Normal Force (Newtons, N)", font_size=28).next_to(formula[4], DOWN, buff=0.5)

        self.play(Indicate(formula[0]), Write(fk_desc))
        self.wait(1.5)
        self.play(Indicate(formula[4]), Write(FN_desc))
        self.play(Indicate(VGroup(normal_vector, normal_label)))
        self.wait(1.5)
        self.play(Indicate(formula[2]), Write(mu_k_desc))
        self.wait(2)

        self.play(FadeOut(fk_desc, mu_k_desc, FN_desc))
        self.wait(1)

        # 4. Quantitative Example
        example_title = Text("Example Calculation", font_size=36).to_edge(UP)
        self.play(Transform(forces_title, example_title))
        self.wait(1)

        # Setup example values on the left side
        calc_vgroup = VGroup().to_edge(LEFT, buff=1)
        block_mass_text = MathTex("m = 10 \\text{ kg}").set_color(BLUE)
        mu_k_text = MathTex("\\mu_k = 0.3 \\text{ (wood on wood)}").set_color(ORANGE)
        gravity_const_text = MathTex("g \\approx 10 \\text{ m/s}^2").set_color(WHITE)
        given_info = VGroup(block_mass_text, mu_k_text, gravity_const_text).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        calc_vgroup.add(given_info)
        
        self.play(Write(given_info))
        self.wait(2)

        # Step 1: Calculate Normal Force
        step1_title = Text("Step 1: Find the Normal Force (F_N)", font_size=32).next_to(given_info, DOWN, buff=0.7, aligned_edge=LEFT)
        self.play(Write(step1_title))
        self.wait(1)

        fg_calc = MathTex("F_g = m \\cdot g = 10 \\text{ kg} \\cdot 10 \\text{ m/s}^2 = 100 \\text{ N}", font_size=36).next_to(step1_title, DOWN, aligned_edge=LEFT)
        self.play(Write(fg_calc))
        self.play(Indicate(VGroup(gravity_vector, gravity_label)))
        self.play(Transform(gravity_label, MathTex("100 \\text{ N}", color=WHITE).next_to(gravity_vector, RIGHT)))
        self.wait(1)

        fn_equals_fg = MathTex("F_N = F_g = 100 \\text{ N}", font_size=36).next_to(fg_calc, DOWN, aligned_edge=LEFT)
        self.play(Write(fn_equals_fg))
        self.play(Indicate(VGroup(normal_vector, normal_label)))
        self.play(Transform(normal_label, MathTex("100 \\text{ N}", color=YELLOW).next_to(normal_vector, RIGHT)))
        self.wait(2)

        # Step 2: Calculate Kinetic Friction
        step2_title = Text("Step 2: Calculate Kinetic Friction (f_k)", font_size=32).next_to(fn_equals_fg, DOWN, buff=0.7, aligned_edge=LEFT)
        self.play(Write(step2_title))
        self.wait(1)

        fk_calc_sub = MathTex("f_k = \\mu_k \\cdot F_N = 0.3 \\cdot 100 \\text{ N}", font_size=36).next_to(step2_title, DOWN, aligned_edge=LEFT)
        self.play(Write(fk_calc_sub))
        self.wait(1)

        fk_result = MathTex("f_k = 30 \\text{ N}", font_size=44, color=RED).next_to(fk_calc_sub, DOWN, aligned_edge=LEFT)
        self.play(Write(fk_result))
        self.wait(1)

        # Show the final friction vector with its calculated value
        friction_vector.move_to(block.get_center() + LEFT * 0.75)
        friction_label.next_to(friction_vector, UP)
        self.play(Create(friction_vector))
        self.play(Write(friction_label.become(MathTex("30 \\text{ N}", color=RED).next_to(friction_vector, UP))))
        self.wait(3)

        # 5. Summary and Conclusion
        self.play(
            FadeOut(forces_title, given_info, step1_title, fg_calc, fn_equals_fg, step2_title, fk_calc_sub, fk_result),
            FadeOut(block_vgroup, ground),
            FadeOut(gravity_vector, gravity_label, normal_vector, normal_label),
            FadeOut(friction_vector, friction_label)
        )
        self.wait(1)

        summary_title = Text("Summary: Kinetic Friction", font_size=48).to_edge(UP)
        self.play(Write(summary_title))
        self.wait(1)

        point1 = Text("• Opposes the motion of sliding objects.", font_size=36)
        point2 = Text("• Depends on the Normal Force and surface types (μk).", font_size=36)
        point3 = MathTex("f_k = \\mu_k F_N", font_size=48)

        summary_points = VGroup(point1, point2, point3).arrange(DOWN, buff=0.75).move_to(ORIGIN)
        summary_points[0].align_to(summary_points[1], LEFT)
        
        self.play(Write(summary_points[0]))
        self.wait(1.5)
        self.play(Write(summary_points[1]))
        self.wait(1.5)
        self.play(Write(summary_points[2]))
        self.wait(3)

        # Final fade out to end the scene
        self.play(FadeOut(summary_title, summary_points))
        self.wait(2)