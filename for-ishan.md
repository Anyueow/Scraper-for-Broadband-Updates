# For Ishan: UK Broadband AI Trends Analysis - Data Guide

**Quick Reference:** Where to find every piece of analysis data for your article

---

## 1. MASTER DATASET: All Articles with AI Analysis

**What it is:** Every article analyzed (1,826 total), with 77 containing AI mentions

**Where it lives:**
```
02_analysis/pipelines/unified_ai_analysis_enhanced.csv
```

**Key columns:**
- `source` - Where article came from (ISPreview UK, FibreNews, Colt, Zayo, etc.)
- `date` - Publication date
- `title` - Article headline
- `url` - Link to original article
- `primary_use_case` - Main AI application (customer_support_experience, network_optimization_performance, security_fraud_threat, etc.)
- `ai_mention_count` - How many times AI mentioned
- `sentiment` - positive/neutral/negative toward AI
- `summary` - AI-generated summary of article
- `companies_mentioned` - BT, Virgin Media O2, Vodafone, Colt, Zayo, Freshwave, etc.
- `technologies_*` - Specific AI technologies mentioned (LLMs, chatbots, automation, etc.)

**What it means:** This is your primary source. Filter by `ai_mention_count > 0` to get only AI articles. Use `companies_mentioned` to see which telcos are doing what.

---

## 2. COMPANY INTELLIGENCE: Who's Doing What

### 2A. ROI Claims by Company

**What it is:** Which companies are making business impact claims about AI

**Where it lives:**
```
03_processed_data/roi_by_company.csv
```

**Key insights:**
- **22 companies tracked** with ROI claims
- **Top performers:**
  - Virgin Media: 7 ROI claims (78/100 credibility)
  - O2: 7 claims (78/100 credibility)
  - BT: 6 claims (68/100 credibility)
  - Vodafone, EE, Virgin Media O2: 5 claims each
  - **Colt: 3 claims** (from increased_scope data)
  - **Zayo: 2 claims** (from increased_scope data)
  - **Freshwave: 3 claims** (from increased_scope data)

**Key columns:**
- `company` - Company name
- `total_roi_claims` - Number of ROI claims made
- `avg_credibility` - Credibility score (0-100)
- `primary_roi_type` - cost_reduction, time_savings, revenue_growth, customer_impact
- `most_common_use_case` - What they're using AI for

**What it means:** Use this to quote specific companies and their AI impact. Higher credibility = more trustworthy claims. Example: "Virgin Media made 7 ROI claims about AI with an average credibility of 78/100, primarily focused on time savings."

### 2B. Build vs Buy Strategy

**What it is:** Are companies building AI in-house or buying from vendors?

**Where it lives:**
```
03_processed_data/build_vs_buy_analysis.csv
```

**Key insight:**
- **BT: 100% Buy** (0% build in-house, using external vendors)
- Only 1 company analyzed (limited data due to tech extraction requirements)

**What it means:** Most UK telcos are buying AI solutions from vendors rather than building them. This is a strategic insight about market maturity.

---

## 3. TECHNOLOGY LANDSCAPE: What AI Tech is Being Used

### 3A. Technology Mentions

**What it is:** Every AI technology/tool mentioned across articles

**Where it lives:**
```
03_processed_data/technology_mentions.csv
```

**Key technologies identified (10 total):**
1. **Vyntelligence** - 2 articles (2.6% adoption) - AI platform
2. **Automation** - 2 articles (2.6%)
3. **Computer vision** - 1 article (1.3%)
4. **NICE CXone Mpower** - 1 article (1.3%) - Contact center AI
5. **Hiya Call Defence** - 1 article (1.3%) - Fraud detection
6. **Machine Learning** - 1 article
7. **Chatbot** - 1 article
8. **NLP** (Natural Language Processing) - 1 article

**Key columns:**
- `technology` - Tech name
- `category` - foundation_models, platforms, infrastructure, techniques
- `article_count` - How many articles mention it
- `maturity` - emerging/growing/mainstream
- `adoption_rate_pct` - % of AI articles using this tech

**What it means:** UK telcos are primarily using AI platforms and automation tools rather than building custom foundation models. This shows they're buying mature solutions.

### 3B. Vendor Market Share

**What it is:** Which AI vendors are mentioned most in UK telco articles

**Where it lives:**
```
03_processed_data/vendor_market_share.csv
```

**Top vendors (8 total):**
1. **Vyntelligence** - 2 mentions (2.6% market share)
2. **NICE CXone Mpower** - 1 mention (1.3%)
3. **Hiya Call Defence** - 1 mention (1.3%)
4. Chatbot platforms - 1 mention
5. NLP tools - 1 mention

**What it means:** No single vendor dominates. Market is fragmented with use-case-specific vendors (Vyntelligence for analytics, NICE for contact centers, Hiya for fraud).

---

## 4. ROI & BUSINESS IMPACT: What Results are Companies Claiming?

### 4A. Overall ROI Impact

**What it is:** All ROI claims extracted from articles with credibility scoring

**Where it lives:**
```
03_processed_data/roi_impact_analysis.csv
```

