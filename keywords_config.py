"""
Keywords and patterns configuration file for PDF text analysis.
This file contains all keyword lists and regex patterns used for text classification
and filtering in the PDF processing pipeline.
"""

# Address-related keywords for identifying location and contact information
ADDRESS_KEYWORDS = [
    "street", "st.", "road", "rd.", "avenue", "ave.", "circle", "blvd",
    "lane", "ln.", "p.o.", "po box", "apartment", "suite", "district",
    "city", "village", "state", "country", "zip", "pin"
]

# Instructional keywords for identifying procedural and directive content
INSTRUCTIONAL_KEYWORDS = [
    "please", "must", "required", "should", "do not", "cannot", "will not",
    "need to", "parents or guardians", "visit", "fill out", "waiver", "rsvp",
    "ticket", "registration", "sign up", "sign up for"
]

# Disclaimer and legal keywords for identifying legal and warning content
DISCLAIMER_KEYWORDS = [
    "disclaimer", "terms and conditions","©","Copyright ©"
]

# Website and URL patterns for identifying web content and email addresses
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

# Additional utility functions for keyword management
def get_all_keywords():
    """
    Returns a dictionary containing all keyword lists for easy access
    """
    return {
        'address': ADDRESS_KEYWORDS,
        'instructional': INSTRUCTIONAL_KEYWORDS,
        'disclaimer': DISCLAIMER_KEYWORDS,
        'website_patterns': WEBSITE_PATTERNS
    }

def add_custom_keywords(category, new_keywords):
    """
    Add custom keywords to a specific category
    
    Args:
        category: One of 'address', 'instructional', 'disclaimer'
        new_keywords: List of new keywords to add
    """
    if category == 'address':
        ADDRESS_KEYWORDS.extend(new_keywords)
    elif category == 'instructional':
        INSTRUCTIONAL_KEYWORDS.extend(new_keywords)
    elif category == 'disclaimer':
        DISCLAIMER_KEYWORDS.extend(new_keywords)
    elif category == 'website_patterns':
        WEBSITE_PATTERNS.extend(new_keywords)
    else:
        raise ValueError(f"Unknown category: {category}. Use 'address', 'instructional', 'disclaimer', or 'website_patterns'")

def get_keyword_count():
    """
    Returns the count of keywords in each category
    """
    return {
        'address_keywords': len(ADDRESS_KEYWORDS),
        'instructional_keywords': len(INSTRUCTIONAL_KEYWORDS),
        'disclaimer_keywords': len(DISCLAIMER_KEYWORDS),
        'website_patterns': len(WEBSITE_PATTERNS)
    }
