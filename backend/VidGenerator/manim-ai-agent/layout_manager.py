import re
import ast
from typing import Dict, List, Tuple, Optional
from utils import setup_logger
import time

class LayoutManager:
    """
    Manages layout and positioning to prevent overlapping and frame overflow issues.
    Enhanced with comprehensive debugging and loop prevention.
    """
    
    def __init__(self):
        """Initialize the layout manager"""
        self.logger = setup_logger("layout_manager")
        
        # Frame dimensions (Manim default)
        self.frame_width = 14.22
        self.frame_height = 8.0
        
        # Safe margins
        self.margin_x = 1.0
        self.margin_y = 0.8
        
        # Object tracking
        self.placed_objects = []
        self.object_sizes = {}
        
        # Debug and performance tracking
        self.debug_mode = True
        self.max_fix_iterations = 5  # Prevent infinite loops
        self.analysis_timeout = 30  # seconds
        
        # Layout patterns
        self.layout_patterns = {
            'title_content': {'title_y': 3.0, 'content_start_y': 1.5},
            'multi_column': {'column_spacing': 4.0, 'row_spacing': 1.5},
            'equation_demo': {'equation_y': 1.0, 'demo_y': -1.5},
            'step_by_step': {'step_spacing': 1.2, 'indent': 2.0}
        }
        
        self.logger.info("Layout Manager initialized with enhanced debugging")
    
    def analyze_layout_issues(self, code: str) -> Dict:
        """
        Analyze code for potential layout issues with comprehensive debugging
        """
        if self.debug_mode:
            print(f"\n🔍 Starting layout analysis...")
            print(f"   Code length: {len(code)} characters")
        
        start_time = time.time()
        
        issues = {
            'overlapping_risks': [],
            'frame_overflow_risks': [],
            'positioning_improvements': [],
            'layout_suggestions': [],
            'fixed_code': code,
            'debug_info': {
                'analysis_time': 0,
                'iterations': 0,
                'fixes_applied': 0
            }
        }
        
        try:
            # Parse code to extract positioning information
            if self.debug_mode:
                print(f"   📊 Extracting positioning information...")
            
            positioning_info = self._extract_positioning_info(code)
            
            if self.debug_mode:
                print(f"   Found {len(positioning_info)} positioned objects")
                for i, pos in enumerate(positioning_info[:3]):  # Show first 3
                    print(f"      {i+1}. {pos['object']}: {pos['method']} -> {pos['estimated_coords']}")
                if len(positioning_info) > 3:
                    print(f"      ... and {len(positioning_info) - 3} more")
            
            # Check for overlapping risks with timeout
            if self.debug_mode:
                print(f"   🔍 Checking for overlapping risks...")
            
            overlapping = self._detect_potential_overlapping_with_timeout(positioning_info)
            if overlapping:
                issues['overlapping_risks'] = overlapping
                if self.debug_mode:
                    print(f"   ⚠️ Found {len(overlapping)} overlapping risks")
            
            # Check for frame overflow
            if self.debug_mode:
                print(f"   📐 Checking frame boundaries...")
            
            overflow = self._detect_frame_overflow(positioning_info)
            if overflow:
                issues['frame_overflow_risks'] = overflow
                if self.debug_mode:
                    print(f"   ⚠️ Found {len(overflow)} overflow risks")
            
            # Generate improvements with limits
            improvements = self._suggest_positioning_improvements(positioning_info)
            if improvements:
                issues['positioning_improvements'] = improvements
            
            # Apply fixes with iteration limit
            if self.debug_mode:
                print(f"   🔧 Applying layout fixes (max {self.max_fix_iterations} iterations)...")
            
            fixed_code = self._apply_layout_fixes_with_limits(code, issues)
            issues['fixed_code'] = fixed_code
            
            # Generate suggestions
            issues['layout_suggestions'] = self._generate_layout_suggestions(code)
            
            # Record debug info
            analysis_time = time.time() - start_time
            issues['debug_info']['analysis_time'] = round(analysis_time, 2)
            
            if self.debug_mode:
                print(f"   ✅ Layout analysis complete in {analysis_time:.2f}s")
                print(f"   Results: {len(issues['overlapping_risks'])} overlaps, {len(issues['frame_overflow_risks'])} overflows")
            
            self.logger.info(f"Layout analysis complete: {len(issues['overlapping_risks'])} overlapping risks, {len(issues['frame_overflow_risks'])} overflow risks")
            
        except Exception as e:
            error_msg = f"Layout analysis failed: {e}"
            self.logger.error(error_msg)
            if self.debug_mode:
                print(f"   ❌ {error_msg}")
            issues['error'] = str(e)
        
        return issues
    
    def _detect_potential_overlapping_with_timeout(self, positioning_info: List[Dict]) -> List[Dict]:
        """Detect overlapping with timeout protection"""
        start_time = time.time()
        overlapping_risks = []
        
        # Limit the number of comparisons to prevent exponential growth
        max_comparisons = min(len(positioning_info) * (len(positioning_info) - 1) // 2, 100)
        comparisons_made = 0
        
        if self.debug_mode and len(positioning_info) > 10:
            print(f"      Large object count ({len(positioning_info)}), limiting comparisons to {max_comparisons}")
        
        for i, obj1 in enumerate(positioning_info):
            if time.time() - start_time > 10:  # 10 second timeout
                if self.debug_mode:
                    print(f"      ⏰ Overlap detection timeout after {comparisons_made} comparisons")
                break
                
            for j, obj2 in enumerate(positioning_info[i+1:], i+1):
                comparisons_made += 1
                if comparisons_made > max_comparisons:
                    if self.debug_mode:
                        print(f"      📊 Reached comparison limit ({max_comparisons})")
                    break
                
                coords1 = obj1['estimated_coords']
                coords2 = obj2['estimated_coords']
                
                # Calculate distance
                distance = ((coords1[0] - coords2[0])**2 + (coords1[1] - coords2[1])**2)**0.5
                
                # Assume minimum safe distance of 1.5 units
                min_distance = 1.5
                
                if distance < min_distance:
                    overlapping_risks.append({
                        'object1': obj1['object'],
                        'object2': obj2['object'],
                        'distance': round(distance, 2),
                        'coords1': coords1,
                        'coords2': coords2,
                        'severity': 'high' if distance < 0.5 else 'medium'
                    })
            
            if comparisons_made > max_comparisons:
                break
        
        if self.debug_mode and overlapping_risks:
            print(f"      Found {len(overlapping_risks)} overlapping pairs in {comparisons_made} comparisons")
        
        return overlapping_risks
    
    def _apply_layout_fixes_with_limits(self, code: str, issues: Dict) -> str:
        """Apply layout fixes with iteration limits to prevent infinite loops"""
        fixed_code = code
        iteration = 0
        
        if self.debug_mode:
            print(f"      Starting fix iterations...")
        
        try:
            while iteration < self.max_fix_iterations:
                iteration += 1
                iteration_start_time = time.time()
                
                if self.debug_mode:
                    print(f"      🔄 Fix iteration {iteration}/{self.max_fix_iterations}")
                
                changes_made = False
                original_code = fixed_code
                
                # Fix frame overflow issues
                overflow_risks = issues.get('frame_overflow_risks', [])
                if overflow_risks:
                    if self.debug_mode:
                        print(f"         Fixing {len(overflow_risks)} overflow issues...")
                    
                    for i, overflow in enumerate(overflow_risks[:5]):  # Limit fixes per iteration
                        if self.debug_mode:
                            print(f"           {i+1}. {overflow['object']}: {overflow['issues']}")
                        
                        obj_name = overflow['object']
                        current_pos = overflow['position']
                        
                        # Generate safe position
                        safe_pos = self._generate_safe_position(overflow['coords'], overflow['issues'])
                        
                        # Replace in code
                        old_pattern = f"{obj_name}.move_to({current_pos})"
                        new_pattern = f"{obj_name}.move_to({safe_pos})"
                        
                        if old_pattern in fixed_code:
                            fixed_code = fixed_code.replace(old_pattern, new_pattern)
                            changes_made = True
                            if self.debug_mode:
                                print(f"             ✓ Fixed position: {old_pattern} -> {new_pattern}")
                
                # Fix overlapping with limits
                overlapping_risks = issues.get('overlapping_risks', [])
                if overlapping_risks and len(overlapping_risks) < 50:  # Don't fix if too many overlaps
                    if self.debug_mode:
                        print(f"         Fixing {min(len(overlapping_risks), 3)} overlapping issues...")
                    
                    for i, overlap in enumerate(overlapping_risks[:3]):  # Limit fixes per iteration
                        if overlap['severity'] == 'high':
                            if self.debug_mode:
                                print(f"           {i+1}. Separating {overlap['object1']} and {overlap['object2']}")
                            
                            fixed_code = self._add_object_spacing_limited(fixed_code, overlap)
                            changes_made = True
                
                # Check if we should continue
                iteration_time = time.time() - iteration_start_time
                
                if self.debug_mode:
                    print(f"         Iteration {iteration} completed in {iteration_time:.2f}s, changes: {'Yes' if changes_made else 'No'}")
                
                # If no changes made or code is the same, break
                if not changes_made or fixed_code == original_code:
                    if self.debug_mode:
                        print(f"         No more changes needed, stopping at iteration {iteration}")
                    break
                
                # Update issues for next iteration (but limit re-analysis)
                if iteration < self.max_fix_iterations:
                    # Quick re-check without full analysis
                    new_positioning = self._extract_positioning_info(fixed_code)
                    if len(new_positioning) > 20:  # If too many objects, stop fixing
                        if self.debug_mode:
                            print(f"         Too many objects ({len(new_positioning)}), stopping fixes")
                        break
                    
                    issues['frame_overflow_risks'] = self._detect_frame_overflow(new_positioning)
                    issues['overlapping_risks'] = self._detect_potential_overlapping_with_timeout(new_positioning)
                
                # Safety check: if overlaps are increasing exponentially, stop
                if len(issues.get('overlapping_risks', [])) > 100:
                    if self.debug_mode:
                        print(f"         ⚠️ Overlap count too high ({len(issues['overlapping_risks'])}), stopping fixes")
                    break
            
            if iteration >= self.max_fix_iterations:
                if self.debug_mode:
                    print(f"      ⚠️ Reached maximum iterations ({self.max_fix_iterations})")
            
            issues['debug_info']['iterations'] = iteration
            
        except Exception as e:
            self.logger.error(f"Fix iteration failed: {e}")
            if self.debug_mode:
                print(f"      ❌ Fix iteration error: {e}")
            # Return original code if fixing fails
            return code
        
        return fixed_code
    
    def _add_object_spacing_limited(self, code: str, overlap_info: Dict) -> str:
        """Add spacing with limits to prevent code explosion"""
        try:
            obj1 = overlap_info['object1']
            obj2 = overlap_info['object2']
            
            # Simple fix: add shift to second object
            spacing_fix = f"\n        {obj2}.shift(DOWN * 1.5)  # Auto-spacing fix"
            
            # Find where obj2 is created or positioned and add spacing
            lines = code.split('\n')
            
            # Limit search to prevent infinite loops
            for i, line in enumerate(lines[:100]):  # Only check first 100 lines
                if f"{obj2}" in line and ("=" in line or ".move_to" in line or ".shift" in line):
                    # Check if fix already exists
                    if i + 1 < len(lines) and "Auto-spacing fix" in lines[i + 1]:
                        break  # Fix already applied
                    
                    lines.insert(i + 1, spacing_fix)
                    break
            
            return '\n'.join(lines)
            
        except Exception as e:
            self.logger.error(f"Spacing fix failed: {e}")
            return code
    
    def _extract_positioning_info(self, code: str) -> List[Dict]:
        """Extract positioning information from code with limits"""
        positioning_info = []
        
        # Look for positioning methods with limits
        positioning_patterns = [
            (r'(\w+)\.move_to\(([^)]+)\)', 'move_to'),
            (r'(\w+)\.shift\(([^)]+)\)', 'shift'),
            (r'(\w+)\.next_to\(([^)]+)\)', 'next_to'),
            (r'(\w+)\.to_edge\(([^)]+)\)', 'to_edge'),
            (r'(\w+)\.to_corner\(([^)]+)\)', 'to_corner'),
        ]
        
        for pattern, method_type in positioning_patterns:
            matches = re.findall(pattern, code)
            
            # Limit matches to prevent explosion
            for match in matches[:20]:  # Max 20 matches per pattern
                if len(match) >= 2:
                    obj_name = match[0]
                    position = match[1]
                    
                    # Skip if object name is too long (likely false positive)
                    if len(obj_name) > 30:
                        continue
                    
                    positioning_info.append({
                        'object': obj_name,
                        'method': method_type,
                        'position': position,
                        'estimated_coords': self._estimate_coordinates(position, method_type)
                    })
            
            # Break if we have too many objects
            if len(positioning_info) > 50:
                break
        
        return positioning_info
    
    def _estimate_coordinates(self, position_str: str, method_type: str) -> Tuple[float, float]:
        """Estimate actual coordinates from position string"""
        try:
            # Clean position string
            pos = position_str.strip()
            
            # Handle common position constants
            position_map = {
                'UP': (0, 2),
                'DOWN': (0, -2),
                'LEFT': (-3, 0),
                'RIGHT': (3, 0),
                'UL': (-3, 2),
                'UR': (3, 2),
                'DL': (-3, -2),
                'DR': (3, -2),
                'ORIGIN': (0, 0)
            }
            
            # Direct coordinate match
            coord_match = re.search(r'\[([^,]+),\s*([^,]+)[,\]]', pos)
            if coord_match:
                try:
                    x = float(coord_match.group(1))
                    y = float(coord_match.group(2))
                    return (x, y)
                except ValueError:
                    pass
            
            # Position constant
            for const, coords in position_map.items():
                if const in pos:
                    # Handle multipliers like UP * 2
                    multiplier_match = re.search(f'{const}\\s*\\*\\s*(\\d+(?:\\.\\d+)?)', pos)
                    if multiplier_match:
                        mult = float(multiplier_match.group(1))
                        return (coords[0] * mult, coords[1] * mult)
                    return coords
            
            # Default estimation
            return (0, 0)
            
        except Exception:
            return (0, 0)
    
    def _detect_frame_overflow(self, positioning_info: List[Dict]) -> List[Dict]:
        """Detect objects that might overflow frame boundaries"""
        overflow_risks = []
        
        # Calculate safe boundaries
        safe_x_min = -self.frame_width/2 + self.margin_x
        safe_x_max = self.frame_width/2 - self.margin_x
        safe_y_min = -self.frame_height/2 + self.margin_y
        safe_y_max = self.frame_height/2 - self.margin_y
        
        for obj_info in positioning_info:
            x, y = obj_info['estimated_coords']
            
            overflow_issues = []
            
            if x < safe_x_min:
                overflow_issues.append('left_overflow')
            elif x > safe_x_max:
                overflow_issues.append('right_overflow')
                
            if y < safe_y_min:
                overflow_issues.append('bottom_overflow')
            elif y > safe_y_max:
                overflow_issues.append('top_overflow')
            
            if overflow_issues:
                overflow_risks.append({
                    'object': obj_info['object'],
                    'position': obj_info['position'],
                    'coords': (x, y),
                    'issues': overflow_issues,
                    'suggested_fix': self._suggest_boundary_fix(x, y, overflow_issues)
                })
        
        return overflow_risks
    
    def _suggest_boundary_fix(self, x: float, y: float, issues: List[str]) -> str:
        """Suggest fix for boundary overflow"""
        fixes = []
        
        if 'left_overflow' in issues:
            new_x = -self.frame_width/2 + self.margin_x + 0.5
            fixes.append(f"Move right to x={new_x}")
        elif 'right_overflow' in issues:
            new_x = self.frame_width/2 - self.margin_x - 0.5
            fixes.append(f"Move left to x={new_x}")
            
        if 'bottom_overflow' in issues:
            new_y = -self.frame_height/2 + self.margin_y + 0.5
            fixes.append(f"Move up to y={new_y}")
        elif 'top_overflow' in issues:
            new_y = self.frame_height/2 - self.margin_y - 0.5
            fixes.append(f"Move down to y={new_y}")
        
        return "; ".join(fixes)
    
    def _suggest_positioning_improvements(self, positioning_info: List[Dict]) -> List[Dict]:
        """Suggest improved positioning strategies with limits"""
        improvements = []
        
        # Only suggest if reasonable number of objects
        if len(positioning_info) > 3 and len(positioning_info) < 20:
            improvements.append({
                'type': 'grouping',
                'suggestion': 'Consider using VGroup to organize multiple objects',
                'example': 'group = VGroup(obj1, obj2, obj3).arrange(DOWN, buff=0.5)'
            })
        
        return improvements
    
    def _generate_safe_position(self, coords: Tuple[float, float], issues: List[str]) -> str:
        """Generate safe position string for coordinates"""
        x, y = coords
        
        # Adjust coordinates to safe zone
        if 'left_overflow' in issues:
            x = -self.frame_width/2 + self.margin_x + 0.5
        elif 'right_overflow' in issues:
            x = self.frame_width/2 - self.margin_x - 0.5
            
        if 'bottom_overflow' in issues:
            y = -self.frame_height/2 + self.margin_y + 0.5
        elif 'top_overflow' in issues:
            y = self.frame_height/2 - self.margin_y - 0.5
        
        return f"np.array([{x:.2f}, {y:.2f}, 0])"
    
    def _generate_layout_suggestions(self, code: str) -> List[str]:
        """Generate general layout improvement suggestions"""
        suggestions = []
        
        # Check for missing spacing
        if '.arrange(' not in code and 'VGroup' in code:
            suggestions.append("Use .arrange() method with VGroup for automatic spacing")
        
        # Check for frame-relative positioning
        if '.to_edge(' not in code and ('.move_to(' in code or '.shift(' in code):
            suggestions.append("Consider using .to_edge() for frame-relative positioning")
        
        return suggestions
    
    def validate_final_layout(self, code: str) -> Dict:
        """Final validation with performance limits"""
        if self.debug_mode:
            print(f"\n🔍 Final layout validation...")
        
        validation = {
            'safe': True,
            'warnings': [],
            'suggestions': [],
            'layout_score': 100
        }
        
        try:
            # Quick analysis with limits
            issues = self.analyze_layout_issues(code)
            
            if issues.get('overlapping_risks'):
                overlap_count = len(issues['overlapping_risks'])
                if overlap_count > 10:
                    validation['safe'] = False
                    validation['warnings'].append(f"Too many overlapping issues ({overlap_count})")
                    validation['layout_score'] -= 30
                else:
                    validation['warnings'].append(f"{overlap_count} potential overlapping issues")
                    validation['layout_score'] -= overlap_count * 2
            
            if issues.get('frame_overflow_risks'):
                overflow_count = len(issues['frame_overflow_risks'])
                validation['warnings'].append(f"{overflow_count} potential overflow issues")
                validation['layout_score'] -= overflow_count * 3
            
            validation['layout_score'] = max(0, min(100, validation['layout_score']))
            
            if self.debug_mode:
                print(f"   Layout Score: {validation['layout_score']}/100")
                print(f"   Safe: {'Yes' if validation['safe'] else 'No'}")
            
        except Exception as e:
            self.logger.error(f"Layout validation failed: {e}")
            validation['safe'] = False
            validation['warnings'].append(f"Validation error: {str(e)}")
        
        return validation
