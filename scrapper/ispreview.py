import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin
import sys
import csv
from datetime import datetime, timedelta
import os
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ISPreview uses /index.php/page/X format for pagination
LISTING_URL = "https://www.ispreview.co.uk/"
BASE_URL = "https://www.ispreview.co.uk"

def fetch_html(url: str) -> str:
    """Download and return HTML for a URL."""
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def clean_article_html(container) -> str:
    """
    Given the <div class="text2"> container from the listing page,
    return a clean text version of the article content.
    """
    # Remove HTML comments like <!-- Article Start -->
    for c in container.find_all(string=lambda text: isinstance(text, Comment)):
        c.extract()

    # Option 1: just use get_text
    text = container.get_text(separator=" ", strip=True)
    return " ".join(text.split())  # normalize whitespace


def parse_listing_page(html: str, base_url: str):
    """
    Parse the listing page and yield article records:
    {title, url, date, content}
    """
    soup = BeautifulSoup(html, "html.parser")

    # Each article block looks like the snippet you pasted:
    # <div style="float:left;width:72.5%;" class="isprpara"> ... </div>
    article_blocks = soup.select("div.isprpara")

    for block in article_blocks:
        # title + link
        title_tag = block.select_one("div.fronthl2 h2.h3mobile a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        url = urljoin(base_url, title_tag.get("href"))

        # date line: <p style="color:#757575;">17th Nov 2025 (0 Comments)</p>
        date_tag = block.select_one("p[style*='color:#757575']")
        raw_date = date_tag.get_text(strip=True) if date_tag else ""
        # Strip off "(0 Comments)" etc.
        date = raw_date.split("(")[0].strip()

        # article content is inside <div class="text2">
        text_container = block.select_one("div.text2")
        content = clean_article_html(text_container) if text_container else ""

        yield {
            "title": title,
            "url": url,
            "date": date,
            "content": content,
        }


def scrape_listing(listing_url: str, min_pages: int = 30, max_pages: int = 100, target_days: int = 365):
    """
    Scrape articles going back in time until we have at least target_days worth of articles
    Each page has approximately a week's worth of articles, so we need at least min_pages pages
    """
    all_articles = []
    current_url = listing_url
    oldest_date = None
    target_date = datetime.now() - timedelta(days=target_days)
    
    print(f"Target: Collect articles from the past {target_days} days (until {target_date.strftime('%Y-%m-%d')})")
    print(f"Minimum pages to scrape: {min_pages} (each page ≈ 1 week of articles)")
    print(f"Starting from: {current_url}\n")
    
    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}: {current_url}")
        try:
            html = fetch_html(current_url)
            page_articles = list(parse_listing_page(html, listing_url))
            
            if not page_articles:
                print(f"  No articles found on page {page}, stopping.")
                break
            
            # Add articles to collection
            all_articles.extend(page_articles)
            print(f"  Found {len(page_articles)} articles on page {page} (Total: {len(all_articles)})")
            
            # Check if we've gone back far enough
            # Parse dates to find the oldest article
            for article in page_articles:
                date_str = article.get('date', '')
                if date_str:
                    try:
                        # Try to parse date (format: "17th Nov 2025")
                        # Remove ordinal suffixes (st, nd, rd, th)
                        date_str_clean = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
                        article_date = datetime.strptime(date_str_clean.strip(), "%d %b %Y")
                        
                        if oldest_date is None or article_date < oldest_date:
                            oldest_date = article_date
                    except:
                        # If date parsing fails, continue
                        pass
            
            # Check if we've collected enough historical data
            # But ensure we scrape at least min_pages pages
            if page >= min_pages:
                if oldest_date and oldest_date <= target_date:
                    print(f"\n✅ Collected articles back to {oldest_date.strftime('%Y-%m-%d')}")
                    print(f"   Target was {target_date.strftime('%Y-%m-%d')}")
                    print(f"   Scraped {page} pages (minimum requirement met)")
                    print(f"   Stopping pagination.")
                    break
                elif oldest_date:
                    days_collected = (datetime.now() - oldest_date).days
                    print(f"  Progress: Collected {days_collected} days so far (target: {target_days} days)")
                    if days_collected >= target_days:
                        print(f"\n✅ Collected articles back to {oldest_date.strftime('%Y-%m-%d')}")
                        print(f"   Scraped {page} pages")
                        print(f"   Stopping pagination.")
                        break
            else:
                # Still need to reach minimum page count
                if oldest_date:
                    days_collected = (datetime.now() - oldest_date).days
                    print(f"  Progress: Page {page}/{min_pages} - Collected {days_collected} days so far")
                else:
                    print(f"  Progress: Page {page}/{min_pages}")
            
            # Find next page link - ISPreview uses specific pagination
            soup = BeautifulSoup(html, "html.parser")
            next_link = None
            
            # ISPreview pagination patterns - try multiple approaches
            # Method 1: Look for "Older posts" or pagination links
            next_link = soup.select_one("a.next, a[rel='next']")
            
            # Method 2: Look for pagination container and find next page number
            if not next_link:
                pagination = soup.select_one(".pagination, .nav-links, .page-numbers, .paging")
                if pagination:
                    # Find all pagination links
                    all_links = pagination.select("a")
                    for link in all_links:
                        link_text = link.get_text(strip=True).lower()
                        href = link.get("href", "")
                        # Look for "next", "older", "→", or page numbers
                        if any(word in link_text for word in ["next", "older", "→", "»"]):
                            next_link = link
                            break
                        # Or check if it's a numbered page link
                        try:
                            page_num = int(link_text)
                            if page_num == page + 1:
                                next_link = link
                                break
                        except:
                            pass
            
            # Method 3: Construct next page URL using ISPreview's pattern: /index.php/page/X
            if not next_link:
                import re
                # ISPreview uses /index.php/page/2, /index.php/page/3, etc.
                if "/index.php/page/" in current_url:
                    # Extract current page number and increment
                    match = re.search(r'/index\.php/page/(\d+)', current_url)
                    if match:
                        current_page = int(match.group(1))
                        next_page = current_page + 1
                        # Replace page number in URL
                        current_url = re.sub(r'/index\.php/page/\d+', f'/index.php/page/{next_page}', current_url)
                        print(f"  Constructed next page URL: {current_url}")
                        time.sleep(2)
                        continue
                elif current_url.rstrip('/') == LISTING_URL.rstrip('/') or current_url == LISTING_URL:
                    # First page (homepage), go to page 2
                    current_url = f"{BASE_URL}/index.php/page/2"
                    print(f"  Constructed next page URL: {current_url}")
                    time.sleep(2)
                    continue
                else:
                    # Try to construct /index.php/page/X pattern
                    current_url = f"{BASE_URL}/index.php/page/{page + 1}"
                    print(f"  Constructed next page URL: {current_url}")
                    time.sleep(2)
                    continue
            
            if next_link and next_link.get("href"):
                current_url = urljoin(listing_url, next_link.get("href"))
                print(f"  Next page URL: {current_url}")
            else:
                # No next link found - construct URL using ISPreview pattern: /index.php/page/X
                import re
                if "/index.php/page/" in current_url:
                    # Extract and increment page number
                    match = re.search(r'/index\.php/page/(\d+)', current_url)
                    if match:
                        current_page = int(match.group(1))
                        next_page = current_page + 1
                        current_url = re.sub(r'/index\.php/page/\d+', f'/index.php/page/{next_page}', current_url)
                        print(f"  No next link found, trying constructed URL: {current_url}")
                    else:
                        # Can't parse, try page 2
                        current_url = f"{BASE_URL}/index.php/page/2"
                        print(f"  Constructed fallback URL: {current_url}")
                elif current_url.rstrip('/') == LISTING_URL.rstrip('/') or current_url == LISTING_URL:
                    # First page, go to page 2
                    current_url = f"{BASE_URL}/index.php/page/2"
                    print(f"  No next link found, trying constructed URL: {current_url}")
                else:
                    # Try constructing /index.php/page/X
                    current_url = f"{BASE_URL}/index.php/page/{page + 1}"
                    print(f"  No next link found, trying constructed URL: {current_url}")
                
                # Before continuing, check if we have enough data
                if oldest_date and oldest_date > target_date:
                    print(f"  ⚠️  Still need more data: Only back to {oldest_date.strftime('%Y-%m-%d')}, target is {target_date.strftime('%Y-%m-%d')}")
                    print(f"  Continuing pagination...")
                # Continue to next iteration to try the constructed URL
            
            time.sleep(2)  # Rate limiting between pages
            
        except Exception as e:
            print(f"  Error scraping page {page}: {e}")
            # Don't break immediately - try to continue with next page
            if oldest_date and oldest_date > target_date:
                print(f"  Still need more data, trying next page...")
                import re
                # Try to increment page number using ISPreview pattern
                if "/index.php/page/" in current_url:
                    match = re.search(r'/index\.php/page/(\d+)', current_url)
                    if match:
                        current_page = int(match.group(1))
                        current_url = re.sub(r'/index\.php/page/\d+', f'/index.php/page/{current_page + 1}', current_url)
                    else:
                        current_url = f"{BASE_URL}/index.php/page/{page + 1}"
                else:
                    current_url = f"{BASE_URL}/index.php/page/{page + 1}"
                time.sleep(3)  # Longer delay after error
                continue
            else:
                # If we have enough data or can't continue, break
                import traceback
                traceback.print_exc()
                break
    
    print(f"\n✅ Total articles collected: {len(all_articles)}")
    if oldest_date:
        days_collected = (datetime.now() - oldest_date).days
        print(f"   Date range: {oldest_date.strftime('%Y-%m-%d')} to present ({days_collected} days)")
        if oldest_date > target_date:
            print(f"   ⚠️  WARNING: Only collected {days_collected} days, target was {target_days} days")
            print(f"   You may need to check pagination or increase max_pages")
    else:
        print(f"   ⚠️  WARNING: Could not determine date range")
    
    return all_articles


