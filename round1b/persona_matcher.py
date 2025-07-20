from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class PersonaMatcher:
    def __init__(self):
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence transformer model")
        except Exception as e:
            logger.error(f"Error loading sentence transformer: {e}")
            self.embedder = None
    
    def create_persona_embedding(self, persona_data):
        """Create embedding for persona and job description"""
        if not self.embedder:
            return np.zeros(384)  # Fallback
        
        persona = persona_data.get("persona", "")
        job_description = persona_data.get("job_description", "")
        
        # Combine persona and job for comprehensive embedding
        combined_text = f"{persona}. {job_description}"
        
        try:
            embedding = self.embedder.encode([combined_text])
            return embedding[0]
        except Exception as e:
            logger.error(f"Error creating persona embedding: {e}")
            return np.zeros(384)
    
    def match_content_to_persona(self, content, persona_embedding):
        """Calculate how well content matches the persona"""
        if not self.embedder:
            return 0.5  # Fallback score
        
        try:
            content_embedding = self.embedder.encode([content])
            similarity = cosine_similarity([persona_embedding], content_embedding)[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error matching content to persona: {e}")
            return 0.5
    
    def extract_persona_keywords(self, persona_data):
        """Extract key terms from persona description"""
        persona = persona_data.get("persona", "").lower()
        job = persona_data.get("job_description", "").lower()
        
        # Simple keyword extraction
        import re
        combined = f"{persona} {job}"
        
        # Extract meaningful terms
        keywords = re.findall(r'\b[a-zA-Z]{3,}\b', combined)
        
        # Filter common words
        stop_words = {'the', 'and', 'for', 'are', 'with', 'this', 'that', 'have', 'from', 'they', 'been', 'their', 'said', 'each', 'which', 'will', 'about', 'there', 'could', 'other'}
        
        keywords = [w for w in keywords if w not in stop_words and len(w) > 3]
        
        return list(set(keywords))  # Remove duplicates