# CLAUDE.md - AI Assistant Guide for Broadband AI Scraping Pipeline

## Project Overview

This is a production-ready Python pipeline for scraping, analyzing, and tracking AI mentions in UK broadband industry news. The project uses a modular architecture to collect articles from multiple news sources, identify AI-related content, categorize use cases, and export insights in multiple formats.

**Key Characteristics:**
- **Language:** Python 3.8+
- **Architecture:** Object-oriented, modular pipeline design
- **Purpose:** Track AI adoption and discussion in UK broadband industry
- **Status:** Active development, functional core pipeline

## Repository Structure

```
Scraper-for-Broadband-Updates/
├── config.py                      # Central configuration (SINGLE SOURCE OF TRUTH)
├── pipeline.py                    # Main orchestrator (8-step workflow)
├── run.py                         # CLI entry point with argparse
├── requirements.txt               # Python dependencies (pinned versions)
├── README.md                      # User-facing documentation
├── USAGE.md                       # Detailed usage examples
├── .gitignore                     # Git ignore rules
│
├── scrapers/                      # Web scraping modules
│   ├── __init__.py               # Package exports
│   ├── base_scraper.py           # Abstract base class with common logic
│   ├── thinkbroadband_scraper.py # thinkBroadband implementation
│   ├── fibrenews_scraper.py      # FibreNews implementation
│   └── ispreview_scraper.py      # ISPreview UK implementation
│
├── processors/                    # Data processing modules
│   ├── __init__.py               # Package exports
│   ├── content_parser.py         # Text cleaning and normalization
│   └── deduplicator.py           # Duplicate article detection
│
├── analyzers/                     # AI analysis modules
│   ├── __init__.py               # Package exports
│   ├── ai_analyzer.py            # AI content detection and categorization
│   └── trend_analyzer.py         # Temporal trend analysis
│
├── output/                        # Output formatting (NOTE: See known issues)
│   └── formatter.py              # Export to JSON/CSV/TXT
│
├── data/                         # Data storage (GITIGNORED)
│   ├── raw/                      # Raw scraped data
│   └── processed/                # Processed/cleaned data
│
└── output/                       # Analysis results (GITIGNORED)
    ├── *.json                    # JSON exports
    ├── *.csv                     # CSV exports
    └── *.txt                     # Text reports
```

## Architecture and Design Patterns

### 1. Pipeline Architecture

The project follows a **linear pipeline pattern** with 8 distinct steps (see pipeline.py:86-164):

```
1. Scrape      → 2. Parse      → 3. Deduplicate → 4. Filter AI   →
5. Analyze AI  → 6. Summarize  → 7. Trends      → 8. Export
```

Each step is:
- **Independent**: Can be tested in isolation
- **Error-tolerant**: Failures are logged but don't crash the pipeline
- **Logged**: Every step logs progress to `pipeline.log` and console

### 2. Object-Oriented Design

**Abstract Base Classes:**
- `BaseScraper` (scrapers/base_scraper.py:16-89)
  - Provides common HTTP handling, retry logic, rate limiting
  - Requires subclasses to implement: `scrape_article_list()`, `scrape_article_content()`
  - Uses **Template Method Pattern** in `scrape_all()` method

**Key Classes:**
- `BroadbandAIPipeline` (pipeline.py:26-222) - Main orchestrator
- `ContentParser` (processors/content_parser.py) - Text processing
- `Deduplicator` (processors/deduplicator.py) - Duplicate detection
- `AIAnalyzer` (analyzers/ai_analyzer.py) - AI detection and categorization
- `TrendAnalyzer` (analyzers/trend_analyzer.py) - Temporal analysis
- `OutputFormatter` (output/formatter.py) - Multi-format export

### 3. Configuration Management

**CRITICAL:** `config.py` is the **single source of truth** for all settings.

**Configuration Categories:**
1. **Directories** (lines 7-16): Auto-created using pathlib
2. **Sources** (lines 19-38): News source URLs and enable/disable flags
3. **AI Keywords** (lines 41-57): 15 keywords for AI content detection
4. **Use Cases** (lines 60-89): 6 categories with associated keywords
5. **Scraping Settings** (lines 92-95): Delays, timeouts, retries
6. **Analysis Settings** (lines 98-99): Confidence thresholds
7. **Output Settings** (lines 102-103): Formats and filename prefix

**Key Pattern:** All modules import and use `config` - never hardcode values.

### 4. Error Handling Strategy

The codebase uses **graceful degradation**:

```python
# Pattern used throughout:
try:
    result = risky_operation()
    processed.append(result)
except Exception as e:
    logger.warning(f"Operation failed: {e}")
    processed.append(fallback_value)  # Keep partial results
```

