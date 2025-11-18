import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from urllib.parse import urljoin

BASE_URL = "https://fibrnews.co.uk/"  # replace with actual site root if different
START_PAGE = "https://fibrnews.co.uk/all-news/"  # listing page

def scrape_page(url):
    print(f"Scraping: {url}")
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code != 200:
        print(f"Failed: {url}")
        return []
    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.find_all("article")
    data = []

    for art in articles:
        title_tag = art.find("header")
        title = title_tag.get_text(strip=True) if title_tag else ""

        summary_tag = art.find("div", class_="entry-summary")
        summary = summary_tag.get_text(" ", strip=True) if summary_tag else ""

        link_tag = art.find("a", href=True)
        url_full = urljoin(BASE_URL, link_tag["href"]) if link_tag else ""

        date_tag = art.find("time")
        date = date_tag["datetime"] if date_tag and date_tag.has_attr("datetime") else ""

        ai_mention = bool(re.search(r"\b(ai|artificial intelligence)\b", summary + " " + title, re.IGNORECASE))

        data.append({
            "title": title,
            "summary": summary,
            "url": url_full,
            "publication_date": date,
            "ai_mention": ai_mention,
            "source": url
        })

    return data

def get_all_pages(start_url, max_pages=10):
    page_url = start_url
    all_data = []
    for i in range(max_pages):
        page_data = scrape_page(page_url)
        if not page_data:
            break
        all_data.extend(page_data)

        soup = BeautifulSoup(requests.get(page_url).text, "html.parser")
        next_link = soup.find("a", text=re.compile("Next", re.IGNORECASE))
        if not next_link:
            break
        page_url = urljoin(BASE_URL, next_link["href"])
        time.sleep(1)
    return all_data

def main():
    articles = get_all_pages(START_PAGE)
    df = pd.DataFrame(articles)
    df.to_csv("broadband_ai_mentions.csv", index=False)
    df.to_json("broadband_ai_mentions.json", orient="records", indent=2)
    print(f"✅ Scraped {len(df)} articles. Saved to broadband_ai_mentions.csv and .json")

if __name__ == "__main__":
    main()
