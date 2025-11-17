import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
import sys
import time
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# FibreNews UK news URL
LISTING_URL = "https://fibrenews.co.uk/category/all-news/"


def fetch_html(url: str) -> str:
    """Download and return HTML for a URL."""
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def clean_article_html(container) -> str:
    """Clean and extract text from article container"""
    if not container:
        return ""
    text = container.get_text(separator=" ", strip=True)
    return " ".join(text.split())  # normalize whitespace


def scrape_article_content(url: str) -> str:
    """Scrape full article content from article page"""
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        
        # Try to find main content area
        content_elem = soup.select_one("article, div.entry-content, div.article-content, div.post-content, div.text2")
        
        if not content_elem:
            content_elem = soup.find("main")
        
        if content_elem:
            # Remove unwanted elements
            for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                tag.decompose()
            
            return clean_article_html(content_elem)
        return ""
    except Exception as e:
        print(f"  Warning: Could not fetch content from {url}: {e}")
        return ""


def parse_listing_page(html: str, base_url: str):
    """
    Parse the listing page and yield article records:
    {title, url, date, content}
    """
    soup = BeautifulSoup(html, "html.parser")

    # Each article block - FibreNews structure
    # Try multiple selectors for FibreNews articles
    article_blocks = soup.select("article, div.post, div.entry, div.news-item")

    for block in article_blocks:
        try:
            # title + link - FibreNews structure
            title_tag = block.select_one("h2 a, h3 a, h1 a, header a, a.entry-title-link")
            if not title_tag:
                # Try finding title and link separately
                title_elem = block.select_one("h2, h3, h1, .entry-title")
                link_elem = block.select_one("a[href*='/']")
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    url = urljoin(base_url, link_elem.get("href", ""))
                else:
                    continue
            else:
                title = title_tag.get_text(strip=True)
                url = urljoin(base_url, title_tag.get("href", ""))

            # date - FibreNews structure
            date_tag = block.select_one("time, .published-date, .entry-date, .post-date")
            if date_tag:
                # Try datetime attribute first
                date = date_tag.get("datetime", "") or date_tag.get_text(strip=True)
            else:
                # Fallback: look for date text
                date_elem = block.select_one(".date, [class*='date']")
                date = date_elem.get_text(strip=True) if date_elem else ""
            
            # Clean date - remove extra text
            if date:
                date = date.split("(")[0].strip()

            # article content preview/excerpt
            text_container = block.select_one(".entry-summary, .excerpt, .post-excerpt, .entry-content p")
            content_preview = clean_article_html(text_container) if text_container else ""

            # Fetch full article content
            if url:
                print(f"  Fetching full content from: {url}")
                time.sleep(1)  # Rate limiting
                full_content = scrape_article_content(url)
                # Use full content if available, otherwise use preview
                content = full_content if full_content else content_preview
            else:
                content = content_preview

            yield {
                "title": title,
                "url": url,
                "date": date,
                "content": content,
            }
        except Exception as e:
            print(f"  Error parsing article block: {e}")
            continue


def scrape_listing(listing_url: str, max_pages: int = 5):
    """Scrape articles from listing page(s)"""
    all_articles = []
    current_url = listing_url
    
    for page in range(1, max_pages + 1):
        print(f"\nScraping page {page}: {current_url}")
        try:
            html = fetch_html(current_url)
            page_articles = list(parse_listing_page(html, listing_url))
            
            if not page_articles:
                print(f"  No articles found on page {page}, stopping.")
                break
            
            all_articles.extend(page_articles)
            print(f"  Found {len(page_articles)} articles on page {page}")
            
            # Find next page link for FibreNews pagination
            if page < max_pages:
                soup = BeautifulSoup(html, "html.parser")
                # Look for "Next" link or page number links
                next_link = soup.select_one("a.next, a[rel='next'], .pagination a:contains('Next')")
                if not next_link:
                    # Try finding page number links
                    page_links = soup.select(".pagination a, .page-numbers a")
                    for link in page_links:
                        if link.get_text(strip=True) == str(page + 1) or "next" in link.get_text(strip=True).lower():
                            next_link = link
                            break
                
                if next_link and next_link.get("href"):
                    current_url = urljoin(listing_url, next_link.get("href"))
                else:
                    print(f"  No next page found, stopping at page {page}")
                    break
            
            time.sleep(2)  # Rate limiting between pages
        except Exception as e:
            print(f"  Error scraping page {page}: {e}")
            break
    
    return all_articles


if __name__ == "__main__":
    try:
        print(f"Fetching articles from: {LISTING_URL}")
        
        articles = scrape_listing(LISTING_URL, max_pages=5)
        print(f"\nFound {len(articles)} articles total\n")
        
        if articles:
            # Create output directory if it doesn't exist
            output_dir = "Scraped Output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate CSV filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = os.path.join(output_dir, f"fibrenews_articles_{timestamp}.csv")
            
            # Write to CSV
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Website', 'Article Title', 'Article content', 'Article Link', 'Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write articles
                for a in articles:
                    writer.writerow({
                        'Website': LISTING_URL,
                        'Article Title': a.get('title', ''),
                        'Article content': a.get('content', ''),
                        'Article Link': a.get('url', ''),
                        'Date': a.get('date', '')
                    })
            
            print(f"✅ Successfully saved {len(articles)} articles to: {csv_filename}")
            
            # Also print summary to console
            print("\n" + "=" * 80)
            print("ARTICLES SUMMARY:")
            print("=" * 80)
            for i, a in enumerate(articles, 1):
                print(f"\n[{i}] {a.get('date', 'N/A')} - {a.get('title', 'N/A')}")
                print(f"    URL: {a.get('url', 'N/A')}")
                if a.get('content'):
                    print(f"    Content preview: {a.get('content', '')[:100]}...")
        else:
            print("No articles found. The website structure may have changed.")
            print("Please check the selectors in the code.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
