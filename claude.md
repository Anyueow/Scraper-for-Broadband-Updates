# Claude.md - UK Broadband AI Trends Analysis Project Guide

## Project Mission

This project analyzes AI adoption trends in the UK broadband and telecommunications industry by:
1. **Capturing AI mentions by company** - Tracking which companies are mentioned in AI-related articles
2. **Categorizing AI use cases** - Classifying how AI is being used across the industry
3. **Analyzing sentiment and maturity** - Understanding market perception and adoption stages

---

## Core Focus: AI Use Case Categorization

### Standardized AI Use Case Categories

All articles are analyzed and categorized into one of these **6 primary use case categories**:

#### 1. **Network Planning & Deployment**
**Definition:** AI that supports strategic design and rollout of network infrastructure

**Examples:**
- Coverage and capacity planning
- Site selection and rollout sequencing
- RF design optimization
- Investment prioritization (Capex planning)

**Key Indicators:** Planning, deployment, rollout, site selection, capacity planning, investment decisions, network architecture design

**Code Reference:** `network_planning_deployment`

---

#### 2. **Network Optimization & Performance Management**
**Definition:** AI that maximizes real-time network efficiency and service quality

**Examples:**
- Self-optimizing networks (SON)
- Traffic load balancing
- Interference management
- Real-time QoS monitoring
- SLA assurance for enterprise clients

**Key Indicators:** Optimization, performance, real-time, QoS, SLA, load balancing, interference, dynamic bandwidth allocation

**Code Reference:** `network_optimization_performance`

---

#### 3. **Predictive Maintenance & Network Analytics**
**Definition:** AI that anticipates failures, reduces downtime, and extracts operational insights

**Examples:**
- Fault prediction and anomaly detection
- Automated root-cause analysis
- Asset health scoring
- Preventive maintenance scheduling
- Energy usage optimization analytics

**Key Indicators:** Predictive, maintenance, fault prediction, anomaly detection, preventive, health monitoring, root-cause analysis

**Code Reference:** `predictive_maintenance_analytics`

---

#### 4. **Customer Support & Experience Automation**
**Definition:** AI that improves customer interactions and reduces service friction

**Examples:**
- Virtual agents and chatbots
- AI-assisted troubleshooting
- Sentiment/intent analysis
- Automated ticket triage and resolution
- Personalized self-service flows

**Key Indicators:** Customer support, chatbot, virtual agent, customer experience, troubleshooting, ticket resolution, sentiment analysis

**Code Reference:** `customer_support_experience`

---

#### 5. **Security, Fraud & Threat Intelligence**
**Definition:** AI safeguarding networks, data, and revenue streams

**Examples:**
- Threat detection and mitigation
- DDoS/cyber anomaly detection
- Fraud detection (SIM fraud, subscription fraud)
- Identity verification
- Revenue assurance analytics

**Key Indicators:** Security, fraud, threat detection, cybersecurity, DDoS, identity verification, spam, voice fraud

**Code Reference:** `security_fraud_threat`

---

#### 6. **Internal Productivity & Workforce Enablement**
**Definition:** AI supporting employees (knowledge assistants, document automation, workflow copilots)

**Examples:**
- AI coding assistants
- Internal knowledge bases
- Process automation
- Employee training tools
- Document generation (e.g., spectrumGPT at Charter Communications)
- Workflow automation
- Procurement automation

**Key Indicators:** Internal operations, productivity, workforce, employee training, automation, coding assistant, procurement, knowledge base

**Code Reference:** `internal_productivity_workforce`

---

#### Fallback Category: **other**
**Definition:** AI is mentioned but doesn't fit the above 6 categories, or the use case is unclear

**Examples:**
- General AI strategy discussions
- AI partnerships without specific use case
- Research and development
- Unclear or ambiguous AI applications

**Code Reference:** `other`

---

## Company Mention Tracking

### Primary Companies Tracked

The analysis captures AI mentions for major UK telecommunications companies:

- **BT** (BT Group)
- **VMO2** (Virgin Media O2)
- **Vodafone**
- **EE**
- **Three** (3 UK)
- **Sky**
- **TalkTalk**
- **Plusnet**
- **Other UK broadband providers**

### How Company Mentions Are Captured

