import hashlib
from bs4 import BeautifulSoup
import re

def get_content_hash(html_content: str) -> str:
    """
    Generates a SHA256 hash of the website content.
    Strips scripts, styles, and extra whitespace to focus on visible content changes (OSINT).
    """
    if not html_content:
        return ""
        
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove noisy elements that often change without meaningful content changes
        for element in soup(["script", "style", "meta", "noscript", "iframe"]):
            element.decompose()
            
        # Get visible text
        text = soup.get_text()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Error generating content hash: {e}")
        # Fallback to raw content if parsing fails
        return hashlib.sha256(html_content.encode('utf-8')).hexdigest()

def detect_change(old_hash: str, new_hash: str) -> bool:
    """Compares two hashes to detect change."""
    if not old_hash:
        return False
    return old_hash != new_hash
