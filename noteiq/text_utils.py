"""
Text processing utilities for NoteIQ
Provides helpers for text manipulation, sanitization, and formatting
"""
import re
import unicodedata
from typing import List, Optional, Set


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string for use as a filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove leading/trailing dots
    filename = filename.strip('.')
    # Limit length
    return filename[:255] if len(filename) > 255 else filename


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to slugify
        
    Returns:
        Slugified text
    """
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    # Remove non-alphanumeric characters
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'[-\s]+', '-', text)
    # Remove leading/trailing hyphens
    return text.strip('-').lower()


def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from text.
    
    Args:
        text: Text to extract from
        
    Returns:
        List of hashtags
    """
    return re.findall(r'#(\w+)', text)


def extract_mentions(text: str) -> List[str]:
    """
    Extract mentions from text.
    
    Args:
        text: Text to extract from
        
    Returns:
        List of mentions
    """
    return re.findall(r'@(\w+)', text)


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Text to extract from
        
    Returns:
        List of URLs
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text.
    
    Args:
        text: Text to extract from
        
    Returns:
        List of email addresses
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def highlight_text(text: str, query: str, prefix: str = "**", suffix: str = "**") -> str:
    """
    Highlight query matches in text.
    
    Args:
        text: Text to highlight
        query: Query to highlight
        prefix: Prefix for highlighted text
        suffix: Suffix for highlighted text
        
    Returns:
        Text with highlights
    """
    if not query:
        return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(f"{prefix}{query}{suffix}", text)


def word_count(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count
        
    Returns:
        Word count
    """
    return len(text.split())


def char_count(text: str, include_spaces: bool = True) -> int:
    """
    Count characters in text.
    
    Args:
        text: Text to count
        include_spaces: Whether to include spaces
        
    Returns:
        Character count
    """
    if include_spaces:
        return len(text)
    return len(text.replace(' ', ''))


def sentence_count(text: str) -> int:
    """
    Count sentences in text.
    
    Args:
        text: Text to count
        
    Returns:
        Sentence count
    """
    return len(re.findall(r'[.!?]+', text))


def paragraph_count(text: str) -> int:
    """
    Count paragraphs in text.
    
    Args:
        text: Text to count
        
    Returns:
        Paragraph count
    """
    return len([p for p in text.split('\n\n') if p.strip()])


def remove_html(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: Text with HTML
        
    Returns:
        Plain text
    """
    return re.sub(r'<[^>]+>', '', text)


def remove_urls(text: str) -> str:
    """
    Remove URLs from text.
    
    Args:
        text: Text with URLs
        
    Returns:
        Text without URLs
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_pattern, '', text)


def remove_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace from text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    # Strip leading/trailing whitespace
    return text.strip()


def capitalize_words(text: str) -> str:
    """
    Capitalize first letter of each word.
    
    Args:
        text: Text to capitalize
        
    Returns:
        Capitalized text
    """
    return ' '.join(word.capitalize() for word in text.split())


def title_case(text: str) -> str:
    """
    Convert text to title case.
    
    Args:
        text: Text to convert
        
    Returns:
        Title case text
    """
    # Common articles to not capitalize
    articles = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by'}
    
    words = text.split()
    result = []
    
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in articles:
            result.append(word.capitalize())
        else:
            result.append(word.lower())
    
    return ' '.join(result)


def to_snake_case(text: str) -> str:
    """
    Convert text to snake_case.
    
    Args:
        text: Text to convert
        
    Returns:
        Snake case text
    """
    # Insert underscore before uppercase letters
    text = re.sub(r'(?<!^)(?=[A-Z])', '_', text)
    # Replace spaces and hyphens with underscores
    text = re.sub(r'[\s-]+', '_', text)
    # Convert to lowercase and remove duplicates
    return text.lower().strip('_')


def to_camel_case(text: str) -> str:
    """
    Convert text to camelCase.
    
    Args:
        text: Text to convert
        
    Returns:
        Camel case text
    """
    words = re.sub(r'[^a-zA-Z0-9]', ' ', text).split()
    if not words:
        return ''
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def to_pascal_case(text: str) -> str:
    """
    Convert text to PascalCase.
    
    Args:
        text: Text to convert
        
    Returns:
        Pascal case text
    """
    words = re.sub(r'[^a-zA-Z0-9]', ' ', text).split()
    return ''.join(word.capitalize() for word in words)


def get_unique_words(text: str) -> Set[str]:
    """
    Get unique words from text.
    
    Args:
        text: Text to process
        
    Returns:
        Set of unique words
    """
    return set(text.lower().split())


def common_words(text1: str, text2: str) -> Set[str]:
    """
    Find common words between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Set of common words
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    return words1.intersection(words2)


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Edit distance
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def is_similar(text1: str, text2: str, threshold: float = 0.8) -> bool:
    """
    Check if two texts are similar.
    
    Args:
        text1: First text
        text2: Second text
        threshold: Similarity threshold (0-1)
        
    Returns:
        True if similar
    """
    distance = levenshtein_distance(text1.lower(), text2.lower())
    max_len = max(len(text1), len(text2))
    
    if max_len == 0:
        return True
    
    similarity = 1 - (distance / max_len)
    return similarity >= threshold