1. **Article Title Analysis:** Company names extracted from article titles
2. **Content Analysis:** Companies mentioned in article body text
3. **Big Firm Analysis:** Dedicated analysis pipeline for major company-specific articles
   - Located in: `big firm analysis/`
   - Input: `AI Articles By Company.xlsx`
   - Output: `big_firm_analysis_results.csv` and `big_firm_cache.json`

### Company Data Structure

For each company, the analysis captures:
- **Number of AI mentions** per company
- **Use cases** each company is pursuing
- **Sentiment** toward AI initiatives
- **Maturity stage** (pilot, deployment, scaled)
- **Strategic importance** (high, medium, low)
- **Key technologies** deployed
- **Business impact** descriptions

---

## Data Flow & Output Structure

### Input Sources

1. **Scraped Articles** (`Scraped Output/`)
   - `fibernews_articles.csv`
   - `ispreview_articles.csv`
   - `thinkbroadband_articles.csv`

2. **Big Firm Articles** (`big firm analysis/`)
   - `AI Articles By Company.xlsx` - Manually curated company-specific articles

### Analysis Pipeline

1. **LLM Analysis** (`Article Analysis/llm_analysis_pipeline.py`)
   - Uses Ollama (kimi-k2-thinking or qwen2.5:32b)
   - Analyzes each article for:
     - AI mentions and counts
     - Primary use case classification
     - All use cases mentioned
     - Sentiment analysis
     - Article summary

2. **Big Firm Analysis** (`big firm analysis/big_firm_analyzer.py`)
   - Company-specific deep analysis
   - Additional fields:
     - Strategic importance
     - Maturity stage
     - Key technologies
     - Business impact

### Output Files

1. **Unified Analysis** (`output/unified_ai_analysis.csv`)
   - All articles with standardized use case categorization
   - Columns: `source`, `date`, `title`, `url`, `primary_use_case`, `primary_use_case_confidence`, `ai_use_cases`, `sentiment`, `ai_mention_count`, `ai_mentions`, `word_count`, `summary`, `title_ai_mention_count`, `title_ai_mentions`

2. **Big Firm Results** (`big firm analysis/big_firm_analysis_results.csv`)
   - Company-specific analysis with strategic insights
   - Additional columns: `company`, `strategic_importance`, `maturity_stage`, `key_technologies`, `business_impact`

3. **Cache Files**
   - `Article Analysis/analysis_cache.json` - General article analysis cache
   - `big firm analysis/big_firm_cache.json` - Big firm analysis cache

---

## Key Analysis Metrics

### Use Case Metrics
- **Primary use case** - The main AI application discussed
- **Use case confidence** - LLM confidence score (0.0-1.0)
- **All use cases** - Complete list of use cases mentioned
- **Use case frequency** - How often each use case appears

### Company Metrics
- **Company mention count** - Number of articles mentioning each company
- **Company use case matrix** - Which companies focus on which use cases
- **Company sentiment** - Overall sentiment toward AI by company
- **Company maturity** - Adoption stage by company

### Sentiment Analysis
- **positive** - AI presented as beneficial, innovative, problem-solving
- **neutral** - Factual discussion without strong opinion
- **negative** - Concerns, criticism, or problems with AI
- **mixed** - Both positive and negative aspects
- **not_applicable** - Article doesn't discuss AI

---

## Dashboard Visualization

The Streamlit dashboard (`dashboard.py`) provides:

### 7 Analysis Tabs

1. **Time Series - Where AI is Used**
   - Use case adoption over time
   - Company activity timeline
   - Growth rates by use case

2. **Use Cases Deep Dive**
   - Use case distribution
   - Opportunity matrix
   - Use case statistics

3. **Company Analysis**
   - Company-technology matrix
   - Strategic importance by company
   - Company focus areas

4. **Sentiment & Maturity**
   - Sentiment trends over time
   - Maturity progression
   - Sentiment by use case

5. **Market Positioning**
   - Company-use case heatmap
   - Opportunity bubble chart
   - Source comparison

6. **Technology Trends**
   - Key technologies deployed
   - Technology-use case mapping
   - Technology mentions over time

7. **Strategic Synthesis**
   - Strategic recommendations
   - Key insights summary
   - Actionable implications

---

## Important Guidelines for LLM Analysis

### Use Case Classification Rules

