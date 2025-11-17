#!/usr/bin/env python3
"""
Simple runner script for the Broadband AI Pipeline

Usage:
    python run.py [--pages N] [--delay SECONDS] [--grouping monthly|quarterly]
"""
import argparse
import sys
from pipeline import BroadbandAIPipeline
import config


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Run the Broadband AI Scraping and Analysis Pipeline'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        help='Maximum pages to scrape per source (default: 5)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=config.DELAY_BETWEEN_REQUESTS,
        help=f'Delay between requests in seconds (default: {config.DELAY_BETWEEN_REQUESTS})'
    )

    parser.add_argument(
        '--grouping',
        choices=['monthly', 'quarterly'],
        default='monthly',
        help='Time grouping for trend analysis (default: monthly)'
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    print("=" * 80)
    print("BROADBAND AI SCRAPING AND ANALYSIS PIPELINE")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Max pages per source: {args.pages}")
    print(f"  Delay between requests: {args.delay}s")
    print(f"  Trend grouping: {args.grouping}")
    print(f"  Output directory: {config.OUTPUT_DIR}")
    print("\n" + "=" * 80 + "\n")

    try:
        # Create and run pipeline
        pipeline = BroadbandAIPipeline()
        results = pipeline.run(
            max_pages=args.pages,
            delay=args.delay,
            grouping=args.grouping
        )

        # Print summary
        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Total articles scraped: {results['metadata']['total_scraped']}")
        print(f"Unique articles: {results['metadata']['total_unique']}")
        print(f"AI-related articles: {results['metadata']['total_ai_related']}")
        print(f"\nResults saved to: {config.OUTPUT_DIR}")
        print("=" * 80 + "\n")

        return 0

    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nERROR: Pipeline failed - {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
