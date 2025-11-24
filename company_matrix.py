"""
2x2 Matrix: Company Size vs AI Maturity/Adoption
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import re
import ollama

# Cache file for company data
COMPANY_DATA_CACHE = "output/company_size_data.json"

def fetch_company_data_from_llm(companies):
    """Use Kimi k2 to fetch company size data."""

    prompt = f"""You are a UK telecommunications industry analyst. Provide accurate financial and operational data for these UK telecom companies.

Companies to analyze: {', '.join(companies)}

For each company, provide:
1. revenue_bn: Annual UK revenue in GBP billions (use latest available data, typically 2023-2024)
2. employees: Number of UK employees
3. premises_m: Millions of premises passed/covered (0 if mobile-only)
4. type: Company type (Incumbent, Mobile, Cable, Altnet, Reseller, Infrastructure, Broadcaster)

Important notes:
- For BT Group, include all divisions (Consumer, Enterprise, Openreach)
- For VMO2, this is the merged Virgin Media O2 entity
- Use UK-specific figures, not global
- If a company is a subsidiary (like EE under BT), still provide separate figures

Return ONLY valid JSON in this exact format:
{{
  "BT": {{
    "revenue_bn": 20.8,
    "employees": 99000,
    "premises_m": 32,
    "type": "Incumbent"
  }},
  "Vodafone": {{
    "revenue_bn": 6.0,
    "employees": 9000,
    "premises_m": 0,
    "type": "Mobile"
  }}
}}

