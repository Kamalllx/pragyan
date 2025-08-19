# Manim Community v0.18.0
# To run this code, save it as a .py file and run the following command in your terminal:
# manim -pql your_file_name.py TrigonometryBasics

from manim import *
import math

class TrigonometryBasics(Scene):
    """
    An animation explaining the basics of trigonometry for beginners.
    This scene covers:
    1. The definition of trigonometry.
    2. The components of a right-angled triangle (Hypotenuse, Opposite, Adjacent).
    3. The core trigonometric ratios: Sine, Cosine, and Tangent (SOH CAH TOA).
    4. A practical example of using trigonometry to find the height of a tree.
    """
    def construct(self):
        # Set a consistent theme
        self.camera.background_color = "#1E1E1E" # Dark grey background
        title_color = YELLOW
        text_color = WHITE
        formula_color = BLUE_B
        highlight_color = RED_B

        # --- SCENE 1: INTRODUCTION ---
        title = Text("Trigonometry", font_size=64, color=title_color)
        subtitle = Text(
            "The study of relationships between angles and side lengths of triangles.",
            font_size=28,
            color=text_color
        ).next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        self.wait(1)

        # --- SCENE 2: THE RIGHT-ANGLED TRIANGLE ---
        topic_title = Text("The Right-Angled Triangle", font_size=48, color=title_color).to_edge(UP)
        self.play(Write(topic_title))
        self.wait(1)

        # Create the triangle
        # Vertices: A (origin), B (right), C (up)
        A = [-2, -1.5, 0]
        B = [2, -1.5, 0]
        C = [-2, 1.5, 0]
        triangle = Polygon(A, B, C, color=WHITE, stroke_width=6)
        
        # Right angle symbol
        right_angle = Square(side_length=0.4, color=highlight_color).move_to(A, aligned_edge=DL)

        self.play(Create(triangle), run_time=2)
        self.play(Create(right_angle))
        self.wait(1)

        # Label the sides and angle
        # Angle theta at vertex B
        angle_theta = Angle(Line(C, B), Line(A, B), radius=0.8, color=YELLOW)
        theta_label = MathTex(r"\theta", color=YELLOW).move_to(
            Angle(Line(C, B), Line(A, B), radius=1.1).get_center()
        )

        self.play(Create(angle_theta), Write(theta_label))
        self.wait(1)

        # Labels for sides relative to theta
        hyp_label = Text("Hypotenuse", color=formula_color).next_to(triangle.get_edge_center(1), UR, buff=0.2)
        opp_label = Text("Opposite", color=formula_color).next_to(triangle.get_edge_center(2), LEFT, buff=0.2)
        adj_label = Text("Adjacent", color=formula_color).next_to(triangle.get_edge_center(0), DOWN, buff=0.2)

        # Animate labels appearing
        self.play(Write(hyp_label))
        self.wait(0.5)
        self.play(Write(opp_label))
        self.wait(0.5)
        self.play(Write(adj_label))
        self.wait(2)

        triangle_group = VGroup(
            topic_title, triangle, right_angle, angle_theta, theta_label,
            hyp_label, opp_label, adj_label
        )
        self.play(triangle_group.animate.scale(0.7).to_edge(LEFT, buff=0.5))
        self.wait(1)

        # --- SCENE 3: SOH CAH TOA ---
        # Mnemonic
        soh_cah_toa = VGroup(
            MathTex(r"\text{SOH}", color=highlight_color),
            MathTex(r"\text{CAH}", color=highlight_color),
            MathTex(r"\text{TOA}", color=highlight_color)
        ).arrange(DOWN, buff=0.7).next_to(triangle_group, RIGHT, buff=1)
        
        self.play(Write(soh_cah_toa[0]))
        self.wait(0.5)
        self.play(Write(soh_cah_toa[1]))
        self.wait(0.5)
        self.play(Write(soh_cah_toa[2]))
        self.wait(1)

        # Formulas
        sin_formula = MathTex(r"\sin(\theta) = \frac{\text{Opposite}}{\text{Hypotenuse}}", color=formula_color)
        cos_formula = MathTex(r"\cos(\theta) = \frac{\text{Adjacent}}{\text{Hypotenuse}}", color=formula_color)
        tan_formula = MathTex(r"\tan(\theta) = \frac{\text{Opposite}}{\text{Adjacent}}", color=formula_color)
        
        formulas = VGroup(sin_formula, cos_formula, tan_formula).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        formulas.next_to(soh_cah_toa, RIGHT, buff=0.5)

        self.play(ReplacementTransform(soh_cah_toa[0].copy(), sin_formula))
        self.wait(1)
        self.play(ReplacementTransform(soh_cah_toa[1].copy(), cos_formula))
        self.wait(1)
        self.play(ReplacementTransform(soh_cah_toa[2].copy(), tan_formula))
        self.wait(2)

        # Cleanup for next scene
        self.play(
            FadeOut(triangle_group),
            FadeOut(soh_cah_toa),
            FadeOut(formulas)
        )
        self.wait(1)

        # --- SCENE 4: EXAMPLE PROBLEM ---
        example_title = Text("Example: Find the Tree's Height", font_size=48, color=title_color).to_edge(UP)
        self.play(Write(example_title))
        self.wait(1)

        # Setup the scene
        ground = Line([-6, -2, 0], [6, -2, 0], color=WHITE)
        
        # Simple tree using polygons
        trunk = Rectangle(width=0.4, height=2, color=rgb_to_color([139/255, 69/255, 19/255]), fill_opacity=1).move_to([4, -1, 0])
        leaves = VGroup(
            Polygon([-0.8, 0, 0], [0.8, 0, 0], [0, 1.5, 0], color=GREEN, fill_opacity=1),
            Polygon([-0.7, 0.8, 0], [0.7, 0.8, 0], [0, 2.2, 0], color=GREEN, fill_opacity=1)
        ).move_to([4, 1.2, 0])
        tree = VGroup(trunk, leaves)

        self.play(Create(ground))
        self.play(DrawBorderThenFill(tree))
        self.wait(1)

        # Create the triangle for the problem
        observer_pos = [-4, -2, 0]
        tree_base = [4, -2, 0]
        tree_top = [4, 2.5, 0] # A bit above the visual tree top

        prob_triangle = Polygon(observer_pos, tree_base, tree_top, stroke_width=4, color=BLUE)
        prob_right_angle = Square(side_length=0.4, color=highlight_color).move_to(tree_base, aligned_edge=DL)
        
        self.play(Create(prob_triangle), Create(prob_right_angle))
        self.wait(1)

        # Label the knowns and unknown
        angle_val = 30
        prob_angle = Angle(Line(tree_top, observer_pos), Line(tree_base, observer_pos), radius=1, color=YELLOW)
        prob_angle_label = MathTex(f"{angle_val}^\circ", color=YELLOW).move_to(
            Angle(Line(tree_top, observer_pos), Line(tree_base, observer_pos), radius=1.3).get_center()
        )

        dist_val = 8 # meters
        dist_label = MathTex(f"{dist_val} \\text{{ m}}", color=WHITE).next_to(prob_triangle.get_edge_center(0), DOWN)
        
        height_label = MathTex("h = ?", color=highlight_color).next_to(prob_triangle.get_edge_center(2), LEFT)

        self.play(Create(prob_angle), Write(prob_angle_label))
        self.play(Write(dist_label))
        self.play(Write(height_label))
        self.wait(2)

        # Move visual to the side to make space for calculations
        problem_visuals = VGroup(
            ground, tree, prob_triangle, prob_right_angle,
            prob_angle, prob_angle_label, dist_label, height_label
        )
        self.play(problem_visuals.animate.scale(0.6).to_edge(LEFT, buff=0.5))
        self.wait(1)

        # --- Step-by-step calculation ---
        calc_area = VGroup().next_to(problem_visuals, RIGHT, buff=1).align_to(example_title, UP)
        
        # Step 1: Identify sides and choose formula
        step1_title = Text("1. Identify Sides", font_size=28, color=text_color).next_to(calc_area, UP, aligned_edge=LEFT)
        
        # Using f-strings for safety and clarity
        side_opp = MathTex(r"\text{Opposite} = h \text{ (what we want)}", color=formula_color)
        side_adj = MathTex(f"\\text{{Adjacent}} = {dist_val} \\text{{ m (what we know)}}", color=formula_color)
        
        step1_text = VGroup(side_opp, side_adj).arrange(DOWN, aligned_edge=LEFT).next_to(step1_title, DOWN, aligned_edge=LEFT)

        self.play(Write(step1_title))
        self.play(Write(step1_text))
        self.wait(1)

        chosen_formula = MathTex(r"\text{Use: } \tan(\theta) = \frac{\text{Opposite}}{\text{Adjacent}}", color=highlight_color)
        chosen_formula.next_to(step1_text, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(chosen_formula))
        self.wait(2)

        # Step 2: Substitute values
        step2_title = Text("2. Substitute Values", font_size=28, color=text_color).next_to(chosen_formula, DOWN, buff=0.7, aligned_edge=LEFT)
        
        # Using f-string to insert values into the formula
        subst_formula = MathTex(f"\\tan({angle_val}^\\circ) = \\frac{{h}}{{{dist_val}}}", color=formula_color)
        subst_formula.next_to(step2_title, DOWN, aligned_edge=LEFT)

        self.play(Write(step2_title))
        self.play(Write(subst_formula))
        self.wait(2)

        # Step 3: Solve for h
        step3_title = Text("3. Solve for h", font_size=28, color=text_color).next_to(subst_formula, DOWN, buff=0.7, aligned_edge=LEFT)
        
        rearranged_formula = MathTex(f"h = {dist_val} \\times \\tan({angle_val}^\\circ)", color=formula_color)
        rearranged_formula.next_to(step3_title, DOWN, aligned_edge=LEFT)
        self.play(Write(step3_title))
        self.play(TransformMatchingTex(subst_formula.copy(), rearranged_formula))
        self.wait(1)

        # Calculate result
        tan_val = math.tan(math.radians(angle_val))
        height_val = dist_val * tan_val
        
        # Using f-string for the final calculation steps
        calc_step = MathTex(f"h = {dist_val} \\times {tan_val:.3f}", color=formula_color)
        calc_step.next_to(rearranged_formula, DOWN, aligned_edge=LEFT)
        self.play(Write(calc_step))
        self.wait(1)

        final_answer = MathTex(f"h \\approx {height_val:.2f} \\text{{ m}}", color=GREEN)
        final_answer.next_to(calc_step, DOWN, aligned_edge=LEFT)
        
        result_box = SurroundingRectangle(final_answer, color=GREEN, buff=0.2)

        self.play(Write(final_answer))
        self.play(Create(result_box))
        
        # Update the height label on the diagram
        new_height_label = MathTex(f"h \\approx {height_val:.2f} \\text{{ m}}", color=GREEN, font_size=32)
        new_height_label.move_to(height_label).align_to(height_label, RIGHT)
        self.play(Transform(height_label, new_height_label))

        self.wait(4)