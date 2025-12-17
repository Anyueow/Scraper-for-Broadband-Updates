# Repository Structure & Organization
## Telco AI Analysis Project

**Purpose:** This document defines the canonical structure for the Telco AI Analysis project, designed for publication-ready research.

---

## 📁 Directory Structure

```
Scraper-for-Broadband-Updates/
│
├── 📄 README.md                          # Project overview, quick start guide
├── 📄 CLAUDE.md                          # AI assistant instructions (use case taxonomy, analysis guidelines)
├── 📄 STRATEGIC_ANALYSIS.md              # First-principles analysis, journalism angles, story ideas
├── 📄 REPOSITORY_STRUCTURE.md            # This file (canonical structure reference)
├── 📄 METHODOLOGY.md                     # Research methodology, data quality, validation approach
├── 📄 requirements.txt                   # Python dependencies
├── 📄 .gitignore                         # Git ignore rules
│
├── 📂 01_data_collection/                # Web scraping and data ingestion
│   ├── scrapers/
│   │   ├── fibernews_scraper.py         # FiberNews article scraper
│   │   ├── ispreview_scraper.py         # ISPreview article scraper
│   │   ├── thinkbroadband_scraper.py    # ThinkBroadband article scraper
│   │   ├── base_scraper.py              # Shared scraper utilities
│   │   └── __init__.py
│   │
│   ├── manual_inputs/                    # Manually curated articles (e.g., from company newsrooms, paywalled sources)
│   │   ├── AI_Articles_By_Company.xlsx  # Big firm company-specific articles
│   │   ├── increased_scope.csv          # Expanded scope articles (infrastructure companies)
│   │   └── README.md                    # Documentation for manual inputs
│   │
│   └── raw_outputs/                      # Raw scraped data (CSV)
│       ├── fibrenews_articles_YYYYMMDD.csv
│       ├── ispreview_articles_YYYYMMDD.csv
│       ├── thinkbroadband_articles_YYYYMMDD.csv
│       └── scraping_logs/               # Scraper error logs, run metadata
│
├── 📂 02_analysis/                       # LLM analysis pipelines and caching
│   ├── pipelines/
│   │   ├── llm_analysis_pipeline.py     # Main LLM analysis orchestrator
│   │   ├── big_firm_analyzer.py         # Deep analysis for major company articles
│   │   ├── use_case_classifier.py       # Use case categorization logic
│   │   ├── sentiment_analyzer.py        # Sentiment analysis module
│   │   ├── entity_extractor.py          # Company, technology, person name extraction
│   │   └── __init__.py
│   │
│   ├── caches/                           # Analysis result caches (avoid re-running LLM)
│   │   ├── analysis_cache.json          # General article analysis cache
│   │   ├── big_firm_cache.json          # Big firm analysis cache
│   │   └── cache_README.md              # Cache structure documentation
│   │
│   ├── configs/                          # Analysis configuration files
│   │   ├── use_case_taxonomy.json       # Canonical 6-use-case definitions
│   │   ├── company_taxonomy.json        # Standardized company names, metadata
│   │   ├── technology_taxonomy.json     # AI/ML technologies to track
│   │   └── llm_prompts.json             # LLM prompt templates
│   │
│   └── utilities/
│       ├── ollama_client.py             # Ollama API wrapper
│       ├── text_processing.py           # Text cleaning, tokenization
│       └── validation.py                # Data validation helpers
│
├── 📂 03_processed_data/                 # Cleaned, analyzed, unified datasets
│   ├── unified_ai_analysis.csv          # Master dataset (all articles + LLM analysis)
│   ├── big_firm_analysis.csv            # Company-specific deep-dive results
│   ├── company_profiles.csv             # Company-level aggregations
│   ├── use_case_statistics.csv          # Use case frequency, trends
│   ├── technology_mentions.csv          # Technology stack tracking
│   ├── sentiment_trends.csv             # Sentiment over time
│   └── data_dictionary.md               # Column definitions for all datasets
│
├── 📂 04_advanced_analysis/              # Specialized analytical scripts
│   ├── time_series_analysis.py          # Temporal trend analysis
│   ├── company_benchmarking.py          # Company-to-company comparisons
│   ├── use_case_opportunity_matrix.py   # ROI vs. adoption analysis
│   ├── geographic_analysis.py           # Regional/geographic trends
│   ├── technology_cooccurrence.py       # Tech stack correlation analysis
│   ├── sentiment_evolution.py           # Sentiment trend modeling
│   ├── ai_hype_vs_reality.py            # Public commitment vs. deployment evidence
│   ├── workforce_impact_analysis.py     # Job displacement/creation tracking
│   └── notebooks/                        # Jupyter notebooks for ad-hoc exploration
│       ├── exploratory_data_analysis.ipynb
│       └── publication_charts.ipynb
│
├── 📂 05_visualizations/                 # Dashboards and publication-ready charts
│   ├── dashboard.py                      # Streamlit interactive dashboard
│   ├── publication_charts/              # Static charts for articles/reports (PNG, SVG)
│   │   ├── use_case_distribution.png
│   │   ├── company_maturity_heatmap.png
│   │   ├── sentiment_timeline.png
│   │   ├── ai_hype_vs_reality_matrix.png
│   │   └── README.md                    # Chart descriptions and usage rights
│   │
│   └── dashboard_components/            # Modular dashboard components
│       ├── time_series_tab.py
│       ├── use_case_tab.py
│       ├── company_tab.py
│       └── __init__.py
│
├── 📂 06_outputs/                        # Publication-ready reports and exports
│   ├── reports/
│   │   ├── executive_summary.md         # 2-page executive summary
│   │   ├── full_report.pdf              # Comprehensive report (20-40 pages)
│   │   ├── industry_benchmark_report.pdf # Commercial product
│   │   └── academic_paper.pdf           # Academic/policy paper
│   │
│   ├── data_releases/                    # Public data releases
│   │   ├── telco_ai_index_2025_v1.csv   # Public dataset (anonymized/aggregated)
│   │   ├── codebook.pdf                 # Data dictionary for public release
│   │   └── LICENSE.txt                  # Data usage license
│   │
│   └── media_kits/                       # Assets for journalists/publications
│       ├── press_release.md
│       ├── fact_sheet.pdf
│       ├── key_findings_infographic.png
│       └── expert_quotes.md
│
├── 📂 07_validation/                     # Quality assurance and validation
│   ├── validation_scripts/
│   │   ├── cross_source_validator.py    # Check multi-source corroboration
│   │   ├── outlier_detector.py          # Flag anomalous data points
│   │   ├── consistency_checker.py       # Verify data integrity
│   │   └── source_credibility_scorer.py # Rate article sources (Tier 1-4)
│   │
│   ├── validation_logs/                  # Validation results
│   │   ├── data_quality_report_YYYYMMDD.json
│   │   └── flagged_articles.csv         # Articles requiring manual review
│   │
│   └── expert_review/                    # External validation materials
│       ├── expert_reviewer_guide.md     # Instructions for expert reviewers
│       ├── company_fact_check_template.md
│       └── review_responses/            # Company/expert feedback
│
├── 📂 08_supplementary_data/             # Additional data sources (job postings, patents, etc.)
│   ├── linkedin_job_analysis/
│   │   ├── job_posting_scraper.py       # LinkedIn job posting collector
│   │   ├── ai_job_postings.csv          # AI/ML job openings by company
│   │   └── job_title_taxonomy.json      # Standardized job titles
│   │
│   ├── public_activity_tracking/
│   │   ├── conference_speakers.csv      # AI conference participation
│   │   ├── academic_publications.csv    # Papers published by company employees
│   │   ├── github_activity.csv          # Open-source contributions
│   │   └── thought_leadership_score.py  # Calculate public AI activity index
│   │
│   ├── company_financials/
│   │   ├── earnings_call_transcripts/   # AI mentions in investor communications
│   │   ├── investor_presentations.csv
│   │   └── capex_allocations.csv        # AI investment tracking
│   │
│   └── regulatory_filings/
│       ├── ofcom_filings.csv            # UK regulatory submissions
│       └── foi_requests.csv             # Freedom of Information responses
│
├── 📂 09_documentation/                  # Project documentation and guides
│   ├── GETTING_STARTED.md               # Onboarding guide for new contributors
│   ├── API_DOCUMENTATION.md             # Analysis pipeline API reference
│   ├── CONTRIBUTING.md                  # Contribution guidelines
│   ├── CHANGELOG.md                     # Version history
│   └── FAQ.md                           # Frequently asked questions
│
└── 📂 archive/                           # Deprecated files, old analyses
    ├── old_structure/                    # Previous repo organization (pre-refactor)
    └── deprecated_scripts/               # Retired code (kept for reference)
```

