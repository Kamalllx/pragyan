import os
from typing import Dict, Any

class Config:
    """Configuration settings for the learning-enhanced Manim generator"""
    
    # Google Cloud Settings
    GOOGLE_CLOUD_PROJECT = "warp-ai-hackathon"
    GOOGLE_CLOUD_LOCATION = "global"
    STORAGE_BUCKET = "warp-ai-hackathon-manim-codes"
    
    # AI Model Settings
    PRIMARY_MODEL = "gemini-2.5-pro"
    FALLBACK_MODELS = ["gemini-1.5-pro", "gemini-1.5-flash"]
    
    # Generation Settings
    GENERATION_CONFIG = {
        "temperature": 0.2,
        "max_output_tokens": 8192,
        "top_p": 0.85,
    }
    
    # Learning System Settings
    ERROR_LEARNING_DB = "./data/error_learning.db"
    MAX_EXECUTION_ATTEMPTS = 3
    EXECUTION_TIMEOUT = 180  # seconds
    RATE_LIMIT_DELAY = 3.0  # seconds
    
    # Layout Management Settings
    FRAME_WIDTH = 14.22
    FRAME_HEIGHT = 8.0
    MARGIN_X = 1.0
    MARGIN_Y = 0.8
    MIN_OBJECT_SPACING = 1.0
    
    # Quality Thresholds
    MIN_QUALITY_SCORE = 60
    MIN_LAYOUT_SCORE = 70
    SUCCESS_RATE_THRESHOLD = 0.75
    
    # Directories
    DEBUG_DIR = "./debug_output"
    LOGS_DIR = "./logs"
    GENERATED_CODES_DIR = "./generated_codes"
    DATA_DIR = "./data"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        dirs = [cls.DEBUG_DIR, cls.LOGS_DIR, cls.GENERATED_CODES_DIR, cls.DATA_DIR]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_learning_config(cls) -> Dict[str, Any]:
        """Get learning system configuration"""
        return {
            "database_path": cls.ERROR_LEARNING_DB,
            "max_attempts": cls.MAX_EXECUTION_ATTEMPTS,
            "timeout": cls.EXECUTION_TIMEOUT,
            "quality_threshold": cls.MIN_QUALITY_SCORE,
            "success_rate_threshold": cls.SUCCESS_RATE_THRESHOLD
        }
    
    @classmethod
    def get_layout_config(cls) -> Dict[str, Any]:
        """Get layout management configuration"""
        return {
            "frame_width": cls.FRAME_WIDTH,
            "frame_height": cls.FRAME_HEIGHT,
            "margin_x": cls.MARGIN_X,
            "margin_y": cls.MARGIN_Y,
            "min_spacing": cls.MIN_OBJECT_SPACING
        }
