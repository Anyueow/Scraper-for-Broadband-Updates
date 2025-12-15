from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import csv
from datetime import datetime
import os
import time

# Try different possible URLs
ARCHIVE_URL = "https://www.thinkbroadband.com/news"  # Main news page instead of archive
ARCHIVE_URL_ALT = "https://www.thinkbroadband.com/news/archive"  # Archive page

# Initialize Selenium WebDriver
def get_driver():
    """Create and configure Chrome WebDriver"""
    chrome_options = Options()
    # Run in headless mode (comment out to see browser)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("\nTo fix this, install the required packages:")
        print("  pip install selenium")
        print("  pip install webdriver-manager")
        print("\nOr use webdriver-manager to auto-download ChromeDriver:")
        print("  from webdriver_manager.chrome import ChromeDriverManager")
        print("  driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)")
        raise


def fetch_html_selenium(driver, url: str) -> str:
    """Fetch HTML using Selenium WebDriver"""
    try:
        print(f"  Loading: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(2)
        
        # Wait for main content to be present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("  Warning: Page took too long to load")
        
        # Get page source
        html = driver.page_source
        return html
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        raise


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
    ]

    container = None
    for sel in candidates:
        container = soup.select_one(sel)
        if container:
            break

    if not container:
        # Fallback: just grab all text from main content column if needed
        container = soup.body

    text = container.get_text(" ", strip=True)
    return " ".join(text.split())  # normalize whitespace


def parse_archive_page(html: str, base_url: str, driver=None):
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
    
    print(f"  Found {len(rows)} article rows")

    for i, row in enumerate(rows, 1):
        try:
            # ---- title + link ----
            link = row.select_one("div.col-md-9.news-archive-title a.text-decoration-none")
            if not link:
                # Try alternative selectors
                link = row.select_one("a[href*='/news/'], a.article-link, h2 a, h3 a")
            
            if not link:
                print(f"  Skipping row {i}: No link found")
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
            time.sleep(1)  # Rate limiting between article fetches
            
            if driver:
                article_html = fetch_html_selenium(driver, url)
            else:
                # Fallback if driver not provided
                article_html = ""
            
            content = extract_article_body(article_html) if article_html else ""

            yield {
                "title": title,
                "url": url,
                "date": date,
                "content": content,
            }
        except Exception as e:
            print(f"  Error processing row {i}: {e}")
            continue


def scrape_thinkbroadband_archive(archive_url: str, driver):
    """Scrape articles from thinkbroadband archive using Selenium"""
    html = fetch_html_selenium(driver, archive_url)
    return list(parse_archive_page(html, archive_url, driver))


if __name__ == "__main__":
    driver = None
    try:
        print("Initializing Selenium WebDriver...")
        driver = get_driver()
        print("✅ WebDriver initialized successfully\n")
        
        # Try main news page first, then archive if that fails
        current_url = ARCHIVE_URL
        print(f"Trying to fetch articles from: {current_url}")
        
        try:
            articles = scrape_thinkbroadband_archive(current_url, driver)
        except Exception as e:
            if "403" in str(e) or "blocked" in str(e).lower():
                print(f"\nMain news page had issues. Trying archive page: {ARCHIVE_URL_ALT}")
                current_url = ARCHIVE_URL_ALT
                articles = scrape_thinkbroadband_archive(current_url, driver)
            else:
                raise
        
        print(f"\n✅ Found {len(articles)} articles\n")
        
        if articles:
            # Create output directory if it doesn't exist
            output_dir = "Scraped Output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate CSV filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = os.path.join(output_dir, f"thinkbroadband_articles_{timestamp}.csv")
            
            # Write to CSV
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Website', 'Article Title', 'Article content', 'Article Link', 'Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write articles
                for a in articles:
                    writer.writerow({
                        'Website': current_url,
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
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()
            print("Browser closed.")