---

## 🗂️ File Naming Conventions

### General Rules
- **Lowercase with underscores:** `file_name.ext` (not camelCase or PascalCase)
- **Dates:** `YYYYMMDD` format (e.g., `analysis_cache_20251214.json`)
- **Versions:** `v1`, `v2`, etc. (e.g., `telco_ai_index_2025_v1.csv`)
- **Descriptive names:** `company_use_case_matrix.csv` (not `matrix.csv`)

### Specific Patterns
- **Raw scraped data:** `{source}_articles_{YYYYMMDD}.csv`
  - Example: `fibrenews_articles_20251214.csv`
- **Analysis outputs:** `{analysis_type}_{scope}_{version}.csv`
  - Example: `sentiment_trends_uk_telcos_v2.csv`
- **Cache files:** `{pipeline_name}_cache.json`
  - Example: `big_firm_analysis_cache.json`
- **Reports:** `{report_type}_{date}.pdf`
  - Example: `executive_summary_202512.pdf`

---

## 📊 Key Datasets & Their Purposes

### 1. **unified_ai_analysis.csv** (Master Dataset)
**Location:** `03_processed_data/`
**Purpose:** Single source of truth for all analyzed articles
**Key Columns:**
- `article_id` (unique identifier)
- `source` (publication/website)
- `date` (publication date)
- `title`
- `url`
- `primary_use_case` (one of 6 categories)
- `primary_use_case_confidence` (0.0-1.0)
- `all_use_cases` (JSON array)
- `companies_mentioned` (JSON array)
- `sentiment` (positive/neutral/negative/mixed/not_applicable)
- `ai_mention_count`
- `word_count`
- `summary` (LLM-generated)
- `strategic_importance` (high/medium/low, for big firm articles)
- `maturity_stage` (pilot/limited_deployment/scaled_production)
- `key_technologies` (JSON array)
- `source_tier` (1-4, credibility rating)

