from manim import *

class NuclearFissionScene(Scene):
    """
    An intermediate-level Manim animation explaining the process of nuclear fission,
    including the chain reaction and the role of mass-energy equivalence.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("Nuclear Fission", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))
        self.wait(0.5)

        # 2. Main Educational Content: A Single Fission Event
        # Setup the initial nucleus and neutron
        u235_nucleus = Circle(radius=0.8, color=BLUE, fill_opacity=0.8).set_z_index(1)
        u235_label = MathTex("^{235}U").next_to(u235_nucleus, DOWN)
        uranium_group = VGroup(u235_nucleus, u235_label).move_to(ORIGIN)

        neutron = Circle(radius=0.1, color=GRAY, fill_opacity=1).move_to(LEFT * 5)
        neutron_label = Text("Neutron", font_size=24).next_to(neutron, UP, buff=0.2)
        
        self.play(FadeIn(uranium_group), FadeIn(neutron), Write(neutron_label))
        self.wait(1)

        # Animate neutron impact
        self.play(neutron.animate.move_to(u235_nucleus.get_center()), FadeOut(neutron_label))
        
        # Show unstable nucleus
        unstable_nucleus = Circle(radius=0.9, color=PURPLE, fill_opacity=0.8).set_z_index(0)
        unstable_label = MathTex("^{236}U^*").next_to(unstable_nucleus, DOWN)
        unstable_group = VGroup(unstable_nucleus, unstable_label).move_to(ORIGIN)

        self.play(FadeOut(u235_label), Transform(u235_nucleus, unstable_nucleus), FadeIn(unstable_label))
        self.play(Wiggle(unstable_group))
        self.wait(1)

        # Animate fission
        fragment1 = Circle(radius=0.5, color=GREEN, fill_opacity=0.8).move_to(LEFT * 2)
        fragment1_label = MathTex("^{141}Ba").next_to(fragment1, DOWN)
        f1_group = VGroup(fragment1, fragment1_label)

        fragment2 = Circle(radius=0.4, color=YELLOW, fill_opacity=0.8).move_to(RIGHT * 2)
        fragment2_label = MathTex("^{92}Kr").next_to(fragment2, DOWN)
        f2_group = VGroup(fragment2, fragment2_label)

        new_neutrons = VGroup(
            *[Circle(radius=0.1, color=GRAY, fill_opacity=1) for _ in range(3)]
        ).arrange(RIGHT, buff=0.5).move_to(ORIGIN)

        energy_flash = Circle(radius=2.5, color=ORANGE, fill_opacity=0.6)
        energy_label = Text("Energy Released!", font_size=32, color=ORANGE).next_to(energy_flash, UP, buff=0.2)

        self.play(
            FadeOut(unstable_group),
            FadeIn(f1_group, f2_group),
            Create(energy_flash),
            Write(energy_label)
        )
        self.play(
            new_neutrons[0].animate.move_to(UP * 1.5 + RIGHT * 1),
            new_neutrons[1].animate.move_to(DOWN * 1.5 + LEFT * 1),
            new_neutrons[2].animate.move_to(UP * 0.5 + LEFT * 2.5),
        )
        self.wait(1)
        self.play(FadeOut(energy_flash, energy_label))
        self.wait(1)

        # 3. Key Concepts: Mass-Energy Equivalence
        fission_products = VGroup(f1_group, f2_group, new_neutrons)
        self.play(fission_products.animate.scale(0.7).to_edge(RIGHT, buff=1.0))

        einstein_formula = MathTex("E = mc^2", font_size=48).move_to(LEFT * 3)
        explanation = VGroup(
            Text("The released energy comes from a", font_size=24),
            Text("tiny loss of mass.", font_size=24),
            MathTex(r"\Delta m = m_{initial} - m_{final} > 0")
        ).arrange(DOWN, buff=0.3).next_to(einstein_formula, DOWN, buff=0.5)

        self.play(Write(einstein_formula))
        self.play(FadeIn(explanation, shift=UP))
        self.wait(2)

        self.play(FadeOut(fission_products), FadeOut(einstein_formula), FadeOut(explanation))
        self.wait(1)

        # 4. Example: Chain Reaction
        chain_title = Text("Chain Reaction", font_size=36).to_edge(UP)
        self.play(Transform(title, chain_title))

        nuclei = VGroup(*[
            Circle(radius=0.5, color=BLUE, fill_opacity=0.8) for _ in range(5)
        ]).arrange_in_grid(2, 3, buff=2.0).move_to(ORIGIN).shift(RIGHT * 0.5)
        self.play(FadeIn(nuclei))

        # First fission
        neutron_start = Circle(radius=0.1, color=GRAY, fill_opacity=1).move_to(LEFT * 6)
        self.play(neutron_start.animate.move_to(nuclei[0].get_center()))
        
        # Animate first split and new neutrons
        self.play(Indicate(nuclei[0], color=PURPLE))
        n1 = Circle(radius=0.1, color=GRAY, fill_opacity=1).move_to(nuclei[0].get_center())
        n2 = Circle(radius=0.1, color=GRAY, fill_opacity=1).move_to(nuclei[0].get_center())
        self.play(FadeOut(neutron_start), FadeIn(n1, n2))
        self.play(
            n1.animate.move_to(nuclei[1].get_center()),
            n2.animate.move_to(nuclei[3].get_center())
        )

        # Second wave of fissions
        self.play(Indicate(nuclei[1], color=PURPLE), Indicate(nuclei[3], color=PURPLE))
        n3 = Circle(radius=0.1, color=GRAY, fill_opacity=1).move_to(nuclei[1].get_center())
        n4 = Circle(radius=0.1, color=GRAY, fill_opacity=1).move_to(nuclei[3].get_center())
        self.play(FadeOut(n1, n2), FadeIn(n3, n4))
        self.play(
            n3.animate.move_to(nuclei[2].get_center()),
            n4.animate.move_to(nuclei[4].get_center())
        )
        
        # Final fissions
        self.play(Indicate(nuclei[2], color=PURPLE), Indicate(nuclei[4], color=PURPLE))
        self.wait(2)
        self.play(FadeOut(nuclei), FadeOut(n3, n4))

        # 5. Summary
        summary_title = Text("Summary", font_size=36).to_edge(UP)
        self.play(Transform(title, summary_title))

        summary_points = VGroup(
            Text("1. A heavy nucleus (like U-235) absorbs a neutron.", font_size=28),
            Text("2. It becomes unstable and splits into smaller nuclei.", font_size=28),
            Text("3. This releases a large amount of energy and more neutrons.", font_size=28),
            Text("4. Released neutrons can trigger a chain reaction.", font_size=28)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(ORIGIN)

        self.play(Write(summary_points))
        self.wait(3)

        self.play(FadeOut(title), FadeOut(summary_points))
        self.wait(2)