

# import os
# import re
# import json
# import fitz  # PyMuPDF
# import numpy as np
# from sklearn.cluster import AgglomerativeClustering

# from keywords_config import (
#     ADDRESS_KEYWORDS,
#     INSTRUCTIONAL_KEYWORDS,
#     DISCLAIMER_KEYWORDS,
#     WEBSITE_PATTERNS
# )

# def text_contains_exclusion_keywords(text):
#     low = text.lower()
#     if any(dk in low for dk in DISCLAIMER_KEYWORDS): return True
#     if any(kw in low for kw in ADDRESS_KEYWORDS): return True
#     if any(kw in low for kw in INSTRUCTIONAL_KEYWORDS): return True
#     for pat in WEBSITE_PATTERNS:
#         if re.search(pat, text, re.IGNORECASE): return True
#     # All-caps long lines are likely not headings
#     if text.isupper() and len(text.split()) > 3: return True
#     return False

# def is_paragraph_like(text):
#     # Heuristic: headings are typically not multi-sentence or full paragraphs
#     words = text.strip().split()
#     if len(words) > 18:
#         return True
#     # Heuristic: more than 2 periods, likely a paragraph
#     if text.count('.') > 1:
#         return True
#     # Heuristic: multi-line text
#     if '\n' in text:
#         return True
#     return False

# def filter_heading_candidate(text, font_size, avg_size, bold_ratio):
#     if not text or not text.strip(): return False
#     if text_contains_exclusion_keywords(text):
#         return False
#     if is_paragraph_like(text):
#         return False
#     # Accept if big/bold relative to average or if text is a reasonable length
#     if font_size > avg_size * 1.10 or bold_ratio >= 0.48:
#         if 2 <= len(text.split()) <= 18:
#             return True
#     # Short/bold uppercase seems like a heading (but not all-caps long)
#     if text.isupper() and len(text.split()) <= 6 and font_size > avg_size:
#         return True
#     return False

# def assign_heading_level(font_size, sorted_unique_sizes):
#     """Assigns H1 for largest size, H2 for next, etc."""
#     try:
#         idx = sorted_unique_sizes.index(font_size)
#         return f'H{min(idx+1,6)}'  # Up to H6 max
#     except ValueError:
#         return 'H6'

# def extract_headings(pdf_path):
#     try:
#         doc = fitz.open(pdf_path)
#     except Exception as e:
#         print(f"Error opening PDF {pdf_path}: {e}")
#         return {"title": "", "outline": []}

#     outline = []
#     used_texts = set()
#     all_sizes = []

#     # Pass 1: collect all text, sizes, candidates
#     all_lines = []
#     for page_idx, page in enumerate(doc):
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             if "lines" not in block:
#                 continue
#             for line in block["lines"]:
#                 text = "".join(span["text"] for span in line["spans"]).strip()
#                 if not text: continue
#                 bbox = line["bbox"]
#                 font_size = np.mean([span["size"] for span in line["spans"]])
#                 bold_ratio = sum(
#                     ("bold" in span.get("font", "").lower()) or
#                     (span.get("flags", 0) & 2) for span in line["spans"]
#                 ) / len(line["spans"]) if line["spans"] else 0
#                 all_lines.append({
#                     "text": text,
#                     "bbox": bbox,
#                     "font_size": font_size,
#                     "bold_ratio": bold_ratio,
#                     "page": page_idx,
#                     "y_center": (bbox[1] + bbox[3]) / 2
#                 })
#                 all_sizes.append(font_size)

#     if not all_lines:
#         return {"title": "", "outline": []}

#     all_sizes = [s for s in all_sizes if s > 4]  # filter out footnote-tiny
#     avg_font_size = np.mean(all_sizes)

#     # Heading candidates: relaxed rules
#     candidates = [
#         l for l in all_lines
#         if filter_heading_candidate(l["text"], l["font_size"], avg_font_size, l["bold_ratio"])
#     ]

#     # Gather unique font sizes (descending)
#     uniq_sizes = sorted(set(l['font_size'] for l in candidates), reverse=True)

#     # Assign heading levels
#     for l in candidates:
#         lvl = assign_heading_level(l["font_size"], uniq_sizes)
#         key = (lvl, l['text'], l['page'])
#         if key not in used_texts:
#             outline.append({"level": lvl, "text": l["text"], "page": l["page"]})
#             used_texts.add(key)

#     # Heuristic for selecting title
#     title = ""
#     if outline:
#         # Only promote H1 at the document top
#         title_candidates = [
#             o for o in outline[:3]
#             if o["level"] == "H1" and o["page"] == 0
#             and not text_contains_exclusion_keywords(o["text"])
#         ]
#         if title_candidates:
#             title = title_candidates[0]["text"]
#         else:
#             # fallback: most prominent on first page
#             first_page_outlines = [o for o in outline if o['page'] == 0]
#             if first_page_outlines:
#                 # Largest font used as title
#                 first_page_outlines.sort(key=lambda o: -uniq_sizes.index(all_lines[all_lines.index(next(l for l in all_lines if l['text'] == o['text']))]['font_size']))
#                 title = first_page_outlines[0]['text']
#     # Disallow certain "titles"
#     if title and any(k in title.lower() for k in ["form", "application", "request", "declaration"]):
#         return {"title": title, "outline": []}

#     # Dedupe outline for repeated headings
#     final = []
#     seen = set()
#     for h in outline:
#         key = (h['level'], h['text'], h['page'])
#         if key not in seen:
#             final.append(h)
#             seen.add(key)
#     return {"title": title, "outline": final}

