from manim import *

class MathematicsCircleScene(Scene):
    def construct(self):
        # Set a background color
        self.camera.background_color = "#f0f0f0"
        # Define a consistent color palette
        main_color = BLUE_D
        secondary_color = TEAL_D
        text_color = BLACK

        # 1. Title Introduction
        title = Text("Understanding the Circle", font_size=48, color=text_color)
        title.to_edge(UP, buff=0.8)
        self.play(Write(title))
        self.wait(1)

        # 2. Create the Circle and Center
        # Use a coordinate plane for context
        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-4, 4, 1],
            axis_config={"color": GRAY_A, "include_tip": False},
        ).scale(0.9)
        
        circle = Circle(radius=2, color=main_color, stroke_width=6).move_to(ORIGIN)
        center_dot = Dot(ORIGIN, color=RED)
        center_label = Text("Center", font_size=24, color=text_color).next_to(center_dot, DOWN, buff=0.3)

        self.play(FadeIn(axes))
        self.play(Create(circle))
        self.play(FadeIn(center_dot), Write(center_label))
        self.wait(1.5)

        # 3. Explain the Radius
        radius_line = Line(ORIGIN, circle.point_at_angle(PI / 4), color=secondary_color, stroke_width=5)
        radius_label = MathTex("r", color=secondary_color, font_size=36).next_to(radius_line, UP, buff=0.2).shift(LEFT*0.2)
        
        radius_explanation = Text("The Radius (r) is the distance from the center to the edge.", font_size=24, color=text_color)
        radius_explanation.to_edge(DOWN, buff=1.0)

        self.play(Create(radius_line), Write(radius_label))
        self.play(Write(radius_explanation))
        self.wait(1)

        # Animate the radius to show it's constant
        self.play(Rotate(radius_line, angle=PI * 1.5, about_point=ORIGIN, run_time=3),
                  UpdateFromFunc(radius_label, lambda m: m.next_to(radius_line, UP, buff=0.2)))
        self.wait(1)

        # 4. Explain the Diameter
        self.play(FadeOut(radius_line), FadeOut(radius_label), FadeOut(radius_explanation))
        
        diameter_line = Line(circle.point_at_angle(PI), circle.point_at_angle(0), color=secondary_color, stroke_width=5)
        diameter_label = MathTex("d", color=secondary_color, font_size=36).next_to(diameter_line, UP, buff=0.2)
        
        diameter_explanation = Text("The Diameter (d) goes across the circle, through the center.", font_size=24, color=text_color)
        diameter_explanation.to_edge(DOWN, buff=1.0)
        
        formula_d = MathTex("d = 2 \\times r", color=text_color, font_size=36).to_edge(RIGHT, buff=1.0).shift(UP*1.5)

        self.play(Create(diameter_line), Write(diameter_label))
        self.play(Write(diameter_explanation))
        self.play(Write(formula_d))
        self.wait(2)

        # 5. Explain the Circumference
        self.play(FadeOut(diameter_line), FadeOut(diameter_label), FadeOut(diameter_explanation), FadeOut(formula_d))

        circumference_label = Text("Circumference (C)", font_size=24, color=text_color).next_to(circle, DOWN, buff=0.5)
        formula_c = MathTex("C = 2 \\pi r", color=text_color, font_size=36).to_edge(RIGHT, buff=1.0).shift(UP*1.5)

        self.play(Indicate(circle, color=main_color, scale_factor=1.1))
        self.play(Write(circumference_label))
        self.play(Write(formula_c))
        self.wait(2)

        # Visualization: Unroll the circumference
        unrolled_line = Line(LEFT * PI * 2, RIGHT * PI * 2, color=main_color, stroke_width=6)
        unrolled_line.next_to(circumference_label, DOWN, buff=0.8)
        
        unroll_text = Text("It's the distance around the circle.", font_size=24, color=text_color)
        unroll_text.next_to(unrolled_line, DOWN, buff=0.3)

        self.play(Transform(circle.copy(), unrolled_line))
        self.play(Write(unroll_text))
        self.wait(2.5)

        # 6. Explain the Area
        self.play(FadeOut(circumference_label), FadeOut(formula_c), FadeOut(unrolled_line), FadeOut(unroll_text))
        
        area_explanation = Text("The Area (A) is the space inside the circle.", font_size=24, color=text_color)
        area_explanation.to_edge(DOWN, buff=1.0)
        formula_a = MathTex("A = \\pi r^2", color=text_color, font_size=36).to_edge(RIGHT, buff=1.0).shift(UP*1.5)

        # Create a filled circle for area visualization
        filled_circle = circle.copy().set_fill(main_color, opacity=0.5)

        self.play(FadeIn(filled_circle))
        self.play(Write(area_explanation))
        self.play(Write(formula_a))
        self.wait(2.5)

        # 7. Summary
        self.play(FadeOut(VGroup(title, axes, circle, center_dot, center_label, filled_circle, area_explanation, formula_a)))
        self.wait(0.5)

        summary_title = Text("Circle Formulas Summary", font_size=40, color=text_color)
        summary_title.to_edge(UP, buff=1.0)

        # Grouping formulas for clean layout
        summary_formulas = VGroup(
            MathTex("Radius: r", color=text_color),
            MathTex("Diameter: d = 2r", color=text_color),
            MathTex("Circumference: C = 2\\pi r", color=text_color),
            MathTex("Area: A = \\pi r^2", color=text_color)
        ).arrange(DOWN, buff=0.8, aligned_edge=LEFT).scale(1.2)
        
        summary_formulas.move_to(ORIGIN)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_formulas, shift=DOWN))
        
        self.wait(3)