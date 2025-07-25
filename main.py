import os
import glob
import time
import json
from ExcludeTableText import extract_text_fast
from pdfScapper import extract_headings
import re


import re

def normalize_text(text):
    # Convert to lowercase
    text = text.lower()
    # Replace multiple spaces/newlines/tabs with a single space
    text = re.sub(r'\s+', ' ', text)
    # Optional: remove punctuation (you can skip this if formatting matters)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()


def process_all_pdfs():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    pdf_results = {}

    for pdf_file in pdf_files:
        filename = os.path.basename(pdf_file)
        try:
            print(f"\n📄 Processing: {filename}")
            start_time = time.time()

            # 1. Extract body text
            body_text = extract_text_fast(pdf_file)

            # 2. Extract outline/headings
            heading_data = extract_headings(pdf_file)
            print("------------------------------Extracted headings :--------------------------------------------- ")
            print(heading_data)
            filtered_outline = []

            # 3. Keep headings only if text exists in body
            for h in heading_data["outline"]:
                if normalize_text(h["text"]) in normalize_text(body_text):
                    filtered_outline.append(h)

            # 4. Validate title exists in text
            final_title = heading_data["title"] 

            end_time = time.time()
            processing_time = end_time - start_time

            # 5. Save result as JSON in output directory
            json_output = {
                "title": final_title,
                "outline": filtered_outline
            }

            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)

            # 6. Also save for internal reference if needed
            pdf_results[filename] = {
                "text": body_text,
                "outline": filtered_outline,
                "title": final_title,
                "processing_time": processing_time,
                "file_path": pdf_file
            }

            print(f"✅ Saved to: {output_path} ({len(filtered_outline)} headings, {len(body_text.split())} words)")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            pdf_results[filename] = {
                "text": "",
                "outline": [],
                "title": final_title,
                "processing_time": 0,
                "file_path": pdf_file,
                "error": str(e)
            }

    return pdf_results

def get_pdf_text(pdf_results, filename):
    """
    Get extracted text for a specific PDF file
    
    Args:
        pdf_results: Dictionary returned by process_all_pdfs()
        filename: Name of the PDF file (e.g., 'file01.pdf')
    
    Returns:
        Extracted text string or None if file not found
    """
    if filename in pdf_results:
        return pdf_results[filename]['text']
    else:
        print(f"File {filename} not found in results")
        return None

def get_pdf_info(pdf_results, filename):
    """
    Get complete information for a specific PDF file
    
    Args:
        pdf_results: Dictionary returned by process_all_pdfs()
        filename: Name of the PDF file (e.g., 'file01.pdf')
    
    Returns:
        Dictionary with text, processing_time, file_path, and optionally error
    """
    if filename in pdf_results:
        return pdf_results[filename]
    else:
        print(f"File {filename} not found in results")
        return None
    


if __name__ == "__main__":
    # Process all PDFs and store results
    process_all_pdfs()
    