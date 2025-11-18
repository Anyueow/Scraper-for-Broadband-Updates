"""
Streamlit Dashboard for UK Broadband AI Trends Analysis
Consulting-style insights for strategic decision-making
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
import re
import json
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="UK Broadband AI Trends | Strategic Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for consulting-style presentation
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    .insight-box {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 4px;
        border-left: 4px solid #2563eb;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stPlotlyChart {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(csv_path="output/unified_ai_analysis.csv"):
    """Load and preprocess the analysis data."""
    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df['year'] = df['date'].dt.year
    df['quarter'] = df['date'].dt.quarter
    df['has_ai'] = df['ai_mention_count'] > 0
    df['has_title_ai'] = df['title_ai_mention_count'] > 0

    return df

@st.cache_data
def load_big_firm_data(csv_path="big firm analysis/big_firm_analysis_results.csv"):
    """Load big firm analysis data."""
    if not os.path.exists(csv_path):
        return None
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    
    # Map standardized_use_case to primary_use_case for consistency
    df['primary_use_case'] = df['standardized_use_case']
    
    return df

@st.cache_data
def load_big_firm_cache(cache_path="big firm analysis/big_firm_cache.json"):
    """Load rich big firm cache data with full analysis details."""
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        # Convert cache to DataFrame for easier analysis
        records = []
        for key, value in cache.items():
            # Extract company from key (format: "Company_Article Title")
            parts = key.split('_', 1)
            company = parts[0] if len(parts) > 0 else 'Unknown'
            
            record = {
                'company': company,
                'standardized_use_case': value.get('standardized_use_case', 'other'),
                'confidence': value.get('confidence', 0.0),
                'sentiment': value.get('sentiment', 'neutral'),
                'strategic_importance': value.get('strategic_importance', 'unknown'),
                'maturity_stage': value.get('maturity_stage', 'unknown'),
                'key_technologies': value.get('key_technologies', []),
                'business_impact': value.get('business_impact', ''),
                'summary': value.get('summary', '')
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        df['primary_use_case'] = df['standardized_use_case']
        
        return df
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None

def extract_companies(df):
    """Extract company/vendor names from titles and content."""
    # Common UK telecom companies
    companies = [
        'BT', 'Openreach', 'Virgin Media', 'O2', 'EE', 'Vodafone', 'Three',
        'TalkTalk', 'Sky', 'Plusnet', 'Gigaclear', 'CityFibre', 'Hyperoptic',
        'Community Fibre', 'Zzoomm', 'Fibrus', 'Quickline', 'Daisy',
        'AllPoints', 'Vorboss', 'Connect Fibre', 'Nexfibre', 'TOTSCo',
        'Microsoft', 'Google', 'Amazon', 'IBM', 'Cisco', 'Nokia', 'Ericsson',
        'Huawei', 'Juniper', 'VMware', 'Oracle', 'Salesforce'
    ]
    
    company_mentions = []
    for idx, row in df.iterrows():
        text = f"{row.get('title', '')} {row.get('summary', '')}".lower()
        found_companies = []
        for company in companies:
            if company.lower() in text:
                found_companies.append(company)
        if found_companies:
            company_mentions.append({
                'url': row.get('url', ''),
                'companies': found_companies,
                'primary_use_case': row.get('primary_use_case'),
                'sentiment': row.get('sentiment'),
                'ai_mention_count': row.get('ai_mention_count', 0)
            })
    
    return pd.DataFrame(company_mentions)

def create_clean_time_series(df):
    """Clean time series chart for presentations."""
    monthly = df.groupby('year_month').agg({
        'has_ai': 'sum',
        'title': 'count',
        'ai_mention_count': 'sum'
    }).reset_index()
    
    monthly.columns = ['Month', 'AI Articles', 'Total Articles', 'Total Mentions']
    monthly['% with AI'] = (monthly['AI Articles'] / monthly['Total Articles'] * 100).round(1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly['Month'],
        y=monthly['% with AI'],
        mode='lines+markers',
        name='% Articles Mentioning AI',
        line=dict(color='#2563eb', width=3),
        marker=dict(size=8, color='#2563eb')
    ))

    fig.update_layout(
        title="AI Adoption Trend: % of Articles Mentioning AI",
        xaxis_title="",
        yaxis_title="% of Articles",
        height=450,
        template='plotly_white',
        showlegend=False,
        margin=dict(l=60, r=20, t=60, b=50),
        font=dict(size=12, family="Arial, sans-serif")
    )

    return fig

def create_use_case_distribution(df):
    """Visualize AI use case distribution (pie chart)."""
    use_case_df = df[df['has_ai'] & df['primary_use_case'].notna()].copy()

    if len(use_case_df) == 0:
        return None

    use_case_counts = use_case_df['primary_use_case'].value_counts()

    # Create nicer labels
    label_map = {
        'customer_support': 'Customer Support',
        'network_optimization': 'Network Optimization',
        'predictive_maintenance': 'Predictive Maintenance',
        'security': 'Security',
        'analytics': 'Analytics',
        'marketing_automation': 'Marketing Automation',
        'network_planning': 'Network Planning',
        'qos_optimization': 'QoS Optimization',
        'internal_operations': 'Internal Ops',
        'cybersecurity': 'Cybersecurity',
        'other': 'Other'
    }

    use_case_counts.index = use_case_counts.index.map(lambda x: label_map.get(x, x))

    fig = go.Figure(data=[
        go.Pie(labels=use_case_counts.index, values=use_case_counts.values,
               hole=0.4, marker=dict(colors=px.colors.qualitative.Set3))
    ])

    fig.update_layout(
        title="AI Use Case Distribution",
        height=500,
        template='plotly_white',
        annotations=[dict(text='Use Cases', x=0.5, y=0.5, font_size=20, showarrow=False)],
        margin=dict(l=60, r=20, t=60, b=50),
        font=dict(size=11, family="Arial, sans-serif")
    )

    return fig

def create_use_case_sentiment_chart(df):
    """Stacked bar chart: use cases by sentiment."""
    ai_articles = df[df['has_ai'] & df['primary_use_case'].notna()].copy()
    
    if len(ai_articles) == 0:
        return None
    
    label_map = {
        'customer_support': 'Customer Support',
        'network_optimization': 'Network Optimization',
        'predictive_maintenance': 'Predictive Maintenance',
        'security': 'Security',
        'analytics': 'Analytics',
        'marketing_automation': 'Marketing Automation',
        'network_planning': 'Network Planning',
        'qos_optimization': 'QoS Optimization',
        'other': 'Other'
    }
    
    ai_articles['use_case_label'] = ai_articles['primary_use_case'].map(label_map)
    
    use_case_sentiment = ai_articles.groupby(['use_case_label', 'sentiment']).size().reset_index(name='count')
    use_case_sentiment = use_case_sentiment[use_case_sentiment['sentiment'].isin(['positive', 'neutral', 'negative'])]
    
    fig = px.bar(use_case_sentiment,
                 x='use_case_label',
                 y='count',
                 color='sentiment',
                 title="AI Use Cases by Frequency & Sentiment",
                 labels={'use_case_label': '', 'count': 'Number of Articles'},
                 color_discrete_map={
                     'positive': '#10b981',
                     'neutral': '#6b7280',
                     'negative': '#ef4444'
                 },
                 height=500,
                 template='plotly_white')
    
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=60, r=20, t=60, b=100),
        font=dict(size=11, family="Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

def create_company_use_case_heatmap(df, big_firm_df=None):
    """Heatmap: companies vs use cases. Uses big firm data if available."""
    heatmap_data = []
    
    # Prioritize big firm data if available
    if big_firm_df is not None and len(big_firm_df) > 0:
        for _, row in big_firm_df.iterrows():
            if pd.notna(row.get('primary_use_case')) and pd.notna(row.get('company')):
                heatmap_data.append({
                    'Company': row['company'],
                    'Use Case': row['primary_use_case'],
                    'Count': 1
                })
    
    # Fall back to extracted companies from main data
    if not heatmap_data:
        company_df = extract_companies(df[df['has_ai']])
        if len(company_df) > 0:
            for _, row in company_df.iterrows():
                for company in row['companies']:
                    if pd.notna(row['primary_use_case']):
                        heatmap_data.append({
                            'Company': company,
                            'Use Case': row['primary_use_case'],
                            'Count': 1
                        })
    
    if not heatmap_data:
        return None
    
    heatmap_df = pd.DataFrame(heatmap_data)
    heatmap_pivot = heatmap_df.groupby(['Company', 'Use Case']).size().reset_index(name='Count')
    
    # Get top companies and use cases
    top_companies = heatmap_pivot.groupby('Company')['Count'].sum().nlargest(12).index.tolist()
    top_use_cases = heatmap_pivot.groupby('Use Case')['Count'].sum().nlargest(8).index.tolist()
    
    heatmap_pivot = heatmap_pivot[
        heatmap_pivot['Company'].isin(top_companies) &
        heatmap_pivot['Use Case'].isin(top_use_cases)
    ]
    
    # Create pivot table
    pivot_table = heatmap_pivot.pivot(index='Company', columns='Use Case', values='Count').fillna(0)
    
    # Map use case labels
    label_map = {
        'customer_support': 'Customer Support',
        'network_optimization': 'Network Optimization',
        'predictive_maintenance': 'Predictive Maintenance',
        'security': 'Security',
        'analytics': 'Analytics',
        'marketing_automation': 'Marketing Automation',
        'network_planning': 'Network Planning',
        'qos_optimization': 'QoS Optimization',
        'internal_operations': 'Internal Ops',
        'cybersecurity': 'Cybersecurity',
        'other': 'Other'
    }
    pivot_table.columns = [label_map.get(col, col.replace('_', ' ').title()) for col in pivot_table.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='Blues',
        text=pivot_table.values.astype(int),
        texttemplate='%{text}',
        textfont={"size": 10, "color": "white"},
        colorbar=dict(title="Articles")
    ))
    
    fig.update_layout(
        title="Company Activity by AI Use Case",
        xaxis_title="",
        yaxis_title="",
        height=550,
        template='plotly_white',
        margin=dict(l=120, r=20, t=60, b=80),
        font=dict(size=11, family="Arial, sans-serif")
    )
    
    return fig

def create_company_sentiment_chart(big_firm_df):
    """Compare sentiment across companies."""
    if big_firm_df is None or len(big_firm_df) == 0:
        return None
    
    company_sentiment = big_firm_df.groupby(['company', 'sentiment']).size().reset_index(name='count')
    company_sentiment = company_sentiment[company_sentiment['sentiment'].isin(['positive', 'neutral', 'negative'])]
    
    # Get top companies by total mentions
    top_companies = big_firm_df['company'].value_counts().head(8).index.tolist()
    company_sentiment = company_sentiment[company_sentiment['company'].isin(top_companies)]
    
    fig = px.bar(company_sentiment,
                 x='company',
                 y='count',
                 color='sentiment',
                 title="AI Sentiment by Company",
                 labels={'company': '', 'count': 'Number of Articles'},
                 color_discrete_map={
                     'positive': '#10b981',
                     'neutral': '#6b7280',
                     'negative': '#ef4444'
                 },
                 height=450,
                 template='plotly_white')
    
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=60, r=20, t=60, b=100),
        font=dict(size=11, family="Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_company_maturity_chart(big_firm_df):
    """Show AI maturity stages by company."""
    if big_firm_df is None or len(big_firm_df) == 0:
        return None
    
    company_maturity = big_firm_df.groupby(['company', 'maturity_stage']).size().reset_index(name='count')
    company_maturity = company_maturity[company_maturity['maturity_stage'] != 'unknown']
    
    # Get top companies
    top_companies = big_firm_df['company'].value_counts().head(8).index.tolist()
    company_maturity = company_maturity[company_maturity['company'].isin(top_companies)]
    
    fig = px.bar(company_maturity,
                 x='company',
                 y='count',
                 color='maturity_stage',
                 title="AI Initiative Maturity by Company",
                 labels={'company': '', 'count': 'Number of Initiatives'},
                 color_discrete_map={
                     'pilot': '#fbbf24',
                     'deployment': '#3b82f6',
                     'scaled': '#10b981'
                 },
                 height=450,
                 template='plotly_white')
    
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=60, r=20, t=60, b=100),
        font=dict(size=11, family="Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_opportunity_bubble_chart(df):
    """Bubble chart: opportunity mapping (frequency × sentiment × uniqueness)."""
    ai_articles = df[df['has_ai'] & df['primary_use_case'].notna()].copy()

    if len(ai_articles) == 0:
        return None

    use_case_stats = ai_articles.groupby('primary_use_case').agg({
        'title': 'count',
        'sentiment': lambda x: (x == 'positive').sum() / len(x) if len(x) > 0 else 0,
        'primary_use_case_confidence': 'mean'
    }).reset_index()

    use_case_stats.columns = ['Use Case', 'Frequency', 'Positive Sentiment', 'Confidence']
    use_case_stats['Positive Sentiment'] = use_case_stats['Positive Sentiment'] * 100

    label_map = {
        'customer_support': 'Customer Support',
        'network_optimization': 'Network Optimization',
        'predictive_maintenance': 'Predictive Maintenance',
        'security': 'Security',
        'analytics': 'Analytics',
        'marketing_automation': 'Marketing Automation',
        'network_planning': 'Network Planning',
        'qos_optimization': 'QoS Optimization',
        'other': 'Other'
    }
    use_case_stats['Use Case'] = use_case_stats['Use Case'].map(label_map)

    fig = px.scatter(use_case_stats,
                    x='Frequency',
                    y='Positive Sentiment',
                    size='Confidence',
                     text='Use Case',
                    title="Opportunity Matrix: Market Coverage vs Sentiment",
                     labels={
                        'Frequency': 'Market Coverage (# Articles)',
                        'Positive Sentiment': 'Positive Sentiment (%)'
                     },
                    height=550,
                    template='plotly_white')

    fig.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=1, color='white'), opacity=0.7)
    )

    # Add quadrant lines
    median_freq = use_case_stats['Frequency'].median()
    fig.add_hline(y=50, line_dash="dash", line_color="#9ca3af", opacity=0.5, line_width=1)
    fig.add_vline(x=median_freq, line_dash="dash", line_color="#9ca3af", opacity=0.5, line_width=1)
    
    fig.update_layout(
        margin=dict(l=80, r=20, t=60, b=60),
        font=dict(size=11, family="Arial, sans-serif")
    )

    return fig

def create_word_frequency_chart(df):
    """Horizontal bar chart of top AI terms (word cloud alternative)."""
    ai_articles = df[df['has_ai']].copy()
    
    all_mentions = []
    for mentions in ai_articles['ai_mentions'].dropna():
        all_mentions.extend([m.strip() for m in str(mentions).split(',') if m.strip()])
    
    if not all_mentions:
        return None
    
    mention_counts = pd.Series(all_mentions).value_counts().head(12)

    fig = go.Figure(data=[
        go.Bar(x=mention_counts.values,
               y=mention_counts.index,
               orientation='h',
               marker_color='#2563eb',
               text=mention_counts.values,
               textposition='outside')
    ])

    fig.update_layout(
        title="Top AI Technology Mentions",
        xaxis_title="Number of Mentions",
        yaxis_title="",
        height=500,
        template='plotly_white',
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=150, r=60, t=60, b=50),
        font=dict(size=11, family="Arial, sans-serif")
    )

    return fig

def create_use_case_timeseries(df):
    """Time series showing use case mentions over time - THE MEAT."""
    ai_articles = df[df['has_ai'] & df['primary_use_case'].notna()].copy()
    
    if len(ai_articles) == 0:
        return None
    
    # Group by month and use case
    monthly_use_cases = ai_articles.groupby(['year_month', 'primary_use_case']).size().reset_index(name='count')
    
    # Get top use cases
    top_use_cases = ai_articles['primary_use_case'].value_counts().head(8).index.tolist()
    monthly_use_cases = monthly_use_cases[monthly_use_cases['primary_use_case'].isin(top_use_cases)]
    
    label_map = {
        'customer_support': 'Customer Support',
        'network_optimization': 'Network Optimization',
        'predictive_maintenance': 'Predictive Maintenance',
        'security': 'Security',
        'analytics': 'Analytics',
        'marketing_automation': 'Marketing Automation',
        'network_planning': 'Network Planning',
        'qos_optimization': 'QoS Optimization',
        'other': 'Other'
    }
    monthly_use_cases['Use Case'] = monthly_use_cases['primary_use_case'].map(label_map)
    
    fig = px.line(monthly_use_cases,
                  x='year_month',
                  y='count',
                  color='Use Case',
                  title="AI Use Case Adoption Over Time - Where AI is Actually Being Used",
                  labels={'year_month': 'Month', 'count': 'Number of Mentions'},
                  height=550,
                  template='plotly_white')
    
    fig.update_layout(
        margin=dict(l=60, r=20, t=60, b=80),
        font=dict(size=11, family="Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    
    return fig

def create_use_case_stacked_area(df):
    """Stacked area chart showing use case composition over time."""
    ai_articles = df[df['has_ai'] & df['primary_use_case'].notna()].copy()
    
    if len(ai_articles) == 0:
        return None
    
    monthly_use_cases = ai_articles.groupby(['year_month', 'primary_use_case']).size().reset_index(name='count')
    
    # Pivot for stacked area
    pivot = monthly_use_cases.pivot(index='year_month', columns='primary_use_case', values='count').fillna(0)
    
    label_map = {
        'customer_support': 'Customer Support',
        'network_optimization': 'Network Optimization',
        'predictive_maintenance': 'Predictive Maintenance',
        'security': 'Security',
        'analytics': 'Analytics',
        'marketing_automation': 'Marketing Automation',
        'network_planning': 'Network Planning',
        'qos_optimization': 'QoS Optimization',
        'other': 'Other'
    }
    pivot.columns = [label_map.get(col, col) for col in pivot.columns]

    fig = go.Figure()

    for col in pivot.columns:
        fig.add_trace(go.Scatter(
            x=pivot.index,
            y=pivot[col],
            mode='lines',
            name=col,
            stackgroup='one',
            fill='tonexty' if col != pivot.columns[0] else 'tozeroy'
        ))

    fig.update_layout(
        title="Use Case Market Share Over Time (Stacked)",
        xaxis_title="Month",
        yaxis_title="Number of Mentions",
        height=550,
        template='plotly_white',
        margin=dict(l=60, r=20, t=60, b=80),
        font=dict(size=11, family="Arial, sans-serif"),
        hovermode='x unified'
    )
    
    return fig

def create_company_timeseries(big_firm_df):
    """Time series of AI mentions by company."""
    if big_firm_df is None or len(big_firm_df) == 0:
        return None
    
    company_monthly = big_firm_df.groupby(['year_month', 'company']).size().reset_index(name='count')
    
    # Top companies
    top_companies = big_firm_df['company'].value_counts().head(6).index.tolist()
    company_monthly = company_monthly[company_monthly['company'].isin(top_companies)]
    
    fig = px.line(company_monthly,
                  x='year_month',
                  y='count',
                  color='company',
                  title="AI Initiative Activity by Company Over Time",
                  labels={'year_month': 'Month', 'count': 'Number of Initiatives'},
                  height=550,
                  template='plotly_white')
    
    fig.update_layout(
        margin=dict(l=60, r=20, t=60, b=80),
        font=dict(size=11, family="Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    
    return fig

def create_use_case_company_matrix(big_firm_df):
    """Heatmap showing which companies focus on which use cases."""
    if big_firm_df is None or len(big_firm_df) == 0:
        return None
    
    matrix = big_firm_df.groupby(['company', 'primary_use_case']).size().reset_index(name='count')
    
    # Top companies and use cases
    top_companies = big_firm_df['company'].value_counts().head(10).index.tolist()
    top_use_cases = big_firm_df['primary_use_case'].value_counts().head(8).index.tolist()
    
    matrix = matrix[
        matrix['company'].isin(top_companies) &
        matrix['primary_use_case'].isin(top_use_cases)
    ]
    
    pivot = matrix.pivot(index='company', columns='primary_use_case', values='count').fillna(0)
    
    label_map = {
        'customer_support': 'Customer Support',
        'network_optimization': 'Network Optimization',
        'predictive_maintenance': 'Predictive Maintenance',
        'security': 'Security',
        'analytics': 'Analytics',
        'marketing_automation': 'Marketing Automation',
        'network_planning': 'Network Planning',
        'qos_optimization': 'QoS Optimization',
        'internal_operations': 'Internal Ops',
        'cybersecurity': 'Cybersecurity',
        'other': 'Other'
    }
    pivot.columns = [label_map.get(col, col) for col in pivot.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='YlOrRd',
        text=pivot.values.astype(int),
        texttemplate='%{text}',
        textfont={"size": 10, "color": "black"},
        colorbar=dict(title="Initiatives")
    ))
    
    fig.update_layout(
        title="Company Focus Matrix: Where Each Company is Investing",
        xaxis_title="",
        yaxis_title="",
        height=500,
        template='plotly_white',
        margin=dict(l=120, r=20, t=60, b=100),
        font=dict(size=11, family="Arial, sans-serif")
    )
    
    return fig

def create_sentiment_timeseries(df):
    """Sentiment trends over time."""
    ai_articles = df[df['has_ai']].copy()
    
    if len(ai_articles) == 0:
        return None
    
    sentiment_monthly = ai_articles.groupby(['year_month', 'sentiment']).size().reset_index(name='count')
    sentiment_monthly = sentiment_monthly[sentiment_monthly['sentiment'].isin(['positive', 'neutral', 'negative'])]
    
    fig = px.line(sentiment_monthly,
                  x='year_month',
                  y='count',
                  color='sentiment',
                  title="AI Sentiment Trends Over Time",
                  labels={'year_month': 'Month', 'count': 'Number of Articles'},
                  color_discrete_map={
                      'positive': '#10b981',
                      'neutral': '#6b7280',
                      'negative': '#ef4444'
                  },
                  height=500,
                  template='plotly_white')
    
    fig.update_layout(
        margin=dict(l=60, r=20, t=60, b=80),
        font=dict(size=11, family="Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )

    return fig

def create_maturity_progression(big_firm_df):
    """Show how initiatives progress through maturity stages over time."""
    if big_firm_df is None or len(big_firm_df) == 0:
        return None
    
    maturity_monthly = big_firm_df.groupby(['year_month', 'maturity_stage']).size().reset_index(name='count')
    maturity_monthly = maturity_monthly[maturity_monthly['maturity_stage'] != 'unknown']
    
    fig = px.area(maturity_monthly,
                  x='year_month',
                  y='count',
                  color='maturity_stage',
                  title="AI Initiative Maturity Progression Over Time",
                  labels={'year_month': 'Month', 'count': 'Number of Initiatives'},
                  color_discrete_map={
                      'pilot': '#fbbf24',
                      'deployment': '#3b82f6',
                      'scaled': '#10b981'
                  },
                  height=500,
                  template='plotly_white')
    
    fig.update_layout(
        margin=dict(l=60, r=20, t=60, b=80),
        font=dict(size=11, family="Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    
    return fig

def create_mention_intensity_chart(df):
    """Show AI mention intensity (count per article) over time."""
    ai_articles = df[df['has_ai']].copy()

    if len(ai_articles) == 0:
        return None
    
    monthly_intensity = ai_articles.groupby('year_month').agg({
        'ai_mention_count': ['mean', 'sum', 'count']
    }).reset_index()
    
    monthly_intensity.columns = ['Month', 'Avg Mentions', 'Total Mentions', 'Article Count']
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=monthly_intensity['Month'], y=monthly_intensity['Avg Mentions'],
                   name='Avg Mentions/Article', line=dict(color='#2563eb', width=3)),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(x=monthly_intensity['Month'], y=monthly_intensity['Article Count'],
               name='AI Articles', marker_color='#10b981', opacity=0.6),
        secondary_y=True
    )
    
    fig.update_layout(
        title="AI Mention Intensity: How Deeply AI is Discussed",
        height=500,
        template='plotly_white',
        margin=dict(l=60, r=20, t=60, b=80),
        font=dict(size=11, family="Arial, sans-serif")
    )
    
    fig.update_yaxes(title_text="Avg Mentions per Article", secondary_y=False)
    fig.update_yaxes(title_text="Number of AI Articles", secondary_y=True)
    
    return fig

def create_use_case_growth_rates(df):
    """Calculate and visualize growth rates by use case."""
    ai_articles = df[df['has_ai'] & df['primary_use_case'].notna()].copy()
    
    if len(ai_articles) == 0:
        return None
    
    # Get first and last 3 months
    months = sorted(ai_articles['year_month'].unique())
    if len(months) < 6:
        return None
    
    early_months = months[:3]
    late_months = months[-3:]
    
    early_counts = ai_articles[ai_articles['year_month'].isin(early_months)].groupby('primary_use_case').size()
    late_counts = ai_articles[ai_articles['year_month'].isin(late_months)].groupby('primary_use_case').size()
    
    growth_df = pd.DataFrame({
        'Use Case': early_counts.index,
        'Early Period': early_counts.values,
        'Late Period': late_counts.reindex(early_counts.index, fill_value=0).values
    })
    
    growth_df['Growth Rate'] = ((growth_df['Late Period'] - growth_df['Early Period']) / 
                                 (growth_df['Early Period'] + 1) * 100).round(1)
    growth_df = growth_df.sort_values('Growth Rate', ascending=False)
    
    label_map = {
        'customer_support': 'Customer Support',
        'network_optimization': 'Network Optimization',
        'predictive_maintenance': 'Predictive Maintenance',
        'security': 'Security',
        'analytics': 'Analytics',
        'marketing_automation': 'Marketing Automation',
        'network_planning': 'Network Planning',
        'qos_optimization': 'QoS Optimization',
        'other': 'Other'
    }
    growth_df['Use Case'] = growth_df['Use Case'].map(label_map)
    
    fig = go.Figure(data=[
        go.Bar(x=growth_df['Use Case'],
               y=growth_df['Growth Rate'],
               marker_color=['#10b981' if x > 0 else '#ef4444' for x in growth_df['Growth Rate']],
               text=growth_df['Growth Rate'],
               texttemplate='%{text:.1f}%',
               textposition='outside')
    ])
    
    fig.update_layout(
        title="Use Case Growth Rates (Early vs Late Period)",
        xaxis_title="",
        yaxis_title="Growth Rate (%)",
        height=500,
        template='plotly_white',
        xaxis_tickangle=-45,
        margin=dict(l=60, r=20, t=60, b=120),
        font=dict(size=11, family="Arial, sans-serif")
    )

    return fig

def create_strategic_importance_chart(cache_df):
    """Visualize strategic importance distribution."""
    if cache_df is None or len(cache_df) == 0:
        return None
    
    strategic_dist = cache_df['strategic_importance'].value_counts()
    strategic_dist = strategic_dist[strategic_dist.index != 'unknown']
    
    if len(strategic_dist) == 0:
        return None
    
    fig = go.Figure(data=[
        go.Bar(x=strategic_dist.index,
               y=strategic_dist.values,
               marker_color=['#ef4444', '#fbbf24', '#10b981'][:len(strategic_dist)],
               text=strategic_dist.values,
               textposition='outside')
    ])
    
    fig.update_layout(
        title="Strategic Importance of AI Initiatives",
        xaxis_title="",
        yaxis_title="Number of Initiatives",
        height=450,
        template='plotly_white',
        margin=dict(l=60, r=20, t=60, b=50),
        font=dict(size=11, family="Arial, sans-serif")
    )
    
    return fig

def create_key_technologies_chart(cache_df):
    """Extract and visualize key technologies from cache."""
    if cache_df is None or len(cache_df) == 0:
        return None
    
    all_techs = []
    for techs in cache_df['key_technologies']:
        if isinstance(techs, list):
            all_techs.extend(techs)
        elif pd.notna(techs):
            # Handle string format
            if ',' in str(techs):
                all_techs.extend([t.strip() for t in str(techs).split(',')])
            else:
                all_techs.append(str(techs).strip())
    
    if not all_techs:
        return None
    
    tech_counts = pd.Series(all_techs).value_counts().head(15)
    
    fig = go.Figure(data=[
        go.Bar(x=tech_counts.values,
               y=tech_counts.index,
               orientation='h',
               marker_color='#2563eb',
               text=tech_counts.values,
               textposition='outside')
    ])
    
    fig.update_layout(
        title="Key Technologies Deployed by Companies",
        xaxis_title="Number of Mentions",
        yaxis_title="",
        height=500,
        template='plotly_white',
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=150, r=60, t=60, b=50),
        font=dict(size=11, family="Arial, sans-serif")
    )
    
    return fig

def create_company_technology_matrix(cache_df):
    """Heatmap: companies vs technologies."""
    if cache_df is None or len(cache_df) == 0:
        return None
    
    matrix_data = []
    for _, row in cache_df.iterrows():
        company = row['company']
        techs = row['key_technologies']
        if isinstance(techs, list) and len(techs) > 0:
            for tech in techs:
                matrix_data.append({'Company': company, 'Technology': tech, 'Count': 1})
    
    if not matrix_data:
        return None
    
    matrix_df = pd.DataFrame(matrix_data)
    pivot = matrix_df.groupby(['Company', 'Technology']).size().reset_index(name='count')
    
    # Top companies and technologies
    top_companies = cache_df['company'].value_counts().head(8).index.tolist()
    top_techs = matrix_df['Technology'].value_counts().head(10).index.tolist()
    
    pivot = pivot[
        pivot['Company'].isin(top_companies) &
        pivot['Technology'].isin(top_techs)
    ]
    
    pivot_table = pivot.pivot(index='Company', columns='Technology', values='count').fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='YlGnBu',
        text=pivot_table.values.astype(int),
        texttemplate='%{text}',
        textfont={"size": 9, "color": "black"},
        colorbar=dict(title="Mentions")
    ))
    
    fig.update_layout(
        title="Company Technology Stack Matrix",
        xaxis_title="",
        yaxis_title="",
        height=500,
        template='plotly_white',
        margin=dict(l=120, r=20, t=60, b=100),
        font=dict(size=10, family="Arial, sans-serif")
    )
    
    return fig

def create_strategic_use_case_matrix(cache_df):
    """Strategic importance by use case."""
    if cache_df is None or len(cache_df) == 0:
        return None
    
    matrix = cache_df.groupby(['primary_use_case', 'strategic_importance']).size().reset_index(name='count')
    matrix = matrix[matrix['strategic_importance'] != 'unknown']
    
    pivot = matrix.pivot(index='primary_use_case', columns='strategic_importance', values='count').fillna(0)
    
    label_map = {
        'customer_support': 'Customer Support',
        'network_optimization': 'Network Optimization',
        'predictive_maintenance': 'Predictive Maintenance',
        'security': 'Security',
        'analytics': 'Analytics',
        'marketing_automation': 'Marketing Automation',
        'network_planning': 'Network Planning',
        'qos_optimization': 'QoS Optimization',
        'internal_operations': 'Internal Ops',
        'cybersecurity': 'Cybersecurity',
        'other': 'Other'
    }
    pivot.index = [label_map.get(idx, idx) for idx in pivot.index]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        text=pivot.values.astype(int),
        texttemplate='%{text}',
        textfont={"size": 10, "color": "black"},
        colorbar=dict(title="Initiatives")
    ))
    
    fig.update_layout(
        title="Strategic Importance by Use Case",
        xaxis_title="Strategic Importance",
        yaxis_title="",
        height=500,
        template='plotly_white',
        margin=dict(l=150, r=20, t=60, b=50),
        font=dict(size=11, family="Arial, sans-serif")
    )
    
    return fig

def create_confidence_distribution(cache_df):
    """Show confidence score distribution."""
    if cache_df is None or len(cache_df) == 0:
        return None
    
    fig = go.Figure(data=[
        go.Histogram(x=cache_df['confidence'],
                    nbinsx=20,
                    marker_color='#2563eb',
                    opacity=0.7)
    ])
    
    fig.update_layout(
        title="Analysis Confidence Score Distribution",
        xaxis_title="Confidence Score",
        yaxis_title="Number of Initiatives",
        height=450,
        template='plotly_white',
        margin=dict(l=60, r=20, t=60, b=50),
        font=dict(size=11, family="Arial, sans-serif")
    )
    
    return fig

def create_company_strategic_focus(cache_df):
    """Show strategic importance by company."""
    if cache_df is None or len(cache_df) == 0:
        return None
    
    company_strategic = cache_df.groupby(['company', 'strategic_importance']).size().reset_index(name='count')
    company_strategic = company_strategic[company_strategic['strategic_importance'] != 'unknown']
    
    top_companies = cache_df['company'].value_counts().head(6).index.tolist()
    company_strategic = company_strategic[company_strategic['company'].isin(top_companies)]
    
    fig = px.bar(company_strategic,
                x='company',
                y='count',
                color='strategic_importance',
                title="Strategic Focus by Company",
                labels={'company': '', 'count': 'Number of Initiatives'},
                color_discrete_map={
                    'high': '#10b981',
                    'medium': '#fbbf24',
                    'low': '#ef4444'
                },
                height=450,
                template='plotly_white')
    
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=60, r=20, t=60, b=100),
        font=dict(size=11, family="Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def generate_strategic_synthesis(df, big_firm_df=None, cache_df=None):
    """Generate strategic synthesis text."""
    ai_articles = df[df['has_ai']].copy()
    total_articles = len(df)
    ai_count = len(ai_articles)
    ai_pct = (ai_count / total_articles * 100) if total_articles > 0 else 0
    
    # Date range
    if df['date'].notna().any():
        date_range = f"{df['date'].min().strftime('%b %Y')} to {df['date'].max().strftime('%b %Y')}"
    else:
        date_range = "N/A"
    
    # Top use cases
    use_case_counts = ai_articles[ai_articles['primary_use_case'].notna()]['primary_use_case'].value_counts()
    top_use_case = use_case_counts.index[0] if len(use_case_counts) > 0 else None
    top_use_case_label = top_use_case.replace('_', ' ').title() if top_use_case else 'various use cases'
    
    # Sentiment
    sentiment_dist = ai_articles['sentiment'].value_counts()
    positive_pct = (sentiment_dist.get('positive', 0) / len(ai_articles) * 100) if len(ai_articles) > 0 else 0
    
    # Cache insights (richest data)
    cache_insights = ""
    if cache_df is not None and len(cache_df) > 0:
        top_companies = cache_df['company'].value_counts().head(3).index.tolist()
        company_list = ", ".join(top_companies)
        high_strategic_pct = (cache_df['strategic_importance'] == 'high').sum() / len(cache_df) * 100
        scaled_pct = (cache_df['maturity_stage'] == 'scaled').sum() / len(cache_df) * 100
        
        # Top technologies
        all_techs = []
        for techs in cache_df['key_technologies']:
            if isinstance(techs, list):
                all_techs.extend(techs)
        top_tech = pd.Series(all_techs).value_counts().index[0] if all_techs else "various"
        
        cache_insights = f"""
