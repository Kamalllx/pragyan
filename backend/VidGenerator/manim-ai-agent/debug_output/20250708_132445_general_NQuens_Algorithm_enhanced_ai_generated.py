from manim import *

class NQueensAlgorithmScene(Scene):
    """
    An animation explaining the N-Queens problem and the backtracking algorithm
    used to solve it, following best practices for clarity and layout.
    """
    def construct(self):
        # 1. Title and Introduction
        title = Text("The N-Queens Problem", font_size=48).to_edge(UP)
        problem_desc = Text(
            "Goal: Place N queens on an N×N chessboard such that\n"
            "no two queens can attack each other.",
            font_size=24,
            line_spacing=0.8
        ).next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(problem_desc, shift=DOWN))
        self.wait(2)
        self.play(FadeOut(problem_desc))

        # 2. Setup the Board and Queens for a 4-Queens example
        n = 4
        board = self.create_chessboard(n)
        board.scale(0.8).to_edge(LEFT, buff=1.0)
        
        self.play(Create(board))
        self.wait(1)

        # 3. Demonstrate the Backtracking Algorithm
        explanation_text = VGroup(
            Text("1. Place a queen in the first column.", font_size=24),
            Text("2. Move to the next column and find a safe spot.", font_size=24),
            Text("3. If no safe spot is found, backtrack.", font_size=24),
            Text("4. Repeat until a full solution is found.", font_size=24)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(board, RIGHT, buff=1.0)

        # Step 1: Place first queen
        q1_pos = self.get_square_center(board, 0, 1)
        q1 = self.create_queen().move_to(q1_pos)
        self.play(Write(explanation_text[0]))
        self.play(FadeIn(q1, scale=0.5))
        self.wait(1)

        # Step 2: Place second queen
        q2_pos = self.get_square_center(board, 1, 3)
        q2 = self.create_queen().move_to(q2_pos)
        self.play(Transform(explanation_text[0], explanation_text[1]))
        self.play(FadeIn(q2, scale=0.5))
        self.wait(1)

        # Step 3: Show a conflict
        q3_attempt_pos = self.get_square_center(board, 2, 0)
        q3_attempt = self.create_queen(color=RED).move_to(q3_attempt_pos)
        
        attack_line_1 = Line(q1.get_center(), q3_attempt.get_center(), color=RED, stroke_width=6)
        
        self.play(FadeIn(q3_attempt, scale=0.5))
        self.play(Create(attack_line_1))
        self.play(Indicate(q1), Indicate(q3_attempt))
        self.wait(1)
        self.play(FadeOut(q3_attempt, attack_line_1))

        # Step 4: Show backtracking
        self.play(Transform(explanation_text[0], explanation_text[2]))
        self.play(Indicate(q2))
        self.play(FadeOut(q2))
        self.wait(1)

        # Step 5: Show finding a new spot and the final solution
        self.play(Transform(explanation_text[0], explanation_text[3]))
        
        # Fade out the partial setup
        self.play(FadeOut(q1), FadeOut(explanation_text[0]))

        # Show the final solution board
        solution_queens = VGroup()
        solution_positions = [(0, 1), (1, 3), (2, 0), (3, 2)]
        for r, c in solution_positions:
            pos = self.get_square_center(board, r, c)
            solution_queens.add(self.create_queen().move_to(pos))

        solution_text = Text("A Solution is Found!", font_size=32, color=GREEN).next_to(board, RIGHT, buff=1.0)
        self.play(FadeIn(solution_queens))
        self.play(Write(solution_text))
        self.wait(3)

        # 4. Key Concepts Summary
        self.play(FadeOut(board, solution_queens, solution_text))

        summary_title = Text("Core Idea: Backtracking", font_size=36).to_edge(UP, buff=1.0)
        summary_points = VGroup(
            Text("1. Explore: Move forward by making a choice (place a queen).", font_size=24),
            Text("2. Check: Validate if the choice is safe.", font_size=24),
            Text("3. Recurse: If safe, solve for the next step.", font_size=24),
            Text("4. Backtrack: If not safe, undo the choice and try another.", font_size=24)
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).next_to(summary_title, DOWN, buff=0.8)

        summary_group = VGroup(summary_title, summary_points).move_to(ORIGIN)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_points, shift=UP, lag_ratio=0.2))
        self.wait(3)

        # 5. Conclusion
        self.play(FadeOut(summary_group))
        conclusion_text = Text(
            "The N-Queens algorithm is a classic example of\nsolving combinatorial problems with recursion.",
            font_size=28,
            line_spacing=0.8
        ).move_to(ORIGIN)
        self.play(Write(conclusion_text))
        self.wait(2)

    def create_chessboard(self, n=4, square_size=1.0):
        """Creates an N x N chessboard."""
        board = VGroup()
        colors = [WHITE, GRAY]
        for i in range(n):
            for j in range(n):
                square = Square(side_length=square_size)
                square.set_fill(colors[(i + j) % 2], opacity=1)
                square.set_stroke(width=2, color=BLACK)
                square.move_to(np.array([j, -i, 0]) * square_size)
                board.add(square)
        board.move_to(ORIGIN)
        return board

    def create_queen(self, color=YELLOW):
        """Creates a queen mobject."""
        # Using a simple MathTex for the queen symbol for compatibility
        queen = MathTex("♕", color=color)
        queen.scale(2.5) # Scale to fit nicely in a square
        return queen

    def get_square_center(self, board, row, col, n=4, square_size=1.0 * 0.8):
        """
        Calculates the center of a square on the board.
        Note: The square_size must match the scaled size used in construct.
        """
        board_center = board.get_center()
        # Top-left corner of the board
        top_left = board_center + np.array([-n/2, n/2, 0]) * square_size
        # Center of the specific square
        square_center = top_left + np.array([col + 0.5, -(row + 0.5), 0]) * square_size
        return square_center