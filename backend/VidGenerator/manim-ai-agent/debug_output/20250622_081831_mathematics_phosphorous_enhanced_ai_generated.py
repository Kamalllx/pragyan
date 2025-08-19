from manim import *

class PhosphorusMathematics(Scene):
    """
    An animation explaining the connection between Phosphorus and Mathematics
    through the geometry of its white allotrope (tetrahedron) and Euler's formula.
    """
    def construct(self):
        # Set a consistent color scheme
        phosphorus_color = PURE_RED
        math_color = BLUE
        text_color = WHITE

        # --- 1. Title Introduction ---
        title = Text("Phosphorus in Mathematics", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # --- 2. Main Educational Content: Introducing Phosphorus ---
        # Create a periodic table style box for Phosphorus
        p_box = Square(side_length=2.0, stroke_color=phosphorus_color, stroke_width=6)
        p_number = Text("15", font_size=36).move_to(p_box.get_center() + UP * 0.5)
        p_symbol = Text("P", font_size=60, weight=BOLD).move_to(p_box.get_center())
        p_name = Text("Phosphorus", font_size=24).move_to(p_box.get_center() + DOWN * 0.6)
        phosphorus_element = VGroup(p_box, p_number, p_symbol, p_name).move_to(LEFT * 4)

        intro_text_1 = Text("This is Phosphorus (P).", font_size=28).next_to(phosphorus_element, RIGHT, buff=1.0)
        intro_text_2 = Text("Its atomic number is 15.", font_size=28).next_to(intro_text_1, DOWN, buff=0.5, aligned_edge=LEFT)
        
        self.play(Create(p_box), FadeIn(p_number, p_symbol, p_name))
        self.play(Write(intro_text_1))
        self.play(Indicate(p_number))
        self.play(Write(intro_text_2))
        self.wait(2)

        # Transition to the math connection
        math_question = Text("But what is its connection to Math?", font_size=32, color=math_color)
        math_question.next_to(VGroup(phosphorus_element, intro_text_1, intro_text_2), DOWN, buff=1.0)
        self.play(Write(math_question))
        self.wait(2)

        self.play(
            FadeOut(phosphorus_element),
            FadeOut(intro_text_1),
            FadeOut(intro_text_2),
            math_question.animate.move_to(ORIGIN).to_edge(UP).scale(0.8)
        )
        self.wait(1)

        # --- 3. Key Concepts: The Tetrahedron Shape ---
        # Define vertices for a 2D projection of a tetrahedron
        v_top = UP * 1.5
        v_left = DOWN * 1 + LEFT * 1.7
        v_right = DOWN * 1 + RIGHT * 1.7
        v_back = DOWN * 0.5 + RIGHT * 0.1 # A point to give a 3D illusion

        # Create dots for Phosphorus atoms
        p_atoms = VGroup(*[Dot(point, radius=0.15, color=phosphorus_color) for point in [v_top, v_left, v_right, v_back]])
        p_labels = VGroup(*[MathTex("P", color=text_color).scale(0.8).next_to(dot, dot - ORIGIN, buff=0.2) for dot in p_atoms])

        shape_intro = Text("White Phosphorus (P₄) forms a special geometric shape.", font_size=28).next_to(math_question, DOWN, buff=0.5)
        self.play(Write(shape_intro))
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in p_atoms], lag_ratio=0.5))
        self.play(Write(p_labels))
        self.wait(1)

        # Create edges to form the tetrahedron
        edges = VGroup(
            Line(v_top, v_left), Line(v_top, v_right), Line(v_top, v_back),
            Line(v_left, v_right), Line(v_left, v_back), Line(v_right, v_back)
        )
        edges.set_color(WHITE)
        # Make one edge dashed to show it's "behind"
        dashed_edge = DashedLine(v_left, v_right, dash_length=0.2).set_color(WHITE)
        edges[3] = dashed_edge

        self.play(LaggedStart(*[Create(edge) for edge in edges], lag_ratio=0.5))
        self.wait(1)

        tetrahedron = VGroup(p_atoms, p_labels, edges)
        tetra_title = Text("A Tetrahedron", font_size=36, color=math_color).next_to(tetrahedron, DOWN, buff=0.8)
        self.play(tetrahedron.animate.shift(LEFT * 3.5), Write(tetra_title.next_to(tetrahedron, DOWN, buff=0.8)))
        self.wait(2)

        # --- 4. Example/Application: Euler's Formula ---
        # Analyze the properties of the tetrahedron
        analysis_group = VGroup()
        analysis_title = Text("Let's analyze this shape:", font_size=28).to_edge(RIGHT, buff=1.5).shift(UP * 2)
        self.play(Write(analysis_title))

        # Count Vertices
        v_text = MathTex("V", "\\text{ (Vertices)} = 4", font_size=32).next_to(analysis_title, DOWN, buff=0.8, aligned_edge=LEFT)
        self.play(Write(v_text[0:2]), Indicate(p_atoms, color=YELLOW))
        self.play(Write(v_text[2]))
        self.wait(1)

        # Count Edges
        e_text = MathTex("E", "\\text{ (Edges)} = 6", font_size=32).next_to(v_text, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(e_text[0:2]), Indicate(edges, color=GREEN))
        self.play(Write(e_text[2]))
        self.wait(1)

        # Count Faces
        faces = VGroup(
            Polygon(v_top, v_left, v_back, fill_color=BLUE, fill_opacity=0.5, stroke_width=0),
            Polygon(v_top, v_right, v_back, fill_color=BLUE, fill_opacity=0.5, stroke_width=0),
            Polygon(v_top, v_left, v_right, fill_color=BLUE, fill_opacity=0.5, stroke_width=0),
            Polygon(v_left, v_right, v_back, fill_color=BLUE, fill_opacity=0.5, stroke_width=0)
        )
        f_text = MathTex("F", "\\text{ (Faces)} = 4", font_size=32).next_to(e_text, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(f_text[0:2]))
        self.play(FadeIn(faces), run_time=2)
        self.play(FadeOut(faces))
        self.play(Write(f_text[2]))
        self.wait(1)

        analysis_group.add(analysis_title, v_text, e_text, f_text)

        # Introduce Euler's Formula
        euler_title = Text("Euler's Formula for Polyhedra:", font_size=28).next_to(analysis_group, DOWN, buff=1.0, aligned_edge=LEFT)
        euler_formula = MathTex("V - E + F = 2", font_size=36).next_to(euler_title, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(euler_title))
        self.play(Write(euler_formula))
        self.wait(1)

        # Substitute values
        calculation = MathTex("4 - 6 + 4 = 2", font_size=36).next_to(euler_formula, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Transform(VGroup(v_text[2].copy(), e_text[2].copy(), f_text[2].copy()), calculation))
        self.wait(2)

        # --- 5. Summary ---
        self.play(FadeOut(math_question, shape_intro, tetrahedron, tetra_title, analysis_group, euler_title, euler_formula, calculation))
        self.wait(1)

        summary_title = Text("Summary: Math in Phosphorus", font_size=40).to_edge(UP)
        
        summary_points = VGroup(
            Text("1. White Phosphorus (P₄) has a geometric structure.", font_size=28),
            Text("2. This structure is a Tetrahedron, a basic 3D shape.", font_size=28),
            Text("3. A tetrahedron has 4 Vertices, 6 Edges, and 4 Faces.", font_size=28),
            Text("4. It follows Euler's mathematical formula: V - E + F = 2.", font_size=28)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(ORIGIN).shift(LEFT*2)

        self.play(Write(summary_title))
        self.play(LaggedStart(*[Write(point) for point in summary_points], lag_ratio=0.7))

        self.wait(2)