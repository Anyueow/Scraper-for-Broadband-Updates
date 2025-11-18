"""
LLM Analysis Pipeline for Big Firm AI Articles.
Analyzes company-specific AI use cases in UK telecom industry.
"""

import pandas as pd
import os
import json
import re
from datetime import datetime
from typing import Dict, List
import ollama
from tqdm import tqdm
import time

class BigFirmAnalyzer:
    """
    LLM-based analysis for big firm AI articles.
    """

    # Use case categories
    USE_CASE_CATEGORIES = [
        "network_optimization",
        "customer_support",
        "predictive_maintenance",
        "marketing_automation",
        "security",
        "analytics",
        "network_planning",
        "qos_optimization",
        "internal_operations",
        "cybersecurity",
        "other"
    ]

    def __init__(self,
                 model_name="kimi-k2-thinking:cloud",
                 fallback_model="qwen2.5:32b",
                 cache_file="big_firm_cache.json"):
        """Initialize the analyzer."""
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
        """Check which model is available."""
        try:
            available_models = ollama.list()
            model_names = []
            for m in available_models.get('models', []):
                name = m.get('name') or m.get('model', '')
                if name:
                    model_names.append(name)

            if self.model_name in model_names:
                print(f"✓ Using primary model: {self.model_name}")
                return self.model_name

            if self.fallback_model in model_names:
                print(f"⚠ Using fallback: {self.fallback_model}")
                return self.fallback_model

            # If neither found, just use qwen2.5:32b as default
            if model_names:
                print(f"Using available model: {model_names[0]}")
                return model_names[0]

            # Default to qwen2.5:32b
            print(f"Using default model: qwen2.5:32b")
            return "qwen2.5:32b"

        except Exception as e:
            print(f"Model check error: {e}")
            print(f"Using default model: qwen2.5:32b")
            return "qwen2.5:32b"

    def create_analysis_prompt(self, company: str, article_title: str, date: str,
                                existing_use_case: str, notes: str) -> str:
        """Create prompt for LLM analysis."""
        prompt = f"""You are analyzing AI adoption by major UK telecommunications companies.

Article Information:
- Company: {company}
- Article Title: {article_title}
- Date: {date}
- Manually Tagged Use Case: {existing_use_case if pd.notna(existing_use_case) else 'Not specified'}
- Additional Notes: {notes if pd.notna(notes) else 'None'}

Based on this information, provide a detailed JSON analysis with:

1. **standardized_use_case** (string): Map the use case to one of these categories:
   - "network_optimization" - Traffic management, routing, capacity
   - "customer_support" - Chatbots, virtual assistants, help desk
   - "predictive_maintenance" - Fault prediction, anomaly detection
   - "marketing_automation" - Personalization, targeting
   - "security" - Threat detection, fraud prevention
   - "analytics" - Data analysis, business intelligence
   - "network_planning" - Infrastructure planning
   - "qos_optimization" - Quality of Service
   - "internal_operations" - Internal process automation
   - "cybersecurity" - Cyber threat protection
   - "other" - If doesn't fit above

2. **confidence** (float 0.0-1.0): How confident are you in this categorization?

3. **sentiment** (string): Based on the article title, is the company's AI adoption portrayed as:
   - "positive" - Beneficial, innovative, successful
   - "neutral" - Factual reporting
   - "negative" - Concerns, problems, challenges
   - "mixed" - Both positive and negative aspects

4. **strategic_importance** (string): Rate the strategic importance of this AI initiative:
   - "high" - Core business transformation
   - "medium" - Significant operational improvement
   - "low" - Incremental optimization

5. **maturity_stage** (string): What stage is this AI initiative?
   - "pilot" - Testing/experimental
   - "deployment" - Active rollout
   - "scaled" - Fully operational at scale
   - "unknown" - Cannot determine

6. **key_technologies** (array): List specific AI technologies mentioned or implied:
   - Examples: "chatbot", "NLP", "machine learning", "neural network", "automation", "predictive analytics"

7. **business_impact** (string): One sentence describing the expected business impact.

8. **summary** (string): 2-3 sentence summary of the AI initiative and its significance.

Return ONLY valid JSON, no explanations.

Example:
{{
  "standardized_use_case": "customer_support",
  "confidence": 0.9,
  "sentiment": "positive",
  "strategic_importance": "high",
  "maturity_stage": "deployment",
  "key_technologies": ["chatbot", "NLP", "automation"],
  "business_impact": "Improved customer service response times and satisfaction scores.",
  "summary": "BT is implementing AI-powered customer service tools to transform their support experience. This represents a significant investment in customer-facing AI technology."
}}"""

        return prompt

    def analyze_article(self, company: str, article_title: str, date: str,
                        existing_use_case: str, notes: str) -> Dict:
        """Analyze a single article using the LLM."""

        # Cache key based on article title
        cache_key = f"{company}_{article_title}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Create prompt
        prompt = self.create_analysis_prompt(company, article_title, date,
                                              existing_use_case, notes)

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = ollama.chat(
                    model=self.active_model,
                    messages=[{
                        'role': 'user',
                        'content': prompt
                    }],
                    options={
                        'temperature': 0.3,
                    }
                )

                response_text = response['message']['content'].strip()

                # Extract JSON
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
                elif '```' in response_text:
                    response_text = re.sub(r'```[a-z]*\n?', '', response_text)

                result = json.loads(response_text)
                result = self._validate_result(result)

                self.cache[cache_key] = result
                return result

            except json.JSONDecodeError as e:
                print(f"JSON error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

            except Exception as e:
                print(f"Error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

        # Default on failure
        return {
            'standardized_use_case': 'other',
            'confidence': 0.0,
            'sentiment': 'neutral',
            'strategic_importance': 'unknown',
            'maturity_stage': 'unknown',
            'key_technologies': [],
            'business_impact': 'Analysis failed',
            'summary': 'Could not analyze this article'
        }

    def _validate_result(self, result: Dict) -> Dict:
        """Validate and clean the result."""
        confidence_value = result.get('confidence', 0.0)
        try:
            confidence_float = float(confidence_value)
            confidence_float = max(0.0, min(1.0, confidence_float))
        except (ValueError, TypeError):
            confidence_float = 0.0

        validated = {
            'standardized_use_case': result.get('standardized_use_case', 'other'),
            'confidence': confidence_float,
            'sentiment': result.get('sentiment', 'neutral'),
            'strategic_importance': result.get('strategic_importance', 'unknown'),
            'maturity_stage': result.get('maturity_stage', 'unknown'),
            'key_technologies': result.get('key_technologies', []),
            'business_impact': result.get('business_impact', ''),
            'summary': result.get('summary', '')
        }

        if not isinstance(validated['key_technologies'], list):
            validated['key_technologies'] = []

        return validated

    def analyze_all(self, input_file="AI Articles By Company.xlsx",
                    output_file="big_firm_analysis_results.csv"):
        """Run analysis on all articles."""

        print("="*80)
        print("BIG FIRM AI ANALYSIS PIPELINE")
        print("="*80)

        # Check model
        self.active_model = self._check_model_availability()

        # Load data
        input_path = os.path.join(os.path.dirname(__file__), input_file)
        df = pd.read_excel(input_path)

        print(f"\nLoaded {len(df)} articles from {input_file}")
        print(f"Companies: {df['Company'].unique().tolist()}")
        print(f"\nUsing model: {self.active_model}")

        results = []

        # Process each article
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Analyzing articles"):
            analysis = self.analyze_article(
                company=row['Company'],
                article_title=row['Article'],
                date=str(row['Date']),
                existing_use_case=row.get('AI Use Case', ''),
                notes=row.get('Other Notes', '')
            )

            result = {
                'company': row['Company'],
                'article_title': row['Article'],
                'date': row['Date'],
                'original_use_case': row.get('AI Use Case', ''),
                'original_notes': row.get('Other Notes', ''),
                'standardized_use_case': analysis['standardized_use_case'],
                'confidence': analysis['confidence'],
                'sentiment': analysis['sentiment'],
                'strategic_importance': analysis['strategic_importance'],
                'maturity_stage': analysis['maturity_stage'],
                'key_technologies': ','.join(analysis['key_technologies']),
                'business_impact': analysis['business_impact'],
                'summary': analysis['summary']
            }

            results.append(result)

            # Save cache periodically
            if (idx + 1) % 5 == 0:
                self._save_cache()

        # Save final cache
        self._save_cache()

        # Create results DataFrame
        results_df = pd.DataFrame(results)

        # Save to CSV
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        results_df.to_csv(output_path, index=False, encoding='utf-8')

        # Also save to Excel with better formatting
        excel_output = output_file.replace('.csv', '.xlsx')
        excel_path = os.path.join(os.path.dirname(__file__), excel_output)
        results_df.to_excel(excel_path, index=False, sheet_name='Analysis Results')

        print(f"\n{'='*80}")
        print(f"✓ Analysis complete!")
        print(f"✓ CSV saved to: {output_path}")
        print(f"✓ Excel saved to: {excel_path}")
        print(f"✓ Total articles analyzed: {len(results_df)}")
        print(f"{'='*80}")

        # Print summary statistics
        print("\n📊 SUMMARY STATISTICS:")
        print("-"*50)
        print(f"\nBy Company:")
        print(results_df['company'].value_counts().to_string())
        print(f"\nBy Standardized Use Case:")
        print(results_df['standardized_use_case'].value_counts().to_string())
        print(f"\nBy Strategic Importance:")
        print(results_df['strategic_importance'].value_counts().to_string())
        print(f"\nBy Sentiment:")
        print(results_df['sentiment'].value_counts().to_string())

        return output_path


def main():
    """Main execution function."""
    analyzer = BigFirmAnalyzer(
        model_name="kimi-k2-thinking:cloud",
        fallback_model="qwen2.5:32b"
    )

    analyzer.analyze_all()


if __name__ == "__main__":
    main()
