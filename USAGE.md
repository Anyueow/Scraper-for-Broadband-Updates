# Usage Guide

## Quick Start

### Basic Execution

Run the pipeline with default settings (5 pages per source, monthly trends):

```bash
python run.py
```

### Custom Parameters

```bash
# Scrape 10 pages per source
python run.py --pages 10

# Add 3-second delay between requests
python run.py --delay 3

# Use quarterly trend grouping
python run.py --grouping quarterly

# Combine all options
python run.py --pages 15 --delay 2.5 --grouping quarterly
```

## Configuration

### Editing config.py

#### Enable/Disable Sources

```python
SOURCES = {
    "thinkbroadband": {
        "enabled": True  # Set to False to disable
    },
    "fibrenews": {
        "enabled": True
    },
    "ispreview": {
        "enabled": False  # Disabled
    }
}
```

#### Customize AI Keywords

```python
AI_KEYWORDS = [
    "AI",
    "artificial intelligence",
    "machine learning",
    "your custom keyword"
]
```

#### Adjust Scraping Behavior

```python
DELAY_BETWEEN_REQUESTS = 2  # Seconds between requests
REQUEST_TIMEOUT = 30         # Request timeout in seconds
MAX_RETRIES = 3              # Number of retry attempts
```

## Programmatic Usage

### Basic Pipeline Execution

```python
from pipeline import BroadbandAIPipeline

# Create pipeline instance
pipeline = BroadbandAIPipeline()

# Run pipeline
results = pipeline.run(
    max_pages=5,
    delay=2.0,
    grouping='monthly'
)
```

### Accessing Results

```python
# All AI-related articles with analysis
articles = results['articles']

# Summary by source
summaries = results['summary']
overall_summary = summaries['overall']
thinkbroadband_summary = summaries.get('thinkBroadband', {})

# Trend analysis
trends = results['trends']
trend_summary = results['trend_summary']

# Metadata
metadata = results['metadata']
total_ai_articles = metadata['total_ai_related']
```

### Working with Individual Articles

```python
for article in results['articles']:
    print(f"Title: {article['title']}")
    print(f"Source: {article['source']}")
    print(f"Date: {article['date']}")
    print(f"URL: {article['url']}")
    print(f"Primary Use Case: {article['primary_use_case']}")
    print(f"Confidence: {article['primary_use_case_confidence']}")
    print(f"All Use Cases: {article['ai_use_cases']}")
    print(f"Sentiment: {article['sentiment']}")
    print(f"AI Mentions: {article['ai_mentions']}")
    print(f"Snippets: {article['ai_snippets']}")
    print("-" * 80)
```

### Using Individual Components

#### Just Scraping

```python
from scrapers import ThinkBroadbandScraper
import config

scraper = ThinkBroadbandScraper(
    base_url=config.SOURCES['thinkbroadband']['base_url'],
    user_agent=config.USER_AGENT,
    timeout=config.REQUEST_TIMEOUT
)

articles = scraper.scrape_all(max_pages=3, delay=2.0)
```

#### Just AI Analysis

```python
from analyzers import AIAnalyzer
import config

analyzer = AIAnalyzer(
    ai_keywords=config.AI_KEYWORDS,
    use_case_categories=config.AI_USE_CASES,
    min_confidence=0.3
)

# Analyze a single article
article = {
    'title': 'Broadband provider uses AI for network optimization',
    'content': 'The company deployed machine learning algorithms...',
    'summary': 'AI improves network performance'
}

analyzed = analyzer.analyze(article)
print(analyzed['primary_use_case'])
print(analyzed['ai_use_cases'])
```

#### Trend Analysis

```python
from analyzers import TrendAnalyzer

trend_analyzer = TrendAnalyzer()

# Analyze trends
trends = trend_analyzer.analyze_trends(
    articles=analyzed_articles,
    grouping='monthly'
)

# Generate summary
summary = trend_analyzer.generate_trend_summary(trends)
print(summary)
```

## Output Files

### Understanding Output

After running the pipeline, you'll find several files in the `output/` directory:

