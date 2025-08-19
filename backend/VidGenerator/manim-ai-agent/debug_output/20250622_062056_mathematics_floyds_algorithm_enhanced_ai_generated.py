from manim import *

class FloydsAlgorithmScene(Scene):
    def construct(self):
        # 1. Title Introduction
        title = Text("Floyd's Algorithm", font_size=48)
        subtitle = Text("Finding All-Pairs Shortest Paths", font_size=28)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        title_group.to_edge(UP)

        self.play(Write(title_group))
        self.wait(1)

        # 2. Graph and Initial Matrix Setup
        explanation_text = Text(
            "Let's start with a weighted directed graph.",
            font_size=24
        ).next_to(title_group, DOWN, buff=0.75)
        self.play(Write(explanation_text))
        self.wait(1)

        # Create the graph
        nodes = {
            "A": [-4, 2, 0],
            "B": [-1, 2, 0],
            "C": [-4, -1, 0],
            "D": [-1, -1, 0]
        }
        
        node_circles = VGroup(*[Circle(radius=0.4, color=BLUE).move_to(pos) for pos in nodes.values()])
        node_labels = VGroup(*[Text(name, font_size=24).move_to(nodes[name]) for name in nodes])
        graph = VGroup(node_circles, node_labels)

        edges = {
            ("A", "B"): 3,
            ("A", "C"): 8,
            ("A", "D"): -4,
            ("B", "C"): 1,
            ("B", "D"): 7,
            ("C", "A"): 2,
            ("D", "B"): 5,
            ("D", "C"): -2,
        }

        edge_arrows = VGroup()
        for (start, end), weight in edges.items():
            arrow = Arrow(
                nodes[start], nodes[end], buff=0.4, stroke_width=3, max_tip_length_to_length_ratio=0.15
            )
            label = Text(str(weight), font_size=20).next_to(arrow.get_center(), arrow.get_unit_vector()*0.5 + UP*0.2, buff=0.1)
            edge_arrows.add(VGroup(arrow, label))

        graph_group = VGroup(graph, edge_arrows).scale(0.9).shift(LEFT * 2.5)
        
        self.play(FadeOut(explanation_text), Create(graph_group))
        self.wait(1)

        # Create the initial distance matrix D0
        matrix_title_0 = MathTex("D^{(0)}", font_size=36).to_edge(RIGHT, buff=1.5).shift(UP * 2.5)
        dist_matrix_0 = Matrix(
            [["0", "3", "8", r"\infty"],
             [r"\infty", "0", "1", "7"],
             ["2", r"\infty", "0", r"\infty"],
             [r"\infty", "5", "-2", "0"]],
            h_buff=1.2,
            v_buff=0.8,
            left_bracket="[",
            right_bracket="]"
        ).next_to(matrix_title_0, DOWN, buff=0.5)
        
        matrix_labels_top = VGroup(*[Text(label, font_size=24) for label in ["A", "B", "C", "D"]]).arrange(RIGHT, buff=1.0)
        matrix_labels_top.next_to(dist_matrix_0, UP, buff=0.3)
        matrix_labels_left = VGroup(*[Text(label, font_size=24) for label in ["A", "B", "C", "D"]]).arrange(DOWN, buff=0.65)
        matrix_labels_left.next_to(dist_matrix_0, LEFT, buff=0.3)

        matrix_group_0 = VGroup(matrix_title_0, dist_matrix_0, matrix_labels_top, matrix_labels_left)

        self.play(Write(matrix_group_0))
        self.wait(2)

        # 3. Iteration k=A (k=0)
        iteration_text = Text("Iteration k = A (intermediate node)", font_size=28).to_edge(DOWN)
        self.play(Write(iteration_text))
        self.wait(1)

        # Highlight node A and corresponding row/column
        node_A = graph[0][0]
        row_A = dist_matrix_0.get_rows()[0]
        col_A = dist_matrix_0.get_columns()[0]
        
        self.play(
            node_A.animate.set_color(YELLOW),
            row_A.animate.set_color(YELLOW),
            col_A.animate.set_color(YELLOW)
        )
        self.wait(1)

        # Show the update rule
        formula = MathTex(
            r"D[i][j] = \min(D[i][j], D[i][k] + D[k][j])",
            font_size=28
        ).next_to(iteration_text, UP, buff=0.5)
        self.play(Write(formula))
        self.wait(2)

        # Example update: C -> D via A
        # D[C][D] = min(D[C][D], D[C][A] + D[A][D]) = min(inf, 2 + (-4)) = -2
        # Let's find a better one. D[C][B] = min(inf, D[C][A] + D[A][B]) = min(inf, 2+3) = 5
        path_C_A_B = VGroup(edge_arrows[5][0].copy(), edge_arrows[0][0].copy()).set_color(ORANGE)
        
        cell_CB = dist_matrix_0.get_entries((3,2))
        cell_CA = dist_matrix_0.get_entries((3,1))
        cell_AB = dist_matrix_0.get_entries((1,2))

        self.play(
            Indicate(cell_CB),
            Indicate(cell_CA),
            Indicate(cell_AB),
            Create(path_C_A_B)
        )
        self.wait(1)

        calculation = MathTex(r"D[C][B] = \min(\infty, 2 + 3) = 5", font_size=28).move_to(formula.get_center())
        self.play(Transform(formula, calculation))
        self.wait(2)

        # Create D1 matrix and update the value
        matrix_title_1 = MathTex("D^{(1)}", font_size=36).move_to(matrix_title_0)
        dist_matrix_1 = Matrix(
            [["0", "3", "8", "-4"],
             [r"\infty", "0", "1", "7"],
             ["2", "5", "0", "-2"], # Updated C->B and C->D
             [r"\infty", "5", "-2", "0"]],
            h_buff=1.2,
            v_buff=0.8,
            left_bracket="[",
            right_bracket="]"
        ).next_to(matrix_title_1, DOWN, buff=0.5)
        
        matrix_group_1 = VGroup(matrix_title_1, dist_matrix_1, matrix_labels_top.copy(), matrix_labels_left.copy())

        self.play(
            Transform(matrix_group_0, matrix_group_1),
            FadeOut(path_C_A_B)
        )
        self.play(FadeOut(formula))
        self.wait(2)

        # 4. Subsequent Iterations (Simplified)
        self.play(
            node_A.animate.set_color(BLUE), # Reset color
            row_A.animate.set_color(WHITE),
            col_A.animate.set_color(WHITE)
        )

        # Transition to showing the final result
        final_text = Text(
            "This process repeats for all nodes (B, C, D)...",
            font_size=24
        ).move_to(iteration_text.get_center())
        self.play(Transform(iteration_text, final_text))
        self.wait(2)

        # Final Matrix D4
        matrix_title_final = MathTex("D^{(4)}", font_size=36).move_to(matrix_title_0)
        dist_matrix_final = Matrix(
            [["0", "1", "-3", "-4"],
             ["3", "0", "1", "-1"],
             ["2", "3", "0", "-2"],
             ["5", "5", "-2", "0"]],
            h_buff=1.2,
            v_buff=0.8,
            left_bracket="[",
            right_bracket="]"
        ).next_to(matrix_title_final, DOWN, buff=0.5)
        
        matrix_group_final = VGroup(matrix_title_final, dist_matrix_final, matrix_labels_top.copy(), matrix_labels_left.copy())

        self.play(Transform(matrix_group_0, matrix_group_final))
        self.wait(1)

        # Highlight a final path, e.g., A -> D -> C
        # D[A][C] = -3
        path_A_D_C = VGroup(edge_arrows[2][0].copy(), edge_arrows[7][0].copy()).set_color(GREEN)
        cell_AC = dist_matrix_final.get_entries((1,3))
        
        self.play(
            Indicate(cell_AC, color=GREEN),
            Create(path_A_D_C)
        )
        self.wait(2)
        self.play(FadeOut(path_A_D_C))

        # 5. Summary
        self.play(FadeOut(graph_group, matrix_group_0, iteration_text))

        summary_title = Text("Summary", font_size=36).to_edge(UP, buff=1.0)
        summary_points = VGroup(
            Text("1. Initializes a matrix with direct path distances.", font_size=24),
            Text("2. Iteratively considers each vertex 'k' as an intermediate point.", font_size=24),
            Text("3. Updates the path if 'i -> k -> j' is shorter than 'i -> j'.", font_size=24),
            Text("4. The final matrix contains all-pairs shortest paths.", font_size=24)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(summary_title, DOWN, buff=1.0)

        summary_group = VGroup(summary_title, summary_points).move_to(ORIGIN)

        self.play(FadeOut(title_group), Write(summary_group))
        self.wait(3)

        self.play(FadeOut(summary_group))
        self.wait(2)