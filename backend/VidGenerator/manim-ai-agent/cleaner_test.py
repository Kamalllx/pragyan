from script_cleaner import ScriptCleaner

def test_with_your_script():
    """Test with your actual problematic script"""
    
    raw_script = '''Educational Script - English (Indian)
Generated: 2025-06-22 04:22:52.021809
Subject: physics
Topic: newtons laws
==================================================

Here is the educational narration script for a Manim animation on Newton's Laws of Motion. --- # Educational Narration Script: Newton's Laws of Motion Video Duration: 66.0 seconds Target Audience: Beginner level students (Indian context) Narration Style: Professional, friendly, and clear educational tone. (Begin Script) | Timestamp | Scene Description (For Manim Animator) | Narration | | :--- | :--- | :--- | | 00:00 - 00:07 | [SCENE START]<br>An engaging intro sequence. The words "Newton's Laws of Motion" animate onto the screen. A stylized apple falls next to a silhouette of Sir Isaac Newton. | Hello friends! Ever wondered why things move the way they do? From a cricket ball to the planets, everything follows three simple rules discovered by Sir Isaac Newton. Let's understand them! | | 00:07 - 00:20 | [VISUAL]<br>Title: "First Law: The Law of Inertia". A football is shown at rest on a field. A foot icon appears and gently taps it. The ball starts rolling and continues to roll at a constant speed. | First, we have the Law of Inertia. It says an object will stay at rest, or keep moving at a constant speed, unless an external force acts on it. This resting football only moves when it is kicked! | | 00:20 - 00:38 | [VISUAL]<br>Title: "Second Law: Force, Mass & Acceleration". A block with mass 'm' is shown. A small arrow representing 'Force' pushes it, and it accelerates slowly. Then, a much larger arrow pushes it, and it accelerates quickly. The formula F = m × a appears and highlights each component. | Next is the Second Law, which connects force, mass, and acceleration. The formula is Force equals Mass times Acceleration. This means if you apply more force to an object, it will speed up faster! Think of hitting a cricket ball – a harder hit sends it flying further and faster! | | 00:38 - 00:52 | [VISUAL]<br>Title: "Third Law: Action & Reaction". A simple rocket is shown on a launchpad. It ignites, showing a strong downward arrow labeled "Action (Gas Push)". An equally strong upward arrow appears labeled "Reaction (Rocket Moves Up)", and the rocket lifts off. | And finally, the Third Law. This one is simple: For every action, there is an equal and opposite reaction. When a rocket pushes hot gas downwards—that's the action—the gas pushes the rocket upwards with equal force—that's the reaction! | | 00:52 - 01:06 | [VISUAL]<br>A summary screen appears with three columns. Each column has an icon and a keyword:<br>1. Icon: A resting book. Keyword: Inertia<br>2. Icon: The formula F=ma. Keyword: Acceleration<br>3. Icon: Two opposing arrows. Keyword: Action-Reaction<br>The video ends with a "Keep Exploring!" message. | So, to summarise: The First Law is about inertia. The Second Law tells us that Force equals Mass times Acceleration. And the Third Law is about action and reaction. These three laws are the foundation of physics and explain motion all around us. Keep asking questions and keep learning! | (End Script).'''
    
    cleaner = ScriptCleaner()
    clean_narration = cleaner.extract_clean_narration(raw_script)
    
    print("🎯 EXPECTED CLEAN OUTPUT:")
    print("Hello friends! Ever wondered why things move the way they do? From a cricket ball to the planets, everything follows three simple rules discovered by Sir Isaac Newton. Let's understand them! First, we have the Law of Inertia...")
    
    print(f"\n✅ ACTUAL CLEAN OUTPUT:")
    print(f"Length: {len(clean_narration)} characters")
    print(f"Content: {clean_narration}")
    
    print(f"\n🔍 QUALITY CHECK:")
    print(f"Starts correctly: {'Hello friends' in clean_narration}")
    print(f"No table artifacts: {'|' not in clean_narration}")
    print(f"No timestamps: {not any(c.isdigit() and ':' in clean_narration[i:i+5] for i, c in enumerate(clean_narration))}")
    print(f"No scene descriptions: {'[SCENE' not in clean_narration and '[VISUAL' not in clean_narration}")

if __name__ == "__main__":
    test_with_your_script()