### 2. **company_profiles.csv** (Company-Level Aggregations)
**Location:** `03_processed_data/`
**Purpose:** Company-level metrics for benchmarking
**Key Columns:**
- `company_name`
- `business_model` (retail_isp/wholesale_fiber/mobile_operator/b2b_infrastructure)
- `company_size` (large_incumbent/mid_market/scale_up)
- `headquarters_location`
- `total_ai_mentions`
- `unique_articles`
- `primary_use_cases` (JSON array with counts)
- `average_sentiment` (-1.0 to 1.0)
- `maturity_score` (calculated metric)
- `ai_job_postings_count` (from supplementary data)
- `thought_leadership_score` (conference talks + papers + GitHub)
- `hype_vs_reality_ratio` (public mentions / deployment evidence)

### 3. **use_case_statistics.csv** (Use Case Trends)
**Location:** `03_processed_data/`
**Purpose:** Track adoption and trends by use case
**Key Columns:**
- `use_case` (6 canonical categories)
- `total_mentions`
- `unique_companies`
- `average_maturity_stage`
- `average_sentiment`
- `earliest_mention_date`
- `growth_rate_yoy` (% change year-over-year)
- `median_roi_claimed` (from articles with quantified outcomes)

---

## 🔄 Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: DATA COLLECTION                                        │
│                                                                  │
│  Web Scrapers ──────────► raw_outputs/                          │
│  (fibernews, ispreview,    ├── fibrenews_articles_YYYYMMDD.csv  │
│   thinkbroadband)          ├── ispreview_articles_YYYYMMDD.csv  │
│                            └── thinkbroadband_articles_YYYYMMDD.csv│
│                                                                  │
│  Manual Curation ─────────► manual_inputs/                      │
│  (expanded scope,          ├── AI_Articles_By_Company.xlsx      │
│   company newsrooms)       └── increased_scope.csv              │
│                                                                  │
│  Supplementary Data ──────► 08_supplementary_data/              │
│  (LinkedIn, conferences,   ├── ai_job_postings.csv              │
│   GitHub, etc.)            └── thought_leadership_score.csv     │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: LLM ANALYSIS                                            │
│                                                                  │
│  llm_analysis_pipeline.py ────► Calls Ollama LLM                │
│  ├── use_case_classifier.py    ├── Taxonomy configs             │
│  ├── sentiment_analyzer.py     ├── Prompt templates             │
│  └── entity_extractor.py       └── Validation rules             │
│                                                                  │
│  Results cached in: caches/analysis_cache.json                  │
│                                                                  │
│  Outputs:                                                        │
│  ├── unified_ai_analysis.csv (master dataset)                   │
│  ├── big_firm_analysis.csv (deep-dive results)                  │
│  └── Analysis logs                                              │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: ADVANCED ANALYSIS                                       │
│                                                                  │
│  04_advanced_analysis/ scripts:                                 │
│  ├── time_series_analysis.py ──► sentiment_trends.csv           │
│  ├── company_benchmarking.py ──► company_profiles.csv           │
│  ├── use_case_opportunity_matrix.py ──► roi_adoption_matrix.csv │
│  └── ai_hype_vs_reality.py ──► hype_reality_scores.csv          │
│                                                                  │
│  Integration with supplementary data:                           │
│  └── Merge job postings, thought leadership, financials         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: VALIDATION                                              │
│                                                                  │
│  07_validation/ scripts:                                        │
│  ├── cross_source_validator.py ──► flagged_articles.csv         │
│  ├── source_credibility_scorer.py ──► source_tier assigned      │
│  └── outlier_detector.py ──► data_quality_report.json           │
│                                                                  │
│  Expert review process:                                          │
│  └── Send findings to companies/experts for fact-check          │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: PUBLICATION OUTPUTS                                     │
│                                                                  │
│  05_visualizations/                                              │
│  ├── dashboard.py ──────────► Interactive Streamlit dashboard   │
│  └── publication_charts/ ───► Static charts (PNG, SVG)          │
│                                                                  │
│  06_outputs/                                                     │
│  ├── reports/ ──────────────► PDF reports, exec summaries       │
│  ├── data_releases/ ────────► Public datasets (CSV, codebook)   │
│  └── media_kits/ ───────────► Press releases, infographics      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Reference: Common Tasks

