"""
Streamlit Dashboard for UK Broadband AI Trends Analysis

Visualizes AI adoption trends in the UK broadband/telecom industry
to identify market opportunities and track AI technology mentions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="UK Broadband AI Trends Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff7f0e;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(csv_path="output/unified_ai_analysis.csv"):
    """Load and preprocess the analysis data."""
    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)

    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Add derived columns
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['has_ai'] = df['ai_mention_count'] > 0
    df['has_title_ai'] = df['title_ai_mention_count'] > 0

    return df

def create_time_series_chart(df):
    """Create time series visualization of AI mentions."""
    # Group by month
    monthly = df.groupby('year_month').agg({
        'has_ai': 'sum',
        'title': 'count',
        'ai_mention_count': 'sum'
    }).reset_index()

    monthly.columns = ['Month', 'AI Articles', 'Total Articles', 'Total AI Mentions']
    monthly['% with AI'] = (monthly['AI Articles'] / monthly['Total Articles'] * 100).round(1)

    # Create dual-axis chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=monthly['Month'], y=monthly['AI Articles'],
               name='AI Articles', marker_color='#1f77b4'),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=monthly['Month'], y=monthly['% with AI'],
                   name='% with AI', mode='lines+markers',
                   line=dict(color='#ff7f0e', width=3),
                   marker=dict(size=8)),
        secondary_y=True
    )

    fig.update_layout(
        title="AI Adoption Trend Over Time",
        xaxis_title="Month",
        height=500,
        hovermode='x unified'
    )

    fig.update_yaxes(title_text="Number of AI Articles", secondary_y=False)
    fig.update_yaxes(title_text="% Articles Mentioning AI", secondary_y=True)

    return fig

def create_keyword_frequency_chart(df):
    """Analyze which AI keywords are mentioned most."""
    ai_articles = df[df['has_ai']].copy()

    # Extract all AI mentions
    all_mentions = []
    for mentions in ai_articles['ai_mentions'].dropna():
        all_mentions.extend([m.strip() for m in str(mentions).split(',') if m.strip()])

    # Count frequencies
    mention_counts = pd.Series(all_mentions).value_counts().head(15)

    fig = go.Figure(data=[
        go.Bar(x=mention_counts.values, y=mention_counts.index,
               orientation='h', marker_color='#2ca02c')
    ])

    fig.update_layout(
        title="Top 15 AI Technology Mentions",
        xaxis_title="Number of Mentions",
        yaxis_title="Technology/Term",
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )

    return fig

def create_use_case_distribution(df):
    """Visualize AI use case distribution."""
    use_case_df = df[df['primary_use_case'].notna()].copy()

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
        annotations=[dict(text='Use Cases', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )

    return fig

def create_sentiment_analysis(df):
    """Analyze sentiment toward AI over time."""
    ai_articles = df[df['has_ai']].copy()

    sentiment_over_time = ai_articles.groupby(['year_month', 'sentiment']).size().reset_index(name='count')

    fig = px.bar(sentiment_over_time, x='year_month', y='count', color='sentiment',
                 title="AI Sentiment Over Time",
                 labels={'year_month': 'Month', 'count': 'Number of Articles'},
                 color_discrete_map={
                     'positive': '#2ca02c',
                     'neutral': '#7f7f7f',
                     'negative': '#d62728',
                     'mixed': '#ff7f0e',
                     'not_applicable': '#bcbd22'
                 },
                 height=500)

    return fig

def create_opportunity_matrix(df):
    """Identify underserved AI use cases (opportunities)."""
    ai_articles = df[df['has_ai']].copy()

    if len(ai_articles) == 0:
        return None

    # Calculate use case prevalence and sentiment
    use_case_stats = ai_articles.groupby('primary_use_case').agg({
        'title': 'count',
        'sentiment': lambda x: (x == 'positive').sum() / len(x) if len(x) > 0 else 0,
        'primary_use_case_confidence': 'mean'
    }).reset_index()

    use_case_stats.columns = ['Use Case', 'Article Count', 'Positive Sentiment %', 'Avg Confidence']
    use_case_stats['Positive Sentiment %'] = (use_case_stats['Positive Sentiment %'] * 100).round(1)

    # Map to readable names
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
    use_case_stats['Use Case'] = use_case_stats['Use Case'].map(lambda x: label_map.get(x, x))

    # Opportunity = Low coverage + High positive sentiment
    fig = px.scatter(use_case_stats,
                     x='Article Count',
                     y='Positive Sentiment %',
                     size='Avg Confidence',
                     text='Use Case',
                     title="AI Use Case Opportunity Matrix",
                     labels={
                         'Article Count': 'Market Coverage (# Articles)',
                         'Positive Sentiment %': 'Positive Sentiment (%)'
                     },
                     height=600)

    fig.update_traces(textposition='top center')

    # Add quadrant lines
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=use_case_stats['Article Count'].median(), line_dash="dash", line_color="gray", opacity=0.5)

    # Add annotations for quadrants
    fig.add_annotation(x=use_case_stats['Article Count'].max() * 0.9, y=95,
                      text="High Coverage<br>High Sentiment", showarrow=False,
                      bgcolor="rgba(46, 160, 44, 0.2)", bordercolor="green")

    fig.add_annotation(x=use_case_stats['Article Count'].min() * 1.1, y=95,
                      text="🎯 Opportunity Zone<br>Low Coverage + High Sentiment",
                      showarrow=False,
                      bgcolor="rgba(255, 127, 14, 0.2)", bordercolor="orange")

    return fig

def create_source_comparison(df):
    """Compare AI coverage across news sources."""
    source_stats = df.groupby('source').agg({
        'has_ai': 'sum',
        'title': 'count'
    }).reset_index()

    source_stats.columns = ['Source', 'AI Articles', 'Total Articles']
    source_stats['% with AI'] = (source_stats['AI Articles'] / source_stats['Total Articles'] * 100).round(1)

    fig = go.Figure(data=[
        go.Bar(name='Total Articles', x=source_stats['Source'], y=source_stats['Total Articles'],
               marker_color='lightblue'),
        go.Bar(name='AI Articles', x=source_stats['Source'], y=source_stats['AI Articles'],
               marker_color='#1f77b4')
    ])

    fig.update_layout(
        title="AI Coverage by News Source",
        xaxis_title="Source",
        yaxis_title="Number of Articles",
        barmode='group',
        height=400
    )

    return fig

def create_adoption_trend_chart(df):
    """Show industry AI adoption trend with trendline."""
    monthly = df.groupby('year_month').agg({
        'has_ai': 'sum',
        'title': 'count'
    }).reset_index()

    monthly['% with AI'] = (monthly['has_ai'] / monthly['title'] * 100).round(1)
    monthly['month_index'] = range(len(monthly))

    # Calculate trend
    from numpy import polyfit, poly1d
    if len(monthly) >= 3:
        z = polyfit(monthly['month_index'], monthly['% with AI'], 1)
        p = poly1d(z)
        monthly['trend'] = p(monthly['month_index'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly['year_month'],
        y=monthly['% with AI'],
        mode='lines+markers',
        name='Actual % with AI',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))

    if 'trend' in monthly.columns:
        fig.add_trace(go.Scatter(
            x=monthly['year_month'],
            y=monthly['trend'],
            mode='lines',
            name='Trend',
            line=dict(color='red', width=2, dash='dash')
        ))

    fig.update_layout(
        title="AI Adoption Trend in UK Broadband Industry",
        xaxis_title="Month",
        yaxis_title="% of Articles Mentioning AI",
        height=500,
        hovermode='x unified'
    )

    return fig

def create_title_vs_content_analysis(df):
    """Compare AI mentions in titles vs full content."""
    ai_articles = df[df['has_ai']].copy()

    title_vs_content = pd.DataFrame({
        'Category': ['Title Only', 'Content Only', 'Both Title & Content'],
        'Count': [
            len(ai_articles[ai_articles['has_title_ai'] & (ai_articles['ai_mention_count'] == ai_articles['title_ai_mention_count'])]),
            len(ai_articles[~ai_articles['has_title_ai'] & (ai_articles['ai_mention_count'] > 0)]),
            len(ai_articles[ai_articles['has_title_ai'] & (ai_articles['ai_mention_count'] > ai_articles['title_ai_mention_count'])])
        ]
    })

    fig = px.bar(title_vs_content, x='Category', y='Count',
                 title="AI Mention Prominence: Title vs Content",
                 color='Count',
                 color_continuous_scale='Blues',
                 height=400)

    return fig

# Main Dashboard
def main():
    st.markdown('<div class="main-header">UK Broadband AI Trends Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Analyzing AI adoption and opportunities in the UK telecommunications industry</div>', unsafe_allow_html=True)

    # Load data
    df = load_data()

    if df is None:
        st.error("⚠️ Data file 'output/unified_ai_analysis.csv' not found. Please run the analysis pipeline first.")
        st.info("Run: `cd 'Article Analysis' && python llm_analysis_pipeline.py` to generate the data.")
        return

    # Sidebar filters
    st.sidebar.header("Filters")

    # Date range filter
    if df['date'].notna().any():
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(df['date'].min(), df['date'].max()),
            min_value=df['date'].min().date() if pd.notna(df['date'].min()) else None,
            max_value=df['date'].max().date() if pd.notna(df['date'].max()) else None
        )

        if len(date_range) == 2:
            df = df[(df['date'] >= pd.Timestamp(date_range[0])) & (df['date'] <= pd.Timestamp(date_range[1]))]

    # Source filter
    sources = ['All'] + list(df['source'].unique())
    selected_source = st.sidebar.selectbox("News Source", sources)

    if selected_source != 'All':
        df = df[df['source'] == selected_source]

    # Key Metrics
    st.header("📊 Key Metrics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Articles", f"{len(df):,}")

    with col2:
        ai_count = df['has_ai'].sum()
        st.metric("AI Articles", f"{ai_count:,}")

    with col3:
        ai_pct = (ai_count / len(df) * 100) if len(df) > 0 else 0
        st.metric("AI Coverage", f"{ai_pct:.1f}%")

    with col4:
        total_mentions = df['ai_mention_count'].sum()
        st.metric("Total AI Mentions", f"{int(total_mentions):,}")

    with col5:
        avg_mentions = df[df['has_ai']]['ai_mention_count'].mean() if ai_count > 0 else 0
        st.metric("Avg Mentions/Article", f"{avg_mentions:.1f}")

    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Trends Over Time",
        "🎯 Opportunity Analysis",
        "🔍 Technology Deep Dive",
        "💬 Sentiment Analysis",
        "📰 Source Comparison"
    ])

    with tab1:
        st.header("AI Adoption Trends")

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_time_series_chart(df), use_container_width=True)

        with col2:
            st.plotly_chart(create_adoption_trend_chart(df), use_container_width=True)

        # Insights
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("### 💡 Key Insights")

        monthly_growth = df.groupby('year_month')['has_ai'].sum()
        if len(monthly_growth) >= 2:
            trend = "increasing" if monthly_growth.iloc[-1] > monthly_growth.iloc[0] else "decreasing"
            st.write(f"- AI mentions are **{trend}** over the analyzed period")

        st.write(f"- **{ai_pct:.1f}%** of industry articles discuss AI/ML technologies")
        st.write(f"- Average of **{avg_mentions:.1f}** AI technology mentions per relevant article")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.header("Market Opportunity Analysis")

        st.markdown("""
        **For Cartesian Consulting:** This matrix identifies AI use cases with:
        - **🎯 High Opportunity** (Upper Left): High sentiment but low coverage = underserved market
        - **✅ Established** (Upper Right): High coverage and positive sentiment = competitive market
        - **⚠️ Emerging** (Lower Left): Low coverage and sentiment = early-stage opportunity
        """)

        opp_fig = create_opportunity_matrix(df)
        if opp_fig:
            st.plotly_chart(opp_fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            use_case_fig = create_use_case_distribution(df)
            if use_case_fig:
                st.plotly_chart(use_case_fig, use_container_width=True)

        with col2:
            st.plotly_chart(create_title_vs_content_analysis(df), use_container_width=True)

        # Opportunity recommendations
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("### 🎯 Strategic Recommendations for Boutique Firms")

        ai_articles = df[df['has_ai']].copy()
        if len(ai_articles) > 0:
            use_case_counts = ai_articles['primary_use_case'].value_counts()

            # Identify least covered use cases
            least_covered = use_case_counts.nsmallest(3)

            st.write("**Underserved Use Cases (Opportunity Areas):**")
            for uc, count in least_covered.items():
                if pd.notna(uc):
                    st.write(f"- **{uc.replace('_', ' ').title()}**: Only {count} mentions - potential white space")

            # Most covered (competitive areas)
            st.write("\n**Highly Competitive Areas:**")
            for uc, count in use_case_counts.nlargest(2).items():
                if pd.notna(uc):
                    st.write(f"- **{uc.replace('_', ' ').title()}**: {count} mentions - requires differentiation")

        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.header("AI Technology Mentions")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.plotly_chart(create_keyword_frequency_chart(df), use_container_width=True)

        with col2:
            st.markdown("### Top Technologies")

            ai_articles = df[df['has_ai']].copy()
            all_mentions = []
            for mentions in ai_articles['ai_mentions'].dropna():
                all_mentions.extend([m.strip() for m in str(mentions).split(',') if m.strip()])

            if all_mentions:
                mention_counts = pd.Series(all_mentions).value_counts().head(10)

                for tech, count in mention_counts.items():
                    st.metric(tech, f"{count} mentions")

        # Title prominence
        st.subheader("AI in Headlines vs Content")
        title_ai_count = df['has_title_ai'].sum()
        st.write(f"**{title_ai_count}** articles ({title_ai_count/len(df)*100:.1f}%) mention AI in the **title**")
        st.write(f"**{ai_count}** articles ({ai_pct:.1f}%) mention AI in the **content**")

        if title_ai_count > 0:
            title_prominence = (title_ai_count / ai_count * 100) if ai_count > 0 else 0
            st.write(f"→ **{title_prominence:.1f}%** of AI articles feature it prominently in the title")

    with tab4:
        st.header("Sentiment Analysis")

        st.plotly_chart(create_sentiment_analysis(df), use_container_width=True)

        # Sentiment breakdown
        ai_articles = df[df['has_ai']].copy()
        if len(ai_articles) > 0:
            sentiment_dist = ai_articles['sentiment'].value_counts()

            col1, col2, col3 = st.columns(3)

            with col1:
                positive_pct = (sentiment_dist.get('positive', 0) / len(ai_articles) * 100)
                st.metric("Positive Sentiment", f"{positive_pct:.1f}%", delta="Good")

            with col2:
                neutral_pct = (sentiment_dist.get('neutral', 0) / len(ai_articles) * 100)
                st.metric("Neutral Sentiment", f"{neutral_pct:.1f}%")

            with col3:
                negative_pct = (sentiment_dist.get('negative', 0) / len(ai_articles) * 100)
                st.metric("Negative Sentiment", f"{negative_pct:.1f}%", delta="Concerns" if negative_pct > 10 else None)

    with tab5:
        st.header("Source Comparison")

        st.plotly_chart(create_source_comparison(df), use_container_width=True)

        # Source details
        source_stats = df.groupby('source').agg({
            'has_ai': 'sum',
            'title': 'count',
            'ai_mention_count': 'sum'
        }).reset_index()

        source_stats.columns = ['Source', 'AI Articles', 'Total Articles', 'Total AI Mentions']
        source_stats['% with AI'] = (source_stats['AI Articles'] / source_stats['Total Articles'] * 100).round(1)
        source_stats['Avg Mentions'] = (source_stats['Total AI Mentions'] / source_stats['AI Articles']).round(1)

        st.dataframe(source_stats, use_container_width=True)

    # Footer with data table
    st.header("📋 Raw Data")

    # Show sample of AI articles
    ai_sample = df[df['has_ai']][['date', 'source', 'title', 'primary_use_case', 'sentiment',
                                    'ai_mention_count', 'title_ai_mentions', 'url']].head(50)

    st.dataframe(ai_sample, use_container_width=True)

    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Full Dataset (CSV)",
        data=csv,
        file_name="uk_broadband_ai_analysis.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