1. **Primary Use Case Selection:**
   - Choose the **most prominent** use case from the **6 standard categories**
   - Consider the article's main focus, not just mentions
   - Use confidence score to indicate uncertainty
   - Only use "other" if truly none of the 6 categories fit

2. **Multiple Use Cases:**
   - Include ALL use cases mentioned in `ai_use_cases` array
   - Primary use case should be the dominant one
   - Don't force a single category if article covers multiple areas
   - All use cases must be from the 6 standard categories (or "other")

3. **Company Extraction:**
   - Extract company names from titles and content
   - Use standardized company names (BT, VMO2, Vodafone, etc.)
   - Handle variations (e.g., "BT Group" → "BT")

4. **Sentiment Analysis:**
   - Focus on sentiment toward AI, not general article sentiment
   - Consider context: Is AI presented as solution or problem?
   - "Mixed" should be used when both positive and negative aspects are discussed

### Data Quality Standards

- **Confidence Scores:** Use 0.0-1.0 scale
  - 0.9-1.0: Very clear use case
  - 0.7-0.9: Clear but some ambiguity
  - 0.5-0.7: Moderate confidence
  - 0.0-0.5: Low confidence, use "other" if uncertain

- **AI Mention Detection:**
  - Look for: AI, artificial intelligence, machine learning, ML, deep learning, neural networks, chatbot, automation, predictive analytics, etc.
  - Count all mentions, not just first occurrence
  - Include variations and acronyms

---

## Project Structure

```
Scraper-for-Broadband-Updates/
├── scrapper/                    # Web scraping scripts
│   ├── fibernews.py
│   ├── ispreview.py
│   └── thinkbroadband.py
├── Scraped Output/              # Raw scraped articles (CSV)
├── Article Analysis/            # LLM analysis pipeline
│   ├── llm_analysis_pipeline.py
│   ├── analysis_cache.json
│   └── unified_ai_analysis.csv
├── big firm analysis/           # Company-specific analysis
│   ├── big_firm_analyzer.py
│   ├── AI Articles By Company.xlsx
│   ├── big_firm_cache.json
│   └── big_firm_analysis_results.csv
├── output/                      # Final unified outputs
│   └── unified_ai_analysis.csv
├── dashboard.py                 # Streamlit visualization dashboard
└── claude.md                    # This file
```

---

## Key Questions This Project Answers

1. **Where is AI being used?** → Use case categorization
2. **Which companies are leading?** → Company mention tracking
3. **What technologies are deployed?** → Technology extraction
4. **How mature is adoption?** → Maturity stage analysis
5. **What's the market sentiment?** → Sentiment analysis
6. **What are the opportunities?** → Opportunity matrix analysis

---

## Quick Reference: Use Case Decision Tree

```
Does article mention AI/ML?
├─ NO → "not_applicable" sentiment, no use case
└─ YES → What is the PRIMARY application?
    ├─ Network planning/design/rollout → "Network Planning & Deployment"
    │   (network_planning_deployment)
    ├─ Real-time optimization/performance → "Network Optimization & Performance Management"
    │   (network_optimization_performance)
    ├─ Predictive/fault detection/analytics → "Predictive Maintenance & Network Analytics"
    │   (predictive_maintenance_analytics)
    ├─ Customer service/support/experience → "Customer Support & Experience Automation"
    │   (customer_support_experience)
    ├─ Security/fraud/threat → "Security, Fraud & Threat Intelligence"
    │   (security_fraud_threat)
    ├─ Internal tools/productivity/workforce → "Internal Productivity & Workforce Enablement"
    │   (internal_productivity_workforce)
    └─ Unclear/doesn't fit above → "other"
```

---

## Notes for AI Assistants

- **Always use the 6 standardized use case categories** - Don't create new categories
- **Use proper category names** - Display names (e.g., "Network Planning & Deployment") or code names (e.g., "network_planning_deployment") as appropriate
- **Extract company names consistently** - Use the standardized list
- **Prioritize accuracy over speed** - Use confidence scores appropriately
- **Cache results** - Don't re-analyze articles unnecessarily
- **Validate outputs** - Ensure JSON structure and category validity (must be one of the 6 categories or "other")
- **Focus on the "meat"** - Where is AI actually being used, not just mentioned?
- **Remember: 6 categories, not 7** - The "other" category is a fallback, not a primary category

---

*Last Updated: Based on project structure as of current implementation*

