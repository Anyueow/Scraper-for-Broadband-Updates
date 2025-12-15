# Manual Data Inputs
## Curated Articles and Expanded Scope

**Purpose:** This directory contains manually curated articles that supplement automated web scraping. These sources typically include:
- Company newsrooms and press releases
- Paywalled publications
- Industry reports and whitepapers
- Articles from sources not covered by automated scrapers
- Expanded geographic and company scope beyond UK retail ISPs

---

## 📁 Files in This Directory

### 1. increased_scope.csv
**Description:** Expanded dataset covering broader telecommunications infrastructure companies
**Date Added:** December 2025
**Scope Expansion:**
- **Geographic:** UK → Europe → North America
- **Company Types:**
  - B2B infrastructure (Colt, Zayo, euNetworks)
  - Wholesale fiber (Neos Networks, CityFibre, Openreach)
  - Mobile infrastructure (Cornerstone, Wireless Infrastructure Group, Boldyn Networks)
  - Specialized providers (Freshwave)

**Column Structure:** Same as automated scraper outputs
- `source` - Publication name
- `date` - Publication date (YYYY-MM-DD)
- `title` - Article headline
- `url` - Permanent link
- Additional columns: varies (see data dictionary)

**Data Quality:**
- ✅ Manually verified URLs
- ✅ Curated for AI relevance
- ⚠️ Date precision may vary (some articles only have month/year)

**Source Tiers Represented:**
- Tier 1: Academic journals, independent journalism
- Tier 2: Industry trade press
- Tier 3: Vendor case studies (Microsoft, ServiceNow, NICE, etc.)
- Tier 4: Company newsrooms and press releases

**Update Frequency:** Ad-hoc (as new relevant articles are discovered)

---

### 2. AI_Articles_By_Company.xlsx
**Description:** Company-specific deep-dive articles for major telecommunications firms
**Date Added:** November 2025
**Companies Covered:**
- BT Group
- Virgin Media O2
- Vodafone
- Sky
- TalkTalk
- OpenReach
- CityFibre
- Others (expanding)

**Sheet Structure:**
- Sheet 1: Article metadata (title, URL, date, company)
- Sheet 2: Analysis notes (optional manual annotations)

**Purpose:** Enables `big_firm_analyzer.py` to perform deeper strategic analysis on major incumbents

**Update Frequency:** Monthly (quarterly for comprehensive updates)

---

## ⚙️ How These Files Are Used

### Processing Pipeline
1. **Manual Review & Curation**
   - Articles identified through industry monitoring, Google Alerts, social media, expert recommendations
   - Relevance assessment: Does article discuss AI in telecommunications context?
   - URL validation and metadata extraction

2. **LLM Analysis**
   - `llm_analysis_pipeline.py` treats manual inputs identically to scraped data
   - `big_firm_analyzer.py` applies deeper analysis for company-specific articles

3. **Integration into Master Dataset**
   - Results merged into `03_processed_data/unified_ai_analysis.csv`
   - Source tracking maintained to distinguish manual vs. automated

4. **Validation & Quality Control**
   - Cross-source validation for claims
   - Source tier assignment (credibility rating)
   - Flagging of potential vendor bias

---

## 📊 Current Coverage Statistics

### increased_scope.csv
- **Total Articles:** ~50-60
- **Date Range:** 2024-2025
- **Companies:** 15+ (Colt, Neos, Zayo, euNetworks, Freshwave, Boldyn, CityFibre, Gigaclear, Openreach, Cornerstone, WIG, and more)
- **Use Cases:** All 6 primary use cases represented
- **Geographic Spread:** UK (60%), Europe (25%), North America (15%)

### AI_Articles_By_Company.xlsx
- **Total Articles:** ~30-40
- **Companies:** 8 major UK telcos
- **Depth:** Multiple articles per company for longitudinal analysis

---

## 🔍 Identifying Articles for Manual Curation