This ensures the pipeline continues even if individual operations fail.

## Development Workflow

### Initial Setup

```bash
# Clone and setup
git clone <repository-url>
cd Scraper-for-Broadband-Updates

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python run.py --pages 1  # Test with minimal scraping
```

### Running the Pipeline

**CLI Usage:**
```bash
# Basic run
python run.py

# Custom parameters
python run.py --pages 10 --delay 3 --grouping quarterly

# See help
python run.py --help
```

**Programmatic Usage:**
```python
from pipeline import BroadbandAIPipeline
import config

pipeline = BroadbandAIPipeline()
results = pipeline.run(max_pages=5, delay=2.0, grouping='monthly')
```

### Output Locations

- **Logs:** `pipeline.log` (root directory)
- **Data:** `data/raw/` and `data/processed/` (gitignored)
- **Results:** `output/` directory (gitignored)
  - JSON: Complete structured results
  - CSV: Article data for spreadsheet analysis
  - TXT: Human-readable report

## Key Conventions and Patterns

### 1. Logging

**Standard Pattern:**
```python
import logging

logger = logging.getLogger(__name__)

# Use descriptive messages
logger.info(f"Processing {count} articles")
logger.warning(f"Failed to parse article: {url}")
logger.error(f"Critical error: {e}", exc_info=True)
```

**Log Levels:**
- `INFO`: Normal operation progress
- `WARNING`: Recoverable errors (e.g., failed to parse one article)
- `ERROR`: Serious issues (e.g., scraper initialization failed)

### 2. Data Structures

**Article Dictionary Structure:**
```python
{
    'source': 'thinkbroadband',          # Source identifier
    'title': 'Article Title',             # Article title
    'url': 'https://...',                 # Full URL
    'date': '2024-01-15',                 # ISO date format
    'summary': 'Brief summary...',        # Short description
    'content': 'Full article text...',    # Complete article text
    'word_count': 450,                    # Word count
    'keywords': ['AI', 'broadband'],      # Extracted keywords

    # Added by AI analysis:
    'primary_use_case': 'network_optimization',
    'primary_use_case_confidence': 0.85,
    'ai_use_cases': ['network_optimization', 'analytics'],
    'sentiment': 'positive',              # positive/neutral/negative
    'ai_mention_count': 5,
    'ai_mentions': ['AI', 'machine learning'],
    'ai_snippets': ['...context around AI mention...']
}
```

### 3. Scraper Implementation Pattern

When adding a new scraper:

```python
from scrapers.base_scraper import BaseScraper
from typing import List, Dict, Optional

class NewSourceScraper(BaseScraper):
    def __init__(self, base_url: str, user_agent: str, timeout: int = 30):
        super().__init__('newsource', base_url, user_agent, timeout)

    def scrape_article_list(self, max_pages: int = 10) -> List[Dict]:
        """Return list of {'title', 'url', 'date', 'summary'}"""
        articles = []
        # Implementation here
        return articles

    def scrape_article_content(self, url: str) -> Optional[Dict]:
        """Return {'content': '...', 'word_count': N}"""
        soup = self.fetch_page(url)  # Built-in retry logic
        if not soup:
            return None
        # Extract content
        return {'content': content, 'word_count': len(content.split())}
```

### 4. Import Pattern

**Package imports** (in __init__.py):
```python
# scrapers/__init__.py
from .thinkbroadband_scraper import ThinkBroadbandScraper
from .fibrenews_scraper import FibreNewsScraper
from .ispreview_scraper import ISPreviewScraper

__all__ = ['ThinkBroadbandScraper', 'FibreNewsScraper', 'ISPreviewScraper']
```

**Usage:**
```python
# Preferred
from scrapers import ThinkBroadbandScraper

# Also acceptable
from scrapers.thinkbroadband_scraper import ThinkBroadbandScraper
```

### 5. BeautifulSoup Patterns

**Standard scraping pattern:**
```python
soup = self.fetch_page(url)  # Returns BeautifulSoup or None
if not soup:
    return None

# Safe attribute access
title = soup.find('h1', class_='article-title')
title_text = title.get_text(strip=True) if title else 'Unknown'

# Finding multiple elements
articles = soup.find_all('article', class_='news-item')
for article in articles:
    # Process each
    pass
```

## Common Tasks and How to Approach Them

### Task 1: Add a New News Source

