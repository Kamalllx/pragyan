# manim -pql rusting_of_iron.py RustingOfIron

from manim import *

class RustingOfIron(Scene):
    """
    An animation explaining the process of iron rusting for beginners.
    This scene covers the reactants, the overall chemical reaction,
    and a visual representation of rust formation.
    """
    def construct(self):
        # Set a consistent theme
        Text.set_default(font_size=36)
        MathTex.set_default(font_size=42)

        # --- SCENE 1: INTRODUCTION ---
        title = Text("The Rusting of Iron", font_size=48, weight=BOLD)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        self.wait(0.5)

        # --- SCENE 2: THE REACTANTS ---
        intro_text = Text("Rusting requires three things:").to_edge(UP)
        self.play(Write(intro_text))
        self.wait(1)

        # 1. Introduce Iron
        iron_bar = Rectangle(width=6, height=1.5, color=GRAY_C, fill_opacity=1)
        iron_label = MathTex(r"\text{1. Iron (Fe)}").next_to(iron_bar, DOWN)
        
        self.play(Create(iron_bar), run_time=2)
        self.play(Write(iron_label))
        self.wait(1.5)

        # 2. Introduce Oxygen and Water
        # Oxygen molecule (O2)
        o_atom = Circle(radius=0.2, color=RED, fill_opacity=1, stroke_color=WHITE)
        oxygen_molecule = VGroup(
            o_atom.copy().shift(LEFT*0.2),
            o_atom.copy().shift(RIGHT*0.2)
        ).move_to(UP*2 + LEFT*4)
        oxygen_label = MathTex(r"\text{2. Oxygen (O}_2\text{)}").next_to(oxygen_molecule, UP)

        # Water molecule (H2O)
        h_atom = Circle(radius=0.15, color=WHITE, fill_opacity=1, stroke_color=BLUE_E)
        water_molecule = VGroup(
            o_atom.copy().scale(1.2).set_color(BLUE_D), # Oxygen atom
            h_atom.copy().move_to(LEFT*0.3 + DOWN*0.3), # Hydrogen 1
            h_atom.copy().move_to(RIGHT*0.3 + DOWN*0.3)  # Hydrogen 2
        ).move_to(UP*2 + RIGHT*4)
        water_label = MathTex(r"\text{3. Water (H}_2\text{O)}").next_to(water_molecule, UP)

        self.play(
            FadeIn(oxygen_molecule, shift=DOWN),
            Write(oxygen_label)
        )
        self.wait(1)
        self.play(
            FadeIn(water_molecule, shift=DOWN),
            Write(water_label)
        )
        self.wait(2)

        # --- SCENE 3: THE CHEMICAL REACTION ---
        initial_scene = VGroup(intro_text, iron_bar, iron_label, oxygen_molecule, oxygen_label, water_molecule, water_label)
        self.play(FadeOut(initial_scene))
        self.wait(0.5)

        reaction_title = Text("The Overall Reaction").to_edge(UP)
        # Using a raw string for LaTeX is safe. F-strings are only needed when inserting variables.
        # The arrow shows water is a required medium for the reaction.
        equation = MathTex(
            r"4 \text{ Fe}", r" + ", r"3 \text{ O}_2",
            r"\xrightarrow{\hphantom{\text{Water}}}", # Placeholder for alignment
            r"2 \text{ Fe}_2\text{O}_3 \cdot n\text{H}_2\text{O}"
        ).scale(1.1)
        
        # Label for the catalyst/medium
        arrow_label = Text("Water", font_size=24).next_to(equation[3], UP, buff=0.1)
        
        # Labels for reactants and products
        reactants_label = Text("Reactants", font_size=28).next_to(equation[0:3], DOWN, buff=0.5)
        product_label = Text("Product (Rust)", font_size=28).next_to(equation[4], DOWN, buff=0.5)

        self.play(Write(reaction_title))
        self.play(Write(equation[0:3]), Write(reactants_label), run_time=2) # Reactants
        self.wait(1)
        self.play(Write(equation[3]), Write(arrow_label), run_time=1.5) # Arrow and catalyst
        self.wait(1)
        self.play(Write(equation[4]), Write(product_label), run_time=2) # Product
        self.wait(3)

        reaction_scene = VGroup(reaction_title, equation, arrow_label, reactants_label, product_label)
        self.play(FadeOut(reaction_scene))
        self.wait(0.5)

        # --- SCENE 4: ANIMATING THE RUSTING PROCESS ---
        process_title = Text("Rust forms on the iron's surface").to_edge(UP)
        iron_bar.to_edge(DOWN, buff=2)
        self.play(Write(process_title), FadeIn(iron_bar))
        self.wait(1)

        # Animate reactants moving towards the bar
        oxygen_molecule.move_to(LEFT*2 + UP*1)
        water_molecule.move_to(RIGHT*1 + UP*1)
        self.play(
            FadeIn(oxygen_molecule),
            FadeIn(water_molecule)
        )
        self.play(
            oxygen_molecule.animate.shift(DOWN*2),
            water_molecule.animate.shift(DOWN*2),
            run_time=2
        )
        self.wait(1)

        # Create rust patches
        rust_patch1 = Rectangle(
            width=1.5, height=1.5, color=MAROON_B, fill_opacity=1, stroke_width=0
        ).move_to(iron_bar.get_center() + LEFT*1.5)
        
        rust_label = Text("Rust (Iron Oxide)", font_size=28).next_to(rust_patch1, UP, buff=0.2)
        arrow = Arrow(rust_label.get_bottom(), rust_patch1.get_top(), buff=0.1, stroke_width=3, max_tip_length_to_length_ratio=0.15)

        # Animate the first rust patch appearing
        self.play(FadeOut(oxygen_molecule, water_molecule))
        self.play(FadeIn(rust_patch1), run_time=1.5)
        self.play(Write(rust_label), Create(arrow))
        self.wait(1)

        # Spread the rust
        process_title.become(Text("The rust spreads and weakens the iron").to_edge(UP))
        rust_patch2 = rust_patch1.copy().move_to(iron_bar.get_center() + RIGHT*0.5)
        rust_patch3 = rust_patch1.copy().set(width=2.0).move_to(iron_bar.get_center() + RIGHT*2.2)

        self.play(
            LaggedStart(
                FadeIn(rust_patch2),
                FadeIn(rust_patch3),
                lag_ratio=0.7
            ),
            run_time=3
        )
        self.wait(2)

        # --- SCENE 5: CONCLUSION ---
        final_group = VGroup(process_title, iron_bar, rust_patch1, rust_patch2, rust_patch3, rust_label, arrow)
        self.play(FadeOut(final_group))
        self.wait(0.5)

        conclusion_text = Text(
            "Rusting is an oxidation process that corrodes iron,\n"
            "turning it into a flaky, brittle substance.",
            text_alignment=CENTER,
            line_spacing=1.5,
            font_size=32
        ).scale(0.9)
        
        self.play(Write(conclusion_text))
        self.wait(4)

        # Final wait time before the scene ends
        self.wait(2)