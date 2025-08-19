import os
import requests
import json
import base64
import tempfile
import time
import logging
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
logger = logging.getLogger(__name__)
load_dotenv()
class VoiceToVideoGenerator:
    """
    Complete Voice to Video Generation using Sarvam STT + Vertex AI + Video Generation
    """
    
    def __init__(self):
        """Initialize voice to video generator"""
        self.sarvam_api_key = os.getenv('SARVAM_API_KEY')
        self.sarvam_base_url = "https://api.sarvam.ai"
        
        # Import your existing services
        try:
            from enhanced_video_generator import EnhancedVideoGenerator
            from vertex_ai_service import VertexAIClient
            self.vertex_client = VertexAIClient()
            self.video_generator = EnhancedVideoGenerator()
            logger.info("✅ Video generation services imported successfully")
        except ImportError as e:
            logger.warning(f"Could not import video generation services: {e}")
            self.vertex_client = None
            self.video_generator = None
        
        # Create debug directory
        self.debug_dir = os.path.join(os.getcwd(), 'audio_debug')
        os.makedirs(self.debug_dir, exist_ok=True)
        
        logger.info("🎤 Voice to Video Generator initialized with audio debugging")
    
    def save_debug_audio(self, audio_data: bytes) -> str:
        """Save audio for debugging purposes"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            debug_file = os.path.join(self.debug_dir, f'debug_audio_{timestamp}.wav')
            
            with open(debug_file, 'wb') as f:
                f.write(audio_data)
            
            print(f"🎵 DEBUG: Audio saved to {debug_file}")
            print(f"🎵 DEBUG: Audio size: {len(audio_data)} bytes")
            
            return debug_file
            
        except Exception as e:
            print(f"❌ Failed to save debug audio: {e}")
            return ""
    
    def speech_to_text(self, audio_data: bytes, language: str = 'auto') -> Dict:
        """Convert speech to text using Sarvam API"""
        try:
            # Save audio for debugging
            debug_file = self.save_debug_audio(audio_data)
            
            print(f"🎤 Converting speech to text (auto-detection enabled)")
            print(f"🎤 Audio debug file: {debug_file}")
            
            # Check if API key exists
            if not self.sarvam_api_key:
                return {
                    'success': False, 
                    'error': 'SARVAM_API_KEY not found in environment variables',
                    'debug_file': debug_file
                }
            
            # Sarvam STT endpoint
            stt_url = f"{self.sarvam_base_url}/speech-to-text"
            
            headers = {
                'api-subscription-key': self.sarvam_api_key
            }
            
            # Prepare audio file for upload
            files = {
                'file': ('audio.wav', audio_data, 'audio/wav')
            }
            
            data = {
                'language_code': 'unknown',  # Auto-detection
                'model': 'saarika:v2.5'
            }
            
            print(f"🌐 Making STT request to: {stt_url}")
            response = requests.post(stt_url, headers=headers, files=files, data=data, timeout=30)
            
            print(f"📡 STT Response status: {response.status_code}")
            print(f"📡 STT Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                transcription = result.get('transcript', '').strip()
                detected_language = result.get('language_code', 'en-IN')
                
                print(f"✅ Speech to text successful")
                print(f"📝 Transcription: '{transcription}'")
                print(f"🔍 Detected language: {detected_language}")
                
                # Check if transcription is empty
                if not transcription:
                    return {
                        'success': False,
                        'error': 'Empty transcription - audio might be unclear or too short',
                        'debug_file': debug_file,
                        'detected_language': detected_language
                    }
                
                return {
                    'success': True,
                    'transcription': transcription,
                    'detected_language': detected_language,
                    'confidence': result.get('confidence', 0.9),
                    'request_id': result.get('request_id', ''),
                    'debug_file': debug_file
                }
            else:
                error_msg = f"STT API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False, 
                    'error': error_msg,
                    'debug_file': debug_file
                }
                
        except Exception as e:
            logger.error(f"Speech to text failed: {e}")
            return {
                'success': False, 
                'error': str(e),
                'debug_file': debug_file if 'debug_file' in locals() else ''
            }
    
    def process_natural_language_query(self, text: str, detected_language: str = 'en-IN') -> Dict:
        """Process natural language with better error handling"""
        try:
            print(f"🧠 Processing natural language query: '{text[:50]}...'")
            
            # Check if text is empty or None
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'Empty text provided for processing'
                }
            
            if not self.vertex_client:
                return self._fallback_query_processing(text, detected_language)
            
            # Enhanced prompt for educational video extraction
            prompt = f"""You are an educational video generation AI. Analyze this natural language request and extract structured parameters for creating an educational video.

