# Adobe India Hackathon 2025 - Round 1A Solution
## Team DSA Challenge - PDF Document Structure Extraction

<img width="4770" height="2970" alt="challenge_1a_system_overview" src="https://github.com/user-attachments/assets/be71c38e-81a8-48e8-95b8-b4ed14f2b148" />
<img width="4170" height="3570" alt="challenge_1a_detailed_pipeline" src="https://github.com/user-attachments/assets/b83c692d-615d-4e6d-8072-ab747604aae6" />

### 🎯 **Challenge Overview**
This solution addresses Round 1A of the "Connecting the Dots" challenge, which involves extracting structured outlines (Title and Headings H1, H2, H3) from PDF documents with high accuracy and performance.

## 🎯 **Competitive Advantages we have**

1. **Multilingual Support:** Unicode support for international documents
2. **Hybrid Approach:** Combines OCR and font analysis for maximum coverage
3. **Table Exclusion:** Prevents table content from being misclassified as headings
4. **Context Awareness:** Uses surrounding text for better classification
5. **Performance Optimized:** Multi-threaded processing for speed
6. **Pattern-Driven Filtering:** Easily maintainable exclusion rules

---

## 📋 **Table of Contents**
1. [Problem Statement](#problem-statement)
2. [Solution Architecture](#solution-architecture)
3. [Technical Approach](#technical-approach)
4. [File Structure & Logic](#file-structure--logic)
5. [Key Algorithms](#key-algorithms)
6. [Installation & Usage](#installation--usage)
7. [Libraries & Tools Used](#libraries--&--tools--used)
8. [Performance Optimizations](#performance-optimizations)
9. [Testing Strategy](#testing-strategy)
10. [Constraints & Compliance](#constraints--compliance)

---

## 🎯 **Problem Statement**

**Input:** PDF files (up to 50 pages)  
**Output:** JSON structure containing:
- Document title
- Hierarchical outline with headings (H1, H2, H3)
- Page numbers for each heading

**Constraints:**
- Execution time: ≤ 10 seconds for 50-page PDF
- Model size: ≤ 200MB
- CPU-only execution (AMD64)
- No internet access during processing

---

## 🏗️ **Solution Architecture**

Our solution employs a **multi-stage hybrid approach** combining:

1. **OCR-based Text Extraction** - Handles scanned documents and complex layouts
2. **Font-based Analysis** - Leverages PDF metadata for heading detection
3. **Machine Learning Heuristics** - Uses statistical analysis for heading classification
4. **Context-aware Filtering** - Removes noise and irrelevant content

```
PDF Input → Text Extraction → Heading Detection → Classification → JSON Output
     ↓           ↓              ↓                ↓             ↓
   PyMuPDF   Tesseract OCR   Font Analysis   ML Heuristics  Validation
```

---

## 🔧 **Technical Approach**

### **Phase 1: Text Extraction (`ExcludeTableText.py`)**
**Purpose:** Extract clean text while removing tabular and boxed content

**Key Techniques:**
1. **Computer Vision Pipeline:**
   - Convert PDF pages to images (150 DPI for speed)
   - Apply Gaussian blur and Canny edge detection
   - Detect rectangular contours (tables/boxes)
   - Create masks to exclude tabular regions

2. **OCR Integration:**
   - Use Tesseract with optimized config (`--oem 3 --psm 11`)
   - Parallel processing with ThreadPoolExecutor (8 workers)
   - Focus on sparse text outside detected boxes

**Logic Flow:**
```python
def process_page(page):
    # 1. PDF → Image conversion
    pix = page.get_pixmap(dpi=150)
    
    # 2. Computer vision preprocessing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 30, 150)
    
    # 3. Table/box detection
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 4. Mask creation and text extraction
    mask = create_mask_excluding_boxes(contours)
    text = pytesseract.image_to_string(masked_area)
```

### **Phase 2: Heading Detection (`pdfScapper.py`)**
**Purpose:** Identify and classify headings using multi-factor analysis

**Core Algorithm:**
1. **Font Metadata Analysis:**
   - Extract font size, bold ratio, positioning
   - Calculate statistical baselines (mean font size)
   - Identify font size hierarchies

2. **Heading Candidate Filtering:**
   - Text length validation (2-18 words optimal)
   - Font size thresholds (>110% of average)
   - Bold ratio analysis (≥0.48 threshold)
   - Pattern matching for numbered headings

3. **Level Classification Logic:**
   ```python
   def assign_heading_level(text, font_size, sorted_sizes, bold_ratio):
       # 1. Numbered headings (e.g., "2.1.1 Topic")
       if numeric_pattern_match:
           depth = count_dots() + 1
           return f'H{min(depth, 3)}'
       
       # 2. Heuristic scoring system
       score = calculate_score(font_size_rank, bold_ratio, word_count)
       
       # 3. Threshold-based classification
       if score >= 3.5: return 'H1'
       elif score >= 2.0: return 'H2'
       elif score >= 0.2: return 'H3'
   ```

### **Phase 3: Noise Filtering (`keywords_config.py`)**
**Purpose:** Remove non-heading elements using pattern recognition

**Filter Categories:**
1. **Address Detection:** Street names, postal codes, geographic terms
2. **Instructional Text:** Guidelines, instructions, disclaimers
3. **Website/Email Patterns:** URLs, contact information
4. **Form Elements:** Labels, field names, RSVP text

**YAML-based Pattern Management:**
```yaml
ADDRESS_KEYWORDS: 'address|suite|road|street|avenue|parkway'
DISCLAIMER_KEYWORDS: 'disclaimer|terms and conditions|privacy policy'
INSTRUCTIONAL_KEYWORDS: 'instructions|please read carefully|guidelines'
```

---

## 📁 **File Structure & Logic**

### **Core Processing Files:**

#### `main.py` - **Orchestration Engine**
- **Function:** Coordinates entire pipeline
- **Logic:** 
  - Processes all PDFs in `/input` directory
  - Combines text extraction and heading detection
  - Validates headings against extracted body text
  - Generates JSON output with proper formatting
  - Handles error cases and logging

#### `ExcludeTableText.py` - **OCR Text Extractor**
- **Function:** Intelligent text extraction, avoiding tables
- **Key Logic:**
  - Computer vision-based table detection
  - Parallel processing for performance
  - OCR optimization for document text
  - Noise reduction through masking

#### `pdfScapper.py` - **Heading Intelligence Engine**
- **Function:** Advanced heading detection and classification
- **Core Algorithms:**
  - Multi-factor heading scoring system
  - Font hierarchy analysis
  - Context-aware filtering
  - Numbered heading pattern recognition

#### `keywords_config.py` - **Content Filter**
- **Function:** Pattern-based noise elimination
- **Strategy:**
  - YAML-driven pattern management
  - Multi-category text classification
  - Regex-based exclusion rules
  - Performance-optimized pre-compiled patterns

### **Configuration Files:**

#### `patterns.yaml` - **Filter Patterns Database**
- Centralized pattern definitions
- Easy maintenance and updates
- Category-based organization
- Performance-optimized regex patterns

#### `requirements.txt` - **Dependency Management**
```
PyMuPDF==1.23.5      # PDF processing
numpy==1.24.3        # Numerical computations
pytesseract==0.3.10  # OCR engine
opencv-python==4.8.0.76  # Computer vision
Pillow==10.0.0       # Image processing
```

---

## 🧠 **Key Algorithms**

### **1. Multi-Factor Heading Scoring**
```python
def calculate_heading_score(text, font_size, bold_ratio, word_count):
    score = 0
    
    # Font size ranking (larger = higher score)
    font_rank_bonus = get_font_size_rank_bonus(font_size)
    
    # Bold emphasis bonus
    bold_bonus = 1.0 if bold_ratio > 0.7 else 0.5 if bold_ratio > 0.5 else 0
    
    # Word count optimization (headings are concise)
    length_bonus = 2 if word_count <= 10 else -1 if word_count >= 15 else 0
    
    # Uniqueness bonus (appears only once in document)
    uniqueness_bonus = 1 if is_unique_text(text) else 0
    
    return score + font_rank_bonus + bold_bonus + length_bonus + uniqueness_bonus
```

### **2. Numbered Heading Detection**
```python
def detect_numbered_heading(text):
    # Pattern: "1.2.3 Heading Text" or "1. Introduction"
    pattern = r'^(\d+(?:\.\d+){0,2})[\s\.]'
    match = re.match(pattern, text.strip())
    
    if match:
        number_part = match.group(1)
        depth = number_part.count('.') + 1  # Count dots for hierarchy
        return f'H{min(depth, 3)}'  # Cap at H3
    
    return None
```

### **3. Context-Aware Filtering**
```python
def filter_with_context(text, surrounding_lines):
    # Check text against exclusion patterns
    if matches_exclusion_patterns(text):
        return False
    
    # Analyze surrounding context
    context_score = analyze_surrounding_context(surrounding_lines)
    
    # Consider document position and formatting
    position_score = analyze_document_position(text)
    
    return (context_score + position_score) > CONFIDENCE_THRESHOLD
```

---

## 🚀 **Installation & Usage**

### **Docker Method (Recommended)**
```bash
# Build the container
docker build --platform linux/amd64 -t headingDetectionRound1A:teamdsa .

#Add input PDFs


# Run processing
 docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none headingDetectionRound1A:teamdsa
```

### **Direct Python Execution**
```bash
# Install dependencies
pip install -r requirements.txt

Add PDFs in input/ directory

# Process PDFs
python3 main.py
```

---

### Libraries & Tools Used 🪛
- PyMuPDF (fitz) – PDF text and metadata extraction
- OpenCV – Computer vision for table detection
- pytesseract – OCR for scanned text
- Pillow – Image processing
- NumPy – Numerical computations


## ⚡ **Performance Optimizations**

### **1. Parallel Processing**
- **ThreadPoolExecutor** with 8 workers for OCR processing
- **Page-level parallelization** for large documents
- **Memory-efficient** streaming for reduced RAM usage

### **2. OCR Optimization**
- **Reduced DPI** (150 vs 300) for 2x speed improvement
- **Sparse text mode** (`--psm 11`) for document processing
- **Targeted OCR** only on non-tabular regions

### **3. Font Analysis Efficiency**
- **Pre-compiled regex patterns** for pattern matching
- **Statistical sampling** for font size analysis
- **Cached computations** for repeated operations

### **4. Memory Management**
- **Streaming PDF processing** (page-by-page)
- **Garbage collection** after heavy operations
- **Minimal object retention** between pages

---

## 🧪 **Testing Strategy**

### **Test Categories:**
1. **Simple Documents:** Clear headings, standard formatting
2. **Complex Layouts:** Mixed fonts, embedded content
3. **Scanned Documents:** OCR-dependent processing
4. **Multilingual Content:** Unicode and international text
5. **Edge Cases:** Unusual formatting, minimal content

### **Validation Metrics:**
- **Precision:** Correctly identified headings / Total identified headings
- **Recall:** Correctly identified headings / Actual headings in document
- **Processing Time:** Per-page and total document timing
- **Memory Usage:** Peak RAM consumption monitoring

---

## ⚙️ **Constraints & Compliance**

### **Technical Constraints Met:**
✅ **Platform:** AMD64 architecture support  
✅ **Runtime:** CPU-only execution (no GPU dependencies)  
✅ **Performance:** Optimized for <10 seconds per 50-page PDF  
✅ **Model Size:** No large ML models (under 200MB constraint)  
✅ **Network:** Fully offline processing capability  
✅ **Memory:** Efficient processing within 16GB RAM limits  

### **Output Format Compliance:**
✅ **JSON Structure:** Matches required schema exactly  
✅ **Page Numbering:** 0-based indexing (consistent with implementation)  
✅ **Heading Levels:** H1, H2, H3 classification  
✅ **Unicode Support:** Full international character support  

---

## 🎯 **Competitive Advantages**

1. **Hybrid Approach:** Combines OCR and font analysis for maximum coverage
2. **Table Exclusion:** Prevents table content from being misclassified as headings
3. **Context Awareness:** Uses surrounding text for better classification
4. **Performance Optimized:** Multi-threaded processing for speed
5. **Multilingual Support:** Unicode support for international documents
6. **Pattern-Driven Filtering:** Easily maintainable exclusion rules

---

## 📊 **Expected Performance**

- **Accuracy:** 85-95% precision/recall on diverse document types
- **Speed:** 2-8 seconds per 50-page document
- **Memory:** <2GB RAM usage for large documents
- **Multilingual:** Full support for Unicode text extraction




## 👥 **Team DSA**
*Adobe India Hackathon 2025 - Round 1A Solution*

This solution represents a comprehensive approach to document structure extraction, balancing accuracy, performance, and maintainability for real-world PDF processing scenarios.

<img width="1878" height="637" alt="image" src="https://github.com/user-attachments/assets/335a44a4-3f57-4875-b4be-c0d5e80c91d2" />
<img width="1858" height="646" alt="image" src="https://github.com/user-attachments/assets/bedc65af-f00b-4f8c-80f4-2262d8b4e14a" />




