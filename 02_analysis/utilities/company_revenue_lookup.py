#!/usr/bin/env python3
"""
Company Revenue and Employee Count Lookup Script
Uses GPT-oss through Ollama with web search to fetch latest company financial data.
"""

import ollama
import json
import re
import time
import sys
import os
from typing import Dict, Optional, Tuple
from pathlib import Path
import pandas as pd


class CompanyDataLookup:
    """
    Lookup company revenue and employee count using GPT-oss through Ollama with web search.
    """
    
    def __init__(self, 
                 model_name: str = "gpt-oss:20b-cloud",
                 fallback_model: str = "gpt-oss:20b",
                 cache_file: str = "company_data_cache.json"):
        """
        Initialize the lookup tool.
        
        Args:
            model_name: Primary Ollama model (prefer cloud version with web search)
            fallback_model: Fallback model if primary unavailable
            cache_file: JSON file to cache results
        """
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.active_model = None
        self._initialize_model()
    
    def _load_cache(self) -> Dict:
        """Load cached company data."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def _initialize_model(self):
        """Initialize and verify model availability."""
        try:
            available = ollama.list()
            model_names = [m.get('name') or m.get('model', '') for m in available.get('models', [])]
            
            if self.model_name in model_names:
                self.active_model = self.model_name
                print(f"✓ Using model: {self.active_model}")
            elif self.fallback_model in model_names:
                self.active_model = self.fallback_model
                print(f"✓ Using fallback model: {self.active_model}")
            else:
                # Try to find any gpt-oss model
                gpt_oss_models = [m for m in model_names if 'gpt-oss' in m.lower()]
                if gpt_oss_models:
                    self.active_model = gpt_oss_models[0]
                    print(f"✓ Using available GPT-oss model: {self.active_model}")
                else:
                    raise ValueError(f"Neither {self.model_name} nor {self.fallback_model} found. Available models: {model_names}")
        except Exception as e:
            print(f"Error initializing model: {e}")
            raise
    
    def _create_lookup_prompt(self, company_name: str, uk_brand: str) -> str:
        """
        Create a prompt that instructs the model to search for company data.
        
        Args:
            company_name: The company name
            uk_brand: The UK-specific brand name
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a financial research assistant. Use web search to find the LATEST available information about the following UK company.

Company Name: {company_name}
UK Brand Name: {uk_brand}

Please search the internet for the most recent:
1. Annual revenue (in GBP, USD, or EUR - specify currency)
2. Employee count (total number of employees)

Search for information from:
- Official company websites and investor relations pages
- Companies House (UK company registry)
- Recent financial reports, annual reports, or press releases
- Reputable financial news sources (Financial Times, Reuters, Bloomberg, etc.)
- Company LinkedIn pages or official corporate information

IMPORTANT:
- Use web search to get the LATEST available data (2024 or 2025 if available)
- If multiple revenue figures exist, use the most recent annual revenue
- For employee count, use the most recent figure available
- If data is not available, clearly state that

Return your findings in the following JSON format:
{{
  "company_name": "{company_name}",
  "uk_brand": "{uk_brand}",
  "revenue": {{
    "amount": "1234567890",
    "currency": "GBP",
    "year": "2024",
    "source": "URL or source name",
    "note": "Annual revenue or other description"
  }},
  "employee_count": {{
    "count": "5000",
    "year": "2024",
    "source": "URL or source name",
    "note": "Total employees or other description"
  }},
  "data_quality": "high|medium|low",
  "search_timestamp": "current date/time"
}}