**Steps:**
1. Create new scraper in `scrapers/new_source_scraper.py` inheriting from `BaseScraper`
2. Implement `scrape_article_list()` and `scrape_article_content()`
3. Add source configuration to `config.py` SOURCES dict
4. Import scraper in `scrapers/__init__.py`
5. Add scraper instantiation logic in `pipeline.py:_create_scraper()` (lines 58-84)
6. Test with `python run.py --pages 1`

**Files to modify:**
- `scrapers/new_source_scraper.py` (new)
- `scrapers/__init__.py`
- `config.py` (SOURCES section)
- `pipeline.py` (_create_scraper method)

### Task 2: Modify AI Keywords or Use Cases

**ONLY modify `config.py`:**

```python
# Add keyword to AI_KEYWORDS (line 41)
AI_KEYWORDS = [
    "AI",
    # ... existing keywords ...
    "your new keyword"
]

# Add new use case category to AI_USE_CASES (line 60)
AI_USE_CASES = {
    # ... existing categories ...
    "new_category": [
        "keyword1",
        "keyword2",
        "multi word phrase"
    ]
}
```

No other files need modification - the analyzers automatically use these values.

### Task 3: Adjust Scraping Behavior

**Scenario: Website is rate-limiting or timing out**

**Modify `config.py`:**
```python
DELAY_BETWEEN_REQUESTS = 3  # Increase from 2
REQUEST_TIMEOUT = 45         # Increase from 30
MAX_RETRIES = 5              # Increase from 3
```

**Or use CLI flags:**
```bash
python run.py --delay 3.5
```

### Task 4: Fix a Broken Scraper

**Common causes:**
1. Website HTML structure changed
2. URL format changed
3. Anti-scraping measures

**Debugging approach:**
1. Check logs in `pipeline.log` for error messages
2. Manually visit the website and inspect HTML
3. Update CSS selectors in the specific scraper file
4. Test with `--pages 1` to verify fix

**Example fix in scraper:**
```python
# Old (broken)
articles = soup.find_all('div', class_='article')

# New (updated selector)
articles = soup.find_all('article', class_='news-item')
```

### Task 5: Add New Output Format

**Create exporter in `output/formatter.py`:**
```python
def export_xml(self, data: Dict, filename: str) -> Path:
    """Export results as XML"""
    filepath = self.output_dir / filename
    # Implementation
    return filepath
```

**Update `config.py`:**
```python
OUTPUT_FORMATS = ["json", "csv", "xml"]
```

**Update `pipeline.py` or formatter to use new format.**

### Task 6: Debug the Pipeline

**Enable debug logging:**
```python
# In pipeline.py or run.py
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO
    # ... rest of config
)
```

**Run specific pipeline steps:**
```python
from pipeline import BroadbandAIPipeline

pipeline = BroadbandAIPipeline()

# Test just scraping
articles = pipeline.scrape_all_sources(max_pages=1, delay=2.0)
print(f"Scraped {len(articles)} articles")

# Test just parsing
parsed = pipeline.parse_articles(articles)

# etc.
```

## Important Notes and Gotchas

### Known Issues

**1. Missing OutputFormatter Module (CRITICAL)**
- **Issue:** `pipeline.py:11` imports `from output import OutputFormatter` but this module is referenced but may not be fully implemented
- **Impact:** Pipeline will fail on import if the module is incomplete
- **Check:** Verify `output/formatter.py` exists and has `OutputFormatter` class with methods: `export_all()`, `create_report()`, `export_json()`, `export_csv()`
- **Location:** `output/formatter.py` should contain the implementation

**2. Data Directories Are Gitignored**
- **Impact:** First-time users need to let config.py auto-create directories (it does this automatically)
- **Note:** `data/raw/`, `data/processed/`, and `output/` are in .gitignore
- **Action:** No action needed - directories are auto-created by config.py:15-16

**3. Selenium/WebDriver Setup**
- **Purpose:** Selenium is installed for JavaScript-heavy sites
- **Current Use:** Not currently used by existing scrapers (all use BeautifulSoup)
- **If Used:** Requires ChromeDriver/GeckoDriver installation
- **Cleanup:** WebDriver executables are gitignored (line 34-35 of .gitignore)

**4. Date Parsing Fragility**
- **Issue:** Each scraper must handle different date formats
- **Current:** `BaseScraper.extract_date()` is a placeholder (base_scraper.py:51-58)
- **Action:** Each scraper implementation should override with proper date parsing
- **Recommended:** Use `python-dateutil` for robust parsing

**5. No Formal Testing Infrastructure**
- **Current State:** No pytest, unittest, or CI/CD
- **Impact:** Manual testing required
- **Testing Approach:** Use `--pages 1` for quick validation
- **Future:** Consider adding pytest with fixtures for sample HTML

### Rate Limiting and Ethics

