from manim import *

class DotProductExplanation(Scene):
    """
    An intermediate-level Manim scene explaining the dot product of vectors,
    covering both its algebraic and geometric interpretations.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("Understanding the Dot Product", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP).scale(0.8))

        # Setup axes for context
        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-4, 4, 1],
            axis_config={"color": BLUE},
            x_length=10,
            y_length=7,
        ).add_coordinates()
        axes.to_edge(DOWN, buff=0.5)
        
        self.play(Create(axes))
        self.wait(0.5)

        # 2. Main Educational Content: Introduce Vectors and Formulas
        # Define two vectors
        vec_v = Vector([3, 1], color=YELLOW)
        vec_w = Vector([1, 2], color=GREEN)
        
        # Create labels for the vectors
        label_v = MathTex(r"\vec{v}", color=YELLOW).next_to(vec_v.get_end(), UR, buff=0.2)
        label_w = MathTex(r"\vec{w}", color=GREEN).next_to(vec_w.get_end(), UR, buff=0.2)

        vector_group = VGroup(vec_v, vec_w, label_v, label_w)
        self.play(Create(vec_v), Create(vec_w))
        self.play(Write(label_v), Write(label_w))
        self.wait(1)

        # Display the two main formulas for the dot product
        formula_alg = MathTex(r"\vec{v} \cdot \vec{w} = v_x w_x + v_y w_y", font_size=36)
        formula_geo = MathTex(r"\vec{v} \cdot \vec{w} = ||\vec{v}|| \ ||\vec{w}|| \cos(\theta)", font_size=36)
        
        formulas = VGroup(formula_alg, formula_geo).arrange(DOWN, buff=0.8).to_edge(RIGHT, buff=1.0)
        
        self.play(Write(formulas))
        self.wait(2)

        # 3. Key Concepts with Clear Explanations: The Geometric Intuition
        explanation_text = Text("The dot product measures how much one vector\npoints in the direction of another.", font_size=28)
        explanation_text.next_to(title, DOWN, buff=0.5)
        self.play(Write(explanation_text))
        self.wait(2)

        # Visualize the projection
        # Create a line extending from vector w for projection
        line_w = Line(ORIGIN, vec_w.get_end() * 2.5, stroke_width=2, color=GRAY)
        
        # Calculate the projection of v onto w
        projection_scalar = np.dot(vec_v.get_end(), vec_w.get_end()) / np.linalg.norm(vec_w.get_end())**2
        projection_vector = Vector(vec_w.get_end() * projection_scalar, color=RED)
        
        # Dashed line from v's tip to the projection line
        dashed_line = DashedLine(vec_v.get_end(), projection_vector.get_end(), color=WHITE, stroke_width=3)
        
        self.play(Create(line_w))
        self.play(Create(dashed_line))
        self.play(Create(projection_vector))
        self.wait(1)

        proj_label = Text("Projection of v onto w", font_size=24, color=RED).next_to(projection_vector, DOWN, buff=0.2)
        self.play(Write(proj_label))
        self.wait(2)

        # Explain the connection
        self.play(FadeOut(explanation_text), FadeOut(proj_label))
        
        # Highlight the geometric formula parts
        angle = Angle(vec_w, vec_v, radius=0.7, other_angle=False)
        theta_label = MathTex(r"\theta").next_to(angle, RIGHT, buff=0.1)
        
        self.play(Create(angle), Write(theta_label))
        self.play(Indicate(formula_geo))
        self.wait(2)

        # 4. Examples or Applications: Special Cases
        # Case 1: Perpendicular vectors (dot product is 0)
        perp_text = Text("Case 1: Perpendicular Vectors (θ = 90°)", font_size=32).to_corner(UL)
        self.play(Write(perp_text))
        
        new_vec_v = Vector([-2, 3], color=YELLOW)
        new_label_v = MathTex(r"\vec{v}", color=YELLOW).next_to(new_vec_v.get_end(), UL, buff=0.2)
        
        # Fade out old projection visuals
        self.play(FadeOut(projection_vector, dashed_line, line_w, angle, theta_label))
        
        # Transform v to be perpendicular to w
        self.play(Transform(vec_v, new_vec_v), Transform(label_v, new_label_v))
        
        result_zero = MathTex(r"\cos(90^\circ) = 0 \implies \vec{v} \cdot \vec{w} = 0", font_size=36).next_to(formulas, DOWN, buff=0.5)
        self.play(Write(result_zero))
        self.wait(2)
        self.play(FadeOut(perp_text, result_zero))

        # Case 2: Parallel vectors (dot product is maximized)
        para_text = Text("Case 2: Parallel Vectors (θ = 0°)", font_size=32).to_corner(UL)
        self.play(Write(para_text))

        new_vec_v = Vector([0.5, 1], color=YELLOW) # Parallel to [1, 2]
        new_label_v = MathTex(r"\vec{v}", color=YELLOW).next_to(new_vec_v.get_end(), UR, buff=0.2)

        self.play(Transform(vec_v, new_vec_v), Transform(label_v, new_label_v))

        result_max = MathTex(r"\cos(0^\circ) = 1 \implies \vec{v} \cdot \vec{w} = ||\vec{v}|| \ ||\vec{w}||", font_size=36).next_to(formulas, DOWN, buff=0.5)
        self.play(Write(result_max))
        self.wait(2)
        self.play(FadeOut(para_text, result_max))
        self.wait(1)

        # 5. Summary or Conclusion
        self.play(FadeOut(vector_group), FadeOut(vec_v), FadeOut(label_v), FadeOut(vec_w), FadeOut(label_w), FadeOut(axes), FadeOut(formulas))
        
        summary_title = Text("Dot Product: Key Takeaways", font_size=40).to_edge(UP)
        
        summary_points = VGroup(
            Text("1. An algebraic calculation:  v_x * w_x + v_y * w_y", font_size=28),
            Text("2. A geometric concept: Measures alignment of vectors.", font_size=28),
            Text("3. If dot product is 0, vectors are perpendicular.", font_size=28),
            Text("4. If positive, they point in a similar direction.", font_size=28),
            Text("5. If negative, they point in opposite directions.", font_size=28)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(summary_title, DOWN, buff=0.7)

        self.play(Transform(title, summary_title))
        self.play(Write(summary_points))

        self.wait(4)