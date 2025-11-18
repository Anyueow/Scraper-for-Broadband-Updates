import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin
import csv
import os
from datetime import datetime, timedelta
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ArticleScraper/1.0; +https://example.com/bot)"
}

LISTING_URL = "https://www.ispreview.co.uk/"  # Main page
BASE_URL = "https://www.ispreview.co.uk"

# Create a session for connection pooling
session = requests.Session()
session.headers.update(HEADERS)

# Thread-safe counter
counter_lock = Lock()
fetch_counter = 0


def fetch_html(url: str, session_obj=None) -> str:
    """Download and return HTML for a URL using session for connection pooling."""
    if session_obj is None:
        session_obj = session
    resp = session_obj.get(url, timeout=15)
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


def extract_full_article_content(url: str, session_obj=None) -> str:
    """Fetch and extract full article content from article page"""
    global fetch_counter
    try:
        html = fetch_html(url, session_obj)
        soup = BeautifulSoup(html, "html.parser")
        
        # Try to find main content area
        content_elem = soup.find(['article', 'div'], class_=lambda x: x and ('entry-content' in x or 'post-content' in x or 'article-content' in x))
        
        if not content_elem:
            content_elem = soup.find('article')
        
        if not content_elem:
            content_elem = soup.find('div', class_=lambda x: x and 'content' in x.lower())
        
        if content_elem:
            # Remove unwanted elements
            for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header', 'form']):
                tag.decompose()
            
            # Remove ad containers
            for tag in content_elem.find_all(class_=lambda x: x and ('ad' in x.lower() or 'advertisement' in x.lower() or 'social-share' in x.lower())):
                tag.decompose()
            
            content = content_elem.get_text(separator=' ', strip=True)
            
            # Update counter
            with counter_lock:
                fetch_counter += 1
                if fetch_counter % 10 == 0:
                    print(f"    Fetched {fetch_counter} articles...", end='\r')
            
            return " ".join(content.split())  # normalize whitespace
        else:
            return ""
    except Exception as e:
        print(f"\nError fetching full content from {url}: {e}")
        return ""


def parse_listing_page(html: str, base_url: str, fetch_full_content: bool = False):
    """
    Parse the listing page and return article records:
    {title, url, date, content}
    
    Note: If fetch_full_content is True, content will be empty here and filled later in parallel
    """
    soup = BeautifulSoup(html, "html.parser")

    # Each article block looks like the snippet you pasted:
    # <div style="float:left;width:72.5%;" class="isprpara"> ... </div>
    article_blocks = soup.select("div.isprpara")
    articles = []

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

        # Get content - use excerpt from listing page for now, full content fetched in parallel later
        if not fetch_full_content:
            # article content is inside <div class="text2"> (excerpt from listing page)
            text_container = block.select_one("div.text2")
            content = clean_article_html(text_container) if text_container else ""
        else:
            # Content will be fetched in parallel
            content = ""

        articles.append({
            "title": title,
            "url": url,
            "date": date,
            "content": content,
        })
    
    return articles


def fetch_articles_content_parallel(articles: list, max_workers: int = 10) -> list:
    """
    Fetch full article content in parallel using ThreadPoolExecutor
    
    Args:
        articles: List of article dicts with 'url' field
        max_workers: Number of parallel threads (default 10)
    
    Returns:
        List of articles with 'content' field populated
    """
    if not articles:
        return articles
    
    print(f"  Fetching full content for {len(articles)} articles in parallel ({max_workers} workers)...")
    
    # Create a new session for each thread (thread-safe)
    def fetch_with_session(article):
        thread_session = requests.Session()
        thread_session.headers.update(HEADERS)
        content = extract_full_article_content(article['url'], thread_session)
        article['content'] = content
        return article
    
    # Use ThreadPoolExecutor for parallel fetching
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_article = {executor.submit(fetch_with_session, article): article for article in articles}
        
        # Collect results as they complete (maintain order by using original article list)
        results_dict = {}
        for future in as_completed(future_to_article):
            try:
                result = future.result()
                results_dict[result['url']] = result
            except Exception as e:
                article = future_to_article[future]
                print(f"\n    Error fetching {article['url']}: {e}")
                results_dict[article['url']] = article  # Keep article even if content fetch failed
        
        # Maintain original order
        results = [results_dict.get(article['url'], article) for article in articles]
    
    print(f"  ✅ Completed fetching content for {len(results)} articles")
    return results


def parse_date(date_str: str) -> datetime:
    """Parse date string like '13th Nov 2025' to datetime object"""
    if not date_str:
        return None
    
    try:
        # Remove ordinal suffixes (st, nd, rd, th)
        date_str_clean = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '').strip()
        # Parse format: "13 Nov 2025"
        return datetime.strptime(date_str_clean, "%d %b %Y")
    except Exception as e:
        print(f"Warning: Could not parse date '{date_str}': {e}")
        return None


