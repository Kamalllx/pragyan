# Manim v0.19.0

from manim import *

class RustingOfIron(Scene):
    def construct(self):
        # Define colors for consistency
        iron_color = GRAY_BROWN
        water_color = BLUE_C
        oxygen_color = RED
        rust_color = RED_BROWN
        electron_color = YELLOW

        # --- 1. Title Introduction ---
        title = Text("The Chemistry of Rusting", font_size=60)
        subtitle = Text("An Electrochemical Process", font_size=40).next_to(title, DOWN, buff=0.3)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=DOWN))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        self.wait(1)

        # --- 2. Main Educational Content - What is Rusting? ---
        intro_text = Text("Rusting is the corrosion of iron when it is exposed to two key ingredients:", font_size=36).to_edge(UP)
        
        # Create visual representations of the reactants
        oxygen_molecule = VGroup(
            Circle(radius=0.3, color=oxygen_color, fill_opacity=1),
            Circle(radius=0.3, color=oxygen_color, fill_opacity=1)
        ).arrange(RIGHT, buff=0)
        oxygen_label = MathTex("O_2", " (Oxygen)").next_to(oxygen_molecule, DOWN)

        water_molecule = VGroup(
            Circle(radius=0.3, color=oxygen_color, fill_opacity=1),
            Circle(radius=0.2, color=WHITE, fill_opacity=1).shift(0.4*UP + 0.3*LEFT),
            Circle(radius=0.2, color=WHITE, fill_opacity=1).shift(0.4*UP + 0.3*RIGHT)
        )
        water_label = MathTex("H_2O", " (Water)").next_to(water_molecule, DOWN)

        reactants_group = VGroup(oxygen_molecule, water_molecule).arrange(RIGHT, buff=2).center()
        labels_group = VGroup(oxygen_label, water_label).arrange(RIGHT, buff=1.3).next_to(reactants_group, DOWN, buff=0.5)

        self.play(Write(intro_text))
        self.play(FadeIn(reactants_group, shift=UP), FadeIn(labels_group, shift=UP))
        self.wait(3)
        self.play(FadeOut(intro_text), FadeOut(reactants_group), FadeOut(labels_group))
        self.wait(1)

        # --- 3. Visual Demonstration of the Process ---
        # Setup the scene: an iron bar with a water droplet
        iron_bar = Rectangle(width=12, height=1.5, color=iron_color, fill_opacity=1).to_edge(DOWN, buff=1)
        iron_label = Text("Iron (Fe) Surface").scale(0.7).next_to(iron_bar, DOWN)
        water_droplet = Ellipse(width=6, height=3, color=water_color, fill_opacity=0.6).move_to(iron_bar.get_center() + UP*1.4)
        water_droplet_label = Text("Water Droplet").scale(0.7).next_to(water_droplet, UP)

        self.play(Create(iron_bar), Write(iron_label))
        self.play(FadeIn(water_droplet), Write(water_droplet_label))
        self.wait(1)

        # Step 1: Anode - Iron Oxidation
        anode_pos = iron_bar.get_center() + LEFT*2
        anode_label = Text("Anode: Iron loses electrons (Oxidation)", font_size=32).to_edge(UP)
        
        fe_atom = Circle(radius=0.2, color=iron_color, fill_opacity=1).move_to(anode_pos)
        fe_label = MathTex("Fe").next_to(fe_atom, UP)
        
        self.play(Write(anode_label))
        self.play(FadeIn(fe_atom), FadeIn(fe_label))
        self.wait(1)

        # Animate oxidation
        fe_ion = Circle(radius=0.2, color=ORANGE, fill_opacity=1).move_to(anode_pos)
        fe_ion_label = MathTex("Fe^{2+}").next_to(fe_ion, UP)
        electron1 = Circle(radius=0.08, color=electron_color, fill_opacity=1).move_to(anode_pos)
        electron2 = Circle(radius=0.08, color=electron_color, fill_opacity=1).move_to(anode_pos)
        
        oxidation_eq = MathTex("Fe(s) \\rightarrow Fe^{2+}(aq) + 2e^-").next_to(anode_label, DOWN, buff=0.5)

        self.play(
            Transform(fe_atom, fe_ion),
            Transform(fe_label, fe_ion_label),
            electron1.animate.shift(LEFT*0.5 + UP*0.3),
            electron2.animate.shift(LEFT*0.5 + DOWN*0.3)
        )
        self.play(Write(oxidation_eq))
        self.wait(2)

        # Step 2: Cathode - Oxygen Reduction
        cathode_pos = iron_bar.get_center() + RIGHT*2
        self.play(FadeOut(anode_label), FadeOut(oxidation_eq))
        cathode_label = Text("Cathode: Oxygen gains electrons (Reduction)", font_size=32).to_edge(UP)
        self.play(Write(cathode_label))

        # Electrons move through the iron
        path = ArcBetweenPoints(electron1.get_center(), cathode_pos + LEFT*0.5, angle=-PI/2)
        path2 = ArcBetweenPoints(electron2.get_center(), cathode_pos + LEFT*0.5, angle=PI/2)
        self.play(
            MoveAlongPath(electron1, path),
            MoveAlongPath(electron2, path2),
            run_time=2
        )
        self.wait(0.5)

        # Oxygen and water at the cathode
        o2_cathode = oxygen_molecule.copy().scale(0.7).move_to(cathode_pos + UP*0.5)
        h2o_cathode = water_molecule.copy().scale(0.5).move_to(cathode_pos + DOWN*0.5)
        self.play(FadeIn(o2_cathode), FadeIn(h2o_cathode))
        self.wait(1)

        # Animate reduction
        reduction_eq = MathTex("O_2(g) + 2H_2O(l) + 4e^- \\rightarrow 4OH^-(aq)").next_to(cathode_label, DOWN, buff=0.5)
        hydroxide_ions = VGroup(*[MathTex("OH^-", color=PURPLE).scale(0.8) for _ in range(4)]).arrange(RIGHT, buff=0.2).move_to(cathode_pos)

        self.play(
            FadeOut(electron1), FadeOut(electron2),
            FadeOut(o2_cathode), FadeOut(h2o_cathode),
            FadeIn(hydroxide_ions)
        )
        self.play(Write(reduction_eq))
        self.wait(3)

        # Step 3: Forming Rust
        self.play(FadeOut(cathode_label), FadeOut(reduction_eq))
        rust_formation_label = Text("Rust Formation", font_size=32).to_edge(UP)
        self.play(Write(rust_formation_label))

        # Ions move and react
        self.play(
            fe_atom.animate.move_to(iron_bar.get_center()),
            fe_label.animate.move_to(iron_bar.get_center() + UP*0.5),
            hydroxide_ions.animate.move_to(iron_bar.get_center() + DOWN*0.2)
        )
        self.wait(1)

        # Create rust visually
        rust_spot = VGroup(*[
            Polygon(
                *[np.random.rand(3) * 0.3 for _ in range(7)],
                color=rust_color, fill_opacity=0.8, stroke_width=0
            ).shift(iron_bar.get_center() + (np.random.rand(3)-0.5)*0.5)
            for _ in range(20)
        ])
        
        rust_formula = MathTex("Fe_2O_3 \\cdot nH_2O", color=rust_color).scale(1.2).next_to(rust_spot, UP, buff=0.5)
        rust_text_label = Text("Rust", color=rust_color).next_to(rust_formula, UP)

        self.play(
            FadeOut(fe_atom), FadeOut(fe_label), FadeOut(hydroxide_ions),
            FadeIn(rust_spot, scale=0.5)
        )
        self.play(Write(rust_formula), Write(rust_text_label))
        self.wait(3)

        # --- 4. Overall Reaction and Prevention ---
        # Clear the scene for the summary equation
        all_objects = VGroup(*self.mobjects)
        self.play(FadeOut(all_objects))
        self.wait(1)

        overall_title = Text("Overall Reaction for Rusting", font_size=48).to_edge(UP)
        overall_eq = MathTex("4Fe(s) + 3O_2(g) + 2nH_2O(l) \\rightarrow 2Fe_2O_3 \\cdot nH_2O(s)", font_size=48).center()
        
        self.play(Write(overall_title))
        self.play(Write(overall_eq))
        self.wait(4)
        self.play(FadeOut(overall_title), FadeOut(overall_eq))
        self.wait(1)

        # --- 5. Prevention Methods ---
        prevention_title = Text("How to Prevent Rusting?", font_size=48).to_edge(UP)
        self.play(Write(prevention_title))

        # Method 1: Painting
        iron_bar1 = Rectangle(width=5, height=1, color=iron_color, fill_opacity=1).shift(LEFT*3)
        iron_label1 = Text("Iron").scale(0.7).next_to(iron_bar1, DOWN)
        paint_layer = Rectangle(width=5.2, height=1.2, color=GREEN, fill_opacity=0.7).move_to(iron_bar1.get_center())
        paint_label = Text("1. Painting").scale(0.8).next_to(iron_bar1, UP, buff=0.5)

        self.play(Create(iron_bar1), Write(iron_label1), Write(paint_label))
        self.play(Create(paint_layer))
        self.wait(1.5)

        # Method 2: Galvanizing
        iron_bar2 = Rectangle(width=5, height=1, color=iron_color, fill_opacity=1).shift(RIGHT*3)
        iron_label2 = Text("Iron").scale(0.7).next_to(iron_bar2, DOWN)
        zinc_layer = Rectangle(width=5.2, height=1.2, color=LIGHT_GRAY, fill_opacity=0.9).move_to(iron_bar2.get_center())
        zinc_label_text = Text("Zinc (Zn) Coating").scale(0.6).move_to(zinc_layer.get_center())
        galvanizing_label = Text("2. Galvanizing").scale(0.8).next_to(iron_bar2, UP, buff=0.5)

        self.play(Create(iron_bar2), Write(iron_label2), Write(galvanizing_label))
        self.play(Create(zinc_layer), Write(zinc_label_text))
        self.wait(3)

        # --- 6. Summary ---
        all_objects = VGroup(*self.mobjects)
        self.play(FadeOut(all_objects))
        self.wait(1)

        summary_title = Text("Key Concepts Summary", font_size=48).to_edge(UP)
        self.play(Write(summary_title))

        summary_points = BulletedList(
            "Rusting requires: Iron, Oxygen, and Water.",
            "It is an electrochemical process involving an anode and a cathode.",
            "Rust is hydrated iron(III) oxide (Fe₂O₃·nH₂O).",
            "Prevention methods like painting create a protective barrier.",
            font_size=36
        ).next_to(summary_title, DOWN, buff=0.7).shift(LEFT*0.5)

        self.play(Write(summary_points), run_time=5)
        self.wait(4)

        # --- 7. Safety Note ---
        safety_text = Text(
            "Safety Note: Rusting experiments can involve chemicals. Always use proper safety gear.",
            font_size=24,
            color=YELLOW
        ).to_edge(DOWN, buff=0.5)
        
        self.play(FadeIn(safety_text))
        self.wait(2)