# Data Dictionary
## Telco AI Analysis Project - Processed Datasets

**Purpose:** Comprehensive reference for all columns in processed datasets
**Last Updated:** December 14, 2025

---

## 📊 Primary Datasets

### 1. unified_ai_analysis.csv
**Description:** Master dataset containing all analyzed articles with LLM-extracted insights
**Row Count:** ~500-1000 articles (growing)
**Update Frequency:** Weekly
**Primary Key:** `article_id` (composite: source + URL hash)

| Column Name | Data Type | Description | Example Values | Nullability |
|------------|-----------|-------------|----------------|-------------|
| `source` | String | Publication or website name | "Technology Magazine", "ISPreview", "Colt Technology Services" | NOT NULL |
| `date` | Date (YYYY-MM-DD) | Article publication date | "2025-11-26", "2025-03-10" | NOT NULL |
| `title` | String | Article headline | "Colt CIO Priorities: AI Inference, NaaS and Quantum Security" | NOT NULL |
| `url` | String (URL) | Permanent link to article | "https://technologymagazine.com/articles/..." | NOT NULL (UNIQUE) |
| `primary_use_case` | String (Enum) | Main AI application category | "network_planning_deployment", "customer_support_experience" | NULL if AI not mentioned |
| `primary_use_case_confidence` | Float (0.0-1.0) | LLM confidence in classification | 0.85, 0.92, 0.65 | NULL if no use case |
| `ai_use_cases` | JSON Array | All use cases mentioned | `["network_planning_deployment", "security_fraud_threat"]` | NULL if no AI |
| `sentiment` | String (Enum) | Sentiment toward AI | "positive", "neutral", "negative", "mixed", "not_applicable" | NOT NULL |
| `ai_mention_count` | Integer | Total AI keywords in article | 4, 12, 0 | NOT NULL (0 if none) |
| `ai_mentions` | String (Comma-separated) | Specific AI terms found | "AI; artificial intelligence; AI inference; AI workloads" | NULL if 0 |
| `title_ai_mention_count` | Integer | AI keywords in title | 0, 1, 2 | NOT NULL |
| `title_ai_mentions` | String | AI terms in title | "AI" | NULL if 0 |
| `word_count` | Integer | Estimated article length | 1500, 900, 4000 | NOT NULL |
| `summary` | Text | LLM-generated summary (200-300 words) | "Interview-style feature on Colt's CIO outlining..." | NOT NULL |
| `AI` | String (Yes/No) | Binary AI relevance flag | "Yes", "No" | NOT NULL |
| `companies_mentioned` | JSON Array | Company names extracted | `["BT", "Vodafone", "CityFibre"]` | NULL if none |
| `strategic_importance` | String (Enum) | Business significance | "high", "medium", "low" | NULL (only for big firm articles) |
| `maturity_stage` | String (Enum) | Deployment phase | "pilot", "limited_deployment", "scaled_production" | NULL if unclear |
| `key_technologies` | JSON Array | Specific AI/ML technologies | `["Azure OpenAI", "LangChain", "LSTM models"]` | NULL if not mentioned |
| `business_impact` | Text | Quantified outcomes or strategic implications | "40-60% opex reduction in targeted areas" | NULL if not provided |
| `source_tier` | Integer (1-4) | Credibility rating (1=highest) | 1, 2, 3, 4 | NOT NULL (default: 3) |
| `data_quality_flags` | JSON Array | Validation warnings | `["single_source_only", "vendor_bias"]` | NULL if clean |

