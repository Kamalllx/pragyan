import re
from typing import List, Dict, Tuple

class ScriptCleaner:
    """
    Clean and extract pure narration content from AI-generated scripts
    """
    
    def __init__(self):
        self.debug_mode = True
    
    def extract_clean_narration(self, raw_script: str) -> str:
        """Extract only the pure narration content for voice synthesis"""
        
        if self.debug_mode:
            print(f"\n🧹 CLEANING SCRIPT FOR VOICE NARRATION")
            print(f"   📄 Raw script length: {len(raw_script)} characters")
        
        try:
            # Method 1: Extract from markdown table format
            if '|' in raw_script and 'Narration' in raw_script:
                narration = self._extract_from_table_format(raw_script)
                if narration:
                    return narration
            
            # Method 2: Extract from structured format with timestamps
            if 'Timestamp' in raw_script or '00:' in raw_script:
                narration = self._extract_from_timestamp_format(raw_script)
                if narration:
                    return narration
            
            # Method 3: Extract main content (fallback)
            narration = self._extract_main_content(raw_script)
            
            if self.debug_mode:
                print(f"   ✅ Clean narration extracted: {len(narration)} characters")
                print(f"   📝 Preview: {narration[:100]}...")
            
            return narration
            
        except Exception as e:
            print(f"   ❌ Script cleaning failed: {e}")
            return self._fallback_extraction(raw_script)
    
    def _extract_from_table_format(self, script: str) -> str:
        """Extract narration from markdown table format"""
        
        print(f"      🔍 Extracting from table format...")
        
        # Find all table rows with narration content
        # Pattern: | anything | anything | NARRATION_CONTENT |
        pattern = r'\|\s*[^|]*\|\s*[^|]*\|\s*([^|]+)\s*\|'
        
        matches = re.findall(pattern, script, re.MULTILINE | re.DOTALL)
        
        if not matches:
            return ""
        
        # Clean each narration segment
        clean_segments = []
        for match in matches:
            cleaned = self._clean_narration_segment(match)
            if cleaned and len(cleaned) > 10:  # Only meaningful content
                clean_segments.append(cleaned)
        
        print(f"         Found {len(clean_segments)} narration segments")
        
        return " ".join(clean_segments)
    
    def _extract_from_timestamp_format(self, script: str) -> str:
        """Extract narration from timestamp-based format"""
        
        print(f"      🔍 Extracting from timestamp format...")
        
        # Look for patterns like "| 00:00 - 00:07 | ... | NARRATION |"
        # or lines that contain timestamps followed by narration
        
        lines = script.split('\n')
        narration_segments = []
        
        for line in lines:
            # Skip header and separator lines
            if any(skip in line.lower() for skip in ['timestamp', 'scene description', ':---', '====', '---']):
                continue
            
            # Extract from table format
            if line.count('|') >= 3:
                parts = line.split('|')
                if len(parts) >= 4:
                    # Last part should be narration
                    narration_part = parts[-2].strip()  # -1 is usually empty after final |
                    cleaned = self._clean_narration_segment(narration_part)
                    if cleaned and len(cleaned) > 10:
                        narration_segments.append(cleaned)
        
        print(f"         Found {len(narration_segments)} narration segments")
        
        return " ".join(narration_segments)
    
    def _extract_main_content(self, script: str) -> str:
        """Extract main content using content patterns"""
        
        print(f"      🔍 Extracting main content...")
        
        # Remove common headers and metadata
        content = script
        
        # Remove header section
        if '====' in content:
            parts = content.split('====')
            if len(parts) > 1:
                content = parts[-1]  # Take content after last ====
        
        # Remove table headers and markdown
        content = re.sub(r'\|[^|]*\|[^|]*\|[^|]*\|', '', content)  # Remove table structure
        content = re.sub(r'\|.*?:.*?\|', '', content)  # Remove table headers
        content = re.sub(r':---+', '', content)  # Remove table separators
        
        # Extract sentences that look like narration
        sentences = re.findall(r'[.!?]\s+([A-Z][^.!?]*[.!?])', content)
        
        if sentences:
            return " ".join(sentences)
        
        # Fallback: clean the content we have
        return self._clean_narration_segment(content)
    
    def _clean_narration_segment(self, segment: str) -> str:
        """Clean individual narration segment"""
        
        if not segment or not segment.strip():
            return ""
        
        cleaned = segment.strip()
        
        # Remove HTML tags
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Remove markdown formatting
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)  # **bold**
        cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)      # *italic*
        cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)        # `code`
        
        # Remove scene descriptions and stage directions
        cleaned = re.sub(r'\[SCENE[^\]]*\]', '', cleaned)
        cleaned = re.sub(r'\[VISUAL[^\]]*\]', '', cleaned)
        cleaned = re.sub(r'\(pronounce:[^)]+\)', '', cleaned)
        
        # Remove timestamps
        cleaned = re.sub(r'\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', '', cleaned)
        
        # Remove table artifacts
        cleaned = re.sub(r'Timestamp.*?Narration', '', cleaned)
        cleaned = re.sub(r'Scene Description.*?Narration', '', cleaned)
        
        # Remove unwanted phrases
        unwanted_phrases = [
            'Educational Script',
            'Generated:',
            'Subject:',
            'Topic:',
            'Video Duration:',
            'Target Audience:',
            'Narration Style:',
            'Begin Script',
            'End Script',
            'For Manim Animator'
        ]
        
        for phrase in unwanted_phrases:
            cleaned = re.sub(re.escape(phrase) + r'[^\n]*', '', cleaned, flags=re.IGNORECASE)
        
        # Clean whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        # Remove if it's just formatting or very short
        if len(cleaned) < 10 or cleaned.lower() in ['narration', 'scene', 'visual', '']:
            return ""
        
        return cleaned
    
    def _fallback_extraction(self, script: str) -> str:
        """Fallback extraction for unstructured content"""
        
        print(f"      🔧 Using fallback extraction...")
        
        # Find the longest coherent paragraph
        paragraphs = script.split('\n\n')
        
        best_paragraph = ""
        for para in paragraphs:
            cleaned = self._clean_narration_segment(para)
            if len(cleaned) > len(best_paragraph):
                best_paragraph = cleaned
        
        return best_paragraph if best_paragraph else "Educational content about the topic."
    
    def extract_timing_segments(self, raw_script: str) -> List[Dict]:
        """Extract timing information if available for synchronization"""
        
        segments = []
        
        # Look for timestamp patterns
        timestamp_pattern = r'(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})'
        narration_pattern = r'\|\s*[^|]*\|\s*[^|]*\|\s*([^|]+)\s*\|'
        
        lines = raw_script.split('\n')
        
        for line in lines:
            timestamp_match = re.search(timestamp_pattern, line)
            narration_match = re.search(narration_pattern, line)
            
            if timestamp_match and narration_match:
                start_time = self._time_to_seconds(timestamp_match.group(1))
                end_time = self._time_to_seconds(timestamp_match.group(2))
                narration = self._clean_narration_segment(narration_match.group(1))
                
                if narration and len(narration) > 10:
                    segments.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': end_time - start_time,
                        'narration': narration
                    })
        
        return segments
    
    def _time_to_seconds(self, time_str: str) -> float:
        """Convert MM:SS to seconds"""
        try:
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0.0


