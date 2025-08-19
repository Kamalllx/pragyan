from manim import *

class DijkstraAlgorithmScene(Scene):
    def construct(self):
        # 1. Title Introduction
        title = Text("Dijkstra's Algorithm: Finding the Shortest Path", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Define colors for clarity
        start_color = YELLOW
        visited_color = GRAY
        current_color = BLUE
        path_color = GREEN
        default_color = WHITE

        # 2. Graph Setup
        # Define node positions safely within the frame
        node_positions = {
            "A": [-4, 2, 0], "B": [-2, 0, 0], "C": [-4, -2, 0],
            "D": [0, 2, 0], "E": [2, 0, 0], "F": [0, -2, 0]
        }
        
        # Create nodes (circles) and labels (text)
        nodes = VGroup(*[Circle(radius=0.4, color=default_color).move_to(pos) for pos in node_positions.values()])
        node_labels = VGroup(*[Text(name, font_size=24).move_to(nodes[i]) for i, name in enumerate(node_positions.keys())])

        # Define edges with weights
        edges_info = {
            ("A", "B"): 4, ("A", "C"): 2, ("B", "D"): 5,
            ("C", "B"): 1, ("C", "F"): 8, ("D", "E"): 3,
            ("F", "D"): 2, ("F", "E"): 6
        }
        
        edges = VGroup()
        edge_weights = VGroup()
        for (n1, n2), weight in edges_info.items():
            start_pos = nodes[list(node_positions.keys()).index(n1)].get_center()
            end_pos = nodes[list(node_positions.keys()).index(n2)].get_center()
            edge = Line(start_pos, end_pos, stroke_width=3, buff=0.4)
            weight_label = MathTex(str(weight), font_size=24).move_to(edge.get_center() + (end_pos - start_pos) * 0.1 + UP * 0.2)
            edges.add(edge)
            edge_weights.add(weight_label)

        graph = VGroup(nodes, node_labels, edges, edge_weights).shift(LEFT * 1.5)
        self.play(Create(graph))
        self.wait(1)

        # 3. Algorithm Table Setup
        table_data = [
            ["Node", "Dist", "Prev"],
            ["A", "0", "-"],
            ["B", r"\infty", "-"],
            ["C", r"\infty", "-"],
            ["D", r"\infty", "-"],
            ["E", r"\infty", "-"],
            ["F", r"\infty", "-"],
        ]
        
        table = Table(table_data, include_outer_lines=True).scale(0.45)
        table.to_edge(RIGHT, buff=1.0)
        
        table_title = Text("Distances from A", font_size=24).next_to(table, UP, buff=0.3)
        
        self.play(Write(table_title), Create(table))
        self.wait(1)

        # 4. Algorithm Walkthrough
        # Helper function to update table cell
        def update_table_cell(row, col, new_text):
            new_mob = MathTex(new_text, font_size=21).move_to(table.get_cell((row + 2, col + 1)))
            self.play(Transform(table.get_entries((row + 2, col + 1)), new_mob))
            table.add(new_mob) # Add to table for future reference

        # Initialization
        start_node_index = 0
        nodes[start_node_index].set_color(start_color)
        
        explanation = Text("Start at node A. Distance is 0.", font_size=24).to_edge(DOWN)
        self.play(Write(explanation))
        self.play(Indicate(nodes[start_node_index]))
        self.wait(2)
        self.play(FadeOut(explanation))

        # Step 1: Process Node A
        current_node_index = 0
        nodes[current_node_index].set_color(current_color)
        
        # Neighbors of A: B and C
        # A -> C (dist 2)
        update_table_cell(2, 1, "2")
        update_table_cell(2, 2, "A")
        self.play(Indicate(edges[1]), Indicate(table.get_rows()[3]))
        self.wait(1)
        
        # A -> B (dist 4)
        update_table_cell(1, 1, "4")
        update_table_cell(1, 2, "A")
        self.play(Indicate(edges[0]), Indicate(table.get_rows()[2]))
        self.wait(1)

        nodes[current_node_index].set_color(visited_color)
        explanation = Text("Mark A as visited. Select unvisited node with smallest distance: C (Dist=2)", font_size=24).to_edge(DOWN)
        self.play(Write(explanation))
        self.wait(2)
        self.play(FadeOut(explanation))

        # Step 2: Process Node C
        current_node_index = 2
        nodes[current_node_index].set_color(current_color)
        
        # Neighbors of C: B and F
        # C -> B: 2 (from A->C) + 1 = 3. This is < 4. Update B.
        calc1 = MathTex("B: 2+1=3 < 4", font_size=28).next_to(graph, UP, buff=0.5).shift(RIGHT*2)
        self.play(Write(calc1))
        update_table_cell(1, 1, "3")
        update_table_cell(1, 2, "C")
        self.play(Indicate(edges[3]), Indicate(table.get_rows()[2]))
        self.wait(1)
        self.play(FadeOut(calc1))

        # C -> F: 2 (from A->C) + 8 = 10. Update F.
        calc2 = MathTex("F: 2+8=10", font_size=28).next_to(graph, UP, buff=0.5).shift(RIGHT*2)
        self.play(Write(calc2))
        update_table_cell(5, 1, "10")
        update_table_cell(5, 2, "C")
        self.play(Indicate(edges[4]), Indicate(table.get_rows()[6]))
        self.wait(1)
        self.play(FadeOut(calc2))

        nodes[current_node_index].set_color(visited_color)
        explanation = Text("Mark C as visited. Next smallest is B (Dist=3)", font_size=24).to_edge(DOWN)
        self.play(Write(explanation))
        self.wait(2)
        self.play(FadeOut(explanation))

        # Step 3: Process Node B
        current_node_index = 1
        nodes[current_node_index].set_color(current_color)
        
        # Neighbor of B: D
        # B -> D: 3 (from A->C->B) + 5 = 8. Update D.
        calc3 = MathTex("D: 3+5=8", font_size=28).next_to(graph, UP, buff=0.5).shift(RIGHT*2)
        self.play(Write(calc3))
        update_table_cell(3, 1, "8")
        update_table_cell(3, 2, "B")
        self.play(Indicate(edges[2]), Indicate(table.get_rows()[4]))
        self.wait(1)
        self.play(FadeOut(calc3))

        nodes[current_node_index].set_color(visited_color)
        explanation = Text("Mark B as visited. Next smallest is D (Dist=8)", font_size=24).to_edge(DOWN)
        self.play(Write(explanation))
        self.wait(2)
        self.play(FadeOut(explanation))

        # Step 4: Process Node D
        current_node_index = 3
        nodes[current_node_index].set_color(current_color)
        
        # Neighbor of D: E
        # D -> E: 8 (from A->C->B->D) + 3 = 11. Update E.
        calc4 = MathTex("E: 8+3=11", font_size=28).next_to(graph, UP, buff=0.5).shift(RIGHT*2)
        self.play(Write(calc4))
        update_table_cell(4, 1, "11")
        update_table_cell(4, 2, "D")
        self.play(Indicate(edges[5]), Indicate(table.get_rows()[5]))
        self.wait(1)
        self.play(FadeOut(calc4))

        nodes[current_node_index].set_color(visited_color)
        explanation = Text("Mark D as visited. Next smallest is F (Dist=10)", font_size=24).to_edge(DOWN)
        self.play(Write(explanation))
        self.wait(2)
        self.play(FadeOut(explanation))

        # Step 5: Process Node F
        current_node_index = 5
        nodes[current_node_index].set_color(current_color)

        # Neighbor of F: D (visited), E
        # F -> E: 10 (from A->C->F) + 6 = 16. This is > 11. No update.
        calc5 = MathTex("E: 10+6=16 > 11", font_size=28).next_to(graph, UP, buff=0.5).shift(RIGHT*2)
        self.play(Write(calc5))
        self.play(Indicate(edges[7]), color=RED)
        self.wait(1)
        self.play(FadeOut(calc5))

        nodes[current_node_index].set_color(visited_color)
        explanation = Text("Mark F as visited. Last node is E (Dist=11)", font_size=24).to_edge(DOWN)
        self.play(Write(explanation))
        self.wait(2)
        self.play(FadeOut(explanation))

        # Step 6: Process Node E
        current_node_index = 4
        nodes[current_node_index].set_color(current_color)
        self.wait(1)
        nodes[current_node_index].set_color(visited_color)
        
        # 5. Summary and Path Extraction
        self.play(FadeOut(table_title, table))
        
        summary_text = Text("Algorithm complete. Let's find the shortest path to E.", font_size=28)
        summary_text.to_edge(DOWN)
        self.play(Write(summary_text))
        self.wait(2)

        # Trace path back from E
        # E <- D
        path_E_D = Line(nodes[4].get_center(), nodes[3].get_center(), stroke_width=6, color=path_color, z_index=-1, buff=0.4)
        # D <- B
        path_D_B = Line(nodes[3].get_center(), nodes[1].get_center(), stroke_width=6, color=path_color, z_index=-1, buff=0.4)
        # B <- C
        path_B_C = Line(nodes[1].get_center(), nodes[2].get_center(), stroke_width=6, color=path_color, z_index=-1, buff=0.4)
        # C <- A
        path_C_A = Line(nodes[2].get_center(), nodes[0].get_center(), stroke_width=6, color=path_color, z_index=-1, buff=0.4)
        
        final_path = VGroup(path_E_D, path_D_B, path_B_C, path_C_A)

        self.play(Create(path_E_D))
        self.wait(0.5)
        self.play(Create(path_D_B))
        self.wait(0.5)
        self.play(Create(path_B_C))
        self.wait(0.5)
        self.play(Create(path_C_A))
        self.wait(1)

        final_text = MathTex(r"\text{Path: } A \rightarrow C \rightarrow B \rightarrow D \rightarrow E", font_size=32)
        final_cost = MathTex(r"\text{Total Cost: } 2 + 1 + 5 + 3 = 11", font_size=32)
        final_group = VGroup(final_text, final_cost).arrange(DOWN, buff=0.5).to_edge(RIGHT, buff=1.0)

        self.play(Transform(summary_text, final_group))
        self.wait(3)