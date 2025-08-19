from manim import *

class DijkstraAlgorithmScene(Scene):
    def construct(self):
        # 1. Title Introduction
        title = Text("Dijkstra's Algorithm", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Subtitle explaining the goal
        goal_text = Text("Find the shortest path from a start node to all other nodes", font_size=24)
        goal_text.next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(goal_text))
        self.wait(2)
        self.play(FadeOut(goal_text))

        # 2. Create the Graph
        # Node positions
        node_positions = {
            "A": [-4, 1.5, 0], "B": [0, 2.5, 0], "C": [4, 1.5, 0],
            "D": [-2, -1.5, 0], "E": [2, -1.5, 0]
        }
        
        # Create nodes (circles and labels)
        nodes = VGroup()
        node_labels = VGroup()
        node_objects = {}
        for name, pos in node_positions.items():
            circle = Circle(radius=0.4, color=BLUE, fill_opacity=0.8)
            circle.move_to(pos)
            label = Text(name, font_size=24).move_to(circle.get_center())
            nodes.add(circle)
            node_labels.add(label)
            node_objects[name] = VGroup(circle, label)

        # Edge definitions (node1, node2, weight)
        edge_data = [
            ("A", "B", 4), ("A", "D", 2), ("B", "C", 3),
            ("B", "D", 5), ("C", "E", 1), ("D", "E", 6)
        ]

        # Create edges and weights
        edges = VGroup()
        edge_weights = VGroup()
        edge_objects = {}
        for n1, n2, weight in edge_data:
            line = Line(node_objects[n1].get_center(), node_objects[n2].get_center(), stroke_width=3, color=GRAY)
            weight_label = MathTex(str(weight), font_size=30).move_to(line.get_center() + UP*0.3 + RIGHT*0.3)
            edges.add(line)
            edge_weights.add(weight_label)
            edge_objects[(n1, n2)] = VGroup(line, weight_label)

        # Group the entire graph and position it
        graph = VGroup(edges, nodes, node_labels)
        graph.move_to(LEFT * 3).scale(0.9)
        
        self.play(Create(edges), Create(nodes), Write(node_labels), Write(edge_weights))
        self.wait(1)

        # 3. Create the Distance Table
        table_data = {
            "A": ["0", "No"], "B": [r"\infty", "No"], "C": [r"\infty", "No"],
            "D": [r"\infty", "No"], "E": [r"\infty", "No"]
        }
        
        # Create table structure
        table = VGroup()
        header = VGroup(
            Text("Node", font_size=24), Text("Distance", font_size=24), Text("Visited", font_size=24)
        ).arrange(RIGHT, buff=1)
        table.add(header)

        # Store table rows for easy access
        table_rows = {}
        for node_name in sorted(table_data.keys()):
            row = VGroup(
                Text(node_name, font_size=24),
                MathTex(table_data[node_name][0], font_size=24),
                Text(table_data[node_name][1], font_size=24)
            ).arrange(RIGHT, buff=1.5)
            table_rows[node_name] = row
            table.add(row)

        table.arrange(DOWN, buff=0.5).scale(0.8).to_edge(RIGHT, buff=0.5)
        
        self.play(Create(table))
        self.wait(2)

        # 4. Step-by-step Algorithm Execution
        
        # Helper function for highlighting
        def highlight_node(node_name, color):
            return node_objects[node_name][0].animate.set_color(color)

        # Step 0: Initialization
        step_text = Text("Step 0: Initialize. Start at Node A.", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("A", YELLOW))
        
        new_dist_A = MathTex("0", font_size=24).move_to(table_rows["A"][1].get_center())
        new_visited_A = Text("Yes", font_size=24, color=GREEN).move_to(table_rows["A"][2].get_center())
        self.play(Transform(table_rows["A"][1], new_dist_A), Transform(table_rows["A"][2], new_visited_A))
        self.wait(2)
        self.play(FadeOut(step_text))

        # Step 1: From Node A
        step_text = Text("Step 1: Update neighbors of A (B and D).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(Indicate(edge_objects[("A", "B")]), Indicate(edge_objects[("A", "D")]))
        
        # Update B
        new_dist_B = MathTex("4", font_size=24).move_to(table_rows["B"][1].get_center())
        self.play(Transform(table_rows["B"][1], new_dist_B))
        # Update D
        new_dist_D = MathTex("2", font_size=24).move_to(table_rows["D"][1].get_center())
        self.play(Transform(table_rows["D"][1], new_dist_D))
        self.wait(2)

        self.play(FadeOut(step_text))
        step_text = Text("Select unvisited node with smallest distance: D (2).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("D", YELLOW))
        new_visited_D = Text("Yes", font_size=24, color=GREEN).move_to(table_rows["D"][2].get_center())
        self.play(Transform(table_rows["D"][2], new_visited_D))
        self.wait(2)
        self.play(FadeOut(step_text))

        # Step 2: From Node D
        step_text = Text("Step 2: Update neighbors of D (B and E).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(Indicate(edge_objects[("B", "D")]), Indicate(edge_objects[("D", "E")]))
        
        # Update E
        calc_E = MathTex("2+6=8", font_size=24).next_to(table_rows["E"], LEFT)
        self.play(Write(calc_E))
        new_dist_E = MathTex("8", font_size=24).move_to(table_rows["E"][1].get_center())
        self.play(Transform(table_rows["E"][1], new_dist_E))
        self.play(FadeOut(calc_E))
        self.wait(2)

        self.play(FadeOut(step_text))
        step_text = Text("Select unvisited node with smallest distance: B (4).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("B", YELLOW))
        new_visited_B = Text("Yes", font_size=24, color=GREEN).move_to(table_rows["B"][2].get_center())
        self.play(Transform(table_rows["B"][2], new_visited_B))
        self.wait(2)
        self.play(FadeOut(step_text))

        # Step 3: From Node B
        step_text = Text("Step 3: Update neighbors of B (C).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(Indicate(edge_objects[("B", "C")]))
        
        # Update C
        calc_C = MathTex("4+3=7", font_size=24).next_to(table_rows["C"], LEFT)
        self.play(Write(calc_C))
        new_dist_C = MathTex("7", font_size=24).move_to(table_rows["C"][1].get_center())
        self.play(Transform(table_rows["C"][1], new_dist_C))
        self.play(FadeOut(calc_C))
        self.wait(2)

        self.play(FadeOut(step_text))
        step_text = Text("Select unvisited node with smallest distance: C (7).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("C", YELLOW))
        new_visited_C = Text("Yes", font_size=24, color=GREEN).move_to(table_rows["C"][2].get_center())
        self.play(Transform(table_rows["C"][2], new_visited_C))
        self.wait(2)
        self.play(FadeOut(step_text))

        # Step 4: From Node C
        step_text = Text("Step 4: Update neighbors of C (E).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(Indicate(edge_objects[("C", "E")]))
        
        # Check E: current is 8. Path via C is 7+1=8. No change.
        calc_E_check = MathTex("7+1=8", font_size=24).next_to(table_rows["E"], LEFT)
        self.play(Write(calc_E_check))
        self.play(Indicate(table_rows["E"][1]))
        self.play(FadeOut(calc_E_check))
        self.wait(2)

        self.play(FadeOut(step_text))
        step_text = Text("Select unvisited node with smallest distance: E (8).", font_size=24).to_edge(DOWN)
        self.play(Write(step_text))
        self.play(highlight_node("E", YELLOW))
        new_visited_E = Text("Yes", font_size=24, color=GREEN).move_to(table_rows["E"][2].get_center())
        self.play(Transform(table_rows["E"][2], new_visited_E))
        self.wait(2)
        self.play(FadeOut(step_text))

        # 5. Conclusion
        final_text = Text("Algorithm complete! Final distances found.", font_size=28, color=YELLOW)
        final_text.to_edge(DOWN, buff=1.0)
        self.play(Write(final_text))
        self.wait(3)

        # Fade out everything for summary
        self.play(FadeOut(graph), FadeOut(table), FadeOut(final_text), FadeOut(title))

        summary_title = Text("Dijkstra's Algorithm: Summary", font_size=36).to_edge(UP)
        summary_points = VGroup(
            Text("1. Starts at a source node (distance 0).", font_size=28),
            Text("2. Maintains a set of visited nodes.", font_size=28),
            Text("3. Iteratively selects the unvisited node with the lowest distance.", font_size=28),
            Text("4. Updates distances of neighbors if a shorter path is found.", font_size=28)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(summary_title, DOWN, buff=1.0)
        
        summary = VGroup(summary_title, summary_points)
        self.play(Write(summary))
        self.wait(4)
        self.play(FadeOut(summary))
        self.wait(2)