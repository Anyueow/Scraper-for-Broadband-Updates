"""
Base scraper class with common functionality
"""
import time
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all news scrapers"""

    def __init__(self, source_name: str, base_url: str, user_agent: str, timeout: int = 30):
        self.source_name = source_name
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

    def fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a page with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'lxml')
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None

    @abstractmethod
    def scrape_article_list(self, max_pages: int = 10) -> List[Dict]:
        """Scrape list of articles with metadata"""
        pass

    @abstractmethod
    def scrape_article_content(self, url: str) -> Optional[Dict]:
        """Scrape full content of a single article"""
        pass

    def extract_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        try:
            # This is a placeholder - each scraper should implement its own date parsing
            return date_str
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None

    def scrape_all(self, max_pages: int = 10, delay: float = 2.0) -> List[Dict]:
        """
        Complete scraping workflow:
        1. Get article list
        2. Fetch full content for each article
        """
        logger.info(f"Starting scrape of {self.source_name}")

        # Get article metadata
        articles = self.scrape_article_list(max_pages=max_pages)
        logger.info(f"Found {len(articles)} articles from {self.source_name}")

        # Fetch full content for each article
        enriched_articles = []
        for i, article in enumerate(articles):
            logger.info(f"Fetching content {i+1}/{len(articles)}: {article.get('title', 'Unknown')}")

            full_content = self.scrape_article_content(article['url'])
            if full_content:
                article.update(full_content)

            enriched_articles.append(article)

            # Rate limiting
            if i < len(articles) - 1:
                time.sleep(delay)

        logger.info(f"Completed scraping {self.source_name}: {len(enriched_articles)} articles")
        return enriched_articles
