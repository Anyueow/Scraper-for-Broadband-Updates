# UK Broadband AI Trends Dashboard - Launch Guide

## ✅ Pipeline Status: READY

### Data Summary
- **Total Articles Analyzed**: 1,902
- **AI Articles Found**: **154** (Goal: 120+) ✅
- **Companies Tracked**: 25+ UK telecoms companies
- **Data Sources**:
  - Scraped articles (ISPreview, FibreNews, ThinkBroadband): 27 AI articles
  - Manual inputs (increased_scope.csv): 52 AI articles
  - Excel (AI Articles By Company.xlsx): 78 AI articles (NEWLY ADDED)

---

## 🚀 Launch the Dashboard

### Command:
```bash
cd /Users/anyueow/Desktop/coding\ projects/Scraper-for-Broadband-Updates
streamlit run dashboard.py
```

### Expected Behavior:
The dashboard will open in your default browser at: `http://localhost:8501`

---

## 📊 Dashboard Features

### 1. **Overview Metrics**
- Total AI articles
- Companies tracked
- Use case categories
- Time range

### 2. **Time Series Analysis**
- AI article trends over time
- Growth patterns
- Peak activity periods

### 3. **Company Analysis**
- Top companies by AI activity
- Company-use case matrix (heatmap)
- Build vs Buy strategies

### 4. **Use Case Distribution**
- Primary use cases
- Category breakdown
- Adoption patterns

### 5. **Technology Trends**
- Vendor mentions
- Technology adoption
- Platform analysis

### 6. **ROI Analysis**
- ROI claims by company
- ROI claims by use case
- Business impact metrics

---

## 🔧 Recent Fixes Applied

1. ✅ Added 78 articles from Excel file
2. ✅ Fixed dashboard column mapping (company → source)
3. ✅ Fixed build_vs_buy_analysis data handling
4. ✅ Updated all data loading paths
5. ✅ Regenerated all analysis files

---

## 📁 Key Data Files

All files are located and verified:

```
✓ 02_analysis/pipelines/unified_ai_analysis_enhanced.csv (1,902 rows)
✓ company_use_case_matrix_binary_sorted.csv (13 companies)
✓ 03_processed_data/build_vs_buy_analysis.csv (16 companies)
✓ 03_processed_data/technology_mentions.csv (3 technologies)
✓ 03_processed_data/vendor_market_share.csv (2 vendors)
✓ 03_processed_data/roi_impact_analysis.csv (69 ROI claims)
✓ 06_outputs/visualizations/*.png (5 charts)
```

---

## 🎯 Top Companies in Dashboard

1. **BT** - 16 AI articles
2. **Vodafone** - 15 AI articles
3. **VMO2** - 12 AI articles
4. **CityFibre** - 5 AI articles
5. **Gigaclear, Sky, TalkTalk, Openreach** - 4 articles each

---

## 💡 Usage Tips

### Filters Available:
- **Date Range**: Filter articles by publication date
- **Company**: View specific company's AI activities
- **Use Case**: Filter by AI use case category

### Interactive Features:
- Hover over charts for detailed tooltips
- Click on legend items to toggle visibility
- Use zoom controls on time series charts

---

## ⚠️ Known Limitations

1. **Use Case Distribution**: Most articles (84%) fall into "other" category
   - This is expected - many articles mention AI generally without specific use case details

2. **Technology Extraction**: Only 3 specific technologies identified
   - LLM needs better prompting for vendor/platform extraction
   - Many articles don't mention specific product names

3. **Company Size Data**: Using placeholder data for company size scores
   - Would need external data (revenue, employees) for accurate sizing

---

## 🔄 To Refresh Data

If you add more articles or re-run scraping:

```bash
# Re-run the full pipeline
python3 main.py

# Or skip LLM analysis (if data already analyzed)
python3 main.py --skip-llm
```

Then restart the dashboard to see updated data.

---

## 📞 Support

If the dashboard doesn't load:
1. Check that all CSV files exist (listed above)
2. Ensure Streamlit is installed: `pip install streamlit`
3. Check for Python errors in terminal
4. Try clearing Streamlit cache: Press 'c' in the dashboard

---

**Dashboard Ready! Run: `streamlit run dashboard.py`** 🎉
