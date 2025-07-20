import PyMuPDF as fitz
import re
import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import unicodedata

logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    def __init__(self):
        self.heading_patterns = [
            r'^\d+\.?\s+[A-Z]',  # Numbered headings like "1. Introduction"
            r'^[A-Z][A-Z\s]+$',   # All caps headings
            r'^Chapter\s+\d+',    # Chapter patterns
            r'^\d+\.\d+\.?\s+',   # Sub-numbered like "1.1 Overview"
            r'^[IVX]+\.?\s+[A-Z]', # Roman numerals
            r'^[A-Z]\.\s+[A-Z]',   # Letter headings like "A. Overview"
        ]
        
    def extract_outline(self, pdf_path: str) -> Dict:
        """Extract structured outline from PDF"""
        try:
            doc = fitz.open(pdf_path)
            logger.info(f"Opened PDF with {len(doc)} pages")
            
            # Step 1: Extract all text with formatting info
            text_blocks = self._extract_formatted_text(doc)
            
            # Step 2: Analyze font patterns
            font_analysis = self._analyze_fonts(text_blocks)
            
            # Step 3: Detect headings using multiple heuristics
            headings = self._detect_headings(text_blocks, font_analysis)
            
            # Step 4: Build hierarchy
            outline = self._build_hierarchy(headings)
            
            # Step 5: Extract title
            title = self._extract_title(text_blocks, doc)
            
            doc.close()
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            logger.error(f"Error extracting outline: {e}")
            return {"title": "", "outline": []}
    
    def _extract_formatted_text(self, doc) -> List[Dict]:
        """Extract text with formatting information"""
        text_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                text_blocks.append({
                                    "text": text,
                                    "page": page_num + 1,
                                    "font": span["font"],
                                    "size": span["size"],
                                    "flags": span["flags"],
                                    "bbox": span["bbox"],
                                    "x": span["bbox"][0],
                                    "y": span["bbox"][1]
                                })
        
        return text_blocks
    
    def _analyze_fonts(self, text_blocks: List[Dict]) -> Dict:
        """Analyze font patterns to identify potential headings"""
        font_sizes = [block["size"] for block in text_blocks]
        font_counter = Counter(font_sizes)
        
        # Most common font size is likely body text
        body_font_size = font_counter.most_common(1)[0][0]
        
        # Calculate statistics
        avg_font_size = sum(font_sizes) / len(font_sizes)
        
        return {
            "body_font_size": body_font_size,
            "avg_font_size": avg_font_size,
            "font_distribution": font_counter,
            "large_font_threshold": body_font_size * 1.2
        }
    
    def _detect_headings(self, text_blocks: List[Dict], font_analysis: Dict) -> List[Dict]:
        """Detect headings using multiple heuristics"""
        headings = []
        
        for block in text_blocks:
            is_heading = False
            heading_level = None
            confidence = 0
            
            # Check font size
            if block["size"] > font_analysis["large_font_threshold"]:
                is_heading = True
                confidence += 0.3
                
                # Determine level based on relative font size
                size_ratio = block["size"] / font_analysis["body_font_size"]
                if size_ratio >= 1.5:
                    heading_level = "H1"
                elif size_ratio >= 1.3:
                    heading_level = "H2"
                else:
                    heading_level = "H3"
            
            # Check font formatting (bold, etc.)
            if block["flags"] & 2**4:  # Bold flag
                is_heading = True
                confidence += 0.2
            
            # Check text patterns
            text = block["text"]
            for pattern in self.heading_patterns:
                if re.match(pattern, text):
                    is_heading = True
                    confidence += 0.3
                    
                    # Refine heading level based on pattern
                    if re.match(r'^\d+\.?\s+', text):
                        heading_level = "H1"
                    elif re.match(r'^\d+\.\d+\.?\s+', text):
                        heading_level = "H2"
                    elif re.match(r'^\d+\.\d+\.\d+\.?\s+', text):
                        heading_level = "H3"
                    break
            
            # Check position (left-aligned, start of line)
            if block["x"] < 100:  # Assuming left margin
                confidence += 0.1
            
            # Check if text is all caps (strong indicator)
            if text.isupper() and len(text.split()) > 1:
                is_heading = True
                confidence += 0.4
                if not heading_level:
                    heading_level = "H1"
            
            # Check for chapter/section keywords
            chapter_keywords = ["chapter", "section", "part", "introduction", "conclusion", "abstract", "summary"]
            if any(keyword in text.lower() for keyword in chapter_keywords):
                confidence += 0.2
            
            # Apply confidence threshold
            if is_heading and confidence >= 0.3:
                if not heading_level:
                    # Default level based on font size
                    size_ratio = block["size"] / font_analysis["body_font_size"]
                    if size_ratio >= 1.4:
                        heading_level = "H1"
                    elif size_ratio >= 1.2:
                        heading_level = "H2"
                    else:
                        heading_level = "H3"
                
                headings.append({
                    "text": text,
                    "level": heading_level,
                    "page": block["page"],
                    "confidence": confidence,
                    "size": block["size"],
                    "y": block["y"]
                })
        
        # Sort by page and position
        headings.sort(key=lambda x: (x["page"], -x["y"]))
        
        return headings
    
    def _build_hierarchy(self, headings: List[Dict]) -> List[Dict]:
        """Build hierarchical outline from detected headings"""
        if not headings:
            return []
        
        # Clean up and validate heading levels
        outline = []
        level_map = {"H1": 1, "H2": 2, "H3": 3}
        
        for heading in headings:
            # Clean up text
            text = heading["text"].strip()
            
            # Remove numbering for cleaner text (optional)
            # text = re.sub(r'^\d+\.?\s*', '', text)
            # text = re.sub(r'^[IVX]+\.?\s*', '', text, flags=re.IGNORECASE)
            
            outline.append({
                "level": heading["level"],
                "text": text,
                "page": heading["page"]
            })
        
        return outline
    
    def _extract_title(self, text_blocks: List[Dict], doc) -> str:
        """Extract document title using multiple strategies"""
        if not text_blocks:
            return ""
        
        # Strategy 1: Look for largest font on first page
        first_page_blocks = [b for b in text_blocks if b["page"] == 1]
        if first_page_blocks:
            max_font_size = max(b["size"] for b in first_page_blocks)
            title_candidates = [b for b in first_page_blocks if b["size"] == max_font_size]
            
            if title_candidates:
                # Take the first large text as title
                title = title_candidates[0]["text"]
                
                # Clean up title
                title = title.strip()
                if len(title) > 100:  # Too long to be a title
                    title = title[:100] + "..."
                
                return title
        
        # Strategy 2: Use PDF metadata
        try:
            metadata = doc.metadata
            if metadata and metadata.get("title"):
                return metadata["title"].strip()
        except:
            pass
        
        # Strategy 3: First significant text block
        for block in text_blocks[:10]:  # Check first 10 blocks
            text = block["text"].strip()
            if len(text) > 10 and not text.startswith(("Page", "www.", "http")):
                return text
        
        return "Untitled Document"
    
    def _is_multilingual_heading(self, text: str) -> bool:
        """Detect headings in multiple languages (bonus feature)"""
        # Simple multilingual detection
        scripts = set()
        for char in text:
            try:
                script = unicodedata.name(char, '').split()[0]
                scripts.add(script)
            except:
                continue
        
        # Common heading patterns for different scripts
        if 'CJK' in ' '.join(scripts):  # Chinese, Japanese, Korean
            # Look for common CJK heading patterns
            cjk_patterns = [
                r'^第.{1,3}章',  # Chapter patterns in Chinese/Japanese
                r'^.{1,10}について$',  # Japanese "about" pattern
                r'^\d+[．。]\s*.+',  # Numbered with CJK punctuation
            ]
            for pattern in cjk_patterns:
                if re.search(pattern, text):
                    return True
        
        return False