# Test the cleaner
def test_script_cleaner():
    """Test the script cleaner with your example"""
    
    raw_script = '''Educational Script - English (Indian)
Generated: 2025-06-22 04:22:52.021809
Subject: physics
Topic: newtons laws
==================================================

Here is the educational narration script for a Manim animation on Newton's Laws of Motion. --- # Educational Narration Script: Newton's Laws of Motion Video Duration: 66.0 seconds Target Audience: Beginner level students (Indian context) Narration Style: Professional, friendly, and clear educational tone. (Begin Script) | Timestamp | Scene Description (For Manim Animator) | Narration | | :--- | :--- | :--- | | 00:00 - 00:07 | [SCENE START]<br>An engaging intro sequence. The words "Newton's Laws of Motion" animate onto the screen. A stylized apple falls next to a silhouette of Sir Isaac Newton. | Hello friends! Ever wondered why things move the way they do? From a cricket ball to the planets, everything follows three simple rules discovered by Sir Isaac Newton. Let's understand them! | | 00:07 - 00:20 | [VISUAL]<br>Title: "First Law: The Law of Inertia". A football is shown at rest on a field. A foot icon appears and gently taps it. The ball starts rolling and continues to roll at a constant speed. | First, we have the Law of Inertia. (pronounce: in-er-shia). It says an object will stay at rest, or keep moving at a constant speed, unless an external force acts on it. This resting football only moves when it is kicked! | | 00:20 - 00:38 | [VISUAL]<br>Title: "Second Law: Force, Mass & Acceleration". A block with mass 'm' is shown. A small arrow representing 'Force' pushes it, and it accelerates slowly. Then, a much larger arrow pushes it, and it accelerates quickly. The formula F = m × a appears and highlights each component. | Next is the Second Law, which connects force, mass, and acceleration. The formula is Force equals Mass times Acceleration. This means if you apply more force to an object, it will speed up faster! Think of hitting a cricket ball – a harder hit sends it flying further and faster! | | 00:38 - 00:52 | [VISUAL]<br>Title: "Third Law: Action & Reaction". A simple rocket is shown on a launchpad. It ignites, showing a strong downward arrow labeled "Action (Gas Push)". An equally strong upward arrow appears labeled "Reaction (Rocket Moves Up)", and the rocket lifts off. | And finally, the Third Law. This one is simple: For every action, there is an equal and opposite reaction. When a rocket pushes hot gas downwards—that's the action—the gas pushes the rocket upwards with equal force—that's the reaction! | | 00:52 - 01:06 | [VISUAL]<br>A summary screen appears with three columns. Each column has an icon and a keyword:<br>1. Icon: A resting book. Keyword: Inertia<br>2. Icon: The formula F=ma. Keyword: Acceleration<br>3. Icon: Two opposing arrows. Keyword: Action-Reaction<br>The video ends with a "Keep Exploring!" message. | So, to summarise: The First Law is about inertia. The Second Law tells us that Force equals Mass times Acceleration. And the Third Law is about action and reaction. These three laws are the foundation of physics and explain motion all around us. Keep asking questions and keep learning! | (End Script).'''
    
    cleaner = ScriptCleaner()
    
    # Test clean extraction
    clean_narration = cleaner.extract_clean_narration(raw_script)
    print(f"\n✅ CLEAN NARRATION RESULT:")
    print(f"Length: {len(clean_narration)} characters")
    print(f"Content: {clean_narration}")
    
    # Test timing extraction
    timing_segments = cleaner.extract_timing_segments(raw_script)
    print(f"\n⏱️ TIMING SEGMENTS:")
    for i, segment in enumerate(timing_segments, 1):
        print(f"{i}. {segment['start_time']:.0f}s-{segment['end_time']:.0f}s: {segment['narration'][:50]}...")
    
    return clean_narration, timing_segments

if __name__ == "__main__":
    test_script_cleaner()
