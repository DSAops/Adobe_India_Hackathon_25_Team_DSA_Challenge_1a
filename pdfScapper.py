import os
import re
import json
import fitz  # PyMuPDF
import numpy as np
from sklearn.cluster import AgglomerativeClustering

# -- ALL YOUR KEYWORD LISTS --
ADDRESS_KEYWORDS = [
    "street", "st.", "road", "rd.", "avenue", "ave.", "circle", "blvd",
    "lane", "ln.", "p.o.", "po box", "apartment", "suite", "district",
    "city", "village", "state", "country", "zip", "pin", "code",
    "parkway", "drive", "dr.", "court", "ct.", "plaza", "place",
    "way", "highway", "address", "rsvp", "date", "time", "party",
    "phone", "contact", "3735", "pigeon forge", "dixie stampede",
    "route", "rt.", "junction", "jct.", "esplanade", "sq.", "square",
    "terrace", "terr.", "bldg.", "building", "floor", "unit", "apt.",
    "block", "lot", "sector", "ward", "zone", "region", "borough",
    "precinct", "parish", "county", "township", "municipal", "town",
    "hamlet", "settlement", "colony", "locality", "postal", "postcode",
    "postal code", "mailstop", "ms.", "parcel", "lot no.", "dp.", "distr.",
    "division", "village council", "tehsil", "taluka", "mohalla",
    "panchayat", "mandal", "subdistrict", "landmark", "near", "beside",
    "opposite", "adjacent", "corner of", "intersection", "crossroad",
    "mile marker", "milepost", "highway exit", "exit no.", "km marker",
    "km post", "latitude", "longitude", "gps", "coordinates", "geo.",
    "geocode", "zone code", "section", "drawing", "grid", "atlas",
    "cantonment", "gated community", "estate", "residential", "commercial",
    "industrial", "business park", "campus", "station", "terminal",
    "airport", "harbor", "wharf", "dock", "pier", "marina", "ranch",
    "farm", "lottery", "compound", "resort", "hotel", "inn", "motel",
    "casino", "theatre", "stadium", "arena", "park", "garden",
    "cemetery", "sanctuary", "preserve", "forest", "reserve", "beltway"
]

INSTRUCTIONAL_KEYWORDS = [
    "please", "must", "required", "should", "do not", "cannot", "will not",
    "need to", "parents or guardians", "visit", "fill out", "waiver", "rsvp",
    "ticket", "registration", "sign up", "sign up for", "join", "participate", "login", "login for",
    "mandatory", "recommended", "optional", "not allowed", "prohibited",
    "forbidden", "ensure that", "make sure", "verify", "confirm",
    "register", "registration", "sign in", "sign out", "check in",
    "check-in", "check-out", "present", "presentation", "bring", "carry",
    "provide", "supply", "under no circumstances", "only if", "unless",
    "before you", "after you", "during", "throughout", "upon arrival",
    "upon completion", "you must", "you should", "it is advisable",
    "it is recommended", "attendance", "attendance is", "supervised by",
    "with adult supervision", "parental consent", "guardian signature",
    "legal guardian", "medical form", "health form", "emergency contact",
    "first aid", "safety gear", "safety equipment", "protective gear",
    "hard hat", "vest", "goggles", "helmet", "registration fee",
    "processing fee", "late fee", "deadline", "due by", "cut-off date",
    "starting at", "beginning at", "ending at", "concludes at", "open at",
    "close at", "shut at", "doors open", "doors close", "gates open",
    "gates close", "acuity", "prerequisite", "pre-requisite", "qualification",
    "credential", "documentation", "cover letter", "resume", "cv",
    "portfolio", "application", "apply", "submission", "submitted",
    "upload", "download", "collect", "pick up", "drop off", "collectibles",
    "drop-offs", "pickup", "route", "itinerary", "agenda", "schedule",
    "timeline", "agenda items", "briefing", "orientation", "tour", "walk-through"
]

