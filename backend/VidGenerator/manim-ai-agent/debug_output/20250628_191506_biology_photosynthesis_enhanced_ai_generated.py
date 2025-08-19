from manim import *

class PhotosynthesisScene(Scene):
    """
    An animation explaining the process of photosynthesis at an intermediate level.
    This scene covers the overall chemical equation, the inputs and outputs,
    and a simplified view of the light-dependent and light-independent reactions
    within a chloroplast.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("Photosynthesis: The Process of Life", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # 2. Overall Chemical Equation
        equation = MathTex(
            r"6CO_2", r"+", r"6H_2O", r"\xrightarrow{\text{Sunlight}}", r"C_6H_{12}O_6", r"+", r"6O_2",
            font_size=40
        )
        equation.next_to(title, DOWN, buff=0.8)
        self.play(Write(equation))
        self.wait(1)

        # Labels for the equation components
        co2_label = Text("Carbon Dioxide", font_size=24).next_to(equation[0], DOWN)
        h2o_label = Text("Water", font_size=24).next_to(equation[2], DOWN)
        glucose_label = Text("Glucose", font_size=24).next_to(equation[4], DOWN)
        oxygen_label = Text("Oxygen", font_size=24).next_to(equation[6], DOWN)
        
        labels_group = VGroup(co2_label, h2o_label, glucose_label, oxygen_label)
        self.play(FadeIn(labels_group, shift=UP))
        self.wait(2)

        # Fade out equation and labels to make space for the main animation
        self.play(FadeOut(equation), FadeOut(labels_group))
        self.wait(1)

        # 3. Visual Representation of the Chloroplast
        chloroplast = Ellipse(width=6, height=3.5, color=GREEN_D, fill_opacity=0.8)
        chloroplast_label = Text("Chloroplast", font_size=24).next_to(chloroplast, UP, buff=0.2)
        
        # Thylakoids (Grana stacks)
        thylakoid_stack1 = VGroup(*[Circle(radius=0.3, color=GREEN_E, fill_opacity=1).shift(DOWN*i*0.2) for i in range(4)])
        thylakoid_stack2 = thylakoid_stack1.copy()
        thylakoid_stack1.move_to(chloroplast.get_center() + LEFT*1.5)
        thylakoid_stack2.move_to(chloroplast.get_center() + RIGHT*0.5)
        
        thylakoids = VGroup(thylakoid_stack1, thylakoid_stack2)
        thylakoid_label = Text("Thylakoids", font_size=20).next_to(thylakoid_stack1, DOWN, buff=0.3)

        chloroplast_group = VGroup(chloroplast, chloroplast_label, thylakoids, thylakoid_label)
        chloroplast_group.move_to(ORIGIN).shift(RIGHT * 0.5)

        self.play(Create(chloroplast), Write(chloroplast_label))
        self.play(Create(thylakoids), Write(thylakoid_label))
        self.wait(1)

        # 4. Inputs Animation
        # Sun
        sun = Circle(radius=0.6, color=YELLOW, fill_opacity=1).to_edge(UP + LEFT, buff=1)
        sun_rays = VGroup(*[Line(sun.get_center(), sun.get_center() + RIGHT*1.5*np.cos(a) + DOWN*1.5*np.sin(a), color=YELLOW) for a in np.linspace(0, -PI/2, 5)])
        sun_group = VGroup(sun, sun_rays)
        sun_label = Text("Sunlight", font_size=24).next_to(sun, RIGHT)

        # Water
        h2o = VGroup(
            Circle(radius=0.3, color=BLUE_C, fill_opacity=1),
            Text("H₂O", font_size=20, color=WHITE)
        ).arrange(ORIGIN).to_edge(LEFT, buff=1).shift(DOWN*1)
        
        # Carbon Dioxide
        co2 = VGroup(
            Circle(radius=0.3, color=GRAY, fill_opacity=1),
            Text("CO₂", font_size=20, color=WHITE)
        ).arrange(ORIGIN).next_to(h2o, UP, buff=1.5)

        inputs_group = VGroup(sun_group, sun_label, h2o, co2)
        self.play(FadeIn(inputs_group))
        self.wait(1)

        # 5. Light-Dependent Reactions
        light_reaction_title = Text("1. Light-Dependent Reactions", font_size=28, color=YELLOW_A).to_edge(DOWN, buff=0.5).shift(LEFT*3)
        self.play(Write(light_reaction_title))

        # Animate light and water entering thylakoids
        light_beam = Arrow(sun.get_center(), thylakoid_stack1.get_center(), color=YELLOW, buff=0.6)
        self.play(Create(light_beam))
        self.play(h2o.animate.move_to(thylakoid_stack1.get_center() + DOWN*0.5))
        self.play(FadeOut(h2o))
        self.wait(0.5)

        # Oxygen is released
        oxygen_out = VGroup(
            Circle(radius=0.3, color=LIGHT_BLUE, fill_opacity=1),
            Text("O₂", font_size=20, color=BLACK)
        ).arrange(ORIGIN).move_to(thylakoid_stack1.get_center())
        
        self.play(FadeIn(oxygen_out))
        self.play(oxygen_out.animate.shift(RIGHT*4 + UP*1))
        self.play(Indicate(oxygen_out))
        self.wait(1)
        self.play(FadeOut(light_beam))

        # 6. Light-Independent Reactions (Calvin Cycle)
        calvin_cycle_title = Text("2. Light-Independent Reactions", font_size=28, color=BLUE_A).to_edge(DOWN, buff=0.5).shift(RIGHT*3)
        self.play(Transform(light_reaction_title, calvin_cycle_title))

        # Animate CO2 entering the stroma (general chloroplast area)
        self.play(co2.animate.move_to(chloroplast.get_center() + RIGHT*1.5))
        self.play(FadeOut(co2))
        self.wait(0.5)

        # Glucose is produced
        glucose_out = VGroup(
            Polygon(
                *[np.array([np.cos(t), np.sin(t), 0]) * 0.4 for t in np.arange(PI/6, 2*PI, PI/3)],
                color=ORANGE, fill_opacity=1
            ),
            Text("C₆H₁₂O₆", font_size=16, color=BLACK)
        ).arrange(ORIGIN).move_to(chloroplast.get_center() + RIGHT*1.5)

        self.play(FadeIn(glucose_out, scale=0.5))
        self.play(glucose_out.animate.shift(RIGHT*2.5 + DOWN*1))
        self.play(Indicate(glucose_out))
        self.wait(1)

        # 7. Summary
        self.play(FadeOut(chloroplast_group, sun_group, sun_label, light_reaction_title))
        
        summary_title = Text("Photosynthesis Summary", font_size=32).to_edge(UP)
        
        inputs_summary = Text("Inputs:", font_size=28).move_to(LEFT*3.5 + UP*1.5)
        input_items = VGroup(
            Text("• Sunlight", font_size=24),
            Text("• Water (H₂O)", font_size=24),
            Text("• Carbon Dioxide (CO₂)", font_size=24)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(inputs_summary, DOWN, buff=0.5)

        outputs_summary = Text("Outputs:", font_size=28).move_to(RIGHT*3.5 + UP*1.5)
        output_items = VGroup(
            Text("• Glucose (C₆H₁₂O₆) - Energy", font_size=24),
            Text("• Oxygen (O₂) - Waste Product", font_size=24)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(outputs_summary, DOWN, buff=0.5)

        # Position the output objects from the animation
        glucose_out.next_to(output_items[0], DOWN, buff=0.5)
        oxygen_out.next_to(glucose_out, RIGHT, buff=1.2)
        
        self.play(
            Transform(title, summary_title),
            FadeIn(inputs_summary, input_items, outputs_summary, output_items, shift=UP),
            glucose_out.animate.next_to(output_items[0], DOWN, buff=0.5),
            oxygen_out.animate.next_to(glucose_out, RIGHT, buff=1.2)
        )

        self.wait(2)