from manim import *

# Use a font that supports Hindi characters, like "Nirmala UI"
# If you don't have it, you can use other fonts like "Arial Unicode MS"
# or install a Devanagari script font.
config.font = "Nirmala UI"

class NuclearFusionHindi(Scene):
    """
    An intermediate-level animation explaining nuclear fusion in Hindi,
    using the Deuterium-Tritium reaction as an example.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("नाभिकीय संलयन (Nuclear Fusion)", font_size=48)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.wait(1)

        # 2. Main educational content with visual demonstrations
        intro_text = Text(
            "यह वह प्रक्रिया है जिसमें दो हल्के परमाणु नाभिक मिलकर\nएक भारी नाभिक बनाते हैं, और भारी मात्रा में ऊर्जा छोड़ते हैं।",
            font_size=28,
            text_align="CENTER"
        ).next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))
        self.wait(0.5)

        # 3. Key concepts with clear explanations (Reactants)
        # Create Deuterium (1 proton, 1 neutron)
        proton_d = Circle(radius=0.15, color=RED, fill_opacity=1).set_z_index(1)
        neutron_d = Circle(radius=0.15, color=GRAY, fill_opacity=1).set_z_index(1)
        deuterium_core = VGroup(proton_d, neutron_d).arrange(RIGHT, buff=0.05)
        deuterium_atom = VGroup(Circle(radius=0.5, color=BLUE), deuterium_core).move_to(LEFT * 4)
        deuterium_label = MathTex(r"^{2}_{1}\text{H}", r"\\ \text{ड्यूटेरियम}").next_to(deuterium_atom, DOWN, buff=0.3)

        # Create Tritium (1 proton, 2 neutrons)
        proton_t = Circle(radius=0.15, color=RED, fill_opacity=1).set_z_index(1)
        neutron_t1 = Circle(radius=0.15, color=GRAY, fill_opacity=1).set_z_index(1)
        neutron_t2 = Circle(radius=0.15, color=GRAY, fill_opacity=1).set_z_index(1)
        tritium_core = VGroup(proton_t, neutron_t1, neutron_t2).arrange(buff=0.05)
        tritium_atom = VGroup(Circle(radius=0.6, color=GREEN), tritium_core).move_to(LEFT * 1)
        tritium_label = MathTex(r"^{3}_{1}\text{H}", r"\\ \text{ट्रिटियम}").next_to(tritium_atom, DOWN, buff=0.3)

        reactants = VGroup(deuterium_atom, deuterium_label, tritium_atom, tritium_label)
        
        self.play(
            Create(deuterium_atom),
            Write(deuterium_label)
        )
        self.wait(0.5)
        self.play(
            Create(tritium_atom),
            Write(tritium_label)
        )
        self.wait(1)

        # Show conditions for fusion
        conditions_text = Text(
            "अत्यधिक तापमान और दबाव",
            font_size=24,
            color=YELLOW
        ).move_to(UP * 2)
        arrow1 = Arrow(conditions_text.get_bottom(), deuterium_atom.get_top(), buff=0.2, color=YELLOW)
        arrow2 = Arrow(conditions_text.get_bottom(), tritium_atom.get_top(), buff=0.2, color=YELLOW)
        conditions = VGroup(conditions_text, arrow1, arrow2)

        self.play(Write(conditions))
        self.wait(1)

        # Animate fusion
        self.play(
            deuterium_atom.animate.move_to(ORIGIN),
            tritium_atom.animate.move_to(ORIGIN),
            FadeOut(conditions),
            FadeOut(deuterium_label),
            FadeOut(tritium_label)
        )

        # Create a flash for the fusion reaction
        flash = Circle(radius=1.5, color=YELLOW, fill_opacity=0.8).move_to(ORIGIN)
        self.play(FadeOut(deuterium_atom, tritium_atom), FadeIn(flash, scale=0.2))
        self.play(FadeOut(flash))
        self.wait(0.5)

        # 4. Examples or applications (Products)
        # Create Helium (2 protons, 2 neutrons)
        helium_core = VGroup(
            Circle(radius=0.15, color=RED, fill_opacity=1),
            Circle(radius=0.15, color=RED, fill_opacity=1),
            Circle(radius=0.15, color=GRAY, fill_opacity=1),
            Circle(radius=0.15, color=GRAY, fill_opacity=1)
        ).arrange_in_grid(2, 2, buff=0.05).set_z_index(1)
        helium_atom = VGroup(Circle(radius=0.7, color=ORANGE), helium_core)
        helium_label = MathTex(r"^{4}_{2}\text{He}", r"\\ \text{हीलियम}").next_to(helium_atom, DOWN, buff=0.3)
        helium_group = VGroup(helium_atom, helium_label).move_to(LEFT * 2.5)

        # Create a free neutron
        free_neutron = Circle(radius=0.15, color=GRAY, fill_opacity=1)
        neutron_label = MathTex(r"n", r"\\ \text{न्यूट्रॉन}").next_to(free_neutron, DOWN, buff=0.3)
        neutron_group = VGroup(free_neutron, neutron_label).move_to(RIGHT * 1.5)

        # Show energy release
        energy_label = MathTex(r"+\text{ ऊर्जा (Energy)}", color=YELLOW, font_size=48).move_to(RIGHT * 4.5)

        # Animate products appearing
        self.play(
            FadeIn(helium_group, shift=LEFT),
            FadeIn(neutron_group, shift=RIGHT),
        )
        self.play(Write(energy_label))
        self.wait(2)

        # Group all products and fade them out
        products = VGroup(helium_group, neutron_group, energy_label)
        self.play(FadeOut(products))
        self.wait(0.5)

        # Display the full reaction equation
        reaction_equation = MathTex(
            r"^{2}_{1}\text{H} + ^{3}_{1}\text{H} \rightarrow ^{4}_{2}\text{He} + n + 17.6 \text{ MeV}",
            font_size=42
        ).move_to(ORIGIN)
        self.play(Write(reaction_equation))
        self.wait(2)
        self.play(FadeOut(reaction_equation))
        self.wait(0.5)

        # 5. Summary or conclusion (E=mc^2)
        explanation_title = Text("ऊर्जा का स्रोत: द्रव्यमान-ऊर्जा तुल्यता", font_size=36).move_to(UP * 2.5)
        
        mass_defect_text = Text(
            "उत्पादों का कुल द्रव्यमान अभिकारकों से थोड़ा कम होता है।\nयह 'खोया हुआ' द्रव्यमान ऊर्जा में बदल जाता है।",
            font_size=28,
            text_align="CENTER"
        ).next_to(explanation_title, DOWN, buff=0.8)

        einstein_eq = MathTex("E = mc^2", font_size=72, color=YELLOW).next_to(mass_defect_text, DOWN, buff=1.0)
        box = SurroundingRectangle(einstein_eq, buff=0.4, color=BLUE)

        self.play(Write(explanation_title))
        self.play(FadeIn(mass_defect_text, shift=DOWN))
        self.wait(1)
        self.play(Write(einstein_eq))
        self.play(Create(box))
        self.wait(3)

        # Final scene
        final_group = VGroup(explanation_title, mass_defect_text, einstein_eq, box)
        self.play(FadeOut(final_group, title))

        conclusion_text = Text(
            "यह वही प्रक्रिया है जो सूर्य और तारों को शक्ति देती है।",
            font_size=36
        ).move_to(ORIGIN)
        sun = Circle(radius=1, color=YELLOW, fill_opacity=0.8).move_to(ORIGIN)
        
        self.play(FadeIn(sun))
        self.play(Transform(sun, conclusion_text))
        
        self.wait(3)