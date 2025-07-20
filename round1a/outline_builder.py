from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class OutlineBuilder:
    def __init__(self):
        self.level_hierarchy = {"H1": 1, "H2": 2, "H3": 3}
        
    def build_outline(self, headings: List[Dict]) -> List[Dict]:
        """Build hierarchical outline from headings"""
        if not headings:
            return []
        
        outline = []
        current_levels = {"H1": 0, "H2": 0, "H3": 0}
        
        for heading in headings:
            level = heading.get('level', 'H1')
            text = self.clean_heading_text(heading['text'])
            
            outline_item = {
                'level': level,
                'text': text,
                'page': heading['page']
            }
            
            outline.append(outline_item)
        
        return outline
    
    def clean_heading_text(self, text: str) -> str:
        """Clean and format heading text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Optionally remove numbering (uncomment if desired)
        # text = re.sub(r'^\d+\.?\s*', '', text)
        # text = re.sub(r'^[IVX]+\.?\s*', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def validate_hierarchy(self, outline: List[Dict]) -> List[Dict]:
        """Validate and fix heading hierarchy"""
        if not outline:
            return outline
        
        validated = []
        last_level = 0
        
        for item in outline:
            current_level = self.level_hierarchy.get(item['level'], 1)
            
            # Ensure proper hierarchy (can't jump more than one level)
            if current_level > last_level + 1:
                item['level'] = f"H{last_level + 1}"
            
            validated.append(item)
            last_level = self.level_hierarchy.get(item['level'], 1)
        
        return validated