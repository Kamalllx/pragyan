import os
import requests
import json
import time
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
from pathlib import Path
import tempfile
import shutil
from utils import setup_logger
from dotenv import load_dotenv
import re
load_dotenv()
class SarvamAIVoiceAgent:
    """
    Advanced Sarvam AI Voice Narration Agent for educational Manim videos.
    Generates synchronized voice narration in multiple Indian languages.
    """
    
    def __init__(self):
        """Initialize the Sarvam AI Voice Agent"""
        self.logger = setup_logger("sarvam_ai_voice_agent")
        
        # Sarvam AI Configuration
        self.sarvam_api_key = os.getenv('SARVAM_API_KEY')
        self.sarvam_base_url = "https://api.sarvam.ai"
        
        # CORRECTED: Character limits and settings based on actual API
        self.max_chars_per_chunk = 450  # Well below 500 limit for safety
        self.default_voice_speed = 1.0
        self.target_loudness = -16.0  # LUFS standard
        
        # CORRECTED: Supported languages with VALID Sarvam AI speakers
        self.supported_languages = {
            'hindi': {'code': 'hi-IN', 'name': 'Hindi (हिंदी)', 'voice': 'meera'},
            'english': {'code': 'en-IN', 'name': 'English (Indian)', 'voice': 'arvind'},  # FIXED
            'bengali': {'code': 'bn-IN', 'name': 'Bengali (বাংলা)', 'voice': 'diya'},    # FIXED
            'gujarati': {'code': 'gu-IN', 'name': 'Gujarati (ગુજરાતી)', 'voice': 'maya'}, # FIXED
            'kannada': {'code': 'kn-IN', 'name': 'Kannada (ಕನ್ನಡ)', 'voice': 'arjun'},    # FIXED
            'malayalam': {'code': 'ml-IN', 'name': 'Malayalam (മലയാളം)', 'voice': 'neel'}, # FIXED
            'marathi': {'code': 'mr-IN', 'name': 'Marathi (मराठी)', 'voice': 'amol'},     # FIXED
            'odia': {'code': 'or-IN', 'name': 'Odia (ଓଡିଆ)', 'voice': 'misha'},         # FIXED
            'punjabi': {'code': 'pa-IN', 'name': 'Punjabi (ਪੰਜਾਬੀ)', 'voice': 'vian'},   # FIXED
            'tamil': {'code': 'ta-IN', 'name': 'Tamil (தமிழ்)', 'voice': 'anushka'},     # FIXED
            'telugu': {'code': 'te-IN', 'name': 'Telugu (తెలుగు)', 'voice': 'vidya'},     # FIXED
            'urdu': {'code': 'ur-IN', 'name': 'Urdu (اردو)', 'voice': 'pavithra'}       # FIXED
        }
        
        # Working directories
        self.temp_dir = "./temp_audio"
        self.output_dir = "./narrated_videos"
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Vertex AI client for script generation
        self.vertex_client = None
        
        self.logger.info("Sarvam AI Voice Agent initialized with CORRECTED speakers and limits")

    def set_vertex_client(self, vertex_client):
        """Set the Vertex AI client for script generation"""
        self.vertex_client = vertex_client
        self.logger.info("Vertex AI client linked for script generation")
    
    def get_user_language_preference(self) -> str:
        """Get user's preferred language for narration"""
        print(f"\n🗣️ VOICE NARRATION LANGUAGE SELECTION")
        print(f"=" * 60)
        print(f"Available languages for educational narration:")
        print()
        
        # Display languages in a nice format
        for i, (lang_key, lang_info) in enumerate(self.supported_languages.items(), 1):
            print(f"{i:2d}. {lang_info['name']}")
        
        print()
        print(f"Choose your preferred language for voice narration:")
        
        while True:
            try:
                choice = input("Enter language number (1-12) or language name: ").strip().lower()
                
                # Handle numeric choice
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(self.supported_languages):
                        selected_lang = list(self.supported_languages.keys())[choice_num - 1]
                        break
                
                # Handle language name
                if choice in self.supported_languages:
                    selected_lang = choice
                    break
                
                # Handle partial matches
                for lang_key in self.supported_languages:
                    if choice in lang_key or choice in self.supported_languages[lang_key]['name'].lower():
                        selected_lang = lang_key
                        break
                else:
                    print("❌ Invalid choice. Please try again.")
                    continue
                break
                
            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid input. Please try again.")
                continue
        
        selected_info = self.supported_languages[selected_lang]
        print(f"\n✅ Selected: {selected_info['name']}")
        print(f"🎤 Voice: {selected_info['voice']}")
        
        return selected_lang
    
    def generate_educational_script(self, video_analysis: Dict, context: Dict, language: str) -> str:
        """Generate educational narration script using Vertex AI"""
        
        print(f"\n📝 Generating educational script in {self.supported_languages[language]['name']}...")
        
        if not self.vertex_client:
            raise Exception("Vertex AI client not set. Call set_vertex_client() first.")
        
        try:
            # Analyze video content for script generation
            subject = context.get('subject', 'mathematics')
            topic = context.get('topic', 'general concept')
            complexity = context.get('complexity', 'beginner')
            video_duration = video_analysis.get('duration', 30)
            
            # Build comprehensive prompt for educational script
            prompt = self._build_script_generation_prompt(
                subject, topic, complexity, language, video_duration, video_analysis
            )
            
            print(f"   🤖 Sending script request to Vertex AI...")
            
            # Generate script using Vertex AI
            self.vertex_client._wait_for_rate_limit()
            
            response = self.vertex_client.client.models.generate_content(
                model=self.vertex_client.model_name,
                contents=prompt,
                config=self.vertex_client.types.GenerateContentConfig(
                    temperature=0.3,  # Slightly creative but educational
                    max_output_tokens=4096,
                    top_p=0.9
                )
            )
            
            if not response or not hasattr(response, 'text') or not response.text:
                raise Exception("No script generated by Vertex AI")
            
            # Extract and clean the script
            script = self._clean_generated_script(response.text)
            
            # If not in English, translate to target language
            if language != 'english':
                print(f"   🌐 Translating script to {self.supported_languages[language]['name']}...")
                script = self._translate_script(script, language)
            
            print(f"   ✅ Educational script generated ({len(script)} characters)")
            
            return script
            
        except Exception as e:
            self.logger.error(f"Script generation failed: {e}")
            # Fallback script
            return self._generate_fallback_script(subject, topic, language)
    
    def _build_script_generation_prompt(self, subject: str, topic: str, complexity: str, 
                                      language: str, duration: float, video_analysis: Dict) -> str:
        """Build comprehensive prompt for educational script generation"""
        
        lang_info = self.supported_languages[language]
        
        # Educational context based on subject
        subject_context = {
            'physics': "Explain physical concepts, laws, formulas, and real-world applications",
            'mathematics': "Break down mathematical concepts, step-by-step solutions, and problem-solving techniques",
            'chemistry': "Describe chemical processes, reactions, molecular structures, and practical applications",
            'biology': "Explain biological processes, systems, functions, and scientific principles",
            'computer science': "Describe algorithms, programming concepts, data structures, and computational thinking"
        }.get(subject.lower(), "Explain the educational concepts clearly and systematically")
        
        # Complexity-specific instructions
        complexity_instructions = {
            'beginner': "Use simple language, basic terminology, and step-by-step explanations suitable for beginners",
            'intermediate': "Include moderate technical terms with explanations, connecting concepts logically",
            'advanced': "Use appropriate technical vocabulary, complex concepts, and detailed analytical explanations"
        }.get(complexity.lower(), "Use appropriate complexity for the target audience")
        
        prompt = f"""You are an expert educational narrator creating voice-over script for a Manim animation about {topic} in {subject}.

NARRATION REQUIREMENTS:
Subject: {subject}
Topic: {topic}
Complexity Level: {complexity}
Target Language: {lang_info['name']}
Video Duration: {duration} seconds
Target Audience: {complexity} level students

EDUCATIONAL OBJECTIVES:
{subject_context}

COMPLEXITY GUIDELINES:
{complexity_instructions}

SCRIPT SPECIFICATIONS:
1. Create educational narration that synchronizes with visual animations
2. Explain concepts as they appear on screen
3. Use clear, engaging, and pedagogical language
4. Include step-by-step explanations for problem-solving
5. Maintain educational flow and logical progression
6. Use appropriate terminology for {complexity} level
7. Keep pace suitable for {duration}-second video
8. Include transitions between concepts
9. End with summary or key takeaways

NARRATION STYLE:
- Professional yet friendly educational tone
- Clear pronunciation guidance for technical terms
- Appropriate pacing for learning comprehension  
- Engaging and motivational language
- Cultural sensitivity for Indian educational context

CONTENT STRUCTURE:
1. Brief introduction to the topic (5-10 seconds)
2. Main educational content with explanations (70-80% of duration)
3. Step-by-step breakdown of key concepts
4. Practical applications or examples
5. Conclusion with key learning points (5-10 seconds)

SPECIFIC REQUIREMENTS FOR {topic.upper()}:
- Explain the fundamental principles clearly
- Break down complex ideas into digestible parts
- Use analogies appropriate for {complexity} level
- Connect to real-world applications
- Provide learning reinforcement

Generate a comprehensive educational narration script in ENGLISH that will be perfectly synchronized with the Manim animation. The script should be engaging, educational, and appropriate for voice synthesis.

EDUCATIONAL NARRATION SCRIPT:"""

        return prompt
    
    def _clean_generated_script(self, raw_script: str) -> str:
        """Clean and format the generated script"""
        try:
            # Remove markdown and formatting
            script = raw_script.strip()
            
            # Remove common prefixes
            prefixes_to_remove = [
                "EDUCATIONAL NARRATION SCRIPT:",
                "Here's the educational script:",
                "Educational Narration:",
                "Script:",
                "Narration:"
            ]
            
            for prefix in prefixes_to_remove:
                if script.startswith(prefix):
                    script = script[len(prefix):].strip()
            
            # Clean up formatting
            script = script.replace("**", "")  # Remove bold markdown
            script = script.replace("*", "")   # Remove italic markdown
            script = script.replace("##", "")  # Remove headers
            script = script.replace("###", "") # Remove subheaders
            
            # Normalize whitespace
            script = " ".join(script.split())
            
            # Add proper punctuation if missing
            if not script.endswith(('.', '!', '?')):
                script += "."
            
            return script
            
        except Exception as e:
            self.logger.error(f"Script cleaning failed: {e}")
            return raw_script
    
    def _translate_script(self, english_script: str, target_language: str) -> str:
        """Translate script to target language using Sarvam AI"""
        try:
            if target_language == 'english':
                return english_script
            
            target_lang_code = self.supported_languages[target_language]['code']
            
            print(f"      🔄 Translating to {target_lang_code}...")
            
            # Use Sarvam AI Translation API
            translation_url = f"{self.sarvam_base_url}/translate"
            
            headers = {
                'api-subscription-key': self.sarvam_api_key,
                'Content-Type': 'application/json'
            }
            
            # Split script into chunks if too long
            chunks = self._split_text_into_chunks(english_script, 1000)  # Smaller chunks for translation
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                payload = {
                    "input": chunk,
                    "source_language_code": "en-IN",
                    "target_language_code": target_lang_code,
                    "speaker_gender": "Male",
                    "mode": "formal",
                    "model": "mayura:v1",
                    "enable_preprocessing": True
                }
                
                response = requests.post(translation_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    translated_text = result.get('translated_text', chunk)
                    translated_chunks.append(translated_text)
                    print(f"         Chunk {i+1}/{len(chunks)} translated")
                else:
                    self.logger.warning(f"Translation failed for chunk {i+1}: {response.text}")
                    translated_chunks.append(chunk)  # Fallback to original
                
                time.sleep(0.5)  # Rate limiting
            
            return " ".join(translated_chunks)
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            return english_script  # Fallback to English
    
    def _generate_fallback_script(self, subject: str, topic: str, language: str) -> str:
        """Generate fallback script when AI generation fails"""
        lang_name = self.supported_languages[language]['name']
        
        fallback_scripts = {
            'physics': f"Welcome to this educational animation about {topic} in physics. We will explore the fundamental concepts and principles step by step. Let's understand how these physical laws work and their applications in real life.",
            'mathematics': f"Today we will learn about {topic} in mathematics. We'll solve problems step by step and understand the underlying concepts. Mathematics helps us solve real-world problems through logical thinking.",
            'chemistry': f"In this chemistry lesson, we'll explore {topic}. We'll see how molecules interact and understand chemical processes. Chemistry explains the building blocks of matter around us.",
            'biology': f"Let's discover {topic} in biology. We'll learn about life processes and how living organisms function. Biology helps us understand the complexity of life on Earth."
        }
        
        base_script = fallback_scripts.get(subject.lower(), f"Welcome to this educational lesson about {topic}. Let's explore this concept together and understand its importance.")
        
        if language != 'english':
            # Try to translate fallback script
            return self._translate_script(base_script, language)
        
        return base_script
    
    def generate_voice_narration(self, script: str, language: str, output_path: str) -> Dict:
        """Generate voice narration using Sarvam AI with chunking"""
        
        print(f"\n🎤 Generating voice narration...")
        print(f"   📝 Script length: {len(script)} characters")
        print(f"   🗣️ Language: {self.supported_languages[language]['name']}")
        
        try:
            # Split script into chunks
            chunks = self._split_script_intelligently(script)
            print(f"   📊 Split into {len(chunks)} chunks")
            
            # Generate audio for each chunk
            audio_files = []
            total_duration = 0
            
            for i, chunk in enumerate(chunks):
                print(f"   🎵 Generating audio chunk {i+1}/{len(chunks)}...")
                
                chunk_result = self._generate_chunk_audio(chunk, language, i)
                
                if chunk_result['success']:
                    audio_files.append({
                        'file_path': chunk_result['file_path'],
                        'duration': chunk_result['duration'],
                        'text': chunk,
                        'chunk_index': i
                    })
                    total_duration += chunk_result['duration']
                    print(f"      ✅ Chunk {i+1} generated ({chunk_result['duration']:.2f}s)")
                else:
                    print(f"      ❌ Chunk {i+1} failed: {chunk_result['error']}")
                    return {'success': False, 'error': f"Chunk {i+1} generation failed"}
            
            # Combine all audio chunks
            print(f"   🔗 Combining {len(audio_files)} audio chunks...")
            combined_result = self._combine_audio_chunks(audio_files, output_path)
            
            if combined_result['success']:
                print(f"   ✅ Voice narration complete!")
                print(f"   ⏱️ Total duration: {total_duration:.2f} seconds")
                print(f"   💾 Saved to: {output_path}")
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'total_duration': total_duration,
                    'chunks_generated': len(audio_files),
                    'language': language,
                    'script_length': len(script)
                }
            else:
                return {'success': False, 'error': combined_result['error']}
                
        except Exception as e:
            self.logger.error(f"Voice generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _split_script_intelligently(self, script: str) -> List[str]:
        """Split script into chunks intelligently at sentence boundaries with 450 char limit"""
        
        # Split by sentences first
        sentences = []
        current_sentence = ""
        
        for char in script:
            current_sentence += char
            if char in '.!?' and len(current_sentence.strip()) > 5:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Group sentences into chunks under 450 character limit
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed limit, start new chunk
            if len(current_chunk) + len(sentence) + 1 > self.max_chars_per_chunk:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Single sentence is too long, split it
                    if len(sentence) > self.max_chars_per_chunk:
                        # Split long sentence at word boundaries
                        words = sentence.split()
                        temp_chunk = ""
                        for word in words:
                            if len(temp_chunk) + len(word) + 1 <= self.max_chars_per_chunk:
                                temp_chunk += " " + word if temp_chunk else word
                            else:
                                if temp_chunk:
                                    chunks.append(temp_chunk.strip())
                                    temp_chunk = word
                                else:
                                    # Single word too long, truncate
                                    chunks.append(word[:self.max_chars_per_chunk])
                                    temp_chunk = ""
                        if temp_chunk:
                            current_chunk = temp_chunk
                    else:
                        current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Final validation - ensure no chunk exceeds limit
        validated_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.max_chars_per_chunk:
                validated_chunks.append(chunk)
            else:
                # Emergency split
                while len(chunk) > self.max_chars_per_chunk:
                    split_point = chunk.rfind(' ', 0, self.max_chars_per_chunk)
                    if split_point == -1:
                        split_point = self.max_chars_per_chunk
                    validated_chunks.append(chunk[:split_point].strip())
                    chunk = chunk[split_point:].strip()
                if chunk:
                    validated_chunks.append(chunk)
        
        return validated_chunks

    def _split_text_into_chunks(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks of maximum length"""
        chunks = []
        
        while len(text) > max_length:
            # Find the last space before max_length
            split_point = text.rfind(' ', 0, max_length)
            if split_point == -1:
                split_point = max_length
            
            chunks.append(text[:split_point].strip())
            text = text[split_point:].strip()
        
        if text:
            chunks.append(text)
        
        return chunks
    
    def _generate_chunk_audio(self, text: str, language: str, chunk_index: int) -> Dict:
        """Generate audio for a single text chunk using Sarvam AI with CORRECTED parameters"""
        
        try:
            lang_info = self.supported_languages[language]
            
            # Ensure text is within limit
            if len(text) > 500:
                # Further split if needed
                text = text[:450] + "..."
                print(f"      ⚠️ Chunk {chunk_index + 1} truncated to {len(text)} characters")
            
            # Sarvam AI TTS endpoint
            tts_url = f"{self.sarvam_base_url}/text-to-speech"
            
            headers = {
                'api-subscription-key': self.sarvam_api_key,
                'Content-Type': 'application/json'
            }
            
            # CORRECTED payload with valid speaker and proper format
            payload = {
                "inputs": [text],  # Array of strings, each max 500 chars
                "target_language_code": lang_info['code'],
                "speaker": lang_info['voice'],  # Now using valid speakers
                "pitch": 0,
                "pace": 1.0,  # Normal speed
                "loudness": 1.0,
                "speech_sample_rate": 22050,
                "enable_preprocessing": True,
                "model": "bulbul:v1"
            }
            
            print(f"      📡 Sending TTS request for chunk {chunk_index + 1}...")
            print(f"         Speaker: {lang_info['voice']}")
            print(f"         Text length: {len(text)} characters")
            print(f"         Language: {lang_info['code']}")
            
            response = requests.post(tts_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Get audio data
                audio_data = result.get('audios', [])
                if not audio_data:
                    return {'success': False, 'error': 'No audio data received'}
                
                # Save audio file
                chunk_filename = f"chunk_{chunk_index:03d}.wav"
                chunk_path = os.path.join(self.temp_dir, chunk_filename)
                
                # Decode base64 audio and save
                import base64
                audio_bytes = base64.b64decode(audio_data[0])
                
                with open(chunk_path, 'wb') as f:
                    f.write(audio_bytes)
                
                print(f"         ✅ Audio chunk saved: {chunk_filename}")
                
                # Get audio duration
                duration = self._get_audio_duration(chunk_path)
                
                # Normalize audio loudness
                normalized_path = self._normalize_audio_loudness(chunk_path)
                
                return {
                    'success': True,
                    'file_path': normalized_path,
                    'duration': duration,
                    'text': text
                }
                
            else:
                error_msg = f"TTS API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                print(f"         ❌ API Error: {response.status_code}")
                print(f"         Response: {response.text[:200]}...")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.logger.error(f"Chunk audio generation failed: {e}")
            return {'success': False, 'error': str(e)}

    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file"""
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
                 '-of', 'csv=p=0', audio_path],
                capture_output=True, text=True, check=True
            )
            return float(result.stdout.strip())
        except:
            # Fallback: estimate based on text length (average speaking rate)
            return len(audio_path) / 15  # Rough estimate: 15 chars per second
    
    def _normalize_audio_loudness(self, audio_path: str) -> str:
        """Normalize audio loudness to target level"""
        try:
            normalized_path = audio_path.replace('.wav', '_normalized.wav')
            
            # Use ffmpeg to normalize loudness
            cmd = [
                'ffmpeg', '-i', audio_path, 
                '-af', f'loudnorm=I={self.target_loudness}:TP=-1.5:LRA=11',
                '-y', normalized_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            # Remove original file
            os.remove(audio_path)
            
            return normalized_path
            
        except Exception as e:
            self.logger.warning(f"Audio normalization failed: {e}")
            return audio_path  # Return original if normalization fails
    
    def _combine_audio_chunks(self, audio_files: List[Dict], output_path: str) -> Dict:
        """Combine multiple audio chunks into single file"""
        
        try:
            if len(audio_files) == 1:
                # Single file, just copy
                shutil.copy2(audio_files[0]['file_path'], output_path)
                return {'success': True, 'output_path': output_path}
            
            # Create file list for ffmpeg
            list_file_path = os.path.join(self.temp_dir, 'file_list.txt')
            
            with open(list_file_path, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{os.path.abspath(audio_file['file_path'])}'\n")
            
            # Combine using ffmpeg
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0', 
                '-i', list_file_path, '-c', 'copy', '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Cleanup temporary files
                for audio_file in audio_files:
                    try:
                        os.remove(audio_file['file_path'])
                    except:
                        pass
                
                try:
                    os.remove(list_file_path)
                except:
                    pass
                
                return {'success': True, 'output_path': output_path}
            else:
                return {'success': False, 'error': f"ffmpeg error: {result.stderr}"}
                
        except Exception as e:
            self.logger.error(f"Audio combination failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def synchronize_video_audio(self, video_path: str, audio_path: str, output_path: str) -> Dict:
        """Synchronize video with audio narration"""
        
        print(f"\n🎬 Synchronizing video with audio narration...")
        
        try:
            # Get durations
            video_duration = self._get_video_duration(video_path)
            audio_duration = self._get_audio_duration(audio_path)
            
            print(f"   📹 Video duration: {video_duration:.2f}s")
            print(f"   🎵 Audio duration: {audio_duration:.2f}s")
            
            # Determine synchronization strategy
            duration_diff = abs(video_duration - audio_duration)
            
            if duration_diff < 0.5:
                # Very close, simple overlay
                print(f"   ✅ Durations match closely, simple overlay")
                return self._simple_audio_overlay(video_path, audio_path, output_path)
            
            elif audio_duration < video_duration:
                # Audio shorter, pad with silence or loop
                print(f"   ⏸️ Audio shorter by {duration_diff:.2f}s, padding")
                return self._pad_audio_to_video(video_path, audio_path, output_path)
            
            else:
                # Audio longer, speed up slightly or trim video
                print(f"   ⏩ Audio longer by {duration_diff:.2f}s, adjusting")
                return self._adjust_for_longer_audio(video_path, audio_path, output_path)
            
        except Exception as e:
            self.logger.error(f"Video-audio synchronization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_video_duration(self, video_path: str) -> float:
        """Get duration of video file"""
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
                 '-of', 'csv=p=0', video_path],
                capture_output=True, text=True, check=True
            )
            return float(result.stdout.strip())
        except Exception as e:
            self.logger.error(f"Failed to get video duration: {e}")
            return 30.0  # Default fallback
    
    def _simple_audio_overlay(self, video_path: str, audio_path: str, output_path: str) -> Dict:
        """Simple audio overlay when durations match"""
        try:
            cmd = [
                'ffmpeg', '-i', video_path, '-i', audio_path,
                '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
                '-shortest', '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {'success': True, 'output_path': output_path, 'method': 'simple_overlay'}
            else:
                return {'success': False, 'error': f"ffmpeg error: {result.stderr}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _pad_audio_to_video(self, video_path: str, audio_path: str, output_path: str) -> Dict:
        """Pad audio with silence to match video duration"""
        try:
            video_duration = self._get_video_duration(video_path)
            
            # Create padded audio
            temp_audio = os.path.join(self.temp_dir, 'padded_audio.wav')
            
            cmd = [
                'ffmpeg', '-i', audio_path,
                '-af', f'apad=pad_dur={video_duration}',
                '-y', temp_audio
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            # Combine with video
            result = self._simple_audio_overlay(video_path, temp_audio, output_path)
            
            # Cleanup
            try:
                os.remove(temp_audio)
            except:
                pass
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _adjust_for_longer_audio(self, video_path: str, audio_path: str, output_path: str) -> Dict:
        """Adjust when audio is longer than video"""
        try:
            video_duration = self._get_video_duration(video_path)
            audio_duration = self._get_audio_duration(audio_path)
            
            # Calculate speed adjustment (max 10% faster)
            speed_factor = min(audio_duration / video_duration, 1.1)
            
            if speed_factor <= 1.1:
                # Speed up video slightly
                temp_video = os.path.join(self.temp_dir, 'adjusted_video.mp4')
                
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', f'setpts=PTS/{speed_factor}',
                    '-y', temp_video
                ]
                
                subprocess.run(cmd, capture_output=True, check=True)
                
                result = self._simple_audio_overlay(temp_video, audio_path, output_path)
                
                # Cleanup
                try:
                    os.remove(temp_video)
                except:
                    pass
                
                return result
            else:
                # Trim audio to video length
                temp_audio = os.path.join(self.temp_dir, 'trimmed_audio.wav')
                
                cmd = [
                    'ffmpeg', '-i', audio_path, '-t', str(video_duration),
                    '-y', temp_audio
                ]
                
                subprocess.run(cmd, capture_output=True, check=True)
                
                result = self._simple_audio_overlay(video_path, temp_audio, output_path)
                
                # Cleanup
                try:
                    os.remove(temp_audio)
                except:
                    pass
                
                return result
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_narrated_video(self, video_path: str, context: Dict, language: str) -> Dict:
        """Complete workflow: Generate script, voice, and create narrated video"""
        
        print(f"\n🎬 CREATING NARRATED EDUCATIONAL VIDEO")
        print(f"=" * 60)
        
        try:
            # Analyze video
            print(f"📊 Analyzing source video...")
            video_analysis = {
                'duration': self._get_video_duration(video_path),
                'path': video_path
            }
            
            # Generate educational script
            script = self.generate_educational_script(video_analysis, context, language)
            
            # Generate voice narration
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"narration_{language}_{timestamp}.wav"
            audio_path = os.path.join(self.temp_dir, audio_filename)
            
            voice_result = self.generate_voice_narration(script, language, audio_path)
            
            if not voice_result['success']:
                return {'success': False, 'error': f"Voice generation failed: {voice_result['error']}"}
            
            # Create output filename
            video_name = Path(video_path).stem
            output_filename = f"{video_name}_narrated_{language}_{timestamp}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Synchronize video with audio
            sync_result = self.synchronize_video_audio(video_path, audio_path, output_path)
            
            if sync_result['success']:
                print(f"\n✅ NARRATED VIDEO CREATED SUCCESSFULLY!")
                print(f"   📹 Output: {output_path}")
                print(f"   🗣️ Language: {self.supported_languages[language]['name']}")
                print(f"   📝 Script length: {len(script)} characters")
                print(f"   ⏱️ Audio duration: {voice_result['total_duration']:.2f}s")
                
                # Save script for reference
                script_path = output_path.replace('.mp4', '_script.txt')
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(f"Educational Script - {self.supported_languages[language]['name']}\n")
                    f.write(f"Generated: {datetime.now()}\n")
                    f.write(f"Subject: {context.get('subject', 'N/A')}\n")
                    f.write(f"Topic: {context.get('topic', 'N/A')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(script)
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'script': script,
                    'script_path': script_path,
                    'language': language,
                    'audio_duration': voice_result['total_duration'],
                    'chunks_generated': voice_result['chunks_generated']
                }
            else:
                return {'success': False, 'error': f"Video synchronization failed: {sync_result['error']}"}
                
        except Exception as e:
            self.logger.error(f"Narrated video creation failed: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            # Cleanup temporary audio files
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass
    def generate_educational_script(self, video_analysis: Dict, context: Dict, language: str) -> str:
        """Generate educational narration script with CLEAN output"""
        
        print(f"\n📝 Generating CLEAN educational script in {self.supported_languages[language]['name']}...")
        
        if not self.vertex_client:
            raise Exception("Vertex AI client not set. Call set_vertex_client() first.")
        
        try:
            subject = context.get('subject', 'mathematics')
            topic = context.get('topic', 'general concept')
            complexity = context.get('complexity', 'beginner')
            video_duration = video_analysis.get('duration', 30)
            
            # Build CLEAN script generation prompt
            prompt = self._build_clean_script_prompt(subject, topic, complexity, language, video_duration)
            
            print(f"   🤖 Sending CLEAN script request to Vertex AI...")
            
            self.vertex_client._wait_for_rate_limit()
            
            response = self.vertex_client.client.models.generate_content(
                model=self.vertex_client.model_name,
                contents=prompt,
                config=self.vertex_client.types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                    top_p=0.9
                )
            )
            
            if not response or not hasattr(response, 'text') or not response.text:
                raise Exception("No script generated by Vertex AI")
            
            # CLEAN the script using our new cleaner
            from script_cleaner import ScriptCleaner
            cleaner = ScriptCleaner()
            
            # Extract only the pure narration content
            clean_script = cleaner.extract_clean_narration(response.text)
            
            if not clean_script or len(clean_script) < 50:
                # Fallback to simple extraction
                clean_script = self._extract_simple_narration(response.text)
            
            # Translate if needed
            if language != 'english':
                print(f"   🌐 Translating to {self.supported_languages[language]['name']}...")
                clean_script = self._translate_script(clean_script, language)
            
            print(f"   ✅ CLEAN educational script generated ({len(clean_script)} characters)")
            print(f"   📝 Preview: {clean_script[:100]}...")
            
            return clean_script
            
        except Exception as e:
            self.logger.error(f"Clean script generation failed: {e}")
            return self._generate_fallback_script(subject, topic, language)

    def _build_clean_script_prompt(self, subject: str, topic: str, complexity: str, 
                                language: str, duration: float) -> str:
        """Build prompt that generates CLEAN narration without formatting"""
        
        lang_info = self.supported_languages[language]
        
        prompt = f"""You are creating a CLEAN educational voice narration script for a {duration}-second Manim animation about {topic} in {subject}.

    CRITICAL REQUIREMENTS:
    1. Generate ONLY pure narration text - NO tables, timestamps, or formatting
    2. Create flowing, natural speech suitable for voice synthesis
    3. Make it educational and engaging for {complexity} level students
    4. Duration should match {duration} seconds when spoken at normal pace
    5. Use simple, clear language appropriate for voice narration

    CONTENT REQUIREMENTS:
    - Start with an engaging hook
    - Explain {topic} concepts clearly and step-by-step
    - Include real-world examples relevant to Indian context
    - End with a summary or key takeaway
    - Use conversational, friendly tone
    - Avoid any stage directions, scene descriptions, or technical notes

    TARGET: {complexity} level students learning {topic} in {subject}
    LANGUAGE: {lang_info['name']}
    DURATION: {duration} seconds (approximately {int(duration * 3.5)} words)

    Generate a CLEAN, flowing educational narration script that starts immediately with educational content:"""

        return prompt

    def _extract_simple_narration(self, raw_text: str) -> str:
        """Simple fallback extraction method"""
        
        # Remove common unwanted patterns
        text = raw_text
        
        # Remove markdown and HTML
        text = re.sub(r'[#*`]', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove table structures
        text = re.sub(r'\|[^|]*\|', '', text)
        text = re.sub(r':---+', '', text)
        
        # Remove timestamps
        text = re.sub(r'\d{2}:\d{2}', '', text)
        
        # Find the main content (usually the longest paragraph)
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
        
        if paragraphs:
            # Return the longest meaningful paragraph
            return max(paragraphs, key=len)
        
        # Last resort
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        return '. '.join(sentences[:5]) + '.' if sentences else "Educational content about the topic."

    def synchronize_video_audio_precisely(self, video_path: str, audio_path: str, output_path: str) -> Dict:
        """PRECISELY synchronize video with audio for perfect timing"""
        
        print(f"\n🎬 PRECISE VIDEO-AUDIO SYNCHRONIZATION")
        
        try:
            # Get exact durations
            video_duration = self._get_video_duration(video_path)
            audio_duration = self._get_audio_duration(audio_path)
            
            print(f"   📹 Video duration: {video_duration:.3f}s")
            print(f"   🎵 Audio duration: {audio_duration:.3f}s")
            print(f"   📊 Difference: {abs(video_duration - audio_duration):.3f}s")
            
            # Strategy based on difference
            duration_diff = abs(video_duration - audio_duration)
            
            if duration_diff < 0.1:  # Very close
                print(f"   ✅ Perfect timing, simple overlay")
                return self._precise_overlay(video_path, audio_path, output_path)
            
            elif duration_diff < 1.0:  # Small difference
                print(f"   🔧 Small difference, micro-adjustments")
                return self._micro_adjust_sync(video_path, audio_path, output_path, video_duration, audio_duration)
            
            elif audio_duration < video_duration:  # Audio shorter
                print(f"   ⏸️ Audio shorter, intelligent padding")
                return self._intelligent_audio_padding(video_path, audio_path, output_path, video_duration)
            
            else:  # Audio longer
                print(f"   ⏩ Audio longer, speed optimization")
                return self._optimize_audio_speed(video_path, audio_path, output_path, video_duration, audio_duration)
            
        except Exception as e:
            self.logger.error(f"Precise synchronization failed: {e}")
            return {'success': False, 'error': str(e)}

    def _micro_adjust_sync(self, video_path: str, audio_path: str, output_path: str, 
                        video_duration: float, audio_duration: float) -> Dict:
        """Make micro-adjustments for perfect sync"""
        
        try:
            temp_audio = os.path.join(self.temp_dir, 'micro_adjusted_audio.wav')
            
            if audio_duration > video_duration:
                # Slightly speed up audio (max 5% faster)
                speed_factor = min(audio_duration / video_duration, 1.05)
                
                cmd = [
                    'ffmpeg', '-i', audio_path,
                    '-af', f'atempo={speed_factor}',
                    '-y', temp_audio
                ]
                
                print(f"      ⏩ Speeding up audio by {((speed_factor-1)*100):.1f}%")
                
            else:
                # Add tiny amount of silence at end
                silence_duration = video_duration - audio_duration
                
                cmd = [
                    'ffmpeg', '-i', audio_path,
                    '-af', f'apad=pad_dur={silence_duration}',
                    '-y', temp_audio
                ]
                
                print(f"      ⏸️ Adding {silence_duration:.3f}s silence")
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            # Now combine
            result = self._precise_overlay(video_path, temp_audio, output_path)
            
            # Cleanup
            try:
                os.remove(temp_audio)
            except:
                pass
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _precise_overlay(self, video_path: str, audio_path: str, output_path: str) -> Dict:
        """Precise overlay with exact synchronization"""
        
        try:
            cmd = [
                'ffmpeg', '-i', video_path, '-i', audio_path,
                '-c:v', 'copy',  # Copy video stream exactly
                '-c:a', 'aac', '-b:a', '128k',  # High quality audio
                '-map', '0:v:0', '-map', '1:a:0',  # Map streams precisely
                '-shortest',  # End when shortest stream ends
                '-avoid_negative_ts', 'make_zero',  # Handle timing issues
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verify the result
                final_duration = self._get_video_duration(output_path)
                print(f"      ✅ Synchronized video duration: {final_duration:.3f}s")
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'method': 'precise_overlay',
                    'final_duration': final_duration
                }
            else:
                return {'success': False, 'error': f"ffmpeg error: {result.stderr}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


def test_sarvam_agent():
    """Test function for the Sarvam AI agent"""
    print("🧪 Testing Sarvam AI Voice Agent...")
    
    # Check environment
    if not os.getenv('SARVAM_API_KEY'):
        print("❌ SARVAM_API_KEY environment variable not set")
        return False
    
    agent = SarvamAIVoiceAgent()
    
    # Test language selection
    print("\n1. Testing language display...")
    for lang_key, lang_info in agent.supported_languages.items():
        print(f"   {lang_key}: {lang_info['name']} ({lang_info['voice']})")
    
    # Test script generation (mock)
    print("\n2. Testing script processing...")
    test_script = "Welcome to this educational video about mathematics. We will learn step by step."
    chunks = agent._split_script_intelligently(test_script)
    print(f"   Script split into {len(chunks)} chunks")
    
    print("\n✅ Basic tests completed!")
    return True

if __name__ == "__main__":
    test_sarvam_agent()
