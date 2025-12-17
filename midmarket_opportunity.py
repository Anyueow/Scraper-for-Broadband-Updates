"""
Mid-Market AI Opportunity Analysis
Identifies gaps between big firm AI adoption and mid-market opportunities.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import json
import ollama
import re

def load_big_firm_data():
    """Load big firm analysis results."""
    path = "big firm analysis/big_firm_analysis_results.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df.rename(columns={'standardized_use_case': 'primary_use_case'})
        return df
    return None

def load_big_firm_cache():
    """Load rich cache data with technologies."""
    path = "big firm analysis/big_firm_cache.json"
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def analyze_big_firm_patterns(df, cache):
    """Analyze patterns in big firm AI adoption."""

    analysis = {
        'use_case_concentration': {},
        'technology_stack': {},
        'maturity_distribution': {},
        'strategic_focus': {},
        'company_specializations': {}
    }

    # Use case concentration
    use_case_counts = df['primary_use_case'].value_counts()
    total = len(df)
    for uc, count in use_case_counts.items():
        analysis['use_case_concentration'][uc] = {
            'count': count,
            'percentage': count / total * 100
        }

    # Company specializations
    for company in df['company'].unique():
        company_data = df[df['company'] == company]
        top_use_case = company_data['primary_use_case'].mode().iloc[0] if len(company_data) > 0 else None
        analysis['company_specializations'][company] = {
            'top_use_case': top_use_case,
            'initiatives': len(company_data),
            'high_strategic_pct': (company_data['strategic_importance'] == 'high').sum() / len(company_data) * 100
        }

    # Technology stack from cache
    if cache:
        all_techs = []
        for key, value in cache.items():
            techs = value.get('key_technologies', [])
            if isinstance(techs, list):
                all_techs.extend(techs)

        tech_counts = pd.Series(all_techs).value_counts()
        for tech, count in tech_counts.items():
            analysis['technology_stack'][tech] = count

        # Maturity distribution
        maturity_counts = {}
        for key, value in cache.items():
            stage = value.get('maturity_stage', 'unknown')
            maturity_counts[stage] = maturity_counts.get(stage, 0) + 1
        analysis['maturity_distribution'] = maturity_counts

        # Strategic focus
        strategic_counts = {}
        for key, value in cache.items():
            importance = value.get('strategic_importance', 'unknown')
            strategic_counts[importance] = strategic_counts.get(importance, 0) + 1
        analysis['strategic_focus'] = strategic_counts

    return analysis

def identify_midmarket_opportunities(big_firm_analysis):
    """Use LLM to identify mid-market opportunities based on big firm gaps."""

    prompt = f"""You are a UK telecommunications industry consultant specializing in AI strategy for mid-market operators.

Based on the following analysis of big firm (BT, VMO2, Vodafone) AI adoption patterns, identify specific opportunities for mid-market telecoms to innovate with AI.

BIG FIRM AI ADOPTION ANALYSIS:
{json.dumps(big_firm_analysis, indent=2)}

Analyze and provide a JSON response with:

1. **underserved_use_cases**: Use cases where big firms show low investment but have high potential for mid-market differentiation
   - For each: name, opportunity_score (0-100), rationale, implementation_complexity (low/medium/high)

2. **technology_gaps**: Technologies big firms haven't fully exploited that mid-market could leverage
   - For each: technology, opportunity_score, use_cases, competitive_advantage

3. **differentiation_strategies**: How mid-market can compete differently than big firms
   - For each: strategy_name, description, target_segment, expected_impact

4. **quick_wins**: AI initiatives mid-market can implement in 3-6 months
   - For each: initiative, use_case, estimated_cost (low/medium/high), roi_timeframe

5. **strategic_recommendations**: Top 5 prioritized recommendations for mid-market AI investment
   - For each: recommendation, priority (1-5), rationale, dependencies

Consider:
- Mid-market typically has 10-50k customers, limited IT budgets, fewer technical staff
- They need faster ROI and simpler implementations
- They can be more agile and innovative than large incumbents
- Customer intimacy and local market knowledge are advantages

Return ONLY valid JSON, no explanations.

