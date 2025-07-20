import PyMuPDF as fitz
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ContentExtractor:
    def __init__(self):
        self.min_section_length = 50
        self.max_section_length = 2000
    
    def extract_sections(self, pdf_path: str, outline_data: Dict) -> List[Dict]:
        """Extract content sections based on outline structure"""
        try:
            doc = fitz.open(pdf_path)
            sections = []
            
            outline = outline_data.get("outline", [])
            
            if not outline:
                # If no outline, extract by pages
                sections = self._extract_by_pages(doc)
            else:
                sections = self._extract_by_outline(doc, outline)
            
            doc.close()
            return sections
            
        except Exception as e:
            logger.error(f"Error extracting sections: {e}")
            return []
    
    def _extract_by_outline(self, doc, outline: List[Dict]) -> List[Dict]:
        """Extract sections based on document outline"""
        sections = []
        
        for i, heading in enumerate(outline):
            try:
                # Get text from heading's page
                page_num = heading.get("page", 1) - 1  # Convert to 0-based
                
                if page_num < len(doc):
                    page = doc[page_num]
                    
                    # Extract text from the page
                    page_text = page.get_text()
                    
                    # Try to find the heading in the text and extract following content
                    heading_text = heading["text"]
                    content = self._extract_content_after_heading(page_text, heading_text)
                    
                    # If content is too short, get content from next pages too
                    if len(content) < self.min_section_length and page_num + 1 < len(doc):
                        next_page = doc[page_num + 1]
                        content += " " + next_page.get_text()[:1000]  # Add some from next page
                    
                    if len(content) >= self.min_section_length:
                        sections.append({
                            "title": heading_text,
                            "content": content[:self.max_section_length],
                            "page": heading.get("page", 1),
                            "level": heading.get("level", "H1"),
                            "word_count": len(content.split())
                        })
                        
            except Exception as e:
                logger.error(f"Error processing heading {heading}: {e}")
                continue
        
        return sections
    
    def _extract_by_pages(self, doc) -> List[Dict]:
        """Extract sections by pages when no outline is available"""
        sections = []
        
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                text = page.get_text()
                
                if len(text.strip()) >= self.min_section_length:
                    # Try to find a natural break or use first paragraph as title
                    lines = text.split('\n')
                    title = lines[0] if lines else f"Page {page_num + 1}"
                    
                    # Clean title
                    title = title.strip()[:100]
                    
                    sections.append({
                        "title": title,
                        "content": text[:self.max_section_length],
                        "page": page_num + 1,
                        "level": "H1",
                        "word_count": len(text.split())
                    })
                    
            except Exception as e:
                logger.error(f"Error processing page {page_num}: {e}")
                continue
        
        return sections
    
    def _extract_content_after_heading(self, page_text: str, heading_text: str) -> str:
        """Extract content that appears after a specific heading"""
        lines = page_text.split('\n')
        
        # Find the heading line
        heading_index = -1
        for i, line in enumerate(lines):
            if heading_text.lower() in line.lower():
                heading_index = i
                break
        
        if heading_index == -1:
            # Heading not found, return first part of page
            return ' '.join(lines[:10])
        
        # Extract content after heading
        content_lines = lines[heading_index + 1:]
        
        # Stop at next heading or after reasonable amount of content
        content = []
        for line in content_lines:
            line = line.strip()
            if line:
                # Stop if we hit what looks like another heading
                if (len(line) < 100 and 
                    (line.isupper() or 
                     re.match(r'^\d+\.?\s+[A-Z]', line) or
                     re.match(r'^[A-Z][A-Z\s]+$', line))):
                    break
                content.append(line)
            
            if len(' '.join(content)) > 1500:  # Reasonable section size
                break
        
        return ' '.join(content)
    
    def extract_subsections(self, content: str, persona_data: Dict) -> List[Dict]:
        """Extract and refine subsections from content"""
        subsections = []
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
        
        # Create subsections from meaningful paragraphs
        for i, paragraph in enumerate(paragraphs[:5]):  # Limit to 5 subsections
            if len(paragraph) >= 100:  # Meaningful length
                subsections.append({
                    "subsection_id": f"sub_{i+1}",
                    "content": paragraph,
                    "word_count": len(paragraph.split()),
                    "relevance_indicators": self._extract_relevance_indicators(paragraph, persona_data)
                })
        
        return subsections
    
    def _extract_relevance_indicators(self, text: str, persona_data: Dict) -> List[str]:
        """Extract indicators of why this text might be relevant"""
        indicators = []
        
        persona = persona_data.get("persona", "").lower()
        job = persona_data.get("job_description", "").lower()
        
        # Simple keyword matching
        persona_words = persona.split()
        job_words = job.split()
        
        text_lower = text.lower()
        
        for word in persona_words + job_words:
            if len(word) > 3 and word in text_lower:
                indicators.append(f"Contains '{word}' (persona/job relevant)")
        
        # Look for methodology terms, numbers, conclusions
        if re.search(r'\b\d+%\b|\b\d+\.\d+\b', text):
            indicators.append("Contains numerical data")
        
        method_words = ['method', 'approach', 'analysis', 'result', 'conclusion', 'finding']
        for word in method_words:
            if word in text_lower:
                indicators.append(f"Contains methodology term: {word}")
        
        return indicators[:3]