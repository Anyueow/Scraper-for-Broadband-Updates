1. Scrape data (raw) - from the three news sites 
1.1  Clean data (keep AI-only mentions articles)
1.2 Analyze: summarization + categorization into 6 buckets + AI mention counting 
    1.2.a all major AI use case category graphs (bar charts)

2. Extract all company names from each article (maybe add inference code while doing analysis to add a company column there)
2.2 Combine given company pairs (BT / Openreach, VMO2 / nexfibre, APFN / Cuckoo, Netomnia / Brsk / YouFibre)
    2.2.a companies tick matrix by each ai use case as seen in company_use_case_matrix_binary_sorted.csv
2.3 Run script to collect revenue + employee size @Scraper-for-Broadband-Updates/company_revenue_lookup.py
2.4 Company size / AI activity analysis (for building the matrix view)
2.5 Run an impact analysis to classifiy ROI of Telco AI 
    2.5.a Check company names, see if it publicly listed, and parse all 2025 earnings calls, and look for AI mentions and how AI might have led to productivity or revenue growth. Check out ROI_Formula.MD to understand how to qualitatively and quantitiavely qualify ROI 

3. Tech stack analysis 
    3.1  Which AI technologies are actually being deployed, and what does the vendor landscape look like? 
    3.1.a So:**Data to Extract from Articles:
        ****Foundation models:** Azure OpenAI, Google Vertex AI, Ollama, proprietary models
        - **Platforms:** ServiceNow, NICE, LangChain, Lenses.io, IQGeo, Vyntelligence
        - **Infrastructure:** AWS, Azure, Google Cloud, on-premise
        - **Specific techniques:** LSTMs, LLMs, computer vision, reinforcement learning
        - bundling partners, like adding perplexity premium for customer offerings (increasing customer retention / incitement)
    3.1.b
        **Analyses:**
        1. **Vendor Power Matrix:** Which vendors appear most frequently? (ServiceNow, Microsoft dominating?)
        2. **Technology Maturity Curve:** Early-stage (RL, agentic AI) vs. mainstream (LLMs, supervised learning)
        3. **Build vs. Buy Breakdown:** % of companies building in-house vs. buying platforms
    3.2 **Visualizations:**
        - **Technology Co-occurrence Network:** Which technologies are deployed together?
        - **Vendor Market Share Pie Chart*