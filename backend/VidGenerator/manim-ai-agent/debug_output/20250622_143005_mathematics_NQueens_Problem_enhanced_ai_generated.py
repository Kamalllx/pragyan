from manim import *

class NQueensProblemScene(Scene):
    """
    An animation explaining the N-Queens problem for beginners.
    This scene visualizes the problem on a 4x4 chessboard and demonstrates
    the backtracking algorithm to find a solution.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("The N-Queens Problem", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Introduction to the problem
        problem_text = Text(
            "Goal: Place N queens on an N×N chessboard so that\n"
            "no two queens can attack each other.",
            font_size=24,
            line_spacing=0.8
        ).next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(problem_text))
        self.wait(2)
        self.play(FadeOut(problem_text))

        # 2. Main educational content: Setting up the board
        N = 4
        board_size = 4.0
        square_size = board_size / N
        board = self.create_chessboard(N, square_size)
        board.move_to(ORIGIN).shift(LEFT * 2)

        board_label = Text(f"Let's solve for N = {N}", font_size=24).next_to(board, UP, buff=0.5)

        self.play(Create(board), Write(board_label))
        self.wait(1)

        # 3. Key Concepts with clear explanations
        rules_title = Text("The Rules:", font_size=28).to_edge(RIGHT).shift(UP * 2)
        rule1 = Text("1. One queen per row", font_size=24)
        rule2 = Text("2. One queen per column", font_size=24)
        rule3 = Text("3. One queen per diagonal", font_size=24)
        rules = VGroup(rule1, rule2, rule3).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        rules.next_to(rules_title, DOWN, buff=0.5)
        
        rules_group = VGroup(rules_title, rules).shift(RIGHT * 2.5)

        self.play(Write(rules_group))
        self.wait(2)

        # 4. Example: Backtracking Algorithm Visualization
        # Queen representation
        queen = self.create_queen()

        # Store placed queens
        placed_queens = []
        
        # --- Column 1 ---
        # Place Q1 at (0,0)
        q1_pos = self.get_square_center(board, 0, 0, square_size)
        q1 = queen.copy().move_to(q1_pos)
        placed_queens.append(q1)
        self.play(FadeIn(q1, scale=0.5))
        self.wait(0.5)

        # --- Column 2 ---
        # Try (1,0) - Fails (row attack)
        q2_try1_pos = self.get_square_center(board, 1, 0, square_size)
        q2_try1 = queen.copy().move_to(q2_try1_pos)
        self.play(FadeIn(q2_try1, scale=0.5))
        attack_line_row = Line(q1.get_center(), q2_try1.get_center(), color=RED, stroke_width=6)
        self.play(Create(attack_line_row))
        self.play(FadeOut(q2_try1), FadeOut(attack_line_row))
        self.wait(0.5)

        # Try (1,1) - Fails (diagonal attack)
        q2_try2_pos = self.get_square_center(board, 1, 1, square_size)
        q2_try2 = queen.copy().move_to(q2_try2_pos)
        self.play(FadeIn(q2_try2, scale=0.5))
        attack_line_diag = Line(q1.get_center(), q2_try2.get_center(), color=RED, stroke_width=6)
        self.play(Create(attack_line_diag))
        self.play(FadeOut(q2_try2), FadeOut(attack_line_diag))
        self.wait(0.5)

        # Place Q2 at (1,2) - Safe
        q2_pos = self.get_square_center(board, 1, 2, square_size)
        q2 = queen.copy().move_to(q2_pos)
        placed_queens.append(q2)
        self.play(FadeIn(q2, scale=0.5))
        self.wait(0.5)

        # --- Column 3 ---
        # Try all positions in column 3, all fail. Show one example.
        q3_try_pos = self.get_square_center(board, 2, 1, square_size)
        q3_try = queen.copy().move_to(q3_try_pos)
        self.play(FadeIn(q3_try, scale=0.5))
        attack_line_q1 = Line(q1.get_center(), q3_try.get_center(), color=RED, stroke_width=6)
        attack_line_q2 = Line(q2.get_center(), q3_try.get_center(), color=RED, stroke_width=6)
        self.play(Create(attack_line_q1), Create(attack_line_q2))
        self.play(FadeOut(q3_try), FadeOut(attack_line_q1), FadeOut(attack_line_q2))
        self.wait(0.5)

        # Backtrack
        backtrack_text = Text("No safe spot! Backtrack...", font_size=24, color=YELLOW).next_to(board, DOWN, buff=0.5)
        self.play(Write(backtrack_text))
        self.play(Indicate(q2))
        self.play(FadeOut(q2))
        placed_queens.pop()
        self.wait(1)

        # --- Column 2 (Retry) ---
        # Place Q2 at (1,3)
        q2_new_pos = self.get_square_center(board, 1, 3, square_size)
        q2_new = queen.copy().move_to(q2_new_pos)
        placed_queens.append(q2_new)
        self.play(FadeIn(q2_new, scale=0.5))
        self.play(FadeOut(backtrack_text))
        self.wait(0.5)

        # --- Column 3 ---
        # Place Q3 at (2,1)
        q3_pos = self.get_square_center(board, 2, 1, square_size)
        q3 = queen.copy().move_to(q3_pos)
        placed_queens.append(q3)
        self.play(FadeIn(q3, scale=0.5))
        self.wait(0.5)

        # --- Column 4 ---
        # Try all positions, all fail. Show one example.
        q4_try_pos = self.get_square_center(board, 3, 3, square_size)
        q4_try = queen.copy().move_to(q4_try_pos)
        self.play(FadeIn(q4_try, scale=0.5))
        attack_line_q2 = Line(q2_new.get_center(), q4_try.get_center(), color=RED, stroke_width=6)
        attack_line_q3 = Line(q3.get_center(), q4_try.get_center(), color=RED, stroke_width=6)
        self.play(Create(attack_line_q2), Create(attack_line_q3))
        self.play(FadeOut(q4_try), FadeOut(attack_line_q2), FadeOut(attack_line_q3))
        self.wait(0.5)

        # Backtrack again
        self.play(Write(backtrack_text))
        self.play(Indicate(q3))
        self.play(FadeOut(q3), FadeOut(q2_new), FadeOut(q1))
        placed_queens.clear()
        self.play(FadeOut(backtrack_text))
        self.wait(1)
        
        # --- Start over to find a valid solution directly ---
        solution_text = Text("Let's find a valid solution!", font_size=24, color=GREEN).next_to(board, DOWN, buff=0.5)
        self.play(Write(solution_text))
        self.wait(1)

        # Solution: (0,1), (1,3), (2,0), (3,2)
        solution_coords = [(0, 1), (1, 3), (2, 0), (3, 2)]
        solution_queens = VGroup()
        for col, row in solution_coords:
            pos = self.get_square_center(board, col, row, square_size)
            q = queen.copy().move_to(pos)
            solution_queens.add(q)
            self.play(FadeIn(q, scale=0.5))
            self.wait(0.5)

        self.play(FadeOut(solution_text))
        
        # 5. Summary
        summary_text = Text("Solution Found!", font_size=36, color=GREEN)
        summary_text.next_to(board, DOWN, buff=0.5)
        self.play(Write(summary_text))
        
        final_group = VGroup(board, solution_queens)
        self.play(
            final_group.animate.scale(0.8).to_edge(LEFT, buff=1.0),
            rules_group.animate.scale(0.8).to_edge(RIGHT, buff=1.0)
        )
        
        conclusion = Text(
            "The N-Queens problem is a great example of\n"
            "solving problems with backtracking algorithms.",
            font_size=24
        ).to_edge(DOWN, buff=0.5)
        self.play(Write(conclusion))

        self.wait(3)
        
        # Fade out all elements
        self.play(
            FadeOut(title),
            FadeOut(board_label),
            FadeOut(final_group),
            FadeOut(rules_group),
            FadeOut(summary_text),
            FadeOut(conclusion)
        )
        self.wait(2)

    def create_chessboard(self, n, square_size):
        """Creates an N x N chessboard."""
        board = VGroup()
        colors = [WHITE, GRAY]
        for i in range(n):
            for j in range(n):
                square = Square(side_length=square_size)
                square.set_fill(colors[(i + j) % 2], opacity=1)
                square.set_stroke(width=1, color=BLACK)
                square.move_to(np.array([i * square_size, j * square_size, 0]))
                board.add(square)
        board.center()
        return board

    def get_square_center(self, board, col, row, square_size):
        """Gets the center coordinates of a square on the board."""
        board_center = board.get_center()
        # Board's bottom-left corner position
        bottom_left = board_center - np.array([board.width / 2, board.height / 2, 0])
        # Center of the target square
        square_center = bottom_left + np.array(
            [(col + 0.5) * square_size, (row + 0.5) * square_size, 0]
        )
        return square_center

    def create_queen(self):
        """Creates a simple visual representation of a queen."""
        # Using a simple character 'Q' for the queen
        queen = Text("♛", font_size=48, color=GOLD)
        return queen