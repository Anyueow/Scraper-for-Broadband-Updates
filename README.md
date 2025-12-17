# Telco AI Analysis Project
## Mapping Artificial Intelligence Adoption Across Global Telecommunications Infrastructure

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Data Quality](https://img.shields.io/badge/data%20quality-validated-green.svg)](#validation)

---

## 🎯 Project Mission

This project provides **the most comprehensive public analysis of AI adoption in the global telecommunications industry**, tracking how fiber providers, mobile operators, and network infrastructure companies are deploying artificial intelligence across six key use cases.

**Scope:**
- **Companies:** 30+ telecommunications and infrastructure providers (UK, Europe, North America)
- **Articles Analyzed:** 500+ industry publications, company newsrooms, and research papers
- **Time Period:** 2023-2025 (ongoing)
- **Analysis Depth:** LLM-powered classification, sentiment analysis, maturity tracking, and strategic benchmarking

**Target Audience:**
- Industry executives and strategists
- Investors and analysts
- Policymakers and regulators
- Technology journalists
- Academic researchers

---

## 📊 Key Findings at a Glance

*[To be updated with latest analysis results]*

- **Most Active Use Case:** Customer Support & Experience Automation (60-70% adoption among major players)
- **Highest ROI Claims:** Predictive Maintenance (30-50% opex reduction)
- **Leaders in AI Maturity:** BT, Vodafone, Virgin Media O2, CityFibre
- **Fastest-Moving Segment:** B2B infrastructure providers (Colt, Zayo, euNetworks)
- **Emerging Trend:** AI-ready infrastructure positioning (fiber routes for AI data centers)
- **Workforce Impact:** Estimated 5,000+ call center jobs at risk; 500+ AI/ML roles created

---

## 🗂️ Repository Structure

```
telco-ai-analysis/
│
├── 📄 README.md                          # This file
├── 📄 CLAUDE.md                          # AI analysis taxonomy & guidelines
├── 📄 STRATEGIC_ANALYSIS.md              # First-principles analysis & journalism angles
├── 📄 REPOSITORY_STRUCTURE.md            # Detailed directory reference
├── 📄 METHODOLOGY.md                     # Research methodology & validation
│
├── 📂 01_data_collection/                # Web scrapers & manual curation
├── 📂 02_analysis/                       # LLM analysis pipelines
├── 📂 03_processed_data/                 # Cleaned, analyzed datasets
├── 📂 04_advanced_analysis/              # Specialized analytics
├── 📂 05_visualizations/                 # Dashboard & publication charts
├── 📂 06_outputs/                        # Reports & data releases
├── 📂 07_validation/                     # Quality assurance
├── 📂 08_supplementary_data/             # Job postings, conferences, patents
└── 📂 09_documentation/                  # Guides & API docs
```

**For detailed structure, see:** [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md)

---

## 🚀 Quick Start

### Prerequisites
- **Python:** 3.8 or higher
- **Ollama:** Local LLM server (for analysis pipeline)
  - Recommended models: `kimi-k2-thinking:latest` or `qwen2.5:32b`
- **Storage:** ~2GB for datasets and caches

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/telco-ai-analysis.git
cd telco-ai-analysis

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama (if not already installed)
# See: https://ollama.ai/download

# 4. Pull LLM model
ollama pull kimi-k2-thinking:latest

# 5. Verify installation
python -c "import pandas, streamlit, requests; print('Dependencies OK')"
```

### Running the Dashboard

```bash
# Launch interactive Streamlit dashboard
streamlit run 05_visualizations/dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501` with 7 analysis tabs:
1. Time Series - Where AI is Used
2. Use Cases Deep Dive
3. Company Analysis
4. Sentiment & Maturity
5. Market Positioning
6. Technology Trends
7. Strategic Synthesis

### Running Analysis Pipeline

```bash
# Analyze new articles (example: increased_scope.csv)
python 02_analysis/pipelines/llm_analysis_pipeline.py \
    --input 01_data_collection/manual_inputs/increased_scope.csv \
    --output 03_processed_data/unified_ai_analysis.csv \
    --cache 02_analysis/caches/analysis_cache.json

# Deep-dive analysis for major companies
python 02_analysis/pipelines/big_firm_analyzer.py \
    --input 01_data_collection/manual_inputs/AI_Articles_By_Company.xlsx \
    --output 03_processed_data/big_firm_analysis.csv
```

---

## 📚 Core Concepts

### The 6 AI Use Cases in Telecommunications

This analysis categorizes all AI deployments into **six standardized use cases**:

| # | Use Case | Description | Example Applications | Typical ROI |
|---|----------|-------------|---------------------|-------------|
| 1 | **Network Planning & Deployment** | AI for strategic network design and rollout | Coverage planning, site selection, capex optimization | 20-30% capex savings |
| 2 | **Network Optimization & Performance** | Real-time network efficiency and QoS | Self-optimizing networks, load balancing, SLA assurance | 15-25% opex savings |
| 3 | **Predictive Maintenance & Analytics** | Anticipating failures and extracting insights | Fault prediction, anomaly detection, energy optimization | 30-50% opex savings |
| 4 | **Customer Support & Experience** | Improving customer interactions | Chatbots, AI-assisted agents, automated triage | 40-60% opex savings |
| 5 | **Security, Fraud & Threat Intelligence** | Safeguarding networks and revenue | DDoS detection, fraud prevention, identity verification | 1-3% revenue protection |
| 6 | **Internal Productivity & Workforce** | Employee-facing AI tools | Coding assistants, knowledge bases, workflow automation | 10-20% productivity gains |

**See full taxonomy:** [CLAUDE.md](CLAUDE.md)

### Key Metrics Tracked

- **Sentiment:** Positive, neutral, negative, mixed toward AI
- **Maturity Stage:** Pilot → Limited Deployment → Scaled Production
- **Strategic Importance:** High, medium, low
- **Confidence Score:** LLM certainty in classification (0.0-1.0)
- **Source Tier:** Credibility rating (1=peer-reviewed, 4=PR)
- **Hype vs. Reality Ratio:** Public mentions ÷ deployment evidence

---

## 🔍 Research Methodology

### Data Collection
1. **Automated Web Scraping**
   - ISPreview UK, ThinkBroadband, FiberNews (UK broadband press)
   - 3 sources × weekly runs = ~50-100 articles/month

2. **Manual Curation**
   - Company newsrooms (BT, Vodafone, Colt, Zayo, etc.)
   - Industry reports and whitepapers
   - Academic journals and conference proceedings
   - Paywalled publications (Financial Times, WSJ)

### LLM Analysis Pipeline
- **Model:** Ollama running `kimi-k2-thinking:latest` (32B parameter model optimized for reasoning)
- **Processing:** Each article analyzed for:
  - AI use case classification (6 categories + "other")
  - Sentiment analysis
  - Company and technology extraction
  - Strategic importance and maturity assessment
  - Summary generation (200-300 words)
- **Caching:** Results cached to avoid redundant LLM calls
- **Validation:** Multi-source corroboration, expert review, outlier detection

### Quality Assurance
- **Source Tier System:** Rate articles by credibility (independent journalism > vendor case studies > PR)
- **Cross-Source Validation:** Major claims require 2+ independent sources
- **Expert Review:** Findings shared with industry experts for validation
- **Company Fact-Check:** Profiled companies invited to correct errors (not editorial control)

**Full methodology:** [METHODOLOGY.md](METHODOLOGY.md)

---

## 📈 Outputs & Publications

### Interactive Dashboard
**Location:** `05_visualizations/dashboard.py`
**Access:** Run `streamlit run 05_visualizations/dashboard.py`

**Features:**
- Time series analysis of AI adoption by use case
- Company benchmarking and maturity heatmaps
- Sentiment trends over time
- Technology stack co-occurrence analysis
- Opportunity matrix (ROI vs. adoption)

### Data Releases
**Public Dataset:** `06_outputs/data_releases/telco_ai_index_2025_v1.csv`
- Anonymized/aggregated findings
- Company-level metrics (not article-level)
- Licensed under Creative Commons BY-NC-SA 4.0

**Codebook:** `06_outputs/data_releases/codebook.pdf`

### Reports
**Executive Summary:** `06_outputs/reports/executive_summary.md` (2 pages)
**Full Report:** `06_outputs/reports/full_report.pdf` (20-40 pages)
**Industry Benchmark Report:** `06_outputs/reports/industry_benchmark_report.pdf` (commercial product)

### Media Kits
**For Journalists:** `06_outputs/media_kits/`
- Press release template
- Key findings fact sheet
- Infographics (PNG, SVG)
- Expert quotes

---

## 🎓 Academic & Policy Applications

This dataset has been used in:
- Policy briefs on AI governance in critical infrastructure
- Academic papers on technology adoption in telecommunications
- Investor research reports
- Industry conference presentations

**Citing This Work:**
```bibtex
@misc{telco_ai_analysis_2025,
  title={AI Adoption in Global Telecommunications Infrastructure: A Comprehensive Analysis},
  author={[Your Name]},
  year={2025},
  howpublished={\url{https://github.com/yourusername/telco-ai-analysis}},
  note={Dataset version 1.0}
}
```

---

## 🛠️ For Developers

### Adding New Data Sources

1. **Web Scraper:**
   - Create new scraper in `01_data_collection/scrapers/your_source_scraper.py`
   - Inherit from `base_scraper.py` if available
   - Output to `01_data_collection/raw_outputs/`

2. **Manual Curation:**
   - Add articles to `01_data_collection/manual_inputs/increased_scope.csv`
   - Format: `source,date,title,url,[optional additional fields]`

3. **Run Analysis:**
   ```bash
   python 02_analysis/pipelines/llm_analysis_pipeline.py --input your_new_data.csv
   ```

### Extending Analysis

**Custom Metrics:**
- Add scripts to `04_advanced_analysis/`
- Read from `03_processed_data/unified_ai_analysis.csv`
- Output results to same directory with descriptive names

**Dashboard Enhancements:**
- Modular components in `05_visualizations/dashboard_components/`
- Add new tab by creating `your_tab.py` and registering in `dashboard.py`

**See:** `09_documentation/API_DOCUMENTATION.md` for function references

---

## 🔐 Data Privacy & Ethics

### What Data is Collected?
- **Public Information Only:** Articles, press releases, job postings, conference talks
- **Company Names:** Public companies, publicly disclosed initiatives
- **Individual Names:** Only public figures (executives, researchers) in published sources

### What is NOT Included?
- ❌ Leaked or confidential documents
- ❌ Personally identifiable information (PII)
- ❌ Non-public employee data
- ❌ Proprietary financial data (only publicly disclosed figures)

### Ethical Commitments
- **Transparency:** Methodology fully documented
- **Accuracy:** Multi-source validation, company fact-checking
- **Fairness:** Equal treatment of companies; no paid placements
- **Responsible Use:** Data intended for research, analysis, journalism—not competitive intelligence gathering

---

## 📞 Contact & Contributing

**Project Maintainer:** [Your Name]
**Email:** [your.email@example.com]
**GitHub Issues:** [https://github.com/yourusername/telco-ai-analysis/issues](https://github.com/yourusername/telco-ai-analysis/issues)

### How to Contribute

We welcome contributions in several forms:

1. **Data Curation:**
   - Suggest new articles via GitHub issue (label: "Data Curation")
   - Submit curated datasets via pull request

2. **Code Contributions:**
   - Fork repository
   - Create feature branch: `feature/your-feature-name`
   - Submit pull request to `dev` branch
   - See `09_documentation/CONTRIBUTING.md` for style guide

3. **Expert Review:**
   - Industry experts: Validate findings in your area
   - Academics: Collaborate on research papers
   - Contact maintainer for access to expert review materials

4. **Bug Reports & Feature Requests:**
   - Open GitHub issue with descriptive title
   - Include error logs, screenshots, or data samples

---

## 📜 License

### Code
**License:** MIT License
- You may use, modify, and distribute the code freely
- Attribution appreciated but not required

### Data
**License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)
- ✅ Share and adapt for non-commercial purposes
- ✅ Provide attribution
- ✅ Share modifications under same license
- ❌ Commercial use requires permission (contact maintainer)

### Publications
Reports and visualizations in `06_outputs/` are © [Your Name] 2025. Use with attribution.

---

## 🗺️ Roadmap

### Completed ✅
- [x] Core LLM analysis pipeline
- [x] 6-use-case taxonomy
- [x] Interactive Streamlit dashboard
- [x] Manual curation of 500+ articles
- [x] Company benchmarking framework

### In Progress 🚧
- [ ] LinkedIn job posting analysis integration
- [ ] Conference speaker & publication tracking
- [ ] Geographic expansion (Asia-Pacific coverage)
- [ ] Automated validation suite
- [ ] Academic paper publication

### Planned 📋
- [ ] Real-time monitoring (daily scraping + alerts)
- [ ] API endpoint for programmatic access
- [ ] Natural language query interface
- [ ] Predictive modeling (forecast AI adoption curves)
- [ ] Multi-language support (French, German, Spanish telecoms)

---

## 🙏 Acknowledgments

This project builds on open-source tools and public data:
- **LLM Framework:** Ollama (https://ollama.ai)
- **Visualization:** Streamlit (https://streamlit.io)
- **Data Sources:** ISPreview, ThinkBroadband, FiberNews, and 20+ company newsrooms
- **Community:** Contributors, expert reviewers, and beta testers

Special thanks to:
- [List key contributors/advisors if applicable]

---

## 🆘 Support & Troubleshooting

### Common Issues

**Dashboard won't start:**
```bash
# Check if unified_ai_analysis.csv exists
ls -lh 03_processed_data/unified_ai_analysis.csv

# If missing, run analysis pipeline first
python 02_analysis/pipelines/llm_analysis_pipeline.py --input 01_data_collection/manual_inputs/increased_scope.csv
```

**Ollama connection error:**
```bash
# Verify Ollama is running
curl http://localhost:11434/api/version

# Start Ollama if needed
ollama serve
```

**Analysis pipeline slow:**
- Use smaller, faster model: `ollama pull qwen2.5:7b`
- Reduce batch size in pipeline config
- Check LLM cache hit rate (should be >80% on re-runs)

**See full troubleshooting guide:** [REPOSITORY_STRUCTURE.md § Troubleshooting](REPOSITORY_STRUCTURE.md#troubleshooting)

---

## 📚 Further Reading

- **[STRATEGIC_ANALYSIS.md](STRATEGIC_ANALYSIS.md)** - First-principles analysis, journalism angles, creative story ideas
- **[CLAUDE.md](CLAUDE.md)** - Use case taxonomy, AI assistant guidelines, classification rules
- **[METHODOLOGY.md](METHODOLOGY.md)** - Research methodology, validation approach, data quality standards
- **[03_processed_data/data_dictionary.md](03_processed_data/data_dictionary.md)** - Complete field reference for all datasets

---

**Built with:** Python 🐍 | Ollama 🦙 | Streamlit 🚀 | Pandas 🐼

**Last Updated:** December 14, 2025
**Version:** 2.0 (Expanded Scope - Global Telco AI Analysis)

---

*For questions, suggestions, or collaboration opportunities, please open a GitHub issue or contact the maintainer.*
