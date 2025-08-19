import uuid
from datetime import datetime
from typing import Dict, Any
from vertex_ai_service import VertexAIClient
from manim_executor import ManimExecutor
from utils import setup_logger

class ManimAIAgent:
    """
    Enhanced Manim AI Agent with real execution testing and auto-fixing.
    Coordinates between Vertex AI code generation and real Manim execution.
    """
    
    def __init__(self):
        """Initialize the enhanced Manim AI Agent"""
        self.vertex_client = VertexAIClient()
        self.manim_executor = ManimExecutor()
        self.logger = setup_logger("manim_ai_agent")
        
        # Configuration
        self.supported_subjects = ["physics", "mathematics", "chemistry"]
        self.complexity_levels = ["beginner", "intermediate", "advanced"]
        self.max_retries = 2
        self.generation_stats = {
            "total_requests": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "execution_successful": 0,
            "average_generation_time": 0
        }
        
        self.logger.info("Enhanced ManimAIAgent initialized successfully")

    def generate_educational_code(self, 
                                 subject: str,
                                 topic: str,
                                 complexity: str = "intermediate",
                                 specific_requirements: str = "") -> Dict[str, Any]:
        """
        Generate educational Manim code with real execution testing and auto-fixing.
        
        Args:
            subject: Educational subject (physics/mathematics/chemistry)
            topic: Specific topic to create animation for
            complexity: Difficulty level (beginner/intermediate/advanced)
            specific_requirements: Additional requirements or constraints
            
        Returns:
            Dict containing success status, code, execution results, and cloud storage info
        """
        
        start_time = datetime.now()
        request_id = str(uuid.uuid4())
        self.generation_stats["total_requests"] += 1
        
        print("\n🚀 === AI-POWERED CODE GENERATION WITH REAL EXECUTION ===")
        print(f"🆔 Request ID: {request_id}")
        print(f"📋 Subject: {subject}")
        print(f"📋 Topic: {topic}")
        print(f"📋 Complexity: {complexity}")
        print(f"📋 Requirements: {specific_requirements}")
        print(f"🤖 AI Generation: ENABLED")
        print(f"🎬 Real Manim Execution: ENABLED")
        print(f"🔧 Auto-Error Fixing: ENABLED")
        
        self.logger.info(f"Starting AI-powered generation with execution: {subject} - {topic}")
        self.logger.info(f"Request ID: {request_id}")
        
        try:
            # Step 1: Input validation
            print("\n🔍 STEP 1: Input Validation")
            validation_result = self._validate_inputs(subject, topic, complexity)
            if not validation_result["valid"]:
                print(f"❌ Validation failed: {validation_result['message']}")
                self.generation_stats["failed_generations"] += 1
                return self._create_error_response(request_id, validation_result["message"])
            
            print("✅ Input validation passed")
            
            # Step 2: Enhanced topic preprocessing
            print("\n🔍 STEP 2: Topic Preprocessing")
            processed_topic = self._preprocess_topic(topic, subject)
            enhanced_requirements = self._enhance_requirements(specific_requirements, subject, complexity)
            
            print(f"📝 Original topic: {topic}")
            print(f"📝 Processed topic: {processed_topic}")
            print(f"📝 Enhanced requirements: {enhanced_requirements}")
            
            # Step 3: Generate code with AI and real execution testing
            print("\n🔍 STEP 3: AI Code Generation + Real Execution Testing")
            generation_result = self.vertex_client.generate_manim_code(
                subject=subject,
                topic=processed_topic,
                complexity=complexity,
                specific_requirements=enhanced_requirements
            )
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            if generation_result.get("validation", {}).get("execution_successful"):
                self.generation_stats["successful_generations"] += 1
                self.generation_stats["execution_successful"] += 1
            else:
                self.generation_stats["failed_generations"] += 1
            
            self._update_stats(generation_time)
            
            print(f"\n🎉 === AI-POWERED GENERATION COMPLETE ===")
            print(f"⏱️ Total time: {generation_time:.2f} seconds")
            
            # Enhanced result display
            self._display_enhanced_results(generation_result)
            
            return self._create_success_response(
                request_id=request_id,
                subject=subject,
                topic=topic,
                complexity=complexity,
                result=generation_result,
                generation_time=generation_time
            )
                
        except Exception as e:
            print(f"💥 === AI-POWERED GENERATION ERROR ===")
            print(f"❌ {str(e)}")
            self.logger.error(f"AI-powered generation error: {str(e)}")
            self.generation_stats["failed_generations"] += 1
            return self._create_error_response(request_id, str(e))
    
    def _preprocess_topic(self, topic: str, subject: str) -> str:
        """Preprocess and enhance topic description for better AI code generation"""
        
        topic = topic.strip().lower()
        
        # Subject-specific topic enhancement for AI prompting
        topic_enhancements = {
            'physics': {
                'motion': 'projectile motion with gravity and kinematics',
                'wave': 'wave mechanics, interference, and wave properties',
                'electric': 'electric field, potential, and electromagnetic theory',
                'magnetic': 'magnetic field and electromagnetic induction',
                'energy': 'kinetic and potential energy conservation',
                'force': 'forces, Newton\'s laws, and dynamics',
                'momentum': 'momentum conservation and collisions',
                'thermodynamics': 'heat transfer and thermodynamic processes'
            },
            'mathematics': {
                'function': 'function graphing, transformations, and analysis',
                'derivative': 'derivative calculation, interpretation, and applications',
                'integral': 'integration techniques and real-world applications',
                'geometry': 'geometric constructions, proofs, and theorems',
                'algebra': 'algebraic equations, systems, and problem solving',
                'trigonometry': 'trigonometric functions, identities, and applications',
                'calculus': 'limits, derivatives, integrals, and applications',
                'statistics': 'probability distributions and statistical analysis'
            },
            'chemistry': {
                'molecule': 'molecular structure, bonding, and geometry',
                'reaction': 'chemical reaction mechanisms and kinetics',
                'atom': 'atomic structure, electron configuration, and orbitals',
                'bond': 'chemical bonding, molecular geometry, and polarity',
                'acid': 'acids, bases, pH, and chemical equilibrium',
                'organic': 'organic compounds, functional groups, and reactions',
                'periodic': 'periodic table trends and element properties'
            }
        }
        
        if subject in topic_enhancements:
            for key, enhancement in topic_enhancements[subject].items():
                if key in topic:
                    return enhancement
        
        return topic
    
    def _enhance_requirements(self, requirements: str, subject: str, complexity: str) -> str:
        """Enhance requirements based on subject and complexity for better AI animations"""
        
        base_requirements = requirements
        
        # Complexity-based enhancements for AI prompting
        complexity_enhancements = {
            'beginner': "Use simple colors, large clear labels, slow animations for easy understanding, basic concepts only, avoid complex mathematics",
            'intermediate': "Include mathematical formulas, moderate animation speed, detailed explanations, multiple examples, some advanced concepts",
            'advanced': "Add complex visualizations, multiple related concepts, professional-level detail, theoretical depth, advanced mathematics"
        }
        
        # Subject-specific requirements for AI prompting
        subject_requirements = {
            'physics': "Include proper units, vector representations, physical laws, real-world applications, quantitative analysis, and scientific accuracy",
            'mathematics': "Show step-by-step calculations, use coordinate systems, proper mathematical notation, proofs where appropriate, clear logic flow",
            'chemistry': "Use standard chemical notation, proper molecular representations, reaction arrows, electron movements, chemical principles, and safety considerations"
        }
        
        enhanced = base_requirements
        if complexity in complexity_enhancements:
            enhanced += f". {complexity_enhancements[complexity]}"
        if subject in subject_requirements:
            enhanced += f". {subject_requirements[subject]}"
        
        # Add AI-specific requirements
        enhanced += ". Ensure code is AI-generated, execution-ready with proper Manim syntax, complete animations, and no deprecated methods."
        
        return enhanced
    
    def _display_enhanced_results(self, result: Dict):
        """Display comprehensive results with AI generation and execution information"""
        
        validation = result.get("validation", {})
        execution_result = result.get("execution_result", {})
        cloud_storage = result.get("cloud_storage", {})
        
        print(f"\n📊 COMPREHENSIVE AI GENERATION ASSESSMENT:")
        print(f"✅ Syntax Valid: {validation.get('syntax_valid', False)}")
        print(f"✅ AI Generated: {validation.get('ai_generated', False)}")
        print(f"✅ Execution Successful: {validation.get('execution_successful', False)}")
        print(f"✅ Video Generated: {validation.get('video_generated', False)}")
        print(f"✅ Manim Compatible: {validation.get('manim_compatible', False)}")
        print(f"✅ Quality Score: {validation.get('quality_score', 0)}/100")
        
        # Execution details
        if execution_result.get("success"):
            attempts = execution_result.get("attempts", 1)
            final_result = execution_result.get("final_result", {})
            
            print(f"\n🎬 EXECUTION DETAILS:")
            print(f"   Success: ✅ YES")
            print(f"   Attempts: {attempts}")
            
            if final_result.get("video_path"):
                print(f"   Video Generated: ✅ YES")
                print(f"   Video Path: {final_result['video_path']}")
            else:
                print(f"   Video Generated: ❌ NO")
        else:
            print(f"\n🎬 EXECUTION DETAILS:")
            print(f"   Success: ❌ NO")
            print(f"   Attempts: {execution_result.get('attempts', 0)}")
            
            if execution_result.get("final_result", {}).get("error"):
                error = execution_result["final_result"]["error"]
                print(f"   Last Error: {error[:100]}..." if len(error) > 100 else f"   Last Error: {error}")
        
        # Quality warnings and issues
        if validation.get('warnings'):
            print(f"\n⚠️ WARNINGS:")
            for warning in validation['warnings']:
                print(f"   - {warning}")
        
        if validation.get('issues'):
            print(f"\n❗ ISSUES:")
            for issue in validation['issues']:
                print(f"   - {issue}")
        
        # Cloud storage information
        if cloud_storage:
            print(f"\n☁️ CLOUD STORAGE:")
            print(f"📁 Bucket: {cloud_storage.get('bucket', 'Unknown')}")
            print(f"📄 Code URL: {cloud_storage.get('code_url', 'Not available')}")
            
            if cloud_storage.get('video_url'):
                print(f"🎥 Video URL: {cloud_storage.get('video_url')}")
            
            # Readiness assessment
            if validation.get('execution_successful') and validation.get('video_generated'):
                print(f"\n✅ AI-GENERATED CODE IS EXECUTION-TESTED AND READY!")
                print(f"💡 Download code from URL above and run:")
                print(f"   manim -ql downloaded_file.py SceneName")
                print(f"💡 Or watch the generated video directly from the video URL")
            elif validation.get('execution_successful'):
                print(f"\n✅ AI-generated code executed successfully")
                print(f"💡 Download and run manually to generate video")
            else:
                print(f"\n⚠️ AI-generated code needs manual review before execution")
                print(f"💡 Check the issues above and fix before running")
        
        # Session statistics
        print(f"\n📈 SESSION STATISTICS:")
        print(f"   Total Requests: {self.generation_stats['total_requests']}")
        print(f"   Successful: {self.generation_stats['successful_generations']}")
        print(f"   Execution Success: {self.generation_stats['execution_successful']}")
        print(f"   Success Rate: {(self.generation_stats['successful_generations']/max(1, self.generation_stats['total_requests']))*100:.1f}%")
    
    def _validate_inputs(self, subject: str, topic: str, complexity: str) -> Dict[str, Any]:
        """Comprehensive input validation with helpful error messages"""
        
        if not subject or subject.lower() not in self.supported_subjects:
            return {
                "valid": False, 
                "message": f"Subject must be one of: {', '.join(self.supported_subjects)}. Got: '{subject}'"
            }
        
        if not topic or len(topic.strip()) < 3:
            return {
                "valid": False, 
                "message": f"Topic must be at least 3 characters long. Got: '{topic}'"
            }
        
        if complexity.lower() not in self.complexity_levels:
            return {
                "valid": False, 
                "message": f"Complexity must be one of: {', '.join(self.complexity_levels)}. Got: '{complexity}'"
            }
        
        # Additional validation for topic relevance
        forbidden_words = ['test', 'example', 'sample', 'demo']
        if any(word in topic.lower() for word in forbidden_words):
            return {
                "valid": False,
                "message": f"Please provide a specific educational topic, not a generic term like '{topic}'"
            }
        
        return {"valid": True, "message": "All inputs are valid"}
    
    def _update_stats(self, generation_time: float):
        """Update generation statistics"""
        
        total_successful = self.generation_stats["successful_generations"]
        if total_successful > 0:
            current_avg = self.generation_stats["average_generation_time"]
            new_avg = ((current_avg * (total_successful - 1)) + generation_time) / total_successful
            self.generation_stats["average_generation_time"] = new_avg
        else:
            self.generation_stats["average_generation_time"] = generation_time
    
    def _create_success_response(self, **kwargs) -> Dict[str, Any]:
        """Create comprehensive success response with all relevant information"""
        return {
            "success": True,
            "request_id": kwargs["request_id"],
            "timestamp": datetime.now().isoformat(),
            "data": {
                "subject": kwargs["subject"],
                "topic": kwargs["topic"],
                "complexity": kwargs["complexity"],
                "result": kwargs["result"],
                "generation_time_seconds": kwargs.get("generation_time", 0),
                "ai_generated": True,
                "execution_tested": True,
                "session_stats": self.generation_stats.copy()
            },
            "metadata": {
                "agent_version": "ai_powered_v3.0",
                "features": [
                    "ai_powered_code_generation",
                    "real_execution_testing",
                    "ai_powered_error_fixing", 
                    "cloud_storage",
                    "video_generation",
                    "quality_assessment"
                ]
            }
        }
    
    def _create_error_response(self, request_id: str, message: str) -> Dict[str, Any]:
        """Create comprehensive error response with debugging information"""
        return {
            "success": False,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "error": {
                "message": message,
                "type": "ai_generation_error",
                "session_stats": self.generation_stats.copy()
            },
            "suggestions": [
                "Check if all required packages are installed",
                "Verify your internet connection", 
                "Ensure GCP credentials are properly configured",
                "Try with a simpler topic if the issue persists",
                "Check AI model availability and quotas"
            ]
        }
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get current generation statistics for monitoring"""
        return {
            **self.generation_stats,
            "success_rate": (self.generation_stats["successful_generations"] / 
                           max(1, self.generation_stats["total_requests"])) * 100,
            "execution_success_rate": (self.generation_stats["execution_successful"] / 
                                     max(1, self.generation_stats["total_requests"])) * 100
        }
    
    def reset_stats(self):
        """Reset generation statistics"""
        self.generation_stats = {
            "total_requests": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "execution_successful": 0,
            "average_generation_time": 0
        }
        self.logger.info("Generation statistics reset")