Include all companies listed above. Use your knowledge of the latest annual reports and industry data."""

    try:
        # Check available models
        available = ollama.list()
        model_names = [m.get('name') or m.get('model', '') for m in available.get('models', [])]

        if 'kimi-k2-thinking:cloud' in model_names:
            model = 'kimi-k2-thinking:cloud'
        elif 'qwen2.5:32b' in model_names:
            model = 'qwen2.5:32b'
        else:
            model = model_names[0] if model_names else 'qwen2.5:32b'

        print(f"Fetching company data using {model}...")

        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1}
        )

        response_text = response['message']['content'].strip()

        # Extract JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        elif '```' in response_text:
            response_text = re.sub(r'```[a-z]*\n?', '', response_text)

        # Find JSON object
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end > start:
            response_text = response_text[start:end]

        data = json.loads(response_text)

        # Cache the data
        with open(COMPANY_DATA_CACHE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Cached company data to {COMPANY_DATA_CACHE}")

        return data

    except Exception as e:
        print(f"Error fetching from LLM: {e}")
        return None

def get_company_data(companies):
    """Get company data from cache or LLM."""

    # Check cache first
    if os.path.exists(COMPANY_DATA_CACHE):
        try:
            with open(COMPANY_DATA_CACHE, 'r') as f:
                cached_data = json.load(f)

            # Check if all companies are in cache
            missing = [c for c in companies if c not in cached_data]
            if not missing:
                print(f"Using cached company data from {COMPANY_DATA_CACHE}")
                return cached_data
            else:
                print(f"Missing companies in cache: {missing}")
        except Exception as e:
            print(f"Error reading cache: {e}")

    # Fetch from LLM
    return fetch_company_data_from_llm(companies)

# Fallback data if LLM fails
FALLBACK_COMPANY_DATA = {
    'BT': {
        'revenue_bn': 20.7,
        'employees': 100000,
        'premises_m': 32,
        'type': 'Incumbent'
    },
    'Vodafone': {
        'revenue_bn': 6.0,
        'employees': 9000,
        'premises_m': 0,
        'type': 'Mobile'
    },
    'VMO2': {
        'revenue_bn': 10.5,
        'employees': 18000,
        'premises_m': 16,
        'type': 'Cable/Mobile'
    }
}

def calculate_ai_maturity(df):
    """Calculate AI maturity scores from analysis data."""
    maturity_scores = {}

    for company in df['company'].unique():
        company_data = df[df['company'] == company]

        # Factors for AI maturity score:
        # 1. Number of AI initiatives (volume)
        initiative_count = len(company_data)

        # 2. % High strategic importance
        if 'strategic_importance' in company_data.columns:
            high_strategic = (company_data['strategic_importance'] == 'high').sum()
            high_strategic_pct = high_strategic / len(company_data) * 100 if len(company_data) > 0 else 0
        else:
            high_strategic_pct = 50  # Default

        # 3. % Scaled deployments (maturity stage)
        if 'maturity_stage' in company_data.columns:
            scaled = (company_data['maturity_stage'] == 'scaled').sum()
            scaled_pct = scaled / len(company_data) * 100 if len(company_data) > 0 else 0
        else:
            scaled_pct = 30  # Default

        # 4. Diversity of use cases
        if 'primary_use_case' in company_data.columns:
            use_case_diversity = company_data['primary_use_case'].nunique()
        else:
            use_case_diversity = 1

        # 5. Positive sentiment (market perception)
        if 'sentiment' in company_data.columns:
            positive_pct = (company_data['sentiment'] == 'positive').sum() / len(company_data) * 100 if len(company_data) > 0 else 50
        else:
            positive_pct = 50

        # 6. Average confidence (analysis quality proxy)
        if 'confidence' in company_data.columns:
            avg_confidence = company_data['confidence'].mean() * 100
        else:
            avg_confidence = 50

        # Weighted maturity score (0-100)
        maturity_score = (
            min(initiative_count * 5, 30) +  # Cap at 30 points for volume
            high_strategic_pct * 0.25 +      # Up to 25 points
            scaled_pct * 0.20 +              # Up to 20 points
            min(use_case_diversity * 3, 15) + # Up to 15 points for diversity
            positive_pct * 0.05 +            # Up to 5 points
            avg_confidence * 0.05            # Up to 5 points
        )

        maturity_scores[company] = min(maturity_score, 100)  # Cap at 100

    return maturity_scores

def create_matrix_visualization(size_metric='revenue_bn'):
    """Create 2x2 matrix visualization."""

    # Load combined data
    combined_path = "output/combined_by_company.csv"
    big_firm_path = "big firm analysis/big_firm_analysis_results.csv"

    if os.path.exists(big_firm_path):
        df = pd.read_csv(big_firm_path)
        df = df.rename(columns={'standardized_use_case': 'primary_use_case'})
    elif os.path.exists(combined_path):
        df = pd.read_csv(combined_path)
    else:
        print("No data files found!")
        return None

    print(f"Loaded {len(df)} articles")

    # Get unique companies from data
    companies = df['company'].unique().tolist()

    # Fetch company size data from LLM
    company_data = get_company_data(companies)
    if company_data is None:
        print("Using fallback company data")
        company_data = FALLBACK_COMPANY_DATA

    # Calculate AI maturity scores
    maturity_scores = calculate_ai_maturity(df)

    # Build visualization data
    viz_data = []
    for company, score in maturity_scores.items():
        if company in company_data:
            company_info = company_data[company]
            viz_data.append({
                'company': company,
                'ai_maturity': score,
                'size': company_info.get(size_metric, 1),
                'type': company_info.get('type', 'Unknown'),
                'initiatives': len(df[df['company'] == company])
            })

    if not viz_data:
        print("No matching company data found!")
        return None

    viz_df = pd.DataFrame(viz_data)

    # Determine quadrant thresholds
    median_size = viz_df['size'].median()
    median_maturity = viz_df['ai_maturity'].median()

    print(f"\nMatrix thresholds:")
    print(f"  Size median: {median_size:.2f}")
    print(f"  AI Maturity median: {median_maturity:.1f}")

    # Size metric labels
    size_labels = {
        'revenue_bn': 'Company Revenue (GBP Billions)',
        'employees': 'Number of Employees',
        'premises_m': 'Premises Passed (Millions)'
    }

    # Create scatter plot
    fig = px.scatter(
        viz_df,
        x='ai_maturity',
        y='size',
        text='company',
        size='initiatives',
        color='type',
        title=f'UK Telecom AI Maturity Matrix: Company Size vs AI Adoption',
        labels={
            'ai_maturity': 'AI Maturity Score (0-100)',
            'size': size_labels.get(size_metric, 'Company Size'),
            'type': 'Company Type'
        },
        height=700,
        template='plotly_white'
    )

    # Update text position
    fig.update_traces(
        textposition='top center',
        marker=dict(
            sizemin=10,
            sizeref=0.5,
            line=dict(width=1, color='white')
        )
    )

    # Add quadrant lines
    fig.add_hline(y=median_size, line_dash="dash", line_color="#9ca3af", opacity=0.7, line_width=1.5)
    fig.add_vline(x=median_maturity, line_dash="dash", line_color="#9ca3af", opacity=0.7, line_width=1.5)

    # Add quadrant labels
    max_size = viz_df['size'].max()
    max_maturity = viz_df['ai_maturity'].max()

    annotations = [
        # Top-left: Large, Low AI
        dict(x=median_maturity/2, y=max_size * 0.9, text="<b>Large Scale<br>AI Laggards</b>",
             showarrow=False, font=dict(size=11, color="#6b7280"), opacity=0.6),
        # Top-right: Large, High AI
        dict(x=(median_maturity + max_maturity)/2, y=max_size * 0.9, text="<b>AI Leaders</b>",
             showarrow=False, font=dict(size=11, color="#10b981"), opacity=0.8),
        # Bottom-left: Small, Low AI
        dict(x=median_maturity/2, y=median_size * 0.3, text="<b>Emerging<br>Players</b>",
             showarrow=False, font=dict(size=11, color="#6b7280"), opacity=0.6),
        # Bottom-right: Small, High AI
        dict(x=(median_maturity + max_maturity)/2, y=median_size * 0.3, text="<b>AI-First<br>Challengers</b>",
             showarrow=False, font=dict(size=11, color="#3b82f6"), opacity=0.8),
    ]

    fig.update_layout(
        annotations=annotations,
        margin=dict(l=80, r=40, t=80, b=60),
        font=dict(size=12, family="Arial, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig, viz_df

def main():
    print("="*60)
    print("UK TELECOM AI MATURITY MATRIX")
    print("="*60)

    # Create visualizations for different size metrics
    metrics = ['revenue_bn', 'employees']

    for metric in metrics:
        print(f"\n--- Creating matrix with {metric} ---")
        result = create_matrix_visualization(metric)

        if result:
            fig, viz_df = result

            # Save as PNG
            png_file = f"output/ai_maturity_matrix_{metric}.png"
            fig.write_image(png_file, width=1200, height=800, scale=2)
            print(f"Saved: {png_file}")

            # Also save as PDF for presentations
            pdf_file = f"output/ai_maturity_matrix_{metric}.pdf"
            fig.write_image(pdf_file, width=1200, height=800)
            print(f"Saved: {pdf_file}")

            # Print data table
            print(f"\nCompany Data ({metric}):")
            print(viz_df.sort_values('ai_maturity', ascending=False).to_string(index=False))

    # Create summary
    print("\n" + "="*60)
    print("QUADRANT ANALYSIS")
    print("="*60)

    result = create_matrix_visualization('revenue_bn')
    if result:
        fig, viz_df = result

        median_size = viz_df['size'].median()
        median_maturity = viz_df['ai_maturity'].median()

        # Categorize companies
        quadrants = {
            'AI Leaders (Large + High AI)': [],
            'AI Laggards (Large + Low AI)': [],
            'AI-First Challengers (Small + High AI)': [],
            'Emerging Players (Small + Low AI)': []
        }

        for _, row in viz_df.iterrows():
            if row['size'] >= median_size and row['ai_maturity'] >= median_maturity:
                quadrants['AI Leaders (Large + High AI)'].append(row['company'])
            elif row['size'] >= median_size and row['ai_maturity'] < median_maturity:
                quadrants['AI Laggards (Large + Low AI)'].append(row['company'])
            elif row['size'] < median_size and row['ai_maturity'] >= median_maturity:
                quadrants['AI-First Challengers (Small + High AI)'].append(row['company'])
            else:
                quadrants['Emerging Players (Small + Low AI)'].append(row['company'])

        for quadrant, companies in quadrants.items():
            print(f"\n{quadrant}:")
            if companies:
                for company in companies:
                    score = viz_df[viz_df['company'] == company]['ai_maturity'].values[0]
                    print(f"  - {company} (score: {score:.1f})")
            else:
                print("  (none)")

if __name__ == "__main__":
    main()
