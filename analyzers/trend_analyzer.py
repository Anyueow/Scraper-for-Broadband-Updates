"""
Trend analyzer for temporal analysis of AI mentions
"""
import logging
from typing import Dict, List
from collections import defaultdict, Counter
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyze trends in AI mentions over time"""

    def __init__(self):
        pass

    def analyze_trends(self, articles: List[Dict], grouping: str = 'monthly') -> Dict:
        """
        Analyze trends over time

        Args:
            articles: List of analyzed articles with AI content
            grouping: 'monthly' or 'quarterly'

        Returns:
            Dictionary with trend analysis
        """
        # Group articles by time period
        time_groups = self._group_by_time(articles, grouping)

        # Analyze each time period
        trend_data = {}
        for period, period_articles in time_groups.items():
            trend_data[period] = self._analyze_period(period_articles)

        # Calculate overall trends
        overall_stats = self._calculate_overall_stats(trend_data)

        return {
            'grouping': grouping,
            'periods': trend_data,
            'overall_statistics': overall_stats,
            'total_periods': len(trend_data),
            'total_articles': len(articles)
        }

    def _group_by_time(self, articles: List[Dict], grouping: str) -> Dict[str, List[Dict]]:
        """Group articles by time period"""
        time_groups = defaultdict(list)

        for article in articles:
            period = self._extract_period(article.get('date', ''), grouping)
            time_groups[period].append(article)

        return dict(sorted(time_groups.items()))

    def _extract_period(self, date_str: str, grouping: str) -> str:
        """Extract time period from date string"""
        if not date_str:
            return 'unknown'

        try:
            # Try to parse various date formats
            date_obj = self._parse_date(date_str)

            if not date_obj:
                return 'unknown'

            if grouping == 'monthly':
                return date_obj.strftime('%Y-%m')
            elif grouping == 'quarterly':
                quarter = (date_obj.month - 1) // 3 + 1
                return f"{date_obj.year}-Q{quarter}"
            else:
                return date_obj.strftime('%Y')

        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return 'unknown'

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None

        # Common date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%d %B %Y',
            '%d %b %Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d/%m/%Y',
            '%m/%d/%Y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        # Try to extract year-month-day with regex
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if match:
            try:
                return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            except ValueError:
                pass

        return None

    def _analyze_period(self, articles: List[Dict]) -> Dict:
        """Analyze a single time period"""
        article_count = len(articles)

        # Count use cases
        use_case_counter = Counter()
        for article in articles:
            for use_case in article.get('ai_use_cases', []):
                use_case_counter[use_case] += 1

        # Count sources
        source_counter = Counter()
        for article in articles:
            source = article.get('source', 'unknown')
            source_counter[source] += 1

        # Sentiment distribution
        sentiment_counter = Counter()
        for article in articles:
            sentiment = article.get('sentiment', 'neutral')
            sentiment_counter[sentiment] += 1

        # Top keywords
        all_mentions = []
        for article in articles:
            all_mentions.extend(article.get('ai_mentions', []))
        mention_counter = Counter(all_mentions)

        return {
            'article_count': article_count,
            'use_cases': dict(use_case_counter.most_common()),
            'sources': dict(source_counter),
            'sentiments': dict(sentiment_counter),
            'top_ai_keywords': dict(mention_counter.most_common(5))
        }

    def _calculate_overall_stats(self, trend_data: Dict) -> Dict:
        """Calculate overall statistics across all periods"""
        total_articles = sum(period['article_count'] for period in trend_data.values())

        # Aggregate use cases
        overall_use_cases = Counter()
        for period_data in trend_data.values():
            for use_case, count in period_data.get('use_cases', {}).items():
                overall_use_cases[use_case] += count

        # Aggregate sentiments
        overall_sentiments = Counter()
        for period_data in trend_data.values():
            for sentiment, count in period_data.get('sentiments', {}).items():
                overall_sentiments[sentiment] += count

        # Find trending use cases (appearing in recent periods)
        if len(trend_data) >= 2:
            periods = list(trend_data.keys())
            recent_period = trend_data[periods[-1]]
            trending = [
                uc for uc in recent_period.get('use_cases', {}).keys()
            ]
        else:
            trending = []

        return {
            'total_articles': total_articles,
            'top_use_cases': dict(overall_use_cases.most_common(5)),
            'sentiment_distribution': dict(overall_sentiments),
            'trending_use_cases': trending[:3]
        }

    def generate_trend_summary(self, trend_analysis: Dict) -> str:
        """Generate natural language summary of trends"""
        summary_parts = []

        total_articles = trend_analysis['total_articles']
        total_periods = trend_analysis['total_periods']
        grouping = trend_analysis['grouping']

        summary_parts.append(
            f"Analyzed {total_articles} AI-related articles across {total_periods} {grouping} periods."
        )

        # Top use cases
        overall_stats = trend_analysis['overall_statistics']
        top_use_cases = overall_stats.get('top_use_cases', {})
        if top_use_cases:
            top_3 = list(top_use_cases.items())[:3]
            use_case_text = ", ".join([f"{uc} ({count})" for uc, count in top_3])
            summary_parts.append(f"Most common use cases: {use_case_text}.")

        # Trending
        trending = overall_stats.get('trending_use_cases', [])
        if trending:
            summary_parts.append(f"Recent trending topics: {', '.join(trending)}.")

        # Sentiment
        sentiments = overall_stats.get('sentiment_distribution', {})
        if sentiments:
            total_sent = sum(sentiments.values())
            positive_pct = round((sentiments.get('positive', 0) / total_sent) * 100, 1)
            summary_parts.append(f"Overall sentiment: {positive_pct}% positive coverage.")

        return ' '.join(summary_parts)


# Make Optional available
from typing import Optional
