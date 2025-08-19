import time
import re
import ast
from typing import Dict, List, Optional, Tuple
from utils import setup_logger

class IntelligentErrorFixer:
    """
    Advanced error correction system that uses Vertex AI to intelligently fix syntax and runtime errors.
    Continues until perfect code is achieved or timeout reached.
    """
    
    def __init__(self, vertex_client, max_timeout_minutes: int = 15):
        """Initialize the intelligent error fixer"""
        self.logger = setup_logger("intelligent_error_fixer")
        self.vertex_client = vertex_client
        self.max_timeout = max_timeout_minutes * 60  # Convert to seconds
        self.debug_mode = True
        
        # Error correction tracking
        self.error_history = []
        self.fix_attempts = []
        self.learning_patterns = {}
        
        # Performance settings
        self.ai_fix_timeout = 60  # 1 minute per AI fix attempt
        self.execution_timeout = 300  # 5 minutes per execution
        
        self.logger.info(f"Intelligent Error Fixer initialized with {max_timeout_minutes}min timeout")
    
    def fix_code_until_perfect(self, initial_code: str, context: Dict) -> Dict:
        """
        Main method: Fix code using AI until it's perfect or timeout reached
        
        Args:
            initial_code: The initial code to fix
            context: Generation context for AI learning
            
        Returns:
            Dict with final code, success status, and detailed execution history
        """
        if self.debug_mode:
            print(f"\n🤖 Starting INTELLIGENT ERROR CORRECTION")
            print(f"   ⏱️ Maximum timeout: {self.max_timeout/60:.1f} minutes")
            print(f"   🎯 Goal: Perfect working code with video output")
        
        start_time = time.time()
        current_code = initial_code
        attempt_number = 0
        last_error_type = None
        consecutive_same_errors = 0
        
        result = {
            'final_code': initial_code,
            'success': False,
            'total_attempts': 0,
            'total_time': 0,
            'video_path': None,
            'error_history': [],
            'ai_fixes_applied': [],
            'final_error': None,
            'timeout_reached': False
        }
        
        try:
            while time.time() - start_time < self.max_timeout:
                attempt_number += 1
                attempt_start = time.time()
                
                if self.debug_mode:
                    print(f"\n🔄 ATTEMPT #{attempt_number}")
                    print(f"   ⏱️ Elapsed: {(time.time() - start_time)/60:.1f}min")
                    print(f"   📝 Code length: {len(current_code)} characters")
                
                # Execute the current code
                execution_result = self._execute_code_safely(current_code, context, attempt_number)
                
                # Check if successful
                if execution_result['success'] and execution_result.get('video_path'):
                    if self.debug_mode:
                        print(f"   ✅ SUCCESS! Video generated: {execution_result['video_path']}")
                    
                    result.update({
                        'final_code': current_code,
                        'success': True,
                        'video_path': execution_result['video_path'],
                        'total_attempts': attempt_number,
                        'total_time': time.time() - start_time
                    })
                    return result
                
                # Extract and analyze error
                error_info = self._extract_error_information(execution_result)
                error_type = error_info.get('type', 'unknown')
                
                if self.debug_mode:
                    print(f"   ❌ Error detected: {error_type}")
                    print(f"   📄 Error message: {error_info.get('message', 'Unknown')[:100]}...")
                
                # Track consecutive same errors
                if error_type == last_error_type:
                    consecutive_same_errors += 1
                    if consecutive_same_errors >= 3:
                        if self.debug_mode:
                            print(f"   ⚠️ Same error type {consecutive_same_errors} times, trying alternative approach")
                        # Switch to alternative fixing strategy
                        error_info['alternative_approach'] = True
                else:
                    consecutive_same_errors = 0
                    last_error_type = error_type
                
                # Record error in history
                self.error_history.append({
                    'attempt': attempt_number,
                    'error': error_info,
                    'execution_result': execution_result,
                    'timestamp': time.time()
                })
                result['error_history'].append(error_info)
                
                # Use AI to fix the error
                if self.debug_mode:
                    print(f"   🤖 Sending error to Vertex AI for intelligent fixing...")
                
                ai_fix_result = self._get_ai_error_fix(current_code, error_info, context, attempt_number)
                
                if ai_fix_result['success']:
                    current_code = ai_fix_result['fixed_code']
                    result['ai_fixes_applied'].append(ai_fix_result)
                    
                    if self.debug_mode:
                        print(f"   ✅ AI fix applied successfully")
                        print(f"   📝 New code length: {len(current_code)} characters")
                        print(f"   🔧 Fix description: {ai_fix_result.get('fix_description', 'No description')}")
                else:
                    if self.debug_mode:
                        print(f"   ⚠️ AI fix failed, trying fallback approach...")
                    
                    # Fallback: try basic pattern-based fixes
                    fallback_code = self._apply_fallback_fixes(current_code, error_info)
                    if fallback_code != current_code:
                        current_code = fallback_code
                        if self.debug_mode:
                            print(f"   🔨 Fallback fix applied")
                    else:
                        if self.debug_mode:
                            print(f"   ❌ No fallback fix available, will retry...")
                
                # Check timeout
                if time.time() - start_time > self.max_timeout:
                    if self.debug_mode:
                        print(f"   ⏰ TIMEOUT REACHED ({self.max_timeout/60:.1f} minutes)")
                    result['timeout_reached'] = True
                    break
                    
                # Brief pause before next attempt
                time.sleep(2)
            
            # If we reach here, we didn't succeed
            result.update({
                'final_code': current_code,
                'success': False,
                'total_attempts': attempt_number,
                'total_time': time.time() - start_time,
                'final_error': self.error_history[-1] if self.error_history else None
            })
            
            if self.debug_mode:
                print(f"\n❌ INTELLIGENT CORRECTION COMPLETED WITHOUT SUCCESS")
                print(f"   📊 Total attempts: {attempt_number}")
                print(f"   ⏱️ Total time: {(time.time() - start_time)/60:.1f} minutes")
                print(f"   🤖 AI fixes attempted: {len(result['ai_fixes_applied'])}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Intelligent error fixing failed: {e}")
            result['final_error'] = {'type': 'system_error', 'message': str(e)}
            return result
    
    def _execute_code_safely(self, code: str, context: Dict, attempt: int) -> Dict:
        """Execute code with comprehensive error capture"""
        if self.debug_mode:
            print(f"      🎬 Executing code (attempt {attempt})...")
        
        # Create execution environment
        exec_env = self.vertex_client._create_safe_execution_environment(code, f"fix_attempt_{attempt}", attempt)
        if not exec_env:
            return {
                'success': False,
                'error': 'Failed to create execution environment',
                'stderr': '',
                'stdout': '',
                'return_code': -1
            }
        
        # Execute with extended timeout
        execution_result = self.vertex_client._execute_manim_safely(exec_env)
        
        if self.debug_mode:
            print(f"      📊 Execution completed in {execution_result.get('execution_time', 0):.2f}s")
            print(f"      🎯 Success: {'Yes' if execution_result['success'] else 'No'}")
            if execution_result.get('video_path'):
                print(f"      📹 Video: {execution_result['video_path']}")
        
        return execution_result
    
    def _extract_error_information(self, execution_result: Dict) -> Dict:
        """Extract comprehensive error information for AI analysis"""
        error_info = {
            'type': 'unknown',
            'category': 'unknown', 
            'message': execution_result.get('error', 'Unknown error'),
            'stderr': execution_result.get('stderr', ''),
            'stdout': execution_result.get('stdout', ''),
            'return_code': execution_result.get('return_code', -1),
            'line_number': None,
            'specific_issue': None,
            'suggested_fix_type': None
        }
        
        stderr = error_info['stderr'].lower()
        stdout = error_info['stdout'].lower()
        combined_output = stderr + ' ' + stdout
        
        # Detailed error categorization
        if 'syntaxerror' in combined_output:
            error_info['type'] = 'syntax_error'
            error_info['category'] = 'code_structure'
            
            # Extract specific syntax issues
            if 'perhaps you forgot a comma' in combined_output:
                error_info['specific_issue'] = 'missing_comma'
                error_info['suggested_fix_type'] = 'add_missing_comma'
            elif 'invalid syntax' in combined_output:
                error_info['specific_issue'] = 'invalid_syntax'
                error_info['suggested_fix_type'] = 'fix_syntax_structure'
            elif 'unexpected eof' in combined_output:
                error_info['specific_issue'] = 'incomplete_code'
                error_info['suggested_fix_type'] = 'complete_code_blocks'
            elif 'unmatched' in combined_output:
                error_info['specific_issue'] = 'unmatched_brackets'
                error_info['suggested_fix_type'] = 'balance_brackets'
                
        elif 'nameerror' in combined_output:
            error_info['type'] = 'name_error'
            error_info['category'] = 'undefined_variable'
            error_info['suggested_fix_type'] = 'define_missing_variables'
            
        elif 'attributeerror' in combined_output:
            error_info['type'] = 'attribute_error'
            error_info['category'] = 'api_compatibility'
            error_info['suggested_fix_type'] = 'fix_api_calls'
            
        elif 'importerror' in combined_output or 'modulenotfounderror' in combined_output:
            error_info['type'] = 'import_error'
            error_info['category'] = 'missing_imports'
            error_info['suggested_fix_type'] = 'add_imports'
            
        elif 'indentationerror' in combined_output:
            error_info['type'] = 'indentation_error'
            error_info['category'] = 'code_structure'
            error_info['suggested_fix_type'] = 'fix_indentation'
            
        elif 'typeerror' in combined_output:
            error_info['type'] = 'type_error'
            error_info['category'] = 'parameter_mismatch'
            error_info['suggested_fix_type'] = 'fix_parameter_types'
            
        elif 'valueerror' in combined_output:
            error_info['type'] = 'value_error'
            error_info['category'] = 'invalid_values'
            error_info['suggested_fix_type'] = 'validate_parameters'
        
        # Extract line number if available
        line_match = re.search(r'line (\d+)', combined_output)
        if line_match:
            error_info['line_number'] = int(line_match.group(1))
        
        return error_info
    def _get_ai_error_fix(self, code: str, error_info: Dict, context: Dict, attempt: int) -> Dict:
        """Enhanced AI error fix with specific Manim error handling"""
        fix_start_time = time.time()
        
        try:
            # First, try specific Manim fixes
            if error_info['type'] == 'name_error' and 'animate' in error_info.get('message', '').lower():
                print(f"      🎯 Applying specific Manim animate fixes first...")
                
                specific_fix = self._apply_specific_manim_fixes(code, error_info)
                if specific_fix != code:
                    # Validate the specific fix
                    validation_result = self._validate_ai_fix(specific_fix, error_info)
                    if validation_result['valid']:
                        return {
                            'success': True,
                            'fixed_code': specific_fix,
                            'original_code': code,
                            'fix_description': 'Applied specific Manim animate fixes',
                            'fix_time': time.time() - fix_start_time,
                            'ai_response_length': 0,
                            'validation_result': validation_result,
                            'method': 'specific_fix'
                        }
                    else:
                        print(f"         Specific fix validation failed: {validation_result['issues']}")
            
            # If specific fix didn't work, try AI fix with enhanced prompt
            prompt = self._build_enhanced_error_fixing_prompt(code, error_info, context, attempt)
            
            if self.debug_mode:
                print(f"      🧠 Sending enhanced prompt to AI: {error_info['type']} -> {error_info.get('specific_issue', 'general')}")
            
            # Send to Vertex AI with timeout
            self.vertex_client._wait_for_rate_limit()
            
            response = self.vertex_client.client.models.generate_content(
                model=self.vertex_client.model_name,
                contents=prompt,
                config=self.vertex_client.types.GenerateContentConfig(
                    temperature=0.1,  # Very low for precise fixes
                    max_output_tokens=8192,
                    top_p=0.85
                )
            )
            
            if not response or not hasattr(response, 'text') or not response.text:
                return {'success': False, 'error': 'No AI response received'}
            
            # Extract fixed code
            fixed_code = self._extract_fixed_code_from_ai_response(response.text)
            
            if not fixed_code or fixed_code == code:
                return {'success': False, 'error': 'AI did not provide a different code solution'}
            
            # Validate the fix with enhanced validation
            validation_result = self._validate_ai_fix(fixed_code, error_info)
            
            fix_time = time.time() - fix_start_time
            
            if self.debug_mode:
                print(f"      ✅ AI fix completed in {fix_time:.2f}s")
                print(f"      📏 Code length: {len(code)} -> {len(fixed_code)}")
                print(f"      🎯 Validation: {'Passed' if validation_result['valid'] else 'Failed'}")
                if not validation_result['valid']:
                    print(f"         Issues: {validation_result['issues']}")
            
            if not validation_result['valid']:
                # If AI fix fails validation, try one more specific fix
                if error_info['type'] == 'name_error' and 'animate' in error_info.get('message', '').lower():
                    print(f"      🔧 AI fix failed, trying enhanced specific fix...")
                    enhanced_fix = self._apply_enhanced_animate_fix(fixed_code, error_info)
                    enhanced_validation = self._validate_ai_fix(enhanced_fix, error_info)
                    
                    if enhanced_validation['valid']:
                        return {
                            'success': True,
                            'fixed_code': enhanced_fix,
                            'original_code': code,
                            'fix_description': 'Applied enhanced animate fix after AI attempt',
                            'fix_time': fix_time,
                            'validation_result': enhanced_validation,
                            'method': 'enhanced_specific_fix'
                        }
                
                return {
                    'success': False, 
                    'error': f"AI fix validation failed: {validation_result['issues']}"
                }
            
            return {
                'success': True,
                'fixed_code': fixed_code,
                'original_code': code,
                'fix_description': self._describe_fix_applied(code, fixed_code, error_info),
                'fix_time': fix_time,
                'ai_response_length': len(response.text),
                'validation_result': validation_result,
                'method': 'ai_fix'
            }
            
        except Exception as e:
            fix_time = time.time() - fix_start_time
            self.logger.error(f"AI error fix failed after {fix_time:.2f}s: {e}")
            return {'success': False, 'error': f"AI fix exception: {str(e)}", 'fix_time': fix_time}

    def _build_error_fixing_prompt(self, code: str, error_info: Dict, context: Dict, attempt: int) -> str:
        """Build a specialized prompt for fixing the specific error"""
        
        error_type = error_info['type']
        specific_issue = error_info.get('specific_issue', 'general')
        error_message = error_info['message']
        stderr_content = error_info['stderr']
        
        # Build context from previous attempts
        learning_context = ""
        if len(self.error_history) > 0:
            learning_context = f"\nPREVIOUS ATTEMPTS ANALYSIS:\n"
            for i, prev_error in enumerate(self.error_history[-3:], 1):  # Last 3 attempts
                learning_context += f"Attempt {prev_error['attempt']}: {prev_error['error']['type']} - {prev_error['error']['message'][:50]}...\n"
        
        # Specialized prompts based on error type
        if error_type == 'syntax_error':
            specific_instructions = f"""
SYNTAX ERROR FIXING INSTRUCTIONS:
- Error Type: {specific_issue}
- Error Message: {error_message}
- Focus on fixing the exact syntax issue without changing the logic
- Pay special attention to commas, brackets, quotes, and indentation
- Ensure all code blocks are properly closed
- Validate all function calls and method syntax
"""
        
        elif error_type == 'attribute_error':
            specific_instructions = f"""
ATTRIBUTE ERROR FIXING INSTRUCTIONS:
- Error suggests using non-existent methods or properties
- Replace deprecated Manim methods with modern v0.19.0 API
- Check for typos in method names
- Ensure objects have the methods being called
- Use proper Manim object hierarchy
"""
        
        elif error_type == 'name_error':
            specific_instructions = f"""
NAME ERROR FIXING INSTRUCTIONS:
- Variable or function not defined
- Add missing imports if needed
- Define missing variables before use
- Check for typos in variable names
- Ensure proper scope for all variables
"""
        
        else:
            specific_instructions = f"""
GENERAL ERROR FIXING INSTRUCTIONS:
- Error Type: {error_type}
- Category: {error_info['category']}
- Fix the specific issue while maintaining code functionality
- Ensure Manim v0.19.0 compatibility
- Maintain educational value and animation quality
"""
        
        # Build the comprehensive prompt
        prompt = f"""You are an expert Manim debugging assistant. Fix the following error in the Manim animation code.

DEBUGGING CONTEXT:
Subject: {context.get('subject', 'Unknown')}
Topic: {context.get('topic', 'Unknown')}
Complexity: {context.get('complexity', 'Unknown')}
Attempt Number: {attempt}

{specific_instructions}

ERROR DETAILS:
Type: {error_type}
Message: {error_message}
STDERR Output:
{stderr_content}

{learning_context}

CURRENT CODE WITH ERROR:
{code}


DEBUGGING REQUIREMENTS:
1. Fix the EXACT error mentioned above
2. Maintain all educational content and animations
3. Use ONLY Manim v0.19.0 compatible API methods
4. Ensure proper Python syntax and structure
5. Keep the same Scene class name and structure
6. Preserve all educational value and visual elements
7. Add comments explaining the fix if complex

CRITICAL: Return ONLY the corrected Python code. Do NOT include explanations, markdown formatting, or any other text. The response should start with 'from manim import *' and be complete, executable code.

FIXED CODE:"""

        return prompt
    
    def _extract_fixed_code_from_ai_response(self, ai_response: str) -> str:
        """Extract the fixed code from AI response"""
        try:
            # Clean the response
            cleaned_response = ai_response.strip()
            
            # Remove markdown if present
            if '```python' in cleaned_response:
                start = cleaned_response.find('```python') + len('```python')
                end = cleaned_response.find('```', start)
                if end != -1:
                    cleaned_response = cleaned_response[start:end].strip()
            elif '```' in cleaned_response:
                start = cleaned_response.find('```') + 3
                end = cleaned_response.find('```', start)
                if end != -1:
                    cleaned_response = cleaned_response[start:end].strip()
            
            # Ensure it starts with proper imports
            if not cleaned_response.startswith(('from manim import', 'import manim')):
                cleaned_response = 'from manim import *\nimport numpy as np\n\n' + cleaned_response
            
            return cleaned_response.strip()
        except Exception as e:
            self.logger.error(f"Failed to extract fixed code: {e}")
            return ""
            
        except Exception as e:
            self.logger.error(f"Failed to extract fixed code: {e}")
            return ""
    
    def _validate_ai_fix(self, fixed_code: str, error_info: Dict) -> Dict:
        """CORRECTED validation that properly distinguishes correct vs incorrect animate usage"""
        validation = {
            'valid': True,
            'issues': []
        }
        
        try:
            # Basic syntax validation
            try:
                ast.parse(fixed_code)
            except SyntaxError as e:
                validation['valid'] = False
                validation['issues'].append(f"Syntax error still present: {str(e)}")
                return validation
            
            # SPECIFIC MANIM ANIMATE ERROR CHECK - CORRECTED
            error_type = error_info['type']
            error_message = error_info.get('message', '').lower()
            
            if error_type == 'name_error' and 'animate' in error_message:
                print(f"         🔍 Checking for remaining animate issues...")
                
                # CORRECTED: Only check for PROBLEMATIC animate patterns
                problematic_patterns = [
                    r'(?<!\.)\banimate\s*\.',   # standalone animate. (not preceded by a dot)
                    r'^\s*animate\s*\.',        # animate. at start of line
                    r'=\s*animate\b',           # var = animate
                    r'\banimate\s*\(',          # animate() function call
                    r'\banimate\s*\[',          # animate[index]
                    r'(?<!\.)\banimate\s*$',    # standalone animate at end
                ]
                
                issues_found = []
                for pattern in problematic_patterns:
                    matches = re.findall(pattern, fixed_code, re.MULTILINE)
                    if matches:
                        issues_found.append(f"Found problematic pattern '{pattern}': {matches}")
                
                if issues_found:
                    validation['valid'] = False
                    validation['issues'].extend(issues_found)
                    print(f"         ❌ Still has problematic animate usage:")
                    for issue in issues_found:
                        print(f"            - {issue}")
                else:
                    print(f"         ✅ No problematic animate patterns found")
                
                # VERIFY correct animate usage is present (if any animate is used)
                correct_animate_pattern = r'\w+\.animate\.\w+'
                correct_usages = re.findall(correct_animate_pattern, fixed_code)
                if correct_usages:
                    print(f"         ✅ Found {len(correct_usages)} correct animate usages: {correct_usages}")
                
                # If animate is used, ensure it's within proper context
                if '.animate.' in fixed_code:
                    animate_lines = [line.strip() for line in fixed_code.split('\n') if '.animate.' in line]
                    for line in animate_lines:
                        if not any(context in line for context in ['self.play(', 'self.add(', 'self.remove(']):
                            validation['issues'].append(f"animate usage not in proper context: {line}")
            
            # Check for essential Manim components
            if 'from manim import' not in fixed_code and 'import manim' not in fixed_code:
                validation['issues'].append("Missing Manim imports")
            
            if not re.search(r'class\s+\w+\s*\(\s*Scene\s*\):', fixed_code):
                validation['valid'] = False
                validation['issues'].append("No Scene class found")
            
            if 'def construct(' not in fixed_code:
                validation['valid'] = False
                validation['issues'].append("No construct method found")
            
            # Final check: Mark as valid if no critical issues
            critical_issues = [issue for issue in validation['issues'] 
                            if any(critical in issue.lower() 
                                    for critical in ['syntax error', 'no scene class', 'no construct', 'problematic pattern'])]
            
            if critical_issues:
                validation['valid'] = False
            
        except Exception as e:
            validation['valid'] = False
            validation['issues'].append(f"Validation exception: {str(e)}")
        
        return validation

    def _describe_fix_applied(self, original_code: str, fixed_code: str, error_info: Dict) -> str:
        """Generate a description of what fix was applied"""
        try:
            # Basic comparison
            original_lines = original_code.split('\n')
            fixed_lines = fixed_code.split('\n')
            
            if len(fixed_lines) != len(original_lines):
                return f"Code structure changed: {len(original_lines)} -> {len(fixed_lines)} lines"
            
            # Find changed lines
            changed_lines = []
            for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines), 1):
                if orig.strip() != fixed.strip():
                    changed_lines.append(f"Line {i}: '{orig.strip()[:30]}...' -> '{fixed.strip()[:30]}...'")
            
            if changed_lines:
                return f"Modified {len(changed_lines)} lines: " + "; ".join(changed_lines[:3])
            else:
                return "Subtle changes applied (whitespace, formatting, or small corrections)"
                
        except Exception:
            return f"Fixed {error_info['type']} error"
    
    def _apply_fallback_fixes(self, code: str, error_info: Dict) -> str:
        """Apply basic pattern-based fixes as fallback"""
        fixed_code = code
        error_type = error_info['type']
        
        try:
            if error_type == 'syntax_error':
                # Basic syntax fixes
                if 'missing_comma' in error_info.get('specific_issue', ''):
                    # Try to add missing commas in function calls
                    fixed_code = re.sub(r'(\w+)\s+(\w+\s*=)', r'\1, \2', fixed_code)
                    fixed_code = re.sub(r'(\w+)\s+([A-Z][a-z])', r'\1, \2', fixed_code)
                
            elif error_type == 'name_error':
                # Add common imports
                if 'np' in error_info['message'] and 'import numpy' not in fixed_code:
                    fixed_code = 'import numpy as np\n' + fixed_code
                    
            elif error_type == 'attribute_error':
                # Fix common deprecated methods
                fixed_code = re.sub(r'\.get_sides$$$$', '', fixed_code)
                fixed_code = re.sub(r'\.get_part_by_text$$[^)]+$$', '', fixed_code)
                fixed_code = re.sub(r'Indicate$$([^,]+),\s*color=[^)]+$$', r'Indicate(\1)', fixed_code)
                
        except Exception as e:
            self.logger.error(f"Fallback fix failed: {e}")
        
        return fixed_code
    def _apply_specific_manim_fixes(self, code: str, error_info: Dict) -> str:
        """Apply specific fixes for known Manim errors"""
        
        if error_info['type'] == 'name_error' and 'animate' in error_info.get('message', '').lower():
            print(f"      🎯 Applying specific Manim animate fix...")
            
            fixed_code = code
            
            # Fix common animate issues
            fixes_applied = []
            
            # 1. Replace standalone 'animate' with proper object.animate syntax
            # Look for patterns like: animate.shift(UP) -> object.animate.shift(UP)
            animate_pattern = r'\banimate\.([\w_]+)\(([^)]*)\)'
            matches = re.findall(animate_pattern, fixed_code)
            
            for method, params in matches:
                # Find the most recent object creation to apply animate to
                lines = fixed_code.split('\n')
                for i, line in enumerate(lines):
                    if f'animate.{method}(' in line:
                        # Look backwards for the most recent object
                        obj_name = None
                        for j in range(i-1, -1, -1):
                            obj_match = re.search(r'(\w+)\s*=\s*(?:Text|Circle|Rectangle|Square|Triangle|Line|MathTex|Tex)\s*\(', lines[j])
                            if obj_match:
                                obj_name = obj_match.group(1)
                                break
                        
                        if obj_name:
                            old_line = line
                            new_line = line.replace(f'animate.{method}(', f'{obj_name}.animate.{method}(')
                            fixed_code = fixed_code.replace(old_line, new_line)
                            fixes_applied.append(f"Fixed animate.{method} -> {obj_name}.animate.{method}")
                            break
            
            # 2. Remove standalone animate references
            standalone_animate = re.findall(r'\banimate\b(?!\s*\.)', fixed_code)
            if standalone_animate:
                # Replace with a comment or remove the line
                fixed_code = re.sub(r'^\s*animate\s*$', '        # Animation removed (was standalone animate)', fixed_code, flags=re.MULTILINE)
                fixes_applied.append("Removed standalone animate references")
            
            # 3. Fix animate in self.play() calls
            # Look for self.play(animate...) and fix it
            play_animate_pattern = r'self\.play\s*\(\s*animate\.'
            if re.search(play_animate_pattern, fixed_code):
                # This is trickier - we need to find the object context
                lines = fixed_code.split('\n')
                for i, line in enumerate(lines):
                    if 'self.play(' in line and 'animate.' in line:
                        # Find the most recent object
                        obj_name = None
                        for j in range(i-1, -1, -1):
                            obj_match = re.search(r'(\w+)\s*=\s*(?:Text|Circle|Rectangle|Square|Triangle|Line|MathTex|Tex|VGroup)\s*\(', lines[j])
                            if obj_match:
                                obj_name = obj_match.group(1)
                                break
                        
                        if obj_name:
                            old_line = line
                            new_line = re.sub(r'animate\.', f'{obj_name}.animate.', line)
                            fixed_code = fixed_code.replace(old_line, new_line)
                            fixes_applied.append(f"Fixed self.play(animate...) -> self.play({obj_name}.animate...)")
            
            # 4. If no specific fixes worked, replace with basic animation
            if not fixes_applied and 'animate' in fixed_code:
                # Last resort: replace problematic animate lines with basic alternatives
                lines = fixed_code.split('\n')
                new_lines = []
                
                for line in lines:
                    if 'animate.' in line and 'self.play(' not in line and '.animate.' not in line:
                        # Replace with a basic Write animation
                        if 'Text(' in line or 'MathTex(' in line:
                            new_line = line.replace('animate.', 'Write(')
                            if not new_line.endswith(')'):
                                new_line += ')'
                            new_lines.append(f"        self.play({new_line})")
                        else:
                            # Comment out the problematic line
                            new_lines.append(f"        # {line.strip()} # Fixed: removed problematic animate")
                        fixes_applied.append("Replaced animate with Write animation")
                    else:
                        new_lines.append(line)
                
                fixed_code = '\n'.join(new_lines)
            
            if fixes_applied:
                print(f"         Applied {len(fixes_applied)} specific fixes:")
                for fix in fixes_applied:
                    print(f"           - {fix}")
            
            return fixed_code
        
        return code
    def _apply_enhanced_animate_fix(self, code: str, error_info: Dict) -> str:
        """Enhanced fix specifically for animate errors in Manim"""
        
        print(f"         🔧 Applying enhanced animate fix...")
        
        fixed_code = code
        
        # Strategy 1: Replace all problematic animate usage with proper Manim syntax
        lines = fixed_code.split('\n')
        new_lines = []
        current_objects = []
        
        for i, line in enumerate(lines):
            # Track object creations
            obj_match = re.search(r'(\w+)\s*=\s*(Text|Circle|Rectangle|Square|Triangle|Line|MathTex|Tex|VGroup)\s*\(', line)
            if obj_match:
                current_objects.append(obj_match.group(1))
            
            # Fix animate issues
            if 'animate.' in line and not '.animate.' in line:
                # This is the problematic pattern: animate.method()
                
                if 'self.play(' in line:
                    # Inside self.play, replace with object.animate
                    if current_objects:
                        last_obj = current_objects[-1]
                        new_line = line.replace('animate.', f'{last_obj}.animate.')
                        new_lines.append(new_line)
                        print(f"           Fixed: animate. -> {last_obj}.animate.")
                    else:
                        # No object found, replace with basic animation
                        new_line = line.replace('animate.', 'Write(')
                        if not new_line.count('(') == new_line.count(')'):
                            new_line += ')'
                        new_lines.append(new_line)
                        print(f"           Fixed: animate. -> Write(")
                else:
                    # Outside self.play, wrap in self.play
                    if current_objects:
                        last_obj = current_objects[-1]
                        method_match = re.search(r'animate\.(\w+)\(([^)]*)\)', line)
                        if method_match:
                            method_name = method_match.group(1)
                            method_params = method_match.group(2)
                            indent = len(line) - len(line.lstrip())
                            new_line = ' ' * indent + f'self.play({last_obj}.animate.{method_name}({method_params}))'
                            new_lines.append(new_line)
                            print(f"           Fixed: wrapped animate in self.play")
                        else:
                            new_lines.append(f'        # {line.strip()} # Commented out problematic animate')
                    else:
                        new_lines.append(f'        # {line.strip()} # Commented out problematic animate')
            else:
                new_lines.append(line)
        
        fixed_code = '\n'.join(new_lines)
        
        # Strategy 2: Remove any remaining standalone 'animate' references
        fixed_code = re.sub(r'^\s*animate\s*$', '        # Removed standalone animate', fixed_code, flags=re.MULTILINE)
        
        # Strategy 3: Ensure proper structure
        if 'self.play(' not in fixed_code and '.animate.' in fixed_code:
            # Add self.play around animate calls
            fixed_code = re.sub(r'(\s+)(\w+\.animate\.\w+\([^)]*\))', r'\1self.play(\2)', fixed_code)
        
        return fixed_code
    def _build_enhanced_error_fixing_prompt(self, code: str, error_info: Dict, context: Dict, attempt: int) -> str:
        """Build enhanced prompt specifically addressing the error type"""
        
        error_type = error_info['type']
        error_message = error_info['message']
        
        if error_type == 'name_error' and 'animate' in error_message.lower():
            return f"""You are a Manim expert fixing a specific NameError with 'animate'. 

    CRITICAL ERROR TO FIX:
    The code has "NameError: name 'animate' is not defined"

    MANIM ANIMATE RULES:
    1. 'animate' is NOT a standalone variable or function
    2. 'animate' is a property of Manim objects: object.animate.method()
    3. Animations must be used within self.play(): self.play(object.animate.method())
    4. NEVER use just 'animate.method()' - this is WRONG
    5. ALWAYS use 'object.animate.method()' where object is a real Manim object

    COMMON WRONG PATTERNS TO FIX:
    ❌ animate.shift(UP)          → ✅ object.animate.shift(UP)
    ❌ self.play(animate.move())  → ✅ self.play(object.animate.move())
    ❌ animate = something        → ✅ Remove this line
    ❌ var = animate             → ✅ Remove this line

    ERROR CODE:
    {code}

    FIXING INSTRUCTIONS:
    1. Find ALL instances of incorrect 'animate' usage
    2. Replace with proper object.animate.method() syntax
    3. Ensure animations are within self.play() calls
    4. Use the most recently created object if unclear which object to animate
    5. Remove any standalone 'animate' references
    6. Test that the fix makes sense in Manim context

    Return ONLY the corrected code with proper Manim animate syntax. No explanations."""

        else:
            # Use the original prompt building logic for other errors
            return self._build_error_fixing_prompt(code, error_info, context, attempt)
