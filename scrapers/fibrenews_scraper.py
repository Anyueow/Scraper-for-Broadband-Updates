"""
Scraper for Fibre News
"""
from typing import List, Dict, Optional
import re
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class FibreNewsScraper(BaseScraper):
    """Scraper for fibrenews.co.uk"""

    def __init__(self, base_url: str, user_agent: str, timeout: int = 30):
        super().__init__("FibreNews", base_url, user_agent, timeout)
        self.news_url = f"{base_url}/news"

    def scrape_article_list(self, max_pages: int = 10) -> List[Dict]:
        """Scrape article list from news section"""
        articles = []

        for page in range(1, max_pages + 1):
            url = f"{self.news_url}/page/{page}" if page > 1 else self.news_url
            soup = self.fetch_page(url)

            if not soup:
                break

            # Find article elements
            article_elements = soup.find_all(['article', 'div'], class_=re.compile(r'post|article|news-item|story'))

            if not article_elements:
                # Fallback patterns
                article_elements = soup.find_all('div', class_=re.compile(r'item|entry'))

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
        # Find title
        title_elem = element.find(['h2', 'h3', 'h1', 'a'], class_=re.compile(r'title|headline|entry-title'))
        if not title_elem:
            title_elem = element.find(['h2', 'h3', 'h1'])

        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)

        # Find URL
        link_elem = title_elem.find('a', href=True) if title_elem.name != 'a' else title_elem
        if not link_elem:
            link_elem = element.find('a', href=True)

        if not link_elem:
            return None

        url = link_elem['href']
        if not url.startswith('http'):
            url = self.base_url + url

        # Find date
        date_elem = element.find(['time', 'span'], class_=re.compile(r'date|time|published|posted'))
        date_str = None
        if date_elem:
            date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)

        # Find summary
        summary_elem = element.find(['p', 'div'], class_=re.compile(r'excerpt|summary|description'))
        if not summary_elem:
            summary_elem = element.find('p')
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
            # Find main content
            content_elem = soup.find(['article', 'div'], class_=re.compile(r'entry-content|article-content|post-content|content'))

            if not content_elem:
                content_elem = soup.find('article')

            if content_elem:
                # Remove unwanted elements
                for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
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
