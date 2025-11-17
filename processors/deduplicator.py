"""
Deduplication module to remove duplicate articles
"""
import hashlib
import logging
from typing import List, Dict, Set
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class Deduplicator:
    """Remove duplicate articles based on various criteria"""

    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()

    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles"""
        unique_articles = []

        for article in articles:
            if self.is_duplicate(article):
                logger.debug(f"Skipping duplicate: {article.get('title', 'Unknown')}")
                continue

            unique_articles.append(article)
            self._register_article(article)

        logger.info(f"Deduplication: {len(articles)} -> {len(unique_articles)} articles")
        return unique_articles

    def is_duplicate(self, article: Dict) -> bool:
        """Check if article is a duplicate"""
        # Check URL
        url = article.get('url', '')
        if url and url in self.seen_urls:
            return True

        # Check content hash
        content_hash = self._generate_hash(article)
        if content_hash in self.seen_hashes:
            return True

        # Check title similarity with existing articles
        title = article.get('title', '')
        if title and self._is_similar_title(title):
            return True

        return False

    def _register_article(self, article: Dict):
        """Register article as seen"""
        url = article.get('url', '')
        if url:
            self.seen_urls.add(url)

        content_hash = self._generate_hash(article)
        self.seen_hashes.add(content_hash)

    def _generate_hash(self, article: Dict) -> str:
        """Generate hash for article based on title and content"""
        # Combine title and first part of content for hashing
        title = article.get('title', '').lower().strip()
        content = article.get('content', '')[:500].lower().strip()  # First 500 chars
        summary = article.get('summary', '').lower().strip()

        hash_input = f"{title}|{content}|{summary}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def _is_similar_title(self, title: str) -> bool:
        """Check if title is similar to any seen title"""
        # This is a simplified check - in production, you might want to use
        # more sophisticated similarity measures or store seen titles
        # For now, we rely on hash comparison
        return False

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def reset(self):
        """Reset seen articles"""
        self.seen_urls.clear()
        self.seen_hashes.clear()
        logger.info("Deduplicator reset")
