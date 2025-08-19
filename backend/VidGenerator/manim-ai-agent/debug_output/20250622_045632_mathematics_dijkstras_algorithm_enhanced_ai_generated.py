from manim import *

class DijkstrasAlgorithmScene(Scene):
    def construct(self):
        # 1. Title introduction
        title = Text("Dijkstra's Algorithm", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        # Explanation text
        explanation = Text("Finds the shortest path between nodes in a weighted graph.", font_size=24)
        explanation.next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(explanation))
        self.wait(2)
        self.play(FadeOut(explanation))

        # 2. Create the graph
        # Node positions
        node_positions = {
            "S": [-5, 2, 0],
            "A": [-2, 3, 0],
            "B": [-2, 1, 0],
            "C": [1, 2, 0],
            "D": [1, 0, 0],
            "E": [4, 1, 0],
        }

        # Create nodes (circles) and labels
        nodes = VGroup(*[Circle(radius=0.4, color=BLUE, fill_opacity=0.8) for _ in node_positions])
        node_labels = VGroup()
        for i, (name, pos) in enumerate(node_positions.items()):
            nodes[i].move_to(pos)
            label = MathTex(name, font_size=36).move_to(pos)
            node_labels.add(label)

        # Edges and weights
        edges_info = {
            ("S", "A"): 7, ("S", "B"): 2,
            ("A", "B"): 3, ("A", "C"): 1,
            ("B", "C"): 4, ("B", "D"): 8,
            ("C", "E"): 5,
            ("D", "E"): 2,
        }

        edges = VGroup()
        edge_weights = VGroup()
        for (start_node, end_node), weight in edges_info.items():
            start_pos = node_positions[start_node]
            end_pos = node_positions[end_node]
            edge = Line(start_pos, end_pos, stroke_width=3, color=GRAY)
            edges.add(edge)

            weight_label = MathTex(str(weight), font_size=30, color=YELLOW)
            weight_label.move_to(edge.get_center() + UP * 0.3)
            edge_weights.add(weight_label)
        
        graph = VGroup(edges, nodes, node_labels, edge_weights)
        graph.move_to(ORIGIN).shift(LEFT * 2.5)

        self.play(Create(graph))
        self.wait(1)

        # 3. Create the distance table
        table_title = Text("Distance Table", font_size=28).to_edge(RIGHT, buff=1).shift(UP * 2.5)
        
        # Table structure
        rows = ["S", "A", "B", "C", "D", "E"]
        header = VGroup(
            Text("Vertex", font_size=24),
            Text("Distance", font_size=24),
            Text("Previous", font_size=24)
        ).arrange(RIGHT, buff=0.7)
        
        table = VGroup(header)
        table_data = {}

        # Initialize table with infinity
        for i, row_name in enumerate(rows):
            dist = MathTex(r"\infty", font_size=24) if row_name != "S" else MathTex("0", font_size=24)
            prev = MathTex("-", font_size=24)
            
            row_vgroup = VGroup(
                MathTex(row_name, font_size=24),
                dist,
                prev
            ).arrange(RIGHT, buff=1.2)
            
            table_data[row_name] = row_vgroup
            table.add(row_vgroup)

        table.arrange(DOWN, buff=0.4).next_to(table_title, DOWN, buff=0.5)
        
        self.play(Write(table_title), Create(table))
        self.wait(1)

        # 4. Step-by-step algorithm execution
        
        # Keep track of visited and unvisited nodes
        unvisited = {name: nodes[i] for i, name in enumerate(node_positions.keys())}
        visited_nodes = {}
        distances = {name: float('inf') for name in node_positions.keys()}
        distances["S"] = 0
        
        # Highlight start node
        start_node_obj = nodes[0]
        self.play(start_node_obj.animate.set_color(ORANGE))
        
        # Main loop
        current_node_name = "S"
        
        # --- Step 1: Process S ---
        status_text = Text(f"Current Node: {current_node_name}", font_size=24).to_edge(DOWN)
        self.play(Write(status_text))
        self.play(Indicate(nodes[0]))

        # Neighbors of S: A (7), B (2)
        # Update A
        self.play(edges[0].animate.set_color(ORANGE), run_time=0.5)
        new_dist_A = 7
        distances["A"] = new_dist_A
        new_dist_A_tex = MathTex(str(new_dist_A), font_size=24).move_to(table_data["A"][1].get_center())
        new_prev_A_tex = MathTex("S", font_size=24).move_to(table_data["A"][2].get_center())
        self.play(Transform(table_data["A"][1], new_dist_A_tex), Transform(table_data["A"][2], new_prev_A_tex))
        self.play(edges[0].animate.set_color(GRAY), run_time=0.5)

        # Update B
        self.play(edges[1].animate.set_color(ORANGE), run_time=0.5)
        new_dist_B = 2
        distances["B"] = new_dist_B
        new_dist_B_tex = MathTex(str(new_dist_B), font_size=24).move_to(table_data["B"][1].get_center())
        new_prev_B_tex = MathTex("S", font_size=24).move_to(table_data["B"][2].get_center())
        self.play(Transform(table_data["B"][1], new_dist_B_tex), Transform(table_data["B"][2], new_prev_B_tex))
        self.play(edges[1].animate.set_color(GRAY), run_time=0.5)

        # Mark S as visited
        self.play(nodes[0].animate.set_color(GREEN))
        visited_nodes["S"] = unvisited.pop("S")
        self.wait(1)

        # --- Step 2: Process B (smallest distance: 2) ---
        current_node_name = "B"
        self.play(Transform(status_text, Text(f"Current Node: {current_node_name}", font_size=24).to_edge(DOWN)))
        self.play(Indicate(nodes[2]))

        # Neighbors of B: A (2+3=5), C (2+4=6), D (2+8=10)
        # Update A
        self.play(edges[2].animate.set_color(ORANGE), run_time=0.5)
        new_dist_A = distances["B"] + 3 # 2 + 3 = 5
        if new_dist_A < distances["A"]:
            distances["A"] = new_dist_A
            new_dist_A_tex = MathTex(str(new_dist_A), font_size=24).move_to(table_data["A"][1].get_center())
            new_prev_A_tex = MathTex("B", font_size=24).move_to(table_data["A"][2].get_center())
            self.play(Transform(table_data["A"][1], new_dist_A_tex), Transform(table_data["A"][2], new_prev_A_tex))
        self.play(edges[2].animate.set_color(GRAY), run_time=0.5)

        # Update C
        self.play(edges[4].animate.set_color(ORANGE), run_time=0.5)
        new_dist_C = distances["B"] + 4 # 2 + 4 = 6
        distances["C"] = new_dist_C
        new_dist_C_tex = MathTex(str(new_dist_C), font_size=24).move_to(table_data["C"][1].get_center())
        new_prev_C_tex = MathTex("B", font_size=24).move_to(table_data["C"][2].get_center())
        self.play(Transform(table_data["C"][1], new_dist_C_tex), Transform(table_data["C"][2], new_prev_C_tex))
        self.play(edges[4].animate.set_color(GRAY), run_time=0.5)

        # Update D
        self.play(edges[5].animate.set_color(ORANGE), run_time=0.5)
        new_dist_D = distances["B"] + 8 # 2 + 8 = 10
        distances["D"] = new_dist_D
        new_dist_D_tex = MathTex(str(new_dist_D), font_size=24).move_to(table_data["D"][1].get_center())
        new_prev_D_tex = MathTex("B", font_size=24).move_to(table_data["D"][2].get_center())
        self.play(Transform(table_data["D"][1], new_dist_D_tex), Transform(table_data["D"][2], new_prev_D_tex))
        self.play(edges[5].animate.set_color(GRAY), run_time=0.5)

        # Mark B as visited
        self.play(nodes[2].animate.set_color(GREEN))
        visited_nodes["B"] = unvisited.pop("B")
        self.wait(1)

        # --- Step 3: Process A (smallest distance: 5) ---
        current_node_name = "A"
        self.play(Transform(status_text, Text(f"Current Node: {current_node_name}", font_size=24).to_edge(DOWN)))
        self.play(Indicate(nodes[1]))

        # Neighbors of A: C (5+1=6)
        self.play(edges[3].animate.set_color(ORANGE), run_time=0.5)
        new_dist_C = distances["A"] + 1 # 5 + 1 = 6
        # No update since 6 is not less than current distance 6
        self.play(Indicate(table_data["C"][1], color=RED))
        self.play(edges[3].animate.set_color(GRAY), run_time=0.5)
        
        # Mark A as visited
        self.play(nodes[1].animate.set_color(GREEN))
        visited_nodes["A"] = unvisited.pop("A")
        self.wait(1)

        # --- Step 4: Process C (smallest distance: 6) ---
        current_node_name = "C"
        self.play(Transform(status_text, Text(f"Current Node: {current_node_name}", font_size=24).to_edge(DOWN)))
        self.play(Indicate(nodes[3]))

        # Neighbors of C: E (6+5=11)
        self.play(edges[6].animate.set_color(ORANGE), run_time=0.5)
        new_dist_E = distances["C"] + 5 # 6 + 5 = 11
        distances["E"] = new_dist_E
        new_dist_E_tex = MathTex(str(new_dist_E), font_size=24).move_to(table_data["E"][1].get_center())
        new_prev_E_tex = MathTex("C", font_size=24).move_to(table_data["E"][2].get_center())
        self.play(Transform(table_data["E"][1], new_dist_E_tex), Transform(table_data["E"][2], new_prev_E_tex))
        self.play(edges[6].animate.set_color(GRAY), run_time=0.5)

        # Mark C as visited
        self.play(nodes[3].animate.set_color(GREEN))
        visited_nodes["C"] = unvisited.pop("C")
        self.wait(1)

        # --- Step 5: Process D (smallest distance: 10) ---
        current_node_name = "D"
        self.play(Transform(status_text, Text(f"Current Node: {current_node_name}", font_size=24).to_edge(DOWN)))
        self.play(Indicate(nodes[4]))

        # Neighbors of D: E (10+2=12)
        self.play(edges[7].animate.set_color(ORANGE), run_time=0.5)
        new_dist_E = distances["D"] + 2 # 10 + 2 = 12
        # No update since 12 is not less than current distance 11
        self.play(Indicate(table_data["E"][1], color=RED))
        self.play(edges[7].animate.set_color(GRAY), run_time=0.5)

        # Mark D as visited
        self.play(nodes[4].animate.set_color(GREEN))
        visited_nodes["D"] = unvisited.pop("D")
        self.wait(1)

        # --- Step 6: Process E (smallest distance: 11) ---
        current_node_name = "E"
        self.play(Transform(status_text, Text(f"Current Node: {current_node_name}", font_size=24).to_edge(DOWN)))
        self.play(Indicate(nodes[5]))
        self.play(nodes[5].animate.set_color(GREEN))
        visited_nodes["E"] = unvisited.pop("E")
        self.wait(1)

        # 5. Final path visualization
        self.play(FadeOut(status_text))
        result_text = Text("Shortest path from S to E found!", font_size=28).to_edge(DOWN)
        self.play(Write(result_text))
        self.wait(1)

        # Backtrack to find the path: E -> C -> B -> S
        path_edge_indices = [6, 4, 1] # E-C, C-B, B-S
        path_edges = VGroup(*[edges[i] for i in path_edge_indices])
        
        self.play(path_edges.animate.set_color(PURPLE).set_stroke(width=6), run_time=2)
        
        final_dist_text = MathTex(r"\text{Total Distance: } 2+4+5 = 11", font_size=36)
        final_dist_text.next_to(result_text, UP, buff=0.5)
        self.play(Write(final_dist_text))

        self.wait(2)