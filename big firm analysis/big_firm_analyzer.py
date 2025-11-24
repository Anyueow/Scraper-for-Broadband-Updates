"""
LLM Analysis Pipeline for Big Firm AI Articles.
Analyzes company-specific AI use cases in UK telecom industry.
"""

import pandas as pd
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple
import ollama
from tqdm import tqdm
import time

class BigFirmAnalyzer:
    """
    LLM-based analysis for big firm AI articles.
    """

    # Use case categories
    USE_CASE_CATEGORIES = [
        "network_planning_deployment",
        "network_optimization_performance",
        "predictive_maintenance_analytics",
        "customer_support_experience",
        "security_fraud_threat",
        "internal_productivity_workforce",
        "other"
    ]

    def __init__(self,
                 model_name="gpt-oss:20b-cloud",
                 fallback_model="gpt-oss:20b",
                 cache_file="big_firm_scrape_cache.json",
                 batch_size=5):
        """Initialize the analyzer."""
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.cache_file = os.path.join(os.path.dirname(__file__), cache_file)
        self.cache = self._load_cache()
        self.active_model = None
        self.batch_size = batch_size
        self.rate_limited = False  # Track if we've hit rate limits

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
        prompt = f"""You are an expert analyst specializing in AI adoption by major UK telecommunications companies. Your task is to carefully analyze articles and accurately identify AI use cases.

Article Information:
- Company: {company}
- Article Title: {article_title}
- Date: {date}
- Manually Tagged Use Case: {existing_use_case if pd.notna(existing_use_case) else 'Not specified'}
- Additional Notes: {notes if pd.notna(notes) else 'None'}

CRITICAL INSTRUCTIONS:
- Read the article title, existing use case tag, and notes CAREFULLY
- Focus on ACTUAL AI applications being implemented or deployed
- Look for specific use cases, technologies, and implementations
- The manually tagged use case provides important context - use it to inform your analysis
- Pay attention to the CONTEXT of how AI is being used

Based on this information, provide a detailed JSON analysis with:

1. **standardized_use_case** (string): Map the use case to the MOST APPROPRIATE category. READ CAREFULLY and choose from:

   - "network_planning_deployment" - AI for infrastructure strategy and rollout
     SPECIFIC INDICATORS: "network design", "capacity planning", "site selection", "rollout", "deployment planning", "RF optimization", "coverage planning", "infrastructure planning", "capex", "network architecture"
     Examples: AI determining where to build towers, planning fiber rollout routes, optimizing coverage areas

   - "network_optimization_performance" - AI for real-time network efficiency and quality
     SPECIFIC INDICATORS: "network optimization", "performance management", "traffic management", "load balancing", "QoS", "SLA", "bandwidth allocation", "latency reduction", "self-optimizing", "SON"
     Examples: AI dynamically adjusting network traffic, optimizing bandwidth in real-time, improving connection quality

   - "predictive_maintenance_analytics" - AI anticipating failures and preventing downtime
     SPECIFIC INDICATORS: "predictive maintenance", "fault prediction", "anomaly detection", "preventive maintenance", "failure prediction", "equipment monitoring", "asset health", "root cause analysis", "network analytics", "diagnostics"
     Examples: AI predicting when equipment will fail, detecting network anomalies before they cause outages

   - "customer_support_experience" - AI improving customer service and interactions
     SPECIFIC INDICATORS: "customer support", "customer service", "chatbot", "virtual assistant", "customer experience", "CX", "support automation", "ticket resolution", "call center", "self-service", "troubleshooting assistant"
     Examples: AI chatbots handling customer queries, automated troubleshooting guides, virtual support agents

   - "security_fraud_threat" - AI protecting networks, data, and revenue
     SPECIFIC INDICATORS: "security", "cybersecurity", "fraud detection", "threat detection", "DDoS", "intrusion detection", "identity verification", "spam detection", "revenue assurance", "security monitoring"
     Examples: AI detecting fraud patterns, identifying cyber threats, preventing unauthorized access

   - "internal_productivity_workforce" - AI helping employees work more efficiently
     SPECIFIC INDICATORS: "employee productivity", "workforce tools", "internal tools", "knowledge management", "process automation", "workflow automation", "training tools", "coding assistant", "document automation", "operations efficiency"
     Examples: AI assistants for employees, automated internal processes, knowledge bases for staff

   - "other" - AI mentioned but no clear use case, or general AI strategy/partnership discussions

2. **confidence** (float 0.0-1.0): How confident are you in this categorization?
   - 0.9-1.0: Very clear, explicit use case with specific details
   - 0.7-0.9: Clear use case with good context
   - 0.5-0.7: Moderate confidence, some ambiguity
   - 0.0-0.5: Low confidence, vague or unclear

3. **sentiment** (string): Based on the article title and context, is the company's AI adoption portrayed as:
   - "positive" - Beneficial, innovative, successful, problem-solving
   - "neutral" - Factual reporting without clear positive/negative framing
   - "negative" - Concerns, problems, challenges, failures
   - "mixed" - Both positive and negative aspects discussed

4. **strategic_importance** (string): Rate the strategic importance of this AI initiative:
   - "high" - Core business transformation, significant competitive advantage
   - "medium" - Significant operational improvement, important but not transformative
   - "low" - Incremental optimization, tactical improvement
   - "unknown" - Cannot determine from available information

5. **maturity_stage** (string): What stage is this AI initiative at?
   - "pilot" - Testing/experimental/trial phase
   - "deployment" - Active rollout/implementation in progress
   - "scaled" - Fully operational at scale across the organization
   - "unknown" - Cannot determine from available information

6. **key_technologies** (array): List specific AI technologies mentioned or implied from the article title and tags:
   - Examples: "chatbot", "NLP", "natural language processing", "machine learning", "neural network", "automation", "predictive analytics", "computer vision", "generative AI", "LLM"

7. **business_impact** (string): One sentence describing the expected or actual business impact of this AI initiative.

8. **summary** (string): 2-3 sentence summary covering:
   - WHAT AI technology/solution is being discussed
   - HOW the company is using it (the specific use case)
   - WHY it matters or what impact it has

ANALYSIS APPROACH:
1. Read the article title, manually tagged use case, and notes carefully
2. Identify the SPECIFIC AI application from the available information
3. Match the application to the most appropriate use case based on INDICATORS above
4. Assess the maturity, importance, and sentiment based on the context
5. Be generous in identifying AI content - if there's any mention of AI/ML/automation, analyze it

IMPORTANT: Return ONLY valid JSON. No explanations, no markdown code blocks, just the raw JSON object.

Example:
{{
  "standardized_use_case": "customer_support_experience",
  "confidence": 0.9,
  "sentiment": "positive",
  "strategic_importance": "high",
  "maturity_stage": "deployment",
  "key_technologies": ["chatbot", "NLP", "automation"],
  "business_impact": "Improved customer service response times and satisfaction scores by 40%.",
  "summary": "BT is deploying AI-powered customer service chatbots to transform their support experience. The virtual assistants use natural language processing to handle common queries automatically. This represents a significant investment in customer-facing AI technology."
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
                error_msg = str(e).lower()

                # Check for rate limit errors
                if ('rate limit' in error_msg or 'too many requests' in error_msg or
                    '429' in error_msg or 'quota' in error_msg) and not self.rate_limited:
                    print(f"\n⚠️ RATE LIMIT DETECTED! Switching to local model: {self.fallback_model}")
                    self.active_model = self.fallback_model
                    self.rate_limited = True
                    # Retry immediately with fallback model
                    time.sleep(1)
                    continue

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

    def _extract_ai_keywords(self, text: str) -> Tuple[List[str], int]:
        """Extract AI-related keywords from text."""
        if pd.isna(text):
            return [], 0

        text_lower = str(text).lower()
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml',
            'deep learning', 'neural network', 'chatbot', 'automation',
            'predictive analytics', 'generative ai', 'llm', 'gpt',
            'natural language processing', 'nlp', 'computer vision'
        ]

        found_keywords = []
        for keyword in ai_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)

        return list(set(found_keywords)), len(found_keywords)

    def analyze_all(self, input_file="AI Articles By Company.xlsx",
                    output_file="big_firm_unified_analysis.csv"):
        """Run analysis on all articles and output in unified format."""

        print("="*80)
        print("BIG FIRM AI ANALYSIS PIPELINE")
        print("="*80)

        # Check model
        self.active_model = self._check_model_availability()

        # Load data from the correct sheet
        input_path = os.path.join(os.path.dirname(__file__), input_file)
        df = pd.read_excel(input_path, sheet_name='AI Use Case Data')

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

            # Extract AI keywords from title
            title_ai_keywords, title_ai_count = self._extract_ai_keywords(row['Article'])

            # Format result in unified CSV format
            result = {
                'source': 'big_firm_manual',
                'date': row['Date'],
                'title': row['Article'],
                'url': '',  # No URLs for manually curated articles
                'primary_use_case': analysis['standardized_use_case'],
                'primary_use_case_confidence': analysis['confidence'],
                'ai_use_cases': analysis['standardized_use_case'],  # Single use case as comma-separated
                'sentiment': analysis['sentiment'],
                'ai_mention_count': title_ai_count,
                'ai_mentions': ','.join(title_ai_keywords) if title_ai_keywords else '',
                'title_ai_mention_count': title_ai_count,
                'title_ai_mentions': ','.join(title_ai_keywords) if title_ai_keywords else '',
                'word_count': 0,  # No article content available, only titles
                'summary': analysis['summary'],
                # Additional big firm columns
                'company': row['Company'],
                'strategic_importance': analysis['strategic_importance'],
                'maturity_stage': analysis['maturity_stage'],
                'key_technologies': ','.join(analysis['key_technologies']),
                'business_impact': analysis['business_impact']
            }

            results.append(result)

            # Save cache periodically based on batch_size
            if (idx + 1) % self.batch_size == 0:
                self._save_cache()
                print(f"\n💾 Cache saved at {idx + 1} articles")

        # Save final cache
        self._save_cache()
        print(f"\n✓ Final cache saved")

        # Create results DataFrame
        results_df = pd.DataFrame(results)

        # Save to CSV
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        results_df.to_csv(output_path, index=False, encoding='utf-8')

        print(f"\n{'='*80}")
        print(f"✓ Analysis complete!")
        print(f"✓ CSV saved to: {output_path}")
        print(f"✓ Total articles analyzed: {len(results_df)}")
        print(f"{'='*80}")

        # Print summary statistics
        print("\n📊 SUMMARY STATISTICS:")
        print("-"*50)
        print(f"\nBy Company:")
        print(results_df['company'].value_counts().to_string())
        print(f"\nBy Primary Use Case:")
        print(results_df['primary_use_case'].value_counts().to_string())
        print(f"\nBy Strategic Importance:")
        print(results_df['strategic_importance'].value_counts().to_string())
        print(f"\nBy Sentiment:")
        print(results_df['sentiment'].value_counts().to_string())

        if self.rate_limited:
            print(f"\n⚠️ Note: Rate limit was hit. Switched to local model: {self.fallback_model}")

        return output_path


def main():
    """Main execution function."""
    analyzer = BigFirmAnalyzer(
        model_name="gpt-oss:20b-cloud",
        fallback_model="gpt-oss:20b",
        batch_size=5
    )

    analyzer.analyze_all()


if __name__ == "__main__":
    main()
