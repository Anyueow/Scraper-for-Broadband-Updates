"""
Content parser for cleaning and normalizing article text
"""
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ContentParser:
    """Parse and clean article content"""

    def __init__(self):
        self.boilerplate_patterns = [
            r'cookie\s+(policy|notice|consent)',
            r'terms\s+(of\s+use|and\s+conditions)',
            r'privacy\s+policy',
            r'subscribe\s+to\s+our\s+newsletter',
            r'follow\s+us\s+on\s+(twitter|facebook|linkedin)',
            r'share\s+this\s+article',
            r'related\s+articles',
            r'you\s+may\s+also\s+like',
            r'comments\s+\(\d+\)',
            r'leave\s+a\s+comment',
        ]

    def parse(self, article: Dict) -> Dict:
        """Parse and clean article content"""
        parsed = article.copy()

        # Clean title
        if 'title' in parsed:
            parsed['title'] = self.clean_text(parsed['title'])

        # Clean summary
        if 'summary' in parsed:
            parsed['summary'] = self.clean_text(parsed['summary'])

        # Clean and process full content
        if 'content' in parsed:
            content = parsed['content']
            content = self.remove_boilerplate(content)
            content = self.clean_text(content)
            parsed['content'] = content
            parsed['word_count'] = len(content.split())

        return parsed

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters (keep alphanumeric, punctuation, and common symbols)
        text = re.sub(r'[^\w\s\-.,!?;:()\[\]\'\"£$%&/]', '', text)

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        return text.strip()

    def remove_boilerplate(self, content: str) -> str:
        """Remove common boilerplate text"""
        if not content:
            return ""

        # Remove patterns that match boilerplate
        for pattern in self.boilerplate_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        # Remove very short sentences that are likely navigation/ads
        sentences = content.split('.')
        filtered_sentences = [s for s in sentences if len(s.split()) > 3]
        content = '. '.join(filtered_sentences)

        return content

    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract top keywords from text (simple frequency-based)"""
        if not text:
            return []

        # Tokenize
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())

        # Remove common stopwords
        stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
            'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
            'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
            'its', 'let', 'put', 'say', 'she', 'too', 'use', 'will', 'with', 'about',
            'that', 'this', 'have', 'from', 'they', 'been', 'were', 'said', 'what',
            'when', 'your', 'more', 'than', 'other', 'into', 'could', 'would', 'their'
        }

        words = [w for w in words if w not in stopwords]

        # Count frequencies
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        return [word for word, freq in sorted_words[:top_n]]