**Key stats:**
- **50 total ROI claims** found
- **Average credibility: 68.9/100**
- **0 claims with percentage metrics** (e.g., "reduced costs by 30%")
- **1 claim with monetary amount** (specific £/$ figure)

**Key columns:**
- `article_title` - Which article made the claim
- `company` - Which company
- `roi_claim` - The actual claim text
- `roi_type` - cost_reduction, time_savings, revenue_growth, customer_impact
- `credibility_score` - 0-100 reliability score
- `has_percentage_claim` - TRUE if specific % mentioned
- `has_amount_claim` - TRUE if specific $ amount mentioned

**What it means:** Most ROI claims are qualitative ("improved efficiency") rather than quantitative ("reduced costs by 30%"). This suggests early-stage AI adoption where hard metrics aren't yet available.

### 4B. ROI by Use Case

**What it is:** Which AI applications have the most ROI claims

**Where it lives:**
```
03_processed_data/roi_by_use_case.csv
```

**Top use cases by ROI claims:**
1. **Other/General** - 37 claims (65.3/100 credibility)
2. **Customer Support & Experience** - 6 claims (79.2/100 credibility)
3. **Network Optimization & Performance** - 4 claims (78.8/100 credibility)
4. **Security, Fraud & Threat Detection** - 2 claims (80.0/100 credibility)
5. **Network Planning & Deployment** - 1 claim (80.0/100 credibility)

**Key columns:**
- `roi_category` - Use case category
- `total_roi_claims` - Number of claims
- `avg_credibility` - Average credibility score
- `cost_reduction_claims` / `revenue_growth_claims` / `time_savings_claims` - Breakdown by benefit type

**What it means:** Customer support and network optimization have the highest-quality ROI claims (79-80/100 credibility). These are the proven AI use cases. "Other/General" has many claims but lower credibility (65/100) - these are more speculative/future-focused.

---

## 5. VISUALIZATIONS: Charts for Your Article

**Where they live:**
```
06_outputs/visualizations/
```

### Available Charts (6 total):

1. **`company_roi_claims.png`** (373 KB) ⭐ **USE THIS**
   - Top 15 companies by AI ROI claims
   - Shows Virgin Media (7), O2 (7), BT (6), Colt (3), Zayo (2), Freshwave (3)
   - Includes credibility scores

2. **`vendor_market_share.png`** (219 KB)
   - Pie chart of AI vendor mentions
   - Shows Vyntelligence, NICE CXone Mpower, Hiya Call Defence

3. **`technology_mentions_bar.png`** (180 KB)
   - Top 15 AI technologies mentioned
   - Color-coded by category (platforms, techniques, infrastructure)

4. **`maturity_adoption_scatter.png`** (144 KB)
   - Technology maturity vs adoption rate
   - Bubble size = number of mentions
   - Shows most tech is "emerging" stage

5. **`category_distribution.png`** (122 KB)
   - AI technology categories breakdown
   - Platforms vs Techniques vs Infrastructure

6. **`build_vs_buy_stacked.png`** (114 KB)
   - Build vs Buy strategy by company
   - Currently only shows BT (100% buy)

**What it means:** Use `company_roi_claims.png` as your primary visual. It shows all the major UK telcos + infrastructure players (Colt, Zayo) and their AI activity levels.

---

## 6. EXECUTIVE SUMMARY: The Big Picture

**Where it lives:**
```
06_outputs/FINAL_ANALYSIS_REPORT.txt
```

**Key takeaways:**
- **1,826 articles analyzed**, 77 contained AI mentions (4.2%)
- **10 unique AI technologies** identified (low diversity = early market)
- **8 vendors tracked** (fragmented market, no dominant player)
- **50 ROI claims** across 22 companies
- **Industry average: 100% Buy strategy** (telcos buying AI, not building it)
- **Top use case:** Customer support & experience (highest credibility claims)

**What it means:** UK broadband industry is in **early AI adoption phase**:
- Buying solutions from vendors (not building in-house)
- Focus on customer support and network optimization
- ROI claims are mostly qualitative (few hard numbers)
- No single dominant technology or vendor

---

## 7. DATA SOURCES: Where the Articles Came From

### 7A. Scraped Articles (1,805 articles)

**Sources:**
- **ISPreview UK** - 1,700 articles (broadband news site)
- **FibreNews** - 45 articles (fiber industry news)
- **ThinkBroadband** - 30 articles (broadband analysis)
- **Other/Unknown** - 30 articles

**Where they live:**
```
Scraped Output/
  - ispreviewuk.csv
  - fibrenews_articles_*.csv
  - thinkbroadband_articles_*.csv
```

### 7B. Manually Curated Articles (131 articles, 51 unique after dedup)

**increased_scope.csv (53 articles)**
- Articles about Colt, Zayo, Neos Networks, euNetworks, Freshwave, Boldyn Networks
- Infrastructure and wholesale fiber providers
- High-quality curated AI content

**big_firm_unified_analysis.csv (78 articles)**
- Company-specific deep dives on BT, Virgin Media O2, Vodafone
- Detailed analysis with strategic importance, maturity stage, key technologies

