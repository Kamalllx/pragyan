import os
import subprocess
import sys

def setup_sarvam_environment():
    """Setup environment for Sarvam AI integration"""
    
    print("🔧 Setting up Sarvam AI Environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        return False
    
    # Install required packages
    required_packages = [
        'requests>=2.31.0',
        'ffmpeg-python>=0.2.0'
    ]
    
    print("📦 Installing required packages...")
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"   ✅ {package}")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")
            return False
    
    # Check for ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found. Please install FFmpeg:")
        print("   Windows: Download from https://ffmpeg.org/download.html")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        return False
    
    # Check environment variables
    if not os.getenv('SARVAM_API_KEY'):
        print("⚠️ SARVAM_API_KEY not set")
        print("Please get your API key from https://sarvam.ai and set:")
        print("export SARVAM_API_KEY='your_api_key_here'")
        return False
    
    print("✅ Sarvam AI environment setup complete!")
    return True

if __name__ == "__main__":
    setup_sarvam_environment()
