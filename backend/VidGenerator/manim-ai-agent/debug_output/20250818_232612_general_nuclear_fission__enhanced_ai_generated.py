from manim import *

class NuclearFission(Scene):
    def construct(self):
        # 1. Title Introduction
        title = Text("Nuclear Fission", font_size=48)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Helper function to create a nucleus
        def create_nucleus(protons, neutrons, radius, p_color=RED, n_color=GRAY):
            nucleus_group = VGroup()
            center_circle = Circle(radius=radius, color=BLUE, fill_opacity=0.3)
            nucleus_group.add(center_circle)
            
            # Add protons and neutrons inside
            for _ in range(protons):
                p = Circle(radius=0.1, color=p_color, fill_opacity=1).move_to(
                    center_circle.get_center() + np.random.uniform(-radius*0.6, radius*0.6, 3)
                )
                nucleus_group.add(p)
            for _ in range(neutrons):
                n = Circle(radius=0.1, color=n_color, fill_opacity=1).move_to(
                    center_circle.get_center() + np.random.uniform(-radius*0.6, radius*0.6, 3)
                )
                nucleus_group.add(n)
            return nucleus_group

        # 2. Main educational content with visual demonstrations
        # Initial setup
        u235_label = Text("Uranium-235", font_size=24).shift(DOWN * 2.5)
        uranium_nucleus = create_nucleus(10, 15, 1.0).shift(LEFT * 3)
        neutron = Circle(radius=0.15, color=WHITE, fill_opacity=1).move_to(LEFT * 6)
        
        self.play(FadeIn(uranium_nucleus), Write(u235_label))
        self.play(FadeIn(neutron))
        self.wait(1)

        # Neutron collision
        self.play(neutron.animate.move_to(uranium_nucleus.get_center()))
        
        # Unstable nucleus
        unstable_nucleus = uranium_nucleus.copy().add(neutron)
        unstable_label = Text("Unstable U-236", font_size=24).move_to(u235_label)
        self.play(Transform(uranium_nucleus, unstable_nucleus), Transform(u235_label, unstable_label))
        self.play(Wiggle(uranium_nucleus, n_wiggles=8, scale_value=1.2), run_time=1.5)
        self.wait(0.5)

        # Fission products
        krypton = create_nucleus(4, 5, 0.6, p_color=GREEN).move_to(LEFT * 4 + UP * 1)
        barium = create_nucleus(6, 8, 0.8, p_color=ORANGE).move_to(LEFT * 1.5 + DOWN * 1)
        
        neutrons_out = VGroup(
            Circle(radius=0.15, color=WHITE, fill_opacity=1).move_to(LEFT * 2 + UP * 2),
            Circle(radius=0.15, color=WHITE, fill_opacity=1).move_to(ORIGIN),
            Circle(radius=0.15, color=WHITE, fill_opacity=1).move_to(LEFT * 3 + DOWN * 2)
        )
        
        energy_waves = VGroup(*[Line(ORIGIN, RIGHT*2).apply_function(
            lambda p: [p[0], 0.2 * np.sin(p[0] * 3), 0]
        ).move_to(uranium_nucleus.get_center()).rotate(i*PI/3) for i in range(6)])
        energy_waves.set_color(YELLOW)
        
        self.play(
            FadeOut(uranium_nucleus),
            FadeOut(u235_label),
            FadeIn(krypton, barium),
            FadeIn(neutrons_out),
            Create(energy_waves)
        )
        self.play(FadeOut(energy_waves, scale=3))
        self.wait(1)

        # 3. Key concepts with clear explanations (The Fission Reaction)
        fission_group = VGroup(krypton, barium, neutrons_out).scale(0.8).move_to(ORIGIN)
        
        equation = MathTex(
            r"^{1}_{0}\text{n} + ^{235}_{92}\text{U} \rightarrow "
            r"^{141}_{56}\text{Ba} + ^{92}_{36}\text{Kr} + 3(^{1}_{0}\text{n}) + \text{Energy}",
            font_size=36
        ).to_edge(DOWN, buff=1.0)

        self.play(fission_group.animate.shift(UP * 1.5))
        self.play(Write(equation))
        self.wait(2)

        self.play(FadeOut(fission_group), FadeOut(equation))
        self.wait(1)

        # 4. Example: Chain Reaction
        chain_title = Text("Chain Reaction", font_size=40).to_edge(UP)
        self.play(Transform(title, chain_title))

        # Create a grid of Uranium nuclei
        nuclei = VGroup(*[
            create_nucleus(5, 7, 0.5).move_to(x * RIGHT * 3 + y * UP * 2.5)
            for x in [-1.5, 0, 1.5] for y in [-0.5, 0.5]
        ]).move_to(ORIGIN).shift(RIGHT * 1)
        
        initial_neutron = Circle(radius=0.1, color=WHITE, fill_opacity=1).move_to(LEFT * 6)
        
        self.play(FadeIn(nuclei), FadeIn(initial_neutron))
        self.wait(0.5)

        # First fission
        target1 = nuclei[2]
        self.play(initial_neutron.animate.move_to(target1.get_center()))
        
        new_neutrons1 = VGroup(*[Circle(radius=0.1, color=WHITE, fill_opacity=1) for _ in range(2)])
        new_neutrons1.arrange(RIGHT, buff=0.1).move_to(target1.get_center())
        
        self.play(
            FadeOut(initial_neutron),
            Indicate(target1, color=YELLOW),
            FadeOut(target1, scale=0.5),
            FadeIn(new_neutrons1)
        )

        # Second wave of fissions
        target2a = nuclei[1]
        target2b = nuclei[4]
        self.play(
            new_neutrons1[0].animate.move_to(target2a.get_center()),
            new_neutrons1[1].animate.move_to(target2b.get_center())
        )
        
        new_neutrons2a = VGroup(*[Circle(radius=0.1, color=WHITE, fill_opacity=1) for _ in range(2)])
        new_neutrons2a.arrange(RIGHT, buff=0.1).move_to(target2a.get_center())
        new_neutrons2b = VGroup(*[Circle(radius=0.1, color=WHITE, fill_opacity=1) for _ in range(2)])
        new_neutrons2b.arrange(RIGHT, buff=0.1).move_to(target2b.get_center())

        self.play(
            FadeOut(new_neutrons1),
            Indicate(target2a, color=YELLOW), Indicate(target2b, color=YELLOW),
            FadeOut(target2a, scale=0.5), FadeOut(target2b, scale=0.5),
            FadeIn(new_neutrons2a), FadeIn(new_neutrons2b)
        )
        self.wait(2)
        
        self.play(FadeOut(VGroup(nuclei, new_neutrons2a, new_neutrons2b)))
        self.wait(1)

        # 5. Summary and Conclusion
        summary_title = Text("Energy from Mass", font_size=40).to_edge(UP)
        self.play(Transform(title, summary_title))
        
        emc2 = MathTex("E = mc^2", font_size=60).move_to(ORIGIN)
        
        explanation = VGroup(
            Text("Fission converts a tiny amount of mass", font_size=24),
            Text("into a huge amount of energy.", font_size=24)
        ).arrange(DOWN, buff=0.5).next_to(emc2, DOWN, buff=1.0)
        
        self.play(Write(emc2))
        self.play(FadeIn(explanation, shift=UP))
        self.wait(2)

        self.play(FadeOut(emc2), FadeOut(explanation), FadeOut(title))
        self.wait(2)