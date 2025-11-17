"""
Main pipeline orchestrator for the broadband AI scraping project
"""
import logging
from typing import List, Dict, Optional
from pathlib import Path

from scrapers import ThinkBroadbandScraper, FibreNewsScraper, ISPreviewScraper
from processors import ContentParser, Deduplicator
from analyzers import AIAnalyzer, TrendAnalyzer
from output import OutputFormatter
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BroadbandAIPipeline:
    """Main pipeline for scraping and analyzing broadband AI news"""

    def __init__(self):
        """Initialize pipeline components"""
        logger.info("Initializing Broadband AI Pipeline")

        # Initialize scrapers
        self.scrapers = {}
        for source_key, source_config in config.SOURCES.items():
            if source_config['enabled']:
                scraper = self._create_scraper(source_key, source_config)
                if scraper:
                    self.scrapers[source_key] = scraper

        # Initialize processors
        self.parser = ContentParser()
        self.deduplicator = Deduplicator()

        # Initialize analyzers
        self.ai_analyzer = AIAnalyzer(
            ai_keywords=config.AI_KEYWORDS,
            use_case_categories=config.AI_USE_CASES,
            min_confidence=config.MIN_CONFIDENCE_SCORE
        )
        self.trend_analyzer = TrendAnalyzer()

        # Initialize output formatter
        self.formatter = OutputFormatter(config.OUTPUT_DIR)

        logger.info(f"Pipeline initialized with {len(self.scrapers)} scrapers")

    def _create_scraper(self, source_key: str, source_config: Dict):
        """Create appropriate scraper for source"""
        try:
            if source_key == 'thinkbroadband':
                return ThinkBroadbandScraper(
                    base_url=source_config['base_url'],
                    user_agent=config.USER_AGENT,
                    timeout=config.REQUEST_TIMEOUT
                )
            elif source_key == 'fibrenews':
                return FibreNewsScraper(
                    base_url=source_config['base_url'],
                    user_agent=config.USER_AGENT,
                    timeout=config.REQUEST_TIMEOUT
                )
            elif source_key == 'ispreview':
                return ISPreviewScraper(
                    base_url=source_config['base_url'],
                    user_agent=config.USER_AGENT,
                    timeout=config.REQUEST_TIMEOUT
                )
            else:
                logger.warning(f"Unknown source type: {source_key}")
                return None
        except Exception as e:
            logger.error(f"Failed to create scraper for {source_key}: {e}")
            return None

    def run(self, max_pages: int = 5, delay: float = 2.0,
            grouping: str = 'monthly') -> Dict:
        """
        Run the complete pipeline

        Args:
            max_pages: Maximum pages to scrape per source
            delay: Delay between requests in seconds
            grouping: Time grouping for trends ('monthly' or 'quarterly')

        Returns:
            Dictionary with all results
        """
        logger.info("=" * 80)
        logger.info("STARTING BROADBAND AI PIPELINE")
        logger.info("=" * 80)

        # Step 1: Scrape articles from all sources
        logger.info("\n[STEP 1] Scraping articles from sources...")
        all_articles = self.scrape_all_sources(max_pages, delay)
        logger.info(f"Total articles scraped: {len(all_articles)}")

        # Step 2: Parse and clean content
        logger.info("\n[STEP 2] Parsing and cleaning content...")
        parsed_articles = self.parse_articles(all_articles)
        logger.info(f"Articles parsed: {len(parsed_articles)}")

        # Step 3: Deduplicate
        logger.info("\n[STEP 3] Removing duplicates...")
        unique_articles = self.deduplicator.deduplicate(parsed_articles)
        logger.info(f"Unique articles: {len(unique_articles)}")

        # Step 4: Filter for AI content
        logger.info("\n[STEP 4] Filtering for AI-related content...")
        ai_articles = self.ai_analyzer.filter_ai_articles(unique_articles)
        logger.info(f"AI-related articles found: {len(ai_articles)}")

        # Step 5: Analyze AI content
        logger.info("\n[STEP 5] Analyzing AI content and categorizing...")
        analyzed_articles = self.analyze_ai_content(ai_articles)
        logger.info(f"Articles analyzed: {len(analyzed_articles)}")

        # Step 6: Generate summaries
        logger.info("\n[STEP 6] Generating summaries...")
        summaries = self.generate_summaries(analyzed_articles)

        # Step 7: Analyze trends
        logger.info("\n[STEP 7] Analyzing trends...")
        trends = self.trend_analyzer.analyze_trends(analyzed_articles, grouping)
        trend_summary = self.trend_analyzer.generate_trend_summary(trends)

        # Step 8: Export results
        logger.info("\n[STEP 8] Exporting results...")
        results = {
            'articles': analyzed_articles,
            'summary': summaries,
            'trends': trends,
            'trend_summary': trend_summary,
            'metadata': {
                'total_scraped': len(all_articles),
                'total_unique': len(unique_articles),
                'total_ai_related': len(ai_articles),
                'sources': list(self.scrapers.keys()),
                'grouping': grouping
            }
        }

        output_files = self.formatter.export_all(results)
        report_file = self.formatter.create_report(results)
        output_files['report'] = report_file

        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"\nResults exported to:")
        for format_type, filepath in output_files.items():
            logger.info(f"  {format_type}: {filepath}")

        return results

    def scrape_all_sources(self, max_pages: int = 5, delay: float = 2.0) -> List[Dict]:
        """Scrape articles from all enabled sources"""
        all_articles = []

        for source_key, scraper in self.scrapers.items():
            try:
                logger.info(f"\nScraping {source_key}...")
                articles = scraper.scrape_all(max_pages=max_pages, delay=delay)
                all_articles.extend(articles)
                logger.info(f"  -> Collected {len(articles)} articles from {source_key}")
            except Exception as e:
                logger.error(f"Error scraping {source_key}: {e}", exc_info=True)

        return all_articles

    def parse_articles(self, articles: List[Dict]) -> List[Dict]:
        """Parse and clean article content"""
        parsed = []
        for article in articles:
            try:
                parsed_article = self.parser.parse(article)
                parsed.append(parsed_article)
            except Exception as e:
                logger.warning(f"Failed to parse article: {e}")
                parsed.append(article)  # Keep unparsed if parsing fails

        return parsed

    def analyze_ai_content(self, articles: List[Dict]) -> List[Dict]:
        """Analyze articles for AI content"""
        analyzed = []
        for article in articles:
            try:
                analyzed_article = self.ai_analyzer.analyze(article)
                analyzed.append(analyzed_article)
            except Exception as e:
                logger.warning(f"Failed to analyze article: {e}")
                analyzed.append(article)  # Keep unanalyzed if analysis fails

        return analyzed

    def generate_summaries(self, analyzed_articles: List[Dict]) -> Dict:
        """Generate summaries for each source and overall"""
        summaries = {}

        # Overall summary
        summaries['overall'] = self.ai_analyzer.generate_summary(analyzed_articles)

        # Per-source summaries
        sources = set(article.get('source') for article in analyzed_articles)
        for source in sources:
            summaries[source] = self.ai_analyzer.generate_summary(
                analyzed_articles, source=source
            )

        return summaries


def main():
    """Main entry point"""
    try:
        # Create and run pipeline
        pipeline = BroadbandAIPipeline()

        # Run with configurable parameters
        results = pipeline.run(
            max_pages=5,  # Adjust as needed
            delay=config.DELAY_BETWEEN_REQUESTS,
            grouping='monthly'  # or 'quarterly'
        )

        logger.info("\nPipeline execution completed!")
        logger.info(f"Total AI-related articles: {len(results['articles'])}")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
