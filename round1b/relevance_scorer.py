import numpy as np
import re
import logging
from typing import List, Dict
from .persona_matcher import PersonaMatcher

logger = logging.getLogger(__name__)

class RelevanceScorer:
    def __init__(self):
        self.persona_matcher = PersonaMatcher()
        
        # Domain-specific keywords for different personas
        self.domain_keywords = {
            'researcher': ['method', 'analysis', 'study', 'research', 'data', 'result', 'conclusion', 'hypothesis'],
            'analyst': ['trend', 'performance', 'metric', 'revenue', 'growth', 'market', 'competitive', 'strategy'],
            'student': ['concept', 'theory', 'example', 'definition', 'principle', 'explanation', 'overview'],
            'manager': ['strategy', 'team', 'project', 'goal', 'resource', 'planning', 'execution', 'decision'],
            'engineer': ['system', 'design', 'implementation', 'technical', 'architecture', 'solution', 'performance']
        }
    
    def score_sections(self, sections: List[Dict], persona_data: Dict) -> List[Dict]:
        """Score all sections for relevance to persona"""
        if not sections:
            return []
        
        # Create persona embedding
        persona_embedding = self.persona_matcher.create_persona_embedding(persona_data)
        
        # Score each section
        scored_sections = []
        for section in sections:
            score_data = self._calculate_comprehensive_score(section, persona_data, persona_embedding)
            
            section.update(score_data)
            scored_sections.append(section)
        
        # Sort by relevance score
        scored_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored_sections
    
    def _calculate_comprehensive_score(self, section: Dict, persona_data: Dict, persona_embedding) -> Dict:
        """Calculate comprehensive relevance score using multiple factors"""
        content = section.get("content", "")
        
        # 1. Semantic similarity score (40% weight)
        semantic_score = self.persona_matcher.match_content_to_persona(content, persona_embedding)
        
        # 2. Keyword relevance score (30% weight)
        keyword_score = self._calculate_keyword_score(content, persona_data)
        
        # 3. Content quality score (20% weight)
        quality_score = self._calculate_content_quality(content)
        
        # 4. Position/importance score (10% weight)
        position_score = self._calculate_position_score(section)
        
        # Combine scores with weights
        final_score = (0.4 * semantic_score + 
                      0.3 * keyword_score + 
                      0.2 * quality_score + 
                      0.1 * position_score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(semantic_score, keyword_score, quality_score, position_score)
        
        return {
            "relevance_score": round(float(final_score), 3),
            "semantic_similarity": round(float(semantic_score), 3),
            "keyword_relevance": round(float(keyword_score), 3),
            "content_quality": round(float(quality_score), 3),
            "position_importance": round(float(position_score), 3),
            "reasoning": reasoning
        }
    
    def _calculate_keyword_score(self, content: str, persona_data: Dict) -> float:
        """Calculate keyword-based relevance score"""
        content_lower = content.lower()
        
        # Extract persona keywords
        persona_keywords = self.persona_matcher.extract_persona_keywords(persona_data)
        
        # Detect persona type for domain-specific keywords
        persona_type = self._detect_persona_type(persona_data.get("persona", ""))
        domain_keywords = self.domain_keywords.get(persona_type, [])
        
        # Count keyword matches
        persona_matches = sum(1 for keyword in persona_keywords if keyword in content_lower)
        domain_matches = sum(1 for keyword in domain_keywords if keyword in content_lower)
        
        # Calculate scores
        persona_score = min(persona_matches / max(len(persona_keywords), 1), 1.0)
        domain_score = min(domain_matches / max(len(domain_keywords), 1), 1.0)
        
        # Combine scores
        return (0.6 * persona_score + 0.4 * domain_score)
    
    def _calculate_content_quality(self, content: str) -> float:
        """Calculate content quality score"""
        if not content:
            return 0.0
        
        score = 0.0
        
        # Length appropriateness (not too short, not too long)
        length = len(content)
        if 100 <= length <= 2000:
            score += 0.3
        elif 50 <= length < 100 or 2000 < length <= 3000:
            score += 0.2
        else:
            score += 0.1
        
        # Sentence structure variety
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) >= 3:
            score += 0.2
        
        # Presence of numbers/data (often important)
        if re.search(r'\b\d+%\b|\b\d+\.\d+\b|\b\d{4}\b', content):
            score += 0.2
        
        # Presence of technical terms or jargon
        if re.search(r'\b[A-Z]{2,}\b', content):  # Acronyms
            score += 0.1
        
        # Good paragraph structure
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 2:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_position_score(self, section: Dict) -> float:
        """Calculate importance based on position in document"""
        page = section.get("page", 1)
        level = section.get("level", "H3")
        
        # Earlier pages are often more important
        page_score = max(0.0, 1.0 - (page - 1) * 0.1)
        
        # Higher level headings are more important
        level_scores = {"H1": 1.0, "H2": 0.8, "H3": 0.6}
        level_score = level_scores.get(level, 0.5)
        
        return (0.6 * page_score + 0.4 * level_score)
    
    def _detect_persona_type(self, persona: str) -> str:
        """Detect the general type of persona"""
        persona_lower = persona.lower()
        
        if any(word in persona_lower for word in ['research', 'phd', 'scientist', 'academic']):
            return 'researcher'
        elif any(word in persona_lower for word in ['analyst', 'investment', 'business', 'finance']):
            return 'analyst'
        elif any(word in persona_lower for word in ['student', 'learn', 'education']):
            return 'student'
        elif any(word in persona_lower for word in ['manager', 'director', 'lead', 'team']):
            return 'manager'
        elif any(word in persona_lower for word in ['engineer', 'developer', 'technical', 'software']):
            return 'engineer'
        else:
            return 'general'
    
    def _generate_reasoning(self, semantic_score: float, keyword_score: float, 
                          quality_score: float, position_score: float) -> str:
        """Generate human-readable reasoning for the score"""
        reasons = []
        
        if semantic_score >= 0.7:
            reasons.append("High semantic similarity to persona requirements")
        elif semantic_score >= 0.5:
            reasons.append("Moderate semantic similarity to persona")
        else:
            reasons.append("Limited semantic alignment with persona")
        
        if keyword_score >= 0.6:
            reasons.append("Strong keyword relevance")
        elif keyword_score >= 0.3:
            reasons.append("Some relevant keywords found")
        
        if quality_score >= 0.7:
            reasons.append("High-quality, well-structured content")
        elif quality_score >= 0.5:
            reasons.append("Good content quality")
        
        if position_score >= 0.7:
            reasons.append("Important position in document")
        
        return "; ".join(reasons) if reasons else "Basic relevance detected"
