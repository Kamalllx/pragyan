An expert Manim animation developer with REINFORCEMENT LEARNING capabilities.
You have learned from 0 previous errors and 2 successful patterns.

GENERATION PARAMETERS:
Subject: general
Topic: Explain Educational Content
Complexity Level: intermediate
Specific Requirements: Explain Educational Content




=== LAYOUT OPTIMIZATION (ANTI-OVERLAP) ===
- Keep elements within frame boundaries
  Example: .move_to(ORIGIN)
- Use DOWN, UP, LEFT, RIGHT for positioning
  Example: .shift(DOWN * 2)
- Maintain minimum spacing of 0.5 units
  Example: .arrange(DOWN, buff=0.5)
- Group related elements using VGroup
  Example: VGroup(obj1, obj2)
- Use .to_edge() for frame-relative positioning
  Example: .to_edge(UP)



=== PROVEN SUCCESS PATTERNS ===
- general - Nuclear fission in Hindi: Quality 96.2/100
- general - Friction: Quality 96.05/100


SUBJECT-SPECIFIC CONTEXT:
Create educational content with clear explanations

COMPLEXITY INSTRUCTIONS:
Include moderate complexity, some mathematical formulas, and detailed explanations

ENHANCED TECHNICAL REQUIREMENTS WITH ERROR PREVENTION:

✅ MANDATORY API COMPATIBILITY (Zero Tolerance):
- Use ONLY modern Manim v0.19.0 API methods
- Start with: from manim import *
- Create a complete Scene class with construct method
- Use Text() for simple text, MathTex() for math (KEEP SIMPLE!)
- Use basic shapes: Circle, Rectangle, Triangle, Line, Polygon
- Use VGroup for grouping objects
- Use animations: Write, Create, FadeIn, FadeOut, Transform, Indicate
- Include proper self.wait() statements between animations
- End with self.wait(2)

❌ ABSOLUTELY FORBIDDEN (LEARNED FROM ERRORS):
- get_sides() method - DOES NOT EXIST
- get_part_by_text() method - DOES NOT EXIST  
- get_part_by_tex() method - DOES NOT EXIST
- Indicate(obj, color=X) - color parameter NOT SUPPORTED
- text_alignment= - use text_align=
- Empty MathTex like r"\\text{}" - CAUSES COMPILATION ERRORS
- Complex nested LaTeX - KEEP SIMPLE

🎯 LAYOUT MANAGEMENT (ANTI-OVERLAP SYSTEM):
- Use VGroup for organizing multiple objects
- Apply .arrange(DOWN, buff=0.8) for vertical spacing
- Apply .arrange(RIGHT, buff=1.2) for horizontal spacing  
- Use .to_edge(UP/DOWN/LEFT/RIGHT) for frame positioning
- Keep objects within frame: -7 < x < 7, -4 < y < 4
- Minimum spacing between objects: 1.0 units
- Use .next_to() with proper buff parameter
- Group related elements before positioning

📐 FRAME SAFETY SYSTEM:
- Text objects: Use font_size=24 or smaller
- Positions: Stay within safe zone [-6, 6] x [-3.5, 3.5]
- Use .scale(0.8) if objects appear too large
- Test positioning with .move_to(ORIGIN) first
- Use .shift() for fine adjustments only

🎨 ANIMATION STRUCTURE FOR EXPLAIN EDUCATIONAL CONTENT IN GENERAL:
1. Title introduction (positioned safely at TOP)
2. Main educational content with visual demonstrations
3. Key concepts with clear explanations (proper spacing)
4. Examples or applications (organized layout)
5. Summary or conclusion (bottom positioning)

SPECIFIC CONTENT GENERATION FOR "Explain Educational Content" IN general:
- Create educational content specifically about Explain Educational Content
- Make it appropriate for intermediate level learners
- Include visual representations relevant to the topic
- Add clear explanations and demonstrations
- Follow spacing and positioning rules above
- Explain Educational Content

QUALITY ASSURANCE CHECKLIST:
□ All objects positioned with adequate spacing
□ No overlapping elements
□ Frame boundaries respected
□ VGroup used for organization
□ Modern Manim API only
□ LaTeX kept simple and safe
□ Proper wait() statements included
□ Educational value maximized

Generate a COMPLETE, SAFE, LEARNING-ENHANCED Manim animation that educates about Explain Educational Content in general:
```python
from manim import *

class PythagoreanTheoremExplanation(Scene):
    """
    An intermediate-level animation explaining the Pythagorean Theorem
    using a visual proof with squares and a numerical example.
    """
    def construct(self):
        # 1. Title Introduction
        title = Text("The Pythagorean Theorem", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # 2. Main Content: Introduce the triangle and the formula
        intro_text = Text(
            "For any right-angled triangle:",
            font_size=28
        ).next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(intro_text, shift=DOWN))
        self.wait(1)

        # Define triangle vertices for a 3-4-5 triangle
        A = LEFT * 2 + DOWN * 1.5
        B = A + RIGHT * 4  # Side length = 4
        C = A + UP * 3     # Side length = 3
        
        # Create the triangle and its right-angle mark
        triangle = Polygon(A, B, C, color=BLUE, fill_opacity=0.5)
        right_angle = Square(side_length=0.4, color=WHITE).move_to(A, aligned_edge=UR)

        # Create labels for the sides
        side_a = Line(A, C)
        side_b = Line(A, B)
        side_c = Line(B, C)
        
        label_a = MathTex("a").next_to(side_a, LEFT, buff=0.3)
        label_b = MathTex("b").next_to(side_b, DOWN, buff=0.3)
        label_c = MathTex("