"""
Test script for enhanced LLM analysis pipeline.
Tests company and technology extraction on a small sample of articles.
"""

import sys
import pandas as pd
from pathlib import Path
from llm_analysis_pipeline_enhanced import BroadbandAIAnalyzer

def test_enhanced_pipeline(num_articles=5):
    """
    Test the enhanced pipeline on a small sample of articles.

    Args:
        num_articles: Number of articles to test with (default: 5)
    """
    print("="*80)
    print("TESTING ENHANCED LLM ANALYSIS PIPELINE")
    print("="*80)
    print(f"\nTesting with {num_articles} articles...")

    # Initialize analyzer with test CSV directory
    analyzer = BroadbandAIAnalyzer(
        scraped_output_dir=".",  # Current directory contains test_articles.csv
        model_name="gpt-oss:20b-cloud",
        fallback_model="gpt-oss:20b",
        cache_file="test_cache_enhanced.json",
        batch_size=2
    )

    # Check if taxonomies loaded successfully
    print("\n✓ Taxonomy Loading:")
    print(f"  - Company taxonomy loaded: {len(analyzer.company_taxonomy)} categories")
    print(f"  - Technology taxonomy loaded: {len(analyzer.tech_taxonomy)} categories")

    # Check model availability
    analyzer.active_model = analyzer._check_model_availability()

    # Load articles
    print("\n✓ Loading articles...")
    df = analyzer.load_and_normalize_csvs()

    # Limit to test sample
    df_test = df.head(num_articles)
    print(f"  - Loaded {len(df_test)} articles for testing")

    # Process articles
    print("\n✓ Processing articles through LLM...")
    results_df = analyzer.process_articles(df_test)

    # Display results
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)

    for idx, row in results_df.iterrows():
        print(f"\n--- Article {idx + 1} ---")
        print(f"Title: {row['title'][:80]}...")
        print(f"Primary Use Case: {row['primary_use_case']} (confidence: {row['primary_use_case_confidence']:.2f})")
        print(f"Sentiment: {row['sentiment']}")
        print(f"Companies: {row['companies_mentioned']}")
        print(f"Tech - Models: {row['technologies_foundation_models']}")
        print(f"Tech - Platforms: {row['technologies_platforms']}")
        print(f"Tech - Infrastructure: {row['technologies_infrastructure']}")
        print(f"Tech - Techniques: {row['technologies_techniques']}")

    # Save test results
    output_path = Path(__file__).parent / "test_enhanced_results.csv"
    results_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\n✓ Test results saved to: {output_path}")

    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"Total articles tested: {len(results_df)}")
    print(f"Articles with AI content: {len(results_df[results_df['ai_mention_count'] > 0])}")
    print(f"Articles with companies mentioned: {len(results_df[results_df['companies_mentioned'] != ''])}")
    print(f"Articles with technologies found: {len(results_df[results_df['technologies_foundation_models'] != ''])}")

    print("\n✓ Test complete!")
    return results_df

if __name__ == "__main__":
    # Get number of articles from command line or use default
    num_articles = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    test_enhanced_pipeline(num_articles)
