import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class HeadingDetector:
    def __init__(self):
        self.patterns = {
            'numbered': r'^\d+\.?\s+[A-Z]',
            'sub_numbered': r'^\d+\.\d+\.?\s+',
            'all_caps': r'^[A-Z][A-Z\s]+$',
            'chapter': r'^Chapter\s+\d+',
            'roman': r'^[IVX]+\.?\s+[A-Z]',
            'letter': r'^[A-Z]\.\s+[A-Z]',
        }
        
    def detect_heading_patterns(self, text: str) -> Dict:
        """Detect various heading patterns in text"""
        results = {}
        
        for pattern_name, pattern in self.patterns.items():
            if re.match(pattern, text, re.IGNORECASE):
                results[pattern_name] = True
            else:
                results[pattern_name] = False
                
        return results
    
    def calculate_heading_score(self, text_block: Dict) -> float:
        """Calculate confidence score for heading detection"""
        score = 0.0
        text = text_block['text']
        
        # Font size score
        if 'size' in text_block and 'body_size' in text_block:
            size_ratio = text_block['size'] / text_block['body_size']
            if size_ratio > 1.2:
                score += 0.3 * min(size_ratio - 1, 1)
        
        # Pattern matching score
        patterns = self.detect_heading_patterns(text)
        if any(patterns.values()):
            score += 0.4
        
        # Font formatting score
        if text_block.get('flags', 0) & 2**4:  # Bold
            score += 0.2
        
        # Position score
        if text_block.get('x', 0) < 100:  # Left aligned
            score += 0.1
        
        return min(score, 1.0)