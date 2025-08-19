#!/usr/bin/env python3
"""
Enhanced Manim Generator with Reinforcement Learning
Run this script to start the learning-enhanced generation system
"""

import sys
import os
from pathlib import Path
from config import Config

def setup_environment():
    """Setup the environment for the enhanced generator"""
    print("🔧 Setting up enhanced environment...")
    
    # Ensure directories exist
    Config.ensure_directories()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        sys.exit(1)
    
    # Check for required environment variables
    required_env_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",  # For Google Cloud authentication
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set up Google Cloud authentication:")
        print("1. Create a service account in Google Cloud Console")
        print("2. Download the JSON key file")
        print("3. Set GOOGLE_APPLICATION_CREDENTIALS to the path of the JSON file")
    
    print("✅ Environment setup complete")

def main():
    """Main entry point for the enhanced generator"""
    print("🚀 MANIM GENERATOR WITH REINFORCEMENT LEARNING")
    print("=" * 60)
    print("🧠 Features: Error Learning, Layout Management, Quality Improvement")
    print("=" * 60)
    
    try:
        # Setup environment
        setup_environment()
        
        # Import and run the main application
        from main import main as run_main
        run_main()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
