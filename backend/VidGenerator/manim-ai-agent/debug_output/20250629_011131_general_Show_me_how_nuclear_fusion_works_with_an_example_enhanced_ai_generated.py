from manim import *

class NuclearFusionScene(Scene):
    """
    An intermediate-level animation explaining the process of nuclear fusion
    using the Deuterium-Tritium (D-T) reaction as an example.
    """
    def construct(self):
        # Set a consistent color scheme
        proton_color = RED_C
        neutron_color = LIGHT_GREY
        electron_color = BLUE_C
        energy_color = YELLOW

        # --- Helper function to create a nucleus ---
        def create_nucleus(protons, neutrons, radius=0.6):
            """Creates a VGroup representing an atomic nucleus."""
            nucleus_circle = Circle(radius=radius, color=WHITE, fill_opacity=0.2)
            
            # Create protons and neutrons
            p_dots = VGroup(*[Dot(color=proton_color) for _ in range(protons)])
            n_dots = VGroup(*[Dot(color=neutron_color) for _ in range(neutrons)])
            
            # Arrange them inside the circle
            if protons > 0 and neutrons > 0:
                particles = VGroup(p_dots, n_dots).arrange_in_grid(rows=2, cols=max(protons, neutrons), buff=0.1)
            elif protons > 0:
                particles = p_dots.arrange(RIGHT, buff=0.1)
            else:
                particles = n_dots.arrange(RIGHT, buff=0.1)
            
            particles.move_to(nucleus_circle.get_center()).scale(0.5)
            
            return VGroup(nucleus_circle, particles)

        # --- 1. Title Introduction ---
        title = Text("How Nuclear Fusion Works", font_size=48)
        title.to_edge(UP)
        subtitle = Text("The Deuterium-Tritium (D-T) Reaction", font_size=32)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=DOWN))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        self.wait(0.5)

        # --- 2. Introduce Reactants ---
        reactants_title = Text("The Ingredients: Isotopes of Hydrogen", font_size=36).to_edge(UP)
        self.play(Write(reactants_title))
        self.wait(1)

        # Create Deuterium
        deuterium = create_nucleus(1, 1)
        deuterium_label = MathTex(r"\text{Deuterium } (^2\text{H})", font_size=32)
        deuterium_group = VGroup(deuterium, deuterium_label).arrange(DOWN, buff=0.3)

        # Create Tritium
        tritium = create_nucleus(1, 2)
        tritium_label = MathTex(r"\text{Tritium } (^3\text{H})", font_size=32)
        tritium_group = VGroup(tritium, tritium_label).arrange(DOWN, buff=0.3)

        # Arrange reactants on screen
        reactants_group = VGroup(deuterium_group, tritium_group).arrange(RIGHT, buff=2.0)
        reactants_group.move_to(ORIGIN).shift(UP * 0.5)
        
        self.play(FadeIn(reactants_group, shift=UP))
        self.wait(2)

        # --- 3. Explain Conditions for Fusion ---
        conditions_text = Text("Fusion requires extreme heat and pressure", font_size=28)
        conditions_text.next_to(reactants_group, DOWN, buff=1.5)
        
        self.play(Write(conditions_text))
        self.play(
            Indicate(deuterium, scale_factor=1.2),
            Indicate(tritium, scale_factor=1.2)
        )
        self.wait(2)
        
        self.play(FadeOut(reactants_title), FadeOut(conditions_text))
        self.wait(0.5)

        # --- 4. The Fusion Reaction ---
        # Animate reactants moving to the center
        plus_sign = MathTex("+", font_size=48).move_to(reactants_group.get_center())
        self.play(
            deuterium_group.animate.shift(LEFT * 2),
            tritium_group.animate.shift(RIGHT * 2)
        )
        self.play(Write(plus_sign))
        self.wait(1)

        # The collision
        target_pos = ORIGIN
        self.play(
            deuterium_group.animate.move_to(target_pos),
            tritium_group.animate.move_to(target_pos),
            FadeOut(plus_sign)
        )
        
        # Create a flash for the fusion event
        fusion_flash = Flash(target_pos, color=energy_color, line_length=1.0, num_lines=20, flash_radius=1.5)
        self.play(fusion_flash)
        self.play(FadeOut(deuterium_group), FadeOut(tritium_group))
        self.wait(0.5)

        # --- 5. Show the Products ---
        products_title = Text("The Products: Helium and a Neutron", font_size=36).to_edge(UP)
        self.play(Write(products_title))

        # Create Helium (Alpha Particle)
        helium = create_nucleus(2, 2, radius=0.7)
        helium_label = MathTex(r"\text{Helium } (^4\text{He})", font_size=32)
        helium_group = VGroup(helium, helium_label).arrange(DOWN, buff=0.3)

        # Create Neutron
        neutron = create_nucleus(0, 1, radius=0.3)
        neutron_label = MathTex(r"\text{Neutron (n)}", font_size=32)
        neutron_group = VGroup(neutron, neutron_label).arrange(DOWN, buff=0.3)

        # Arrange products
        products_group = VGroup(helium_group, neutron_group).arrange(RIGHT, buff=2.0)
        products_group.move_to(ORIGIN).shift(UP * 0.5)
        
        self.play(FadeIn(products_group))
        self.play(
            helium_group.animate.shift(LEFT * 2),
            neutron_group.animate.shift(RIGHT * 3) # Neutron moves faster
        )
        self.wait(2)

        # --- 6. Energy Release and Equation ---
        energy_text = Text("Mass is converted into a huge amount of energy!", font_size=28, color=energy_color)
        energy_text.to_edge(DOWN, buff=1.0)
        
        # The full reaction equation
        reaction_equation = MathTex(
            r"^{2}\text{H} + ^{3}\text{H} \rightarrow ^{4}\text{He} + \text{n} + 17.6 \text{ MeV}",
            font_size=40
        )
        reaction_equation.next_to(energy_text, UP, buff=0.5)

        self.play(Write(energy_text))
        self.play(Write(reaction_equation))
        self.wait(3)

        # --- 7. Final Summary ---
        final_elements = VGroup(products_title, products_group, energy_text, reaction_equation)
        self.play(FadeOut(final_elements))
        self.wait(0.5)

        summary_title = Text("In Summary", font_size=48).to_edge(UP)
        summary_points = VGroup(
            Text("1. Light nuclei (like H-2 and H-3) are forced together.", font_size=28),
            Text("2. They fuse to form a heavier nucleus (Helium-4).", font_size=28),
            Text("3. A tiny amount of mass is lost and released as energy.", font_size=28),
            Text("This process powers the sun and is the goal for clean energy.", font_size=28, color=YELLOW)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        
        summary_group = VGroup(summary_title, summary_points).arrange(DOWN, buff=1.0)
        summary_group.move_to(ORIGIN)

        self.play(Write(summary_group))
        self.wait(4)
        self.play(FadeOut(summary_group))
        self.wait(2)