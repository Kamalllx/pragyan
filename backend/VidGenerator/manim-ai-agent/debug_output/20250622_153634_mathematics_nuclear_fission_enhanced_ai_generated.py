from manim import *

class NuclearFissionScene(Scene):
    """
    An animation explaining the concept of nuclear fission for beginners,
    connecting the physical process to the mathematical principle of mass-energy equivalence.
    """
    def construct(self):
        # Set a background color
        self.camera.background_color = "#0E1A25"

        # --- 1. Title Introduction ---
        title = Text("Understanding Nuclear Fission", font_size=40)
        title.to_edge(UP, buff=0.8)
        self.play(Write(title))
        self.wait(1)

        # --- 2. Introducing the Components ---
        # Uranium-235 Nucleus
        u235_nucleus = Circle(radius=1.2, color=BLUE_D, fill_opacity=0.8)
        u235_label = VGroup(
            Text("Uranium-235", font_size=24),
            Text("(Unstable Nucleus)", font_size=20)
        ).arrange(DOWN, buff=0.2).next_to(u235_nucleus, DOWN, buff=0.5)
        uranium_group = VGroup(u235_nucleus, u235_label).move_to(ORIGIN)

        # Neutron
        neutron = Circle(radius=0.2, color=GRAY_A, fill_opacity=1)
        neutron_label = Text("Neutron", font_size=24).next_to(neutron, UP, buff=0.3)
        neutron_group = VGroup(neutron, neutron_label).move_to(LEFT * 5)

        self.play(FadeIn(uranium_group, shift=DOWN), FadeIn(neutron_group, shift=UP))
        self.wait(2)

        # --- 3. The Fission Process ---
        # Neutron Collision
        self.play(neutron_group.animate.move_to(u235_nucleus.get_center() + LEFT * 1.2))
        self.play(FadeOut(neutron_label))
        self.play(neutron.animate.move_to(u235_nucleus.get_center()))
        
        # Nucleus becomes unstable
        unstable_nucleus = u235_nucleus.copy()
        self.play(Transform(u235_nucleus, unstable_nucleus), FadeIn(neutron))
        self.play(Wiggle(u235_nucleus, n_wiggles=8, scale_value=1.1), run_time=1.5)
        self.wait(0.5)

        # --- 4. Fission and Release of Energy/Neutrons ---
        # Create fission fragments
        fragment1 = Circle(radius=0.7, color=GREEN_D, fill_opacity=0.8).move_to(LEFT * 1.5)
        fragment2 = Circle(radius=0.6, color=YELLOW_D, fill_opacity=0.8).move_to(RIGHT * 1.5)
        fragments = VGroup(fragment1, fragment2)
        
        # Create new neutrons
        neutron_out1 = Circle(radius=0.2, color=GRAY_A, fill_opacity=1).move_to(UP * 1.5 + RIGHT * 0.5)
        neutron_out2 = Circle(radius=0.2, color=GRAY_A, fill_opacity=1).move_to(DOWN * 1.2 + LEFT * 0.2)
        neutron_out3 = Circle(radius=0.2, color=GRAY_A, fill_opacity=1).move_to(RIGHT * 1.8)
        new_neutrons = VGroup(neutron_out1, neutron_out2, neutron_out3)

        # Energy release visualization
        energy_flash = AnnularSector(inner_radius=0, outer_radius=3, angle=2*PI, start_angle=0, color=ORANGE, fill_opacity=0.7)

        self.play(
            FadeOut(u235_nucleus, neutron, u235_label),
            FadeIn(energy_flash),
            FadeIn(fragments),
            FadeIn(new_neutrons)
        )
        self.play(
            FadeOut(energy_flash, scale=3),
            fragments.animate.shift(LEFT * 1.5 + RIGHT * 1.5), # moves them further apart
            new_neutrons.animate.scale(1.5).move_to(ORIGIN).shift(UP*0.2 + RIGHT*0.2).scale(3).set_opacity(0),
            run_time=2
        )
        self.wait(1)
        self.play(FadeOut(fragments, new_neutrons))

        # --- 5. The Mathematics: Mass-Energy Equivalence ---
        # Clear the title and introduce the math concept
        self.play(Transform(title, Text("The Math Behind the Energy", font_size=40).to_edge(UP, buff=0.8)))

        # Display E=mc^2
        equation = MathTex("E = m c^2", font_size=60).move_to(ORIGIN)
        self.play(Write(equation))
        self.wait(2)

        # Explain the terms
        explanation = VGroup(
            Text("E = Energy Released", font_size=28),
            Text("m = Mass Lost (Mass Defect)", font_size=28),
            Text("c = Speed of Light (a very large constant)", font_size=28)
        ).arrange(DOWN, buff=0.5).next_to(equation, DOWN, buff=1.0)
        
        self.play(FadeIn(explanation, shift=UP))
        self.wait(3)

        self.play(FadeOut(equation), FadeOut(explanation))
        self.wait(1)

        # --- 6. Visualizing Mass Defect ---
        # "Before" state
        mass_before_label = Text("Mass Before Fission", font_size=28).to_edge(UP, buff=1.5).shift(LEFT * 3)
        u235_before = Circle(radius=0.6, color=BLUE_D, fill_opacity=0.8)
        neutron_before = Circle(radius=0.15, color=GRAY_A, fill_opacity=1).next_to(u235_before, RIGHT, buff=0.2)
        group_before = VGroup(u235_before, neutron_before).next_to(mass_before_label, DOWN, buff=0.5)

        # "After" state
        mass_after_label = Text("Mass After Fission", font_size=28).to_edge(UP, buff=1.5).shift(RIGHT * 3)
        frag1_after = Circle(radius=0.45, color=GREEN_D, fill_opacity=0.8)
        frag2_after = Circle(radius=0.4, color=YELLOW_D, fill_opacity=0.8).next_to(frag1_after, RIGHT, buff=0.2)
        neutrons_after = VGroup(
            Circle(radius=0.15, color=GRAY_A, fill_opacity=1),
            Circle(radius=0.15, color=GRAY_A, fill_opacity=1),
            Circle(radius=0.15, color=GRAY_A, fill_opacity=1)
        ).arrange(RIGHT, buff=0.1).next_to(frag2_after, RIGHT, buff=0.2)
        group_after = VGroup(frag1_after, frag2_after, neutrons_after).next_to(mass_after_label, DOWN, buff=0.5)

        self.play(
            Write(mass_before_label), Create(group_before),
            Write(mass_after_label), Create(group_after)
        )
        self.wait(2)

        # Show the inequality
        mass_inequality = MathTex("m_{before}", ">", "m_{after}", font_size=48).move_to(DOWN * 1.5)
        mass_inequality.set_color_by_tex("m_{before}", BLUE)
        mass_inequality.set_color_by_tex("m_{after}", GREEN)
        
        self.play(Write(mass_inequality))
        self.wait(2)

        # Explain the result
        conclusion_text = Text(
            "The 'lost' mass is converted into a huge amount of energy!",
            font_size=28,
            color=ORANGE
        ).to_edge(DOWN, buff=1.0)
        self.play(Write(conclusion_text))

        # --- 7. Final Summary ---
        self.wait(3)
        self.play(
            FadeOut(title), FadeOut(mass_before_label), FadeOut(group_before),
            FadeOut(mass_after_label), FadeOut(group_after), FadeOut(mass_inequality),
            FadeOut(conclusion_text)
        )
        self.wait(1)

        summary_title = Text("Summary of Nuclear Fission", font_size=40).to_edge(UP, buff=0.8)
        summary_points = VGroup(
            Text("1. A neutron hits a large, unstable nucleus.", font_size=28, text_align="left"),
            Text("2. The nucleus splits into smaller parts (fragments).", font_size=28, text_align="left"),
            Text("3. A small amount of mass is lost in the process.", font_size=28, text_align="left"),
            Text("4. This lost mass becomes a vast amount of energy (E=mc²).", font_size=28, text_align="left")
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(ORIGIN).shift(LEFT*2)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_points, shift=UP, lag_ratio=0.5))

        self.wait(5)