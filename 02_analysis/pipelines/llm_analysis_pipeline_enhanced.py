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
    ENHANCED LLM-based analysis pipeline for UK broadband industry articles.
    Analyzes articles using Ollama to identify AI trends, use cases, sentiment,
    companies mentioned, and technologies deployed.

    New features in enhanced version:
    - Extracts telecommunications companies mentioned in articles
    - Extracts AI technologies categorized by type (models, platforms, infrastructure, techniques)
    - Uses company and technology taxonomies for standardization
    """

    # Use case categories as defined in project requirements
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
                 scraped_output_dir="../../Scraped Output",
                 model_name="gpt-oss:20b-cloud",
                 fallback_model="gpt-oss:20b",
                 cache_file="analysis_cache_enhanced.json",
                 batch_size=5):
        """
        Initialize the analyzer.

        Args:
            scraped_output_dir: Directory containing scraped CSV files
            model_name: Primary Ollama model to use
            fallback_model: Fallback model if primary is unavailable
            cache_file: JSON file to cache analysis results
            batch_size: Number of articles to process before saving cache
        """
        self.scraped_output_dir = scraped_output_dir
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.cache_file = os.path.join(os.path.dirname(__file__), cache_file)
        self.cache = self._load_cache()
        self.active_model = None
        self.batch_size = batch_size
        self.rate_limited = False  # Track if we've hit rate limits

        # Load company and technology taxonomies
        self.company_taxonomy = self._load_company_taxonomy()
        self.tech_taxonomy = self._load_technology_taxonomy()

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

    def _load_company_taxonomy(self) -> Dict:
        """Load company taxonomy configuration."""
        config_path = os.path.join(os.path.dirname(__file__), '../configs/company_taxonomy.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load company taxonomy: {e}")
            return {}

    def _load_technology_taxonomy(self) -> Dict:
        """Load technology taxonomy configuration."""
        config_path = os.path.join(os.path.dirname(__file__), '../configs/technology_taxonomy.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load technology taxonomy: {e}")
            return {}

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
        prompt = f"""You are an expert analyst specializing in AI adoption in the UK broadband and telecommunications industry. Your task is to carefully analyze articles and accurately identify AI use cases.

Article Details:
- Title: {title}
- Source: {source}
- Date: {date}
- Content: {content[:4000]}{'...' if len(content) > 4000 else ''}

CRITICAL INSTRUCTIONS:
- Read the ENTIRE article carefully, not just the title
- Focus on ACTUAL AI applications being implemented or deployed, not just general mentions
- Look for specific use cases, technologies, and implementations
- If AI is mentioned but no specific use case is clear, use "other"
- Pay attention to the CONTEXT of how AI is being used

Provide a JSON response with the following information:

1. **has_ai_content** (boolean): Does this article discuss actual AI/ML implementation, deployment, or specific use cases? (Not just generic mentions)

2. **ai_mentions** (array of strings): List ALL AI-related terms found in the article:
   - Keywords: "AI", "artificial intelligence", "machine learning", "ML", "deep learning", "neural network"
   - Technologies: "LLM", "large language model", "GPT", "ChatGPT", "Claude", "generative AI"
   - Applications: "chatbot", "virtual assistant", "automation", "predictive analytics", "computer vision"
   - Techniques: "natural language processing", "NLP", "sentiment analysis", "anomaly detection"

3. **ai_mention_count** (integer): Total number of times AI-related concepts are mentioned (count each occurrence).

4. **primary_use_case** (string): The PRIMARY AI use case this article discusses. READ CAREFULLY and choose the MOST APPROPRIATE category:

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
   - null - Article doesn't discuss AI at all

5. **primary_use_case_confidence** (float 0.0-1.0): How confident are you in the primary use case classification?
   - 0.9-1.0: Very clear, explicit use case described with specific details
   - 0.7-0.9: Clear use case with good context
   - 0.5-0.7: Moderate confidence, some ambiguity
   - 0.0-0.5: Low confidence, vague or unclear

6. **ai_use_cases** (array of strings): ALL AI use case categories mentioned in the article (can include multiple from the list above). Look for secondary use cases beyond the primary one.

