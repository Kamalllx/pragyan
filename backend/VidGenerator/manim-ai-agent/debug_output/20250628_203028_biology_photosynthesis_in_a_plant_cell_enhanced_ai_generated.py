from manim import *

class PhotosynthesisInPlantCell(Scene):
    """
    An animation explaining the process of photosynthesis in a plant cell for beginners.
    This scene visualizes the key inputs and outputs of the process, focusing on the chloroplast.
    """
    def construct(self):
        # Set a background color for better contrast
        self.camera.background_color = "#F0F8FF"

        # 1. Title Introduction
        title = Text("Photosynthesis: How Plants Make Food", font_size=36, color=DARK_BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)

        # Subtitle to set the scene
        subtitle = Text("Let's look inside a plant cell!", font_size=24, color=BLACK)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(subtitle, shift=DOWN))
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))
        self.wait(0.5)

        # 2. Create the Chloroplast (the main stage)
        # We focus on the chloroplast, the 'factory' for photosynthesis.
        chloroplast_wall = Ellipse(width=6.0, height=3.5, color=GREEN_E, fill_opacity=0.3)
        chloroplast_wall.set_stroke(width=6)
        
        # Internal structures (grana) for visual detail
        grana_stack1 = VGroup(*[Circle(radius=0.2, color=GREEN_D, fill_opacity=1).set_stroke(width=0) for _ in range(5)]).arrange(DOWN, buff=0.05)
        grana_stack2 = VGroup(*[Circle(radius=0.2, color=GREEN_D, fill_opacity=1).set_stroke(width=0) for _ in range(4)]).arrange(DOWN, buff=0.05)
        grana_stack1.move_to(chloroplast_wall.get_center() + LEFT * 1.5)
        grana_stack2.move_to(chloroplast_wall.get_center() + RIGHT * 1.5 + UP * 0.5)
        
        chloroplast = VGroup(chloroplast_wall, grana_stack1, grana_stack2)
        chloroplast.move_to(ORIGIN).shift(UP * 0.5)

        chloroplast_label = Text("Chloroplast", font_size=28, color=DARK_GREEN)
        chloroplast_label.next_to(chloroplast, DOWN, buff=0.5)

        self.play(Create(chloroplast_wall), run_time=2)
        self.play(FadeIn(grana_stack1, grana_stack2))
        self.play(Write(chloroplast_label))
        self.wait(1)

        # 3. Show the Inputs entering the Chloroplast
        inputs_title = Text("Inputs (What's Needed)", font_size=24, color=BLUE).to_edge(LEFT, buff=0.5).shift(UP*2.5)
        self.play(Write(inputs_title))

        # Input 1: Sunlight
        sun = Circle(radius=0.5, color=YELLOW_C, fill_opacity=1).move_to(UP * 5 + LEFT * 5)
        sun_rays = VGroup()
        for i in range(3):
            ray = Arrow(sun.get_center(), chloroplast.get_top() + LEFT * (1-i), buff=0.5, color=YELLOW_C, stroke_width=5)
            sun_rays.add(ray)
        sun_label = Text("Sunlight", font_size=24, color=ORANGE).next_to(sun_rays, UP, buff=0.2)
        
        self.play(FadeIn(sun, scale=0.5))
        self.play(Write(sun_label), LaggedStart(*[Create(ray) for ray in sun_rays], lag_ratio=0.3))
        self.wait(1)

        # Input 2: Carbon Dioxide (CO2)
        co2_molecules = VGroup(*[MathTex("CO_2", font_size=36, color=GRAY) for _ in range(3)])
        co2_molecules.arrange(UP, buff=1.0).move_to(RIGHT * 6)
        co2_label = Text("Carbon Dioxide", font_size=24, color=GRAY).next_to(co2_molecules, RIGHT, buff=0.2)

        self.play(Write(co2_label))
        self.play(co2_molecules.animate.shift(LEFT * 4))
        self.wait(1)

        # Input 3: Water (H2O)
        h2o_molecules = VGroup(*[MathTex("H_2O", font_size=36, color=BLUE_D) for _ in range(3)])
        h2o_molecules.arrange(RIGHT, buff=1.0).move_to(DOWN * 3)
        h2o_label = Text("Water", font_size=24, color=BLUE_D).next_to(h2o_molecules, DOWN, buff=0.2)

        self.play(Write(h2o_label))
        self.play(h2o_molecules.animate.shift(UP * 1.5))
        self.wait(1)

        # Animate inputs entering the chloroplast
        self.play(
            LaggedStart(
                *[FadeOut(ray, target_position=chloroplast.get_center()) for ray in sun_rays],
                *[molecule.animate.move_to(chloroplast.get_center()) for molecule in co2_molecules],
                *[molecule.animate.move_to(chloroplast.get_center()) for molecule in h2o_molecules],
                lag_ratio=0.1
            ),
            FadeOut(sun_label), FadeOut(co2_label), FadeOut(h2o_label), FadeOut(sun),
            run_time=3
        )
        self.play(FadeOut(co2_molecules), FadeOut(h2o_molecules))
        self.play(Indicate(chloroplast, color=YELLOW, scale_factor=1.1), run_time=2)
        self.wait(1)

        # 4. Show the Outputs being produced
        self.play(FadeOut(inputs_title))
        outputs_title = Text("Outputs (What's Made)", font_size=24, color=PURPLE).to_edge(RIGHT, buff=0.5).shift(UP*2.5)
        self.play(Write(outputs_title))

        # Output 1: Oxygen (O2)
        o2_molecules = VGroup(*[MathTex("O_2", font_size=36, color=TEAL) for _ in range(3)])
        o2_molecules.arrange(UP, buff=1.0).move_to(chloroplast.get_center())
        o2_label = Text("Oxygen", font_size=24, color=TEAL).move_to(RIGHT * 5 + UP * 1)

        self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in o2_molecules]))
        self.play(
            o2_molecules.animate.move_to(RIGHT * 5),
            Write(o2_label)
        )
        self.wait(1)

        # Output 2: Glucose (C6H12O6)
        glucose_hex = Polygon(
            *[np.cos(i*PI/3)*RIGHT + np.sin(i*PI/3)*UP for i in range(6)],
            color=PINK, fill_opacity=1, stroke_width=4
        ).scale(0.5)
        glucose_hex.move_to(chloroplast.get_center() + LEFT * 1.5)
        glucose_label = Text("Glucose (Sugar for Energy)", font_size=24, color=PINK)
        glucose_label.next_to(glucose_hex, DOWN, buff=0.3)

        self.play(FadeIn(glucose_hex, scale=0.2))
        self.play(Write(glucose_label))
        self.wait(2)

        # 5. Summary
        self.play(
            FadeOut(chloroplast), FadeOut(chloroplast_label),
            FadeOut(outputs_title), FadeOut(o2_molecules),
            FadeOut(o2_label), FadeOut(glucose_hex), FadeOut(glucose_label)
        )
        self.wait(0.5)

        summary_title = Text("In Summary: Photosynthesis", font_size=36, color=DARK_BLUE).to_edge(UP, buff=1.0)
        
        # Using MathTex for a clear, final equation
        equation = MathTex(
            r"\text{Sunlight}", "+", r"CO_2", "+", r"H_2O", 
            r"\rightarrow", 
            r"\text{Glucose}", "+", r"O_2",
            font_size=40
        )
        equation.set_color_by_tex("Sunlight", YELLOW_C)
        equation.set_color_by_tex("CO_2", GRAY)
        equation.set_color_by_tex("H_2O", BLUE_D)
        equation.set_color_by_tex("Glucose", PINK)
        equation.set_color_by_tex("O_2", TEAL)
        equation.move_to(ORIGIN)

        explanation = Text("Plants use light energy to convert simple inputs\ninto food (glucose) and release oxygen.",
                           font_size=24, line_spacing=0.8, text_align="center").next_to(equation, DOWN, buff=1.0)

        self.play(Write(summary_title))
        self.play(Write(equation), run_time=3)
        self.play(Write(explanation))

        # Final wait to let the viewer absorb the information
        self.wait(4)