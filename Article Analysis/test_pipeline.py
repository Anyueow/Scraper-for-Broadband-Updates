"""
Test script to validate the LLM analysis pipeline with a small sample of articles.
"""
from llm_analysis_pipeline import BroadbandAIAnalyzer
import pandas as pd

def main():
    print("="*80)
    print("TESTING LLM ANALYSIS PIPELINE WITH SAMPLE DATA")
    print("="*80)

    # Initialize analyzer
    # Note: Using qwen2.5:32b since kimi-k2-thinking:cloud requires API authentication
    analyzer = BroadbandAIAnalyzer(
        model_name="qwen2.5:32b",
        fallback_model="llama3.1:8b",
        cache_file="test_cache.json"
    )

    # Check model availability
    analyzer.active_model = analyzer._check_model_availability()

    # Load all data
    print("\nLoading articles...")
    df = analyzer.load_and_normalize_csvs()

    # Take a sample of 15 articles - mix of different sources and dates
    print(f"\nSelecting 15 sample articles from {len(df)} total...")

    # Get 5 from each source if possible
    sample_dfs = []
    for source in df['source'].unique():
        source_df = df[df['source'] == source]
        sample_size = min(5, len(source_df))
        sample_dfs.append(source_df.head(sample_size))

    sample_df = pd.concat(sample_dfs, ignore_index=True)

    print(f"\nSample breakdown:")
    print(sample_df['source'].value_counts())

    # Process the sample
    print(f"\n{'='*80}")
    print("Processing sample articles through LLM...")
    print(f"{'='*80}")

    results_df = analyzer.process_articles(sample_df)

    # Display results
    print(f"\n{'='*80}")
    print("SAMPLE ANALYSIS RESULTS")
    print(f"{'='*80}")

    # Show AI-related articles
    ai_articles = results_df[results_df['ai_mention_count'] > 0]
    print(f"\nArticles with AI content: {len(ai_articles)}/{len(results_df)}")

    # Show articles with AI in title
    title_ai_articles = results_df[results_df['title_ai_mention_count'] > 0]
    print(f"Articles with AI mentions in TITLE: {len(title_ai_articles)}/{len(results_df)}")

    if len(ai_articles) > 0:
        print("\nAI-Related Articles:")
        print("-" * 80)
        for idx, row in ai_articles.head(10).iterrows():
            print(f"\n{idx + 1}. {row['title']}")
            print(f"   Source: {row['source']} | Date: {row['date']}")
            print(f"   Primary Use Case: {row['primary_use_case']} (confidence: {row['primary_use_case_confidence']:.2f})")
            print(f"   AI Mentions (all): {row['ai_mentions']}")
            print(f"   AI Mentions (title): {row['title_ai_mentions']} ({row['title_ai_mention_count']} mentions)")
            print(f"   Sentiment: {row['sentiment']}")
            print(f"   Summary: {row['summary'][:150]}...")

    # Show sentiment distribution
    print(f"\n{'='*80}")
    print("SENTIMENT DISTRIBUTION")
    print("-" * 80)
    print(results_df['sentiment'].value_counts())

    # Show use case distribution
    print(f"\n{'='*80}")
    print("PRIMARY USE CASE DISTRIBUTION")
    print("-" * 80)
    use_case_counts = results_df['primary_use_case'].value_counts()
    print(use_case_counts)

    # Save test results
    output_file = "test_unified_ai_analysis.csv"
    results_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n{'='*80}")
    print(f"✓ Test results saved to: {output_file}")
    print(f"{'='*80}")

    # Validation checks
    print("\nVALIDATION CHECKS:")
    print("-" * 80)

    # Check all required columns exist
    required_columns = [
        'source', 'date', 'title', 'url',
        'primary_use_case', 'primary_use_case_confidence',
        'ai_use_cases', 'sentiment',
        'ai_mention_count', 'ai_mentions',
        'word_count', 'summary'
    ]

    missing_columns = [col for col in required_columns if col not in results_df.columns]
    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
    else:
        print(f"✓ All required columns present")

    # Check for null values in critical fields
    print(f"✓ Rows with data: {len(results_df)}")
    print(f"✓ Articles with summaries: {len(results_df[results_df['summary'].notna()])}")
    print(f"✓ Articles with sentiment: {len(results_df[results_df['sentiment'].notna()])}")

    print("\n" + "="*80)
    print("TEST COMPLETE - Review results above before running full pipeline")
    print("="*80)

if __name__ == "__main__":
    main()
