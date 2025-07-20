import os
import json
import sys
import time
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from round1a.pdf_parser import PDFOutlineExtractor
from round1b.document_analyzer import PersonaDrivenAnalyzer

def main():
    # Use local input/output directories for development
    input_dir = Path("./input") if Path("./input").exists() else Path("/app/input")
    output_dir = Path("./output") if Path("./output").exists() else Path("/app/output")
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Processing files from {input_dir}")
    logger.info(f"Output will be saved to {output_dir}")
    
    try:
        # Check if this is Round 1B based on input structure
        if (input_dir / "persona.json").exists():
            logger.info("Detected Round 1B: Persona-driven analysis")
            start_time = time.time()
            
            analyzer = PersonaDrivenAnalyzer()
            result = analyzer.process_directory(input_dir)
            
            with open(output_dir / "analysis_result.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Round 1B completed in {elapsed_time:.2f} seconds")
            
        else:
            logger.info("Detected Round 1A: PDF outline extraction")
            
            extractor = PDFOutlineExtractor()
            
            pdf_files = list(input_dir.glob("*.pdf"))
            if not pdf_files:
                logger.error("No PDF files found in input directory")
                sys.exit(1)
            
            for pdf_file in pdf_files:
                try:
                    start_time = time.time()
                    logger.info(f"Processing {pdf_file.name}")
                    
                    outline = extractor.extract_outline(str(pdf_file))
                    
                    output_file = output_dir / f"{pdf_file.stem}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(outline, f, indent=2, ensure_ascii=False)
                    
                    elapsed_time = time.time() - start_time
                    logger.info(f"Processed {pdf_file.name} in {elapsed_time:.2f} seconds")
                    
                except Exception as e:
                    logger.error(f"Error processing {pdf_file}: {e}")
                    continue
                    
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()