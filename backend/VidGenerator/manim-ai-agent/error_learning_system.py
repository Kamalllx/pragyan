import json
import os
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import re
from utils import setup_logger

class ErrorLearningSystem:
    """
    Reinforcement learning system that learns from errors and improves code generation quality.
    Stores error patterns, solutions, and prevention strategies.
    """
    
    def __init__(self, db_path: str = "./data/error_learning.db"):
        """Initialize the error learning system with database storage"""
        self.logger = setup_logger("error_learning_system")
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize quality metrics FIRST
        self.quality_trends = {
            "success_rate_history": [],
            "error_reduction_rate": 0.0,
            "learned_patterns_count": 0,
            "generation_quality_score": 0.0
        }
        
        # Error pattern cache for quick access
        self.error_patterns = {}
        self.solutions_cache = {}
        self.prevention_rules = []
        
        # Initialize database
        self._init_database()
        
        # Load cached data AFTER quality_trends is initialized
        self._load_error_patterns()
        
        self.logger.info("Error Learning System initialized successfully")
    
    def _init_database(self):
        """Initialize SQLite database for persistent error learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Error patterns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS error_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        error_hash TEXT UNIQUE,
                        error_type TEXT,
                        error_message TEXT,
                        stderr_content TEXT,
                        subject TEXT,
                        topic TEXT,
                        complexity TEXT,
                        code_snippet TEXT,
                        solution TEXT,
                        prevention_strategy TEXT,
                        occurrence_count INTEGER DEFAULT 1,
                        first_seen TIMESTAMP,
                        last_seen TIMESTAMP,
                        success_rate REAL DEFAULT 0.0
                    )
                ''')
                
                # Code quality metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS quality_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP,
                        subject TEXT,
                        topic TEXT,
                        complexity TEXT,
                        generation_attempt INTEGER,
                        success BOOLEAN,
                        error_count INTEGER,
                        quality_score REAL,
                        execution_time REAL,
                        learned_patterns_applied INTEGER
                    )
                ''')
                
                # Layout issues table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS layout_issues (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        issue_type TEXT,
                        description TEXT,
                        solution TEXT,
                        prevention_code TEXT,
                        subject TEXT,
                        topic TEXT,
                        timestamp TIMESTAMP
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def _load_error_patterns(self):
        """Load error patterns from database into memory for quick access"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Load error patterns
                cursor.execute('''
                    SELECT error_hash, error_type, error_message, solution, 
                           prevention_strategy, occurrence_count, success_rate
                    FROM error_patterns
                    ORDER BY occurrence_count DESC
                ''')
                
                rows = cursor.fetchall()
                for row in rows:
                    error_hash, error_type, error_msg, solution, prevention, count, success_rate = row
                    self.error_patterns[error_hash] = {
                        'type': error_type,
                        'message': error_msg,
                        'solution': solution or '',
                        'prevention': prevention or '',
                        'count': count,
                        'success_rate': success_rate or 0.0
                    }
                
                # Load prevention rules
                cursor.execute('''
                    SELECT DISTINCT prevention_strategy 
                    FROM error_patterns 
                    WHERE prevention_strategy IS NOT NULL AND success_rate > 0.7
                ''')
                
                prevention_rows = cursor.fetchall()
                self.prevention_rules = [row[0] for row in prevention_rows if row[0]]
                
                self.quality_trends["learned_patterns_count"] = len(self.error_patterns)
                self.logger.info(f"Loaded {len(self.error_patterns)} error patterns and {len(self.prevention_rules)} prevention rules")
                
        except Exception as e:
            self.logger.error(f"Failed to load error patterns: {e}")
            # Initialize empty structures on error
            self.error_patterns = {}
            self.prevention_rules = []
    
    def learn_from_error(self, error_data: Dict, code: str, context: Dict) -> Dict:
        """
        Learn from an encountered error and store the pattern for future prevention
        
        Args:
            error_data: Dictionary containing error information
            code: The code that caused the error
            context: Generation context (subject, topic, complexity, etc.)
            
        Returns:
            Dictionary with learning results and suggestions
        """
        try:
            # Create error hash for uniqueness
            error_content = f"{error_data.get('type', '')}:{error_data.get('message', '')}:{error_data.get('stderr', '')}"
            error_hash = hashlib.md5(error_content.encode()).hexdigest()
            
            # Analyze the error
            analysis = self._analyze_error(error_data, code, context)
            
            # Store or update error pattern
            learning_result = self._store_error_pattern(error_hash, error_data, analysis, context)
            
            # Generate prevention strategy
            prevention = self._generate_prevention_strategy(error_data, analysis, code)
            
            # Update quality metrics
            self._update_quality_metrics(context, False, analysis['error_count'])
            
            result = {
                'error_hash': error_hash,
                'learned': learning_result['is_new'],
                'occurrence_count': learning_result['count'],
                'analysis': analysis,
                'prevention_strategy': prevention,
                'suggested_fixes': self._get_suggested_fixes(error_data, analysis),
                'quality_impact': self._calculate_quality_impact(error_hash)
            }
            
            self.logger.info(f"Learned from error: {error_data.get('type', 'Unknown')} (occurrence #{learning_result['count']})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error learning failed: {e}")
            return {
                'error_hash': '',
                'learned': False,
                'occurrence_count': 0,
                'analysis': {'category': 'unknown', 'severity': 'medium'},
                'prevention_strategy': '',
                'suggested_fixes': [],
                'quality_impact': {},
                'error': str(e)
            }
    
    def _analyze_error(self, error_data: Dict, code: str, context: Dict) -> Dict:
        """Analyze error to understand its nature and cause"""
        analysis = {
            'category': 'unknown',
            'severity': 'medium',
            'likely_cause': 'unknown',
            'code_patterns': [],
            'error_count': 1,
            'is_layout_issue': False,
            'is_api_issue': False,
            'is_syntax_issue': False
        }
        
        error_message = error_data.get('message', '').lower()
        stderr = error_data.get('stderr', '').lower()
        
        # Categorize error
        if 'latex' in stderr or 'missing }' in stderr:
            analysis['category'] = 'latex_compilation'
            analysis['is_syntax_issue'] = True
            analysis['likely_cause'] = 'LaTeX syntax error in MathTex'
            analysis['severity'] = 'high'
            
        elif 'attributeerror' in stderr:
            analysis['category'] = 'api_compatibility'
            analysis['is_api_issue'] = True
            analysis['likely_cause'] = 'Using deprecated or non-existent Manim methods'
            analysis['severity'] = 'high'
            
        elif 'nameerror' in stderr:
            analysis['category'] = 'missing_import'
            analysis['is_syntax_issue'] = True
            analysis['likely_cause'] = 'Undefined variable or missing import'
            analysis['severity'] = 'medium'
            
        elif 'valueerror' in stderr:
            analysis['category'] = 'parameter_error'
            analysis['likely_cause'] = 'Invalid parameter values or types'
            analysis['severity'] = 'medium'
            
        elif 'overlap' in stderr or 'position' in stderr:
            analysis['category'] = 'layout_issue'
            analysis['is_layout_issue'] = True
            analysis['likely_cause'] = 'Overlapping elements or positioning problems'
            analysis['severity'] = 'low'
        
        # Extract problematic code patterns
        if code:
            analysis['code_patterns'] = self._extract_problematic_patterns(code, analysis['category'])
        
        return analysis
    
    def _extract_problematic_patterns(self, code: str, category: str) -> List[str]:
        """Extract specific code patterns that likely caused the error"""
        patterns = []
        
        if category == 'latex_compilation':
            # Find MathTex with potential issues
            mathtex_matches = re.findall(r'MathTex\([^)]+\)', code)
            patterns.extend(mathtex_matches)
            
        elif category == 'api_compatibility':
            # Find deprecated methods
            deprecated_methods = ['get_sides(', 'get_part_by_text(', 'get_part_by_tex(']
            for method in deprecated_methods:
                if method in code:
                    patterns.append(method)
                    
        elif category == 'layout_issue':
            # Find positioning-related code
            position_patterns = re.findall(r'\.move_to\([^)]+\)|\.shift\([^)]+\)|\.next_to\([^)]+\)', code)
            patterns.extend(position_patterns)
        
        return patterns
    
    def _store_error_pattern(self, error_hash: str, error_data: Dict, analysis: Dict, context: Dict) -> Dict:
        """Store error pattern in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if error already exists
                cursor.execute('SELECT occurrence_count FROM error_patterns WHERE error_hash = ?', (error_hash,))
                existing = cursor.fetchone()
                
                current_time = datetime.now().isoformat()
                
                if existing:
                    # Update existing pattern
                    new_count = existing[0] + 1
                    cursor.execute('''
                        UPDATE error_patterns 
                        SET occurrence_count = ?, last_seen = ?
                        WHERE error_hash = ?
                    ''', (new_count, current_time, error_hash))
                    
                    return {'is_new': False, 'count': new_count}
                    
                else:
                    # Insert new pattern
                    cursor.execute('''
                        INSERT INTO error_patterns 
                        (error_hash, error_type, error_message, stderr_content, subject, topic, complexity,
                         code_snippet, first_seen, last_seen)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        error_hash,
                        analysis['category'],
                        error_data.get('message', ''),
                        error_data.get('stderr', ''),
                        context.get('subject', ''),
                        context.get('topic', ''),
                        context.get('complexity', ''),
                        str(analysis.get('code_patterns', [])),
                        current_time,
                        current_time
                    ))
                    
                    return {'is_new': True, 'count': 1}
                    
        except Exception as e:
            self.logger.error(f"Failed to store error pattern: {e}")
            return {'is_new': False, 'count': 0}
    
    def _generate_prevention_strategy(self, error_data: Dict, analysis: Dict, code: str) -> str:
        """Generate prevention strategy based on error analysis"""
        category = analysis['category']
        
        strategies = {
            'latex_compilation': "Use raw strings for MathTex: r'\\\\text{content}'; Properly escape braces: {{text}} instead of {text}; Avoid empty MathTex content",
            'api_compatibility': "Use only modern Manim v0.19.0 API methods; Replace get_sides() with manual positioning; Remove color parameter from Indicate()",
            'missing_import': "Always include 'from manim import *' at the top; Import additional modules as needed",
            'parameter_error': "Validate parameter types and ranges; Use appropriate default values",
            'layout_issue': "Use proper spacing between elements; Check frame boundaries; Use VGroup for layouts"
        }
        
        return strategies.get(category, "General error prevention: validate inputs and test thoroughly")
    
    def _get_suggested_fixes(self, error_data: Dict, analysis: Dict) -> List[str]:
        """Get specific suggested fixes for the error"""
        fixes = []
        category = analysis['category']
        
        if category == 'latex_compilation':
            fixes.extend([
                "Replace MathTex with Text() for simple content",
                "Use raw strings: r'\\\\frac{a}{b}' instead of '\\\\frac{a}{b}'",
                "Escape braces properly: {{content}} in LaTeX",
                "Remove empty MathTex() calls"
            ])
            
        elif category == 'api_compatibility':
            fixes.extend([
                "Remove .get_sides() method calls",
                "Replace .get_part_by_text() with direct indexing",
                "Use Text() instead of deprecated text methods",
                "Update to modern Manim API methods"
            ])
            
        elif category == 'layout_issue':
            fixes.extend([
                "Add proper spacing: .shift(DOWN * 2)",
                "Use .arrange() for automatic layouts",
                "Check frame boundaries with get_frame_height()/width()",
                "Implement collision detection before positioning"
            ])
        
        return fixes
    
    def get_prevention_context(self, subject: str, topic: str, complexity: str) -> Dict:
        """
        Get prevention context for code generation based on learned patterns
        
        Returns accumulated knowledge to prevent known errors
        """
        try:
            prevention_context = {
                'known_error_patterns': [],
                'prevention_rules': [],
                'layout_guidelines': [],
                'api_recommendations': [],
                'quality_boosters': [],
                'success_patterns': []
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get error patterns for similar contexts
                cursor.execute('''
                    SELECT error_type, prevention_strategy, occurrence_count, success_rate
                    FROM error_patterns 
                    WHERE (subject = ? OR subject = '') 
                    AND (topic LIKE ? OR topic = '')
                    AND (complexity = ? OR complexity = '')
                    AND prevention_strategy IS NOT NULL
                    ORDER BY occurrence_count DESC, success_rate ASC
                    LIMIT 20
                ''', (subject, f'%{topic}%', complexity))
                
                rows = cursor.fetchall()
                for row in rows:
                    error_type, prevention, count, success_rate = row
                    if prevention:
                        prevention_context['prevention_rules'].append({
                            'type': error_type,
                            'rule': prevention,
                            'importance': count,
                            'success_rate': success_rate or 0.0
                        })
                
                # Get layout guidelines
                cursor.execute('''
                    SELECT DISTINCT solution, prevention_code
                    FROM layout_issues
                    WHERE subject = ? OR subject = ''
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''', (subject,))
                
                layout_rows = cursor.fetchall()
                for row in layout_rows:
                    solution, prevention_code = row
                    if solution:
                        prevention_context['layout_guidelines'].append({
                            'guideline': solution,
                            'code_example': prevention_code or ''
                        })
                
                # Get successful patterns
                cursor.execute('''
                    SELECT subject, topic, quality_score, learned_patterns_applied
                    FROM quality_metrics
                    WHERE success = 1 AND quality_score > 80
                    AND (subject = ? OR subject LIKE ?)
                    ORDER BY quality_score DESC
                    LIMIT 5
                ''', (subject, f'%{subject}%'))
                
                success_rows = cursor.fetchall()
                for row in success_rows:
                    subj, top, score, patterns = row
                    prevention_context['success_patterns'].append({
                        'context': f"{subj} - {top}",
                        'score': score,
                        'patterns_used': patterns or 0
                    })
            
            # Add general API recommendations
            prevention_context['api_recommendations'] = [
                "Use only Manim v0.19.0 compatible methods",
                "Prefer Text() over MathTex() for simple content",
                "Use VGroup for organizing multiple objects",
                "Always include proper wait() statements",
                "Use .arrange() for automatic spacing"
            ]
            
            # Add default layout guidelines if none found
            if not prevention_context['layout_guidelines']:
                prevention_context['layout_guidelines'] = [
                    {"guideline": "Keep elements within frame boundaries", "code_example": ".move_to(ORIGIN)"},
                    {"guideline": "Use DOWN, UP, LEFT, RIGHT for positioning", "code_example": ".shift(DOWN * 2)"},
                    {"guideline": "Maintain minimum spacing of 0.5 units", "code_example": ".arrange(DOWN, buff=0.5)"},
                    {"guideline": "Group related elements using VGroup", "code_example": "VGroup(obj1, obj2)"},
                    {"guideline": "Use .to_edge() for frame-relative positioning", "code_example": ".to_edge(UP)"}
                ]
            
            self.logger.info(f"Generated prevention context with {len(prevention_context['prevention_rules'])} rules")
            return prevention_context
            
        except Exception as e:
            self.logger.error(f"Failed to get prevention context: {e}")
            return {
                'known_error_patterns': [],
                'prevention_rules': [],
                'layout_guidelines': [
                    {"guideline": "Keep elements within frame boundaries", "code_example": ".move_to(ORIGIN)"},
                    {"guideline": "Use proper spacing between objects", "code_example": ".shift(DOWN * 1.5)"},
                    {"guideline": "Group related elements", "code_example": "VGroup(obj1, obj2)"},
                    {"guideline": "Use frame-relative positioning", "code_example": ".to_edge(UP)"},
                    {"guideline": "Apply automatic arrangements", "code_example": ".arrange(DOWN, buff=0.8)"}
                ],
                'api_recommendations': [],
                'quality_boosters': [],
                'success_patterns': [],
                'error': str(e)
            }
    
    def record_success(self, context: Dict, quality_score: float, execution_time: float, patterns_applied: int = 0):
        """Record successful generation for learning"""
        try:
            self._update_quality_metrics(context, True, 0, quality_score, execution_time, patterns_applied)
            
            # Update success rates for applied patterns
            if patterns_applied > 0:
                self._update_pattern_success_rates(context, True)
            
            self.logger.info(f"Recorded success: quality={quality_score}, patterns_applied={patterns_applied}")
            
        except Exception as e:
            self.logger.error(f"Failed to record success: {e}")
    
    def _update_quality_metrics(self, context: Dict, success: bool, error_count: int, 
                               quality_score: float = 0.0, execution_time: float = 0.0, 
                               patterns_applied: int = 0):
        """Update quality metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO quality_metrics 
                    (timestamp, subject, topic, complexity, success, error_count, 
                     quality_score, execution_time, learned_patterns_applied)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    context.get('subject', ''),
                    context.get('topic', ''),
                    context.get('complexity', ''),
                    success,
                    error_count,
                    quality_score,
                    execution_time,
                    patterns_applied
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to update quality metrics: {e}")
    
    def _update_pattern_success_rates(self, context: Dict, success: bool):
        """Update success rates for error patterns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # This is a simplified implementation
                cursor.execute('''
                    UPDATE error_patterns 
                    SET success_rate = (
                        SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)
                        FROM quality_metrics 
                        WHERE subject = error_patterns.subject
                    )
                    WHERE subject = ?
                ''', (context.get('subject', ''),))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to update pattern success rates: {e}")
    
    def _calculate_quality_impact(self, error_hash: str) -> Dict:
        """Calculate the quality impact of an error"""
        pattern = self.error_patterns.get(error_hash, {})
        
        return {
            'frequency_impact': min(pattern.get('count', 1) * 0.1, 1.0),
            'severity_multiplier': 1.5 if pattern.get('count', 1) > 5 else 1.0,
            'learning_opportunity': 1.0 - pattern.get('success_rate', 0.0)
        }
    
    def get_learning_stats(self) -> Dict:
        """Get comprehensive learning statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Basic stats
                cursor.execute('SELECT COUNT(*) FROM error_patterns')
                total_patterns_result = cursor.fetchone()
                total_patterns = total_patterns_result[0] if total_patterns_result else 0
                
                cursor.execute('SELECT AVG(success_rate) FROM error_patterns WHERE success_rate > 0')
                avg_success_result = cursor.fetchone()
                avg_success_rate = avg_success_result[0] if avg_success_result and avg_success_result[0] else 0.0
                
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM quality_metrics 
                    WHERE timestamp > datetime('now', '-7 days')
                ''')
                recent_generations_result = cursor.fetchone()
                recent_generations = recent_generations_result[0] if recent_generations_result else 0
                
                cursor.execute('''
                    SELECT AVG(quality_score) 
                    FROM quality_metrics 
                    WHERE success = 1 AND timestamp > datetime('now', '-7 days')
                ''')
                recent_quality_result = cursor.fetchone()
                recent_quality = recent_quality_result[0] if recent_quality_result and recent_quality_result[0] else 0.0
                
                # Error reduction trend
                cursor.execute('''
                    SELECT 
                        AVG(CASE WHEN timestamp > datetime('now', '-3 days') THEN error_count ELSE NULL END) as recent_errors,
                        AVG(CASE WHEN timestamp <= datetime('now', '-3 days') THEN error_count ELSE NULL END) as older_errors
                    FROM quality_metrics
                ''')
                error_trend_result = cursor.fetchone()
                recent_errors, older_errors = error_trend_result if error_trend_result else (0, 0)
                
                error_reduction = 0.0
                if older_errors and older_errors > 0 and recent_errors is not None:
                    error_reduction = ((older_errors - recent_errors) / older_errors) * 100
                
                return {
                    'total_learned_patterns': total_patterns,
                    'average_success_rate': round(float(avg_success_rate), 3),
                    'recent_generations': recent_generations,
                    'recent_quality_average': round(float(recent_quality), 2),
                    'error_reduction_percentage': round(float(error_reduction), 2),
                    'learning_effectiveness': round(float(avg_success_rate) * (total_patterns / 10), 3),
                    'database_path': self.db_path
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get learning stats: {e}")
            return {
                'total_learned_patterns': 0,
                'average_success_rate': 0.0,
                'recent_generations': 0,
                'recent_quality_average': 0.0,
                'error_reduction_percentage': 0.0,
                'learning_effectiveness': 0.0,
                'database_path': self.db_path,
                'error': str(e)
            }