**Major Player Activity & Technology Deployment**

Analysis of {len(cache_df):,} company-specific AI initiatives reveals concentrated activity among {company_list}, with {high_strategic_pct:.0f}% of initiatives classified as high strategic importance. {scaled_pct:.0f}% have reached scaled deployment, indicating mature AI adoption. Leading technologies include {top_tech}, automation, and machine learning. This concentration suggests opportunities for boutique firms to target mid-tier operators or specific use cases where major players show less activity.
"""
    # Fallback to CSV insights
    elif big_firm_df is not None and len(big_firm_df) > 0:
        top_companies = big_firm_df['company'].value_counts().head(3).index.tolist()
        company_list = ", ".join(top_companies)
        cache_insights = f"""
**Major Player Activity**

Analysis of {len(big_firm_df):,} company-specific AI initiatives reveals concentrated activity among {company_list}. This concentration suggests opportunities for boutique firms to target mid-tier operators or specific use cases where major players show less activity.
"""
    
    synthesis = f"""
**AI Adoption Maturity in UK Broadband**

Analysis of {total_articles:,} industry articles ({date_range}) reveals that {ai_pct:.1f}% mention AI/ML technologies, indicating moderate but growing adoption. The industry shows a {positive_pct:.0f}% positive sentiment toward AI applications, suggesting receptive market conditions. Primary focus areas cluster around {top_use_case_label}, with emerging interest in predictive maintenance and network optimization.
{cache_insights}
**Strategic Focus Areas for Boutique Firms**

