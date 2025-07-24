import os
import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import time



def process_page(page):
    # Step 1: Convert PDF page to image
    pix = page.get_pixmap(dpi=150)  # use lower DPI for speed
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 3: Detect rectangular box contours
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 30, 150)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Step 4: Create mask and remove boxed areas
    mask = np.ones(gray.shape, dtype="uint8") * 255
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 50 and h > 30:  # ignore small artifacts
            cv2.rectangle(mask, (x, y), (x + w, y + h), 0, -1)

    # Step 5: Mask out boxes and apply OCR
    unboxed_area = cv2.bitwise_and(gray, gray, mask=mask)
    config = r'--oem 3 --psm 11'  # fast sparse text config
    text = pytesseract.image_to_string(unboxed_area, config=config)

    return text


def extract_text_fast(pdf_path):
    doc = fitz.open(pdf_path)
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(process_page, [doc[i] for i in range(len(doc))])
    return "\n".join(results)


if __name__ == "__main__":
    pdf_path = "input/file05.pdf"

    start = time.time()
    clean_text = extract_text_fast(pdf_path)
    end = time.time()

    print("✅ Time taken: {:.2f} seconds".format(end - start))
    print("\n--- Extracted Text (Outside Boxes) ---\n")
    print(f"Script size: {os.path.getsize('lanka.py') / 1024:.2f} KB")
    for line in clean_text.split('\n'):
        line = line.strip()
        if line:
            print(line)