Example format:
{{
  "underserved_use_cases": [
    {{
      "name": "predictive_maintenance",
      "opportunity_score": 85,
      "rationale": "Big firms focus on network optimization but neglect proactive maintenance for rural/regional networks",
      "implementation_complexity": "medium"
    }}
  ],
  "technology_gaps": [...],
  "differentiation_strategies": [...],
  "quick_wins": [...],
  "strategic_recommendations": [...]
}}"""

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

        print(f"Analyzing mid-market opportunities using {model}...")

        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.3}
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

        return json.loads(response_text)

    except Exception as e:
        print(f"Error in LLM analysis: {e}")
        return None

def create_opportunity_visualizations(big_firm_analysis, opportunities):
    """Create visualizations for mid-market opportunities."""

    figures = []

    # 1. Big Firm vs Mid-Market Opportunity Gap
    if opportunities and 'underserved_use_cases' in opportunities:
        use_cases = opportunities['underserved_use_cases']

        # Combine with big firm data
        gap_data = []
        for uc in use_cases:
            big_firm_pct = big_firm_analysis['use_case_concentration'].get(
                uc['name'], {'percentage': 0}
            )
            if isinstance(big_firm_pct, dict):
                big_firm_pct = big_firm_pct.get('percentage', 0)

            gap_data.append({
                'Use Case': uc['name'].replace('_', ' ').title(),
                'Big Firm Focus (%)': big_firm_pct,
                'Mid-Market Opportunity': uc['opportunity_score'],
                'Complexity': uc['implementation_complexity']
            })

        gap_df = pd.DataFrame(gap_data)

        fig1 = go.Figure()

        fig1.add_trace(go.Bar(
            name='Big Firm Focus',
            x=gap_df['Use Case'],
            y=gap_df['Big Firm Focus (%)'],
            marker_color='#6b7280',
            text=gap_df['Big Firm Focus (%)'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))

        fig1.add_trace(go.Bar(
            name='Mid-Market Opportunity Score',
            x=gap_df['Use Case'],
            y=gap_df['Mid-Market Opportunity'],
            marker_color='#10b981',
            text=gap_df['Mid-Market Opportunity'],
            textposition='outside'
        ))

        fig1.update_layout(
            title='Big Firm Focus vs Mid-Market Opportunity Gap',
            xaxis_title='',
            yaxis_title='Score / Percentage',
            barmode='group',
            height=500,
            template='plotly_white',
            xaxis_tickangle=-45,
            margin=dict(b=120),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        figures.append(('opportunity_gap', fig1))

    # 2. Quick Wins Matrix
    if opportunities and 'quick_wins' in opportunities:
        quick_wins = opportunities['quick_wins']

        # Map cost/complexity to numeric
        cost_map = {'low': 1, 'medium': 2, 'high': 3}
        roi_map = {'1-3 months': 1, '3-6 months': 2, '6-12 months': 3, '12+ months': 4}

        qw_data = []
        for qw in quick_wins:
            cost_val = cost_map.get(qw.get('estimated_cost', 'medium').lower(), 2)

            # Parse ROI timeframe
            roi_str = qw.get('roi_timeframe', '6 months').lower()
            if '1-3' in roi_str or '< 3' in roi_str:
                roi_val = 1
            elif '3-6' in roi_str or '6' in roi_str:
                roi_val = 2
            elif '6-12' in roi_str or '12' in roi_str:
                roi_val = 3
            else:
                roi_val = 2

            qw_data.append({
                'Initiative': qw['initiative'][:30] + '...' if len(qw['initiative']) > 30 else qw['initiative'],
                'Cost': cost_val,
                'ROI Speed': 4 - roi_val,  # Invert for better = higher
                'Use Case': qw.get('use_case', 'general')
            })

        qw_df = pd.DataFrame(qw_data)

        fig2 = px.scatter(
            qw_df,
            x='Cost',
            y='ROI Speed',
            text='Initiative',
            title='Quick Wins: Cost vs ROI Speed',
            labels={'Cost': 'Implementation Cost (1=Low, 3=High)',
                   'ROI Speed': 'ROI Speed (Higher=Faster)'},
            height=500,
            template='plotly_white'
        )

        fig2.update_traces(
            textposition='top center',
            marker=dict(size=15, color='#3b82f6')
        )

        # Add quadrant indicators
        fig2.add_hline(y=2, line_dash="dash", line_color="#9ca3af", opacity=0.5)
        fig2.add_vline(x=2, line_dash="dash", line_color="#9ca3af", opacity=0.5)

        # Annotations for quadrants
        fig2.add_annotation(x=1.5, y=3.5, text="<b>Best Bets</b>", showarrow=False,
                           font=dict(color="#10b981", size=10))
        fig2.add_annotation(x=2.5, y=3.5, text="<b>Worth It</b>", showarrow=False,
                           font=dict(color="#3b82f6", size=10))
        fig2.add_annotation(x=1.5, y=0.5, text="<b>Low Priority</b>", showarrow=False,
                           font=dict(color="#6b7280", size=10))
        fig2.add_annotation(x=2.5, y=0.5, text="<b>Avoid</b>", showarrow=False,
                           font=dict(color="#ef4444", size=10))

        figures.append(('quick_wins', fig2))

    # 3. Technology Gap Analysis
    if opportunities and 'technology_gaps' in opportunities:
        tech_gaps = opportunities['technology_gaps']

        tech_data = []
        for tg in tech_gaps:
            tech_data.append({
                'Technology': tg['technology'],
                'Opportunity Score': tg['opportunity_score']
            })

        tech_df = pd.DataFrame(tech_data).sort_values('Opportunity Score', ascending=True)

        fig3 = go.Figure(data=[
            go.Bar(
                x=tech_df['Opportunity Score'],
                y=tech_df['Technology'],
                orientation='h',
                marker_color='#2563eb',
                text=tech_df['Opportunity Score'],
                textposition='outside'
            )
        ])

        fig3.update_layout(
            title='Technology Opportunities for Mid-Market',
            xaxis_title='Opportunity Score',
            yaxis_title='',
            height=450,
            template='plotly_white',
            margin=dict(l=150)
        )

        figures.append(('technology_gaps', fig3))

    # 4. Strategic Recommendations Priority
    if opportunities and 'strategic_recommendations' in opportunities:
        recs = opportunities['strategic_recommendations']

        rec_data = []
        for rec in recs:
            rec_data.append({
                'Recommendation': rec['recommendation'][:40] + '...' if len(rec['recommendation']) > 40 else rec['recommendation'],
                'Priority': rec['priority'],
                'Full': rec['recommendation']
            })

        rec_df = pd.DataFrame(rec_data).sort_values('Priority')

        colors = ['#10b981', '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7']

        fig4 = go.Figure(data=[
            go.Bar(
                x=rec_df['Priority'],
                y=rec_df['Recommendation'],
                orientation='h',
                marker_color=colors[:len(rec_df)],
                text=rec_df['Priority'],
                textposition='inside'
            )
        ])

        fig4.update_layout(
            title='Strategic Recommendations by Priority',
            xaxis_title='Priority (1=Highest)',
            yaxis_title='',
            height=400,
            template='plotly_white',
            margin=dict(l=200),
            yaxis={'categoryorder': 'total descending'}
        )

        figures.append(('strategic_recommendations', fig4))

    # 5. Big Firm Concentration Sunburst
    use_case_data = big_firm_analysis['use_case_concentration']

    sunburst_data = []
    for uc, data in use_case_data.items():
        sunburst_data.append({
            'Use Case': uc.replace('_', ' ').title(),
            'Count': data['count'],
            'Percentage': data['percentage']
        })

    sun_df = pd.DataFrame(sunburst_data)

    fig5 = px.pie(
        sun_df,
        values='Count',
        names='Use Case',
        title='Big Firm AI Focus Distribution',
        hole=0.4,
        height=450,
        template='plotly_white'
    )

    fig5.update_layout(
        annotations=[dict(text='Big Firms', x=0.5, y=0.5, font_size=14, showarrow=False)]
    )

    figures.append(('big_firm_focus', fig5))

    return figures

def generate_report(big_firm_analysis, opportunities):
    """Generate text report of findings."""

    report = """