User Request: "{text}"
Detected Language: {detected_language}

Extract the following information in JSON format:

{{
    "subject": "physics/mathematics/chemistry/biology/computer_science/general",
    "topic": "specific topic to explain",
    "complexity": "beginner/intermediate/advanced",
    "video_type": "explanation/problem_solving/demonstration/tutorial",
    "key_concepts": ["concept1", "concept2", "concept3"],
    "specific_requirements": "detailed description of what to show",
    "duration_preference": "short/medium/long",
    "visual_style": "simple/detailed/animated/interactive",
    "examples_needed": true,
    "step_by_step": true
}}

Important: ALL fields must be filled with valid values, not null.

Examples:
- "Show me how photosynthesis works" → subject: "biology", topic: "photosynthesis", video_type: "explanation"
- "Solve this calculus problem step by step" → subject: "mathematics", video_type: "problem_solving", step_by_step: true
- "Explain why the sky is blue" → subject: "physics", topic: "light scattering", video_type: "explanation"

Provide ONLY the JSON response:"""

            # Get AI response
            self.vertex_client._wait_for_rate_limit()
            
            response = self.vertex_client.client.models.generate_content(
                model=self.vertex_client.model_name,
                contents=prompt,
                config=self.vertex_client.types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1024,
                    top_p=0.9
                )
            )
            
            if response and hasattr(response, 'text') and response.text:
                # Extract JSON from response
                response_text = response.text.strip()
                print(f"🤖 AI Response: {response_text[:200]}...")
                
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end]
                    parameters = json.loads(json_str)
                    
                    # Validate parameters
                    required_fields = ['subject', 'topic', 'complexity', 'video_type']
                    for field in required_fields:
                        if not parameters.get(field):
                            parameters[field] = self._get_default_value(field, text)
                    
                    print(f"✅ Extracted parameters: {parameters['subject']} - {parameters['topic']}")
                    
                    return {
                        'success': True,
                        'parameters': parameters,
                        'original_query': text
                    }
                else:
                    raise ValueError("No valid JSON found in AI response")
            else:
                raise Exception("No response from Vertex AI")
                
        except Exception as e:
            logger.error(f"Natural language processing failed: {e}")
            return self._fallback_query_processing(text, detected_language)
    
    def _get_default_value(self, field: str, text: str) -> str:
        """Get default value for required fields"""
        defaults = {
            'subject': 'general',
            'topic': text[:50] if text else 'Educational Topic',
            'complexity': 'intermediate',
            'video_type': 'explanation'
        }
        return defaults.get(field, 'unknown')
    
    def _fallback_query_processing(self, text: str, detected_language: str) -> Dict:
        """Improved fallback processing"""
        
        if not text:
            text = "General educational content"
        
        text_lower = text.lower()
        
        # Subject detection
        subject_keywords = {
            'physics': ['physics', 'force', 'motion', 'energy', 'light', 'electricity', 'friction', 'gravity'],
            'mathematics': ['math', 'calculus', 'algebra', 'geometry', 'equation', 'solve', 'calculate'],
            'chemistry': ['chemistry', 'molecule', 'reaction', 'atom', 'chemical', 'compound'],
            'biology': ['biology', 'cell', 'organism', 'photosynthesis', 'genetics', 'evolution']
        }
        
        detected_subject = 'general'
        detected_topic = text.strip()
        
        for subject, keywords in subject_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_subject = subject
                # Extract topic more intelligently
                for keyword in keywords:
                    if keyword in text_lower:
                        detected_topic = keyword
                        break
                break
        
        # Video type detection
        if any(word in text_lower for word in ['solve', 'solution', 'problem']):
            video_type = 'problem_solving'
        elif any(word in text_lower for word in ['show', 'demonstrate', 'how']):
            video_type = 'demonstration'
        elif any(word in text_lower for word in ['explain', 'why', 'what']):
            video_type = 'explanation'
        else:
            video_type = 'tutorial'
        
        return {
            'success': True,
            'parameters': {
                'subject': detected_subject,
                'topic': detected_topic,
                'complexity': 'intermediate',
                'video_type': video_type,
                'key_concepts': [detected_subject, detected_topic],
                'specific_requirements': text,
                'duration_preference': 'medium',
                'visual_style': 'animated',
                'examples_needed': True,
                'step_by_step': 'step' in text_lower
            },
            'original_query': text,
            'processing_method': 'fallback'
        }
    
    def generate_video_from_voice(self, audio_data: bytes, language: str = 'auto') -> Dict:
        """
        COMPLETE METHOD: Speech → Text → AI Processing → Video Generation
        """
        try:
            print(f"🎬 Starting voice to video pipeline...")
            
            # Step 1: Speech to Text
            stt_result = self.speech_to_text(audio_data, language)
            if not stt_result['success']:
                return {
                    'success': False, 
                    'error': f"STT failed: {stt_result['error']}",
                    'debug_file': stt_result.get('debug_file', '')
                }
            
            transcription = stt_result['transcription']
            detected_language = stt_result.get('detected_language', 'en-IN')
            print(f"📝 Transcription: {transcription}")
            print(f"🔍 Detected language: {detected_language}")
            
            # Step 2: Process natural language
            processing_result = self.process_natural_language_query(transcription, detected_language)
            if not processing_result['success']:
                return {
                    'success': False, 
                    'error': f"NLP failed: {processing_result['error']}",
                    'transcription': transcription
                }
            
            parameters = processing_result['parameters']
            print(f"🎯 Extracted parameters: {parameters}")
            
            # Step 3: Generate video
            if not self.video_generator:
                return {
                    'success': False, 
                    'error': 'Video generator not available',
                    'transcription': transcription,
                    'parameters': parameters
                }
            
            video_result = self.video_generator.generate_complete_educational_video(
                subject=parameters['subject'],
                topic=parameters['topic'],
                complexity=parameters['complexity'],
                specific_requirements=parameters['specific_requirements'],
                include_narration=True
            )
            
            if video_result.get('success'):
                return {
                    'success': True,
                    'transcription': transcription,
                    'detected_language': detected_language,
                    'extracted_parameters': parameters,
                    'video_result': video_result,
                    'confidence': stt_result.get('confidence', 0.9),
                    'processing_time': time.time()
                }
            else:
                return {
                    'success': False,
                    'error': f"Video generation failed: {video_result.get('error')}",
                    'transcription': transcription,
                    'parameters': parameters
                }
                
        except Exception as e:
            logger.error(f"Voice to video pipeline failed: {e}")
            return {'success': False, 'error': str(e)}

    def process_text_to_video(self, text: str, language: str = 'english') -> Dict:
        """
        COMPLETE METHOD: Direct text to video without STT
        """
        try:
            print(f"📝 Processing text to video: {text[:50]}...")
            
            # Process natural language
            processing_result = self.process_natural_language_query(text, language)
            if not processing_result['success']:
                return {
                    'success': False, 
                    'error': f"Text processing failed: {processing_result['error']}"
                }
            
            parameters = processing_result['parameters']
            
            # Generate video
            if not self.video_generator:
                return {'success': False, 'error': 'Video generator not available'}
            
            video_result = self.video_generator.generate_complete_educational_video(
                subject=parameters['subject'],
                topic=parameters['topic'],
                complexity=parameters['complexity'],
                specific_requirements=parameters['specific_requirements'],
                include_narration=True
            )
            
            return {
                'success': video_result.get('success', False),
                'extracted_parameters': parameters,
                'video_result': video_result,
                'original_text': text
            }
            
        except Exception as e:
            logger.error(f"Text to video failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_image_with_vertex_ai(self, image_bytes: bytes) -> Dict:
        """Analyze image using Vertex AI Vision"""
        try:
            print(f"🤖 Starting Vertex AI image analysis...")
            
            # Initialize Vertex AI if available
            try:
                from vertexai.preview.generative_models import GenerativeModel, Part
                import vertexai
                
                vertexai.init(project="warp-ai-hackathon", location="us-central1")
                model = GenerativeModel("gemini-1.5-pro-vision")
                
                analysis_prompt = """Analyze this educational image and extract detailed learning information:

