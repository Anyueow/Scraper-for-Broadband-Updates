"""
AI content analyzer - detects and categorizes AI mentions
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyze articles for AI-related content"""

    def __init__(self, ai_keywords: List[str], use_case_categories: Dict[str, List[str]],
                 min_confidence: float = 0.3):
        self.ai_keywords = [k.lower() for k in ai_keywords]
        self.use_case_categories = {
            category: [kw.lower() for kw in keywords]
            for category, keywords in use_case_categories.items()
        }
        self.min_confidence = min_confidence

    def filter_ai_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles that contain AI-related keywords"""
        ai_articles = []

        for article in articles:
            if self.contains_ai_content(article):
                ai_articles.append(article)

        logger.info(f"AI filtering: {len(articles)} -> {len(ai_articles)} articles with AI content")
        return ai_articles

    def contains_ai_content(self, article: Dict) -> bool:
        """Check if article contains AI-related content"""
        # Combine searchable text
        searchable_text = ' '.join([
            article.get('title', ''),
            article.get('summary', ''),
            article.get('content', '')
        ]).lower()

        # Check for any AI keyword
        for keyword in self.ai_keywords:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, searchable_text, re.IGNORECASE):
                return True

        return False

    def analyze(self, article: Dict) -> Dict:
        """Analyze article for AI content and categorize"""
        result = article.copy()

        # Combine text for analysis
        full_text = ' '.join([
            article.get('title', ''),
            article.get('summary', ''),
            article.get('content', '')
        ])

        # Detect AI mentions
        ai_mentions = self._detect_ai_mentions(full_text)
        result['ai_mentions'] = ai_mentions
        result['ai_mention_count'] = len(ai_mentions)

        # Categorize use cases
        use_cases, confidence_scores = self._categorize_use_cases(full_text)
        result['ai_use_cases'] = use_cases
        result['use_case_confidence'] = confidence_scores

        # Extract AI context snippets
        snippets = self._extract_context_snippets(full_text, ai_mentions[:3])  # Top 3 mentions
        result['ai_snippets'] = snippets

        # Determine primary use case
        if use_cases:
            primary_use_case = max(confidence_scores.items(), key=lambda x: x[1])
            result['primary_use_case'] = primary_use_case[0]
            result['primary_use_case_confidence'] = primary_use_case[1]
        else:
            result['primary_use_case'] = 'general'
            result['primary_use_case_confidence'] = 0.0

        # Simple sentiment (positive/neutral/negative based on context)
        sentiment = self._analyze_sentiment(full_text)
        result['sentiment'] = sentiment

        return result

    def _detect_ai_mentions(self, text: str) -> List[str]:
        """Detect all AI keyword mentions in text"""
        mentions = []
        text_lower = text.lower()

        for keyword in self.ai_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            mentions.extend(matches)

        return list(set(mentions))  # Remove duplicates

    def _categorize_use_cases(self, text: str) -> Tuple[List[str], Dict[str, float]]:
        """Categorize AI use cases mentioned in text"""
        text_lower = text.lower()
        confidence_scores = {}

        for category, keywords in self.use_case_categories.items():
            score = 0
            matches = 0

            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                count = len(re.findall(pattern, text_lower))
                if count > 0:
                    matches += 1
                    score += count

            # Normalize score
            if matches > 0:
                confidence = min(1.0, (score / 10.0) * (matches / len(keywords)))
                confidence_scores[category] = round(confidence, 3)

        # Filter by minimum confidence
        use_cases = [
            category for category, score in confidence_scores.items()
            if score >= self.min_confidence
        ]

        return use_cases, confidence_scores

    def _extract_context_snippets(self, text: str, keywords: List[str],
                                   window: int = 100) -> List[str]:
        """Extract text snippets around AI keywords for context"""
        snippets = []

        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                start = max(0, match.start() - window)
                end = min(len(text), match.end() + window)
                snippet = text[start:end].strip()

                # Clean up snippet
                snippet = re.sub(r'\s+', ' ', snippet)
                snippets.append(f"...{snippet}...")

                if len(snippets) >= 3:  # Limit to 3 snippets
                    break

            if len(snippets) >= 3:
                break

        return snippets

    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis based on positive/negative keywords"""
        text_lower = text.lower()

        positive_words = [
            'innovative', 'improve', 'enhance', 'better', 'efficient', 'advanced',
            'breakthrough', 'success', 'benefit', 'advantage', 'optimized', 'growth',
            'revolutionary', 'cutting-edge', 'state-of-the-art', 'promising'
        ]

        negative_words = [
            'concern', 'risk', 'challenge', 'problem', 'issue', 'threat', 'worry',
            'fear', 'danger', 'difficult', 'failure', 'loss', 'decline', 'worse',
            'complicated', 'expensive', 'costly'
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count * 1.5:
            return 'positive'
        elif negative_count > positive_count * 1.5:
            return 'negative'
        else:
            return 'neutral'

    def generate_summary(self, analyzed_articles: List[Dict], source: Optional[str] = None) -> Dict:
        """Generate summary of AI trends for a source"""
        if source:
            articles = [a for a in analyzed_articles if a.get('source') == source]
        else:
            articles = analyzed_articles

        if not articles:
            return {
                'source': source or 'all',
                'total_articles': 0,
                'summary': 'No AI-related articles found.'
            }

        # Aggregate statistics
        total_articles = len(articles)
        use_case_counter = Counter()
        sentiment_counter = Counter()

        for article in articles:
            for use_case in article.get('ai_use_cases', []):
                use_case_counter[use_case] += 1
            sentiment = article.get('sentiment', 'neutral')
            sentiment_counter[sentiment] += 1

        # Top use cases
        top_use_cases = use_case_counter.most_common(3)

        # Generate natural language summary
        summary_parts = []
        summary_parts.append(f"Found {total_articles} AI-related articles.")

        if top_use_cases:
            use_case_text = ", ".join([f"{uc} ({count})" for uc, count in top_use_cases])
            summary_parts.append(f"Primary applications: {use_case_text}.")

        sentiment_text = ", ".join([f"{sent}: {count}" for sent, count in sentiment_counter.most_common()])
        summary_parts.append(f"Sentiment distribution: {sentiment_text}.")

        return {
            'source': source or 'all',
            'total_articles': total_articles,
            'top_use_cases': dict(top_use_cases),
            'sentiment_distribution': dict(sentiment_counter),
            'summary': ' '.join(summary_parts)
        }
