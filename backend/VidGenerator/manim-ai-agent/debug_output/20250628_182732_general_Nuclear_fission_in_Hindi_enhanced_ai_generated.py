# Manim v0.19.0
from manim import *

class NuclearFissionHindi(Scene):
    def construct(self):
        # Set a background color
        self.camera.background_color = "#0d1b2a"

        # 1. Title Introduction
        title = Text(
            "नाभिकीय विखंडन", 
            font="Nirmala UI", 
            weight=BOLD, 
            font_size=48
        )
        title.to_edge(UP)
        
        underline = Line(
            title.get_left() + DOWN * 0.2, 
            title.get_right() + DOWN * 0.2, 
            color=YELLOW
        )

        self.play(Write(title))
        self.play(Create(underline))
        self.wait(1)

        # 2. Main educational content: The Fission Process
        
        # Introduction Text
        intro_text = Text(
            "यह एक प्रक्रिया है जिसमें एक भारी परमाणु का नाभिक\nदो या दो से अधिक हल्के नाभिकों में टूट जाता है।",
            font="Nirmala UI",
            font_size=28,
            line_spacing=0.8
        ).next_to(underline, DOWN, buff=0.8)

        self.play(FadeIn(intro_text, shift=DOWN))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # Create Uranium-235 Nucleus
        nucleus_center = ORIGIN + DOWN * 0.5
        uranium_nucleus = Circle(radius=1.2, color=BLUE_D, fill_opacity=0.6).move_to(nucleus_center)
        
        protons = VGroup(*[
            Circle(radius=0.1, color=RED, fill_opacity=1).move_to(
                nucleus_center + np.array([
                    0.8 * np.cos(i * PI / 8), 
                    0.8 * np.sin(i * PI / 8), 
                    0
                ])
            ) for i in range(16)
        ])
        
        neutrons_inside = VGroup(*[
            Circle(radius=0.1, color=WHITE, fill_opacity=1).move_to(
                nucleus_center + np.array([
                    0.5 * np.cos(i * PI / 6), 
                    0.5 * np.sin(i * PI / 6), 
                    0
                ])
            ) for i in range(12)
        ])
        
        uranium_group = VGroup(uranium_nucleus, protons, neutrons_inside)
        uranium_label = MathTex("^{235}U").next_to(uranium_group, DOWN, buff=0.5)

        self.play(Create(uranium_group), Write(uranium_label))
        self.wait(1)

        # Incoming Neutron
        incoming_neutron = Circle(radius=0.15, color=WHITE, fill_opacity=1).move_to(LEFT * 5)
        neutron_label = Text("न्यूट्रॉन", font="Nirmala UI", font_size=24).next_to(incoming_neutron, UP, buff=0.2)
        
        self.play(FadeIn(incoming_neutron), Write(neutron_label))
        self.wait(0.5)

        # Neutron hits the nucleus
        self.play(
            neutron_label.animate.shift(RIGHT * 3.5),
            incoming_neutron.animate.move_to(uranium_nucleus.get_center() + LEFT * 1.2)
        )
        self.play(FadeOut(neutron_label))
        self.play(Transform(incoming_neutron, Circle(radius=0.1, color=WHITE).move_to(uranium_nucleus.get_center())))
        
        # Unstable Nucleus
        unstable_nucleus_group = VGroup(uranium_group, incoming_neutron)
        unstable_label = MathTex("^{236}U^* \ (\text{अस्थिर})").next_to(unstable_nucleus_group, DOWN, buff=0.5)
        self.play(Transform(uranium_label, unstable_label), Wiggle(unstable_nucleus_group, n_wiggles=8, scale_value=1.1))
        self.wait(1)

        # Fission happens
        self.play(FadeOut(unstable_nucleus_group, uranium_label))

        # Fission Products
        fragment1 = VGroup(
            Circle(radius=0.7, color=GREEN_D, fill_opacity=0.6),
            *[Circle(radius=0.08, color=RED).move_to(0.3*np.random.randn(3)) for _ in range(5)],
            *[Circle(radius=0.08, color=WHITE).move_to(0.3*np.random.randn(3)) for _ in range(5)]
        ).move_to(LEFT * 2)
        
        fragment2 = VGroup(
            Circle(radius=0.6, color=PURPLE_D, fill_opacity=0.6),
            *[Circle(radius=0.08, color=RED).move_to(0.25*np.random.randn(3)) for _ in range(4)],
            *[Circle(radius=0.08, color=WHITE).move_to(0.25*np.random.randn(3)) for _ in range(4)]
        ).move_to(RIGHT * 2)

        new_neutrons = VGroup(
            Circle(radius=0.1, color=WHITE).move_to(UP * 1.5),
            Circle(radius=0.1, color=WHITE).move_to(RIGHT * 1.5 + DOWN * 1.5),
            Circle(radius=0.1, color=WHITE).move_to(LEFT * 1.5 + DOWN * 1.5)
        )

        energy_flash = Flash(ORIGIN, line_length=1, num_lines=20, color=YELLOW, flash_radius=3)
        energy_label = Text("ऊर्जा!", font="Nirmala UI", font_size=36, color=YELLOW).next_to(energy_flash, UP, buff=0.5)

        self.play(
            FadeIn(fragment1, shift=LEFT),
            FadeIn(fragment2, shift=RIGHT),
            FadeIn(new_neutrons, scale=2),
            energy_flash,
            Write(energy_label)
        )
        self.wait(1)
        
        # Animate products moving away
        self.play(
            fragment1.animate.shift(LEFT * 2),
            fragment2.animate.shift(RIGHT * 2),
            new_neutrons[0].animate.shift(UP * 2),
            new_neutrons[1].animate.shift(DOWN * 1.5 + RIGHT * 1.5),
            new_neutrons[2].animate.shift(DOWN * 1.5 + LEFT * 1.5),
            FadeOut(energy_label)
        )
        self.wait(2)

        # Clear the screen for the next part
        self.play(FadeOut(VGroup(fragment1, fragment2, new_neutrons, title, underline)))
        
        # 3. Chain Reaction
        chain_title = Text("श्रृंखला अभिक्रिया", font="Nirmala UI", weight=BOLD, font_size=48).to_edge(UP)
        self.play(Write(chain_title))
        self.wait(1)

        # Create a grid of nuclei
        nuclei = VGroup()
        positions = [
            LEFT * 4 + UP * 1, LEFT * 4 + DOWN * 2,
            ORIGIN + UP * 2, ORIGIN, ORIGIN + DOWN * 2.5,
            RIGHT * 4 + UP * 1, RIGHT * 4 + DOWN * 2
        ]
        for pos in positions:
            nucleus = VGroup(
                Circle(radius=0.6, color=BLUE_D, fill_opacity=0.6),
                *[Circle(radius=0.05, color=RED).move_to(0.2*np.random.randn(3)) for _ in range(3)],
                *[Circle(radius=0.05, color=WHITE).move_to(0.2*np.random.randn(3)) for _ in range(3)]
            ).move_to(pos)
            nuclei.add(nucleus)
        
        self.play(FadeIn(nuclei, lag_ratio=0.1))
        self.wait(1)

        # Start the chain reaction
        initial_neutron = Circle(radius=0.1, color=WHITE).move_to(LEFT * 6.5 + UP * 1)
        self.play(FadeIn(initial_neutron))
        
        # First fission
        self.play(initial_neutron.animate.move_to(nuclei[0].get_center()))
        
        fission_flash1 = Flash(nuclei[0].get_center(), color=YELLOW, flash_radius=1.5)
        neutron1_1 = Circle(radius=0.1, color=WHITE).move_to(nuclei[0].get_center())
        neutron1_2 = Circle(radius=0.1, color=WHITE).move_to(nuclei[0].get_center())
        self.play(fission_flash1, FadeOut(nuclei[0], initial_neutron))
        self.play(
            neutron1_1.animate.move_to(nuclei[2].get_center()),
            neutron1_2.animate.move_to(nuclei[4].get_center())
        )

        # Second wave of fissions
        fission_flash2 = Flash(nuclei[2].get_center(), color=YELLOW, flash_radius=1.5)
        fission_flash3 = Flash(nuclei[4].get_center(), color=YELLOW, flash_radius=1.5)
        neutron2_1 = Circle(radius=0.1, color=WHITE).move_to(nuclei[2].get_center())
        neutron3_1 = Circle(radius=0.1, color=WHITE).move_to(nuclei[4].get_center())
        self.play(
            fission_flash2, fission_flash3,
            FadeOut(nuclei[2], nuclei[4], neutron1_1, neutron1_2)
        )
        self.play(
            neutron2_1.animate.move_to(nuclei[5].get_center()),
            neutron3_1.animate.move_to(nuclei[6].get_center())
        )

        # Third wave
        fission_flash4 = Flash(nuclei[5].get_center(), color=YELLOW, flash_radius=1.5)
        fission_flash5 = Flash(nuclei[6].get_center(), color=YELLOW, flash_radius=1.5)
        self.play(
            fission_flash4, fission_flash5,
            FadeOut(nuclei[5], nuclei[6], neutron2_1, neutron3_1)
        )
        self.wait(2)

        # Clear the screen
        self.play(FadeOut(VGroup(chain_title, nuclei)))

        # 4. Energy Release Formula (E=mc^2)
        formula_title = Text("ऊर्जा का स्रोत", font="Nirmala UI", weight=BOLD, font_size=48).to_edge(UP)
        self.play(Write(formula_title))

        formula = MathTex("E = mc^2", font_size=72).move_to(ORIGIN)
        
        explanation = VGroup(
            Text("E = ऊर्जा (Energy)", font="Nirmala UI", font_size=24),
            Text("m = द्रव्यमान में कमी (mass defect)", font="Nirmala UI", font_size=24),
            Text("c = प्रकाश की गति (speed of light)", font="Nirmala UI", font_size=24)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(formula, DOWN, buff=1.0)

        self.play(Write(formula))
        self.wait(1)
        self.play(FadeIn(explanation, shift=UP))
        
        box = SurroundingRectangle(formula, buff=0.5, color=ORANGE)
        self.play(Create(box))
        self.wait(3)

        # 5. Summary
        self.play(FadeOut(VGroup(formula_title, formula, explanation, box)))
        
        summary_title = Text("सारांश", font="Nirmala UI", weight=BOLD, font_size=48).to_edge(UP)
        
        summary_points = VGroup(
            Text("1. भारी नाभिक पर न्यूट्रॉन की बमबारी होती है।", font="Nirmala UI", font_size=28),
            Text("2. नाभिक दो छोटे नाभिकों में टूट जाता है।", font="Nirmala UI", font_size=28),
            Text("3. नए न्यूट्रॉन और भारी मात्रा में ऊर्जा निकलती है।", font="Nirmala UI", font_size=28),
            Text("4. यह प्रक्रिया एक श्रृंखला अभिक्रिया को जन्म दे सकती है।", font="Nirmala UI", font_size=28)
        ).arrange(DOWN, buff=0.6, aligned_edge=LEFT).next_to(summary_title, DOWN, buff=0.8)
        
        self.play(Write(summary_title))
        self.play(FadeIn(summary_points, lag_ratio=0.5, shift=UP))

        self.wait(4)
        
        self.play(FadeOut(VGroup(summary_title, summary_points)))
        
        self.wait(2)