Look for:
1. Mathematical equations, formulas, or problems
2. Scientific diagrams, charts, or illustrations  
3. Text content, headings, or educational material
4. Subject matter and topics covered
5. Complexity level and target audience

Extract the following in JSON format:
{
    "topics": ["specific topic 1", "specific topic 2", "specific topic 3"],
    "questions": ["What is the main concept?", "How does this work?", "What are the applications?"],
    "subject": "mathematics/physics/chemistry/biology/computer_science/general",
    "difficulty": "beginner/intermediate/advanced", 
    "text_content": "any visible text or equations",
    "description": "detailed description of educational content",
    "educational_value": "how this can be used for learning",
    "key_concepts": ["concept1", "concept2", "concept3"]
}

Provide ONLY the JSON response:"""

                image_part = Part.from_data(
                    mime_type="image/jpeg",
                    data=image_bytes
                )
                
                response = model.generate_content([analysis_prompt, image_part])
                
                if response and response.text:
                    response_text = response.text.strip()
                    print(f"🤖 Vertex AI Response: {response_text[:200]}...")
                    
                    # Extract JSON from response
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start != -1 and json_end != -1:
                        json_str = response_text[json_start:json_end]
                        analysis = json.loads(json_str)
                        
                        print(f"✅ Vertex AI analysis successful: {analysis.get('subject')} - {analysis.get('topics', [])}")
                        
                        return {"success": True, "analysis": analysis}
                    else:
                        raise ValueError("No valid JSON in Vertex AI response")
                else:
                    raise Exception("No response from Vertex AI Vision")
                    
            except Exception as e:
                print(f"❌ Vertex AI analysis failed: {e}")
                # Return fallback analysis
                return {
                    "success": True,
                    "analysis": {
                        "topics": ["Educational Material", "Visual Learning Content", "Study Resource"],
                        "questions": ["What is the main concept shown?", "How can this be explained?", "What are the key learning points?"],
                        "subject": "general",
                        "difficulty": "intermediate",
                        "description": "Educational content detected in uploaded image",
                        "educational_value": "Suitable for creating explanatory videos",
                        "key_concepts": ["learning", "education", "visual"]
                    }
                }
                
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {"success": False, "error": str(e)}

# Test function
def test_voice_to_video():
    """Test the voice to video functionality"""
    
    print("🧪 Testing Voice to Video Generator...")
    
    # Check if Sarvam API key is available
    if not os.getenv('SARVAM_API_KEY'):
        print("❌ SARVAM_API_KEY not found. Set environment variable.")
        return False
    
    generator = VoiceToVideoGenerator()
    
    # Test text-to-video first (easier to test)
    test_queries = [
        "Show me how photosynthesis works in a plant cell",
        "Animate the solution to quadratic equations step by step", 
        "Create a video explaining why the sky is blue",
        "Demonstrate how neural networks learn"
    ]
    
    for query in test_queries:
        print(f"\n🔄 Testing query: {query}")
        
        result = generator.process_text_to_video(query)
        
        if result['success']:
            params = result['extracted_parameters']
            print(f"✅ Success!")
            print(f"   Subject: {params['subject']}")
            print(f"   Topic: {params['topic']}")
            print(f"   Type: {params['video_type']}")
            print(f"   Complexity: {params['complexity']}")
        else:
            print(f"❌ Failed: {result['error']}")
        
        print("-" * 50)
    
    print("🎯 Voice to Video testing complete!")
    return True

if __name__ == "__main__":
    test_voice_to_video()