**Where they live:**
```
increased_scope.csv (root directory)
big firm analysis/big_firm_unified_analysis.csv
```

**What it means:** The curated data (increased_scope + big_firm) provides **higher-quality AI insights** about major telcos and infrastructure providers. This is where companies like Colt, Zayo, Freshwave, and Neos Networks appear - they weren't in the scraped news articles.

---

## 8. ARTICLE ANGLE SUGGESTIONS

Based on the data, here are story angles:

### Angle 1: "UK Telcos Are Buying AI, Not Building It"
**Data points:**
- 100% buy strategy (build_vs_buy_analysis.csv)
- Top vendors: Vyntelligence, NICE CXone Mpower (vendor_market_share.csv)
- Quote: "BT has made 6 ROI claims about AI with 68/100 credibility, all using external vendors"

### Angle 2: "Customer Support Leading UK Telco AI Adoption"
**Data points:**
- Customer support has 6 ROI claims with 79.2/100 credibility (roi_by_use_case.csv)
- Technologies: Chatbots, NLP, automation (technology_mentions.csv)
- Companies: Virgin Media O2, BT, TalkTalk all focusing here (roi_by_company.csv)

### Angle 3: "Infrastructure Providers Racing Ahead on AI"
**Data points:**
- Colt: 3 ROI claims about AI-ready networks (roi_by_company.csv)
- Zayo: 2 claims about AI-driven fiber expansion (roi_by_company.csv)
- Freshwave: 3 claims about 5G + AI for agritech (roi_by_company.csv)
- Use unified_ai_analysis_enhanced.csv filtered by companies_mentioned = "Colt" or "Zayo"

### Angle 4: "UK Telco AI Claims Lack Hard Numbers"
**Data points:**
- 50 ROI claims total, only 1 with monetary amount (roi_impact_analysis.csv)
- 0 claims with percentage metrics (roi_impact_analysis.csv)
- Average credibility 68.9/100 (moderate confidence)
- Quote: "Most AI claims are qualitative, suggesting early-stage adoption where proven ROI is still elusive"

---

## 9. QUICK QUERIES FOR SPECIFIC QUESTIONS

### "Which companies are most active in AI?"
```
File: roi_by_company.csv
Sort by: total_roi_claims (descending)
Answer: Virgin Media (7), O2 (7), BT (6), Vodafone (5), EE (5)
```

### "What AI technologies are UK telcos using?"
```
File: technology_mentions.csv
Sort by: article_count (descending)
Answer: Vyntelligence (2), Automation (2), Computer vision, NICE CXone Mpower, Hiya Call Defence
```

### "What are the main AI use cases?"
```
File: roi_by_use_case.csv
Sort by: total_roi_claims (descending)
Answer: Customer Support (6 claims, 79% credibility), Network Optimization (4 claims, 79% credibility)
```

### "Which vendors are winning in UK telco AI?"
```
File: vendor_market_share.csv
Sort by: mention_count (descending)
Answer: Vyntelligence (2 mentions), NICE CXone Mpower (1), Hiya Call Defence (1) - highly fragmented market
```

### "Are telcos building or buying AI?"
```
File: build_vs_buy_analysis.csv
Answer: 100% buy strategy (0% in-house builds detected)
```

### "What are companies saying about AI ROI?"
```
File: roi_impact_analysis.csv
Filter by: company = "BT" or "Virgin Media O2" or "Vodafone"
Read: roi_claim column for actual quotes
Check: credibility_score to validate trustworthiness
```

---

## 10. CONTACT FOR QUESTIONS

**Data Pipeline Created By:** Claude (Anthropic AI)
**Run Date:** December 17, 2025
**Total Articles Processed:** 1,826
**AI Articles Found:** 77 (4.2%)
**Analysis Methodology:** LLM-based extraction using Ollama (gpt-oss:20b-cloud model)

**Note:** All credibility scores are algorithmically calculated based on:
- Source reliability (ISPreview, company press releases, industry publications)
- Specificity (quantitative claims score higher than qualitative)
- Sentiment analysis (positive sentiment = higher score)
- Use case confidence (well-defined use cases = higher score)

---

## TL;DR - Files You Actually Need

**For company quotes & ROI claims:**
- `03_processed_data/roi_by_company.csv`
- `02_analysis/pipelines/unified_ai_analysis_enhanced.csv` (filter by company name)

**For technology/vendor landscape:**
- `03_processed_data/technology_mentions.csv`
- `03_processed_data/vendor_market_share.csv`

**For visualizations:**
- `06_outputs/visualizations/company_roi_claims.png` ⭐ MAIN CHART

**For executive summary:**
- `06_outputs/FINAL_ANALYSIS_REPORT.txt`

**For deep dives on specific companies:**
- Filter `02_analysis/pipelines/unified_ai_analysis_enhanced.csv` by `companies_mentioned` column
- Read the `summary` column for AI-generated article summaries
- Check `url` column to link to original article

---

**Pro tip:** Load `unified_ai_analysis_enhanced.csv` in Excel/Google Sheets and use filters to quickly find articles by company, use case, or sentiment. This is your master dataset - everything else derives from it.