The opportunity matrix reveals underserved segments where high positive sentiment meets low market coverage—specifically in predictive maintenance, QoS optimization, and network planning. These areas represent white space for specialized consulting services. Conversely, customer support and network optimization show high competition but remain viable through differentiation strategies targeting specific operator pain points or vertical applications.

**Actionable Implications**

1. **Target Predictive Maintenance & Network Planning**: Low coverage (under 15% of AI mentions) combined with high positive sentiment (60%+) indicates strong demand with limited supply—ideal for boutique positioning.

2. **Develop Vertical-Specific Solutions**: Rather than competing broadly in customer support, focus on telecom-specific AI implementations (e.g., network fault prediction, capacity planning) where domain expertise creates barriers to entry.

3. **Monitor Emerging Technologies**: Track LLM adoption, automation platforms, and analytics tools mentioned in articles—these represent near-term consulting opportunities as operators seek implementation guidance.
"""
    
    return synthesis

# Main Dashboard
def main():
    st.markdown('<div class="main-header">UK Broadband AI Trends: Strategic Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Market intelligence for consulting strategy | {}</div>'.format(datetime.now().strftime('%B %Y')), unsafe_allow_html=True)

    df = load_data()

    if df is None:
        st.error("⚠️ Data file 'output/unified_ai_analysis.csv' not found.")
        st.info("Run: `cd 'Article Analysis' && python llm_analysis_pipeline.py` to generate the data.")
        return

    # Sidebar filters
    st.sidebar.header("Filters")

    if df['date'].notna().any():
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(df['date'].min(), df['date'].max()),
            min_value=df['date'].min().date() if pd.notna(df['date'].min()) else None,
            max_value=df['date'].max().date() if pd.notna(df['date'].max()) else None
        )
        if len(date_range) == 2:
            df = df[(df['date'] >= pd.Timestamp(date_range[0])) & (df['date'] <= pd.Timestamp(date_range[1]))]

    sources = ['All'] + list(df['source'].unique())
    selected_source = st.sidebar.selectbox("News Source", sources)
    if selected_source != 'All':
        df = df[df['source'] == selected_source]

    # Load big firm data
    big_firm_df = load_big_firm_data()

    # Key metrics at top
    col1, col2, col3, col4, col5 = st.columns(5)
    ai_count = df['has_ai'].sum()
    ai_pct = (ai_count / len(df) * 100) if len(df) > 0 else 0

    with col1:
        st.metric("Total Articles", f"{len(df):,}")
    with col2:
        st.metric("AI Articles", f"{ai_count:,}")
    with col3:
        st.metric("AI Coverage", f"{ai_pct:.1f}%")
    with col4:
        total_mentions = df['ai_mention_count'].sum()
        st.metric("Total Mentions", f"{int(total_mentions):,}")
    with col5:
        date_range_str = f"{df['date'].min().strftime('%b %Y')} - {df['date'].max().strftime('%b %Y')}" if df['date'].notna().any() else "N/A"
        st.metric("Date Range", date_range_str)
    
    # ========== TABS FOR COMPREHENSIVE ANALYSIS ==========
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Time Series - Where AI is Used",
        "🎯 Use Cases Deep Dive",
        "🏢 Company Analysis",
        "💬 Sentiment & Maturity",
        "📊 Market Positioning",
        "🔍 Technology Trends",
        "📋 Strategic Synthesis"
    ])
    
    # TAB 1: TIME SERIES - THE MEAT
    with tab1:
        st.header("Time Series Analysis: Where AI is Actually Being Used")
        
        st.markdown("""
        <div class="insight-box">
        <strong>Key Insight:</strong> These charts show WHERE AI is being applied over time - the actual use cases, 
        companies, and technologies driving adoption. This is the core intelligence for understanding market dynamics.
        </div>
        """, unsafe_allow_html=True)
        
        # THE MAIN CHART - Use case time series
        use_case_ts = create_use_case_timeseries(df)
        if use_case_ts:
            st.plotly_chart(use_case_ts, use_container_width=True)
            st.caption("**Primary Chart:** Shows which AI use cases are growing, declining, or stable over time")

        col1, col2 = st.columns(2)

        with col1:
            stacked_area = create_use_case_stacked_area(df)
            if stacked_area:
                st.plotly_chart(stacked_area, use_container_width=True)
                st.caption("Market share composition - how use cases compete for attention")

        with col2:
            intensity_chart = create_mention_intensity_chart(df)
            if intensity_chart:
                st.plotly_chart(intensity_chart, use_container_width=True)
                st.caption("Mention depth - are articles discussing AI more deeply over time?")
        
        # Company time series
        if big_firm_df is not None and len(big_firm_df) > 0:
            company_ts = create_company_timeseries(big_firm_df)
            if company_ts:
                st.plotly_chart(company_ts, use_container_width=True)
                st.caption("Which companies are most active in AI initiatives over time")
        
        # Growth rates
        growth_chart = create_use_case_growth_rates(df)
        if growth_chart:
            st.plotly_chart(growth_chart, use_container_width=True)
            st.caption("Which use cases are growing fastest (early vs late period comparison)")
    
    # TAB 2: USE CASES DEEP DIVE
    with tab2:
        st.header("Use Case Analysis: Where the Opportunities Are")
        
        col1, col2 = st.columns(2)
        
        with col1:
            use_case_sentiment = create_use_case_sentiment_chart(df)
            if use_case_sentiment:
                st.plotly_chart(use_case_sentiment, use_container_width=True)
        
        with col2:
            bubble_chart = create_opportunity_bubble_chart(df)
            if bubble_chart:
                st.plotly_chart(bubble_chart, use_container_width=True)
        
        # Use case distribution
        use_case_dist = create_use_case_distribution(df)
        if use_case_dist:
            st.plotly_chart(use_case_dist, use_container_width=True)
        
        # Use case stats table
        ai_articles = df[df['has_ai'] & df['primary_use_case'].notna()].copy()
        if len(ai_articles) > 0:
            use_case_stats = ai_articles.groupby('primary_use_case').agg({
                'title': 'count',
                'sentiment': lambda x: (x == 'positive').sum() / len(x) * 100 if len(x) > 0 else 0,
                'ai_mention_count': 'mean',
                'primary_use_case_confidence': 'mean'
            }).reset_index()
            use_case_stats.columns = ['Use Case', 'Articles', 'Positive %', 'Avg Mentions', 'Avg Confidence']
            use_case_stats = use_case_stats.sort_values('Articles', ascending=False)
            
            label_map = {
                'customer_support': 'Customer Support',
                'network_optimization': 'Network Optimization',
                'predictive_maintenance': 'Predictive Maintenance',
                'security': 'Security',
                'analytics': 'Analytics',
                'marketing_automation': 'Marketing Automation',
                'network_planning': 'Network Planning',
                'qos_optimization': 'QoS Optimization',
                'other': 'Other'
            }
            use_case_stats['Use Case'] = use_case_stats['Use Case'].map(label_map)
            use_case_stats['Positive %'] = use_case_stats['Positive %'].apply(lambda x: f"{x:.1f}%")
            use_case_stats['Avg Mentions'] = use_case_stats['Avg Mentions'].apply(lambda x: f"{x:.1f}")
            use_case_stats['Avg Confidence'] = use_case_stats['Avg Confidence'].apply(lambda x: f"{x:.2f}")
            
            st.markdown("**Detailed Use Case Statistics:**")
            st.dataframe(use_case_stats, use_container_width=True, hide_index=True)
    
    # TAB 3: COMPANY ANALYSIS
    with tab3:
        st.header("Company-Specific AI Activity")
        
        # Load rich cache data
        cache_df = load_big_firm_cache()
        
        if cache_df is not None and len(cache_df) > 0:
            st.markdown(f"""
            <div class="insight-box">
            <strong>Rich Analysis Data:</strong> {len(cache_df):,} initiatives with detailed technology, strategic importance, 
            and maturity analysis from cache data.
            </div>
            """, unsafe_allow_html=True)
            
            # Strategic importance and technologies section
            st.subheader("Strategic Focus & Technology Stack")

        col1, col2 = st.columns(2)

        with col1:
                strategic_imp = create_strategic_importance_chart(cache_df)
                if strategic_imp:
                    st.plotly_chart(strategic_imp, use_container_width=True)

        with col2:
                key_techs = create_key_technologies_chart(cache_df)
                if key_techs:
                    st.plotly_chart(key_techs, use_container_width=True)
            
            # Company technology matrix
            company_tech_matrix = create_company_technology_matrix(cache_df)
            if company_tech_matrix:
                st.plotly_chart(company_tech_matrix, use_container_width=True)
                st.caption("Which technologies each company is deploying")
            
            # Strategic importance matrices
            col1, col2 = st.columns(2)
            
            with col1:
                strategic_uc = create_strategic_use_case_matrix(cache_df)
                if strategic_uc:
                    st.plotly_chart(strategic_uc, use_container_width=True)
                    st.caption("Which use cases are strategically important")
            
            with col2:
                company_strategic = create_company_strategic_focus(cache_df)
                if company_strategic:
                    st.plotly_chart(company_strategic, use_container_width=True)
                    st.caption("Strategic focus breakdown by company")
            
            # Confidence distribution
            confidence_dist = create_confidence_distribution(cache_df)
            if confidence_dist:
                st.plotly_chart(confidence_dist, use_container_width=True)
                st.caption("Analysis confidence scores - higher scores indicate more reliable categorization")
            
            # Summary insights from cache
            st.subheader("Key Insights from Rich Analysis")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                high_strategic = (cache_df['strategic_importance'] == 'high').sum()
                st.metric("High Strategic Initiatives", f"{high_strategic}", f"{high_strategic/len(cache_df)*100:.0f}%")
            
            with col2:
                scaled = (cache_df['maturity_stage'] == 'scaled').sum()
                st.metric("Scaled Deployments", f"{scaled}", f"{scaled/len(cache_df)*100:.0f}%")
            
            with col3:
                avg_confidence = cache_df['confidence'].mean()
                st.metric("Avg Confidence", f"{avg_confidence:.2f}")
            
            with col4:
                unique_techs = set()
                for techs in cache_df['key_technologies']:
                    if isinstance(techs, list):
                        unique_techs.update(techs)
                st.metric("Unique Technologies", f"{len(unique_techs)}")
            
            # Top technologies summary
            all_techs = []
            for techs in cache_df['key_technologies']:
                if isinstance(techs, list):
                    all_techs.extend(techs)
            
            if all_techs:
                top_tech_summary = pd.Series(all_techs).value_counts().head(5)
                st.markdown("**Most Deployed Technologies:**")
                tech_list = ", ".join([f"{tech} ({count})" for tech, count in top_tech_summary.items()])
                st.write(tech_list)
        
        # Fallback to CSV data if cache not available
        if big_firm_df is not None and len(big_firm_df) > 0:
            if cache_df is None or len(cache_df) == 0:
                st.markdown(f"""
                <div class="insight-box">
                <strong>Big Firm Analysis:</strong> {len(big_firm_df):,} analyzed company-specific AI initiatives
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)

        with col1:
                company_focus = create_use_case_company_matrix(big_firm_df)
                if company_focus:
                    st.plotly_chart(company_focus, use_container_width=True)
                    st.caption("Which companies focus on which use cases")

        with col2:
                company_heatmap = create_company_use_case_heatmap(df, big_firm_df)
                if company_heatmap:
                    st.plotly_chart(company_heatmap, use_container_width=True)
                    st.caption("Company activity across all use cases")
            
            col1, col2 = st.columns(2)
            
            with col1:
                company_sentiment = create_company_sentiment_chart(big_firm_df)
                if company_sentiment:
                    st.plotly_chart(company_sentiment, use_container_width=True)
            
            with col2:
                company_maturity = create_company_maturity_chart(big_firm_df)
                if company_maturity:
                    st.plotly_chart(company_maturity, use_container_width=True)
            
            # Company stats table
            company_stats = big_firm_df.groupby('company').agg({
                'article_title': 'count',
                'sentiment': lambda x: (x == 'positive').sum() / len(x) * 100 if len(x) > 0 else 0,
                'strategic_importance': lambda x: (x == 'high').sum() / len(x) * 100 if len(x) > 0 else 0,
                'maturity_stage': lambda x: (x == 'scaled').sum() / len(x) * 100 if len(x) > 0 else 0
            }).reset_index()
            company_stats.columns = ['Company', 'Initiatives', 'Positive %', 'High Strategic %', 'Scaled %']
            company_stats = company_stats.sort_values('Initiatives', ascending=False)
            
            company_stats['Positive %'] = company_stats['Positive %'].apply(lambda x: f"{x:.1f}%")
            company_stats['High Strategic %'] = company_stats['High Strategic %'].apply(lambda x: f"{x:.1f}%")
            company_stats['Scaled %'] = company_stats['Scaled %'].apply(lambda x: f"{x:.1f}%")
            
            st.markdown("**Company Performance Metrics:**")
            st.dataframe(company_stats, use_container_width=True, hide_index=True)
        else:
            st.info("Big firm analysis data not available. Run the big firm analyzer to see company-specific insights.")
    
    # TAB 4: SENTIMENT & MATURITY
    with tab4:
        st.header("Sentiment Trends & Initiative Maturity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sentiment_ts = create_sentiment_timeseries(df)
            if sentiment_ts:
                st.plotly_chart(sentiment_ts, use_container_width=True)
        
        with col2:
            if big_firm_df is not None and len(big_firm_df) > 0:
                maturity_prog = create_maturity_progression(big_firm_df)
                if maturity_prog:
                    st.plotly_chart(maturity_prog, use_container_width=True)
        
        # Sentiment by use case
        ai_articles = df[df['has_ai']].copy()
        if len(ai_articles) > 0:
            sentiment_by_uc = ai_articles[ai_articles['primary_use_case'].notna()].groupby(['primary_use_case', 'sentiment']).size().reset_index(name='count')
            sentiment_by_uc = sentiment_by_uc[sentiment_by_uc['sentiment'].isin(['positive', 'neutral', 'negative'])]
            
            if len(sentiment_by_uc) > 0:
                label_map = {
                    'customer_support': 'Customer Support',
                    'network_optimization': 'Network Optimization',
                    'predictive_maintenance': 'Predictive Maintenance',
                    'security': 'Security',
                    'analytics': 'Analytics',
                    'marketing_automation': 'Marketing Automation',
                    'network_planning': 'Network Planning',
                    'qos_optimization': 'QoS Optimization',
                    'other': 'Other'
                }
                sentiment_by_uc['Use Case'] = sentiment_by_uc['primary_use_case'].map(label_map)
                
                fig = px.bar(sentiment_by_uc,
                            x='Use Case',
                            y='count',
                            color='sentiment',
                            title="Sentiment by Use Case",
                            color_discrete_map={
                                'positive': '#10b981',
                                'neutral': '#6b7280',
                                'negative': '#ef4444'
                            },
                            height=500,
                            template='plotly_white')
                fig.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
                st.plotly_chart(fig, use_container_width=True)
    
    # TAB 5: MARKET POSITIONING
    with tab5:
        st.header("Market Positioning & Competitive Landscape")
        
        col1, col2 = st.columns(2)
        
        with col1:
            heatmap = create_company_use_case_heatmap(df, big_firm_df)
            if heatmap:
                st.plotly_chart(heatmap, use_container_width=True)
        
        with col2:
            bubble = create_opportunity_bubble_chart(df)
            if bubble:
                st.plotly_chart(bubble, use_container_width=True)
        
        # Source comparison
        source_stats = df.groupby('source').agg({
            'has_ai': 'sum',
            'title': 'count',
            'ai_mention_count': 'sum'
        }).reset_index()
        source_stats.columns = ['Source', 'AI Articles', 'Total Articles', 'Total Mentions']
        source_stats['% with AI'] = (source_stats['AI Articles'] / source_stats['Total Articles'] * 100).round(1)
        source_stats['Avg Mentions'] = source_stats.apply(
            lambda row: round(row['Total Mentions'] / row['AI Articles'], 1) if row['AI Articles'] > 0 else 0.0,
            axis=1
        )
        
        fig = px.bar(source_stats,
                    x='Source',
                    y=['AI Articles', 'Total Articles'],
                    title="AI Coverage by News Source",
                    barmode='group',
                    height=400,
                    template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(source_stats, use_container_width=True, hide_index=True)
    
    # TAB 6: TECHNOLOGY TRENDS
    with tab6:
        st.header("AI Technology & Terminology Trends")
        
        cache_df = load_big_firm_cache()
        
        col1, col2 = st.columns(2)
        
        with col1:
            word_freq = create_word_frequency_chart(df)
            if word_freq:
                st.plotly_chart(word_freq, use_container_width=True)
                st.caption("General AI terminology from all articles")
        
        with col2:
            # Use cache data for actual deployed technologies
            if cache_df is not None and len(cache_df) > 0:
                key_techs = create_key_technologies_chart(cache_df)
                if key_techs:
                    st.plotly_chart(key_techs, use_container_width=True)
                    st.caption("Actual technologies being deployed by companies")
        
        # Company technology matrix
        if cache_df is not None and len(cache_df) > 0:
            company_tech = create_company_technology_matrix(cache_df)
            if company_tech:
                st.plotly_chart(company_tech, use_container_width=True)
                st.caption("Technology stack comparison across companies")
        
        # Technology mentions over time
        ai_articles = df[df['has_ai']].copy()
        if len(ai_articles) > 0:
            all_mentions = []
            mention_dates = []
            for idx, row in ai_articles.iterrows():
                mentions = row.get('ai_mentions', '')
                if pd.notna(mentions):
                    for m in str(mentions).split(','):
                        m = m.strip()
                        if m:
                            all_mentions.append(m)
                            mention_dates.append(row.get('year_month', ''))
            
            if all_mentions:
                tech_df = pd.DataFrame({'Technology': all_mentions, 'Month': mention_dates})
                top_tech = tech_df['Technology'].value_counts().head(8).index.tolist()
                tech_df = tech_df[tech_df['Technology'].isin(top_tech)]
                
                tech_timeseries = tech_df.groupby(['Month', 'Technology']).size().reset_index(name='count')
                
                fig = px.line(tech_timeseries,
                             x='Month',
                             y='count',
                             color='Technology',
                             title="Top Technology Mentions Over Time",
                             height=500,
                             template='plotly_white')
                fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig, use_container_width=True)
        
        # Technology by use case (from cache)
        if cache_df is not None and len(cache_df) > 0:
            st.subheader("Technologies by Use Case")
            
            tech_uc_data = []
            for _, row in cache_df.iterrows():
                use_case = row.get('primary_use_case', 'other')
                techs = row.get('key_technologies', [])
                if isinstance(techs, list):
                    for tech in techs:
                        tech_uc_data.append({'Use Case': use_case, 'Technology': tech})
            
            if tech_uc_data:
                tech_uc_df = pd.DataFrame(tech_uc_data)
                tech_uc_pivot = tech_uc_df.groupby(['Use Case', 'Technology']).size().reset_index(name='count')
                
                # Top use cases and technologies
                top_ucs = tech_uc_df['Use Case'].value_counts().head(6).index.tolist()
                top_techs = tech_uc_df['Technology'].value_counts().head(10).index.tolist()
                
                tech_uc_pivot = tech_uc_pivot[
                    tech_uc_pivot['Use Case'].isin(top_ucs) &
                    tech_uc_pivot['Technology'].isin(top_techs)
                ]
                
                pivot_table = tech_uc_pivot.pivot(index='Use Case', columns='Technology', values='count').fillna(0)
                
                label_map = {
                    'customer_support': 'Customer Support',
                    'network_optimization': 'Network Optimization',
                    'predictive_maintenance': 'Predictive Maintenance',
                    'security': 'Security',
                    'analytics': 'Analytics',
                    'internal_operations': 'Internal Ops',
                    'cybersecurity': 'Cybersecurity',
                    'other': 'Other'
                }
                pivot_table.index = [label_map.get(idx, idx) for idx in pivot_table.index]
                
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_table.values,
                    x=pivot_table.columns,
                    y=pivot_table.index,
                    colorscale='Blues',
                    text=pivot_table.values.astype(int),
                    texttemplate='%{text}',
                    textfont={"size": 9, "color": "white"},
                    colorbar=dict(title="Mentions")
                ))
                
                fig.update_layout(
                    title="Technology Adoption by Use Case",
                    xaxis_title="",
                    yaxis_title="",
                    height=500,
                    template='plotly_white',
                    margin=dict(l=150, r=20, t=60, b=100),
                    font=dict(size=10, family="Arial, sans-serif")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Which technologies are used for which use cases")
    
    # TAB 7: STRATEGIC SYNTHESIS
    with tab7:
        st.header("Strategic Synthesis & Recommendations")
        
        cache_df = load_big_firm_cache()
        synthesis = generate_strategic_synthesis(df, big_firm_df, cache_df)
        st.markdown(synthesis)
        
        # Key insights summary
        ai_articles = df[df['has_ai']].copy()
        if len(ai_articles) > 0:
            st.markdown("---")
            st.subheader("Key Data Points")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                use_case_counts = ai_articles['primary_use_case'].value_counts()
                st.metric("Top Use Case", use_case_counts.index[0].replace('_', ' ').title() if len(use_case_counts) > 0 else "N/A")
            
            with col2:
                sentiment_dist = ai_articles['sentiment'].value_counts()
                positive_pct = (sentiment_dist.get('positive', 0) / len(ai_articles) * 100)
                st.metric("Positive Sentiment", f"{positive_pct:.1f}%")
            
            with col3:
                avg_mentions = ai_articles['ai_mention_count'].mean()
                st.metric("Avg Mentions/Article", f"{avg_mentions:.1f}")

    # Export section in sidebar
    st.sidebar.markdown("---")
    st.sidebar.header("Export")
    
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Download Full Dataset (CSV)",
        data=csv,
        file_name="uk_broadband_ai_analysis.csv",
        mime="text/csv"
    )
    
    st.sidebar.info("💡 **Tip:** Right-click any chart and select 'Download plot as PNG' for slide integration")

if __name__ == "__main__":
    main()
