"""
Big Firm Article Scraper and Analyzer
Scrapes URLs from Excel, extracts content, and runs LLM analysis to generate unified CSV.
"""

import pandas as pd
import openpyxl
import requests
from bs4 import BeautifulSoup
import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List
import ollama
from tqdm import tqdm
import time

# Add parent directory to path to import from llm_analysis_pipeline
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Article Analysis'))
from llm_analysis_pipeline import BroadbandAIAnalyzer

class BigFirmScraperAnalyzer:
    """
    Scraper and analyzer for big firm articles from Excel.
    """

    def __init__(self,
                 excel_file="AI Articles By Company.xlsx",
                 model_name="qwen2.5:32b",
                 fallback_model="qwen2.5:32b",
                 cache_file="big_firm_cache.json"):
        self.excel_file = os.path.join(os.path.dirname(__file__), excel_file)
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.cache_file = os.path.join(os.path.dirname(__file__), cache_file)
        self.cache = self._load_cache()
        self.active_model = None

        # Create analyzer instance to reuse its methods
        self.analyzer = BroadbandAIAnalyzer(
            model_name=model_name,
            fallback_model=fallback_model
        )

    def _load_cache(self) -> Dict:
        """Load cached scraped content and analysis."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
                return {}
        return {}

    def _save_cache(self):
        """Save cache."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def read_excel_with_urls(self) -> pd.DataFrame:
        """Read Excel file and extract URLs from hyperlinks."""
        # Load workbook to get hyperlinks
        wb = openpyxl.load_workbook(self.excel_file)
        ws = wb.active

        # Extract data with URLs
        data = []
        for idx, row_cells in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
            # Stop at empty rows (check Company column)
            if len(row_cells) < 3 or not row_cells[1].value:
                break

            company = row_cells[1].value  # Column B
            article_cell = row_cells[2]   # Column C
            date_cell = row_cells[3] if len(row_cells) > 3 else None     # Column D
            use_case_cell = row_cells[4] if len(row_cells) > 4 else None  # Column E
            notes_cell = row_cells[5] if len(row_cells) > 5 else None  # Column F

            # Extract URL from hyperlink
            url = article_cell.hyperlink.target if article_cell.hyperlink else None
            title = article_cell.value

            # If no hyperlink but value is URL
            if not url and title and isinstance(title, str) and title.startswith('http'):
                url = title

            if url and company:  # Only add if we have URL and company
                data.append({
                    'company': company,
                    'title': title if title and not title.startswith('http') else url,
                    'url': url,
                    'date': date_cell.value if date_cell else None,
                    'manual_use_case': use_case_cell.value if use_case_cell else None,
                    'notes': notes_cell.value if notes_cell else None
                })

        df = pd.DataFrame(data)
        return df

    def scrape_url(self, url: str) -> str:
        """Scrape content from URL."""
        # Check cache first
        if url in self.cache and 'content' in self.cache[url]:
            return self.cache[url]['content']

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Limit to reasonable length
            content = text[:10000]

            # Cache the content
            if url not in self.cache:
                self.cache[url] = {}
            self.cache[url]['content'] = content

            return content

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return f"[Content unavailable - {str(e)[:100]}]"

    def analyze_all(self, output_file="big_firm_unified_analysis.csv"):
        """Main pipeline: scrape and analyze all articles."""

        print("="*80)
        print("BIG FIRM SCRAPER & ANALYZER")
        print("="*80)

        # Check model availability
        self.active_model = self.analyzer._check_model_availability()
        self.analyzer.active_model = self.active_model

        # Read Excel
        print(f"\nReading Excel file: {self.excel_file}")
        df = self.read_excel_with_urls()
        print(f"Found {len(df)} articles with URLs")
        print(f"Companies: {df['company'].unique().tolist()}")

        results = []

        # Process each article
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Scraping & analyzing"):
            url = row['url']
            title = row['title']
            company = row['company']
            date = row['date']

            # Scrape content
            content = self.scrape_url(url)

            # Normalize date
            date_str = self.analyzer.normalize_date(str(date))

            # Check if scraping failed
            content_unavailable = content.startswith('[Content unavailable')

            # If content unavailable, analyze based on title/URL only
            if content_unavailable:
                # Use title and URL for analysis with a note
                analysis_content = f"TITLE: {title}\nURL: {url}\nNOTE: Content could not be scraped. Analysis based on title only. Manual review required."
                print(f"  ⚠ Scraping failed for {company}: {title[:60]}... - Analyzing title only")
            else:
                analysis_content = content

            # Analyze using the main pipeline's logic
            analysis = self.analyzer.analyze_article_with_llm(
                title=title,
                content=analysis_content,
                source=company,  # Use company as source
                date=date_str,
                url=url
            )

            # Extract title AI mentions
            title_ai_mentions, title_ai_count = self.analyzer.extract_ai_keywords_from_text(title)

            # Word count
            word_count = len(content.split()) if content and not content.startswith('[Content unavailable') else 0

            # Get summary and add manual review note if needed
            summary = analysis.get('summary', 'N/A')
            if content_unavailable:
                summary = f"[MANUAL REVIEW REQUIRED - Content unavailable] {summary}"

            # Build result row
            result = {
                'source': company,
                'date': date_str,
                'title': title,
                'url': url,
                'primary_use_case': analysis.get('primary_use_case'),
                'primary_use_case_confidence': analysis.get('primary_use_case_confidence', 0.0),
                'ai_use_cases': ','.join(analysis.get('ai_use_cases', [])),
                'sentiment': analysis.get('sentiment', 'not_applicable'),
                'ai_mention_count': analysis.get('ai_mention_count', 0),
                'ai_mentions': ','.join(analysis.get('ai_mentions', [])),
                'title_ai_mention_count': title_ai_count,
                'title_ai_mentions': ','.join(title_ai_mentions),
                'word_count': word_count,
                'summary': summary
            }

            results.append(result)

            # Save cache periodically
            if (idx + 1) % 5 == 0:
                self._save_cache()
                self.analyzer._save_cache()

        # Save final cache
        self._save_cache()
        self.analyzer._save_cache()

        # Create DataFrame
        results_df = pd.DataFrame(results)

        # Save to CSV
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        results_df.to_csv(output_path, index=False, encoding='utf-8')

        print(f"\n{'='*80}")
        print(f"✓ Analysis complete!")
        print(f"✓ Saved to: {output_path}")
        print(f"✓ Total articles: {len(results_df)}")
        print(f"✓ Articles with AI content: {results_df['ai_mention_count'].gt(0).sum()}")
        print(f"{'='*80}")

        # Print summary
        print("\n📊 SUMMARY BY COMPANY:")
        print("-"*50)
        company_stats = results_df.groupby('source').agg({
            'title': 'count',
            'ai_mention_count': lambda x: (x > 0).sum()
        }).reset_index()
        company_stats.columns = ['Company', 'Total Articles', 'AI Articles']
        print(company_stats.to_string(index=False))

        print("\n📊 SUMMARY BY USE CASE:")
        print("-"*50)
        use_case_counts = results_df[results_df['primary_use_case'].notna()]['primary_use_case'].value_counts()
        print(use_case_counts.to_string())

        return output_path


def main():
    """Main execution."""
    analyzer = BigFirmScraperAnalyzer(
        model_name="qwen2.5:32b",
        fallback_model="qwen2.5:32b"
    )

    analyzer.analyze_all()


if __name__ == "__main__":
    main()
