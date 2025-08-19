from manim import *

class DijkstraAlgorithmScene(Scene):
    def construct(self):
        # 1. Title Introduction
        title = Text("Dijkstra's Algorithm", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Introduction Text
        intro_text = Text(
            "Finds the shortest path between nodes in a graph.",
            font_size=24
        ).next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # 2. Create the Graph
        # Define node positions to be well-spaced
        node_positions = {
            "A": [-4, 1.5, 0],
            "B": [-1, 2.5, 0],
            "C": [-2, -1, 0],
            "D": [2, 2, 0],
            "E": [3, -1.5, 0],
            "F": [5, 0.5, 0]
        }

        # Create nodes (circles with labels)
        nodes = VGroup()
        node_labels = VGroup()
        for name, pos in node_positions.items():
            node = Circle(radius=0.4, color=BLUE, fill_opacity=0.8)
            node.move_to(pos)
            label = Text(name, font_size=24).move_to(node.get_center())
            nodes.add(node)
            node_labels.add(label)
        
        graph_visual = VGroup(nodes, node_labels)

        # Define edges with weights
        edge_data = {
            ("A", "B"): 4, ("A", "C"): 2,
            ("B", "D"): 5,
            ("C", "B"): 1, ("C", "E"): 8,
            ("D", "E"): 2, ("D", "F"): 6,
            ("E", "F"): 1
        }
        
        edges = VGroup()
        edge_weights = VGroup()
        for (n1, n2), weight in edge_data.items():
            start_pos = node_positions[n1]
            end_pos = node_positions[n2]
            edge = Line(start_pos, end_pos, stroke_width=3, color=GRAY)
            
            # Position weight label near the middle of the edge
            label_pos = edge.get_center() + (UP * 0.3)
            weight_label = MathTex(str(weight), font_size=30).move_to(label_pos)
            
            edges.add(edge)
            edge_weights.add(weight_label)

        self.play(Create(edges), Create(nodes), Write(node_labels), Write(edge_weights))
        self.wait(1)

        # 3. Create the Distance Table
        table_title = Text("Distances from A", font_size=28).to_edge(RIGHT, buff=1).shift(UP*2.5)
        
        # Create a simple table structure using rectangles and text
        header = VGroup(
            Rectangle(width=1.5, height=0.6),
            Rectangle(width=1.5, height=0.6),
        ).arrange(RIGHT, buff=0)
        header_text = VGroup(
            Text("Node", font_size=20).move_to(header[0].get_center()),
            Text("Dist", font_size=20).move_to(header[1].get_center())
        )
        header_group = VGroup(header, header_text).next_to(table_title, DOWN, buff=0.2)

        table_rows = VGroup()
        dist_labels = {}
        
        # Initialize distances: 0 for start node 'A', infinity for others
        initial_distances = {"A": 0, "B": "∞", "C": "∞", "D": "∞", "E": "∞", "F": "∞"}

        for i, node_name in enumerate("ABCDEF"):
            row_rects = VGroup(
                Rectangle(width=1.5, height=0.6),
                Rectangle(width=1.5, height=0.6),
            ).arrange(RIGHT, buff=0)
            
            node_label = Text(node_name, font_size=24).move_to(row_rects[0].get_center())
            dist_label = MathTex(str(initial_distances[node_name]), font_size=24).move_to(row_rects[1].get_center())
            dist_labels[node_name] = dist_label
            
            row = VGroup(row_rects, node_label, dist_label)
            if i == 0:
                row.next_to(header_group, DOWN, buff=0)
            else:
                row.next_to(table_rows[-1], DOWN, buff=0)
            table_rows.add(row)

        distance_table = VGroup(table_title, header_group, table_rows)
        self.play(FadeIn(distance_table))
        self.wait(1)

        # 4. Step-by-step Dijkstra's Algorithm
        
        # Helper function to highlight a node
        def highlight_node(node_name, color):
            idx = "ABCDEF".index(node_name)
            return nodes[idx].animate.set_color(color)

        # Helper function to update distance in the table
        def update_distance(node_name, new_dist):
            old_label = dist_labels[node_name]
            new_label = MathTex(str(new_dist), font_size=24).move_to(old_label.get_center())
            return Transform(old_label, new_label)

        # Step 1: Start at A
        step_text = Text("1. Start at node A. Distance is 0.", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("A", YELLOW))
        self.wait(1)

        # Step 2: Visit neighbors of A (B and C)
        self.play(FadeOut(step_text))
        step_text = Text("2. Update distances for neighbors of A.", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        # A -> B
        self.play(edges[0].animate.set_color(YELLOW), run_time=0.5)
        self.play(update_distance("B", 4))
        # A -> C
        self.play(edges[1].animate.set_color(YELLOW), run_time=0.5)
        self.play(update_distance("C", 2))
        self.play(highlight_node("A", GREEN)) # Mark A as visited
        self.wait(2)

        # Step 3: Choose unvisited node with smallest distance (C)
        self.play(FadeOut(step_text))
        step_text = Text("3. Next node is C (distance 2).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("C", YELLOW))
        self.wait(1)

        # Step 4: Visit neighbors of C (B and E)
        self.play(FadeOut(step_text))
        step_text = Text("4. Update distances for neighbors of C.", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        # C -> B: 2 (from A->C) + 1 = 3. This is < 4. Update.
        calc_b = MathTex("2 + 1 = 3 < 4", font_size=28).next_to(nodes[1], UP, buff=0.5)
        self.play(edges[3].animate.set_color(YELLOW), run_time=0.5)
        self.play(Write(calc_b))
        self.play(update_distance("B", 3))
        self.play(FadeOut(calc_b))
        # C -> E: 2 (from A->C) + 8 = 10.
        calc_e = MathTex("2 + 8 = 10", font_size=28).next_to(nodes[4], UP, buff=0.5)
        self.play(edges[4].animate.set_color(YELLOW), run_time=0.5)
        self.play(Write(calc_e))
        self.play(update_distance("E", 10))
        self.play(FadeOut(calc_e))
        self.play(highlight_node("C", GREEN)) # Mark C as visited
        self.wait(2)

        # Step 5: Choose unvisited node with smallest distance (B)
        self.play(FadeOut(step_text))
        step_text = Text("5. Next node is B (distance 3).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("B", YELLOW))
        self.wait(1)

        # Step 6: Visit neighbors of B (D)
        self.play(FadeOut(step_text))
        step_text = Text("6. Update distances for neighbors of B.", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        # B -> D: 3 (from A->C->B) + 5 = 8.
        calc_d = MathTex("3 + 5 = 8", font_size=28).next_to(nodes[3], UP, buff=0.5)
        self.play(edges[2].animate.set_color(YELLOW), run_time=0.5)
        self.play(Write(calc_d))
        self.play(update_distance("D", 8))
        self.play(FadeOut(calc_d))
        self.play(highlight_node("B", GREEN)) # Mark B as visited
        self.wait(2)

        # Step 7: Choose unvisited node with smallest distance (D)
        self.play(FadeOut(step_text))
        step_text = Text("7. Next node is D (distance 8).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("D", YELLOW))
        self.wait(1)
        
        # Step 8: Visit neighbors of D (E and F)
        self.play(FadeOut(step_text))
        step_text = Text("8. Update distances for neighbors of D.", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        # D -> E: 8 + 2 = 10. This is not less than current 10. No update.
        calc_e2 = MathTex("8 + 2 = 10", font_size=28).next_to(nodes[4], UP, buff=0.5)
        self.play(edges[5].animate.set_color(YELLOW), run_time=0.5)
        self.play(Write(calc_e2))
        self.play(Indicate(dist_labels["E"]))
        self.play(FadeOut(calc_e2))
        # D -> F: 8 + 6 = 14.
        calc_f = MathTex("8 + 6 = 14", font_size=28).next_to(nodes[5], UP, buff=0.5)
        self.play(edges[6].animate.set_color(YELLOW), run_time=0.5)
        self.play(Write(calc_f))
        self.play(update_distance("F", 14))
        self.play(FadeOut(calc_f))
        self.play(highlight_node("D", GREEN)) # Mark D as visited
        self.wait(2)

        # Step 9: Choose unvisited node with smallest distance (E)
        self.play(FadeOut(step_text))
        step_text = Text("9. Next node is E (distance 10).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("E", YELLOW))
        self.wait(1)

        # Step 10: Visit neighbors of E (F)
        self.play(FadeOut(step_text))
        step_text = Text("10. Update distances for neighbors of E.", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        # E -> F: 10 + 1 = 11. This is < 14. Update.
        calc_f2 = MathTex("10 + 1 = 11 < 14", font_size=28).next_to(nodes[5], UP, buff=0.5)
        self.play(edges[7].animate.set_color(YELLOW), run_time=0.5)
        self.play(Write(calc_f2))
        self.play(update_distance("F", 11))
        self.play(FadeOut(calc_f2))
        self.play(highlight_node("E", GREEN)) # Mark E as visited
        self.wait(2)

        # Step 11: Final node F
        self.play(FadeOut(step_text))
        step_text = Text("11. Final node is F (distance 11).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("F", GREEN))
        self.wait(1)

        # 5. Summary and Conclusion
        self.play(FadeOut(step_text))
        summary_text = Text("Algorithm complete. Shortest paths from A found.", font_size=28).to_edge(DOWN)
        self.play(Write(summary_text))
        self.wait(1)

        # Highlight the shortest path from A to F: A -> C -> B -> D -> E -> F is not the path.
        # The path to F is A -> C -> E -> F (dist 11)
        # Let's trace back from F: Prev(F)=E, Prev(E)=C, Prev(C)=A
        # Path: A -> C -> E -> F
        path_A_C = edges[1]
        path_C_E = edges[4]
        path_E_F = edges[7]
        
        shortest_path = VGroup(path_A_C, path_C_E, path_E_F)
        path_nodes = VGroup(nodes[0], nodes[2], nodes[4], nodes[5]) # A, C, E, F

        path_title = Text("Shortest Path A to F: A-C-E-F (Cost: 11)", font_size=28).next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(path_title))
        self.play(
            shortest_path.animate.set_color(ORANGE).set_stroke(width=6),
            path_nodes.animate.set_color(ORANGE),
            run_time=2
        )
        
        self.wait(3)