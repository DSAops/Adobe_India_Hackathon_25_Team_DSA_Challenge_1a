## 10. round1b/document_analyzer.py
```python
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import time

from .persona_matcher import PersonaMatcher
from .content_extractor import ContentExtractor
from .relevance_scorer import RelevanceScorer
from round1a.pdf_parser import PDFOutlineExtractor

logger = logging.getLogger(__name__)

class PersonaDrivenAnalyzer:
    def __init__(self):
        self.pdf_extractor = PDFOutlineExtractor()
        self.content_extractor = ContentExtractor()
        self.persona_matcher = PersonaMatcher()
        self.relevance_scorer = RelevanceScorer()
        
    def process_directory(self, input_dir: Path) -> Dict[str, Any]:
        """Process all PDFs in directory with persona-driven analysis"""
        start_time = time.time()
        
        # Load persona and job description
        persona_data = self.load_persona_data(input_dir)
        
        # Find all PDFs
        pdf_files = list(input_dir.glob("*.pdf"))
        if not pdf_files:
            logger.error("No PDF files found")
            return {"error": "No PDF files found"}
        
        logger.info(f"Processing {len(pdf_files)} PDFs with persona analysis")
        
        # Process all documents
        documents = []
        for pdf_file in pdf_files:
            try:
                doc_data = self.process_single_document(pdf_file, persona_data)
                documents.append(doc_data)
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
                continue
        
        if not documents:
            return {"error": "No documents could be processed"}
        
        # Perform cross-document analysis
        analysis_result = self.analyze_documents(documents, persona_data)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Analysis completed in {elapsed_time:.2f} seconds")
        
        return analysis_result
    
    def load_persona_data(self, input_dir: Path) -> Dict[str, Any]:
        """Load persona and job description from JSON file"""
        persona_file = input_dir / "persona.json"
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading persona data: {e}")
            return {
                "persona": "General Analyst",
                "job_description": "Analyze documents for key insights"
            }
    
    def process_single_document(self, pdf_file: Path, persona_data: Dict) -> Dict[str, Any]:
        """Process a single PDF document"""
        logger.info(f"Processing document: {pdf_file.name}")
        
        # Extract outline structure
        outline_data = self.pdf_extractor.extract_outline(str(pdf_file))
        
        # Extract content sections
        sections = self.content_extractor.extract_sections(str(pdf_file), outline_data)
        
        # Calculate relevance scores for each section
        scored_sections = self.relevance_scorer.score_sections(
            sections, persona_data
        )
        
        return {
            "filename": pdf_file.name,
            "title": outline_data.get("title", ""),
            "outline": outline_data.get("outline", []),
            "sections": scored_sections
        }
    
    def analyze_documents(self, documents: List[Dict], persona_data: Dict) -> Dict[str, Any]:
        """Perform comprehensive analysis across all documents"""
        # Collect all sections across documents
        all_sections = []
        for doc in documents:
            for section in doc["sections"]:
                section["source_document"] = doc["filename"]
                all_sections.append(section)
        
        # Sort by relevance score
        all_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Take top sections (customize based on requirements)
        top_sections = all_sections[:20]  # Top 20 most relevant sections
        
        # Group by relevance tiers
        high_relevance = [s for s in all_sections if s["relevance_score"] >= 0.7]
        medium_relevance = [s for s in all_sections if 0.4 <= s["relevance_score"] < 0.7]
        
        # Extract refined subsections from top sections
        refined_subsections = []
        for section in top_sections[:10]:  # Refine top 10 sections
            subsections = self.content_extractor.extract_subsections(
                section["content"], persona_data
            )
            refined_subsections.extend(subsections)
        
        # Generate summary insights
        insights = self.generate_insights(documents, top_sections, persona_data)
        
        return {
            "persona": persona_data.get("persona", ""),
            "job_description": persona_data.get("job_description", ""),
            "documents_processed": len(documents),
            "total_sections_analyzed": len(all_sections),
            "insights": insights,
            "top_relevant_sections": [
                {
                    "source_document": section["source_document"],
                    "title": section["title"],
                    "content_preview": section["content"][:300] + "..." if len(section["content"]) > 300 else section["content"],
                    "relevance_score": round(section["relevance_score"], 3),
                    "page": section.get("page", 1),
                    "reasoning": section.get("reasoning", "")
                }
                for section in top_sections
            ],
            "high_relevance_count": len(high_relevance),
            "medium_relevance_count": len(medium_relevance),
            "refined_subsections": refined_subsections[:15]  # Top 15 refined subsections
        }
    
    def generate_insights(self, documents: List[Dict], top_sections: List[Dict], 
                         persona_data: Dict) -> Dict[str, Any]:
        """Generate key insights for the persona"""
        insights = {
            "key_themes": [],
            "cross_document_connections": [],
            "persona_specific_findings": []
        }
        
        # Extract key themes from top sections
        themes = self.extract_themes(top_sections)
        insights["key_themes"] = themes[:5]  # Top 5 themes
        
        # Find connections between documents
        connections = self.find_cross_document_connections(documents, top_sections)
        insights["cross_document_connections"] = connections[:3]  # Top 3 connections
        
        # Generate persona-specific findings
        findings = self.generate_persona_findings(top_sections, persona_data)
        insights["persona_specific_findings"] = findings[:5]  # Top 5 findings
        
        return insights
    
    def extract_themes(self, sections: List[Dict]) -> List[str]:
        """Extract common themes from top sections"""
        # Simple keyword-based theme extraction
        from collections import Counter
        import re
        
        all_text = " ".join([section["content"] for section in sections])
        
        # Extract potential theme keywords (simple approach)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text.lower())
        word_counts = Counter(words)
        
        # Filter out common words and get themes
        stop_words = {'this', 'that', 'with', 'from', 'they', 'been', 'have', 'were', 
                     'said', 'each', 'which', 'their', 'time', 'will', 'about', 'would', 
                     'there', 'could', 'other', 'after', 'first', 'well', 'many', 'must',
                     'through', 'back', 'years', 'where', 'much', 'should', 'work'}
        
        themes = [word for word, count in word_counts.most_common(20) 
                 if word not in stop_words and count > 2]
        
        return themes[:10]
    
    def find_cross_document_connections(self, documents: List[Dict], 
                                      sections: List[Dict]) -> List[Dict]:
        """Find connections between documents"""
        connections = []
        
        # Simple approach: find sections with similar themes from different documents
        doc_sections = {}
        for section in sections[:10]:  # Top 10 sections
            doc = section["source_document"]
            if doc not in doc_sections:
                doc_sections[doc] = []
            doc_sections[doc].append(section)
        
        # Find documents that share similar high-relevance content
        if len(doc_sections) > 1:
            docs = list(doc_sections.keys())
            for i in range(len(docs)):
                for j in range(i + 1, len(docs)):
                    doc1, doc2 = docs[i], docs[j]
                    connection = {
                        "document_1": doc1,
                        "document_2": doc2,
                        "connection_type": "Shared high-relevance themes",
                        "strength": 0.8  # Simplified scoring
                    }
                    connections.append(connection)
        
        return connections
    
    def generate_persona_findings(self, sections: List[Dict], 
                                persona_data: Dict) -> List[str]:
        """Generate persona-specific findings"""
        persona = persona_data.get("persona", "")
        job = persona_data.get("job_description", "")
        
        findings = []
        
        # Generate findings based on top
        def generate_persona_findings(self, sections: List[Dict], persona_data: Dict) -> List[str]:
            """
            Generate persona-specific findings
            """
            persona = persona_data.get("persona", "")
            job = persona_data.get("job_description", "")

            findings = []

            for section in sections:
                content = section["content"]
                reasoning = section.get("reasoning", "")
                score = section.get("relevance_score", 0)

                # Simple logic to relate section content with persona/job
                if score >= 0.6:
                    finding = f"As a {persona}, the section titled '{section.get('title', '')}' is relevant due to its focus on {reasoning or 'core subject matter'}."
                    findings.append(finding)
                elif score >= 0.4:
                    finding = f"The section '{section.get('title', '')}' might be useful for a {persona}, especially in the context of '{job}'."
                    findings.append(finding)

            if not findings:
                findings.append(f"No strong persona-specific findings could be generated based on the provided documents and job description.")

            return findings
        
            for section in sections:
                content = section["content"]
                reasoning = section.get("reasoning", "")
                score = section.get("relevance_score", 0)

                # Simple logic to relate section content with persona/job
                if score >= 0.6:
                    finding = f"As a {persona}, the section titled '{section.get('title', '')}' is relevant due to its focus on {reasoning or 'core subject matter'}."
                    findings.append(finding)
                elif score >= 0.4:
                    finding = f"The section '{section.get('title', '')}' might be useful for a {persona}, especially in the context of '{job}'."
                    findings.append(finding)
        
            if not findings:
                findings.append(f"No strong persona-specific findings could be generated based on the provided documents and job description.")

            return findings
