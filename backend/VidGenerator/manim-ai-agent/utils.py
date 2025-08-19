import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
import re
def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Enhanced logger setup with file and console output
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create logs directory
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log"),
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def validate_manim_code(code: str) -> Dict[str, Any]:
    """
    Enhanced Manim code validation with learning context
    """
    validation = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "compatibility_score": 0
    }
    
    # Check basic structure
    if not code or not isinstance(code, str):
        validation["valid"] = False
        validation["errors"].append("Empty or invalid code")
        return validation
    
    # Check for Scene class
    if not re.search(r'class\s+\w+\s*$$\s*Scene\s*$$:', code):
        validation["errors"].append("No Scene class found")
        validation["compatibility_score"] -= 20
    
    # Check for construct method
    if 'def construct(' not in code:
        validation["errors"].append("No construct method found")
        validation["compatibility_score"] -= 15
    
    # Check for proper imports
    if 'from manim import *' not in code and 'import manim' not in code:
        validation["errors"].append("Missing Manim imports")
        validation["compatibility_score"] -= 10
    
    # Check for deprecated methods (learned patterns)
    deprecated_patterns = [
        (r'\.get_sides$$$$', "get_sides() method is deprecated"),
        (r'\.get_part_by_text$$', "get_part_by_text() method is deprecated"),
        (r'\.get_part_by_tex$$', "get_part_by_tex() method is deprecated"),
        (r'Indicate$$[^,]+,\s*color=', "color parameter in Indicate() is not supported"),
        (r'text_alignment=', "Use text_align= instead of text_alignment=")
    ]
    
    for pattern, message in deprecated_patterns:
        if re.search(pattern, code):
            validation["warnings"].append(message)
            validation["compatibility_score"] -= 5
    
    # Check for layout issues
    layout_checks = [
        (r'\.move_to$$[^)]*\d*[^)]*$$', "Position values seem too large for frame"),
        (r'font_size=([5-9]\d|\d{3,})', "Font size might be too large"),
        (r'\.scale$$[5-9]\d*$$', "Scale factor might be too large")
    ]
    
    for pattern, message in layout_checks:
        if re.search(pattern, code):
            validation["warnings"].append(message)
            validation["compatibility_score"] -= 3
    
    # Positive compatibility checks
    positive_patterns = [
        (r'VGroup$$', 5, "Uses VGroup for organization"),
        (r'\.arrange$$', 5, "Uses arrange() for spacing"),
        (r'\.to_edge$$', 3, "Uses frame-relative positioning"),
        (r'self\.wait$$', 3, "Includes wait statements")
    ]
    
    for pattern, score, message in positive_patterns:
        if re.search(pattern, code):
            validation["compatibility_score"] += score
            validation["suggestions"].append(f"✓ {message}")
    
    # Final score calculation
    validation["compatibility_score"] = max(0, min(100, validation["compatibility_score"] + 60))
    
    if validation["errors"]:
        validation["valid"] = False
    
    return validation

def create_safe_filename(text: str) -> str:
    """Create safe filename from text"""
    import re
    # Remove or replace unsafe characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', text)
    safe_name = re.sub(r'\s+', '_', safe_name)
    safe_name = safe_name.strip('_')
    return safe_name[:50]  # Limit length

def ensure_directory_exists(path: str) -> None:
    """Ensure directory exists, create if not"""
    os.makedirs(path, exist_ok=True)

def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging"""
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "timestamp": datetime.now().isoformat()
    }