**CRITICAL: Respect website resources**

1. **Default delay:** 2 seconds between requests (config.py:94)
2. **Minimum recommended:** Never go below 1 second
3. **Retry logic:** Exponential backoff (2^attempt seconds) in base_scraper.py:36
4. **User Agent:** Identifies as Chrome browser (config.py:92)
5. **Best Practice:** Check each site's `robots.txt` before scraping

**Commands to check robots.txt:**
```bash
curl https://www.thinkbroadband.com/robots.txt
curl https://www.fibrenews.co.uk/robots.txt
curl https://www.ispreview.co.uk/robots.txt
```

### Performance Considerations

**Memory:**
- Scraped articles are kept in memory during pipeline execution
- For large scrapes (100+ pages), monitor memory usage
- Consider processing sources individually for very large datasets

**Speed:**
- Main bottleneck is rate limiting (intentional)
- Pipeline is single-threaded (prevents overwhelming sites)
- 5 pages × 3 sources × 2 sec delay ≈ 5-10 minutes typical runtime

**Optimization opportunities:**
- Parallel source scraping (requires careful rate limiting)
- Incremental processing (avoid re-scraping)
- Database storage for large datasets

## Testing Guidelines

### Manual Testing Workflow

**1. Quick Smoke Test:**
```bash
python run.py --pages 1 --delay 1
```
Expected: Should complete in 1-2 minutes, produce output files

**2. Single Source Test:**
Edit `config.py` to disable all but one source:
```python
SOURCES = {
    "thinkbroadband": {"enabled": True, ...},
    "fibrenews": {"enabled": False, ...},
    "ispreview": {"enabled": False, ...}
}
```

**3. Component Testing:**
```python
# Test individual scraper
from scrapers import ThinkBroadbandScraper
import config

scraper = ThinkBroadbandScraper(
    base_url=config.SOURCES['thinkbroadband']['base_url'],
    user_agent=config.USER_AGENT,
    timeout=config.REQUEST_TIMEOUT
)
articles = scraper.scrape_all(max_pages=1, delay=1.0)
print(f"Scraped {len(articles)} articles")
```

**4. Validation Checks:**
- Check `pipeline.log` for errors
- Verify output files exist in `output/`
- Spot-check CSV/JSON for data quality
- Verify AI detection is working (not all articles flagged)

### Future Testing Infrastructure

**Recommended additions:**

**Unit tests (pytest):**
```python
# tests/test_content_parser.py
def test_parser_removes_boilerplate():
    parser = ContentParser()
    article = {'content': 'Cookie Policy ... actual content ... Social Media'}
    parsed = parser.parse(article)
    assert 'Cookie Policy' not in parsed['content']
    assert 'actual content' in parsed['content']
```

**Integration tests:**
```python
# tests/test_pipeline.py
def test_pipeline_end_to_end():
    pipeline = BroadbandAIPipeline()
    results = pipeline.run(max_pages=1, delay=0.5)
    assert results['metadata']['total_scraped'] > 0
    assert 'articles' in results
```

**Fixtures for HTML samples:**
```python
# tests/fixtures/sample_thinkbroadband.html
# Store sample HTML pages for offline testing
```

## Git Workflow

### Branch Strategy

**Current Setup:**
- **Main/Master:** Production-ready code
- **Feature Branches:** Use `claude/` prefix for AI assistant work
- **Convention:** `claude/descriptive-name-<session-id>`

### Commit Guidelines

**Commit message format:**
```
<type>: <short description>

<optional longer description>

<optional issue reference>
```

**Types:**
- `feat`: New feature (e.g., new scraper, new analysis)
- `fix`: Bug fix (e.g., broken CSS selector)
- `docs`: Documentation only (README, USAGE, CLAUDE.md)
- `refactor`: Code restructuring without behavior change
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance (e.g., dependency updates)

**Examples:**
```
feat: Add ISPreview UK scraper

Implements scraper for ISPreview UK news section with pagination
support and content extraction.

fix: Update thinkBroadband CSS selectors

Website redesign changed article container class from 'article'
to 'news-item'. Updated scraper accordingly.

docs: Update CLAUDE.md with testing guidelines
```

### Pull Request Workflow

**Before creating PR:**
1. Test changes locally with `python run.py --pages 1`
2. Check `pipeline.log` for errors
3. Verify output files are generated correctly
4. Update documentation if needed (README.md, USAGE.md, CLAUDE.md)

**PR Description Template:**
```markdown
## Changes
- Brief bullet points of changes

## Testing
- How was this tested?
- What edge cases were considered?

## Checklist
- [ ] Code runs without errors
- [ ] Logs are clean (no unexpected warnings)
- [ ] Documentation updated if needed
- [ ] No sensitive data in commits
```

