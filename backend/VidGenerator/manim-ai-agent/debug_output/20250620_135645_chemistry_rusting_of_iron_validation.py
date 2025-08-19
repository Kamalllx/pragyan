
import sys
import os
sys.path.append(os.path.dirname(r"./debug_output\20250620_135645_chemistry_rusting_of_iron_test.py"))

# Try to import manim components used in the code
try:
    from manim import *
    import numpy as np
    import math
    print("IMPORT_SUCCESS")
except Exception as e:
    print(f"IMPORT_ERROR: {e}")
    sys.exit(1)

# Try to parse and validate the scene class
try:
    import ast
    with open(r"./debug_output\20250620_135645_chemistry_rusting_of_iron_test.py", "r") as f:
        code_content = f.read()
    
    # Parse AST and check for scene class
    tree = ast.parse(code_content)
    scene_classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "Scene":
                    scene_classes.append(node.name)
    
    if scene_classes:
        print(f"SCENE_CLASS_FOUND: {scene_classes[0]}")
    else:
        print("SCENE_CLASS_ERROR: No Scene class found")
    
except Exception as e:
    print(f"VALIDATION_ERROR: {e}")