### Inclusion Criteria
✅ **Include if:**
- Discusses AI/ML deployment, pilot, or strategy in telecommunications
- Features telecommunications company executives discussing AI
- Reports on AI partnership announcements (vendor + telco)
- Provides quantified AI outcomes (ROI, cost savings, performance improvements)
- Covers AI-related workforce changes (hiring, job cuts, training)
- Analyzes regulatory or policy implications of AI in telco sector

❌ **Exclude if:**
- Generic AI news with no telco connection
- Tangential mentions (e.g., "company uses Microsoft Office with AI features")
- Purely aspirational statements without implementation details
- Consumer device AI (e.g., smartphone features) unless network-related

### Source Priority
**High Priority:**
1. Company official newsrooms (Tier 4, but authoritative)
2. Industry trade press interviews (Tier 2)
3. Vendor case studies with quantified outcomes (Tier 3)
4. Academic/policy papers (Tier 1)

**Medium Priority:**
5. General business press covering telco AI (Tier 2)
6. Conference proceedings and presentation decks

**Low Priority:**
7. Social media posts (require corroboration)
8. Unverified blog posts

---

## ✏️ How to Add New Articles

### Step 1: Prepare Article Metadata
Create a CSV row with the following minimum fields:
```csv
source,date,title,url
"Company Newsroom",2025-12-14,"Company X Deploys AI for Network Optimization","https://example.com/article"
```

### Step 2: Add to increased_scope.csv
- Open `increased_scope.csv` in spreadsheet editor
- Append new row(s)
- **Validation:** Ensure URL is accessible and date format is YYYY-MM-DD
- Save and commit to repository

### Step 3: Run Analysis Pipeline
```bash
cd /path/to/project
python 02_analysis/pipelines/llm_analysis_pipeline.py --input 01_data_collection/manual_inputs/increased_scope.csv
```

### Step 4: Verify Output
- Check `03_processed_data/unified_ai_analysis.csv` for new entries
- Review `02_analysis/caches/analysis_cache.json` to confirm caching
- Run validation: `python 07_validation/validation_scripts/consistency_checker.py`

---

## 📝 Data Provenance

**Who curates these files?**
- Project maintainer
- Research assistants
- Community contributions (reviewed before inclusion)

**How are sources discovered?**
- Google Alerts for "telecommunications + AI" and company names
- RSS feeds from industry publications
- LinkedIn posts from telco executives
- Conference proceedings (e.g., Mobile World Congress, Fiber Connect)
- Academic databases (IEEE Xplore, ACM Digital Library)
- Direct company newsletter subscriptions

**Quality control:**
- Duplicate detection (URL matching)
- Broken link checking (quarterly)
- Source tier validation (annual review)

---

## 🚨 Known Issues & Limitations

1. **Selection Bias**
   - Manual curation may favor more prominent companies or positive news
   - Mitigation: Actively seek critical/analytical sources, not just PR

2. **Date Precision**
   - Some vendor case studies lack precise publication dates
   - Solution: Use approximate dates, flag in `data_quality_flags` field

3. **Paywall Access**
   - Some valuable sources (Financial Times, WSJ) are behind paywalls
   - Current approach: Use freely accessible summaries/excerpts where possible

4. **Language Barrier**
   - Non-English articles underrepresented
   - Future: Add translation step for European sources

---

## 📂 File Versioning

To maintain historical record, use timestamped versions:
- `increased_scope_20251214.csv` (snapshot before major update)
- Keep most recent version as `increased_scope.csv` (canonical)

**Backup Schedule:**
- Create snapshot before bulk updates (100+ articles added)
- Monthly snapshots stored in `archive/manual_inputs_history/`

---

## 📞 Questions or Suggestions?

- To suggest new articles for inclusion: Open GitHub issue with "Data Curation" label
- To report broken links or errors: Use `07_validation/validation_logs/flagged_articles.csv`
- General questions: See `09_documentation/FAQ.md`

---

**Last Updated:** December 14, 2025
**Next Review:** Monthly during active research phase