================================================================================
MID-MARKET AI OPPORTUNITY ANALYSIS
================================================================================

EXECUTIVE SUMMARY
-----------------
This analysis identifies gaps in big firm (BT, VMO2, Vodafone) AI adoption
that present opportunities for mid-market telecom operators to differentiate
and innovate.

BIG FIRM AI ADOPTION PATTERNS
-----------------------------
"""

    # Use case concentration
    report += "\nUse Case Concentration:\n"
    for uc, data in sorted(big_firm_analysis['use_case_concentration'].items(),
                           key=lambda x: x[1]['percentage'], reverse=True):
        report += f"  - {uc.replace('_', ' ').title()}: {data['percentage']:.1f}% ({data['count']} initiatives)\n"

    # Technology stack
    if big_firm_analysis['technology_stack']:
        report += "\nTop Technologies Deployed:\n"
        for tech, count in sorted(big_firm_analysis['technology_stack'].items(),
                                  key=lambda x: x[1], reverse=True)[:10]:
            report += f"  - {tech}: {count} mentions\n"

    # Maturity
    if big_firm_analysis['maturity_distribution']:
        report += "\nMaturity Distribution:\n"
        for stage, count in big_firm_analysis['maturity_distribution'].items():
            report += f"  - {stage}: {count}\n"

    # Opportunities
    if opportunities:
        report += "\n" + "="*80 + "\n"
        report += "MID-MARKET OPPORTUNITIES\n"
        report += "="*80 + "\n"

        # Underserved use cases
        if 'underserved_use_cases' in opportunities:
            report += "\nUnderserved Use Cases (High Opportunity):\n"
            for uc in sorted(opportunities['underserved_use_cases'],
                           key=lambda x: x['opportunity_score'], reverse=True):
                report += f"\n  {uc['name'].replace('_', ' ').title()} (Score: {uc['opportunity_score']})\n"
                report += f"    Complexity: {uc['implementation_complexity']}\n"
                report += f"    Rationale: {uc['rationale']}\n"

        # Quick wins
        if 'quick_wins' in opportunities:
            report += "\nQuick Wins (3-6 month implementation):\n"
            for qw in opportunities['quick_wins']:
                report += f"\n  - {qw['initiative']}\n"
                report += f"    Use Case: {qw.get('use_case', 'N/A')}\n"
                report += f"    Cost: {qw.get('estimated_cost', 'N/A')}\n"
                report += f"    ROI: {qw.get('roi_timeframe', 'N/A')}\n"

        # Strategic recommendations
        if 'strategic_recommendations' in opportunities:
            report += "\nStrategic Recommendations:\n"
            for rec in sorted(opportunities['strategic_recommendations'],
                            key=lambda x: x['priority']):
                report += f"\n  {rec['priority']}. {rec['recommendation']}\n"
                report += f"     Rationale: {rec['rationale']}\n"

        # Differentiation strategies
        if 'differentiation_strategies' in opportunities:
            report += "\nDifferentiation Strategies:\n"
            for strat in opportunities['differentiation_strategies']:
                report += f"\n  - {strat['strategy_name']}\n"
                report += f"    {strat['description']}\n"
                report += f"    Target: {strat.get('target_segment', 'N/A')}\n"

    report += "\n" + "="*80 + "\n"

    return report

def main():
    print("="*60)
    print("MID-MARKET AI OPPORTUNITY ANALYSIS")
    print("="*60)

    # Load data
    df = load_big_firm_data()
    cache = load_big_firm_cache()

    if df is None:
        print("Error: Big firm data not found!")
        return

    print(f"Loaded {len(df)} big firm initiatives")

    # Analyze big firm patterns
    print("\nAnalyzing big firm AI patterns...")
    big_firm_analysis = analyze_big_firm_patterns(df, cache)

    # Use LLM to identify opportunities
    print("\nIdentifying mid-market opportunities...")
    opportunities = identify_midmarket_opportunities(big_firm_analysis)

    if opportunities is None:
        print("Error: Could not generate opportunity analysis")
        return

    # Save opportunities to JSON
    with open("output/midmarket_opportunities.json", 'w') as f:
        json.dump(opportunities, f, indent=2)
    print("\nSaved opportunities to: output/midmarket_opportunities.json")

    # Create visualizations
    print("\nGenerating visualizations...")
    figures = create_opportunity_visualizations(big_firm_analysis, opportunities)

    for name, fig in figures:
        png_path = f"output/midmarket_{name}.png"
        fig.write_image(png_path, width=1200, height=600, scale=2)
        print(f"Saved: {png_path}")

    # Generate report
    report = generate_report(big_firm_analysis, opportunities)

    report_path = "output/midmarket_opportunity_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nSaved report to: {report_path}")

    # Print summary
    print("\n" + "="*60)
    print("KEY FINDINGS")
    print("="*60)

    if opportunities and 'strategic_recommendations' in opportunities:
        print("\nTop 3 Strategic Recommendations:")
        for rec in sorted(opportunities['strategic_recommendations'],
                        key=lambda x: x['priority'])[:3]:
            print(f"\n  {rec['priority']}. {rec['recommendation']}")

    if opportunities and 'quick_wins' in opportunities:
        print("\nQuick Wins:")
        for qw in opportunities['quick_wins'][:3]:
            print(f"  - {qw['initiative']}")

if __name__ == "__main__":
    main()
