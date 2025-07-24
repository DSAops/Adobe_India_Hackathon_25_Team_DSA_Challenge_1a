import os
import re
import json
import fitz  # PyMuPDF
import numpy as np
from sklearn.cluster import AgglomerativeClustering
import pytesseract
import cv2
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# Import the functions from other files
from ExcludeTableText import extract_text_fast
from lanka import extract_all_headings

def extract_headings_filtered(pdf_path):
    """
    Two-step heading extraction process:
    
    1. Extract ALL potential headings using lanka.py (without any filtering)
    2. Get text outside tables/boxes using ExcludeTableText.py
    3. Filter headings to only include those that exist in the clean text
    4. Write final filtered results to JSON
    """
    print(f"\n=== Processing {pdf_path} ===")
    
    # Step 1: Extract ALL potential headings from lanka.py
    print("Step 1: Extracting all potential headings...")
    all_headings_result = extract_all_headings(pdf_path)
    all_headings = all_headings_result.get("outline", [])
    title = all_headings_result.get("title", "")
    
    print(f"Found {len(all_headings)} potential headings from formatting analysis")
    
    # Step 2: Get clean text (outside tables/boxes) using ExcludeTableText
    print("Step 2: Extracting text outside tables/boxes...")
    excluded_text = extract_text_fast(pdf_path)
    
    # Create a set of clean text lines for fast lookup
    clean_text_lines = set()
    for line in excluded_text.split('\n'):
        line = line.strip()
        if line:
            clean_text_lines.add(line.lower())
    
    print(f"Found {len(clean_text_lines)} lines of clean text outside tables/boxes")
    
    # Step 3: Filter headings - only keep those that exist in clean text
    print("Step 3: Filtering headings against clean text...")
    filtered_headings = []
    filtered_title = ""
    
    # Check title first
    if title and title.lower() in clean_text_lines:
        filtered_title = title
        print(f"✅ Title kept: '{title}'")
    elif title:
        print(f"❌ Title filtered out: '{title}'")
    
    # Check each heading
    for heading in all_headings:
        heading_text = heading["text"]
        if heading_text.lower() in clean_text_lines:
            filtered_headings.append(heading)
            print(f"✅ Heading kept: '{heading_text}' (Level: {heading['level']})")
        else:
            print(f"❌ Heading filtered out: '{heading_text}' (Level: {heading['level']})")
    
    print(f"\nFinal result: {len(filtered_headings)} headings passed the filter")
    
    return {
        "title": filtered_title,
        "outline": filtered_headings,
        "stats": {
            "total_potential_headings": len(all_headings),
            "clean_text_lines": len(clean_text_lines),
            "final_headings": len(filtered_headings)
        }
    }

def process_all_pdfs_filtered(input_dir="input", output_dir="output"):
    """
    Process all PDFs using the two-step filtering approach
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing PDFs from: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    pdf_files = [f for f in sorted(os.listdir(input_dir)) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print("No PDF files found in input directory!")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for fn in pdf_files:
        print(f"\n{'='*60}")
        print(f"Processing: {fn}")
        print(f"{'='*60}")
        
        try:
            # Extract and filter headings
            result = extract_headings_filtered(os.path.join(input_dir, fn))
            
            # Save to JSON
            output_filename = os.path.splitext(fn)[0] + ".json"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # Print summary
            stats = result.get("stats", {})
            print(f"\n📊 Summary for {fn}:")
            print(f"   Title: '{result['title']}'")
            print(f"   Potential headings found: {stats.get('total_potential_headings', 0)}")
            print(f"   Clean text lines: {stats.get('clean_text_lines', 0)}")
            print(f"   Final headings: {stats.get('final_headings', 0)}")
            print(f"   Output saved to: {output_filename}")
            
        except Exception as e:
            print(f"❌ Error processing {fn}: {e}")
            continue
    
    print(f"\n🎉 Processing complete! Check the '{output_dir}' directory for results.")

if __name__ == "__main__":
    process_all_pdfs_filtered()
