import os
import re
import json
import fitz  # PyMuPDF
import numpy as np
from sklearn.cluster import AgglomerativeClustering

# Keywords/patterns to exclude from headings
ADDRESS_KEYWORDS = [
    "street", "st.", "road", "rd.", "avenue", "ave.", "circle", "blvd",
    "lane", "ln.", "p.o.", "po box", "apartment", "suite", "district",
    "city", "village", "state", "country", "zip", "pin", "code", "parkway",
    "drive", "dr.", "court", "ct.", "plaza", "place", "way", "highway"
]

WEBSITE_PATTERNS = [
    r"http[s]?://", r"www\.", r"\.com", r"\.org", r"\.net", r"\.edu",
    r"mailto:", r"\@\w+", r"\.gov", r"\.info"
]

INSTRUCTIONAL_PATTERNS = [
    r"please\s+\w+", r"must\s+\w+", r"required\s+\w+", r"should\s+\w+",
    r"do\s+not", r"cannot\s+\w+", r"will\s+not", r"need\s+to"
]

DISCLAIMER_KEYWORDS = [
    "disclaimer", "terms and conditions", "notice", "important", "please note"
]


def is_rect_overlap(r1, r2):
    """Check if two rectangles overlap. Rect: (x0,y0,x1,y1)"""
    x0_1, y0_1, x1_1, y1_1 = r1
    x0_2, y0_2, x1_2, y1_2 = r2
    return not (x1_1 <= x0_2 or x1_2 <= x0_1 or y1_1 <= y0_2 or y1_2 <= y0_1)


def get_form_widget_rects(page):
    """Return list of rectangles occupied by form fields."""
    widgets = page.widgets() or []
    return [w.rect for w in widgets if w.rect is not None]


def get_table_block_rects(page):
    """Return list of rectangles approximating tables using block density heuristics."""
    rects = []
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if b["type"] != 0:  # Ignore non-text
            continue
        lines = b.get("lines", [])
        if len(lines) < 5:
            continue
        avg_spans = sum(len(l.get("spans", [])) for l in lines) / len(lines)
        if avg_spans >= 3:  # heuristic threshold for table-like block
            rects.append(b["bbox"])
    return rects


def is_in_any_rect(rect, rect_list):
    """Check if rect overlaps any rectangle in rect_list."""
    for r in rect_list:
        if is_rect_overlap(rect, r):
            return True
    return False


def filter_heading_candidate(text):
    """
    Return True if text is a valid heading candidate.

    Accepts short, expressive lines (e.g. with '!' or mixed case),
    filters out addresses, disclaimers, paragraphs, website links,
    names, labels, and instructions.
    """

    # Normalize spaces and strip trailing punctuations (except '!' at end)
    line = re.sub(r'\s+', ' ', text).strip()
    # Keep exclamation if present
    if line.endswith('!'):
        line = line.rstrip(",.;:- ") + '!'
    else:
        line = line.rstrip(",.;:- ")

    if not line:
        return False

    low = line.lower()

    # Exclude disclaimers explicitly
    if any(d in low for d in DISCLAIMER_KEYWORDS):
        return False

    # Exclude lines with website/email
    for pat in WEBSITE_PATTERNS:
        if re.search(pat, line, re.IGNORECASE):
            return False

    # Exclude address keywords
    if any(kw in low for kw in ADDRESS_KEYWORDS):
        return False

    # Exclude phone number patterns
    if re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", line):
        return False

    # Accept lines ending with exclamation if short and multiple words
    if line.endswith('!') and len(line) <= 60 and len(line.split()) >= 2:
        return True

    # Reject single word lines unless numbered
    if len(line.split()) < 2 and not re.match(r"^\d+[\.\)]", line):
        return False

    # Reject personal names (2-3 capitalization pattern)
    if re.match(r"^[A-Z][a-z]+\s[A-Z][a-z]+(\s[A-Z][a-z]+)?$", line):
        return False

    # Reject paragraphs: lines longer than 80 chars with periods
    if len(line) > 80 and '.' in line:
        return False

    # Reject TOC style lines (text + dots + page number)
    if re.match(r".{1,40}\s+\.{2,}\s*\d+$", line):
        return False

    # Accept reasonable short lines with multiple words
    if len(line.split()) >= 2 and len(line) <= 60:
        return True

    return False


