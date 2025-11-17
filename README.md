# Broadband AI Scraping and Analysis Pipeline

A scalable pipeline for scraping, analyzing, and tracking AI mentions in UK broadband industry news.

## Overview

This project automatically scrapes and analyzes news articles from major UK broadband news sources to identify how and where artificial intelligence is being mentioned and applied in the broadband industry.

### Supported Sources

- **thinkBroadband** - News Archive
- **Fibre News** - All News section
- **ISPreview UK** - Latest news

## Features

### 1. Automated Scraping
- Crawls article metadata (title, date, URL, summary)
- Extracts full article content
- Robust error handling and retry logic
- Configurable rate limiting

### 2. Content Processing
- Removes boilerplate and navigation text
- Deduplicates articles across sources
- Normalizes and cleans text content

### 3. AI Detection & Categorization
- Identifies AI-related content using comprehensive keyword matching
- Categorizes AI use cases:
  - Network optimization
  - Customer support
  - Predictive maintenance
  - Marketing automation
  - Security
  - Analytics

### 4. Analysis & Insights
- Trend analysis over time (monthly/quarterly)
- Sentiment analysis (positive/neutral/negative)
- Use case frequency tracking
- Source-specific summaries

### 5. Flexible Output
- JSON format for programmatic access
- CSV format for spreadsheet analysis
- Human-readable text reports
- Structured data with confidence scores

## Installation

### Requirements
- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd Scraper-for-Broadband-Updates

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the pipeline with default settings:

```bash
python run.py
```

### Advanced Usage

Customize pipeline parameters:

```bash
# Scrape 10 pages per source with 3-second delays
python run.py --pages 10 --delay 3

# Use quarterly grouping for trend analysis
python run.py --grouping quarterly

# Combine options
python run.py --pages 15 --delay 2 --grouping monthly
```

### Programmatic Usage

```python
from pipeline import BroadbandAIPipeline

# Initialize pipeline
pipeline = BroadbandAIPipeline()

# Run with custom parameters
results = pipeline.run(
    max_pages=5,
    delay=2.0,
    grouping='monthly'
)

# Access results
ai_articles = results['articles']
summaries = results['summary']
trends = results['trends']
```

## Configuration

Edit `config.py` to customize:

- **Sources**: Enable/disable specific news sources
- **Keywords**: AI-related search terms
- **Use Cases**: Category definitions
- **Scraping**: Delays, timeouts, retries
- **Analysis**: Confidence thresholds
- **Output**: File formats and locations

## Output Structure

### JSON Output

```json
{
  "articles": [
    {
      "source": "thinkBroadband",
      "date": "2024-01-15",
      "title": "...",
      "url": "...",
      "summary": "...",
      "content": "...",
      "primary_use_case": "network_optimization",
      "primary_use_case_confidence": 0.85,
      "ai_use_cases": ["network_optimization", "analytics"],
      "sentiment": "positive",
      "ai_mention_count": 5,
      "ai_mentions": ["AI", "machine learning"],
      "ai_snippets": ["...context around AI mention..."],
      "word_count": 450
    }
  ],
  "summary": {
    "overall": {
      "total_articles": 42,
      "top_use_cases": {...},
      "summary": "..."
    }
  },
  "trends": {
    "grouping": "monthly",
    "periods": {...},
    "overall_statistics": {...}
  }
}
```

### CSV Output

The CSV file contains one row per article with columns:
- source
- date
- title
- url
- primary_use_case
- primary_use_case_confidence
- ai_use_cases (comma-separated)
- sentiment
- ai_mention_count
- ai_mentions (comma-separated)
- word_count
- summary

## Project Structure

```
Scraper-for-Broadband-Updates/
├── config.py                 # Configuration settings
├── pipeline.py              # Main pipeline orchestrator
├── run.py                   # CLI runner script
├── requirements.txt         # Python dependencies
├── scrapers/               # Web scraping modules
│   ├── base_scraper.py
│   ├── thinkbroadband_scraper.py
│   ├── fibrenews_scraper.py
│   └── ispreview_scraper.py
├── processors/             # Data processing modules
│   ├── content_parser.py
│   └── deduplicator.py
├── analyzers/              # Analysis modules
│   ├── ai_analyzer.py
│   └── trend_analyzer.py
├── output/                 # Output formatting
│   └── formatter.py
├── data/                   # Data storage (gitignored)
│   ├── raw/
│   └── processed/
└── output/                 # Results (gitignored)
```

## How It Works

### Pipeline Steps

1. **Scraping**: Crawls article lists and full content from each source
2. **Parsing**: Cleans and normalizes article text
3. **Deduplication**: Removes duplicate articles
4. **Filtering**: Identifies AI-related articles
5. **Analysis**: Categorizes use cases and analyzes sentiment
6. **Summarization**: Generates insights per source
7. **Trend Analysis**: Tracks changes over time
8. **Export**: Saves results in multiple formats

### AI Detection

The pipeline uses comprehensive keyword matching to identify AI-related content:
- Direct terms: "AI", "artificial intelligence", "machine learning"
- Related concepts: "neural network", "deep learning", "automation"
- Industry terms: "chatbot", "predictive analytics", "intelligent"

### Use Case Categorization

Articles are categorized based on context analysis:
- **Network Optimization**: Traffic management, routing, capacity planning
- **Customer Support**: Chatbots, virtual assistants, help desk automation
- **Predictive Maintenance**: Fault prediction, anomaly detection
- **Marketing Automation**: Personalization, targeting, campaigns
- **Security**: Threat detection, fraud prevention, intrusion detection
- **Analytics**: Data analysis, business intelligence, forecasting

## Customization

### Adding New Sources

1. Create a new scraper class inheriting from `BaseScraper`
2. Implement `scrape_article_list()` and `scrape_article_content()`
3. Add source configuration to `config.py`
4. Register scraper in `pipeline.py`

### Modifying Use Cases

Edit `AI_USE_CASES` in `config.py`:

```python
AI_USE_CASES = {
    "your_category": [
        "keyword1",
        "keyword2",
        "phrase with multiple words"
    ]
}
```

## Troubleshooting

### Common Issues

**No articles found**
- Check if website structure has changed
- Verify source URLs in `config.py`
- Review logs in `pipeline.log`

**Slow scraping**
- Increase `DELAY_BETWEEN_REQUESTS` in `config.py`
- Reduce `max_pages` parameter

**Memory issues with large datasets**
- Process sources individually
- Reduce `max_pages`
- Enable incremental processing

## Best Practices

1. **Respect website resources**: Use appropriate delays between requests
2. **Monitor logs**: Check `pipeline.log` for warnings and errors
3. **Regular updates**: Run periodically to track trends over time
4. **Validate results**: Review sample articles to ensure accuracy

## License

This project is for educational and research purposes. Ensure compliance with each website's terms of service and robots.txt when scraping.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Roadmap

- [ ] Add more news sources
- [ ] Implement advanced NLP for better categorization
- [ ] Add email notifications for new trends
- [ ] Create web dashboard for visualization
- [ ] Support for historical data analysis
- [ ] API endpoint for real-time queries

---

**Built with Python** | **Powered by BeautifulSoup, Requests, and Pandas**
