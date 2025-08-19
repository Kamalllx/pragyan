from vertex_ai_service import VertexAIClient
from sarvam_ai_agent import SarvamAIVoiceAgent
from google.cloud import storage
import os
from datetime import datetime
from utils import setup_logger
from typing import Dict, Optional
import json
class EnhancedVideoGenerator:
    """
    Enhanced video generator that combines Manim generation with Sarvam AI voice narration
    """
    
    def __init__(self):
        """Initialize the enhanced video generator"""
        self.logger = setup_logger("enhanced_video_generator")
        
        # Initialize clients
        self.vertex_client = VertexAIClient()
        self.voice_agent = SarvamAIVoiceAgent()
        
        # Link vertex client to voice agent
        self.voice_agent.set_vertex_client(self.vertex_client)
        
        # Cloud storage
        self.storage_client = storage.Client(project="warp-ai-hackathon")
        self.bucket_name = "warp-ai-hackathon-manim-codes"
        
        self.logger.info("Enhanced Video Generator initialized")
    
    def generate_complete_educational_video(self, subject: str, topic: str, complexity: str, 
                                          specific_requirements: str, include_narration: bool = True) -> Dict:
        """
        Generate complete educational video with optional voice narration
        """
        
        print(f"\n🚀 ENHANCED EDUCATIONAL VIDEO GENERATION")
        print(f"=" * 70)
        print(f"📚 Subject: {subject}")
        print(f"🎯 Topic: {topic}")
        print(f"📊 Complexity: {complexity}")
        print(f"🎤 Narration: {'Enabled' if include_narration else 'Disabled'}")
        
        context = {
            'subject': subject,
            'topic': topic,
            'complexity': complexity,
            'requirements': specific_requirements
        }
        
        try:
            # Step 1: Generate Manim video
            print(f"\n📹 Step 1: Generating Manim Animation")
            video_result = self.vertex_client.generate_manim_code(
                subject=subject,
                topic=topic, 
                complexity=complexity,
                specific_requirements=specific_requirements
            )
            
            if not video_result.get('execution_result', {}).get('success'):
                return {
                    'success': False,
                    'error': 'Manim video generation failed',
                    'details': video_result
                }
            
            video_path = video_result['execution_result']['video_path']
            print(f"   ✅ Manim video generated: {video_path}")
            
            # Step 2: Voice narration (if requested)
            if include_narration:
                print(f"\n🗣️ Step 2: Adding Voice Narration")
                
                # Get language preference
                language = self.voice_agent.get_user_language_preference()
                
                # Create narrated version
                narration_result = self.voice_agent.create_narrated_video(
                    video_path, context, language
                )
                
                if narration_result['success']:
                    final_video_path = narration_result['output_path']
                    print(f"   ✅ Narrated video created: {final_video_path}")
                else:
                    print(f"   ⚠️ Narration failed, using original video: {narration_result['error']}")
                    final_video_path = video_path
                    narration_result = None
            else:
                final_video_path = video_path
                narration_result = None
                language = 'none'
            
            # Step 3: Upload to cloud storage
            print(f"\n☁️ Step 3: Uploading to Cloud Storage")
            upload_result = self._upload_final_video(
                final_video_path, context, language, 
                video_result, narration_result
            )
            
            # Prepare final result
            result = {
                'success': True,
                'video_generation': video_result,
                'narration_result': narration_result,
                'final_video_path': final_video_path,
                'cloud_upload': upload_result,
                'language': language,
                'context': context
            }
            
            # Display final results
            self._display_final_results(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced video generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _upload_final_video(self, video_path: str, context: Dict, language: str,
                           video_result: Dict, narration_result: Optional[Dict]) -> Dict:
        """Upload final video and related files to cloud storage"""
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create descriptive filename
            subject = context['subject']
            topic = context['topic'].replace(' ', '_')
            lang_suffix = f"_{language}" if language != 'none' else ""
            
            base_name = f"{subject}_{topic}{lang_suffix}_{timestamp}"
            
            # Upload video
            video_blob_name = f"enhanced_videos/{base_name}.mp4"
            video_blob = bucket.blob(video_blob_name)
            
            print(f"   📤 Uploading video: {video_blob_name}")
            
            with open(video_path, 'rb') as video_file:
                video_blob.upload_from_file(video_file, content_type='video/mp4')
            
            video_blob.make_public()
            video_url = f"https://storage.googleapis.com/{self.bucket_name}/{video_blob_name}"
            
            upload_result = {
                'video_blob_name': video_blob_name,
                'video_url': video_url,
                'bucket': self.bucket_name
            }
            
            # Upload script if narration was used
            if narration_result and narration_result.get('script_path'):
                script_blob_name = f"scripts/{base_name}_script.txt"
                script_blob = bucket.blob(script_blob_name)
                
                print(f"   📝 Uploading script: {script_blob_name}")
                
                with open(narration_result['script_path'], 'r', encoding='utf-8') as script_file:
                    script_blob.upload_from_string(script_file.read(), content_type='text/plain')
                
                script_blob.make_public()
                script_url = f"https://storage.googleapis.com/{self.bucket_name}/{script_blob_name}"
                
                upload_result.update({
                    'script_blob_name': script_blob_name,
                    'script_url': script_url
                })
            
            # Upload metadata
            metadata = {
                'generated_at': datetime.now().isoformat(),
                'subject': context['subject'],
                'topic': context['topic'],
                'complexity': context['complexity'],
                'language': language,
                'has_narration': narration_result is not None,
                'video_generation_quality': video_result.get('validation', {}).get('quality_score', 0),
                'learning_metrics': video_result.get('learning_metrics', {})
            }
            
            metadata_blob_name = f"metadata/{base_name}_metadata.json"
            metadata_blob = bucket.blob(metadata_blob_name)
            metadata_blob.upload_from_string(
                json.dumps(metadata, indent=2), 
                content_type='application/json'
            )
            
            print(f"   📊 Metadata uploaded: {metadata_blob_name}")
            
            upload_result['metadata_blob_name'] = metadata_blob_name
            
            return upload_result
            
        except Exception as e:
            self.logger.error(f"Cloud upload failed: {e}")
            return {'error': str(e)}
    
    def _display_final_results(self, result: Dict):
        """Display comprehensive final results"""
        
        print(f"\n" + "="*80)
        print(f"🎉 ENHANCED EDUCATIONAL VIDEO GENERATION COMPLETE!")
        print(f"="*80)
        
        # Video generation results
        video_gen = result.get('video_generation', {})
        validation = video_gen.get('validation', {})
        
        print(f"\n📹 VIDEO GENERATION:")
        print(f" Quality Score: {validation.get('quality_score', 0)}/100")
        print(f" Execution Success: {'✅' if validation.get('execution_successful') else '❌'}")
        print(f" Learning Enhanced: {'✅' if validation.get('learning_enhanced') else '❌'}")
        
        # Narration results
        narration = result.get('narration_result')
        if narration:
            print(f"\n🎤 VOICE NARRATION:")
            print(f" Language: {result['language']}")
            print(f" Success: {'✅' if narration['success'] else '❌'}")
            if narration['success']:
                print(f" Audio Duration: {narration['audio_duration']:.2f}s")
                print(f" Chunks Generated: {narration['chunks_generated']}")
        
        # Cloud storage
        cloud = result.get('cloud_upload', {})
        if cloud and not cloud.get('error'):
            print(f"\n☁️ CLOUD STORAGE:")
            print(f" Video URL: {cloud.get('video_url', 'Not available')}")
            if cloud.get('script_url'):
                print(f" Script URL: {cloud['script_url']}")
        
        # Local files
        print(f"\n💾 LOCAL FILES:")
        print(f" Final Video: {result['final_video_path']}")
        if narration and narration.get('script_path'):
            print(f" Script File: {narration['script_path']}")
        
        print(f"\n✅ All components completed successfully!")
        print(f"="*80)


def main():
    """Main function for enhanced video generation"""
    
    print("🚀 ENHANCED EDUCATIONAL VIDEO GENERATOR")
    print("🎬 Manim Animation + 🗣️ Sarvam AI Voice Narration")
    print("=" * 60)
    
    # Check environment variables
    required_env_vars = ['SARVAM_API_KEY', 'GOOGLE_APPLICATION_CREDENTIALS']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set up:")
        print("- SARVAM_API_KEY: Your Sarvam AI API key")
        print("- GOOGLE_APPLICATION_CREDENTIALS: Path to Google Cloud service account JSON")
        return
    
    try:
        generator = EnhancedVideoGenerator()
        
        # Get user input
        print(f"\n📝 Enter your requirements:")
        
        subjects = ["physics", "mathematics", "chemistry", "biology", "computer science"]
        print(f"\n🎯 Available subjects: {', '.join(subjects)}")
        subject = input("Subject: ").strip().lower()
        if subject not in subjects:
            subject = "mathematics"
        
        topic = input("Topic: ").strip()
        if not topic:
            topic = "basic concepts"
        
        complexities = ["beginner", "intermediate", "advanced"]
        print(f"\n📊 Complexity levels: {', '.join(complexities)}")
        complexity = input("Complexity level: ").strip().lower()
        if complexity not in complexities:
            complexity = "intermediate"
        
        requirements = input("Specific requirements (optional): ").strip()
        if not requirements:
            requirements = "Create engaging educational content with clear explanations"
        
        # Ask about narration
        narration_choice = input("\nAdd voice narration? (y/n): ").strip().lower()
        include_narration = narration_choice.startswith('y')
        
        # Generate complete video
        result = generator.generate_complete_educational_video(
            subject=subject,
            topic=topic,
            complexity=complexity,
            specific_requirements=requirements,
            include_narration=include_narration
        )
        
        if result['success']:
            print(f"\n🎉 Complete educational video generated successfully!")
        else:
            print(f"\n❌ Generation failed: {result.get('error', 'Unknown error')}")
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Generation interrupted by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")

if __name__ == "__main__":
    main()