if __name__ == "__main__":
    try:
        print("=" * 80)
        print("ISPreview UK Article Scraper - Historical Collection")
        print("=" * 80)
        print(f"Fetching articles from: {LISTING_URL}")
        print("Collecting at least 1 year of historical articles...\n")
        
        # Scrape articles going back at least 365 days
        # Each page has ~1 week of articles, so 30 pages = ~210 days, 52 pages = ~1 year
        print("Starting to scrape from main page...")
        articles = scrape_listing(LISTING_URL, min_pages=30, max_pages=100, target_days=365)
        
        if articles:
            # Create output directory if it doesn't exist
            output_dir = "Scraped Output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Use fixed filename as requested
            csv_filename = os.path.join(output_dir, "ispreviewuk.csv")
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_articles = []
            for article in articles:
                url = article.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_articles.append(article)
            
            print(f"\nRemoved {len(articles) - len(unique_articles)} duplicate articles")
            print(f"Writing {len(unique_articles)} unique articles to CSV...\n")
            
            # Write to CSV
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Website', 'Article Title', 'Article content', 'Article Link', 'Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write articles (sorted by date, newest first)
                # Sort articles by date if possible
                def get_sort_date(article):
                    date_str = article.get('date', '')
                    if date_str:
                        try:
                            date_str_clean = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
                            return datetime.strptime(date_str_clean.strip(), "%d %b %Y")
                        except:
                            return datetime.min
                    return datetime.min
                
                sorted_articles = sorted(unique_articles, key=get_sort_date, reverse=True)
                
                for a in sorted_articles:
                    writer.writerow({
                        'Website': LISTING_URL,
                        'Article Title': a.get('title', ''),
                        'Article content': a.get('content', ''),
                        'Article Link': a.get('url', ''),
                        'Date': a.get('date', '')
                    })
            
            print(f"✅ Successfully saved {len(unique_articles)} articles to: {csv_filename}")
            
            # Print date range summary
            dates = [a.get('date', '') for a in sorted_articles if a.get('date')]
            if dates:
                print(f"\nDate range: {dates[-1]} to {dates[0]}")
            
            # Print summary of first few articles
            print("\n" + "=" * 80)
            print("SAMPLE ARTICLES (First 5):")
            print("=" * 80)
            for i, a in enumerate(sorted_articles[:5], 1):
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
