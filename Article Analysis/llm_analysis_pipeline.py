import pandas as pd
import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import ollama
from tqdm import tqdm
import time

class BroadbandAIAnalyzer:
    """
    LLM-based analysis pipeline for UK broadband industry articles.
    Analyzes articles using Ollama to identify AI trends, use cases, and sentiment.
    """

    # Use case categories as defined in project requirements
    USE_CASE_CATEGORIES = [
        "network_optimization",
        "customer_support",
        "predictive_maintenance",
        "marketing_automation",
        "security",
        "analytics",
        "network_planning",
        "qos_optimization",
        "other"
    ]

    def __init__(self,
                 scraped_output_dir="../Scraped Output",
                 model_name="kimi-k2-thinking:cloud",
                 fallback_model="qwen2.5:32b",
                 cache_file="analysis_cache.json"):
        """
        Initialize the analyzer.

        Args:
            scraped_output_dir: Directory containing scraped CSV files
            model_name: Primary Ollama model to use
            fallback_model: Fallback model if primary is unavailable
            cache_file: JSON file to cache analysis results
        """
        self.scraped_output_dir = scraped_output_dir
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.cache_file = os.path.join(os.path.dirname(__file__), cache_file)
        self.cache = self._load_cache()
        self.active_model = None

    def _load_cache(self) -> Dict:
        """Load cached analysis results."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
                return {}
        return {}

    def _save_cache(self):
        """Save analysis results to cache."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def _check_model_availability(self) -> str:
        """Check which model is available and return the active model name."""
        try:
            # Try to list models
            available_models = ollama.list()
            model_names = [m['name'] for m in available_models.get('models', [])]

            # Check if primary model is available
            if self.model_name in model_names:
                print(f"✓ Using primary model: {self.model_name}")
                return self.model_name

            # Check if fallback model is available
            if self.fallback_model in model_names:
                print(f"⚠ Primary model not available. Using fallback: {self.fallback_model}")
                return self.fallback_model

            # If neither is available, try the first available model
            if model_names:
                fallback = model_names[0]
                print(f"⚠ Configured models not available. Using: {fallback}")
                return fallback

            raise Exception("No Ollama models available")

        except Exception as e:
            print(f"Error checking model availability: {e}")
            print(f"Attempting to use configured model: {self.model_name}")
            return self.model_name

    def normalize_date(self, date_str: str) -> str:
        """
        Normalize various date formats to ISO format (YYYY-MM-DD).

        Args:
            date_str: Date string in various formats

        Returns:
            ISO formatted date string
        """
        if pd.isna(date_str) or not date_str or str(date_str).strip() == '':
            return ""

        date_str = str(date_str).strip()

        # Try various date format patterns
        patterns = [
            # "17th Nov 2025"
            (r'(\d{1,2})(?:st|nd|rd|th)\s+(\w+)\s+(\d{4})', '%d %b %Y'),
            # "2025-11-17"
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
            # "Date Posted:Monday, 17 November 2025"
            (r'Date Posted:\w+,\s+(\d{1,2})\s+(\w+)\s+(\d{4})', '%d %B %Y'),
            # "2025-03-07T09:11:00+00:00" (ISO 8601)
            (r'(\d{4})-(\d{2})-(\d{2})T', '%Y-%m-%d'),
        ]

        for pattern, date_format in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    # Extract date part
                    if 'T' in pattern:
                        date_part = date_str.split('T')[0]
                        return date_part
                    elif 'st|nd|rd|th' in pattern:
                        # Remove ordinal suffix
                        clean_date = re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', date_str)
                        parsed = datetime.strptime(clean_date, date_format)
                        return parsed.strftime('%Y-%m-%d')
                    elif 'Date Posted:' in date_str:
                        # Extract just the date part after the day name
                        date_part = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', date_str).group(1)
                        parsed = datetime.strptime(date_part, date_format)
                        return parsed.strftime('%Y-%m-%d')
                    else:
                        parsed = datetime.strptime(date_str, date_format)
                        return parsed.strftime('%Y-%m-%d')
                except Exception:
                    continue

        # If no pattern matched, return as-is
        print(f"Warning: Could not parse date: {date_str}")
        return date_str

    def normalize_source(self, url: str) -> str:
        """
        Map URLs to clean source names.

        Args:
            url: Source URL

        Returns:
            Clean source name
        """
        if pd.isna(url) or not url:
            return "Unknown"

        url = str(url).lower()

        if 'fibrenews' in url or 'fibernews' in url:
            return "FibreNews"
        elif 'ispreview' in url:
            return "ISPreview UK"
        elif 'thinkbroadband' in url:
            return "ThinkBroadband"
        else:
            return "Unknown"

    def clean_content(self, content: str) -> str:
        """
        Clean article content by removing HTML artifacts and normalizing whitespace.

        Args:
            content: Raw article content

        Returns:
            Cleaned content
        """
        if pd.isna(content) or not content:
            return ""

        content = str(content)

        # Remove common HTML/JavaScript artifacts from failed scrapes
        if 'Verifying you are human' in content or 'Cloudflare' in content:
            return "[Content unavailable - blocked by anti-bot protection]"

        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()

        return content

    def contains_ai_keywords(self, title: str, content: str) -> bool:
        """
        Check if article contains AI-related keywords (case-insensitive).
        This is used to pre-filter articles before expensive LLM analysis.

        IMPORTANT: Searches BOTH title AND content for AI keywords.

        Args:
            title: Article title
            content: Article content (full article text)

        Returns:
            True if AI keywords found in title OR content, False otherwise
        """
        # AI-related keywords to search for
        ai_keywords = [
            r'\bAI\b',
            r'\bartificial intelligence\b',
            r'\bmachine learning\b',
            r'\bML\b',
            r'\bLLMs?\b',
            r'\blarge language models?\b',
            r'\bOpenAI\b',
            r'\bAnthropic\b',
            r'\bClaude\b',
            r'\bChatGPT\b',
            r'\bneural network',
            r'\bdeep learning\b',
            r'\bautomation\b',
            r'\bchatbots?\b',
            r'\bvirtual assistant',
            r'\bpredictive analytics\b',
            r'\bdata science\b',
            r'\balgorithm',
        ]

        # Combine BOTH title AND content for comprehensive search
        text = f"{title} {content}".lower()

        # Check each keyword pattern
        for keyword_pattern in ai_keywords:
            if re.search(keyword_pattern, text, re.IGNORECASE):
                return True

        return False

    def extract_ai_keywords_from_text(self, text: str) -> Tuple[List[str], int]:
        """
        Extract AI keywords found in a specific text (e.g., title only).

        Args:
            text: Text to search

        Returns:
            Tuple of (list of found keywords, count of keywords)
        """
        if not text:
            return ([], 0)

        text_lower = text.lower()
        found_keywords = []

        # AI keywords to search for
        keyword_patterns = {
            r'\bAI\b': 'AI',
            r'\bartificial intelligence\b': 'artificial intelligence',
            r'\bmachine learning\b': 'machine learning',
            r'\bML\b': 'ML',
            r'\bLLMs?\b': 'LLM',
            r'\blarge language models?\b': 'large language model',
            r'\bOpenAI\b': 'OpenAI',
            r'\bAnthropic\b': 'Anthropic',
            r'\bClaude\b': 'Claude',
            r'\bChatGPT\b': 'ChatGPT',
            r'\bneural network': 'neural network',
            r'\bdeep learning\b': 'deep learning',
            r'\bautomation\b': 'automation',
            r'\bchatbots?\b': 'chatbot',
            r'\bvirtual assistant': 'virtual assistant',
            r'\bpredictive analytics\b': 'predictive analytics',
        }

        for pattern, keyword_name in keyword_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                if keyword_name not in found_keywords:
                    found_keywords.append(keyword_name)

        return (found_keywords, len(found_keywords))

    def create_analysis_prompt(self, title: str, content: str, source: str, date: str) -> str:
        """
        Create a structured prompt for LLM analysis.

        Args:
            title: Article title
            content: Article content
            source: News source
            date: Publication date

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are analyzing UK broadband and telecommunications industry news articles to identify AI and machine learning trends.

Article Details:
- Title: {title}
- Source: {source}
- Date: {date}
- Content: {content[:3000]}{'...' if len(content) > 3000 else ''}

Your task is to analyze this article and provide a JSON response with the following information:

1. **has_ai_content** (boolean): Does this article mention AI, machine learning, automation, neural networks, or related technologies?

2. **ai_mentions** (array of strings): List ALL AI-related terms and phrases mentioned in the article. Examples: "AI", "artificial intelligence", "machine learning", "neural network", "deep learning", "LLM", "large language model", "automation", "chatbot", "predictive analytics", etc.

3. **ai_mention_count** (integer): Total number of times AI-related concepts are mentioned in the article.

4. **primary_use_case** (string): The PRIMARY AI use case category this article discusses. Choose from:
   - "network_optimization" - Traffic management, routing, capacity planning
   - "customer_support" - Chatbots, virtual assistants, help desk automation
   - "predictive_maintenance" - Fault prediction, anomaly detection, proactive repairs
   - "marketing_automation" - Personalization, targeting, campaign optimization
   - "security" - Threat detection, fraud prevention, intrusion detection
   - "analytics" - Data analysis, business intelligence, forecasting
   - "network_planning" - Infrastructure planning, deployment optimization
   - "qos_optimization" - Quality of Service management, bandwidth allocation
   - "other" - AI is mentioned but doesn't fit above categories
   - null - Article doesn't discuss AI

5. **primary_use_case_confidence** (float 0.0-1.0): How confident are you in the primary use case classification? 1.0 = very confident, 0.0 = not confident.

6. **ai_use_cases** (array of strings): ALL AI use case categories mentioned in the article (can include multiple). Use same categories as above.

7. **sentiment** (string): Overall sentiment toward AI in this article. Choose from:
   - "positive" - AI is presented as beneficial, innovative, or solving problems
   - "neutral" - AI is discussed factually without strong opinion
   - "negative" - AI is presented with concerns, criticism, or problems
   - "mixed" - Both positive and negative aspects discussed
   - "not_applicable" - Article doesn't discuss AI

8. **summary** (string): A concise 2-3 sentence summary of the article. If the article discusses AI, focus on the AI-related aspects. If it doesn't mention AI, provide a general summary.

IMPORTANT: Return ONLY valid JSON. No explanations, no markdown, just the JSON object.

Example response format:
{{
  "has_ai_content": true,
  "ai_mentions": ["AI", "machine learning", "chatbot"],
  "ai_mention_count": 5,
  "primary_use_case": "customer_support",
  "primary_use_case_confidence": 0.9,
  "ai_use_cases": ["customer_support", "analytics"],
  "sentiment": "positive",
  "summary": "The article discusses how a broadband provider is implementing AI-powered chatbots to improve customer support response times and satisfaction."
}}"""

        return prompt

    def analyze_article_with_llm(self, title: str, content: str, source: str, date: str, url: str) -> Dict:
        """
        Analyze a single article using the LLM.

        Args:
            title: Article title
            content: Article content
            source: News source
            date: Publication date
            url: Article URL

        Returns:
            Dictionary with analysis results
        """
        # Check cache first
        cache_key = url
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Skip articles with unavailable content
        if '[Content unavailable' in content:
            result = {
                'has_ai_content': False,
                'ai_mentions': [],
                'ai_mention_count': 0,
                'primary_use_case': None,
                'primary_use_case_confidence': 0.0,
                'ai_use_cases': [],
                'sentiment': 'not_applicable',
                'summary': 'Content unavailable - blocked by anti-bot protection'
            }
            self.cache[cache_key] = result
            return result

        # PRE-FILTER: Check if article contains AI keywords
        # If no AI keywords found, skip expensive LLM analysis
        if not self.contains_ai_keywords(title, content):
            result = {
                'has_ai_content': False,
                'ai_mentions': [],
                'ai_mention_count': 0,
                'primary_use_case': None,
                'primary_use_case_confidence': 0.0,
                'ai_use_cases': [],
                'sentiment': 'not_applicable',
                'summary': f'Article about {source} broadband/telecom news without AI mentions'
            }
            self.cache[cache_key] = result
            return result

        # Create prompt
        prompt = self.create_analysis_prompt(title, content, source, date)

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                # Call Ollama
                response = ollama.chat(
                    model=self.active_model,
                    messages=[{
                        'role': 'user',
                        'content': prompt
                    }],
                    options={
                        'temperature': 0.3,  # Lower temperature for more consistent analysis
                    }
                )

                # Parse response
                response_text = response['message']['content'].strip()

                # Try to extract JSON from response (handle markdown code blocks)
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
                elif '```' in response_text:
                    # Remove any code block markers
                    response_text = re.sub(r'```[a-z]*\n?', '', response_text)

                # Parse JSON
                result = json.loads(response_text)

                # Validate and clean result
                result = self._validate_analysis_result(result)

                # Cache result
                self.cache[cache_key] = result

                return result

            except json.JSONDecodeError as e:
                print(f"JSON parsing error (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Response: {response_text[:200]}...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

            except Exception as e:
                print(f"Error analyzing article (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

        # If all retries failed, return default values
        print(f"Failed to analyze: {title}")
        return {
            'has_ai_content': False,
            'ai_mentions': [],
            'ai_mention_count': 0,
            'primary_use_case': None,
            'primary_use_case_confidence': 0.0,
            'ai_use_cases': [],
            'sentiment': 'not_applicable',
            'summary': 'Analysis failed - could not process article'
        }

    def _validate_analysis_result(self, result: Dict) -> Dict:
        """Validate and clean the LLM analysis result."""
        # Safely convert confidence to float, handling non-numeric values
        confidence_value = result.get('primary_use_case_confidence', 0.0)
        try:
            confidence_float = float(confidence_value)
            # Clamp to valid range [0.0, 1.0]
            confidence_float = max(0.0, min(1.0, confidence_float))
        except (ValueError, TypeError):
            # If conversion fails, default to 0.0
            confidence_float = 0.0
        
        # Ensure all required fields exist with defaults
        validated = {
            'has_ai_content': result.get('has_ai_content', False),
            'ai_mentions': result.get('ai_mentions', []),
            'ai_mention_count': result.get('ai_mention_count', 0),
            'primary_use_case': result.get('primary_use_case'),
            'primary_use_case_confidence': confidence_float,
            'ai_use_cases': result.get('ai_use_cases', []),
            'sentiment': result.get('sentiment', 'not_applicable'),
            'summary': result.get('summary', '')
        }

        # Ensure lists are actually lists
        if not isinstance(validated['ai_mentions'], list):
            validated['ai_mentions'] = []
        if not isinstance(validated['ai_use_cases'], list):
            validated['ai_use_cases'] = []

        # Validate use cases are in allowed categories
        valid_use_cases = [uc for uc in validated['ai_use_cases']
                          if uc in self.USE_CASE_CATEGORIES]
        validated['ai_use_cases'] = valid_use_cases

        if validated['primary_use_case'] not in self.USE_CASE_CATEGORIES:
            validated['primary_use_case'] = None

        # Validate sentiment
        valid_sentiments = ['positive', 'neutral', 'negative', 'mixed', 'not_applicable']
        if validated['sentiment'] not in valid_sentiments:
            validated['sentiment'] = 'not_applicable'

        return validated

    def load_and_normalize_csvs(self) -> pd.DataFrame:
        """
        Load all CSV files and normalize them into a unified format.

        Returns:
            DataFrame with normalized data
        """
        csv_files = list(Path(self.scraped_output_dir).glob("*.csv"))

        if not csv_files:
            raise Exception(f"No CSV files found in {self.scraped_output_dir}")

        print(f"Loading {len(csv_files)} CSV file(s)...")

        all_data = []

        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)

                # Check for required columns
                if 'Article Title' not in df.columns:
                    print(f"Warning: Skipping {csv_file.name} - no 'Article Title' column")
                    continue

                # Normalize each row
                for _, row in df.iterrows():
                    normalized = {
                        'source': self.normalize_source(row.get('Website', '')),
                        'date': self.normalize_date(row.get('Date', '')),
                        'title': str(row.get('Article Title', '')).strip(),
                        'url': str(row.get('Article Link', '')).strip(),
                        'content': self.clean_content(row.get('Article content', '')),
                        'word_count': len(str(row.get('Article content', '')).split())
                    }

                    # Skip empty titles
                    if not normalized['title'] or normalized['title'] == 'nan':
                        continue

                    all_data.append(normalized)

                print(f"  ✓ Loaded {csv_file.name}: {len(df)} articles")

            except Exception as e:
                print(f"  ✗ Error loading {csv_file.name}: {e}")

        if not all_data:
            raise Exception("No valid articles found in CSV files")

        df = pd.DataFrame(all_data)

        # Remove duplicates based on URL
        df = df.drop_duplicates(subset=['url'], keep='first')

        print(f"\nTotal unique articles loaded: {len(df)}")

        return df

    def process_articles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process all articles through LLM analysis.

        Args:
            df: DataFrame with normalized article data

        Returns:
            DataFrame with LLM analysis results added
        """
        print(f"\nProcessing {len(df)} articles through LLM analysis...")
        print(f"Using model: {self.active_model}")

        results = []

        # Process with progress bar
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Analyzing articles"):
            try:
                analysis = self.analyze_article_with_llm(
                    title=row['title'],
                    content=row['content'],
                    source=row['source'],
                    date=row['date'],
                    url=row['url']
                )

                # Extract AI keywords from title specifically
                title_ai_keywords, title_ai_count = self.extract_ai_keywords_from_text(row['title'])

                # Combine original data with analysis
                result = {
                    **row.to_dict(),
                    'primary_use_case': analysis['primary_use_case'],
                    'primary_use_case_confidence': analysis['primary_use_case_confidence'],
                    'ai_use_cases': ','.join(analysis['ai_use_cases']),
                    'sentiment': analysis['sentiment'],
                    'ai_mention_count': analysis['ai_mention_count'],
                    'ai_mentions': ','.join(analysis['ai_mentions']),
                    'title_ai_mentions': ','.join(title_ai_keywords),
                    'title_ai_mention_count': title_ai_count,
                    'summary': analysis['summary']
                }

                results.append(result)

                # Save cache periodically (every 10 articles)
                if (idx + 1) % 10 == 0:
                    self._save_cache()

            except Exception as e:
                print(f"\nError processing article {idx}: {e}")
                # Add row with empty analysis on error
                results.append({
                    **row.to_dict(),
                    'primary_use_case': None,
                    'primary_use_case_confidence': 0.0,
                    'ai_use_cases': '',
                    'sentiment': 'not_applicable',
                    'ai_mention_count': 0,
                    'ai_mentions': '',
                    'title_ai_mentions': '',
                    'title_ai_mention_count': 0,
                    'summary': 'Analysis error'
                })

        # Save final cache
        self._save_cache()

        return pd.DataFrame(results)

    def generate_unified_csv(self, output_file="unified_ai_analysis.csv") -> str:
        """
        Main pipeline: Load CSVs, analyze articles, generate unified output.

        Args:
            output_file: Output CSV filename

        Returns:
            Path to generated CSV file
        """
        print("="*80)
        print("BROADBAND AI TRENDS ANALYSIS PIPELINE")
        print("="*80)

        # Check model availability
        self.active_model = self._check_model_availability()

        # Load and normalize data
        df = self.load_and_normalize_csvs()

        # Process through LLM
        results_df = self.process_articles(df)

        # Reorder columns to match target schema (with title AI mentions added)
        column_order = [
            'source', 'date', 'title', 'url',
            'primary_use_case', 'primary_use_case_confidence',
            'ai_use_cases', 'sentiment',
            'ai_mention_count', 'ai_mentions',
            'title_ai_mention_count', 'title_ai_mentions',
            'word_count', 'summary'
        ]

        # Ensure all columns exist
        for col in column_order:
            if col not in results_df.columns:
                results_df[col] = None

        results_df = results_df[column_order]

        # Save to CSV
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        results_df.to_csv(output_path, index=False, encoding='utf-8')

        print(f"\n{'='*80}")
        print(f"✓ Analysis complete!")
        print(f"✓ Unified CSV saved to: {output_path}")
        print(f"✓ Total articles processed: {len(results_df)}")
        print(f"✓ Articles with AI content: {len(results_df[results_df['ai_mention_count'] > 0])}")
        print(f"{'='*80}")

        return output_path


def main():
    """Main execution function."""
    # Initialize analyzer
    # Using kimi-k2-thinking:cloud (Ollama Cloud model with advanced reasoning)
    analyzer = BroadbandAIAnalyzer(
        model_name="kimi-k2-thinking:cloud",
        fallback_model="qwen2.5:32b"
    )

    # Run the pipeline
    output_path = analyzer.generate_unified_csv()

    print(f"\nOutput file ready: {output_path}")
    print("\nNext steps:")
    print("1. Review the unified CSV for accuracy")
    print("2. Use the data for trend analysis, visualization, or reporting")


if __name__ == "__main__":
    main()