# def process_all_pdfs(input_dir="input", output_dir="output"):
#     os.makedirs(output_dir, exist_ok=True)
#     for fn in sorted(os.listdir(input_dir)):
#         if not fn.lower().endswith(".pdf"):
#             continue
#         res = extract_headings(os.path.join(input_dir, fn))
#         out = os.path.splitext(fn)[0] + ".json"
#         with open(os.path.join(output_dir, out), 'w', encoding='utf-8') as f:
#             json.dump(res, f, ensure_ascii=False, indent=2)
#         print(f"Processed {fn}, title: '{res['title']}'")

# if __name__ == "__main__":
#     process_all_pdfs()

import os
import re
import json
import fitz  # PyMuPDF
import numpy as np
from sklearn.cluster import AgglomerativeClustering

from keywords_config import (
    ADDRESS_KEYWORDS,
    INSTRUCTIONAL_KEYWORDS,
    DISCLAIMER_KEYWORDS,
    WEBSITE_PATTERNS
)

def text_contains_exclusion_keywords(text):
    low = text.lower()
    if any(dk in low for dk in DISCLAIMER_KEYWORDS): return True
    if any(kw in low for kw in ADDRESS_KEYWORDS): return True
    if any(kw in low for kw in INSTRUCTIONAL_KEYWORDS): return True
    for pat in WEBSITE_PATTERNS:
        if re.search(pat, text, re.IGNORECASE): return True
    if text.isupper() and len(text.split()) > 3: return True
    return False

def is_paragraph_like(text):
    words = text.strip().split()
    if len(words) > 18: return True
    if text.count('.') > 1: return True
    if '\n' in text: return True
    return False

def filter_heading_candidate(text, font_size, avg_size, bold_ratio):
    if not text or not text.strip(): return False
    if text_contains_exclusion_keywords(text): return False
    if is_paragraph_like(text): return False
    if font_size > avg_size * 1.10 or bold_ratio >= 0.48:
        if 2 <= len(text.split()) <= 18:
            return True
    if text.isupper() and len(text.split()) <= 6 and font_size > avg_size:
        return True
    return False

def assign_heading_level(text, font_size, sorted_unique_sizes):
    """
    Assign H1, H2, H3 based on prefix (like '2.1.1') if available, else use font size rank.
    """
    match = re.match(r'^(\d+(?:\.\d+){0,2})[\s\.]', text.strip())
    if match:
        depth = match.group(1).count('.') + 1
        if 1 <= depth <= 3:
            return f'H{depth}'
        return None
    try:
        idx = sorted_unique_sizes.index(font_size)
        if idx < 3:
            return f'H{idx+1}'
    except ValueError:
        pass
    return None

def extract_headings(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF {pdf_path}: {e}")
        return {"title": "", "outline": []}

    outline = []
    used_texts = set()
    all_sizes = []
    all_lines = []

    for page_idx, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = "".join(span["text"] for span in line["spans"]).strip()
                if not text:
                    continue
                bbox = line["bbox"]
                font_size = np.mean([span["size"] for span in line["spans"]])
                bold_ratio = sum(
                    ("bold" in span.get("font", "").lower()) or
                    (span.get("flags", 0) & 2) for span in line["spans"]
                ) / len(line["spans"]) if line["spans"] else 0
                all_lines.append({
                    "text": text,
                    "bbox": bbox,
                    "font_size": font_size,
                    "bold_ratio": bold_ratio,
                    "page": page_idx,
                    "y_center": (bbox[1] + bbox[3]) / 2
                })
                all_sizes.append(font_size)

    if not all_lines:
        return {"title": "", "outline": []}

    all_sizes = [s for s in all_sizes if s > 4]
    avg_font_size = np.mean(all_sizes)

    candidates = [
        l for l in all_lines
        if filter_heading_candidate(l["text"], l["font_size"], avg_font_size, l["bold_ratio"])
    ]

    uniq_sizes = sorted(set(l['font_size'] for l in candidates), reverse=True)

    for l in candidates:
        lvl = assign_heading_level(l["text"], l["font_size"], uniq_sizes)
        if lvl is None:
            continue
        key = (lvl, l['text'], l['page'])
        if key not in used_texts:
            outline.append({"level": lvl, "text": l["text"], "page": l["page"]})
            used_texts.add(key)

    # Title detection
    title = ""
    if outline:
        title_candidates = [
            o for o in outline[:3]
            if o["level"] == "H1" and o["page"] == 0 and not text_contains_exclusion_keywords(o["text"])
        ]
        if title_candidates:
            title = title_candidates[0]["text"]
        else:
            first_page_outlines = [o for o in outline if o['page'] == 0]
            if first_page_outlines:
                first_page_outlines.sort(
                    key=lambda o: -uniq_sizes.index(
                        next(l for l in all_lines if l['text'] == o['text'])['font_size']
                    )
                )
                title = first_page_outlines[0]['text']

    if title and any(k in title.lower() for k in ["form", "application", "request", "declaration"]):
        return {"title": title, "outline": []}

    # Deduplication
    final = []
    seen = set()
    for h in outline:
        key = (h['level'], h['text'], h['page'])
        if key not in seen:
            final.append(h)
            seen.add(key)

    return {"title": title, "outline": final}

def process_all_pdfs(input_dir="input", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    for fn in sorted(os.listdir(input_dir)):
        if not fn.lower().endswith(".pdf"):
            continue
        res = extract_headings(os.path.join(input_dir, fn))
        out = os.path.splitext(fn)[0] + ".json"
        with open(os.path.join(output_dir, out), 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"Processed {fn}, title: '{res['title']}'")

if __name__ == "__main__":
    process_all_pdfs()

