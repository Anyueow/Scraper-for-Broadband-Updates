"""
Monitoring script to check the progress of the LLM analysis pipeline.
"""
import json
import os
from pathlib import Path
import time

def monitor_progress(cache_file="analysis_cache.json", check_interval=30):
    """
    Monitor the progress of the analysis pipeline by checking the cache file.

    Args:
        cache_file: Path to the cache file
        check_interval: How often to check progress (seconds)
    """
    cache_path = os.path.join(os.path.dirname(__file__), cache_file)

    print("="*80)
    print("LLM ANALYSIS PIPELINE MONITOR")
    print("="*80)
    print(f"Monitoring cache file: {cache_file}")
    print(f"Press Ctrl+C to stop monitoring")
    print("="*80)

    # Get total article count
    from llm_analysis_pipeline import BroadbandAIAnalyzer
    analyzer = BroadbandAIAnalyzer(cache_file=cache_file)
    try:
        df = analyzer.load_and_normalize_csvs()
        total_articles = len(df)
    except Exception as e:
        print(f"Could not load article count: {e}")
        total_articles = 1775  # Fallback to known count

    print(f"Total articles to process: {total_articles}\n")

    last_count = 0
    start_time = time.time()

    try:
        while True:
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r') as f:
                        cache = json.load(f)

                    processed = len(cache)
                    ai_articles = sum(1 for v in cache.values() if v.get('has_ai_content', False))

                    # Calculate progress
                    progress_pct = (processed / total_articles) * 100 if total_articles > 0 else 0

                    # Calculate processing rate
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        rate = processed / elapsed
                        if rate > 0:
                            remaining = (total_articles - processed) / rate
                            eta_minutes = remaining / 60
                        else:
                            eta_minutes = 0
                    else:
                        eta_minutes = 0

                    # Articles processed since last check
                    new_articles = processed - last_count
                    last_count = processed

                    # Display progress
                    print(f"\r[{time.strftime('%H:%M:%S')}] Progress: {processed}/{total_articles} ({progress_pct:.1f}%) | "
                          f"AI Articles: {ai_articles} | "
                          f"Rate: {rate:.2f} art/sec | "
                          f"ETA: {eta_minutes:.1f} min | "
                          f"New: +{new_articles}     ", end='', flush=True)

                except json.JSONDecodeError:
                    print(f"\r[{time.strftime('%H:%M:%S')}] Cache file is being written... ", end='', flush=True)
                except Exception as e:
                    print(f"\r[{time.strftime('%H:%M:%S')}] Error reading cache: {e} ", end='', flush=True)
            else:
                print(f"\r[{time.strftime('%H:%M:%S')}] Waiting for cache file to be created... ", end='', flush=True)

            time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        print("="*80)
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cache = json.load(f)
            processed = len(cache)
            ai_articles = sum(1 for v in cache.values() if v.get('has_ai_content', False))
            print(f"Final Status:")
            print(f"  Articles processed: {processed}/{total_articles}")
            print(f"  Articles with AI content: {ai_articles}")
            print(f"  Progress: {(processed/total_articles)*100:.1f}%")
        print("="*80)

def show_cache_stats(cache_file="analysis_cache.json"):
    """Show detailed statistics from the cache file."""
    cache_path = os.path.join(os.path.dirname(__file__), cache_file)

    if not os.path.exists(cache_path):
        print(f"Cache file not found: {cache_file}")
        return

    with open(cache_path, 'r') as f:
        cache = json.load(f)

    print("="*80)
    print("CACHE STATISTICS")
    print("="*80)

    total = len(cache)
    ai_articles = [v for v in cache.values() if v.get('has_ai_content', False)]

    print(f"Total cached articles: {total}")
    print(f"Articles with AI content: {len(ai_articles)}")
    print(f"Articles without AI content: {total - len(ai_articles)}")

    # Sentiment distribution
    sentiments = {}
    for v in ai_articles:
        sent = v.get('sentiment', 'unknown')
        sentiments[sent] = sentiments.get(sent, 0) + 1

    if sentiments:
        print(f"\nSentiment distribution (AI articles):")
        for sent, count in sorted(sentiments.items(), key=lambda x: -x[1]):
            print(f"  {sent}: {count}")

    # Use case distribution
    use_cases = {}
    for v in ai_articles:
        uc = v.get('primary_use_case')
        if uc:
            use_cases[uc] = use_cases.get(uc, 0) + 1

    if use_cases:
        print(f"\nPrimary use case distribution:")
        for uc, count in sorted(use_cases.items(), key=lambda x: -x[1]):
            print(f"  {uc}: {count}")

    print("="*80)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        show_cache_stats()
    else:
        monitor_progress()