1. **broadband_ai_analysis_TIMESTAMP.json** - Complete results in JSON
2. **broadband_ai_analysis_TIMESTAMP_articles.csv** - Article data in CSV
3. **broadband_ai_analysis_TIMESTAMP_summary.json** - Summaries only
4. **broadband_ai_analysis_TIMESTAMP_trends.json** - Trend analysis only
5. **report.txt** - Human-readable summary report

### Working with Output Files

#### Loading JSON Results

```python
import json

with open('output/broadband_ai_analysis_20240115_143022.json', 'r') as f:
    data = json.load(f)

articles = data['articles']
summaries = data['summary']
```

#### Reading CSV in Pandas

```python
import pandas as pd

df = pd.read_csv('output/broadband_ai_analysis_20240115_143022_articles.csv')

# Filter by use case
network_articles = df[df['primary_use_case'] == 'network_optimization']

# Filter by sentiment
positive_articles = df[df['sentiment'] == 'positive']

# Count by source
source_counts = df['source'].value_counts()
```

## Advanced Usage

### Custom Pipeline Steps

```python
from pipeline import BroadbandAIPipeline

pipeline = BroadbandAIPipeline()

# Run only scraping
all_articles = pipeline.scrape_all_sources(max_pages=3, delay=2.0)

# Parse articles
parsed = pipeline.parse_articles(all_articles)

# Filter for AI content
ai_articles = pipeline.ai_analyzer.filter_ai_articles(parsed)

# Analyze
analyzed = pipeline.analyze_ai_content(ai_articles)

# Generate custom summary
summary = pipeline.ai_analyzer.generate_summary(
    analyzed,
    source='thinkBroadband'
)
```

### Exporting Custom Results

```python
from output import OutputFormatter
import config

formatter = OutputFormatter(config.OUTPUT_DIR)

# Export only specific data
custom_data = {
    'articles': filtered_articles,
    'metadata': {'custom': 'data'}
}

# Export as JSON
formatter.export_json(custom_data, 'custom_results.json')

# Export as CSV
formatter.export_csv(filtered_articles, 'custom_articles.csv')

# Create custom report
formatter.create_report(custom_data, 'custom_report.txt')
```

### Filtering and Analysis

```python
# Filter by date range
recent_articles = [
    a for a in results['articles']
    if a.get('date', '').startswith('2024-01')
]

# Filter by confidence threshold
high_confidence = [
    a for a in results['articles']
    if a.get('primary_use_case_confidence', 0) > 0.7
]

# Group by use case
from collections import defaultdict

by_use_case = defaultdict(list)
for article in results['articles']:
    use_case = article.get('primary_use_case', 'unknown')
    by_use_case[use_case].append(article)

# Print statistics
for use_case, articles in by_use_case.items():
    print(f"{use_case}: {len(articles)} articles")
```

## Scheduling Regular Runs

### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add line to run daily at 2 AM
0 2 * * * cd /path/to/Scraper-for-Broadband-Updates && /usr/bin/python3 run.py --pages 10

# Run weekly on Monday at 3 AM
0 3 * * 1 cd /path/to/Scraper-for-Broadband-Updates && /usr/bin/python3 run.py --pages 20 --grouping quarterly
```

### Using Task Scheduler (Windows)

Create a batch file `run_pipeline.bat`:

```batch
@echo off
cd C:\path\to\Scraper-for-Broadband-Updates
python run.py --pages 10
```

Then schedule it using Windows Task Scheduler.

## Best Practices

1. **Start small**: Test with `--pages 1` first
2. **Be respectful**: Use appropriate delays (2+ seconds)
3. **Monitor logs**: Check `pipeline.log` for issues
4. **Backup results**: Archive output files regularly
5. **Update regularly**: Run periodically to track trends
6. **Validate data**: Spot-check results for accuracy

## Troubleshooting

### Scraper Not Finding Articles

Check the HTML structure of the website - it may have changed. Update the scraper's CSS selectors in the appropriate scraper file.

### Slow Performance

- Reduce number of pages
- Increase delay between requests
- Disable unused sources

### High Memory Usage

- Process fewer pages at once
- Clear old output files
- Process sources individually

## Examples

See complete working examples in the `examples/` directory (if available).
