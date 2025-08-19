from manim import *

class ChemistryTest(Scene):
    def construct(self):
        # Title
        title = Text("H₂O Formation Animation", font_size=40, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        self.wait(0.5)
        
        # Create hydrogen atoms
        h1 = Circle(radius=0.4, color=WHITE, fill_opacity=0.9)
        h1_label = Text("H", font_size=24, color=BLACK)
        h1_atom = Group(h1, h1_label)
        h1_atom.move_to(LEFT * 4 + DOWN * 1)
        
        h2 = Circle(radius=0.4, color=WHITE, fill_opacity=0.9)
        h2_label = Text("H", font_size=24, color=BLACK)
        h2_atom = Group(h2, h2_label)
        h2_atom.move_to(RIGHT * 4 + DOWN * 1)
        
        # Create oxygen atom
        o = Circle(radius=0.6, color=RED, fill_opacity=0.9)
        o_label = Text("O", font_size=28, color=WHITE)
        o_atom = Group(o, o_label)
        o_atom.move_to(UP * 2)
        
        # Show atoms appearing
        self.play(FadeIn(h1_atom), FadeIn(h2_atom), FadeIn(o_atom))
        self.wait(1)
        
        # Move atoms together
        self.play(
            h1_atom.animate.move_to(LEFT * 1.2 + DOWN * 0.8),
            h2_atom.animate.move_to(RIGHT * 1.2 + DOWN * 0.8),
            o_atom.animate.move_to(UP * 0.5)
        )
        
        # Create bonds
        bond1 = Line(h1_atom.get_center(), o_atom.get_center(), 
                    color=YELLOW, stroke_width=6)
        bond2 = Line(h2_atom.get_center(), o_atom.get_center(), 
                    color=YELLOW, stroke_width=6)
        
        self.play(Create(bond1), Create(bond2))
        
        # Final molecule label
        molecule_label = Text("H₂O - Water Molecule", font_size=32, color=GREEN)
        molecule_label.to_edge(DOWN)
        self.play(Write(molecule_label))
        
        self.wait(2)

class PhysicsTest(Scene):
    def construct(self):
        # Title
        title = Text("Projectile Motion", font_size=40, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        # Create axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 6, 1],
            x_length=8,
            y_length=5
        ).to_edge(DOWN)
        
        self.play(Create(axes))
        
        # Create projectile
        ball = Circle(radius=0.2, color=BLUE, fill_opacity=1)
        ball.move_to(axes.coords_to_point(0, 0))
        
        # Trajectory function
        def trajectory_func(t):
            x = 2 * t
            y = 2 * t - 0.5 * t**2
            return axes.coords_to_point(x, y)
        
        # Create trajectory path
        trajectory = ParametricFunction(
            lambda t: trajectory_func(t),
            t_range=[0, 4],
            color=RED,
            stroke_width=3
        )
        
        self.play(FadeIn(ball))
        self.play(Create(trajectory))
        self.play(MoveAlongPath(ball, trajectory), run_time=4)
        
        # Add equations
        equations = MathTex(
            r"x = v_0 \cos(\theta) \cdot t",
            r"y = v_0 \sin(\theta) \cdot t - \frac{1}{2}gt^2"
        ).arrange(DOWN).to_corner(UL)
        
        self.play(Write(equations))
        self.wait(2)

class MathTest(Scene):
    def construct(self):
        # Title
        title = Text("Function Transformation", font_size=40, color=BLUE)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        # Create axes
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 8, 1],
            x_length=8,
            y_length=6
        )
        
        self.play(Create(axes))
        
        # Original function
        func1 = axes.plot(lambda x: x**2, color=BLUE, x_range=[-3, 3])
        func1_label = MathTex("f(x) = x^2", color=BLUE).next_to(axes, UP, buff=0.5)
        
        self.play(Create(func1), Write(func1_label))
        self.wait(1)
        
        # Transformed function
        func2 = axes.plot(lambda x: (x-1)**2 + 2, color=RED, x_range=[-2, 4])
        func2_label = MathTex("g(x) = (x-1)^2 + 2", color=RED).next_to(func1_label, DOWN)
        
        self.play(Transform(func1, func2), Write(func2_label))
        self.wait(2)
        
        # Show transformation steps
        steps = VGroup(
            Text("1. Shift right by 1 unit", font_size=24),
            Text("2. Shift up by 2 units", font_size=24)
        ).arrange(DOWN).to_corner(UR)
        
        self.play(Write(steps))
        self.wait(2)
