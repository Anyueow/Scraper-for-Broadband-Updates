"""
Clean & Simple Streamlit Dashboard for UK Broadband AI Trends
Source of Truth: output/ai_articles_updated.csv & company_use_case_matrix_binary_sorted.csv
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="UK Broadband AI Trends",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean presentation
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #2563eb;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_ai_articles():
    """Load cleaned AI articles data."""
    csv_path = "output/ai_articles_updated.csv"
    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year_month'] = df['date'].dt.to_period('M').astype(str)

    return df

@st.cache_data
def load_company_matrix():
    """Load company use case binary matrix."""
    csv_path = "company_use_case_matrix_binary_sorted.csv"
    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path, index_col=0)
    # Remove TOTAL row if present
    if 'TOTAL' in df.index:
        df = df.drop('TOTAL')

    return df

def create_binary_matrix_chart(matrix_df):
    """Create binary matrix with checkmarks/crosses."""
    if matrix_df is None or len(matrix_df) == 0:
        return None

    # Create custom heatmap with checkmarks
    z_values = matrix_df.values

    # Create text with checkmarks and crosses
    text_values = []
    for row in z_values:
        text_row = []
        for val in row:
            if val == 1:
                text_row.append('✓')
            else:
                text_row.append('')
        text_values.append(text_row)

    # Create color scale: white for 0, green for 1
    colorscale = [[0, '#f0f0f0'], [1, '#10b981']]

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=matrix_df.columns,
        y=matrix_df.index,
        colorscale=colorscale,
        showscale=False,
        text=text_values,
        texttemplate='%{text}',
        textfont={"size": 20, "color": "white"},
        hovertemplate='Company: %{y}<br>Category: %{x}<br>Has: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title="Company AI Use Case Coverage Matrix",
        xaxis_title="",
        yaxis_title="",
        height=600,
        template='plotly_white',
        margin=dict(l=150, r=20, t=60, b=150),
        font=dict(size=12, family="Arial, sans-serif"),
        xaxis={'side': 'bottom'},
        xaxis_tickangle=-45
    )

    return fig

def create_ai_adoption_timeseries(df):
    """Time series showing AI article count over time."""
    if df is None or len(df) == 0:
        return None

    # Group by month
    monthly = df.groupby('year_month').size().reset_index(name='AI Articles')

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly['year_month'],
        y=monthly['AI Articles'],
        mode='lines+markers',
        name='AI Articles',
        line=dict(color='#2563eb', width=3),
        marker=dict(size=8, color='#2563eb'),
        fill='tozeroy',
        fillcolor='rgba(37, 99, 235, 0.1)'
    ))

    fig.update_layout(
        title="AI Adoption Over Time",
        xaxis_title="",
        yaxis_title="Number of AI Articles",
        height=450,
        template='plotly_white',
        showlegend=False,
        margin=dict(l=60, r=20, t=60, b=80),
        font=dict(size=12, family="Arial, sans-serif"),
        hovermode='x unified'
    )

    return fig

def create_use_case_bar_chart(df):
    """Bar chart of AI use cases."""
    if df is None or len(df) == 0:
        return None

    # Count use cases
    use_case_counts = df[df['primary_use_case'].notna()]['primary_use_case'].value_counts().reset_index()
    use_case_counts.columns = ['Use Case', 'Count']

    # Map to readable names
    label_map = {
        'customer_support_experience': 'Customer Support & Experience',
        'internal_productivity_workforce': 'Internal Productivity & Workforce',
        'network_optimization_performance': 'Network Optimization & Performance',
        'security_fraud_threat': 'Security, Fraud & Threat',
        'network_planning_deployment': 'Network Planning & Deployment',
        'predictive_maintenance_analytics': 'Predictive Maintenance & Analytics',
        'other': 'Other'
    }

    use_case_counts['Use Case'] = use_case_counts['Use Case'].map(label_map)

    # Sort by count
    use_case_counts = use_case_counts.sort_values('Count', ascending=True)

    fig = go.Figure(data=[
        go.Bar(
            y=use_case_counts['Use Case'],
            x=use_case_counts['Count'],
            orientation='h',
            marker_color='#2563eb',
            text=use_case_counts['Count'],
            textposition='outside',
            textfont=dict(size=12)
        )
    ])

    fig.update_layout(
        title="AI Use Cases by Frequency",
        xaxis_title="Number of Articles",
        yaxis_title="",
        height=500,
        template='plotly_white',
        margin=dict(l=300, r=60, t=60, b=50),
        font=dict(size=12, family="Arial, sans-serif")
    )

    return fig

def create_company_bar_chart(df):
    """Bar chart of company mentions."""
    if df is None or len(df) == 0:
        return None

    # Count companies (excluding unknowns)
    company_counts = df[df['company'].notna()]['company'].value_counts().reset_index()
    company_counts.columns = ['Company', 'Count']

    # Top 15 companies
    company_counts = company_counts.head(15).sort_values('Count', ascending=True)

    fig = go.Figure(data=[
        go.Bar(
            y=company_counts['Company'],
            x=company_counts['Count'],
            orientation='h',
            marker_color='#10b981',
            text=company_counts['Count'],
            textposition='outside',
            textfont=dict(size=12)
        )
    ])

    fig.update_layout(
        title="Top Companies by AI Initiative Count",
        xaxis_title="Number of AI Initiatives",
        yaxis_title="",
        height=500,
        template='plotly_white',
        margin=dict(l=150, r=60, t=60, b=50),
        font=dict(size=12, family="Arial, sans-serif")
    )

    return fig

def create_company_size_activity_matrix(matrix_df):
    """2x2 matrix: Company Size vs AI Public Activity."""
    if matrix_df is None or len(matrix_df) == 0:
        return None

    # Company size ranking (based on company_ranked.md)
    # Higher number = larger company
    company_size = {
        'BT': 100,
        'VMO2': 95,
        'Sky': 90,
        'Vodafone': 85,
        'Openreach': 80,
        'Utility Warehouse': 75,
        'TalkTalk': 70,
        # Tier 2
        'CityFibre': 60,
        'Zen': 55,
        'Hyperoptic': 50,
        'YouFibre / Brsk': 45,
        'Netomnia': 45,
        # Tier 3
        'Community Fibre': 35,
        'Glide': 30,
        'Gigaclear': 25,
        'ITS': 20,
        'FullFibre': 15,
        'Cuckoo': 10,
        # Tier 4
        'nexfibre': 5,
        'APFN': 5,
    }

    # Calculate AI public activity (number of categories with AI)
    ai_activity = matrix_df.sum(axis=1).to_dict()

    # Create data for scatter plot
    plot_data = []
    for company in matrix_df.index:
        if company in company_size:
            plot_data.append({
                'Company': company,
                'Size': company_size[company],
                'AI Activity': ai_activity[company],
                'Size Label': 'Large' if company_size[company] >= 70 else 'Medium' if company_size[company] >= 30 else 'Small'
            })

    if not plot_data:
        return None

    plot_df = pd.DataFrame(plot_data)

    # Calculate quadrants
    median_activity = plot_df['AI Activity'].median()
    median_size = plot_df['Size'].median()

    # Create scatter plot
    fig = go.Figure()

    # Add quadrant backgrounds
    fig.add_shape(type="rect",
                  x0=0, y0=median_size, x1=median_activity, y1=100,
                  fillcolor="rgba(200, 200, 200, 0.1)", line_width=0,
                  layer="below")
    fig.add_shape(type="rect",
                  x0=median_activity, y0=median_size, x1=6, y1=100,
                  fillcolor="rgba(16, 185, 129, 0.1)", line_width=0,
                  layer="below")
    fig.add_shape(type="rect",
                  x0=0, y0=0, x1=median_activity, y1=median_size,
                  fillcolor="rgba(239, 68, 68, 0.1)", line_width=0,
                  layer="below")
    fig.add_shape(type="rect",
                  x0=median_activity, y0=0, x1=6, y1=median_size,
                  fillcolor="rgba(251, 191, 36, 0.1)", line_width=0,
                  layer="below")

    # Add scatter points
    fig.add_trace(go.Scatter(
        x=plot_df['AI Activity'],
        y=plot_df['Size'],
        mode='markers+text',
        marker=dict(
            size=15,
            color=plot_df['AI Activity'],
            colorscale='Blues',
            showscale=False,
            line=dict(width=2, color='white')
        ),
        text=plot_df['Company'],
        textposition='top center',
        textfont=dict(size=10),
        hovertemplate='<b>%{text}</b><br>AI Categories: %{x}<br>Size Tier: %{customdata}<extra></extra>',
        customdata=plot_df['Size Label']
    ))

    # Add quadrant lines
    fig.add_hline(y=median_size, line_dash="dash", line_color="gray", line_width=2)
    fig.add_vline(x=median_activity, line_dash="dash", line_color="gray", line_width=2)

    # Add quadrant labels
    fig.add_annotation(x=median_activity/2, y=95,
                      text="Large, Low Activity<br>(Opportunity)",
                      showarrow=False, font=dict(size=11, color="gray"))
    fig.add_annotation(x=(median_activity + 6)/2, y=95,
                      text="Large, High Activity<br>(Leaders)",
                      showarrow=False, font=dict(size=11, color="green"))
    fig.add_annotation(x=median_activity/2, y=5,
                      text="Small, Low Activity<br>(Laggards)",
                      showarrow=False, font=dict(size=11, color="red"))
    fig.add_annotation(x=(median_activity + 6)/2, y=5,
                      text="Small, High Activity<br>(Ambitious)",
                      showarrow=False, font=dict(size=11, color="orange"))

    fig.update_layout(
        title="Company Positioning: Size vs AI Public Activity",
        xaxis_title="AI Public Activity (Number of AI Use Case Categories)",
        yaxis_title="Company Size (Revenue & Scale)",
        height=600,
        template='plotly_white',
        margin=dict(l=80, r=80, t=80, b=80),
        font=dict(size=12, family="Arial, sans-serif"),
        showlegend=False,
        xaxis=dict(range=[-0.5, 6.5], dtick=1),
        yaxis=dict(range=[0, 105])
    )

    return fig

# Main Dashboard
def main():
    st.markdown('<div class="main-header">UK Broadband AI Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Clean analysis of AI adoption in UK telecom industry</div>', unsafe_allow_html=True)

    # Load data
    df = load_ai_articles()
    matrix_df = load_company_matrix()

    if df is None:
        st.error("⚠️ Data file 'output/ai_articles_updated.csv' not found.")
        st.info("Please ensure the analysis has been run and the file exists.")
        return

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    total_articles = len(df)
    total_companies = df['company'].nunique() if 'company' in df.columns else 0
    total_use_cases = df['primary_use_case'].nunique() if 'primary_use_case' in df.columns else 0

    with col1:
        st.metric("Total AI Articles", f"{total_articles:,}")

    with col2:
        st.metric("Companies Tracked", f"{total_companies}")

    with col3:
        st.metric("Use Case Categories", f"{total_use_cases}")

    with col4:
        if df['date'].notna().any():
            date_range = f"{df['date'].min().strftime('%b %Y')} - {df['date'].max().strftime('%b %Y')}"
        else:
            date_range = "N/A"
        st.metric("Period", date_range)

    st.markdown("---")

    # 1. Company Use Case Matrix (Binary)
    st.subheader("📊 Company AI Use Case Coverage")
    st.markdown("*Green checkmarks (✓) indicate that a company has AI initiatives in that category*")

    if matrix_df is not None:
        matrix_chart = create_binary_matrix_chart(matrix_df)
        if matrix_chart:
            st.plotly_chart(matrix_chart, use_container_width=True)

            # Calculate coverage stats
            coverage = matrix_df.sum(axis=1).sort_values(ascending=False)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Top Companies by Category Coverage:**")
                for company, count in coverage.head(5).items():
                    st.write(f"• **{company}**: {int(count)}/6 categories ({count/6*100:.0f}%)")

            with col2:
                # Category coverage
                category_coverage = matrix_df.sum(axis=0).sort_values(ascending=False)
                st.markdown("**Most Common Use Cases:**")
                for category, count in category_coverage.items():
                    st.write(f"• **{category}**: {int(count)} companies")
    else:
        st.warning("Company use case matrix not found. Please ensure 'company_use_case_matrix_binary_sorted.csv' exists.")

    st.markdown("---")

    # 2. Company Size vs AI Activity Matrix
    st.subheader("📍 Company Positioning: Size vs AI Public Activity")
    st.markdown("*2x2 matrix showing company size (revenue/scale) against AI public activity (number of AI use case categories)*")

    if matrix_df is not None:
        positioning_matrix = create_company_size_activity_matrix(matrix_df)
        if positioning_matrix:
            st.plotly_chart(positioning_matrix, use_container_width=True)

            # Key insights
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Leaders (Large + High Activity):**")
                st.write("• VMO2 (5/6 categories)")
                st.write("• BT, Vodafone (4/6 categories)")
                st.markdown("*These companies are maximizing their AI visibility*")

            with col2:
                st.markdown("**Opportunities (Large + Low Activity):**")
                st.write("• Sky, Openreach, TalkTalk, Utility Warehouse")
                st.markdown("*Large companies with potential to increase AI public engagement*")

    st.markdown("---")

    # 3. AI Adoption Time Series
    st.subheader("📈 AI Adoption Over Time")

    adoption_ts = create_ai_adoption_timeseries(df)
    if adoption_ts:
        st.plotly_chart(adoption_ts, use_container_width=True)

        # Monthly growth stats
        monthly = df.groupby('year_month').size()
        if len(monthly) > 1:
            latest_month = monthly.iloc[-1]
            prev_month = monthly.iloc[-2]
            growth = ((latest_month - prev_month) / prev_month * 100) if prev_month > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latest Month", f"{latest_month} articles")
            with col2:
                st.metric("Previous Month", f"{prev_month} articles")
            with col3:
                st.metric("Month-over-Month Growth", f"{growth:+.1f}%")

    st.markdown("---")

    # 4. Use Case Distribution
    st.subheader("🎯 AI Use Case Distribution")

    col1, col2 = st.columns([2, 1])

    with col1:
        use_case_chart = create_use_case_bar_chart(df)
        if use_case_chart:
            st.plotly_chart(use_case_chart, use_container_width=True)

    with col2:
        # Use case percentages
        st.markdown("**Use Case Breakdown:**")
        use_case_counts = df[df['primary_use_case'].notna()]['primary_use_case'].value_counts()

        label_map = {
            'customer_support_experience': 'Customer Support',
            'internal_productivity_workforce': 'Internal Productivity',
            'network_optimization_performance': 'Network Optimization',
            'security_fraud_threat': 'Security & Fraud',
            'network_planning_deployment': 'Network Planning',
            'predictive_maintenance_analytics': 'Predictive Maintenance',
            'other': 'Other'
        }

        for use_case, count in use_case_counts.items():
            label = label_map.get(use_case, use_case)
            pct = count / use_case_counts.sum() * 100
            st.write(f"**{label}**")
            st.progress(pct / 100)
            st.write(f"{count} articles ({pct:.1f}%)")
            st.write("")

    st.markdown("---")

    # 5. Company Rankings
    st.subheader("🏢 Top Companies by AI Activity")

    company_chart = create_company_bar_chart(df)
    if company_chart:
        st.plotly_chart(company_chart, use_container_width=True)

    # Sidebar - Filters
    st.sidebar.header("Filters")

    # Date filter
    if df['date'].notna().any():
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()

        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if len(date_range) == 2:
            df = df[(df['date'] >= pd.Timestamp(date_range[0])) &
                   (df['date'] <= pd.Timestamp(date_range[1]))]

    # Company filter
    if 'company' in df.columns:
        companies = ['All'] + sorted(df['company'].dropna().unique().tolist())
        selected_company = st.sidebar.selectbox("Company", companies)

        if selected_company != 'All':
            df = df[df['company'] == selected_company]

    # Use case filter
    if 'primary_use_case' in df.columns:
        use_cases = ['All'] + sorted(df['primary_use_case'].dropna().unique().tolist())
        selected_use_case = st.sidebar.selectbox("Use Case", use_cases)

        if selected_use_case != 'All':
            df = df[df['primary_use_case'] == selected_use_case]

    # Export
    st.sidebar.markdown("---")
    st.sidebar.header("Export")

    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name="uk_broadband_ai_filtered.csv",
        mime="text/csv"
    )

    # Info
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Data Sources:**
    - `output/ai_articles_updated.csv`
    - `company_use_case_matrix_binary_sorted.csv`

    **Last Updated:** {}
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M')))

if __name__ == "__main__":
    main()
