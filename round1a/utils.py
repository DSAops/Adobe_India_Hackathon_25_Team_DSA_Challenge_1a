import unicodedata
import re
from typing import List, Dict

def is_likely_header_text(text: str) -> bool:
    """Determine if text is likely a header based on content"""
    # Skip very short or very long text
    if len(text) < 3 or len(text) > 200:
        return False
    
    # Skip URLs, emails, page numbers
    if any(pattern in text.lower() for pattern in ['http', 'www.', '@', 'page ']):
        return False
    
    # Skip text that's mostly punctuation or numbers
    if len(re.sub(r'[^\w\s]', '', text)) < len(text) * 0.5:
        return False
    
    return True

def normalize_text(text: str) -> str:
    """Normalize text for better processing"""
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    return text

def detect_language_script(text: str) -> str:
    """Detect the primary script of the text"""
    scripts = {}
    
    for char in text:
        try:
            script = unicodedata.name(char, '').split()[0]
            scripts[script] = scripts.get(script, 0) + 1
        except:
            continue
    
    if not scripts:
        return 'LATIN'
    
    return max(scripts, key=scripts.get)