def scrape_listing(listing_url: str, fetch_full_content: bool = True, min_pages: int = 30, max_pages: int = 100, target_days: int = 365, save_interval: int = 5):
    """
    Scrape articles going back in time until we have at least target_days worth of articles.
    Each page has approximately 20 articles, so we need at least min_pages pages.
    
    Args:
        listing_url: Starting URL (can be main page or category page)
        fetch_full_content: Whether to fetch full article content
        min_pages: Minimum number of pages to scrape
        max_pages: Maximum number of pages to scrape
        target_days: Target number of days to go back (default 365 for a year)
        save_interval: Save progress every N pages (default 5)
    
    Returns:
        tuple: (all_articles, oldest_date) - articles collected and oldest date found
    """
    all_articles = []
    oldest_date = None
    target_date = datetime.now() - timedelta(days=target_days)
    
    global fetch_counter
    fetch_counter = 0  # Reset counter
    
    print(f"Target: Collect articles from the past {target_days} days (until {target_date.strftime('%Y-%m-%d')})")
    print(f"Minimum pages to scrape: {min_pages} (each page ≈ 20 articles)")
    print(f"Starting from: {listing_url}")
    print(f"💾 Progress will be saved every {save_interval} pages")
    print(f"⚡ Using parallel processing (10 workers) for faster scraping")
    print(f"⚠️  Press Ctrl+C to stop and save collected data\n")
    
    # Determine starting page number
    # If listing_url contains /page/X, extract it; otherwise start from page 1
    page_match = re.search(r'/page/(\d+)', listing_url)
    if page_match:
        current_page = int(page_match.group(1))
        base_url_pattern = re.sub(r'/page/\d+', '', listing_url)
    else:
        current_page = 1
        # Use main listing URL pattern
        if '/category/' in listing_url:
            base_url_pattern = listing_url
        else:
            base_url_pattern = f"{BASE_URL}/index.php"
    
    for page in range(1, max_pages + 1):
        # Construct page URL
        if page == 1:
            # First page - use original listing URL or base pattern
            if '/page/' not in listing_url:
                current_url = listing_url
            else:
                current_url = base_url_pattern
        else:
            # Subsequent pages: /index.php/page/X
            current_url = f"{BASE_URL}/index.php/page/{page}"
        
        print(f"Scraping page {page}: {current_url}")
        try:
            html = fetch_html(current_url, session)
            page_articles = parse_listing_page(html, BASE_URL, fetch_full_content=False)
            
            if not page_articles:
                print(f"  No articles found on page {page}, stopping.")
                break
            
            # If we need full content, fetch it in parallel
            if fetch_full_content:
                page_articles = fetch_articles_content_parallel(page_articles, max_workers=10)
            
            # Add articles to collection
            all_articles.extend(page_articles)
            print(f"  Found {len(page_articles)} articles on page {page} (Total: {len(all_articles)})")
            
            # Check if we've gone back far enough
            # Parse dates to find the oldest article
            for article in page_articles:
                date_str = article.get('date', '')
                if date_str:
                    article_date = parse_date(date_str)
                    if article_date:
                        if oldest_date is None or article_date < oldest_date:
                            oldest_date = article_date
            
            # Periodic save (every save_interval pages)
            if page % save_interval == 0 and all_articles:
                print(f"  💾 Saving progress checkpoint ({len(all_articles)} articles so far)...")
                # This will be handled by the main function
            
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
            
            time.sleep(0.5)  # Reduced rate limiting between pages
            
        except Exception as e:
            print(f"  Error scraping page {page}: {e}")
            # Don't break immediately - try to continue with next page
            if oldest_date and oldest_date > target_date:
                print(f"  Still need more data, trying next page...")
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
            print(f"   You may need to increase max_pages")
    else:
        print(f"   ⚠️  WARNING: Could not determine date range")
    
    return all_articles, oldest_date


def export_to_csv(articles: list, output_dir: str = "Scraped Output", filename: str = None):
    """Export articles to CSV with the specified format"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate CSV filename
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"ispreview_articles_{timestamp}.csv")
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
    print("=" * 80)
    print("ISPreview UK Article Scraper - Historical Collection")
    print("=" * 80)
    print(f"Scraping articles from: {LISTING_URL}")
    print("Collecting at least 1 year of historical articles...")
    print("Fetching full article content...\n")
    
    articles = []
    oldest_date = None
    
    try:
        # Scrape articles going back at least 365 days
        # Each page has ~20 articles, so 30 pages = ~600 articles (should cover a year)
        articles, oldest_date = scrape_listing(
            LISTING_URL, 
            fetch_full_content=True, 
            min_pages=30, 
            max_pages=100, 
            target_days=365,
            save_interval=5  # Save every 5 pages
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user (Ctrl+C)")
        print("Saving collected data...")
        if articles:
            print(f"  Collected {len(articles)} articles before interruption")
        else:
            print("  No articles collected yet.")
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}")
        print("Saving collected data...")
        import traceback
        traceback.print_exc()
    
    if articles:
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
        
        # Sort articles by date (newest first)
        def get_sort_date(article):
            date_str = article.get('date', '')
            if date_str:
                article_date = parse_date(date_str)
                if article_date:
                    return article_date
            return datetime.min
        
        sorted_articles = sorted(unique_articles, key=get_sort_date, reverse=True)
        
        # Export to CSV
        csv_filename = export_to_csv(sorted_articles)
        
        # Print date range summary
        dates = [a.get('date', '') for a in sorted_articles if a.get('date')]
        if dates:
            oldest_parsed = parse_date(sorted_articles[-1].get('date', ''))
            newest_parsed = parse_date(sorted_articles[0].get('date', ''))
            if oldest_parsed and newest_parsed:
                print(f"\nDate range: {oldest_parsed.strftime('%Y-%m-%d')} to {newest_parsed.strftime('%Y-%m-%d')}")
        
        # Print summary of first few articles
        print("\n" + "=" * 80)
        print("SAMPLE ARTICLES (First 5):")
        print("=" * 80)
        for i, a in enumerate(sorted_articles[:5], 1):
            print(f"\n[{i}] {a.get('date', 'N/A')} - {a.get('title', 'N/A')}")
            print(f"    URL: {a.get('url', 'N/A')}")
            if a.get('content'):
                print(f"    Content preview: {a.get('content', '')[:100]}...")
        
        print(f"\n✅ All data saved to: {csv_filename}")
        print("   You can safely stop the script at any time - data is saved incrementally.")
    else:
        print("No articles found.")
