```python
from manim import *

class MarkovChainExample(Scene):
    def construct(self):
        # Set a consistent color scheme
        sunny_color = YELLOW_C
        rainy_color = BLUE_C
        text_color = WHITE

        # --- 1. Title ---
        title = Text("Markov Chains: A Simple Example", font_size=40)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        # --- 2. Introduction of States ---
        # Create nodes for "Sunny" and "Rainy" states
        sunny_node = Circle(radius=0.8, color=sunny_color, fill_opacity=0.5)
        sunny_label = Text("Sunny", color=text_color).move_to(sunny_node.get_center())
        sunny_state = VGroup(sunny_node, sunny_label).shift(LEFT * 3)

        rainy_node = Circle(radius=0.8, color=rainy_color, fill_opacity=0.5)
        rainy_label = Text("Rainy", color=text_color).move_to(rainy_node.get_center())
        rainy_state = VGroup(rainy_node, rainy_label).shift(RIGHT * 3)

        # Display the states
        self.play(Create(sunny_state), Create(rainy_state))
        self.wait(1)

        # --- 3. Transition Probabilities ---
        # Create arrows and labels for probabilities
        # Sunny to Sunny (loop)
        arrow_ss = Arrow(sunny_node.get_top(), sunny_node.get_top() + UP * 1.5, buff=0.2).scale(0.6, scale_tips=True)
        arrow_ss.tip.move_to(sunny_node.get_top())
        prob_ss = MathTex("0.9", color=text_color).next_to(arrow_ss, UP)

        # Sunny to Rainy
        arrow_sr = Arrow(sunny_state.get_right(), rainy_state.get_left(), buff=0.2, color=text_color)
        prob_sr = MathTex("0.1", color=text_color).next_to(arrow_sr, UP, buff=0.1)

        # Rainy to Rainy (loop)
        arrow_rr = Arrow(rainy_node.get_bottom(), rainy_node.get_bottom() + DOWN * 1.5, buff=0.2).scale(0.6, scale_tips=True)
        arrow_rr.tip.move_to(rainy_node.get_bottom())
        prob_rr = MathTex("0.5", color=text_color).next_to(arrow_rr, DOWN)

        # Rainy to Sunny
        arrow_rs = Arrow(rainy_state.get_left(), sunny_state.get_right(), buff=0.2, color=text_color)
        prob_rs = MathTex("0.5", color=text_color).next_to(arrow_rs, DOWN, buff=0.1)

        # Animate the transitions
        self.play(
            GrowArrow(arrow_ss), Write(prob_ss),
            GrowArrow(arrow_sr), Write(prob_sr),
            GrowArrow(arrow_rr), Write(prob_rr),
            GrowArrow(arrow_rs), Write(prob_rs)
        )
        self.wait(2)

        # Group the entire diagram
        diagram = VGroup(sunny_state, rainy_state, arrow_ss, prob_ss, arrow_sr, prob_sr, arrow_rr, prob_rr, arrow_rs, prob_rs)

        # --- 4. Introduce State Vector and Transition Matrix ---
        self.play(diagram.animate.scale(0.7).to_edge(LEFT, buff=0.5))

        # Initial State Vector
        initial_state_text = Text("Initial State (Today is Sunny):", font_size=28).to_edge(RIGHT, buff=1).shift(UP * 2.5)
        initial_vector = MathTex(r"P_0 = \begin{bmatrix} 1 & \text{(Sunny)} \\ 0 & \text{(Rainy)} \end{bmatrix}", font_size=36).next_to(initial_state_text, DOWN, buff=0.3)
        
        self.play(Write(initial_state_text))
        self.play(Write(initial_vector))
        self.wait(2)

        # Transition Matrix
        matrix_text = Text("Transition Matrix (T):", font_size=28).move_to(initial_state_text).shift(DOWN * 2.5)
        # Note: Columns represent 'from', rows represent 'to'.
        # Col 1: From Sunny, Col 2: From Rainy
        # Row 1: To Sunny, Row 2: To Rainy
        transition_matrix = MathTex(
            r"T = \begin{bmatrix} 0.9 & 0.5 \\ 0.1 & 0.5 \end{bmatrix}",
            font_size=36
        ).next_to(matrix_text, DOWN, buff=0.3)
        
        self.play(Write(matrix_text))
        self.play(Write(transition_matrix))
        self.wait(2)

        # --- 5. The Prediction Calculation ---
        # Clear previous text and move matrix to position for calculation
        calc_group = VGroup(initial_state_text, initial_vector, matrix_text)
        self.play(FadeOut(calc_group))
        
        # Reposition matrix and vector for the calculation
        self.play(
            transition_matrix.animate.move_to(LEFT * 0.5 + DOWN * 2),
            initial_vector.animate.move_to(RIGHT * 2 + DOWN * 2)
        )
        
        # Formula for next state
        formula = MathTex(r"P_1 = T \times P_0", font_size=36).to_edge(DOWN, buff=2.5).shift(UP*0.5)
        self.play(Write(formula))
        self.wait(1)

        # Show the calculation
        equals_sign = MathTex("=", font_size=48).move_to(RIGHT * 3.5 + DOWN * 2)
        
        # Step-by-step calculation result
        result_vector = MathTex(
            r"\begin{bmatrix} (0.9 \times 1) + (0.5 \times 0) \\ (0.1 \times 1) + (0.5 \times 0) \end{bmatrix}",
            font_size=36
        ).next_to(equals_sign, RIGHT, buff=0.2)
        
        self.play(Write(equals_sign), Write(result_vector))
        self.wait(2)

        # Final result
        final_result = MathTex(r"= \begin{bmatrix} 0.9 \\ 0.1 \end{bmatrix}", font_size=36).move_to(result_vector)
        self.play(Transform(result_vector, final_result))
        self.wait(2)
        
        # --- 6. Conclusion ---
        # Explain the result
        conclusion_text = Text(
            "So, tomorrow has a 90% chance of being Sunny\nand a 10% chance of being Rainy.",
            font_size=28,
            line_spacing=0.8
        ).to_edge(DOWN, buff=1)
        
        # Create a box around the final result to highlight it
        result_box = SurroundingRectangle(result_vector, color=GREEN)
        
        self.play(FadeOut(formula, transition_matrix, initial_vector, equals_sign))
        self.play(
            VGroup(result_vector, result_box).animate.move_to(ORIGIN).scale(1.2),
            Write(conclusion_text)
        )
        self.wait(3)

        # --- 7. Final Fade Out ---
        self.play(
            FadeOut(title),
            FadeOut(diagram),
            FadeOut(result_vector),
            FadeOut(result_box),
            FadeOut(conclusion_text)
        )
        self.wait(1)
```