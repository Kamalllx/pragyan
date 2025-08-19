from manim import *

class ISROExplanationScene(Scene):
    def construct(self):
        # Set a background color
        self.camera.background_color = "#000033"

        # 1. Title Introduction
        title = Text("The Indian Space Research Organisation (ISRO)", font_size=36, color=ORANGE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Underline for the title
        underline = Line(title.get_left(), title.get_right(), color=WHITE).next_to(title, DOWN, buff=0.2)
        self.play(Create(underline))
        self.wait(2)

        # 2. ISRO's Formation and Mission
        isro_logo = ImageMobject("isro_logo.png").scale(0.5) # Assumes you have an ISRO logo file
        formation_text = Text("Formed: 1969", font_size=24).next_to(isro_logo, DOWN, buff=0.5)
        
        logo_group = VGroup(isro_logo, formation_text).move_to(LEFT * 4)

        mission_title = Text("Primary Mission:", font_size=28, color=YELLOW).to_edge(RIGHT).shift(UP * 2 + LEFT * 2)
        mission_text = Text(
            "Harness space technology for\n"
            "national development.",
            font_size=24,
            line_spacing=0.8
        ).next_to(mission_title, DOWN, buff=0.5)

        self.play(FadeIn(logo_group))
        self.wait(1)
        self.play(Write(mission_title))
        self.play(Write(mission_text))
        self.wait(3)

        self.play(FadeOut(logo_group), FadeOut(mission_title), FadeOut(mission_text))
        self.wait(1)

        # 3. Key Launch Vehicle: PSLV
        pslv_title = Text("The Workhorse: PSLV", font_size=32, color=CYAN).to_edge(UP, buff=1.5)
        self.play(Transform(title, pslv_title), FadeOut(underline))
        self.wait(1)

        # Create a simple rocket
        rocket_body = Rectangle(height=3, width=0.5, color=WHITE, fill_opacity=1)
        rocket_tip = Triangle().scale(0.25).next_to(rocket_body, UP, buff=0)
        rocket_tip.set_fill(RED, opacity=1)
        fin1 = Triangle().scale(0.3).stretch_to_fit_width(0.5).next_to(rocket_body, DOWN, buff=0).shift(LEFT*0.25)
        fin2 = fin1.copy().shift(RIGHT*0.5)
        rocket = VGroup(rocket_body, rocket_tip, fin1, fin2).move_to(ORIGIN).shift(DOWN*0.5)

        pslv_info = VGroup(
            Text("Polar Satellite Launch Vehicle", font_size=24),
            Text("Known for Reliability & Cost-Effectiveness", font_size=24),
            Text("Over 50 successful missions", font_size=24)
        ).arrange(DOWN, buff=0.5).to_edge(RIGHT, buff=1)

        self.play(Create(rocket))
        self.play(rocket.animate.shift(UP*0.2))
        self.play(Write(pslv_info))
        self.wait(3)

        self.play(FadeOut(rocket), FadeOut(pslv_info))
        self.wait(1)

        # 4. Major Missions: Chandrayaan & Mangalyaan
        missions_title = Text("Landmark Missions", font_size=32, color=GREEN).to_edge(UP, buff=1.5)
        self.play(Transform(title, missions_title))
        self.wait(1)

        # Chandrayaan (Moon Mission)
        moon = Circle(radius=1, color=GRAY, fill_opacity=1).move_to(LEFT * 3.5)
        moon_label = Text("Chandrayaan-3 (2023)", font_size=24).next_to(moon, DOWN, buff=0.5)
        lander = Polygon(
            [-0.2, 0.2, 0], [0.2, 0.2, 0], [0.1, -0.2, 0], [-0.1, -0.2, 0],
            color=GOLD, fill_opacity=1
        ).scale(0.5).move_to(moon.get_center() + UP * 1.2)
        
        self.play(Create(moon), Write(moon_label))
        self.play(lander.animate.move_to(moon.get_center() + UP * 0.5))
        self.play(Indicate(lander))
        self.wait(1)
        
        # Mangalyaan (Mars Mission)
        mars = Circle(radius=1, color=RED_B, fill_opacity=1).move_to(RIGHT * 3.5)
        mars_label = Text("Mangalyaan (2014)", font_size=24).next_to(mars, DOWN, buff=0.5)
        orbiter = Dot(color=YELLOW).scale(2).move_to(mars.get_center() + UP * 1.5)
        orbit_path = Circle(radius=1.5, color=YELLOW, stroke_width=2).move_to(mars.get_center())

        self.play(Create(mars), Write(mars_label))
        self.play(Create(orbit_path), FadeIn(orbiter))
        self.play(MoveAlongPath(orbiter, orbit_path), run_time=3, rate_func=linear)
        self.wait(2)

        missions_group = VGroup(moon, moon_label, lander, mars, mars_label, orbiter, orbit_path)
        self.play(FadeOut(missions_group))
        self.wait(1)

        # 5. The Science: Orbital Mechanics
        science_title = Text("The Science: Geosynchronous Orbit", font_size=32, color=PURPLE).to_edge(UP, buff=1.5)
        self.play(Transform(title, science_title))
        self.wait(1)

        earth = Circle(radius=1, color=BLUE, fill_opacity=1).move_to(ORIGIN)
        earth_label = Text("Earth", font_size=20).next_to(earth, DOWN)
        
        # Geosynchronous Orbit
        geo_orbit = Circle(radius=3, color=WHITE, stroke_width=2)
        satellite = Dot(point=geo_orbit.point_from_proportion(0), color=YELLOW)
        
        orbit_group = VGroup(earth, earth_label, geo_orbit, satellite)
        
        # Orbital Velocity Formula
        formula = MathTex(r"v = \sqrt{\frac{GM}{r}}", font_size=36).to_edge(DOWN, buff=1)
        formula_desc = VGroup(
            Text("v = orbital velocity", font_size=20),
            Text("G = gravitational constant", font_size=20),
            Text("M = Earth's mass, r = orbital radius", font_size=20)
        ).arrange(DOWN, buff=0.2).next_to(formula, UP, buff=0.3)

        self.play(Create(earth), Write(earth_label))
        self.play(Create(geo_orbit), FadeIn(satellite))
        self.play(Write(formula), Write(formula_desc))
        self.wait(2)
        self.play(MoveAlongPath(satellite, geo_orbit), run_time=5, rate_func=linear)
        self.wait(2)

        self.play(FadeOut(orbit_group), FadeOut(formula), FadeOut(formula_desc))
        self.wait(1)

        # 6. Conclusion
        conclusion_title = Text("ISRO: A Symbol of National Pride", font_size=32, color=GOLD).to_edge(UP, buff=1.5)
        self.play(Transform(title, conclusion_title))
        
        conclusion_points = VGroup(
            Text("• Cost-effective space exploration", font_size=28),
            Text("• Advances in science and technology", font_size=28),
            Text("• Inspiring future generations", font_size=28)
        ).arrange(DOWN, buff=0.8).move_to(ORIGIN)

        self.play(Write(conclusion_points))
        self.wait(4)

        # Final Fade Out
        self.play(FadeOut(title), FadeOut(conclusion_points))
        self.wait(2)