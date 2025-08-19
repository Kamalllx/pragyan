from manim import *

class HuffmanCodingExplained(Scene):
    def construct(self):
        """
        An animation explaining the Huffman Coding algorithm for beginners.
        """
        # ----------------------------------------------------------------
        # 1. Title and Introduction
        # ----------------------------------------------------------------
        title = Text("Huffman Coding Explained", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        intro_text = Text(
            "A lossless data compression algorithm that gives shorter codes\n"
            "to more frequent characters.",
            font_size=24,
            text_align=CENTER
        ).next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(intro_text, shift=DOWN))
        self.wait(2)

        self.play(FadeOut(intro_text))

        # ----------------------------------------------------------------
        # 2. Example Setup: Character Frequencies
        # ----------------------------------------------------------------
        data_str = "AABBBCCCCCD"
        frequencies = {"A": 2, "B": 3, "C": 5, "D": 1}
        sorted_chars = sorted(frequencies.items(), key=lambda item: item[1])

        # Create the frequency table
        table_title = Text("Step 1: Count Frequencies", font_size=32).to_edge(LEFT).shift(UP * 2.5)
        
        table = VGroup(
            VGroup(Text("Character", font_size=24), Text("Frequency", font_size=24)).arrange(RIGHT, buff=1.5),
            Line(LEFT, RIGHT).set_length(4)
        )
        for char, freq in sorted_chars:
            row = VGroup(Text(char, font_size=24), Text(str(freq), font_size=24)).arrange(RIGHT, buff=2.0)
            table.add(row)
        
        table.arrange(DOWN, buff=0.5).next_to(table_title, DOWN, buff=0.5)
        
        self.play(Write(table_title))
        self.play(Create(table))
        self.wait(2)

        # ----------------------------------------------------------------
        # 3. Building the Huffman Tree
        # ----------------------------------------------------------------
        tree_title = Text("Step 2: Build the Huffman Tree", font_size=32).to_edge(RIGHT, buff=1.0).shift(UP * 3.0)
        self.play(Write(tree_title))

        # Create initial leaf nodes from the table
        nodes = VGroup()
        for i, (char, freq) in enumerate(sorted_chars):
            node = VGroup(
                Circle(radius=0.4, color=BLUE, fill_opacity=1),
                Text(f"{char}:{freq}", font_size=24)
            )
            nodes.add(node)
        
        nodes.arrange(RIGHT, buff=0.8).next_to(tree_title, DOWN, buff=1.0)
        
        self.play(Transform(table[2:].copy(), nodes))
        self.wait(1)

        # --- Tree construction loop ---
        
        # Combine D(1) and A(2)
        node_d = nodes[0]
        node_a = nodes[1]
        self.play(Indicate(node_d), Indicate(node_a))
        
        parent1_freq = 1 + 2
        parent1_node = VGroup(
            Circle(radius=0.4, color=GREEN, fill_opacity=1),
            Text(str(parent1_freq), font_size=24)
        ).move_to((node_d.get_center() + node_a.get_center()) / 2 + UP * 1.5)

        line1_d = Line(parent1_node.get_bottom(), node_d.get_top(), buff=0.1)
        line1_a = Line(parent1_node.get_bottom(), node_a.get_top(), buff=0.1)
        label_0_da = MathTex("0").next_to(line1_d, LEFT, buff=0.1)
        label_1_da = MathTex("1").next_to(line1_a, RIGHT, buff=0.1)

        self.play(
            Create(parent1_node),
            Create(line1_d), Create(line1_a),
            Write(label_0_da), Write(label_1_da)
        )
        self.wait(1)
        
        subtree1 = VGroup(parent1_node, node_d, node_a, line1_d, line1_a, label_0_da, label_1_da)
        
        # Update node list
        remaining_nodes = VGroup(subtree1, nodes[2], nodes[3])
        self.play(remaining_nodes.animate.arrange(RIGHT, buff=1.0).next_to(tree_title, DOWN, buff=1.0))
        self.wait(1)

        # Combine new node(3) and B(3)
        node_b = remaining_nodes[1]
        self.play(Indicate(subtree1[0]), Indicate(node_b))

        parent2_freq = 3 + 3
        parent2_node = VGroup(
            Circle(radius=0.4, color=GREEN, fill_opacity=1),
            Text(str(parent2_freq), font_size=24)
        ).move_to((subtree1.get_center() + node_b.get_center()) / 2 + UP * 1.5)

        line2_sub1 = Line(parent2_node.get_bottom(), subtree1[0].get_top(), buff=0.1)
        line2_b = Line(parent2_node.get_bottom(), node_b.get_top(), buff=0.1)
        label_0_sub1b = MathTex("0").next_to(line2_sub1, LEFT, buff=0.1)
        label_1_sub1b = MathTex("1").next_to(line2_b, RIGHT, buff=0.1)

        self.play(
            Create(parent2_node),
            Create(line2_sub1), Create(line2_b),
            Write(label_0_sub1b), Write(label_1_sub1b)
        )
        self.wait(1)

        subtree2 = VGroup(parent2_node, subtree1, node_b, line2_sub1, line2_b, label_0_sub1b, label_1_sub1b)

        # Update node list
        remaining_nodes = VGroup(subtree2, remaining_nodes[2])
        self.play(remaining_nodes.animate.arrange(RIGHT, buff=1.5).next_to(tree_title, DOWN, buff=1.0))
        self.wait(1)

        # Combine C(5) and new node(6)
        node_c = remaining_nodes[1]
        self.play(Indicate(node_c), Indicate(subtree2[0]))

        root_freq = 5 + 6
        root_node = VGroup(
            Circle(radius=0.5, color=YELLOW, fill_opacity=1),
            Text(str(root_freq), font_size=24)
        ).move_to((node_c.get_center() + subtree2.get_center()) / 2 + UP * 1.5)

        line_root_c = Line(root_node.get_bottom(), node_c.get_top(), buff=0.1)
        line_root_sub2 = Line(root_node.get_bottom(), subtree2[0].get_top(), buff=0.1)
        label_0_root = MathTex("0").next_to(line_root_c, LEFT, buff=0.1)
        label_1_root = MathTex("1").next_to(line_root_sub2, RIGHT, buff=0.1)

        self.play(
            Create(root_node),
            Create(line_root_c), Create(line_root_sub2),
            Write(label_0_root), Write(label_1_root)
        )
        self.wait(1)

        final_tree = VGroup(root_node, subtree2, node_c, line_root_c, line_root_sub2, label_0_root, label_1_root)
        self.play(final_tree.animate.move_to(ORIGIN).shift(RIGHT * 2.5).scale(0.9))
        self.wait(2)

        # ----------------------------------------------------------------
        # 4. Generate Codes
        # ----------------------------------------------------------------
        self.play(FadeOut(table), FadeOut(table_title))

        code_title = Text("Step 3: Generate Codes", font_size=32).to_edge(LEFT).shift(UP * 2.5)
        self.play(Write(code_title))

        # Create code table
        code_table = Table(
            [["C", "0"],
             ["B", "11"],
             ["A", "101"],
             ["D", "100"]],
            row_labels=[Text("C"), Text("B"), Text("A"), Text("D")],
            col_labels=[Text("Char"), Text("Code")],
            include_outer_lines=True
        ).scale(0.5).next_to(code_title, DOWN, buff=0.5)

        self.play(Create(code_table.get_horizontal_lines()), Create(code_table.get_vertical_lines()))
        self.play(Write(code_table.get_col_labels()), Write(code_table.get_row_labels()))
        
        # Trace paths and fill table
        path_c = VGroup(line_root_c)
        self.play(ShowPassingFlash(path_c.copy().set_color(ORANGE), time_width=0.5))
        self.play(Write(code_table.get_entries((1,2))))
        self.wait(0.5)

        path_b = VGroup(line_root_sub2, line2_b)
        self.play(ShowPassingFlash(path_b.copy().set_color(ORANGE), time_width=0.5))
        self.play(Write(code_table.get_entries((2,2))))
        self.wait(0.5)

        path_a = VGroup(line_root_sub2, line2_sub1, line1_a)
        self.play(ShowPassingFlash(path_a.copy().set_color(ORANGE), time_width=0.5))
        self.play(Write(code_table.get_entries((3,2))))
        self.wait(0.5)

        path_d = VGroup(line_root_sub2, line2_sub1, line1_d)
        self.play(ShowPassingFlash(path_d.copy().set_color(ORANGE), time_width=0.5))
        self.play(Write(code_table.get_entries((4,2))))
        self.wait(1)

        # ----------------------------------------------------------------
        # 5. Summary and Compression Result
        # ----------------------------------------------------------------
        summary_group = VGroup()
        
        result_title = Text("Result: Compression", font_size=32).next_to(code_table, DOWN, buff=1.0).align_to(code_table, LEFT)
        
        original_text = MathTex(r"\text{Original (ASCII, 8 bits/char): } 11 \times 8 = 88 \text{ bits}", font_size=28)
        compressed_text = MathTex(r"\text{Compressed (Huffman): } (5\times1) + (3\times2) + (2\times3) + (1\times3) = 20 \text{ bits}", font_size=28)
        
        summary_group.add(result_title, original_text, compressed_text)
        summary_group.arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(code_table, DOWN, buff=1.0)
        
        self.play(Write(result_title))
        self.play(Write(original_text))
        self.wait(1)
        self.play(Write(compressed_text))
        self.wait(2)

        # Final fade out
        self.play(
            FadeOut(final_tree),
            FadeOut(code_table),
            FadeOut(code_title),
            FadeOut(summary_group)
        )
        
        conclusion = Text(
            "Frequent characters get short codes.\n"
            "Infrequent characters get long codes.",
            font_size=36,
            text_align=CENTER
        ).move_to(ORIGIN)
        
        self.play(Write(conclusion))
        self.wait(3)
        self.play(FadeOut(conclusion), FadeOut(title))
        self.wait(2)