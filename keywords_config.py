import yaml
import re
import os

def load_patterns_from_yaml(path):
    """Load regex patterns for each category from a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        patterns = yaml.safe_load(f)
    # Pre-compile all regex for performance
    return {cat: re.compile(pattern, re.IGNORECASE) for cat, pattern in patterns.items()}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "patterns.yaml")
PATTERNS = load_patterns_from_yaml(CONFIG_PATH)

def classify_text(text):
    """
    Returns a list of all category names whose pattern is found in the text.
    """
    return [cat for cat, pattern in PATTERNS.items() if pattern.search(text)]

def text_contains_exclusion_keywords(text):
    """
    Centralized logic for excluding unwanted headings like addresses, RSVP, Table of Contents, etc.
    """
    text = text.strip()

    # 1. Check against all patterns from YAML
    if classify_text(text):
        return True

    # 2. Exclude RSVP and similar
    if text.startswith("RSVP"):
        return True

    # 3. Exclude likely addresses (starts with number + uppercase words)
    if re.match(r'^\d+\s+[A-Z]+', text):
        return True

    # 4. Exclude phone numbers
    if re.match(r'^[\d\-\(\)\+ ]+$', text):
        return True

    # 5. Exclude all-uppercase long text (often not headings)
    if text.isupper() and len(text.split()) > 3:
        return True

    # 6. Exclude very short labels like "FAX", "EMAIL"
    if len(text) <= 6 and text.isupper():
        return True

    return False

def get_pattern_count():
    """Returns the number of loaded patterns."""
    return len(PATTERNS)

if __name__ == "__main__":
    print("Loaded patterns:", PATTERNS)
