import os
import sys
from datetime import datetime
from vertex_ai_service import VertexAIClient
from utils import setup_logger, validate_manim_code

def main():
    """Enhanced main function with learning system integration and error handling"""
    logger = setup_logger("main")
    
    print("🚀 AI-POWERED MANIM GENERATOR WITH REINFORCEMENT LEARNING")
    print("=" * 70)
    print("Features:")
    print("✅ Error Learning & Prevention")
    print("✅ Layout Management & Anti-Overlap")
    print("✅ Reinforcement Learning from Mistakes")
    print("✅ Quality Improvement Over Time")
    print("=" * 70)
    
    try:
        # Apply quick fixes
        try:
            from error_learning_system_fix import patch_error_learning_system
            patch_error_learning_system()
        except ImportError:
            pass  # Patch not available, continue anyway
        
        # Initialize the enhanced AI client
        print("\n🔧 Initializing Learning-Enhanced AI System...")
        client = VertexAIClient()
        
        # Display learning dashboard with error handling
        try:
            dashboard = client.get_learning_dashboard()
            if not dashboard.get('error'):
                print(f"\n🧠 LEARNING SYSTEM STATUS:")
                system_status = dashboard.get('system_status', {})
                print(f" - Learning Enabled: {'✅' if system_status.get('learning_enabled') else '❌'}")
                print(f" - Layout Management: {'✅' if system_status.get('layout_management') else '❌'}")
                print(f" - Error Prevention: {'✅' if system_status.get('error_prevention_active') else '❌'}")
                
                learning_metrics = dashboard.get('learning_metrics', {})
                print(f" - Learned Patterns: {learning_metrics.get('total_learned_patterns', 0)}")
                print(f" - Success Rate: {learning_metrics.get('average_success_rate', 0):.3f}")
        except Exception as dashboard_error:
            print(f"⚠️ Dashboard error: {dashboard_error}")
            print("Continuing with basic functionality...")
        
        # Get user input
        print("\n📝 Enter your animation requirements:")
        
        # Subject selection
        subjects = ["physics", "mathematics", "chemistry", "biology", "computer science"]
        print(f"\n🎯 Available subjects: {', '.join(subjects)}")
        subject = input("Subject: ").strip().lower()
        if subject not in subjects:
            subject = "mathematics"  # Default
            print(f"Using default subject: {subject}")
        
        # Topic input
        topic = input("Topic (e.g., 'quadratic equations', 'newton's laws'): ").strip()
        if not topic:
            topic = "basic concepts"
            print(f"Using default topic: {topic}")
        
        # Complexity selection
        complexities = ["beginner", "intermediate", "advanced"]
        print(f"\n📊 Complexity levels: {', '.join(complexities)}")
        complexity = input("Complexity level: ").strip().lower()
        if complexity not in complexities:
            complexity = "intermediate"  # Default
            print(f"Using default complexity: {complexity}")
        
        # Specific requirements
        requirements = input("Specific requirements (optional): ").strip()
        if not requirements:
            requirements = "Create an engaging and educational animation with clear explanations"
        
        # Generate with learning enhancements
        try:
            print(f"\n🚀 Starting UNLIMITED AI Error Correction Generation...")
            print(f"⏱️ Maximum time: 15 minutes per generation")
            print(f"🎯 Will continue until perfect code is achieved")
            print(f"🤖 Each error will be intelligently fixed by Vertex AI")
            
            result = client.generate_manim_code(
                subject=subject,
                topic=topic,
                complexity=complexity,
                specific_requirements=requirements
            )
            
            # Enhanced result display
            execution_result = result.get('execution_result', {})
            
            if execution_result.get('success'):
                print(f"\n🎉 PERFECT CODE ACHIEVED!")
                print(f"✅ Video successfully generated: {execution_result.get('video_path')}")
                print(f"📊 Total attempts needed: {execution_result.get('attempts', 0)}")
                print(f"⏱️ Total correction time: {execution_result.get('total_time', 0)/60:.1f} minutes")
                print(f"🤖 AI fixes applied: {len(execution_result.get('ai_fixes_applied', []))}")
            else:
                print(f"\n⚠️ Code generation completed but not perfect:")
                print(f"📊 Total attempts: {execution_result.get('attempts', 0)}")
                print(f"⏱️ Time spent: {execution_result.get('total_time', 0)/60:.1f} minutes")
                if execution_result.get('timeout_reached'):
                    print(f"⏰ Timeout reached (15 minutes)")
                if execution_result.get('final_error'):
                    final_error = execution_result['final_error']
                    print(f"❌ Final error: {final_error.get('type', 'unknown')} - {final_error.get('message', 'Unknown')[:100]}...")
            # Rest of the display code remains the same...
            
            # Code validation
            validation = result.get('validation', {})
            print(f"\n📋 QUALITY ASSESSMENT:")
            print(f" Overall Score: {validation.get('quality_score', 0)}/100")
            print(f" Layout Score: {validation.get('layout_score', 0)}/100")
            print(f" Execution Success: {'✅' if validation.get('execution_successful') else '❌'}")
            print(f" Video Generated: {'✅' if validation.get('video_generated') else '❌'}")
            
            # Learning metrics
            learning_metrics = result.get('learning_metrics', {})
            print(f"\n🧠 LEARNING METRICS:")
            print(f" Prevention Rules Applied: {learning_metrics.get('prevention_rules_applied', 0)}")
            print(f" Layout Fixes Applied: {learning_metrics.get('layout_fixes_applied', 0)}")
            print(f" Quality Trend: {learning_metrics.get('quality_trend', {}).get('trend', 'unknown')}")
            
            # Cloud storage info
            cloud_storage = result.get('cloud_storage', {})
            if cloud_storage:
                print(f"\n☁️ CLOUD STORAGE:")
                print(f" Code URL: {cloud_storage.get('code_url', 'Not available')}")
                if cloud_storage.get('video_url'):
                    print(f" Video URL: {cloud_storage.get('video_url')}")
            
            # Display generated code
            code = result.get('code', '')
            if code:
                print(f"\n📄 GENERATED CODE (Preview):")
                print("-" * 60)
                print(code[:500] + "..." if len(code) > 500 else code)
                print("-" * 60)
            
            # Save local copy
            if code:
                filename = f"{subject}_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
                local_path = f"./generated_codes/{filename}"
                os.makedirs("./generated_codes", exist_ok=True)
                
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                print(f"\n💾 Code saved locally: {local_path}")
            
            print("\n✅ Generation completed successfully!")
            
        except Exception as generation_error:
            print(f"\n❌ Generation system failed: {generation_error}")
            # Show error details
            import traceback
            print("📄 Full error trace:")
            traceback.print_exc()
            
            # Provide helpful error information
            if "string indices must be integers" in str(generation_error):
                print("\n🔧 This appears to be a data structure issue.")
                print("The system is learning from this error and will improve.")
            
        # Ask for another generation
        print(f"\n🔄 Generate another animation? (y/n): ", end="")
        try:
            if input().lower().startswith('y'):
                print("\n" + "="*70)
                main()  # Recursive call for another generation
        except KeyboardInterrupt:
            print("\n\n⚠️ Exiting...")
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Generation interrupted by user.")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Main function failed: {str(e)}")
        print(f"\n❌ System initialization failed: {str(e)}")
        
        # Ask if user wants to try again
        print(f"\n🔄 Try again? (y/n): ", end="")
        try:
            if input().lower().startswith('y'):
                print("\n" + "="*70)
                main()  # Recursive call to try again
            else:
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n⚠️ Exiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()