DISCLAIMER_KEYWORDS = [
    "disclaimer", "terms and conditions", "notice", "important", "please note",
    "legal notice", "liability", "liability waiver", "release", "hold harmless",
    "indemnity", "indemnification", "privacy", "privacy policy", "cookie policy",
    "confidential", "confidentiality", "non-disclosure", "nda", "copyright",
    "trademark", "patent", "intellectual property", "ip", "all rights reserved",
    "subject to change", "without notice", "at your own risk", "as is",
    "as available", "no warranty", "no guarantee", "no endorsement",
    "third party", "third-party", "external", "external link", "link to",
    "affiliated", "affiliation", "sponsorship", "sponsor", "advertisement",
    "ad", "advert", "promo", "promotion", "advertising", "advice",
    "recommendation", "not professional", "not a substitute", "consult a professional",
    "medical advice", "financial advice", "legal advice", "consultation",
    "consult a doctor", "consult an attorney", "consult a lawyer",
    "risk factors", "side effects", "caution", "warning", "alert",
    "attention", "be aware", "be advised", "this product", "this service",
    "use at your own risk", "under no circumstances", "no liability",
    "no responsibility", "not liable", "not responsible", "the company",
    "the organization", "the event organizers", "safety instructions",
    "subject to availability", "inventory", "stock", "out of stock",
    "backorder", "cancellation policy", "refund policy", "return policy",
    "exchange policy", "breach", "arbitration", "jurisdiction",
    "governing law", "severability", "entire agreement", "amendment",
    "modification", "update"
]

WEBSITE_PATTERNS = [
    r"http[s]?://", r"www\.", r"\.com", r"\.org", r"\.net",
    r"mailto:", r"@\w+", r"\.gov", r"\.info",
    r"\.edu", r"\.io", r"\.co", r"\.us", r"\.uk", r"\.ca", r"\.au", r"\.de",
    r"\.jp", r"\.fr", r"\.ru", r"\.ch", r"\.it", r"\.nl", r"\.se", r"\.no",
    r"\.es", r"\.cz", r"\.in", r"\.br", r"\.mx", r"\.ar", r"\.za", r"\.kr",
    r"\.hk", r"\.sg", r"\.nz", r"\.be", r"\.at", r"\.dk", r"\.fi", r"\.pl",
    r"\.pt", r"\.gr", r"\.tr", r"\.il", r"\.sa", r"\.ae", r"\.cl", r"\.co\.uk",
    r"\.ac", r"\.museum", r"\.pro", r"\.biz", r"\.tv", r"\.info", r"\.int",
    r"\.mil", r"\.arpa", r"\.xxx", r"https?://[\w\-\.]+\.\w{2,}",
    r"ftp://", r"sftp://", r"scp://", r"ssh://", r"\.ly", r"\.am",
    r"\.fm", r"\.la", r"\.me", r"\.name", r"\.password", r"\.io/",
    r"\.ai", r"\.app", r"\.dev", r"\.cloud", r"\.shop", r"\.store", r"\.blog",
    r"\.news", r"\.live", r"\.games", r"\.mobile", r"\.online",
    r"\.site", r"\.tech", r"\.website", r"\.world", r"\.space",
    r"\.network", r"\.systems", r"\.solutions", r"\.services", r"\.center",
    r"\.agency", r"\.company", r"\.group", r"\.industries", r"\.ventures",
    r"\.capital", r"\.partners", r"\.studio", r"\.digital", r"\.expert",
    r"\.education", r"\.ltd", r"\.plc", r"\.inc", r"\.corp", r"\.org.uk",
    r"@[\w\.-]+\.\w{2,}"
]
# =================================================================

# Text exclusion and heading filtering

def text_contains_exclusion_keywords(text):
    low = text.lower()
    if any(dk in low for dk in DISCLAIMER_KEYWORDS): return True
    if any(kw in low for kw in ADDRESS_KEYWORDS): return True
    if any(kw in low for kw in INSTRUCTIONAL_KEYWORDS): return True
    for pat in WEBSITE_PATTERNS:
        if re.search(pat, text, re.IGNORECASE): return True
    if text.isupper() and len(text.split())>3: return True
    return False

