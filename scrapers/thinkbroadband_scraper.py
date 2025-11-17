"""
Scraper for thinkBroadband news archive
"""
from typing import List, Dict, Optional
from datetime import datetime
import re
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ThinkBroadbandScraper(BaseScraper):
    """Scraper for thinkbroadband.com news"""

    def __init__(self, base_url: str, user_agent: str, timeout: int = 30):
        super().__init__("thinkBroadband", base_url, user_agent, timeout)
        self.news_url = f"{base_url}/news"

    def scrape_article_list(self, max_pages: int = 10) -> List[Dict]:
        """Scrape article list from news archive"""
        articles = []

        for page in range(1, max_pages + 1):
            url = f"{self.news_url}?page={page}" if page > 1 else self.news_url
            soup = self.fetch_page(url)

            if not soup:
                break

            # Find article elements (structure may vary - this is a best-effort approach)
            article_elements = soup.find_all(['article', 'div'], class_=re.compile(r'news|article|story'))

            if not article_elements:
                # Fallback: try to find articles by common patterns
                article_elements = soup.find_all('div', class_=re.compile(r'item|post|entry'))

            if not article_elements:
                logger.warning(f"No articles found on page {page}")
                break

            for element in article_elements:
                try:
                    article_data = self._parse_article_element(element)
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    logger.warning(f"Failed to parse article element: {e}")

            logger.info(f"Scraped page {page}: {len(article_elements)} articles")

        return articles

    def _parse_article_element(self, element) -> Optional[Dict]:
        """Parse individual article element"""
        # Try to find title
        title_elem = element.find(['h2', 'h3', 'h4', 'a'])
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)

        # Try to find URL
        link_elem = element.find('a', href=True)
        if not link_elem:
            return None

        url = link_elem['href']
        if not url.startswith('http'):
            url = self.base_url + url

        # Try to find date
        date_elem = element.find(['time', 'span'], class_=re.compile(r'date|time|published'))
        date_str = date_elem.get_text(strip=True) if date_elem else None
        if date_elem and date_elem.get('datetime'):
            date_str = date_elem['datetime']

        # Try to find summary/excerpt
        summary_elem = element.find(['p', 'div'], class_=re.compile(r'summary|excerpt|description'))
        summary = summary_elem.get_text(strip=True) if summary_elem else ""

        return {
            'source': self.source_name,
            'title': title,
            'url': url,
            'date': date_str,
            'summary': summary
        }

    def scrape_article_content(self, url: str) -> Optional[Dict]:
        """Scrape full article content"""
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Find main content area
            content_elem = soup.find(['article', 'div'], class_=re.compile(r'content|article-body|entry-content|post-content'))

            if not content_elem:
                # Fallback: try to find main tag
                content_elem = soup.find('main')

            if content_elem:
                # Extract text, removing scripts and styles
                for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'footer']):
                    tag.decompose()

                full_content = content_elem.get_text(separator=' ', strip=True)
            else:
                full_content = ""

            return {
                'content': full_content
            }
        except Exception as e:
            logger.error(f"Failed to scrape content from {url}: {e}")
            return {'content': ""}
