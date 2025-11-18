import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
from datetime import datetime
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; tbb-scraper/1.0)"
}

ARCHIVE_URL = "https://www.thinkbroadband.com/news/archive"
BASE_URL = "https://www.thinkbroadband.com"


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def extract_article_body(html: str) -> str:
    """
    Extract main article text from a thinkbroadband article page.

    NOTE: You may need to tweak the selectors below once you inspect
    one full article page – this is the only "site-specific" part.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Try a few likely containers in order of preference
    candidates = [
        "article",                    # generic <article> tag
        "div.news-article-body",      # example class
        "div#news-article-body",
        "div.article-body",
        "div.col-md-9.col-lg-10"     # Specific to thinkbroadband article content
    ]

    container = None
    for sel in candidates:
        container = soup.select_one(sel)
        if container:
            break

    if not container:
        # Fallback: just grab all text from main content column if needed
        container = soup.body

    if container:
        # Remove unwanted elements
        for tag in container.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
            tag.decompose()
        
        text = container.get_text(" ", strip=True)
        return " ".join(text.split())  # normalize whitespace
    else:
        return ""


def parse_archive_page(html: str, base_url: str):
    """
    Yield dicts with: title, url, date, content
    for each row in the archive.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Each article row:
    rows = soup.select("div.row.py-2.border-bottom")
    
    # If that selector doesn't work, try alternative selectors
    if not rows:
        rows = soup.select("div.news-item, article, div.article-item")

    for i, row in enumerate(rows, 1):
        try:
            # ---- title + link ----
            link = row.select_one("div.col-md-9.news-archive-title a.text-decoration-none")
            if not link:
                # Try alternative selectors
                link = row.select_one("a[href*='/news/'], a.article-link, h2 a, h3 a")
            
            if not link:
                continue

            url = urljoin(base_url, link.get("href"))

            # The <a> contains "<strong>Title: </strong>Actual title"
            # so strip out the "Title:" label and keep the remaining text.
            title_parts = []
            for txt in link.stripped_strings:
                if "title:" in txt.lower():   # skip the label
                    continue
                title_parts.append(txt)
            title = " ".join(title_parts) if title_parts else link.get_text(strip=True)

            # ---- date ----
            date_div = row.select_one("div.col-md-3.news-archive-title")
            if not date_div:
                date_div = row.select_one("time, .date, .published-date")
            date = date_div.get_text(strip=True) if date_div else ""

            # ---- article content (follow link) ----
            print(f"  [{i}/{len(rows)}] Fetching content for: {title[:50]}...")
            article_html = fetch_html(url)
            content = extract_article_body(article_html)
            time.sleep(1)  # Rate limiting

            yield {
                "title": title,
                "url": url,
                "date": date,
                "content": content,
            }
        except Exception as e:
            print(f"  Error processing row {i}: {e}")
            continue


def scrape_thinkbroadband_archive(archive_url: str):
    html = fetch_html(archive_url)
    return list(parse_archive_page(html, archive_url))


def export_to_csv(articles: list, output_dir: str = "Scraped Output", filename: str = None):
    """Export articles to CSV with the specified format"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate CSV filename
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"thinkbroadband_articles_{timestamp}.csv")
    else:
        filename = os.path.join(output_dir, filename)
    
    # Write to CSV with exact column names
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Website source', 'Article Title', 'Article Link', 'Date', 'Article Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write articles
        for article in articles:
            writer.writerow({
                'Website source': BASE_URL,
                'Article Title': article.get('title', ''),
                'Article Link': article.get('url', ''),
                'Date': article.get('date', ''),
                'Article Content': article.get('content', '')
            })
    
    print(f"✅ Exported {len(articles)} articles to: {filename}")
    return filename


if __name__ == "__main__":
    print(f"Scraping articles from: {ARCHIVE_URL}")
    print("Fetching full article content...")
    articles = scrape_thinkbroadband_archive(ARCHIVE_URL)
    
    if articles:
        export_to_csv(articles)
        
        # Print summary
        print(f"\n✅ Scraped {len(articles)} articles")
        print("\nSample articles:")
        for i, a in enumerate(articles[:3], 1):
            print(f"\n[{i}] {a['date']} - {a['title']}")
            print(f"    URL: {a['url']}")
            print(f"    Content preview: {a['content'][:100]}...")
    else:
        print("No articles found.")