### Task: Add New Scraped Articles
1. Run scraper: `python 01_data_collection/scrapers/fibernews_scraper.py`
2. Output saved to: `01_data_collection/raw_outputs/fibrenews_articles_YYYYMMDD.csv`
3. Run analysis pipeline: `python 02_analysis/pipelines/llm_analysis_pipeline.py --input raw_outputs/fibrenews_articles_YYYYMMDD.csv`
4. Results appended to: `03_processed_data/unified_ai_analysis.csv`

### Task: Regenerate Dashboard
1. Ensure latest data in: `03_processed_data/unified_ai_analysis.csv`
2. Run: `streamlit run 05_visualizations/dashboard.py`
3. Dashboard opens in browser at `http://localhost:8501`

### Task: Export Publication-Ready Report
1. Run analysis scripts in `04_advanced_analysis/` to update all processed datasets
2. Generate charts: `python 04_advanced_analysis/notebooks/publication_charts.ipynb`
3. Compile report: `python 06_outputs/reports/generate_full_report.py`
4. Output: `06_outputs/reports/full_report.pdf`

### Task: Validate Data Quality
1. Run: `python 07_validation/validation_scripts/consistency_checker.py`
2. Review: `07_validation/validation_logs/data_quality_report_YYYYMMDD.json`
3. Address flagged articles in: `07_validation/validation_logs/flagged_articles.csv`

