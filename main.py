# import os
# import fitz  # PyMuPDF

# def describe_pdf_pages(input_dir='input'):
#     for filename in os.listdir(input_dir):
#         if not filename.lower().endswith(".pdf"):
#             continue
#         path = os.path.join(input_dir, filename)
#         try:
#             doc = fitz.open(path)
#         except Exception as e:
#             print(f"Could not open {filename}: {e}")
#             continue
#         print(f"PDF: {filename}")
#         for page_num, page in enumerate(doc, 1):
#             text = page.get_text("text").strip()
#             images = page.get_images(full=True)
#             img_count = len(images)
#             has_text = len(text) > 20  # tweak as needed for noise
#             # Classification logic
#             if img_count > 0 and not has_text:
#                 page_type = "image"
#             elif img_count > 0 and has_text:
#                 page_type = "image and text"
#             elif has_text:
#                 page_type = "text"
#             else:
#                 page_type = "blank or unclassified"
#             print(f"  Page {page_num}: {page_type}")

# # Main execution
# if __name__ == "__main__":
#     describe_pdf_pages()


import os
import fitz  # PyMuPDF

def extract_text_blocks_from_pdf(input_dir='input'):
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
            print(f"  Page {page_num}:")
            blocks = page.get_text("blocks")
            # Optionally, also get lines/dicts for finer structure
            # lines = page.get_text("dict")["blocks"]
            for i, block in enumerate(blocks):
                x0, y0, x1, y1, text, block_type, _ = block  # block_type: 0=text, 1=image
                width = x1 - x0
                height = y1 - y0
                if block_type == 0 and len(text.strip()) > 0:
                    # Use heuristics to identify: block within form/table/box
                    # For example: if width> certain threshold & height> threshold, likely a "block" or "form"
                    print(f"    Block {i+1}: Bounds=({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}) - '{text.strip()[:60]}'")
            # To further detect table structure, you'd cluster nearby blocks into rows/columns

if __name__ == "__main__":
    extract_text_blocks_from_pdf()