7. **sentiment** (string): Overall sentiment toward AI in this article:
   - "positive" - AI presented as beneficial, innovative, successful, solving problems
   - "neutral" - Factual reporting without clear positive/negative framing
   - "negative" - Concerns, criticism, failures, problems with AI
   - "mixed" - Both positive and negative aspects discussed equally
   - "not_applicable" - Article doesn't discuss AI meaningfully

8. **summary** (string): A concise 2-3 sentence summary focusing on:
   - WHAT AI technology/solution is being discussed
   - HOW it's being used (the specific use case)
   - WHY it matters or what impact it has
   If no AI content, return "N/A".

9. **companies_mentioned** (array of strings): Extract ALL telecommunications company names mentioned in the article:
   - Look for UK telcos: BT, Virgin Media O2 (VMO2), Vodafone, Sky, TalkTalk, EE, Three, Plusnet, Openreach
   - Look for UK altnets/wholesale: CityFibre, Neos Networks, Netomnia, Community Fibre, Gigaclear, Hyperoptic, YouFibre, Brsk, nexfibre, County Broadband, G.Network
   - Look for infrastructure: Colt, Cornerstone, Wireless Infrastructure Group, Boldyn Networks, Freshwave
   - Look for European/Global: euNetworks, TelCables Europe, Zayo
   - Exclude: Generic references like "UK telcos", "operators", "ISPs" (don't include these)
   - Include: Specific company names only, even if not UK-based
   - Format: Use canonical names (e.g., "BT" not "British Telecom", "Virgin Media O2" not "VMO2")
   - If article mentions vendor partnerships, extract the TELCO company, not the vendor (e.g., if "BT partners with Microsoft", extract "BT")

10. **technologies** (object): Extract ALL AI technologies mentioned, categorized by type:
    {{
      "foundation_models": [...],     // LLMs: GPT-3/4, Claude, Gemini, PaLM, LLaMA, Mistral, Azure OpenAI, Bedrock, Ollama, Qwen, etc.
      "platforms": [...],              // AI Platforms: ServiceNow, NICE CXone, Nokia AVA, Lenses.io, IQGeo, Vyntelligence, Domo, LangChain, etc.
      "infrastructure": [...],         // Cloud/Infrastructure: AWS, Azure, GCP, edge compute, on-premise
      "techniques": [...]              // AI Techniques: NLP, computer vision, anomaly detection, predictive analytics, RAG, neural networks, etc.
    }}
    - Look for explicit technology names, not generic terms
    - Include version numbers if mentioned (e.g., "GPT-4", "Claude 3")
    - If article says "using AI" without specifying technology, leave that category empty
    - Focus on technologies actively used/deployed, not just mentioned in passing

ANALYSIS APPROACH:
1. First, scan for AI-related keywords and determine if there's meaningful AI content
2. Read the full article to understand the CONTEXT and specific application
3. Match the application to the most appropriate use case based on INDICATORS above
4. Look for multiple use cases if the article discusses various applications
5. Assess sentiment based on how AI is framed in the article

IMPORTANT: Return ONLY valid JSON. No explanations, no markdown code blocks, just the raw JSON object.

Example response format:
{{
  "has_ai_content": true,
  "ai_mentions": ["AI", "machine learning", "chatbot", "virtual assistant", "automation"],
  "ai_mention_count": 12,
  "primary_use_case": "customer_support_experience",
  "primary_use_case_confidence": 0.95,
  "ai_use_cases": ["customer_support_experience"],
  "sentiment": "positive",
  "summary": "BT is deploying AI-powered chatbots to handle customer support queries, aiming to reduce wait times by 40% and improve customer satisfaction. The virtual assistants use natural language processing to understand and resolve common technical issues automatically.",
  "companies_mentioned": ["BT"],
  "technologies": {{
    "foundation_models": ["Azure OpenAI"],
    "platforms": ["ServiceNow AI Platform"],
    "infrastructure": ["Azure"],
    "techniques": ["NLP", "natural language processing"]
  }}
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
                'summary': 'N/A',
                'companies_mentioned': [],
                'technologies': {
                    'foundation_models': [],
                    'platforms': [],
                    'infrastructure': [],
                    'techniques': []
                }
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
                'summary': 'N/A',
                'companies_mentioned': [],
                'technologies': {
                    'foundation_models': [],
                    'platforms': [],
                    'infrastructure': [],
                    'techniques': []
                }
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
            'summary': 'N/A',
            'companies_mentioned': [],
            'technologies': {
                'foundation_models': [],
                'platforms': [],
                'infrastructure': [],
                'techniques': []
            }
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
            'summary': result.get('summary', ''),
            'companies_mentioned': result.get('companies_mentioned', []),
            'technologies': result.get('technologies', {
                'foundation_models': [],
                'platforms': [],
                'infrastructure': [],
                'techniques': []
            })
        }

        # Ensure lists are actually lists
        if not isinstance(validated['ai_mentions'], list):
            validated['ai_mentions'] = []
        if not isinstance(validated['ai_use_cases'], list):
            validated['ai_use_cases'] = []
        if not isinstance(validated['companies_mentioned'], list):
            validated['companies_mentioned'] = []

        # Validate technologies structure
        if not isinstance(validated['technologies'], dict):
            validated['technologies'] = {
                'foundation_models': [],
                'platforms': [],
                'infrastructure': [],
                'techniques': []
            }
        else:
            # Ensure each technology category is a list
            for category in ['foundation_models', 'platforms', 'infrastructure', 'techniques']:
                if category not in validated['technologies'] or not isinstance(validated['technologies'][category], list):
                    validated['technologies'][category] = []

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

    def load_pre_analyzed_articles(self) -> pd.DataFrame:
        """
        Load pre-analyzed articles from increased_scope.csv and big_firm_unified_analysis.csv.
        These articles already have LLM analysis completed, so we just need to normalize their format.

        Returns:
            DataFrame with pre-analyzed articles in normalized format
        """
        all_pre_analyzed = []

        # 1. Load increased_scope.csv (manually curated AI articles)
        increased_scope_path = os.path.join(os.path.dirname(__file__), "../../increased_scope.csv")
        if os.path.exists(increased_scope_path):
            try:
                df = pd.read_csv(increased_scope_path)
                print(f"  ✓ Loaded increased_scope.csv: {len(df)} articles")

                # Convert text confidence to numeric
                confidence_map = {
                    'High': 0.9,
                    'Medium': 0.7,
                    'Low': 0.5
                }

                # These articles are already analyzed, so add them with 'already_analyzed' flag
                for _, row in df.iterrows():
                    # Convert confidence
                    conf_raw = row.get('primary_use_case_confidence', 0.0)
                    if isinstance(conf_raw, str):
                        confidence = confidence_map.get(conf_raw, 0.7)
                    else:
                        confidence = float(conf_raw) if pd.notna(conf_raw) else 0.7

                    # Parse word_count robustly (handle extra quotes/spaces)
                    wc_raw = str(row.get('word_count', '0')).strip().replace('"', '').replace("'", '')
                    try:
                        word_count = int(wc_raw) if wc_raw.isdigit() else 0
                    except:
                        word_count = 0

                    # Note: increased_scope.csv has descriptive use cases, not standardized codes
                    # We'll keep them as-is since they're manually curated
                    normalized = {
                        'source': str(row.get('source', 'Manual')),
                        'date': self.normalize_date(row.get('date', '')),
                        'title': str(row.get('title', '')).strip(),
                        'url': str(row.get('url', '')).strip(),
                        'content': str(row.get('summary', '')),  # Use summary as content
                        'word_count': word_count,
                        'already_analyzed': True,
                        'primary_use_case': 'other',  # Default to 'other' for non-standard use cases
                        'primary_use_case_confidence': confidence,
                        'ai_use_cases': str(row.get('ai_use_cases', '')),
                        'sentiment': str(row.get('sentiment', 'not_applicable')).lower(),
                        'ai_mention_count': int(row.get('ai_mention_count', 0)) if pd.notna(row.get('ai_mention_count')) else 0,
                        'ai_mentions': str(row.get('ai_mentions', '')),
                        'title_ai_mention_count': int(row.get('title_ai_mention_count', 0)) if pd.notna(row.get('title_ai_mention_count')) else 0,
                        'title_ai_mentions': str(row.get('title_ai_mentions', '')),
                        'summary': str(row.get('summary', '')),
                        'companies_mentioned': '',  # Will extract from existing data if available
                        'technologies_foundation_models': '',
                        'technologies_platforms': '',
                        'technologies_infrastructure': '',
                        'technologies_techniques': ''
                    }

                    if normalized['title'] and normalized['title'] != 'nan':
                        all_pre_analyzed.append(normalized)

            except Exception as e:
                print(f"  ✗ Error loading increased_scope.csv: {e}")
                import traceback
                traceback.print_exc()

        # 2. Load big_firm_unified_analysis.csv (company-specific AI articles)
        big_firm_path = os.path.join(os.path.dirname(__file__), "../../big firm analysis/big_firm_unified_analysis.csv")
        if os.path.exists(big_firm_path):
            try:
                df = pd.read_csv(big_firm_path)
                print(f"  ✓ Loaded big_firm_unified_analysis.csv: {len(df)} articles")

                for _, row in df.iterrows():
                    # Extract technologies from key_technologies field
                    key_techs = str(row.get('key_technologies', ''))

                    normalized = {
                        'source': str(row.get('source', 'BigFirm')),
                        'date': self.normalize_date(row.get('date', '')),
                        'title': str(row.get('title', '')).strip(),
                        'url': str(row.get('url', '')).strip(),
                        'content': str(row.get('summary', '')),
                        'word_count': int(row.get('word_count', 0)) if pd.notna(row.get('word_count')) else 0,
                        'already_analyzed': True,
                        'primary_use_case': str(row.get('primary_use_case', '')),
                        'primary_use_case_confidence': float(row.get('primary_use_case_confidence', 0.0)) if pd.notna(row.get('primary_use_case_confidence')) else 0.0,
                        'ai_use_cases': str(row.get('ai_use_cases', '')),
                        'sentiment': str(row.get('sentiment', 'not_applicable')),
                        'ai_mention_count': int(row.get('ai_mention_count', 0)) if pd.notna(row.get('ai_mention_count')) else 0,
                        'ai_mentions': str(row.get('ai_mentions', '')),
                        'title_ai_mention_count': int(row.get('title_ai_mention_count', 0)) if pd.notna(row.get('title_ai_mention_count')) else 0,
                        'title_ai_mentions': str(row.get('title_ai_mentions', '')),
                        'summary': str(row.get('summary', '')),
                        'companies_mentioned': str(row.get('company', '')),  # Use company field
                        'technologies_foundation_models': '',
                        'technologies_platforms': key_techs,  # Put all tech in platforms for now
                        'technologies_infrastructure': '',
                        'technologies_techniques': ''
                    }

                    if normalized['title'] and normalized['title'] != 'nan':
                        all_pre_analyzed.append(normalized)

            except Exception as e:
                print(f"  ✗ Error loading big_firm_unified_analysis.csv: {e}")

        if all_pre_analyzed:
            return pd.DataFrame(all_pre_analyzed)
        else:
            return pd.DataFrame()

    def load_and_normalize_csvs(self) -> pd.DataFrame:
        """
        Load all CSV files (scraped + pre-analyzed) and normalize them into a unified format.

        Returns:
            DataFrame with normalized data from all sources
        """
        print("Loading data from all sources...")

        # 1. Load scraped articles (require LLM analysis)
        csv_files = list(Path(self.scraped_output_dir).glob("*.csv"))

        if not csv_files:
            print(f"⚠ No CSV files found in {self.scraped_output_dir}")
            scraped_data = []
        else:
            print(f"\n📂 Loading {len(csv_files)} scraped CSV file(s)...")
            scraped_data = []

            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)

                    # Check for required columns
                    if 'Article Title' not in df.columns:
                        print(f"  Warning: Skipping {csv_file.name} - no 'Article Title' column")
                        continue

                    # Normalize each row
                    for _, row in df.iterrows():
                        normalized = {
                            'source': self.normalize_source(row.get('Website', '')),
                            'date': self.normalize_date(row.get('Date', '')),
                            'title': str(row.get('Article Title', '')).strip(),
                            'url': str(row.get('Article Link', '')).strip(),
                            'content': self.clean_content(row.get('Article content', '')),
                            'word_count': len(str(row.get('Article content', '')).split()),
                            'already_analyzed': False
                        }

                        # Skip empty titles
                        if not normalized['title'] or normalized['title'] == 'nan':
                            continue

                        scraped_data.append(normalized)

                    print(f"  ✓ Loaded {csv_file.name}: {len(df)} articles")

                except Exception as e:
                    print(f"  ✗ Error loading {csv_file.name}: {e}")

        # 2. Load pre-analyzed articles
        print(f"\n📂 Loading pre-analyzed articles...")
        pre_analyzed_df = self.load_pre_analyzed_articles()

        # 3. Combine all sources
        if scraped_data:
            scraped_df = pd.DataFrame(scraped_data)
        else:
            scraped_df = pd.DataFrame()

        # Merge both dataframes
        if not scraped_df.empty and not pre_analyzed_df.empty:
            df = pd.concat([scraped_df, pre_analyzed_df], ignore_index=True)
        elif not scraped_df.empty:
            df = scraped_df
        elif not pre_analyzed_df.empty:
            df = pre_analyzed_df
        else:
            raise Exception("No valid articles found from any source")

        # Remove duplicates based on URL or title
        original_count = len(df)
        df = df.drop_duplicates(subset=['url'], keep='first')
        duplicates_removed = original_count - len(df)

        print(f"\n📊 Summary:")
        print(f"  - Scraped articles: {len(scraped_df) if not scraped_df.empty else 0}")
        print(f"  - Pre-analyzed articles: {len(pre_analyzed_df) if not pre_analyzed_df.empty else 0}")
        print(f"  - Duplicates removed: {duplicates_removed}")
        print(f"  - Total unique articles: {len(df)}")
        print(f"  - Pre-analyzed (skip LLM): {len(df[df.get('already_analyzed', False) == True]) if 'already_analyzed' in df.columns else 0}")
        print(f"  - Require LLM analysis: {len(df[df.get('already_analyzed', False) == False]) if 'already_analyzed' in df.columns else len(df)}")

        return df

    def process_articles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process articles through LLM analysis.
        Pre-analyzed articles (from increased_scope.csv and big_firm_unified_analysis.csv)
        are skipped and their existing analysis is preserved.

        Args:
            df: DataFrame with normalized article data

        Returns:
            DataFrame with LLM analysis results added
        """
        # Count pre-analyzed vs. requiring analysis
        pre_analyzed_count = len(df[df.get('already_analyzed', False) == True]) if 'already_analyzed' in df.columns else 0
        needs_analysis_count = len(df) - pre_analyzed_count

        print(f"\nProcessing {len(df)} total articles:")
        print(f"  - Pre-analyzed (skip LLM): {pre_analyzed_count}")
        print(f"  - Require LLM analysis: {needs_analysis_count}")
        print(f"Using model: {self.active_model}")

        results = []

        # Process with progress bar
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing articles"):
            try:
                # Check if article is already analyzed
                if row.get('already_analyzed', False):
                    # Use existing analysis data, just ensure all fields are present
                    result = {
                        'source': row.get('source', ''),
                        'date': row.get('date', ''),
                        'title': row.get('title', ''),
                        'url': row.get('url', ''),
                        'content': row.get('content', ''),
                        'word_count': row.get('word_count', 0),
                        'primary_use_case': row.get('primary_use_case', ''),
                        'primary_use_case_confidence': row.get('primary_use_case_confidence', 0.0),
                        'ai_use_cases': row.get('ai_use_cases', ''),
                        'sentiment': row.get('sentiment', 'not_applicable'),
                        'ai_mention_count': row.get('ai_mention_count', 0),
                        'ai_mentions': row.get('ai_mentions', ''),
                        'title_ai_mentions': row.get('title_ai_mentions', ''),
                        'title_ai_mention_count': row.get('title_ai_mention_count', 0),
                        'summary': row.get('summary', ''),
                        'companies_mentioned': row.get('companies_mentioned', ''),
                        'technologies_foundation_models': row.get('technologies_foundation_models', ''),
                        'technologies_platforms': row.get('technologies_platforms', ''),
                        'technologies_infrastructure': row.get('technologies_infrastructure', ''),
                        'technologies_techniques': row.get('technologies_techniques', '')
                    }
                    results.append(result)
                    continue

                # Article needs LLM analysis
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
                    'source': row['source'],
                    'date': row['date'],
                    'title': row['title'],
                    'url': row['url'],
                    'content': row['content'],
                    'word_count': row['word_count'],
                    'primary_use_case': analysis['primary_use_case'],
                    'primary_use_case_confidence': analysis['primary_use_case_confidence'],
                    'ai_use_cases': ','.join(analysis['ai_use_cases']),
                    'sentiment': analysis['sentiment'],
                    'ai_mention_count': analysis['ai_mention_count'],
                    'ai_mentions': ','.join(analysis['ai_mentions']),
                    'title_ai_mentions': ','.join(title_ai_keywords),
                    'title_ai_mention_count': title_ai_count,
                    'summary': analysis['summary'],
                    'companies_mentioned': ','.join(analysis['companies_mentioned']),
                    'technologies_foundation_models': ','.join(analysis['technologies']['foundation_models']),
                    'technologies_platforms': ','.join(analysis['technologies']['platforms']),
                    'technologies_infrastructure': ','.join(analysis['technologies']['infrastructure']),
                    'technologies_techniques': ','.join(analysis['technologies']['techniques'])
                }

                results.append(result)

                # Save cache periodically based on batch_size
                if (idx + 1) % self.batch_size == 0:
                    self._save_cache()
                    print(f"\n💾 Cache saved at {idx + 1} articles")

            except Exception as e:
                print(f"\nError processing article {idx}: {e}")
                # Add row with empty analysis on error
                results.append({
                    'source': row.get('source', ''),
                    'date': row.get('date', ''),
                    'title': row.get('title', ''),
                    'url': row.get('url', ''),
                    'content': row.get('content', ''),
                    'word_count': row.get('word_count', 0),
                    'primary_use_case': None,
                    'primary_use_case_confidence': 0.0,
                    'ai_use_cases': '',
                    'sentiment': 'not_applicable',
                    'ai_mention_count': 0,
                    'ai_mentions': '',
                    'title_ai_mentions': '',
                    'title_ai_mention_count': 0,
                    'summary': 'N/A',
                    'companies_mentioned': '',
                    'technologies_foundation_models': '',
                    'technologies_platforms': '',
                    'technologies_infrastructure': '',
                    'technologies_techniques': ''
                })

        # Save final cache
        self._save_cache()
        print(f"\n✓ Final cache saved")

        return pd.DataFrame(results)

    def generate_unified_csv(self, output_file="unified_ai_analysis_enhanced.csv") -> str:
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

        # Reorder columns to match target schema (with new company and technology fields)
        column_order = [
            'source', 'date', 'title', 'url',
            'primary_use_case', 'primary_use_case_confidence',
            'ai_use_cases', 'sentiment',
            'ai_mention_count', 'ai_mentions',
            'title_ai_mention_count', 'title_ai_mentions',
            'word_count', 'summary',
            'companies_mentioned',
            'technologies_foundation_models',
            'technologies_platforms',
            'technologies_infrastructure',
            'technologies_techniques'
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
    # Using gpt-oss:20b-cloud (Cloud model) with automatic fallback to gpt-oss:20b (Local) on rate limits
    analyzer = BroadbandAIAnalyzer(
        model_name="gpt-oss:20b-cloud",
        fallback_model="gpt-oss:20b",
        batch_size=5  # Save cache every 5 articles
    )

    # Run the pipeline
    output_path = analyzer.generate_unified_csv()

    print(f"\nOutput file ready: {output_path}")
    print("\nNext steps:")
    print("1. Review the unified CSV for accuracy")
    print("2. Use the data for trend analysis, visualization, or reporting")

    if analyzer.rate_limited:
        print(f"\n⚠️ Note: Rate limit was hit. Switched to local model: {analyzer.fallback_model}")


if __name__ == "__main__":
    main()
