"""
Combine big firm analysis and overall output CSVs, grouped by company.
"""

import pandas as pd
import os
import re

def extract_company_from_text(text):
    """Extract company names from text."""
    companies = [
        'BT', 'Openreach', 'Virgin Media', 'VMO2', 'O2', 'EE', 'Vodafone', 'Three',
        'TalkTalk', 'Sky', 'Plusnet', 'Gigaclear', 'CityFibre', 'Hyperoptic',
        'Community Fibre', 'Zzoomm', 'Fibrus', 'Quickline', 'Daisy',
        'Vorboss', 'Nexfibre', 'TOTSCo'
    ]

    found = []
    text_lower = text.lower() if text else ""

    for company in companies:
        if company.lower() in text_lower:
            found.append(company)

    return found if found else ['Unknown']

def main():
    # Paths
    big_firm_path = "big firm analysis/big_firm_analysis_results.csv"
    overall_path = "output/unified_ai_analysis.csv"
    output_path = "output/combined_by_company.csv"

    # Load big firm data
    if os.path.exists(big_firm_path):
        big_firm_df = pd.read_csv(big_firm_path)
        big_firm_df['data_source'] = 'big_firm_analysis'
        print(f"Loaded {len(big_firm_df)} big firm articles")
    else:
        print(f"Big firm file not found: {big_firm_path}")
        big_firm_df = pd.DataFrame()

    # Load overall data
    if os.path.exists(overall_path):
        overall_df = pd.read_csv(overall_path)
        overall_df['data_source'] = 'general_analysis'
        print(f"Loaded {len(overall_df)} general articles")

        # Extract companies from titles for general data
        overall_df['company'] = overall_df['title'].apply(
            lambda x: extract_company_from_text(str(x))[0]
        )
    else:
        print(f"Overall file not found: {overall_path}")
        overall_df = pd.DataFrame()

    # Standardize column names
    if len(big_firm_df) > 0:
        big_firm_df = big_firm_df.rename(columns={
            'article_title': 'title',
            'standardized_use_case': 'primary_use_case',
            'original_use_case': 'manual_use_case',
            'original_notes': 'notes'
        })

    # Select common columns for combining
    common_cols = ['company', 'title', 'date', 'primary_use_case', 'sentiment',
                   'confidence', 'summary', 'data_source']

    # Prepare big firm data
    if len(big_firm_df) > 0:
        for col in common_cols:
            if col not in big_firm_df.columns:
                big_firm_df[col] = None
        big_firm_subset = big_firm_df[common_cols].copy()
    else:
        big_firm_subset = pd.DataFrame(columns=common_cols)

    # Prepare overall data (only AI articles)
    if len(overall_df) > 0:
        ai_articles = overall_df[overall_df['ai_mention_count'] > 0].copy()
        for col in common_cols:
            if col not in ai_articles.columns:
                ai_articles[col] = None
        # Use primary_use_case_confidence as confidence if available
        if 'primary_use_case_confidence' in ai_articles.columns:
            ai_articles['confidence'] = ai_articles['primary_use_case_confidence']
        overall_subset = ai_articles[common_cols].copy()
    else:
        overall_subset = pd.DataFrame(columns=common_cols)

    # Combine
    combined_df = pd.concat([big_firm_subset, overall_subset], ignore_index=True)

    # Convert date
    combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')

    # Sort by company and date
    combined_df = combined_df.sort_values(['company', 'date'], ascending=[True, False])

    # Save combined data
    combined_df.to_csv(output_path, index=False)
    print(f"\nSaved combined data to: {output_path}")
    print(f"Total articles: {len(combined_df)}")

    # Generate company summary
    print("\n" + "="*60)
    print("COMPANY SUMMARY")
    print("="*60)

    company_stats = combined_df.groupby('company').agg({
        'title': 'count',
        'sentiment': lambda x: (x == 'positive').sum() / len(x) * 100 if len(x) > 0 else 0,
        'primary_use_case': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A'
    }).reset_index()

    company_stats.columns = ['Company', 'Articles', 'Positive %', 'Top Use Case']
    company_stats = company_stats.sort_values('Articles', ascending=False)
    company_stats['Positive %'] = company_stats['Positive %'].apply(lambda x: f"{x:.1f}%")

    print(company_stats.to_string(index=False))

    # Save company summary
    summary_path = "output/company_summary.csv"
    company_stats.to_csv(summary_path, index=False)
    print(f"\nSaved company summary to: {summary_path}")

    # Use case by company pivot
    print("\n" + "="*60)
    print("USE CASES BY COMPANY")
    print("="*60)

    use_case_pivot = pd.crosstab(combined_df['company'], combined_df['primary_use_case'])
    use_case_pivot = use_case_pivot.loc[use_case_pivot.sum(axis=1).sort_values(ascending=False).head(10).index]

    pivot_path = "output/use_case_by_company.csv"
    use_case_pivot.to_csv(pivot_path)
    print(f"Saved use case pivot to: {pivot_path}")
    print(use_case_pivot)

if __name__ == "__main__":
    main()
