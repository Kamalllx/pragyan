import os
import json
import time
import base64
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class NaturalLanguageProcessor:
    """
    Clean, focused natural language to video processor that integrates with existing services
    """
    
    def __init__(self, vertex_client, sarvam_agent, video_generator):
        """Initialize with existing services"""
        self.logger = logging.getLogger("natural_language_processor")
        
        # Use existing services
        self.vertex_client = vertex_client
        self.sarvam_agent = sarvam_agent
        self.video_generator = video_generator
        
        # Configuration
        self.supported_languages = {
            'english': {'code': 'en-IN', 'name': 'English', 'sarvam_voice': 'arvind'},
            'hindi': {'code': 'hi-IN', 'name': 'हिंदी', 'sarvam_voice': 'meera'},
            'tamil': {'code': 'ta-IN', 'name': 'தமிழ்', 'sarvam_voice': 'anushka'},
            'bengali': {'code': 'bn-IN', 'name': 'বাংলা', 'sarvam_voice': 'diya'},
            'gujarati': {'code': 'gu-IN', 'name': 'ગુજરાતી', 'sarvam_voice': 'maya'},
            'kannada': {'code': 'kn-IN', 'name': 'ಕನ್ನಡ', 'sarvam_voice': 'arjun'},
            'malayalam': {'code': 'ml-IN', 'name': 'മലയാളം', 'sarvam_voice': 'neel'},
            'marathi': {'code': 'mr-IN', 'name': 'मराठी', 'sarvam_voice': 'amol'},
            'odia': {'code': 'or-IN', 'name': 'ଓଡିଆ', 'sarvam_voice': 'misha'},
            'punjabi': {'code': 'pa-IN', 'name': 'ਪੰਜਾਬੀ', 'sarvam_voice': 'vian'},
            'telugu': {'code': 'te-IN', 'name': 'తెలుగు', 'sarvam_voice': 'vidya'},
            'urdu': {'code': 'ur-IN', 'name': 'اردو', 'sarvam_voice': 'pavithra'}
        }
        
        # Debug directory
        self.debug_dir = os.path.join(os.getcwd(), 'nlp_debug')
        os.makedirs(self.debug_dir, exist_ok=True)
        
        self.logger.info("✅ Natural Language Processor initialized")
    
    def process_voice_to_video(self, audio_data: bytes, language: str = "auto") -> Dict:
        """
        Complete pipeline: Voice -> Text -> Understanding -> Video Generation
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.logger.info(f"🎤 Starting voice-to-video pipeline at {timestamp}")
            
            # Step 1: Save debug audio
            debug_audio_path = self._save_debug_audio(audio_data, timestamp)
            
            # Step 2: Speech to Text using Sarvam
            stt_result = self._speech_to_text_sarvam(audio_data, language)
            if not stt_result['success']:
                return self._format_error_response("STT Failed", stt_result['error'], debug_audio_path)
            
            transcription = stt_result['transcription']
            detected_language = stt_result.get('detected_language', 'english')
            
            self.logger.info(f"📝 Transcription: '{transcription}'")
            self.logger.info(f"🔍 Detected language: {detected_language}")
            
            # Step 3: Natural Language Understanding
            understanding_result = self._understand_educational_intent(transcription, detected_language)
            if not understanding_result['success']:
                return self._format_error_response("Understanding Failed", understanding_result['error'], debug_audio_path)
            
            # Step 4: Generate Video
            video_params = understanding_result['parameters']
            video_result = self._generate_video_from_params(video_params, detected_language)
            
            if video_result['success']:
                return {
                    'success': True,
                    'transcription': transcription,
                    'detected_language': detected_language,
                    'understood_parameters': video_params,
                    'video_result': video_result,
                    'debug_audio_path': debug_audio_path,
                    'pipeline_timestamp': timestamp
                }
            else:
                return self._format_error_response("Video Generation Failed", video_result['error'], debug_audio_path)
                
        except Exception as e:
            self.logger.error(f"❌ Voice-to-video pipeline failed: {e}")
            return self._format_error_response("Pipeline Exception", str(e))
    
    def process_text_to_video(self, text: str, language: str = "auto") -> Dict:
        """
        Complete pipeline: Text -> Understanding -> Video Generation
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.logger.info(f"📝 Starting text-to-video pipeline at {timestamp}")
            
            # Step 1: Language Detection (if auto)
            if language == "auto":
                detected_language = self._detect_language_from_text(text)
            else:
                detected_language = language
            
            self.logger.info(f"📝 Input text: '{text}...'")
            self.logger.info(f"🔍 Using language: {detected_language}")
            
            # Step 2: Natural Language Understanding
            understanding_result = self._understand_educational_intent(text, detected_language)
            if not understanding_result['success']:
                return self._format_error_response("Understanding Failed", understanding_result['error'])
            
            # Step 3: Generate Video
            video_params = understanding_result['parameters']
            video_result = self._generate_video_from_params(video_params, detected_language)
            
            if video_result['success']:
                return {
                    'success': True,
                    'input_text': text,
                    'detected_language': detected_language,
                    'understood_parameters': video_params,
                    'video_result': video_result,
                    'pipeline_timestamp': timestamp
                }
            else:
                return self._format_error_response("Video Generation Failed", video_result['error'])
                
        except Exception as e:
            self.logger.error(f"❌ Text-to-video pipeline failed: {e}")
            return self._format_error_response("Pipeline Exception", str(e))
    
    def _save_debug_audio(self, audio_data: bytes, timestamp: str) -> str:
        """Save audio for debugging"""
        try:
            debug_path = os.path.join(self.debug_dir, f"voice_input_{timestamp}.wav")
            with open(debug_path, 'wb') as f:
                f.write(audio_data)
            self.logger.info(f"🎵 Debug audio saved: {debug_path}")
            return debug_path
        except Exception as e:
            self.logger.warning(f"Failed to save debug audio: {e}")
            return ""
    
    def _speech_to_text_sarvam(self, audio_data: bytes, language: str) -> Dict:
        """
        Convert speech to text using Sarvam API with proper error handling
        """
        try:
            import requests
            
            # Sarvam API configuration
            sarvam_api_key = os.getenv('SARVAM_API_KEY')
            if not sarvam_api_key:
                return {'success': False, 'error': 'SARVAM_API_KEY not found in environment'}
            
            # Use auto-detection for language
            headers = {
                'api-subscription-key': sarvam_api_key
            }
            
            files = {
                'file': ('audio.wav', audio_data, 'audio/wav')
            }
            
            data = {
                'language_code': 'unknown',  # Auto-detect
                'model': 'saarika:v2.5'
            }
            
            self.logger.info(f"🌐 Calling Sarvam STT API...")
            response = requests.post(
                'https://api.sarvam.ai/speech-to-text',
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            self.logger.info(f"📡 STT Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                transcription = result.get('transcript', '').strip()
                detected_lang_code = result.get('language_code', 'en-IN')
                
                # Map language code to our format
                detected_language = self._map_language_code(detected_lang_code)
                
                if not transcription:
                    return {'success': False, 'error': 'Empty transcription received'}
                
                return {
                    'success': True,
                    'transcription': transcription,
                    'detected_language': detected_language,
                    'confidence': result.get('confidence', 0.9)
                }
            else:
                error_msg = f"Sarvam API error: {response.status_code} - {response.text}"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            return {'success': False, 'error': f"STT exception: {str(e)}"}
    
    def _map_language_code(self, lang_code: str) -> str:
        """Map Sarvam language codes to our internal format"""
        code_mapping = {
            'en-IN': 'english',
            'hi-IN': 'hindi',
            'ta-IN': 'tamil',
            'bn-IN': 'bengali',
            'gu-IN': 'gujarati',
            'kn-IN': 'kannada',
            'ml-IN': 'malayalam',
            'mr-IN': 'marathi',
            'or-IN': 'odia',
            'pa-IN': 'punjabi',
            'te-IN': 'telugu',
            'ur-IN': 'urdu'
        }
        return code_mapping.get(lang_code, 'english')
    
    def _detect_language_from_text(self, text: str) -> str:
        """Simple language detection from text"""
        # Basic keyword-based detection
        text_lower = text.lower()
        
        # Check for language keywords
        if any(word in text_lower for word in ['hindi', 'हिंदी', 'मैं', 'है', 'का', 'में']):
            return 'hindi'
        elif any(word in text_lower for word in ['tamil', 'தமிழ்', 'என்', 'அது', 'இது']):
            return 'tamil'
        elif any(word in text_lower for word in ['bengali', 'বাংলা', 'আমি', 'এটি', 'যা']):
            return 'bengali'
        # Add more language detection logic...
        
        return 'english'  # Default
    
    def _understand_educational_intent(self, text: str, language: str) -> Dict:
        """
        Use Vertex AI to understand educational intent and extract parameters
        """
        try:
            self.logger.info(f"🧠 Understanding educational intent for: '{text[:50]}...'")
            
            # Build prompt for educational understanding
            prompt = f"""Analyze this educational request and extract structured parameters:

User Input: "{text}"
Language: {language}

Extract the following information in JSON format:
{{
    "subject": "physics/mathematics/chemistry/biology/computer_science/general",
    "topic": "specific topic to explain",
    "complexity": "beginner/intermediate/advanced",
    "intent": "explanation/demonstration/problem_solving/tutorial",
    "key_concepts": ["concept1", "concept2"],
    "specific_requirements": "what the user wants to see",
    "video_style": "animated/interactive/step_by_step",
    "estimated_duration": "short/medium/long"
}}

Examples:
- "Explain photosynthesis" → subject: biology, topic: photosynthesis, intent: explanation
- "Show me quadratic equations" → subject: mathematics, topic: quadratic equations, intent: demonstration
- "How does gravity work" → subject: physics, topic: gravity, intent: explanation

Return ONLY valid JSON with all fields filled:"""

            # Call Vertex AI
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
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end]
                    parameters = json.loads(json_str)
                    
                    # Validate and fill missing fields
                    parameters = self._validate_and_fill_parameters(parameters, text)
                    
                    self.logger.info(f"✅ Understood intent: {parameters['subject']} - {parameters['topic']}")
                    
                    return {
                        'success': True,
                        'parameters': parameters,
                        'original_text': text
                    }
                else:
                    raise ValueError("No valid JSON found in AI response")
            else:
                raise Exception("No response from Vertex AI")
                
        except Exception as e:
            self.logger.error(f"Educational intent understanding failed: {e}")
            # Return fallback parameters
            return {
                'success': True,
                'parameters': self._create_fallback_parameters(text, language),
                'original_text': text,
                'fallback_used': True
            }
    
    def _validate_and_fill_parameters(self, params: Dict, original_text: str) -> Dict:
        """Validate and fill missing parameters"""
        # Required fields with defaults
        defaults = {
            'subject': 'general',
            'topic': original_text if original_text else 'educational topic',
            'complexity': 'intermediate',
            'intent': 'explanation',
            'key_concepts': ['learning', 'education'],
            'specific_requirements': original_text,
            'video_style': 'animated',
            'estimated_duration': 'medium'
        }
        
        # Fill missing fields
        for key, default_value in defaults.items():
            if not params.get(key):
                params[key] = default_value
        
        return params
    
    def _create_fallback_parameters(self, text: str, language: str) -> Dict:
        """Create fallback parameters when AI understanding fails"""
        # Simple keyword-based subject detection
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['math', 'equation', 'calculate', 'solve', 'algebra']):
            subject = 'mathematics'
        elif any(word in text_lower for word in ['physics', 'force', 'energy', 'motion', 'gravity']):
            subject = 'physics'
        elif any(word in text_lower for word in ['chemistry', 'reaction', 'molecule', 'atom']):
            subject = 'chemistry'
        elif any(word in text_lower for word in ['biology', 'cell', 'organism', 'photosynthesis']):
            subject = 'biology'
        else:
            subject = 'general'
        
        return {
            'subject': subject,
            'topic': text if text else 'educational content',
            'complexity': 'intermediate',
            'intent': 'explanation',
            'key_concepts': [subject, 'learning'],
            'specific_requirements': text,
            'video_style': 'animated',
            'estimated_duration': 'medium'
        }
    
    def _generate_video_from_params(self, params: Dict, language: str) -> Dict:
        """
        Generate video using existing video generator with enhanced parameters
        """
        try:
            self.logger.info(f"🎬 Generating video with parameters: {params}")
            
            # Use your existing enhanced video generator
            result = self.video_generator.generate_complete_educational_video(
                subject=params['subject'],
                topic=params['topic'],
                complexity=params['complexity'],
                specific_requirements=params['specific_requirements'],
                include_narration=True  # Always include narration for voice requests
            )
            
            if result.get('success'):
                # Override language for narration if needed
                if language != 'english' and result.get('narration_result'):
                    self.logger.info(f"🗣️ Regenerating narration in {language}")
                    # You can add language-specific narration regeneration here
                
                return {
                    'success': True,
                    'video_generation_result': result,
                    'final_video_path': result.get('final_video_path'),
                    'cloud_urls': result.get('cloud_upload', {}),
                    'quality_score': result.get('video_generation', {}).get('validation', {}).get('quality_score', 0)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video generation failed'),
                    'details': result
                }
                
        except Exception as e:
            self.logger.error(f"Video generation from parameters failed: {e}")
            return {
                'success': False,
                'error': f"Video generation exception: {str(e)}"
            }
    
    def _format_error_response(self, error_type: str, error_message: str, debug_path: str = "") -> Dict:
        """Format consistent error response"""
        return {
            'success': False,
            'error_type': error_type,
            'error_message': error_message,
            'debug_audio_path': debug_path,
            'timestamp': datetime.now().isoformat(),
            'suggestions': self._get_error_suggestions(error_type)
        }
    
    def _get_error_suggestions(self, error_type: str) -> List[str]:
        """Get helpful suggestions based on error type"""
        suggestions = {
            'STT Failed': [
                'Check if audio is clear and audible',
                'Verify SARVAM_API_KEY is set correctly',
                'Try speaking more clearly',
                'Check internet connection'
            ],
            'Understanding Failed': [
                'Try rephrasing your request',
                'Be more specific about the topic',
                'Use simpler language',
                'Check if the topic is educational'
            ],
            'Video Generation Failed': [
                'Simplify the topic request',
                'Check if all services are running',
                'Try a different complexity level',
                'Verify cloud storage access'
            ]
        }
        return suggestions.get(error_type, ['Please try again or contact support'])