def filter_heading_candidate(text, font_size, bold_ratio):
    if not text or not text.strip(): return False
    if text_contains_exclusion_keywords(text): return False
    if len(text)>100: return False
    if re.match(r"^\d+\.?$", text.strip()): return False
    if len(text.split())==1 and (font_size<14 or bold_ratio<0.8): return False
    if re.match(r"^(name|age|address|date|signature)$", text.lower().strip()): return False
    if re.search(r"\d{2,}[\./:-]", text): return False
    if re.search(r"(table|figure)\s*\d+", text.lower()): return False
    if len(text.split())<3 and font_size<16: return False
    if text.lower().startswith(("i declare","i certify","signature of")): return False
    return True

# Main extraction
def extract_headings(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF {pdf_path}: {e}")
        return {"title":"","outline":[]}
    outline=[]
    for page_idx, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        lines=[]
        for block in blocks:
            if"lines"not in block:continue
            for line in block["lines"]:
                text="".join(span["text"]for span in line["spans"]).strip()
                bbox=line["bbox"]
                font_size=np.mean([span["size"]for span in line["spans"]])
                bold_ratio=sum(("bold"in span.get("font","").lower())or(span.get("flags",0)&2)for span in line["spans"])/len(line["spans"]) if line["spans"] else 0
                lines.append({"text":text,"bbox":bbox,"font_size":font_size,"bold_ratio":bold_ratio,"page":page_idx,"y_center":(bbox[1]+bbox[3])/2})
        if not lines:continue
        height=page.rect.height
        # Title
        tops=[l for l in lines if not text_contains_exclusion_keywords(l["text"]) and l["y_center"]<height*0.15 and l["font_size"]>14 and len(l["text"].split())>=3]
        if not tops:
            tops=[l for l in lines if l["y_center"]<height*0.25 and l["font_size"]>12 and len(l["text"].split())>=4]
        if tops:
            best=sorted(tops,key=lambda l:(-l["font_size"],-l["bold_ratio"],l["y_center"]))[0]
            outline.append({"level":"H1","text":best["text"],"page":best["page"]})
            used={best["text"]}
        else:
            used=set()
        # Subheadings
        clean=[l for l in lines if l["text"] not in used and filter_heading_candidate(l["text"],l["font_size"],l["bold_ratio"])]
        refined=[l for l in clean if len(l["text"].split())>=5 and len(l["text"])>=15]
        if refined:
            sizes=np.array([l['font_size']for l in refined]).reshape(-1,1)
            weights=np.array([l['bold_ratio']for l in refined]).reshape(-1,1)
            feats=np.hstack([sizes,weights])
            ncl=min(2,len(np.unique(sizes)))
            if ncl>1 and len(refined)>1:
                clustering=AgglomerativeClustering(n_clusters=ncl).fit(feats)
                scores=[]
                for cid in range(ncl):
                    mask=clustering.labels_==cid
                    scores.append((cid,sizes[mask].mean()+weights[mask].mean()))
                scores.sort(key=lambda x:x[1],reverse=True)
                level_map={cid:f"H{i+1}"for i,(cid,_)in enumerate(scores)}
                for idx,l in enumerate(refined):
                    lvl=level_map[clustering.labels_[idx]]
                    if l["text"] not in used:
                        outline.append({"level":lvl,"text":l["text"],"page":page_idx})
                        used.add(l["text"])
            else:
                for l in refined:
                    if l["text"] not in used:
                        outline.append({"level":"H2","text":l["text"],"page":page_idx})
                        used.add(l["text"])
    # Dedupe
    final=[]
    seen=set()
    for h in outline:
        key=(h['level'],h['text'],h['page'])
        if key not in seen:
            final.append(h)
            seen.add(key)
    title=final[0]['text'] if final else ""
    if title and any(k in title.lower() for k in ["form","application","request","declaration"]):
        return {"title":title,"outline":[]}
    return {"title":title,"outline":final}

# Batch processing

def process_all_pdfs(input_dir="input", output_dir="output"):
    os.makedirs(output_dir,exist_ok=True)
    for fn in sorted(os.listdir(input_dir)):
        if not fn.lower().endswith(".pdf"): continue
        res=extract_headings(os.path.join(input_dir,fn))
        out=os.path.splitext(fn)[0]+".json"
        with open(os.path.join(output_dir,out),'w',encoding='utf-8') as f:
            json.dump(res,f,ensure_ascii=False,indent=2)
        print(f"Processed {fn}, title: '{res['title']}'")

if __name__ == "__main__":
    process_all_pdfs()