If information is not found, use null for missing fields but still return valid JSON."""
        
        return prompt
    
    def lookup_company(self, company_name: str, uk_brand: str, use_cache: bool = True) -> Dict:
        """
        Lookup company revenue and employee count.
        
        Args:
            company_name: The company name
            uk_brand: The UK-specific brand name
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with company data
        """
        # Create cache key
        cache_key = f"{company_name.lower()}_{uk_brand.lower()}"
        
        # Check cache
        if use_cache and cache_key in self.cache:
            print(f"✓ Found cached data for {company_name} ({uk_brand})")
            return self.cache[cache_key]
        
        print(f"🔍 Searching for {company_name} ({uk_brand})...")
        
        prompt = self._create_lookup_prompt(company_name, uk_brand)
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Call Ollama with web search enabled
                response = ollama.chat(
                    model=self.active_model,
                    messages=[{
                        'role': 'user',
                        'content': prompt
                    }],
                    options={
                        'temperature': 0.1,  # Low temperature for factual data
                    }
                )
                
                response_text = response['message']['content'].strip()
                
                # Extract JSON from response
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
                elif '```' in response_text:
                    # Remove any code block markers
                    response_text = re.sub(r'```[a-z]*\n?', '', response_text)
                
                # Find JSON object boundaries
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    response_text = response_text[start:end]
                
                # Parse JSON
                result = json.loads(response_text)
                
                # Add metadata
                result['lookup_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                result['model_used'] = self.active_model
                
                # Cache result
                self.cache[cache_key] = result
                self._save_cache()
                
                print(f"✓ Successfully retrieved data for {company_name}")
                return result
                
            except json.JSONDecodeError as e:
                print(f"⚠ JSON parsing error (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Response preview: {response_text[:300]}...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return {
                        "company_name": company_name,
                        "uk_brand": uk_brand,
                        "error": f"Failed to parse JSON after {max_retries} attempts",
                        "raw_response": response_text[:500]
                    }
            
            except Exception as e:
                error_msg = str(e).lower()
                if 'rate limit' in error_msg or '429' in error_msg:
                    print(f"⚠ Rate limit hit (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(f"Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                else:
                    print(f"⚠ Error (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                
                return {
                    "company_name": company_name,
                    "uk_brand": uk_brand,
                    "error": str(e),
                    "lookup_timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
        
        return {
            "company_name": company_name,
            "uk_brand": uk_brand,
            "error": "Failed after all retries",
            "lookup_timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def lookup_batch(self, companies: list, output_csv: str = "company_revenue_data.csv") -> pd.DataFrame:
        """
        Lookup multiple companies and save to CSV.
        
        Args:
            companies: List of tuples (company_name, uk_brand)
            output_csv: Output CSV file path
            
        Returns:
            DataFrame with results
        """
        results = []
        
        for i, (company_name, uk_brand) in enumerate(companies, 1):
            print(f"\n[{i}/{len(companies)}] Processing: {company_name} ({uk_brand})")
            result = self.lookup_company(company_name, uk_brand)
            results.append(result)
            
            # Small delay between requests
            if i < len(companies):
                time.sleep(1)
        
        # Convert to DataFrame
        df = self._results_to_dataframe(results)
        
        # Save to CSV
        df.to_csv(output_csv, index=False)
        print(f"\n✓ Saved results to {output_csv}")
        
        return df
    
    def _results_to_dataframe(self, results: list) -> pd.DataFrame:
        """Convert results list to DataFrame."""
        rows = []
        for r in results:
            row = {
                'company_name': r.get('company_name', ''),
                'uk_brand': r.get('uk_brand', ''),
                'revenue_amount': r.get('revenue', {}).get('amount', '') if isinstance(r.get('revenue'), dict) else '',
                'revenue_currency': r.get('revenue', {}).get('currency', '') if isinstance(r.get('revenue'), dict) else '',
                'revenue_year': r.get('revenue', {}).get('year', '') if isinstance(r.get('revenue'), dict) else '',
                'revenue_source': r.get('revenue', {}).get('source', '') if isinstance(r.get('revenue'), dict) else '',
                'employee_count': r.get('employee_count', {}).get('count', '') if isinstance(r.get('employee_count'), dict) else '',
                'employee_year': r.get('employee_count', {}).get('year', '') if isinstance(r.get('employee_count'), dict) else '',
                'employee_source': r.get('employee_count', {}).get('source', '') if isinstance(r.get('employee_count'), dict) else '',
                'data_quality': r.get('data_quality', ''),
                'lookup_timestamp': r.get('lookup_timestamp', ''),
                'model_used': r.get('model_used', ''),
                'error': r.get('error', '')
            }
            rows.append(row)
        
        return pd.DataFrame(rows)


def main():
    """Main execution function."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(
        description='Lookup company revenue and employee count using GPT-oss through Ollama'
    )
    parser.add_argument('--company', type=str, help='Company name')
    parser.add_argument('--uk-brand', type=str, dest='uk_brand', help='UK brand name')
    parser.add_argument('--csv', type=str, help='CSV file with columns: company_name, uk_brand')
    parser.add_argument('--output', type=str, default='company_revenue_data.csv', help='Output CSV file')
    parser.add_argument('--model', type=str, default='gpt-oss:20b-cloud', help='Ollama model name')
    parser.add_argument('--fallback', type=str, default='gpt-oss:20b', help='Fallback model name')
    parser.add_argument('--no-cache', action='store_true', help='Disable cache')
    
    args = parser.parse_args()
    
    # Initialize lookup tool
    lookup = CompanyDataLookup(
        model_name=args.model,
        fallback_model=args.fallback
    )
    
    # Single company lookup
    if args.company and args.uk_brand:
        result = lookup.lookup_company(args.company, args.uk_brand, use_cache=not args.no_cache)
        print("\n" + "="*60)
        print("RESULT:")
        print("="*60)
        print(json.dumps(result, indent=2))
        return
    
    # Batch lookup from CSV
    if args.csv:
        if not os.path.exists(args.csv):
            print(f"Error: CSV file not found: {args.csv}")
            return
        
        df = pd.read_csv(args.csv)
        
        if 'company_name' not in df.columns or 'uk_brand' not in df.columns:
            print("Error: CSV must have 'company_name' and 'uk_brand' columns")
            return
        
        companies = [(row['company_name'], row['uk_brand']) for _, row in df.iterrows()]
        lookup.lookup_batch(companies, output_csv=args.output)
        return
    
    # Interactive mode
    print("Company Revenue & Employee Count Lookup")
    print("="*60)
    print("\nEnter company information (or 'quit' to exit):\n")
    
    while True:
        company_name = input("Company Name: ").strip()
        if company_name.lower() in ['quit', 'exit', 'q']:
            break
        
        uk_brand = input("UK Brand Name: ").strip()
        if uk_brand.lower() in ['quit', 'exit', 'q']:
            break
        
        result = lookup.lookup_company(company_name, uk_brand, use_cache=not args.no_cache)
        
        print("\n" + "="*60)
        print("RESULT:")
        print("="*60)
        print(json.dumps(result, indent=2))
        print("\n")


if __name__ == "__main__":
    main()