### Working with AI Assistant Branches

**Current branch:** `claude/claude-md-mi3oykfpe0hsp6sh-01QfqjzY2vfni5o2zwaXrxQk`

**Push commands:**
```bash
# Always use -u flag for new branches
git push -u origin claude/your-branch-name

# Retry logic if network issues (up to 4 times with exponential backoff)
```

**CRITICAL:**
- Branch MUST start with `claude/` prefix
- Branch MUST end with matching session ID
- Otherwise push will fail with 403 error

## Additional Resources

### External Documentation

**Python Libraries:**
- [Requests](https://docs.python-requests.org/) - HTTP library
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML parsing
- [Pandas](https://pandas.pydata.org/docs/) - Data manipulation
- [NLTK](https://www.nltk.org/) - Natural language processing

**Scraped Websites:**
- [thinkBroadband News](https://www.thinkbroadband.com/news)
- [FibreNews](https://www.fibrenews.co.uk/news)
- [ISPreview UK](https://www.ispreview.co.uk/index.php/category/news)

### Project Documentation

- `README.md` - High-level overview, features, installation
- `USAGE.md` - Detailed usage examples, API documentation
- `CLAUDE.md` - This file (AI assistant guide)

### Useful Commands Reference

```bash
# Development
python run.py --pages 1                    # Quick test
python run.py --pages 10 --delay 3        # Production run
python -m pdb run.py                      # Debug mode

# Check logs
tail -f pipeline.log                      # Watch logs in real-time
grep ERROR pipeline.log                   # Find errors
grep WARNING pipeline.log                 # Find warnings

# File operations
ls -lh output/                            # Check output files
cat output/report.txt                     # View text report
head -20 output/*.csv                     # Preview CSV output

# Git operations
git status                                # Check working tree
git log --oneline -10                     # Recent commits
git diff                                  # Unstaged changes
git add -p                                # Stage changes interactively

# Virtual environment
python3 -m venv venv                      # Create venv
source venv/bin/activate                  # Activate (Linux/Mac)
venv\Scripts\activate                     # Activate (Windows)
deactivate                                # Deactivate
pip freeze > requirements.txt             # Update requirements

# Dependency management
pip install -r requirements.txt           # Install all deps
pip list --outdated                       # Check for updates
pip install --upgrade package_name        # Update specific package
```

## Quick Reference Card

### File Modification Frequency

**Frequently Modified:**
- `config.py` - Adjust settings, add sources/keywords
- `scrapers/*_scraper.py` - Fix broken selectors, add sources

**Occasionally Modified:**
- `pipeline.py` - Add pipeline steps, modify workflow
- `analyzers/*.py` - Improve analysis algorithms
- `processors/*.py` - Enhance text processing

**Rarely Modified:**
- `run.py` - CLI interface is stable
- `scrapers/base_scraper.py` - Core functionality is solid
- `requirements.txt` - Only for dependency updates

**Read-Only (for users):**
- `README.md`, `USAGE.md` - User documentation
- `.gitignore` - Git exclusions

### Priority Checklist for New AI Assistants

When first working on this codebase:

1. ✅ Read this CLAUDE.md completely
2. ✅ Verify OutputFormatter exists (check output/formatter.py)
3. ✅ Run `python run.py --pages 1` to ensure pipeline works
4. ✅ Check `pipeline.log` for any errors or warnings
5. ✅ Review recent commits: `git log --oneline -10`
6. ✅ Understand the 8-step pipeline flow (pipeline.py:86-164)
7. ✅ Know where to find settings (config.py)
8. ✅ Understand data flow: Scrape → Process → Analyze → Export

### Emergency Debugging

**Pipeline crashes immediately:**
1. Check if `output/formatter.py` exists and is complete
2. Verify all imports work: `python -c "from pipeline import BroadbandAIPipeline"`
3. Check Python version: `python --version` (should be 3.8+)
4. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

**No articles found:**
1. Test with `--pages 1` on single source
2. Check if website is accessible: `curl https://www.thinkbroadband.com/news`
3. Review website HTML structure (may have changed)
4. Check logs for specific scraper errors

**Output files not generated:**
1. Check if `output/` directory exists (auto-created by config.py)
2. Verify OutputFormatter.export_all() method exists
3. Check file permissions on output directory
4. Look for export errors in pipeline.log

---

**Last Updated:** 2025-11-17
**Document Version:** 1.0.0
**Maintained By:** AI Assistant Team
**Questions?** Check README.md, USAGE.md, or examine pipeline.log for runtime issues.