def extract_headings(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to open {pdf_path}: {e}")
        return []

    candidate_lines = []
    font_sizes = []
    font_weights = []  # 1 if bold, else 0 -- PyMuPDF may not have direct bold flag but can check font flags
    # We will approximate bold by checking font names containing 'Bold'

    for page_number, page in enumerate(doc):
        form_rects = get_form_widget_rects(page)
        table_rects = get_table_block_rects(page)
        ignore_rects = form_rects + table_rects

        page_dict = page.get_text("dict")
        for block in page_dict["blocks"]:
            if block["type"] != 0:
                continue
            if is_in_any_rect(block["bbox"], ignore_rects):
                continue
            if "lines" not in block:
                continue
            for line in block["lines"]:
                if is_in_any_rect(line["bbox"], ignore_rects):
                    continue

                line_text = "".join([span["text"] for span in line["spans"]]).strip()
                if not filter_heading_candidate(line_text):
                    continue

                # Compute average font size for line
                sizes = np.array([span["size"] for span in line["spans"]])
                avg_size = sizes.mean()

                # Approximate font weight: check if font name or flags indicate bold (simple heuristic)
                bold_count = 0
                for span in line["spans"]:
                    font_name = span.get("font", "").lower()
                    flags = span.get("flags", 0)
                    # Check if font name contains 'bold' or flag bit 1 (bold) is set
                    bold_count += ("bold" in font_name) or (flags & 2 != 0)
                bold_ratio = bold_count / len(line["spans"]) if line["spans"] else 0

                candidate_lines.append({
                    "text": line_text,
                    "page": page_number,
                    "font_size": avg_size,
                    "bold_ratio": bold_ratio,
                    "line_bbox": line["bbox"],
                })
                font_sizes.append(avg_size)
                font_weights.append(bold_ratio)

    if not candidate_lines:
        return []

    # Feature vector: font size and bold ratio (scaled)
    sizes_np = np.array(font_sizes).reshape(-1, 1)
    weights_np = np.array(font_weights).reshape(-1, 1)
    features = np.hstack([sizes_np, weights_np])

    # Cluster into 3 groups (H1, H2, H3 or fewer)
    n_clusters = min(3, len(np.unique(font_sizes)))
    if n_clusters <= 1:
        # Single cluster, assign all as H1
        return [{
            "level": "H1",
            "text": line["text"],
            "page": line["page"]
        } for line in candidate_lines]

    clustering = AgglomerativeClustering(n_clusters=n_clusters).fit(features)

    # Sort clusters by mean font size + boldness
    cluster_scores = []
    for cid in range(n_clusters):
        mask = clustering.labels_ == cid
        mean_size = sizes_np[mask].mean()
        mean_bold = weights_np[mask].mean()
        score = mean_size + mean_bold  # simple sum score to rank prominence
        cluster_scores.append((cid, score))
    cluster_scores.sort(key=lambda x: x[1], reverse=True)

    cluster_to_level = {cid: f"H{i+1}" for i, (cid, _) in enumerate(cluster_scores)}

    # Boost lines ending with '!' to H1
    outline = []
    for idx, line in enumerate(candidate_lines):
        assigned_level = cluster_to_level[clustering.labels_[idx]]
        if line["text"].strip().endswith('!'):
            assigned_level = "H1"
        outline.append({
            "level": assigned_level,
            "text": line["text"],
            "page": line["page"]
        })

    return outline


def extract_title(outline, pdf_path):
    # Prefer first H1 heading as title
    for item in outline:
        if item["level"] == "H1":
            return item["text"]
    # Else derive from file name
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    return base_name.replace('_', ' ').replace('-', ' ').strip()


def process_all_pdfs(input_dir="input", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    for filename in sorted(os.listdir(input_dir)):
        if not filename.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(input_dir, filename)
        print(f"Processing: {filename} ...")
        outline = extract_headings(pdf_path)
        title = extract_title(outline, pdf_path)
        result = {
            "title": title,
            "outline": outline
        }
        out_file = os.path.splitext(filename)[0] + ".json"
        out_path = os.path.join(output_dir, out_file)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Extracted {len(outline)} headings, title: {title}\n")


if __name__ == "__main__":
    process_all_pdfs()
