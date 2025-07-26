import os
import json
import fitz
import numpy as np
from collections import Counter
import re

from keywords_config import text_contains_exclusion_keywords

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

def assign_heading_level(text, font_size, sorted_unique_sizes, bold_ratio=0, line_height=None, text_freq_map=None):
    text = text.strip()

    # 1. Numeric prefix (e.g. "2.1.1")
    match = re.match(r'^(\d+(?:\.\d+){0,2})[\s\.]', text)
    if match:
        depth = match.group(1).count('.') + 1
        return f'H{min(depth, 3)}'

    # 2. Heuristic scoring for non-numbered
    score = 0
    try:
        idx = sorted_unique_sizes.index(font_size)
        if idx == 0:
            score += 2
        elif idx == 1:
            score += 1
    except ValueError:
        pass

    if bold_ratio > 0.7:
        score += 1
    elif bold_ratio > 0.5:
        score += 0.5

    word_count = len(text.split())
    if word_count <= 4:
        score += 1
    elif word_count >= 10:
        score -= 1

    if text_freq_map and text_freq_map.get(text, 0) == 1:
        score += 1

    if line_height is not None and line_height < 25:
        score += 0.5

    # Final thresholds
    if score >= 3.5:
        return 'H1'
    elif score >= 2.0:
        return 'H2'
    elif score >= 1.0:
        return 'H3'
    return None

def extract_headings(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF {pdf_path}: {e}")
        return {"title": "", "outline": []}

    all_lines = []
    all_sizes = []

    for page_idx, page in enumerate(doc):
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                text = ''.join(span['text'] for span in line['spans']).strip()
                if not text:
                    continue
                bbox = line['bbox']
                font_size = np.mean([span['size'] for span in line['spans']])
                bold_ratio = sum(
                    ('bold' in span.get('font', '').lower()) or (span.get('flags', 0) & 2)
                    for span in line['spans']
                ) / len(line['spans']) if line['spans'] else 0
                all_lines.append({
                    'text': text,
                    'bbox': bbox,
                    'font_size': font_size,
                    'bold_ratio': bold_ratio,
                    'page': page_idx,
                    'y_center': (bbox[1] + bbox[3]) / 2
                })
                all_sizes.append(font_size)

    if not all_lines:
        return {"title": "", "outline": []}

    all_sizes = [s for s in all_sizes if s > 4]
    avg_size = np.mean(all_sizes)
    candidates = [l for l in all_lines if filter_heading_candidate(l['text'], l['font_size'], avg_size, l['bold_ratio'])]

    uniq_sizes = sorted({l['font_size'] for l in candidates}, reverse=True)
    freq_map = Counter(l['text'] for l in all_lines)

    first_numbered = None
    for l in sorted(candidates, key=lambda x: (x['page'], x['y_center'])):
        if re.match(r'^\d+[\s\.]', l['text'].strip()):
            first_numbered = (l['page'], l['y_center'])
            break

    outline = []
    seen = set()
    for l in candidates:
        if first_numbered and (l['page'], l['y_center']) < first_numbered:
            lvl = 'H1'
        else:
            line_h = l['bbox'][3] - l['bbox'][1]
            lvl = assign_heading_level(
                l['text'], l['font_size'], uniq_sizes,
                bold_ratio=l['bold_ratio'],
                line_height=line_h, text_freq_map=freq_map
            )
        if not lvl:
            continue
        key = (lvl, l['text'], l['page'])
        if key in seen:
            continue
        seen.add(key)
        outline.append({'level': lvl, 'text': l['text'], 'page': l['page']})

    title = ''
    for o in outline:
        if o['level'] == 'H1' and o['page'] == 0 and not text_contains_exclusion_keywords(o['text']):
            title = o['text']
            break

    if title and any(k in title.lower() for k in ['form', 'application', 'request', 'declaration']):
        return {'title': title, 'outline': []}

    return {'title': title, 'outline': outline}

def process_all_pdfs(input_dir='input', output_dir='output'):
    os.makedirs(output_dir, exist_ok=True)
    for fn in sorted(os.listdir(input_dir)):
        if not fn.lower().endswith('.pdf'):
            continue
        res = extract_headings(os.path.join(input_dir, fn))
        out = os.path.splitext(fn)[0] + '.json'
        with open(os.path.join(output_dir, out), 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"Processed {fn}, title: '{res['title']}'")

if __name__ == '__main__':
    process_all_pdfs()