#### Use Case Enum Values (primary_use_case)
1. `network_planning_deployment` - Network Planning & Deployment
2. `network_optimization_performance` - Network Optimization & Performance Management
3. `predictive_maintenance_analytics` - Predictive Maintenance & Network Analytics
4. `customer_support_experience` - Customer Support & Experience Automation
5. `security_fraud_threat` - Security, Fraud & Threat Intelligence
6. `internal_productivity_workforce` - Internal Productivity & Workforce Enablement
7. `other` - Fallback category (AI mentioned but doesn't fit above)

#### Sentiment Enum Values
- `positive` - AI presented as beneficial, solving problems, strategic advantage
- `neutral` - Factual discussion without strong opinion
- `negative` - Concerns, criticism, job losses, risks
- `mixed` - Both positive and negative aspects
- `not_applicable` - Article doesn't discuss AI meaningfully

#### Maturity Stage Enum Values
- `pilot` - Experimental phase, small-scale testing
- `limited_deployment` - Deployed in specific areas/regions
- `scaled_production` - Organization-wide, mission-critical usage

#### Source Tier Values
- `1` - Independent journalism, peer-reviewed research (highest credibility)
- `2` - Industry trade press, professional analysis
- `3` - Vendor case studies, sponsored content (potential bias)
- `4` - Company PR, press releases (marketing material)

---

### 2. company_profiles.csv
**Description:** Company-level aggregated metrics for benchmarking
**Row Count:** ~30-50 companies
**Update Frequency:** Monthly
**Primary Key:** `company_name`

| Column Name | Data Type | Description | Example Values |
|------------|-----------|-------------|----------------|
| `company_name` | String | Standardized company name | "BT", "Vodafone", "Colt Technology Services" |
| `business_model` | String (Enum) | Primary business type | "retail_isp", "wholesale_fiber", "mobile_operator", "b2b_infrastructure" |
| `company_size` | String (Enum) | Market position | "large_incumbent", "mid_market", "scale_up" |
| `headquarters_location` | String | Primary HQ location | "London, UK", "Reading, UK", "Slough, UK" |
| `total_ai_mentions` | Integer | Sum of ai_mention_count across all articles | 45, 123, 8 |
| `unique_articles` | Integer | Number of articles mentioning this company | 12, 35, 3 |
| `articles_per_use_case` | JSON Object | Count by use case | `{"customer_support_experience": 8, "network_optimization_performance": 4}` |
| `average_sentiment` | Float (-1.0 to 1.0) | Sentiment score (pos=1, neg=-1) | 0.65, -0.2, 0.0 |
| `dominant_use_case` | String | Most frequent use case | "customer_support_experience" |
| `maturity_score` | Float (0.0-10.0) | Calculated maturity metric | 7.2, 4.5, 2.1 |
| `first_ai_mention_date` | Date | Earliest article date | "2023-06-15" |
| `latest_ai_mention_date` | Date | Most recent article | "2025-11-26" |
| `ai_job_postings_count` | Integer | LinkedIn AI job openings (if available) | 15, 0, NULL |
| `thought_leadership_score` | Float (0.0-100.0) | Conference talks + papers + GitHub | 45.5, 12.0, NULL |
| `hype_vs_reality_ratio` | Float | Public mentions / deployment evidence | 1.2, 0.8, 3.5 |

#### Business Model Enum
- `retail_isp` - Direct-to-consumer internet service providers
- `wholesale_fiber` - Wholesale network infrastructure providers
- `mobile_operator` - Mobile/wireless network operators
- `b2b_infrastructure` - Enterprise/carrier-grade infrastructure specialists

#### Company Size Enum
- `large_incumbent` - Established national carriers (BT, Vodafone)
- `mid_market` - Regional/specialized operators (Neos, CityFibre)
- `scale_up` - Fast-growing challengers (Community Fibre, Gigaclear)

---

### 3. use_case_statistics.csv
**Description:** Trends and statistics by AI use case
**Row Count:** 7 rows (6 use cases + "other")
**Update Frequency:** Monthly
**Primary Key:** `use_case`

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `use_case` | String | Use case category code |
| `use_case_display_name` | String | Human-readable name |
| `total_mentions` | Integer | Total articles mentioning this use case |
| `unique_companies` | Integer | Number of companies active in this use case |
| `earliest_mention_date` | Date | First observed in dataset |
| `latest_mention_date` | Date | Most recent mention |
| `average_sentiment` | Float (-1.0 to 1.0) | Mean sentiment for this use case |
| `pilot_count` | Integer | Articles describing pilots |
| `limited_deployment_count` | Integer | Articles describing limited deployment |
| `scaled_production_count` | Integer | Articles describing scaled production |
| `average_maturity_stage` | Float (1.0-3.0) | Numerical maturity (1=pilot, 3=scaled) |
| `growth_rate_yoy` | Float (%) | Year-over-year mention growth |
| `median_roi_claimed` | Float (%) | Median ROI from articles with quantified outcomes |
| `roi_sample_size` | Integer | Number of articles with ROI data |

---

### 4. company_size_activity_scores.csv
**Description:** Company activity scores segmented by company size
**Row Count:** Variable (company × metric combinations)
**Update Frequency:** Monthly

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `company` | String | Company name |
| `size_category` | String | Company size classification |
| `total_mentions` | Integer | Total AI mentions |
| `article_count` | Integer | Number of articles |
| `activity_score` | Float | Composite activity metric |
| `normalized_score` | Float (0.0-100.0) | Score normalized to 0-100 scale |

---

## 🔧 Calculated Fields & Metrics

### Maturity Score Calculation
**Formula:**
```
maturity_score = (
    (pilot_count * 1.0) +
    (limited_deployment_count * 2.0) +
    (scaled_production_count * 3.0)
) / total_articles * 10
```
**Interpretation:** 0-3 = Early stage, 4-6 = Growing, 7-10 = Mature

### Sentiment Numeric Conversion
```
positive → 1.0
mixed → 0.5
neutral → 0.0
negative → -1.0
not_applicable → NULL (excluded from averages)
```

### Hype vs. Reality Ratio
**Formula:**
```
hype_vs_reality_ratio = total_ai_mentions / deployment_evidence_count

Where deployment_evidence_count = articles with:
- maturity_stage IN ('limited_deployment', 'scaled_production')
- OR quantified business_impact provided
```
**Interpretation:**
- Ratio > 2.0 = High talk, low action ("AI posturing")
- Ratio 0.8-2.0 = Balanced
- Ratio < 0.8 = Silent achiever

### Thought Leadership Score
**Formula:**
```
thought_leadership_score = (
    conference_talks * 5.0 +
    academic_papers * 10.0 +
    github_contributions * 2.0 +
    blog_posts * 1.0
)
```
*(Data from supplementary sources in `08_supplementary_data/`)*

---

## 🗺️ Data Lineage

### unified_ai_analysis.csv
**Source Datasets:**
1. `01_data_collection/raw_outputs/fibrenews_articles_*.csv` (scraped)
2. `01_data_collection/raw_outputs/ispreview_articles_*.csv` (scraped)
3. `01_data_collection/raw_outputs/thinkbroadband_articles_*.csv` (scraped)
4. `01_data_collection/manual_inputs/increased_scope.csv` (manual curation)
5. `01_data_collection/manual_inputs/AI_Articles_By_Company.xlsx` (manual curation)

**Processing Pipeline:**
1. `02_analysis/pipelines/llm_analysis_pipeline.py` (LLM extraction)
2. `02_analysis/pipelines/big_firm_analyzer.py` (deep-dive analysis)
3. Validation via `07_validation/validation_scripts/`

### company_profiles.csv
**Source:** Aggregation of `unified_ai_analysis.csv` + supplementary data
**Processing:** `04_advanced_analysis/company_benchmarking.py`

### use_case_statistics.csv
**Source:** Aggregation of `unified_ai_analysis.csv`
**Processing:** `04_advanced_analysis/time_series_analysis.py`

---

## 📝 Data Quality Notes

### Known Issues
1. **Date Precision:** Some articles have only month/year (imputed to 1st of month)
2. **Vendor Bias:** ~30% of articles are vendor case studies (source_tier=3), may overstate success
3. **Geographic Imbalance:** UK-heavy (75%), European/NA coverage growing
4. **ROI Data Sparse:** Only 15-20% of articles include quantified outcomes

### Validation Rules
- `url` must be valid HTTP(S) URL and unique
- `date` must be between 2020-01-01 and current date
- `sentiment` cannot be NULL
- `primary_use_case` must be one of 7 valid enum values OR NULL
- `ai_mention_count` ≥ 0
- `word_count` > 100 (minimum to be considered an article)

### Missing Data Handling
- Missing `companies_mentioned`: [] (empty array)
- Missing `ai_use_cases`: [] if sentiment != "not_applicable", else NULL
- Missing `summary`: Re-run LLM analysis
- Missing `business_impact`: NULL (acceptable, most articles don't quantify)

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-14 | Initial data dictionary with core datasets |

---

## 📞 Questions?

See `09_documentation/FAQ.md` or contact project maintainer.