---

## 🔐 Data Governance & Privacy

### Sensitive Data
- **Company-Identifying Information:** OK to include (public companies, public statements)
- **Individual Names:** Include only if public figures (executives quoted in press) or in author bylines
- **Financial Data:** Use only publicly disclosed data (earnings calls, investor presentations)
- **Internal Documents:** Do NOT include leaked or confidential materials

### Data Retention
- **Raw scraped data:** Keep all versions in `01_data_collection/raw_outputs/`
- **Analysis caches:** Keep latest + monthly snapshots (purge >6 months old unless needed for longitudinal analysis)
- **Deprecated code:** Move to `archive/deprecated_scripts/` after 3 months of non-use

### Public Data Releases
- **Anonymization:** Not required (all data is from public sources about public companies)
- **Aggregation:** For commercial report, provide aggregated insights, not raw article-level data
- **Licensing:** Creative Commons BY-NC-SA 4.0 for public dataset releases

---

## 🛠️ Development Guidelines

### Code Style
- **Python:** PEP 8 compliant, use `black` formatter
- **Naming:** Descriptive variable names (`use_case_counts`, not `uc`)
- **Comments:** Docstrings for all functions, inline comments for complex logic
- **Type Hints:** Use where beneficial for clarity

### Git Workflow
- **Main branch:** `main` (stable, publication-ready)
- **Development branch:** `dev` (active development)
- **Feature branches:** `feature/descriptive-name` (e.g., `feature/linkedin-job-scraper`)
- **Commit messages:** Descriptive (e.g., "Add sentiment trend visualization to dashboard")

### Testing
- **Unit tests:** For critical analysis functions (use `pytest`)
- **Integration tests:** For full pipeline runs
- **Validation tests:** Automated data quality checks (run before each publication cycle)

---

## 📋 Maintenance Schedule

### Daily
- [ ] Run scrapers for new articles (automated cron job)
- [ ] Check scraper logs for errors

### Weekly
- [ ] Run LLM analysis pipeline on new articles
- [ ] Update unified dataset
- [ ] Review validation logs for flagged articles

### Monthly
- [ ] Regenerate all advanced analysis outputs
- [ ] Update dashboard with latest data
- [ ] Snapshot caches (backup)
- [ ] Review and update company taxonomy (new companies, mergers, etc.)

### Quarterly
- [ ] Run full data validation suite
- [ ] Update methodology documentation
- [ ] Refresh publication charts
- [ ] Export quarterly trend report

### Annually
- [ ] Comprehensive data audit
- [ ] Archive old raw data (move to long-term storage)
- [ ] Update technology taxonomy (new AI frameworks, etc.)

---

## 🆘 Troubleshooting

### Common Issues

**Issue:** LLM analysis cache is stale
**Solution:** Delete `02_analysis/caches/analysis_cache.json` and re-run pipeline (CAUTION: costly in LLM tokens)

**Issue:** Dashboard won't load
**Solution:** Check that `03_processed_data/unified_ai_analysis.csv` exists and is not corrupted

**Issue:** Scraper fails with 403 error
**Solution:** Website may have rate-limiting. Add delays in scraper config or rotate user agents

**Issue:** Use case classification inconsistencies
**Solution:** Review `02_analysis/configs/use_case_taxonomy.json` and update LLM prompts in `llm_prompts.json`

---

## 📞 Contact & Contribution

**Project Maintainer:** [Your Name]
**Email:** [Your Email]
**GitHub:** [Repository URL]

**Contributing:**
- See `09_documentation/CONTRIBUTING.md` for detailed guidelines
- Open issues for bugs or feature requests
- Submit pull requests against `dev` branch

---

**Document Version:** 1.0
**Last Updated:** December 14, 2025
**Next Review:** Monthly during active development
