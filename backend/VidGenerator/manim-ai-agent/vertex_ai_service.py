import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import time
import ast
import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from utils import setup_logger
from error_learning_system import ErrorLearningSystem
from layout_manager import LayoutManager

class VertexAIClient:
    """
    Enhanced Manim-compatible Google Gen AI SDK client with error learning and layout management.
    Features reinforcement learning from mistakes and intelligent layout handling.
    """

    def __init__(self):
        """Initialize with comprehensive error handling, learning system, and layout management"""
        self.logger = setup_logger("vertex_ai_client")
        self.debug_dir = "./debug_output"
        os.makedirs(self.debug_dir, exist_ok=True)
        # Add debug mode
        self.debug_mode = True  # Set to False to reduce output

        # Initialize learning systems
        self.error_learning = ErrorLearningSystem()
        self.layout_manager = LayoutManager()
        
        self.logger.info("🔧 Initializing AI-POWERED Vertex AI client with Learning...")

        try:
            from google import genai
            from google.genai import types
            self.genai = genai
            self.types = types

            # Create client
            self.client = genai.Client(
                vertexai=True,
                project="warp-ai-hackathon",
                location="global",
            )

            self.logger.info("✅ Gen AI Client created successfully")

            # Model configuration
            self.model_name = "gemini-2.5-pro"
            self.alternative_models = ["gemini-1.5-pro", "gemini-1.5-flash"]

            # Enhanced generation config for better quality
            self.generation_config = {
                "temperature": 0.2,  # Lower for more consistent quality
                "max_output_tokens": 8192,
                "top_p": 0.85,
            }

            # Rate limiting
            self.rate_limit_delay = 3.0
            self.last_request_time = 0

            # Execution settings
            self.max_execution_attempts = 3
            self.execution_timeout = 180
            
            # Learning metrics
            self.generation_quality_history = []
            self.error_prevention_count = 0

            self.logger.info(f"🤖 Using model: {self.model_name}")

            # Setup cloud storage
            self._setup_cloud_storage()

            # Test the setup
            self._test_generation()

            self.logger.info("✅ AI-POWERED Vertex AI client with Learning initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize: {str(e)}")
            raise

    def _setup_cloud_storage(self):
        """Setup Google Cloud Storage with comprehensive error handling"""
        try:
            from google.cloud import storage
            self.storage_client = storage.Client(project="warp-ai-hackathon")
            self.bucket_name = "warp-ai-hackathon-manim-codes"
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                self.logger.info(f"Creating bucket: {self.bucket_name}")
                bucket.create(location="us-central1")
            self.logger.info(f"✅ Cloud storage ready: {self.bucket_name}")
        except Exception as e:
            self.logger.error(f"❌ Cloud storage setup failed: {e}")
            self.storage_client = None

    def _save_to_cloud_storage(self, code: str, filename: str, validation_report: Dict = None, video_path: str = None) -> Optional[Dict]:
        """Save code and video to cloud storage with comprehensive error handling"""
        if not self.storage_client:
            self.logger.warning("⚠️ Cloud storage not available")
            return None

        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save code with learning metadata
            code_blob_name = f"generated_codes/{filename}_{timestamp}.py"
            enhanced_code = self._create_enhanced_code_with_header(code, validation_report)
            code_blob = bucket.blob(code_blob_name)
            code_blob.upload_from_string(enhanced_code, content_type='text/plain')
            code_blob.make_public()
            code_url = f"https://storage.googleapis.com/{self.bucket_name}/{code_blob_name}"

            result = {
                "code_blob_name": code_blob_name,
                "code_url": code_url,
                "bucket": self.bucket_name
            }

            # Save video if available
            if video_path and os.path.exists(video_path):
                try:
                    video_blob_name = f"generated_videos/{filename}_{timestamp}.mp4"
                    video_blob = bucket.blob(video_blob_name)
                    with open(video_path, 'rb') as video_file:
                        video_blob.upload_from_file(video_file, content_type='video/mp4')
                    video_blob.make_public()
                    video_url = f"https://storage.googleapis.com/{self.bucket_name}/{video_blob_name}"
                    result.update({
                        "video_blob_name": video_blob_name,
                        "video_url": video_url
                    })
                    self.logger.info(f"☁️ Video saved to cloud: {video_blob_name}")
                except Exception as video_error:
                    self.logger.warning(f"⚠️ Video upload failed: {video_error}")

            self.logger.info(f"☁️ Code saved to cloud: {code_blob_name}")
            return result

        except Exception as e:
            self.logger.error(f"❌ Cloud storage failed: {e}")
            return None

    def _create_enhanced_code_with_header(self, code: str, validation_report: Dict = None) -> str:
        """Create enhanced code with validation header and learning metrics"""
        learning_stats = self.error_learning.get_learning_stats()
        
        if validation_report:
            status = "✅ EXECUTION TESTED" if validation_report.get('execution_successful') else "⚠️ NEEDS REVIEW"
            quality_score = validation_report.get('quality_score', 'Unknown')
            execution_successful = validation_report.get('execution_successful', 'Unknown')
            video_generated = validation_report.get('video_generated', 'Unknown')
            layout_score = validation_report.get('layout_score', 'Unknown')
        else:
            status = "⚠️ NEEDS REVIEW"
            quality_score = execution_successful = video_generated = layout_score = 'Unknown'

        header = f'''"""
MANIM AI-GENERATED CODE - DYNAMICALLY CREATED WITH LEARNING

Generated: {datetime.now().isoformat()}
Status: {status}
Quality Score: {quality_score}/100
Layout Score: {layout_score}/100
Execution Successful: {execution_successful}
Video Generated: {video_generated}

=== LEARNING SYSTEM METRICS ===
Total Learned Patterns: {learning_stats.get('total_learned_patterns', 0)}
Average Success Rate: {learning_stats.get('average_success_rate', 0):.3f}
Error Prevention Applied: {self.error_prevention_count}
Generation Quality History: {len(self.generation_quality_history)} generations

This code was generated by AI with reinforcement learning from previous errors.
Layout management and collision detection applied.
Compatible with Manim v0.19.0

To run this animation:
manim -ql filename.py SceneName

=== LAYOUT SAFETY ===
- Frame overflow protection applied
- Object collision detection enabled
- Automatic spacing optimization
- VGroup organization when applicable
"""

'''
        return header + code

    def _test_generation(self):
        """Test basic generation with comprehensive error handling"""
        try:
            self.logger.info("🧪 Testing basic generation...")
            self._wait_for_rate_limit()
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Say 'Hello from AI-Powered Manim Generator with Learning!'"
            )

            if response and hasattr(response, 'text') and response.text:
                self.logger.info(f"✅ Test successful: {response.text[:50]}...")
            else:
                raise Exception("No response or text attribute")
        except Exception as e:
            self.logger.warning(f"⚠️ Test failed: {e}")

    def _wait_for_rate_limit(self):
        """Implement rate limiting with proper timing"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def generate_manim_code(self, subject: str, topic: str, complexity: str, specific_requirements: str) -> Dict:
        """
        Generate Manim code using AI with error learning and layout management.
        This method continuously improves quality through reinforcement learning.

        Args:
            subject: Educational subject (physics/mathematics/chemistry)
            topic: Specific topic to animate
            complexity: Difficulty level (beginner/intermediate/advanced)
            specific_requirements: Additional user requirements

        Returns:
            Dict containing generated code, validation results, learning metrics, and cloud storage info
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_prefix = f"{timestamp}_{subject}_{topic.replace(' ', '_')}"

        print(f"\n🚀 Generating LEARNING-ENHANCED Manim code for: {subject} - {topic}")
        self.logger.info(f"🚀 Starting enhanced generation for: {subject} - {topic} ({complexity})")

        generation_context = {
            'subject': subject,
            'topic': topic,
            'complexity': complexity,
            'requirements': specific_requirements,
            'timestamp': timestamp
        }

        try:
            # Step 1: Get learning context from previous errors
            print("🧠 Step 1: Loading Learning Context")
            prevention_context = self.error_learning.get_prevention_context(subject, topic, complexity)
            
            print(f"📚 Loaded {len(prevention_context.get('prevention_rules', []))} error prevention rules")
            print(f"📐 Loaded {len(prevention_context.get('layout_guidelines', []))} layout guidelines")

            # Step 2: Generate code with enhanced AI prompting
            print("🤖 Step 2: AI Code Generation with Error Prevention")
            ai_generated_code = self._generate_code_with_enhanced_learning(
                subject, topic, complexity, specific_requirements, prevention_context, debug_prefix
            )

            # Step 3: Apply layout management
            print("📐 Step 3: Layout Analysis and Optimization")
            layout_analysis = self.layout_manager.analyze_layout_issues(ai_generated_code)
            layout_optimized_code = layout_analysis.get('fixed_code', ai_generated_code)
            
            if layout_analysis.get('overlapping_risks'):
                print(f"⚠️ Fixed {len(layout_analysis['overlapping_risks'])} overlapping risks")
            if layout_analysis.get('frame_overflow_risks'):
                print(f"⚠️ Fixed {len(layout_analysis['frame_overflow_risks'])} overflow risks")

            # Step 4: Apply API compatibility fixes
            print("🔧 Step 4: API Compatibility Enhancement")
            api_fixed_code = self._apply_enhanced_api_fixes(layout_optimized_code)

            # Step 5: Execute and learn from results
            print("🎬 Step 5: Execution Testing with Learning")
            final_code, execution_result = self._execute_and_learn_from_results(
                api_fixed_code, generation_context, debug_prefix
            )

            # Step 6: Create comprehensive validation with learning metrics
            print("📊 Step 6: Quality Assessment with Learning Metrics")
            final_validation = self._create_enhanced_validation_report(
                final_code, execution_result, layout_analysis, prevention_context
            )

            # Step 7: Update learning system
            if execution_result.get('success'):
                self.error_learning.record_success(
                    generation_context, 
                    final_validation.get('quality_score', 0),
                    execution_result.get('execution_time', 0),
                    len(prevention_context.get('prevention_rules', []))
                )
                self.generation_quality_history.append(final_validation.get('quality_score', 0))
            else:
                # Learn from the error
                error_data = {
                    'type': 'execution_failure',
                    'message': execution_result.get('error', 'Unknown error'),
                    'stderr': execution_result.get('stderr', '')
                }
                learning_result = self.error_learning.learn_from_error(error_data, final_code, generation_context)
                print(f"🧠 Learned from error: {learning_result.get('error_hash', 'Unknown')[:8]}")

            # Step 8: Display enhanced results
            self._display_enhanced_results_with_learning(execution_result, final_validation, prevention_context)

            # Step 9: Save to cloud with learning metadata
            filename = f"{subject}_{topic.replace(' ', '_')}"
            cloud_result = self._save_to_cloud_storage(
                final_code,
                filename,
                final_validation,
                execution_result.get('video_path')
            )

            print("✅ LEARNING-ENHANCED generation completed!")
            
            return {
                "code": final_code,
                "validation": final_validation,
                "execution_result": execution_result,
                "cloud_storage": cloud_result,
                "learning_metrics": {
                    "prevention_rules_applied": len(prevention_context.get('prevention_rules', [])),
                    "layout_fixes_applied": len(layout_analysis.get('overlapping_risks', [])) + len(layout_analysis.get('frame_overflow_risks', [])),
                    "quality_trend": self._calculate_quality_trend(),
                    "error_prevention_count": self.error_prevention_count,
                    "learning_stats": self.error_learning.get_learning_stats()
                },
                "debug_files": debug_prefix
            }

        except Exception as e:
            error_msg = f"LEARNING-ENHANCED generation failed: {str(e)}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            # Learn from generation failure
            error_data = {
                'type': 'generation_failure',
                'message': str(e),
                'stderr': ''
            }
            self.error_learning.learn_from_error(error_data, '', generation_context)
            
            raise Exception(error_msg)

    def _generate_code_with_enhanced_learning(self, subject: str, topic: str, complexity: str, 
                                            specific_requirements: str, prevention_context: Dict, 
                                            debug_prefix: str) -> str:
        """Generate Manim code using AI with enhanced learning context"""
        
        # Build enhanced prompt with learning context
        prompt = self._build_learning_enhanced_prompt(
            subject, topic, complexity, specific_requirements, prevention_context
        )

        # Save prompt for debugging
        prompt_file = os.path.join(self.debug_dir, f"{debug_prefix}_learning_prompt.txt")
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        # Generate code using AI
        self._wait_for_rate_limit()
        print(f" 🤖 Sending learning-enhanced prompt to AI...")
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.types.GenerateContentConfig(**self.generation_config)
        )

        if not response or not hasattr(response, 'text') or not response.text:
            raise Exception("No valid response from AI")

        ai_generated_code = self._clean_ai_generated_code(response.text)

        # Save AI generated code
        ai_code_file = os.path.join(self.debug_dir, f"{debug_prefix}_enhanced_ai_generated.py")
        with open(ai_code_file, 'w', encoding='utf-8') as f:
            f.write(ai_generated_code)

        print(f" ✅ AI generated {len(ai_generated_code)} characters with learning enhancements")
        return ai_generated_code

    def _build_learning_enhanced_prompt(self, subject: str, topic: str, complexity: str, 
                                      specific_requirements: str, prevention_context: Dict) -> str:
        """Build AI prompt enhanced with learning context and error prevention"""
        
        # Extract prevention rules
        prevention_rules = prevention_context.get('prevention_rules', [])
        layout_guidelines = prevention_context.get('layout_guidelines', [])
        success_patterns = prevention_context.get('success_patterns', [])
        
        # Build prevention section
        prevention_section = ""
        if prevention_rules:
            prevention_section += "\n=== CRITICAL ERROR PREVENTION (LEARNED FROM EXPERIENCE) ===\n"
            for i, rule in enumerate(prevention_rules[:10], 1):  # Top 10 most important
                prevention_section += f"{i}. {rule['type'].upper()}: {rule['rule']}\n"
                prevention_section += f"   Importance: {rule['importance']} occurrences\n"
        
        # Build layout section
        layout_section = ""
        if layout_guidelines:
            layout_section += "\n=== LAYOUT OPTIMIZATION (ANTI-OVERLAP) ===\n"
            for guideline in layout_guidelines[:5]:
                layout_section += f"- {guideline['guideline']}\n"
                if guideline.get('code_example'):
                    layout_section += f"  Example: {guideline['code_example']}\n"
        
        # Build success patterns section
        success_section = ""
        if success_patterns:
            success_section += "\n=== PROVEN SUCCESS PATTERNS ===\n"
            for pattern in success_patterns[:3]:
                success_section += f"- {pattern['context']}: Quality {pattern['score']}/100\n"

        # Subject-specific enhancements
        subject_context = {
            'physics': "Include proper units, physical laws, vector representations, and real-world applications",
            'mathematics': "Show step-by-step calculations, use coordinate systems, proper mathematical notation",
            'chemistry': "Use standard chemical notation, molecular representations, reaction arrows, and chemical principles"
        }.get(subject.lower(), "Create educational content with clear explanations")

        # Complexity-specific instructions
        complexity_instructions = {
            'beginner': "Use simple language, basic concepts, slow animations, and clear visual explanations",
            'intermediate': "Include moderate complexity, some mathematical formulas, and detailed explanations",
            'advanced': "Add complex concepts, theoretical depth, advanced mathematics, and professional-level detail"
        }.get(complexity.lower(), "Use appropriate complexity for the audience")

        # Build the comprehensive prompt
        prompt = f"""You are an expert Manim animation developer with REINFORCEMENT LEARNING capabilities.
You have learned from {len(prevention_rules)} previous errors and {len(success_patterns)} successful patterns.

GENERATION PARAMETERS:
Subject: {subject}
Topic: {topic}
Complexity Level: {complexity}
Specific Requirements: {specific_requirements}

{prevention_section}

{layout_section}

{success_section}

SUBJECT-SPECIFIC CONTEXT:
{subject_context}

COMPLEXITY INSTRUCTIONS:
{complexity_instructions}

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
- Empty MathTex like r"\\\\text{{}}" - CAUSES COMPILATION ERRORS
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

🎨 ANIMATION STRUCTURE FOR {topic.upper()} IN {subject.upper()}:
1. Title introduction (positioned safely at TOP)
2. Main educational content with visual demonstrations
3. Key concepts with clear explanations (proper spacing)
4. Examples or applications (organized layout)
5. Summary or conclusion (bottom positioning)

SPECIFIC CONTENT GENERATION FOR "{topic}" IN {subject}:
- Create educational content specifically about {topic}
- Make it appropriate for {complexity} level learners
- Include visual representations relevant to the topic
- Add clear explanations and demonstrations
- Follow spacing and positioning rules above
- {specific_requirements}

QUALITY ASSURANCE CHECKLIST:
□ All objects positioned with adequate spacing
□ No overlapping elements
□ Frame boundaries respected
□ VGroup used for organization
□ Modern Manim API only
□ LaTeX kept simple and safe
□ Proper wait() statements included
□ Educational value maximized

Generate a COMPLETE, SAFE, LEARNING-ENHANCED Manim animation that educates about {topic} in {subject}:"""

        return prompt

    def _apply_enhanced_api_fixes(self, code: str) -> str:
        """Apply enhanced API compatibility fixes with learning"""
        fixed_code = code
        fixes_applied = []
        
        # Enhanced fix patterns based on learned errors
        fix_patterns = [
            (r'\.get_sides\(\)[^.]*', '', "Removed get_sides() method calls"),
            (r'\.get_part_by_text\([^)]+\)', '', "Removed get_part_by_text() method calls"),
            (r'\.get_part_by_tex\([^)]+\)', '', "Removed get_part_by_tex() method calls"),
            (r'Indicate\(([^,]+),\s*color=[^)]+\)', r'Indicate(\1)', "Removed color parameter from Indicate()"),
            (r'text_alignment=', 'text_align=', "Fixed text_alignment parameter"),
            (r'text_align=CENTER', 'text_align=ORIGIN', "Fixed CENTER alignment"),
            (r'MathTex\(r"\\\\text\{\{\}\}"\)', 'Text("Content")', "Fixed empty MathTex"),
            (r'\.center\(\)', '.move_to(ORIGIN)', "Replaced deprecated center() method"),
        ]
        
        for pattern, replacement, description in fix_patterns:
            if re.search(pattern, fixed_code):
                fixed_code = re.sub(pattern, replacement, fixed_code)
                fixes_applied.append(description)
                self.error_prevention_count += 1

        if fixes_applied:
            print(f" 🔧 Applied {len(fixes_applied)} learned API fixes:")
            for fix in fixes_applied:
                print(f"   - {fix}")
        else:
            print(" ✅ No API fixes needed - Learning system working!")

        return fixed_code

    def _execute_and_learn_from_results(self, code: str, context: Dict, debug_prefix: str) -> Tuple[str, Dict]:
        """Execute code with UNLIMITED intelligent error correction using Vertex AI"""
        
        print(f"\n🤖 Starting UNLIMITED AI Error Correction")
        print(f"⏱️ Maximum time: 15 minutes")
        print(f"🎯 Goal: Perfect working code with video generation")
        
        try:
            # Import the intelligent error fixer
            from intelligent_error_fixer import IntelligentErrorFixer
            
            # Create the intelligent fixer with 15-minute timeout
            error_fixer = IntelligentErrorFixer(self, max_timeout_minutes=15)
            
            # Run unlimited error correction
            correction_result = error_fixer.fix_code_until_perfect(code, context)
            
            # Prepare detailed execution result
            execution_result = {
                "success": correction_result['success'],
                "attempts": correction_result['total_attempts'],
                "total_time": correction_result['total_time'],
                "video_path": correction_result.get('video_path'),
                "error_history": correction_result['error_history'],
                "ai_fixes_applied": correction_result['ai_fixes_applied'],
                "timeout_reached": correction_result.get('timeout_reached', False),
                "final_error": correction_result.get('final_error')
            }
            
            # Display comprehensive results
            self._display_intelligent_correction_results(correction_result)
            
            # Learn from all errors encountered
            for error_info in correction_result['error_history']:
                self.error_learning.learn_from_error(
                    {
                        'type': error_info['type'],
                        'message': error_info['message'],
                        'stderr': error_info['stderr']
                    },
                    code,
                    context
                )
            
            return correction_result['final_code'], execution_result
            
        except ImportError:
            print("⚠️ Intelligent Error Fixer not available, falling back to basic execution")
            return self._execute_basic_fallback(code, context, debug_prefix)
        except Exception as e:
            self.logger.error(f"Intelligent correction system failed: {e}")
            print(f"❌ Intelligent correction failed: {e}")
            return self._execute_basic_fallback(code, context, debug_prefix)

    def _display_intelligent_correction_results(self, correction_result: Dict):
        """Display comprehensive results from intelligent error correction"""
        print(f"\n" + "="*80)
        print(f"🤖 INTELLIGENT ERROR CORRECTION RESULTS")
        print(f"="*80)
        
        print(f"📊 SUMMARY:")
        print(f" Success: {'✅ YES' if correction_result['success'] else '❌ NO'}")
        print(f" Total Attempts: {correction_result['total_attempts']}")
        print(f" Total Time: {correction_result['total_time']/60:.1f} minutes")
        print(f" Timeout Reached: {'Yes' if correction_result.get('timeout_reached') else 'No'}")
        
        if correction_result.get('video_path'):
            print(f" Video Generated: ✅ {correction_result['video_path']}")
        
        print(f"\n🤖 AI FIXES APPLIED:")
        ai_fixes = correction_result.get('ai_fixes_applied', [])
        if ai_fixes:
            for i, fix in enumerate(ai_fixes, 1):
                print(f" {i}. {fix.get('fix_description', 'Unknown fix')} ({fix.get('fix_time', 0):.1f}s)")
        else:
            print(" No AI fixes were successfully applied")
        
        print(f"\n📈 ERROR LEARNING:")
        error_history = correction_result.get('error_history', [])
        if error_history:
            error_types = {}
            for error in error_history:
                error_type = error.get('type', 'unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in error_types.items():
                print(f" {error_type}: {count} occurrence(s)")
        
        if correction_result.get('final_error'):
            final_error = correction_result['final_error']
            print(f"\n❌ FINAL ERROR:")
            print(f" Type: {final_error.get('type', 'unknown')}")
            print(f" Message: {final_error.get('message', 'Unknown')[:100]}...")
        
        print(f"="*80)

    def _execute_basic_fallback(self, code: str, context: Dict, debug_prefix: str) -> Tuple[str, Dict]:
        """Basic fallback execution with limited attempts"""
        print("🔄 Using basic fallback execution...")
        
        # Use the original execution logic but with more attempts
        current_code = code
        max_attempts = 10  # Increase from 3 to 10
        execution_history = []
        
        for attempt in range(max_attempts):
            print(f"\n🎬 Fallback execution attempt {attempt + 1}/{max_attempts}")
            
            exec_env = self._create_safe_execution_environment(current_code, debug_prefix, attempt)
            if not exec_env:
                continue
            
            execution_result = self._execute_manim_safely(exec_env)
            execution_history.append(execution_result)
            
            if execution_result["success"]:
                return current_code, {
                    "success": True,
                    "attempts": attempt + 1,
                    "final_result": execution_result,
                    "history": execution_history,
                    "video_path": execution_result.get("video_path")
                }
            
            # Apply basic fixes
            current_code = self._apply_basic_error_fixes(current_code, {
                'type': 'execution_error',
                'message': execution_result.get('error', ''),
                'stderr': execution_result.get('stderr', '')
            })
        
        return current_code, {
            "success": False,
            "attempts": max_attempts,
            "final_result": execution_result,
            "history": execution_history
        }


    def _create_safe_execution_environment(self, code: str, debug_prefix: str, attempt: int) -> Optional[Dict]:
        """Create safe execution environment with Windows compatibility"""
        try:
            temp_base = tempfile.gettempdir()
            exec_id = f"manim_{debug_prefix[:8]}_{attempt}_{int(time.time())}"
            exec_dir = Path(temp_base) / exec_id

            exec_dir.mkdir(exist_ok=True, parents=True)

            scene_name = self._extract_scene_name(code)
            if not scene_name:
                scene_name = "MainScene"
                code = self._add_scene_class_if_missing(code, scene_name)

            # Create Python file
            python_file = exec_dir / f"{scene_name}.py"
            with open(python_file, 'w', encoding='utf-8') as f:
                f.write(code)

            # Create media directory
            media_dir = exec_dir / "media"
            media_dir.mkdir(exist_ok=True)

            return {
                "exec_dir": exec_dir,
                "python_file": python_file,
                "scene_name": scene_name,
                "media_dir": media_dir,
                "code": code
            }

        except Exception as e:
            self.logger.error(f"Failed to create execution environment: {e}")
            return None

    def _extract_scene_name(self, code: str) -> Optional[str]:
        """Extract scene class name from code"""
        scene_match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\):', code)
        return scene_match.group(1) if scene_match else None

    def _add_scene_class_if_missing(self, code: str, scene_name: str) -> str:
        """Add scene class if missing"""
        if f'class {scene_name}' not in code:
            # Wrap existing code in a scene class
            lines = code.split('\n')
            imports = []
            content = []
            
            for line in lines:
                if line.strip().startswith(('from ', 'import ')):
                    imports.append(line)
                else:
                    content.append(line)
            
            new_code = '\n'.join(imports) + '\n\n'
            new_code += f'class {scene_name}(Scene):\n'
            new_code += '    def construct(self):\n'
            
            for line in content:
                if line.strip():
                    new_code += f'        {line}\n'
                else:
                    new_code += '\n'
            
            return new_code
        
        return code

    def _execute_manim_safely(self, exec_env: Dict) -> Dict:
        """Execute Manim with comprehensive error handling and debugging"""
        try:
            start_time = time.time()
            
            if self.debug_mode:
                print(f"      🎬 Starting Manim execution...")
                print(f"         Working directory: {exec_env['exec_dir']}")
                print(f"         Python file: {exec_env['python_file'].name}")
                print(f"         Scene name: {exec_env['scene_name']}")
            
            # Build Manim command
            cmd = [
                "python", "-m", "manim",
                "-ql",  # Low quality for faster execution
                "--media_dir", str(exec_env["media_dir"]),
                str(exec_env["python_file"]),
                exec_env["scene_name"]
            ]

            if self.debug_mode:
                print(f"         Command: {' '.join(cmd)}")
            
            # Execute command with real-time output
            process = subprocess.Popen(
                cmd,
                cwd=str(exec_env["exec_dir"]),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            output_lines = []
            error_indicators = []
            
            # Read output in real-time
            if self.debug_mode:
                print(f"      📺 Manim execution output:")
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    
                    if self.debug_mode and line:
                        # Show important lines
                        if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'warning']):
                            print(f"         ⚠️  {line}")
                            error_indicators.append(line)
                        elif any(keyword in line.lower() for keyword in ['rendering', 'writing', 'file ready']):
                            print(f"         📹 {line}")
                        elif "%" in line or "frame" in line.lower():
                            print(f"         ⏳ {line}")
            
            # Wait for process to complete
            return_code = process.poll()
            execution_time = time.time() - start_time

            if self.debug_mode:
                print(f"      ✅ Manim execution completed in {execution_time:.2f}s")
                print(f"         Return code: {return_code}")

            # Check for video output
            videos_dir = exec_env["media_dir"] / "videos"
            video_path = None
            
            if videos_dir.exists():
                if self.debug_mode:
                    print(f"      📁 Checking for video files in {videos_dir}")
                
                for video_file in videos_dir.rglob("*.mp4"):
                    video_path = str(video_file)
                    if self.debug_mode:
                        print(f"         📹 Found video: {video_file.name}")
                    break

            all_output = "\n".join(output_lines)
            
            if return_code == 0 and video_path:
                # Copy video to debug directory for persistence
                debug_video_path = os.path.join(self.debug_dir, f"{exec_env['scene_name']}_output.mp4")
                shutil.copy2(video_path, debug_video_path)
                
                if self.debug_mode:
                    print(f"      ✅ Success! Video saved to {debug_video_path}")
                
                return {
                    "success": True,
                    "video_path": debug_video_path,
                    "execution_time": execution_time,
                    "stdout": all_output,
                    "stderr": "",
                    "return_code": return_code
                }
            else:
                if self.debug_mode:
                    print(f"      ❌ Execution failed:")
                    print(f"         Return code: {return_code}")
                    print(f"         Video found: {'Yes' if video_path else 'No'}")
                    if error_indicators:
                        print(f"         Key errors:")
                        for error in error_indicators[-3:]:  # Show last 3 errors
                            print(f"           - {error}")
                
                return {
                    "success": False,
                    "error": f"Process failed with return code {return_code}",
                    "execution_time": execution_time,
                    "stdout": all_output,
                    "stderr": "\n".join(error_indicators),
                    "return_code": return_code
                }

        except subprocess.TimeoutExpired:
            error_msg = f"Execution timeout after {self.execution_timeout} seconds"
            if self.debug_mode:
                print(f"      ⏰ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "execution_time": self.execution_timeout,
                "stdout": "",
                "stderr": "Timeout",
                "return_code": -1
            }
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            if self.debug_mode:
                print(f"      💥 {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "execution_time": 0,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
        finally:
            # Cleanup
            try:
                if exec_env and exec_env.get("exec_dir") and exec_env["exec_dir"].exists():
                    if self.debug_mode:
                        print(f"      🧹 Cleaning up temporary directory...")
                    shutil.rmtree(exec_env["exec_dir"], ignore_errors=True)
            except Exception as cleanup_error:
                if self.debug_mode:
                    print(f"      ⚠️ Cleanup warning: {cleanup_error}")


    def _apply_intelligent_error_fixes(self, code: str, error_data: Dict, learning_result: Dict, context: Dict) -> str:
        """Apply intelligent fixes based on learned patterns"""
        try:
            # Get suggested fixes from learning system
            suggested_fixes = learning_result.get('suggested_fixes', [])
            
            fixed_code = code
            
            # Apply known solutions for this error pattern
            error_hash = learning_result.get('error_hash')
            if error_hash in self.error_learning.error_patterns:
                pattern = self.error_learning.error_patterns[error_hash]
                solution = pattern.get('solution', '')
                
                if solution:
                    print(f"   🎯 Applying learned solution for {pattern['type']}")
                    fixed_code = self._apply_learned_solution(fixed_code, solution, pattern['type'])
            
            # Apply layout fixes if it's a layout issue
            if learning_result.get('analysis', {}).get('is_layout_issue'):
                print("   📐 Applying layout intelligence...")
                layout_fixes = self.layout_manager.analyze_layout_issues(fixed_code)
                fixed_code = layout_fixes.get('fixed_code', fixed_code)
            
            # Apply common fixes based on error category
            analysis = learning_result.get('analysis', {})
            category = analysis.get('category', 'unknown')
            
            category_fixes = {
                'latex_compilation': self._fix_latex_errors,
                'api_compatibility': self._fix_api_errors,
                'missing_import': self._fix_import_errors,
                'parameter_error': self._fix_parameter_errors,
                'layout_issue': self._fix_layout_errors
            }
            
            fix_function = category_fixes.get(category)
            if fix_function:
                print(f"   🔧 Applying {category} fixes...")
                fixed_code = fix_function(fixed_code, error_data)
            
            return fixed_code
            
        except Exception as e:
            self.logger.error(f"Intelligent fix failed: {e}")
            return code

    def _apply_learned_solution(self, code: str, solution: str, error_type: str) -> str:
        """Apply a learned solution to the code"""
        try:
            if 'latex_compilation' in error_type:
                # Apply LaTeX fixes
                code = re.sub(r'MathTex\(r"\\\\text\{\{\}\}"\)', 'Text("Text")', code)
                code = re.sub(r'MathTex\(([^)]*)\{([^}]*)\}([^)]*)\)', r'MathTex(\1{{\2}}\3)', code)
                
            elif 'api_compatibility' in error_type:
                # Apply API fixes
                code = re.sub(r'\.get_sides\(\)', '', code)
                code = re.sub(r'\.get_part_by_text\([^)]+\)', '[0]', code)
                
            elif 'layout_issue' in error_type:
                # Apply layout fixes
                layout_analysis = self.layout_manager.analyze_layout_issues(code)
                code = layout_analysis.get('fixed_code', code)
                
            return code
            
        except Exception as e:
            self.logger.error(f"Failed to apply learned solution: {e}")
            return code

    def _fix_latex_errors(self, code: str, error_data: Dict) -> str:
        """Fix LaTeX compilation errors"""
        fixed_code = code
        
        # Common LaTeX fixes
        latex_fixes = [
            (r'MathTex\(r"\\\\text\{\{\}\}"\)', 'Text("Content")'),
            (r'MathTex\(r""\)', 'Text("Math")'),
            (r'\\\\text\{([^}]*)\}', r'\\\\text{{\1}}'),
            (r'MathTex\(([^)]*[^\\])\{([^}]*)\}([^)]*)\)', r'MathTex(\1{{\2}}\3)'),
        ]
        
        for pattern, replacement in latex_fixes:
            fixed_code = re.sub(pattern, replacement, fixed_code)
        
        return fixed_code

    def _fix_api_errors(self, code: str, error_data: Dict) -> str:
        """Fix API compatibility errors"""
        fixed_code = code
        
        # API compatibility fixes
        api_fixes = [
            (r'\.get_sides\(\)', ''),
            (r'\.get_part_by_text\([^)]+\)', '[0]'),
            (r'\.get_part_by_tex\([^)]+\)', '[0]'),
            (r'Indicate\(([^,]+),\s*color=[^)]+\)', r'Indicate(\1)'),
            (r'\.center\(\)', '.move_to(ORIGIN)'),
        ]
        
        for pattern, replacement in api_fixes:
            fixed_code = re.sub(pattern, replacement, fixed_code)
        
        return fixed_code

    def _fix_import_errors(self, code: str, error_data: Dict) -> str:
        """Fix import-related errors"""
        if 'from manim import *' not in code and 'import manim' not in code:
            code = 'from manim import *\nimport numpy as np\n\n' + code
        return code

    def _fix_parameter_errors(self, code: str, error_data: Dict) -> str:
        """Fix parameter-related errors"""
        fixed_code = code
        
        # Common parameter fixes
        param_fixes = [
            (r'text_alignment=', 'text_align='),
            (r'text_align=CENTER', 'text_align=ORIGIN'),
            (r'font_size=(\d+)', lambda m: f'font_size={min(int(m.group(1)), 32)}'),
        ]
        
        for pattern, replacement in param_fixes:
            if callable(replacement):
                fixed_code = re.sub(pattern, replacement, fixed_code)
            else:
                fixed_code = re.sub(pattern, replacement, fixed_code)
        
        return fixed_code

    def _fix_layout_errors(self, code: str, error_data: Dict) -> str:
        """Fix layout-related errors"""
        layout_analysis = self.layout_manager.analyze_layout_issues(code)
        return layout_analysis.get('fixed_code', code)

    def _apply_basic_error_fixes(self, code: str, error_data: Dict) -> str:
        """Apply basic error fixes as fallback"""
        fixed_code = code
        
        # Basic fixes
        basic_fixes = [
            (r'get_sides\(\)', ''),
            (r'get_part_by_text\([^)]+\)', ''),
            (r'MathTex\(r""\)', 'Text("Content")'),
            (r'Indicate\([^,]+,\s*color=[^)]+\)', 'Indicate(obj)'),
        ]
        
        for pattern, replacement in basic_fixes:
            fixed_code = re.sub(pattern, replacement, fixed_code)
        
        return fixed_code

    def _calculate_quality_trend(self) -> Dict:
        """Calculate quality improvement trend"""
        if len(self.generation_quality_history) < 2:
            return {"trend": "insufficient_data", "improvement": 0.0}
        
        recent = self.generation_quality_history[-5:]  # Last 5 generations
        older = self.generation_quality_history[-10:-5] if len(self.generation_quality_history) >= 10 else []
        
        if not older:
            return {"trend": "improving", "improvement": 0.0}
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        
        improvement = recent_avg - older_avg
        trend = "improving" if improvement > 0 else "declining" if improvement < -5 else "stable"
        
        return {"trend": trend, "improvement": improvement}

    def _create_enhanced_validation_report(self, code: str, execution_result: Dict, 
                                         layout_analysis: Dict, prevention_context: Dict) -> Dict:
        """Create comprehensive validation report with learning metrics"""
        
        validation = {
            "syntax_valid": False,
            "execution_successful": execution_result.get("success", False),
            "video_generated": bool(execution_result.get("video_path")),
            "manim_compatible": False,
            "has_scene_class": False,
            "has_construct": False,
            "ai_generated": True,
            "quality_score": 0,
            "layout_score": 0,
            "learning_enhanced": True,
            "prevention_rules_applied": len(prevention_context.get('prevention_rules', [])),
            "warnings": [],
            "issues": [],
            "learning_metrics": {}
        }

        try:
            if code and isinstance(code, str):
                # Syntax check
                try:
                    ast.parse(code)
                    validation["syntax_valid"] = True
                except SyntaxError as e:
                    validation["syntax_valid"] = False
                    validation["issues"].append(f"Syntax error: {str(e)}")

                # Basic checks
                if 'from manim import *' in code or 'import manim' in code:
                    validation["manim_compatible"] = True
                else:
                    validation["issues"].append("Missing Manim imports")

                if re.search(r'class\s+\w+\s*\(\s*Scene\s*\):', code):
                    validation["has_scene_class"] = True
                else:
                    validation["issues"].append("No Scene class found")

                if 'def construct(' in code:
                    validation["has_construct"] = True
                else:
                    validation["issues"].append("No construct method found")

                # Layout assessment
                layout_validation = self.layout_manager.validate_final_layout(code)
                validation["layout_score"] = layout_validation.get('layout_score', 0)
                validation["warnings"].extend(layout_validation.get('warnings', []))

                # Learning metrics
                learning_stats = self.error_learning.get_learning_stats()
                validation["learning_metrics"] = {
                    "patterns_applied": validation["prevention_rules_applied"],
                    "total_learned_patterns": learning_stats.get('total_learned_patterns', 0),
                    "success_rate_trend": learning_stats.get('average_success_rate', 0),
                    "quality_trend": self._calculate_quality_trend()
                }

        except Exception as e:
            validation["issues"].append(f"Validation failed: {str(e)}")

        # Calculate enhanced quality score
        score = 0
        if validation["syntax_valid"]: score += 15
        if validation["execution_successful"]: score += 35
        if validation["video_generated"]: score += 25
        if validation["manim_compatible"]: score += 10
        if validation["has_scene_class"]: score += 5
        if validation["has_construct"]: score += 5
        
        # Layout bonus
        score += validation["layout_score"] * 0.05  # Max 5 points from layout
        
        # Learning bonus
        if validation["prevention_rules_applied"] > 0:
            score += min(validation["prevention_rules_applied"] * 2, 10)  # Max 10 points
        
        # Deduct for issues and warnings
        score -= len(validation["issues"]) * 3
        score -= len(validation["warnings"]) * 1
        
        validation["quality_score"] = max(0, min(100, score))

        return validation

    def _display_enhanced_results_with_learning(self, execution_result: Dict, 
                                               validation: Dict, prevention_context: Dict):
        """Display comprehensive results with learning information"""
        print("\n" + "="*90)
        print("🎯 LEARNING-ENHANCED MANIM GENERATION RESULTS")
        print("="*90)

        try:
            # Execution summary
            print(f"📊 EXECUTION SUMMARY:")
            print(f" Success: {'✅ YES' if execution_result.get('success') else '❌ NO'}")
            print(f" Attempts: {execution_result.get('attempts', 1)}")
            if execution_result.get("video_path"):
                print(f" Video: ✅ Generated successfully")

            # Learning metrics
            learning_metrics = validation.get("learning_metrics", {})
            print(f"\n🧠 LEARNING SYSTEM METRICS:")
            print(f" Prevention Rules Applied: {validation.get('prevention_rules_applied', 0)}")
            print(f" Total Learned Patterns: {learning_metrics.get('total_learned_patterns', 0)}")
            print(f" Success Rate Trend: {learning_metrics.get('success_rate_trend', 0):.3f}")
            
            quality_trend = learning_metrics.get('quality_trend', {})
            print(f" Quality Trend: {quality_trend.get('trend', 'unknown')} ({quality_trend.get('improvement', 0):+.1f})")

            # Quality assessment
            print(f"\n📋 ENHANCED QUALITY ASSESSMENT:")
            print(f" Overall Quality Score: {validation.get('quality_score', 0)}/100")
            print(f" Layout Score: {validation.get('layout_score', 0)}/100")
            print(f" Execution Success: {'✅' if validation.get('execution_successful') else '❌'}")
            print(f" Video Generated: {'✅' if validation.get('video_generated') else '❌'}")
            print(f" Learning Enhanced: {'✅' if validation.get('learning_enhanced') else '❌'}")

            # Issues and improvements
            if validation.get('issues'):
                print(f"\n❗ ISSUES DETECTED:")
                for issue in validation['issues']:
                    print(f" - {issue}")

            if validation.get('warnings'):
                print(f"\n⚠️ WARNINGS:")
                for warning in validation['warnings']:
                    print(f" - {warning}")

            # Learning insights
            if prevention_context.get('prevention_rules'):
                print(f"\n🛡️ ERROR PREVENTION APPLIED:")
                for rule in prevention_context['prevention_rules'][:3]:
                    print(f" - {rule['type']}: {rule['rule'][:50]}...")

        except Exception as e:
            print(f" Display error: {e}")

        print("="*90)

    def _clean_ai_generated_code(self, raw_code: str) -> str:
        """Clean AI-generated code and ensure proper format"""
        if not raw_code or not isinstance(raw_code, str):
            raise Exception("Invalid AI response")

        cleaned_code = raw_code

        # Remove markdown if present
        if '```python' in cleaned_code:
            start = cleaned_code.find('```python') + len('```python')
            end = cleaned_code.find('```', start)
            if end != -1:
                cleaned_code = cleaned_code[start:end].strip()
        elif '```' in cleaned_code:
            start = cleaned_code.find('```') + 3
            end = cleaned_code.find('```', start)
            if end != -1:
                cleaned_code = cleaned_code[start:end].strip()

        # Remove explanatory text at the beginning
        lines = cleaned_code.split('\n')
        code_start_index = 0
        for i, line in enumerate(lines):
            if (line.strip().startswith(('from ', 'import ', 'class ', 'def ')) or
                (line.strip() and not line.strip().startswith(('Here', 'This', 'The following')))):
                code_start_index = i
                break

        cleaned_code = '\n'.join(lines[code_start_index:])

        # Ensure proper imports
        if 'from manim import *' not in cleaned_code and 'import manim' not in cleaned_code:
            cleaned_code = 'from manim import *\nimport numpy as np\n\n' + cleaned_code

        return cleaned_code.strip()

    def get_learning_dashboard(self) -> Dict:
        """Get comprehensive learning dashboard data"""
        try:
            learning_stats = self.error_learning.get_learning_stats()
            
            dashboard = {
                "system_status": {
                    "operational": True,
                    "learning_enabled": True,
                    "layout_management": True,
                    "error_prevention_active": self.error_prevention_count > 0
                },
                "learning_metrics": learning_stats,
                "quality_trends": {
                    "current_session": {
                        "generations": len(self.generation_quality_history),
                        "average_quality": sum(self.generation_quality_history) / len(self.generation_quality_history) if self.generation_quality_history else 0,
                        "trend": self._calculate_quality_trend()
                    },
                    "prevention_effectiveness": {
                        "rules_applied": self.error_prevention_count,
                        "success_rate": learning_stats.get('average_success_rate', 0)
                    }
                },
                "recent_improvements": {
                    "api_fixes_applied": self.error_prevention_count,
                    "layout_optimizations": "Active",
                    "reinforcement_learning": "Active"
                }
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Failed to generate learning dashboard: {e}")
            return {"error": str(e)}
