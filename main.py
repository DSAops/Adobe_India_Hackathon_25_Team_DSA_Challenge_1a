import os
import fitz  # PyMuPDF

def describe_pdf_pages(input_dir='input'):
    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(".pdf"):
            continue
        path = os.path.join(input_dir, filename)
        try:
            doc = fitz.open(path)
        except Exception as e:
            print(f"Could not open {filename}: {e}")
            continue
        print(f"PDF: {filename}")
        for page_num, page in enumerate(doc, 1):
            text = page.get_text("text").strip()
            images = page.get_images(full=True)
            img_count = len(images)
            has_text = len(text) > 20  # tweak as needed for noise
            # Classification logic
            if img_count > 0 and not has_text:
                page_type = "image"
            elif img_count > 0 and has_text:
                page_type = "image and text"
            elif has_text:
                page_type = "text"
            else:
                page_type = "blank or unclassified"
            print(f"  Page {page_num}: {page_type}")

# Main execution
if __name__ == "__main__":
    describe_pdf_pages()
