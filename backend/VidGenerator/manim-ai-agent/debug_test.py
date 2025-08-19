#!/usr/bin/env python3
"""
Quick debug test to isolate the layout issue
"""

def test_layout_manager():
    """Test layout manager in isolation"""
    print("🔧 Testing Layout Manager...")
    
    try:
        from layout_manager import LayoutManager
        
        # Create test code with intentional overlaps
        test_code = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        obj1 = Text("Object 1").move_to(UP)
        obj2 = Text("Object 2").move_to(UP + LEFT * 0.1)
        obj3 = Text("Object 3").move_to(UP + RIGHT * 0.1)
        obj4 = Text("Object 4").move_to(UP + DOWN * 0.1)
        '''
        
        layout_manager = LayoutManager()
        
        print("📊 Running layout analysis...")
        result = layout_manager.analyze_layout_issues(test_code)
        
        print(f"✅ Test completed!")
        print(f"   Overlaps: {len(result.get('overlapping_risks', []))}")
        print(f"   Overflows: {len(result.get('frame_overflow_risks', []))}")
        print(f"   Analysis time: {result.get('debug_info', {}).get('analysis_time', 0)}s")
        print(f"   Iterations: {result.get('debug_info', {}).get('iterations', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Layout test failed: {e}")
        return False

if __name__ == "__main__":
    test_layout_manager()
