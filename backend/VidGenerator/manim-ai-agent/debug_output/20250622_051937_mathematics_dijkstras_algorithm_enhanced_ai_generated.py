from manim import *

class DijkstraAlgorithmScene(Scene):
    def construct(self):
        # 0. Configuration
        # Colors for node states
        UNVISITED_COLOR = WHITE
        CURRENT_COLOR = YELLOW
        VISITED_COLOR = GREEN
        PATH_COLOR = BLUE

        # 1. Title Introduction
        title = Text("Dijkstra's Algorithm", font_size=48).to_edge(UP)
        subtitle = Text("Finding the shortest path from a starting node to all other nodes", font_size=24).next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))
        self.wait(2)
        self.play(FadeOut(subtitle))

        # 2. Graph Setup
        # Define node positions
        node_positions = {
            "A": LEFT * 4.5,
            "B": LEFT * 2 + UP * 2,
            "C": RIGHT * 2 + UP * 2,
            "D": RIGHT * 4.5,
            "E": ORIGIN + DOWN * 1.5,
        }

        # Create nodes (circles and labels)
        nodes = VGroup()
        node_objects = {}
        for name, pos in node_positions.items():
            node_circle = Circle(radius=0.4, color=UNVISITED_COLOR, fill_opacity=0.8)
            node_label = Text(name, font_size=24).move_to(node_circle.get_center())
            node_group = VGroup(node_circle, node_label).move_to(pos)
            nodes.add(node_group)
            node_objects[name] = node_group

        # Define edges and weights
        edge_data = {
            ("A", "B"): 6, ("A", "E"): 1,
            ("B", "C"): 5, ("B", "E"): 2,
            ("C", "D"): 5, ("C", "E"): 2,
            ("D", "E"): 1,
        }

        # Create edges (lines and weight labels)
        edges = VGroup()
        edge_objects = {}
        for (u, v), weight in edge_data.items():
            line = Line(node_objects[u].get_center(), node_objects[v].get_center(), stroke_width=3, z_index=-1)
            weight_label = MathTex(str(weight), font_size=30).move_to(line.get_midpoint() + line.get_unit_vector()*0.4)
            edges.add(line, weight_label)
            edge_objects[(u,v)] = line
            edge_objects[(v,u)] = line # For easy lookup

        graph = VGroup(nodes, edges).move_to(ORIGIN).shift(LEFT * 2)
        self.play(Create(graph))
        self.wait(1)

        # 3. Distance Table Setup
        table_header = VGroup(
            Text("Node", font_size=24),
            Text("Distance", font_size=24),
            Text("Previous", font_size=24)
        ).arrange(RIGHT, buff=0.8).to_edge(RIGHT, buff=1).shift(UP*2.5)

        table_rows = VGroup()
        table_entries = {}
        node_names = ["A", "B", "C", "D", "E"]
        for i, name in enumerate(node_names):
            dist = "0" if name == "A" else r"\infty"
            prev = "-"
            row = VGroup(
                Text(name, font_size=24),
                MathTex(dist, font_size=24),
                Text(prev, font_size=24)
            ).arrange(RIGHT, buff=1.2)
            table_rows.add(row)
            table_entries[name] = row

        table_rows.arrange(DOWN, buff=0.5).next_to(table_header, DOWN, buff=0.5)
        table = VGroup(table_header, table_rows)
        self.play(Write(table))
        self.wait(2)

        # 4. Algorithm Walkthrough
        
        # Helper function for animation steps
        def visit_node(node_name, neighbors_data):
            # Announce current node
            status_text = Text(f"Current Node: {node_name}", font_size=28).to_edge(DOWN, buff=0.5)
            self.play(Write(status_text))
            self.play(node_objects[node_name].animate.set_color(CURRENT_COLOR))
            self.wait(1)

            # Update neighbors
            current_dist = float(table_entries[node_name][1].tex_string)
            for neighbor, edge_weight, new_dist, new_prev in neighbors_data:
                edge_line = edge_objects[(node_name, neighbor)]
                self.play(Indicate(edge_line))
                
                old_dist_obj = table_entries[neighbor][1]
                old_dist_val = float('inf') if old_dist_obj.tex_string == r"\infty" else float(old_dist_obj.tex_string)

                # Show calculation
                calc_text = MathTex(f"{current_dist} + {edge_weight} = {new_dist}", font_size=28)
                calc_text.next_to(table_entries[neighbor], LEFT, buff=0.5)
                self.play(Write(calc_text))
                self.wait(0.5)

                if new_dist < old_dist_val:
                    # Update is needed
                    update_text = Text("New shortest path!", font_size=24, color=GREEN).next_to(calc_text, DOWN)
                    self.play(Write(update_text))
                    
                    new_dist_tex = MathTex(str(new_dist), font_size=24).move_to(table_entries[neighbor][1])
                    new_prev_tex = Text(new_prev, font_size=24).move_to(table_entries[neighbor][2])
                    
                    self.play(
                        Transform(table_entries[neighbor][1], new_dist_tex),
                        Transform(table_entries[neighbor][2], new_prev_tex)
                    )
                    table_entries[neighbor][1].tex_string = str(new_dist) # Update internal value for next steps
                else:
                    # No update
                    no_update_text = Text("Not shorter.", font_size=24, color=RED).next_to(calc_text, DOWN)
                    self.play(Write(no_update_text))

                self.wait(1)
                self.play(FadeOut(calc_text), FadeOut(update_text if 'update_text' in locals() else no_update_text))

            # Mark as visited
            self.play(node_objects[node_name].animate.set_color(VISITED_COLOR))
            self.play(FadeOut(status_text))
            self.wait(1)

        # Step 1: Visit A
        visit_node("A", [
            ("E", 1, 1, "A"),
            ("B", 6, 6, "A")
        ])

        # Step 2: Visit E (smallest distance: 1)
        visit_node("E", [
            ("B", 2, 3, "E"), # 1+2=3 < 6
            ("C", 2, 3, "E"), # 1+2=3 < inf
            ("D", 1, 2, "E")  # 1+1=2 < inf
        ])

        # Step 3: Visit D (smallest distance: 2)
        visit_node("D", [
            ("C", 5, 7, "D") # 2+5=7 not < 3
        ])

        # Step 4: Visit B (smallest distance: 3)
        visit_node("B", [
            ("C", 5, 8, "B") # 3+5=8 not < 3
        ])

        # Step 5: Visit C (smallest distance: 3)
        visit_node("C", []) # No unvisited neighbors

        # Algorithm finished
        finish_text = Text("Algorithm Finished!", font_size=36, color=GREEN).to_edge(DOWN, buff=0.5)
        self.play(Write(finish_text))
        self.wait(2)
        self.play(FadeOut(finish_text))

        # 5. Result Interpretation
        self.play(FadeOut(table))
        
        result_title = Text("Shortest Path from A to D", font_size=32).to_edge(UP, buff=1.0)
        self.play(Transform(title, result_title), FadeOut(subtitle))

        # Trace path D <- E <- A
        path_D_E = DashedLine(node_objects["D"].get_center(), node_objects["E"].get_center(), color=PATH_COLOR, stroke_width=8)
        path_E_A = DashedLine(node_objects["E"].get_center(), node_objects["A"].get_center(), color=PATH_COLOR, stroke_width=8)
        
        path_text = MathTex(r"A \rightarrow E \rightarrow D", font_size=36).next_to(graph, DOWN, buff=0.5)
        cost_text = MathTex(r"\text{Total Cost: } 1 + 1 = 2", font_size=36).next_to(path_text, DOWN)
        
        self.play(Create(path_D_E))
        self.wait(0.5)
        self.play(Create(path_E_A))
        self.wait(0.5)
        self.play(Write(path_text))
        self.play(Write(cost_text))

        self.wait(3)

        # 6. Summary
        self.play(FadeOut(graph, path_text, cost_text, path_D_E, path_E_A))
        
        summary_title = Text("Dijkstra's Algorithm: Key Ideas", font_size=36).to_edge(UP, buff=1.0)
        self.play(Transform(title, summary_title))

        summary_points = VGroup(
            Text("1. Initialize distances: 0 for start, infinity for others.", font_size=28),
            Text("2. Maintain a set of unvisited nodes.", font_size=28),
            Text("3. Select the unvisited node with the lowest distance.", font_size=28),
            Text("4. For the current node, consider all its unvisited neighbors.", font_size=28),
            Text("5. Update neighbor distances if a shorter path is found.", font_size=28),
            Text("6. Mark the current node as visited and repeat.", font_size=28)
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to(ORIGIN)

        self.play(Write(summary_points))
        self.wait(5)
        
        self.play(FadeOut(title), FadeOut(summary_points))
        self.wait(2)