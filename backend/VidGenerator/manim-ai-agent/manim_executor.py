import subprocess
import os
import shutil
import tempfile
from pathlib import Path
from typing import Tuple, Optional, List
import ast
import re
import time
from utils import setup_logger

class ManimExecutor:
    """
    Handles validation and execution of Manim code.
    Provides comprehensive error handling and quality assurance.
    """
    
    def __init__(self, output_dir: str = "./output"):
        """Initialize the Manim executor with output directory setup"""
        self.logger = setup_logger("manim_executor")
        
        # Setup directory structure
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.code_dir = self.output_dir / "generated_code"
        self.video_dir = self.output_dir / "videos"
        self.temp_dir = self.output_dir / "temp"
        self.logs_dir = self.output_dir / "execution_logs"
        
        # Create all directories
        for directory in [self.code_dir, self.video_dir, self.temp_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
        
        # Quality settings
        self.quality_configs = {
            "low": {
                "flag": "-ql",
                "resolution": "480p15",
                "description": "Low quality (480p, 15fps)"
            },
            "medium": {
                "flag": "-qm", 
                "resolution": "720p30",
                "description": "Medium quality (720p, 30fps)"
            },
            "high": {
                "flag": "-qh",
                "resolution": "1080p60", 
                "description": "High quality (1080p, 60fps)"
            },
            "4k": {
                "flag": "-qk",
                "resolution": "2160p60",
                "description": "4K quality (2160p, 60fps)"
            }
        }
        
        self.logger.info("ManimExecutor initialized successfully")
    
    def validate_and_execute(self, 
                           code: str, 
                           filename: str,
                           quality: str = "medium") -> Tuple[bool, str, Optional[str]]:
        """
        Main method to validate Python code and execute Manim animation.
        
        Args:
            code: Python code to validate and execute
            filename: Base filename for saving
            quality: Video quality setting
            
        Returns:
            Tuple of (success, message, video_path)
        """
        
        execution_start = time.time()
        self.logger.info(f"Starting validation and execution for: {filename}")
        
        try:
            # Step 1: Comprehensive code validation
            validation_result = self._comprehensive_validation(code)
            if not validation_result["valid"]:
                error_msg = f"Code validation failed: {validation_result['message']}"
                self.logger.error(error_msg)
                return False, error_msg, None
            
            # Step 2: Extract scene information
            scene_info = self._extract_scene_information(code)
            if not scene_info["scene_name"]:
                error_msg = "No valid Scene class found in generated code"
                self.logger.error(error_msg)
                return False, error_msg, None
            
            # Step 3: Prepare execution environment
            execution_context = self._prepare_execution_context(code, filename, quality)
            
            # Step 4: Execute Manim with monitoring
            success, message, video_path = self._execute_with_monitoring(
                execution_context, scene_info["scene_name"]
            )
            
            execution_time = time.time() - execution_start
            self.logger.info(f"Total execution time: {execution_time:.2f} seconds")
            
            if success:
                # Step 5: Post-execution validation and cleanup
                final_video_path = self._finalize_video_output(
                    video_path, filename, quality, scene_info["scene_name"]
                )
                return True, f"Execution successful in {execution_time:.2f}s", final_video_path
            else:
                return False, message, None
                
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def _comprehensive_validation(self, code: str) -> dict:
        """Perform comprehensive code validation"""
        
        validation_results = {
            "valid": True,
            "message": "Validation successful",
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Syntax validation
            ast.parse(code)
            
            # Import validation
            if not self._check_imports(code):
                validation_results["valid"] = False
                validation_results["message"] = "Missing required Manim imports"
                return validation_results
            
            # Scene class validation
            scene_validation = self._validate_scene_class(code)
            if not scene_validation["valid"]:
                validation_results["valid"] = False
                validation_results["message"] = scene_validation["message"]
                return validation_results
            
            # Content quality checks
            quality_checks = self._perform_quality_checks(code)
            validation_results["warnings"].extend(quality_checks["warnings"])
            validation_results["suggestions"].extend(quality_checks["suggestions"])
            
            # Security validation
            security_check = self._security_validation(code)
            if not security_check["safe"]:
                validation_results["valid"] = False
                validation_results["message"] = f"Security concern: {security_check['message']}"
                return validation_results
            
            self.logger.info("Code validation passed all checks")
            return validation_results
            
        except SyntaxError as e:
            validation_results["valid"] = False
            validation_results["message"] = f"Syntax error: {str(e)}"
            return validation_results
        except Exception as e:
            validation_results["valid"] = False
            validation_results["message"] = f"Validation error: {str(e)}"
            return validation_results
    
    def _check_imports(self, code: str) -> bool:
        """Check for required Manim imports"""
        return ("from manim import *" in code or 
                "import manim" in code or 
                "from manim import" in code)
    
    def _validate_scene_class(self, code: str) -> dict:
        """Validate Scene class structure"""
        try:
            tree = ast.parse(code)
            scene_classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class inherits from Scene
                    for base in node.bases:
                        if ((isinstance(base, ast.Name) and base.id == "Scene") or
                            (isinstance(base, ast.Attribute) and base.attr == "Scene")):
                            scene_classes.append(node.name)
                            
                            # Check for construct method
                            has_construct = any(
                                isinstance(item, ast.FunctionDef) and item.name == "construct"
                                for item in node.body
                            )
                            
                            if not has_construct:
                                return {
                                    "valid": False,
                                    "message": f"Scene class '{node.name}' missing construct method"
                                }
            
            if not scene_classes:
                return {
                    "valid": False,
                    "message": "No Scene class found or Scene inheritance missing"
                }
            
            return {"valid": True, "message": "Scene class validation passed"}
            
        except Exception as e:
            return {"valid": False, "message": f"Scene validation error: {str(e)}"}
    
    def _perform_quality_checks(self, code: str) -> dict:
        """Perform code quality and educational value checks"""
        warnings = []
        suggestions = []
        
        # Check for educational elements
        if "self.wait(" not in code:
            warnings.append("No wait statements found - animation may be too fast")
        
        if "Text(" not in code and "MathTex(" not in code:
            warnings.append("No text or mathematical expressions found")
        
        if "title" not in code.lower():
            suggestions.append("Consider adding a title to the animation")
        
        # Check animation complexity
        play_count = code.count("self.play(")
        if play_count < 2:
            warnings.append("Very few animations - consider adding more visual elements")
        elif play_count > 20:
            warnings.append("Many animations - consider simplifying for clarity")
        
        # Check for comments
        comment_lines = [line for line in code.split('\n') if line.strip().startswith('#')]
        if len(comment_lines) < 3:
            suggestions.append("Consider adding more comments for clarity")
        
        return {"warnings": warnings, "suggestions": suggestions}
    
    def _security_validation(self, code: str) -> dict:
        """Basic security validation to prevent malicious code"""
        dangerous_patterns = [
            r'import\s+os',
            r'import\s+sys',
            r'import\s+subprocess',
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return {
                    "safe": False,
                    "message": f"Potentially unsafe code pattern detected: {pattern}"
                }
        
        return {"safe": True, "message": "Security validation passed"}
    
    def _extract_scene_information(self, code: str) -> dict:
        """Extract comprehensive scene information"""
        try:
            tree = ast.parse(code)
            scene_info = {
                "scene_name": None,
                "scene_classes": [],
                "methods": [],
                "imports": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if ((isinstance(base, ast.Name) and base.id == "Scene") or
                            (isinstance(base, ast.Attribute) and base.attr == "Scene")):
                            scene_info["scene_classes"].append(node.name)
                            if not scene_info["scene_name"]:  # Take first valid scene
                                scene_info["scene_name"] = node.name
                            
                            # Extract methods
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    scene_info["methods"].append(item.name)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        scene_info["imports"].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        scene_info["imports"].append(node.module)
            
            return scene_info
            
        except Exception as e:
            self.logger.error(f"Scene information extraction failed: {str(e)}")
            return {"scene_name": None, "scene_classes": [], "methods": [], "imports": []}
    
    def _prepare_execution_context(self, code: str, filename: str, quality: str) -> dict:
        """Prepare execution context with all necessary files and settings"""
        
        # Create unique execution directory
        execution_id = f"{filename}_{int(time.time())}"
        execution_dir = self.temp_dir / execution_id
        execution_dir.mkdir(exist_ok=True)
        
        # Save code to file
        code_file = execution_dir / f"{filename}.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Create execution context
        context = {
            "execution_dir": execution_dir,
            "code_file": code_file,
            "filename": filename,
            "quality": quality,
            "quality_config": self.quality_configs.get(quality, self.quality_configs["medium"]),
            "log_file": self.logs_dir / f"{filename}_execution.log"
        }
        
        self.logger.info(f"Execution context prepared: {execution_dir}")
        return context
    
    def _execute_with_monitoring(self, context: dict, scene_name: str) -> Tuple[bool, str, Optional[str]]:
        """Execute Manim with comprehensive monitoring and error handling"""
        
        original_dir = os.getcwd()
        
        try:
            # Change to execution directory
            os.chdir(context["execution_dir"])
            
            # Build Manim command
            cmd = [
                "manim",
                context["quality_config"]["flag"],
                context["code_file"].name,
                scene_name
            ]
            
            self.logger.info(f"Executing command: {' '.join(cmd)}")
            
            # Execute with timeout and logging
            with open(context["log_file"], 'w') as log_file:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    cwd=context["execution_dir"]
                )
                
                # Log execution details
                log_file.write(f"Command: {' '.join(cmd)}\n")
                log_file.write(f"Return code: {result.returncode}\n")
                log_file.write(f"STDOUT:\n{result.stdout}\n")
                log_file.write(f"STDERR:\n{result.stderr}\n")
            
            if result.returncode == 0:
                # Success - find generated video
                video_path = self._find_generated_video(
                    context["execution_dir"], 
                    scene_name, 
                    context["quality"]
                )
                
                if video_path:
                    success_msg = f"Manim execution successful ({context['quality_config']['description']})"
                    self.logger.info(success_msg)
                    return True, success_msg, video_path
                else:
                    error_msg = "Video file not found after successful rendering"
                    self.logger.error(error_msg)
                    return False, error_msg, None
            else:
                # Execution failed
                error_msg = f"Manim execution failed (code {result.returncode}): {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg, None
                
        except subprocess.TimeoutExpired:
            error_msg = "Manim execution timed out (exceeded 5 minutes)"
            self.logger.error(error_msg)
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
        finally:
            os.chdir(original_dir)
    
    def _find_generated_video(self, execution_dir: Path, scene_name: str, quality: str) -> Optional[str]:
        """Find the generated video file in the media directory"""
        
        media_dir = execution_dir / "media" / "videos"
        
        if not media_dir.exists():
            self.logger.error("Media directory not created")
            return None
        
        # Search for video file recursively
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                if (file.startswith(scene_name) and 
                    file.endswith('.mp4') and
                    self.quality_configs[quality]["resolution"] in root):
                    video_path = os.path.join(root, file)
                    self.logger.info(f"Found generated video: {video_path}")
                    return video_path
        
        # Fallback: search for any mp4 file with scene name
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                if file.startswith(scene_name) and file.endswith('.mp4'):
                    video_path = os.path.join(root, file)
                    self.logger.warning(f"Found video with different quality: {video_path}")
                    return video_path
        
        self.logger.error("No video file found")
        return None
    
    def _finalize_video_output(self, source_path: str, filename: str, quality: str, scene_name: str) -> str:
        """Move video to final output directory with proper naming"""
        
        timestamp = int(time.time())
        final_filename = f"{filename}_{scene_name}_{quality}_{timestamp}.mp4"
        final_path = self.video_dir / final_filename
        
        try:
            shutil.copy2(source_path, final_path)
            self.logger.info(f"Video finalized: {final_path}")
            
            # Save metadata
            metadata_file = final_path.with_suffix('.json')
            metadata = {
                "filename": filename,
                "scene_name": scene_name,
                "quality": quality,
                "timestamp": timestamp,
                "source_path": source_path,
                "final_path": str(final_path)
            }
            
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return str(final_path)
            
        except Exception as e:
            self.logger.error(f"Failed to finalize video: {str(e)}")
            return source_path  # Return original path if copy fails
    
    def cleanup_temp_files(self, keep_recent: int = 5):
        """Clean up temporary execution files, keeping only recent ones"""
        
        try:
            temp_dirs = sorted(
                [d for d in self.temp_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Keep only recent directories
            for old_dir in temp_dirs[keep_recent:]:
                shutil.rmtree(old_dir)
                self.logger.info(f"Cleaned up temp directory: {old_dir}")
                
        except Exception as e:
            self.logger.warning(f"Cleanup failed: {str(e)}")
    
    def get_execution_stats(self) -> dict:
        """Get execution statistics and health metrics"""
        
        return {
            "output_directory": str(self.output_dir),
            "total_videos": len(list(self.video_dir.glob("*.mp4"))),
            "total_code_files": len(list(self.code_dir.glob("*.py"))),
            "temp_directories": len(list(self.temp_dir.iterdir())),
            "log_files": len(list(self.logs_dir.glob("*.log"))),
            "quality_configs": self.quality_configs
        }
