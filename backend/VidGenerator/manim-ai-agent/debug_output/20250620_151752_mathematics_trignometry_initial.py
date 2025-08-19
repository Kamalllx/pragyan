# Manim v0.19.0
# To render this animation, run the following command in your terminal:
# manim -pql trigonometry_basics.py TrigonometryBasics

from manim import *

class TrigonometryBasics(Scene):
    """
    An animation explaining the basics of trigonometry for beginners.
    This scene covers the right-angled triangle, SOH CAH TOA, a worked example,
    and a brief introduction to the unit circle.
    """
    def construct(self):
        # Use a consistent, large font size for clarity
        main_font_size = 48
        formula_font_size = 60

        # Set a theme for colors
        angle_color = YELLOW
        hyp_color = BLUE
        opp_color = RED
        adj_color = GREEN

        # --- SCENE 1: INTRODUCTION ---
        title = Text("Introduction to Trigonometry", font_size=main_font_size)
        self.play(Write(title))
        self.wait(1)

        # Explain the core idea
        explanation = Text(
            "The study of relationships between angles and side lengths in triangles.",
            font_size=36
        ).next_to(title, DOWN, buff=0.5)
        self.play(Write(explanation))
        self.wait(2)
        self.play(FadeOut(title, explanation))
        self.wait(1)

        # --- SCENE 2: THE RIGHT-ANGLED TRIANGLE ---
        
        # Create a coordinate system for context
        axes = Axes(
            x_range=[0, 8, 1],
            y_range=[0, 6, 1],
            x_length=8,
            y_length=6,
            axis_config={"color": GRAY}
        ).add_coordinates()
        
        # Define the vertices of the triangle
        p1 = axes.c2p(0, 0) # Origin
        p2 = axes.c2p(4, 0) # On x-axis
        p3 = axes.c2p(4, 3) # The top point

        # Create the triangle from vertices
        triangle = Polygon(p1, p2, p3, color=WHITE, stroke_width=6)

        # Create labels for sides and the angle
        right_angle = Square(side_length=0.4, color=WHITE).move_to(axes.c2p(0.2, 0.2), aligned_edge=DL)
        
        angle = Angle(Line(p2, p1), Line(p3, p1), radius=0.8, color=angle_color)
        angle_label = MathTex(r"\theta", color=angle_color, font_size=main_font_size).move_to(
            axes.c2p(1.1, 0.5)
        )

        # Introduce the triangle and its parts
        self.play(Create(axes), run_time=2)
        self.play(Create(triangle))
        self.play(Write(right_angle))
        self.play(Create(angle), Write(angle_label))
        self.wait(1)

        # Label the sides relative to the angle theta
        hyp_label = Text("Hypotenuse", font_size=36, color=hyp_color).rotate(angle.get_slope()).next_to(triangle.get_sides()[2], UP, buff=-1.5)
        opp_label = Text("Opposite", font_size=36, color=opp_color).next_to(triangle.get_sides()[1], RIGHT, buff=0.2)
        adj_label = Text("Adjacent", font_size=36, color=adj_color).next_to(triangle.get_sides()[0], DOWN, buff=0.2)

        # Animate the appearance of labels and highlight the corresponding sides
        hyp_side = triangle.get_sides()[2].copy().set_color(hyp_color)
        self.play(Create(hyp_side), Write(hyp_label))
        self.play(Indicate(hyp_side))
        self.wait(1)

        opp_side = triangle.get_sides()[1].copy().set_color(opp_color)
        self.play(Create(opp_side), Write(opp_label))
        self.play(Indicate(opp_side))
        self.wait(1)

        adj_side = triangle.get_sides()[0].copy().set_color(adj_color)
        self.play(Create(adj_side), Write(adj_label))
        self.play(Indicate(adj_side))
        self.wait(2)

        # Group all triangle elements to move them together
        triangle_group = VGroup(
            triangle, right_angle, angle, angle_label, 
            hyp_label, opp_label, adj_label,
            hyp_side, opp_side, adj_side
        )
        self.play(FadeOut(axes))
        self.play(triangle_group.animate.scale(0.8).to_edge(LEFT, buff=1))
        self.wait(1)

        # --- SCENE 3: THE TRIGONOMETRIC RATIOS (SOH CAH TOA) ---
        
        # Display the formulas
        soh_cah_toa_title = Text("The Main Ratios", font_size=main_font_size).to_edge(UP)
        
        sin_formula = MathTex(r"\sin(\theta) = \frac{\text{Opposite}}{\text{Hypotenuse}}", font_size=formula_font_size)
        cos_formula = MathTex(r"\cos(\theta) = \frac{\text{Adjacent}}{\text{Hypotenuse}}", font_size=formula_font_size)
        tan_formula = MathTex(r"\tan(\theta) = \frac{\text{Opposite}}{\text{Adjacent}}", font_size=formula_font_size)

        formulas = VGroup(sin_formula, cos_formula, tan_formula).arrange(DOWN, buff=0.8).next_to(triangle_group, RIGHT, buff=1)

        self.play(Write(soh_cah_toa_title))
        self.wait(0.5)

        # Animate each formula and indicate the relevant parts
        self.play(Write(sin_formula.next_to(soh_cah_toa_title, DOWN, buff=1)))
        self.play(Indicate(opp_side), Indicate(hyp_side))
        self.wait(1)

        self.play(Write(cos_formula.next_to(sin_formula, DOWN, buff=0.8)))
        self.play(Indicate(adj_side), Indicate(hyp_side))
        self.wait(1)

        self.play(Write(tan_formula.next_to(cos_formula, DOWN, buff=0.8)))
        self.play(Indicate(opp_side), Indicate(adj_side))
        self.wait(2)

        # Clean up for the next scene
        self.play(FadeOut(soh_cah_toa_title, triangle_group, formulas))
        self.wait(1)

        # --- SCENE 4: A CONCRETE EXAMPLE ---
        
        example_title = Text("Let's see an example", font_size=main_font_size).to_edge(UP)
        self.play(Write(example_title))

        # Create a 3-4-5 triangle
        p1_ex = [-2, -1.5, 0]
        p2_ex = [2, -1.5, 0]
        p3_ex = [2, 1.5, 0]
        
        example_triangle = Polygon(p1_ex, p2_ex, p3_ex, color=WHITE, stroke_width=6)
        
        # Labels for the 3-4-5 triangle
        side_len_adj = MathTex("4", color=adj_color).next_to(example_triangle.get_sides()[0], DOWN)
        side_len_opp = MathTex("3", color=opp_color).next_to(example_triangle.get_sides()[1], RIGHT)
        side_len_hyp = MathTex("5", color=hyp_color).rotate(example_triangle.get_sides()[2].get_angle()).next_to(example_triangle.get_sides()[2], UP, buff=-0.8)

        ex_angle = Angle(Line(p2_ex, p1_ex), Line(p3_ex, p1_ex), radius=0.5, color=angle_color)
        ex_angle_label = MathTex(r"\theta", color=angle_color).move_to(
            [-1.2, -1, 0]
        )

        example_group = VGroup(example_triangle, side_len_adj, side_len_opp, side_len_hyp, ex_angle, ex_angle_label)
        self.play(Create(example_group))
        self.wait(1)

        # Step-by-step calculation
        calc_sin_1 = MathTex(r"\sin(\theta) = \frac{\text{Opposite}}{\text{Hypotenuse}}", font_size=main_font_size)
        calc_sin_2 = MathTex(r"\sin(\theta) = \frac{3}{5}", font_size=main_font_size)
        calc_sin_3 = MathTex(r"\sin(\theta) = 0.6", font_size=main_font_size)
        
        calc_cos_1 = MathTex(r"\cos(\theta) = \frac{\text{Adjacent}}{\text{Hypotenuse}}", font_size=main_font_size)
        calc_cos_2 = MathTex(r"\cos(\theta) = \frac{4}{5}", font_size=main_font_size)
        calc_cos_3 = MathTex(r"\cos(\theta) = 0.8", font_size=main_font_size)

        calc_tan_1 = MathTex(r"\tan(\theta) = \frac{\text{Opposite}}{\text{Adjacent}}", font_size=main_font_size)
        calc_tan_2 = MathTex(r"\tan(\theta) = \frac{3}{4}", font_size=main_font_size)
        calc_tan_3 = MathTex(r"\tan(\theta) = 0.75", font_size=main_font_size)

        calculations = VGroup(calc_sin_1, calc_cos_1, calc_tan_1).arrange(DOWN, buff=0.8).to_edge(RIGHT, buff=1)
        
        # Sine calculation
        self.play(Write(calc_sin_1))
        self.play(Indicate(side_len_opp), Indicate(side_len_hyp))
        self.wait(0.5)
        self.play(Transform(calc_sin_1, calc_sin_2.move_to(calc_sin_1)))
        self.wait(0.5)
        self.play(Transform(calc_sin_1, calc_sin_3.move_to(calc_sin_1)))
        self.wait(1)

        # Cosine calculation
        self.play(Write(calc_cos_1))
        self.play(Indicate(side_len_adj), Indicate(side_len_hyp))
        self.wait(0.5)
        self.play(Transform(calc_cos_1, calc_cos_2.move_to(calc_cos_1)))
        self.wait(0.5)
        self.play(Transform(calc_cos_1, calc_cos_3.move_to(calc_cos_1)))
        self.wait(1)

        # Tangent calculation
        self.play(Write(calc_tan_1))
        self.play(Indicate(side_len_opp), Indicate(side_len_adj))
        self.wait(0.5)
        self.play(Transform(calc_tan_1, calc_tan_2.move_to(calc_tan_1)))
        self.wait(0.5)
        self.play(Transform(calc_tan_1, calc_tan_3.move_to(calc_tan_1)))
        self.wait(2)

        # Clean up
        self.play(FadeOut(example_title, example_group, calculations))
        self.wait(1)

        # --- SCENE 5: THE UNIT CIRCLE CONNECTION ---
        
        unit_circle_title = Text("A Quick Look at the Unit Circle", font_size=main_font_size).to_edge(UP)
        self.play(Write(unit_circle_title))

        # Create a new set of axes and a circle
        plane = NumberPlane(
            x_range=[-2, 2, 1], y_range=[-2, 2, 1],
            x_length=6, y_length=6,
            axis_config={"color": GRAY}
        )
        unit_circle = Circle(radius=plane.x_axis.n2p(1)[0], color=BLUE)
        
        self.play(Create(plane), Create(unit_circle))
        self.wait(1)

        # Create the triangle inside the unit circle
        angle_val = 60 * DEGREES
        point_on_circle = unit_circle.point_at_angle(angle_val)
        
        radius_line = Line(plane.c2p(0,0), point_on_circle, color=hyp_color)
        x_line = Line(plane.c2p(0,0), [point_on_circle[0], 0, 0], color=adj_color)
        y_line = Line([point_on_circle[0], 0, 0], point_on_circle, color=opp_color)
        
        uc_triangle = VGroup(radius_line, x_line, y_line)
        
        uc_angle = Angle(x_line, radius_line, radius=0.4, color=angle_color)
        uc_angle_label = MathTex(r"\theta", color=angle_color).next_to(uc_angle, RIGHT, buff=0.1)

        self.play(Create(uc_triangle), Create(uc_angle), Write(uc_angle_label))
        self.wait(1)

        # Show the coordinates and side lengths
        hyp_len = MathTex("1", color=hyp_color).next_to(radius_line.get_center(), LEFT, buff=0.1).shift(0.2*UP)
        x_coord = MathTex("x", color=adj_color).next_to(x_line, DOWN)
        y_coord = MathTex("y", color=opp_color).next_to(y_line, RIGHT)
        
        self.play(Write(hyp_len), Write(x_coord), Write(y_coord))
        self.wait(1)

        # Show the relationship
        cos_relation = MathTex(r"\cos(\theta) = \frac{x}{1} = x", font_size=main_font_size).to_edge(RIGHT, buff=1).shift(UP)
        sin_relation = MathTex(r"\sin(\theta) = \frac{y}{1} = y", font_size=main_font_size).next_to(cos_relation, DOWN, buff=0.5)
        
        self.play(Write(cos_relation))
        self.play(Indicate(x_line), Indicate(radius_line))
        self.wait(1)
        
        self.play(Write(sin_relation))
        self.play(Indicate(y_line), Indicate(radius_line))
        self.wait(2)

        # Final point label
        point_label = MathTex("(x, y) = (\\cos\\theta, \\sin\\theta)", font_size=main_font_size).next_to(point_on_circle, UR, buff=0.1)
        self.play(Write(point_label))
        self.wait(3)

        # --- SCENE 6: CONCLUSION ---
        self.play(
            FadeOut(unit_circle_title, plane, unit_circle, uc_triangle, uc_angle, uc_angle_label),
            FadeOut(hyp_len, x_coord, y_coord, cos_relation, sin_relation, point_label)
        )
        self.wait(1)
        
        end_text = Text("Thanks for watching!", font_size=main_font_size)
        self.play(Write(end_text))
        self.wait(2)
        self.play(FadeOut(end_text))
        self.wait(1)