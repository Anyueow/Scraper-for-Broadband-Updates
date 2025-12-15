"""
ROI Impact Analysis Script

Extracts and analyzes ROI claims from articles using the ROI Framework.
Quantifies business impact of telco AI initiatives.

Input: unified_ai_analysis_enhanced.csv
Output: roi_impact_analysis.csv
"""

import pandas as pd
import re
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class ROIImpactAnalyzer:
    """Analyzes ROI claims and business impact from article data."""

    # ROI extraction patterns from ROI_Formula.MD
    PERCENTAGE_PATTERNS = [
        r'reduced\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
        r'improved\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
        r'(\d+(?:\.\d+)?)%\s+(?:reduction|decrease|improvement|increase)',
        r'up\s+(\d+(?:\.\d+)?)%',
        r'down\s+(\d+(?:\.\d+)?)%',
        r'(\d+(?:\.\d+)?)%\s+(?:faster|slower|more|less)',
    ]

    AMOUNT_PATTERNS = [
        r'[£$€]\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|m|bn|k)?',
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion)\s+[£$€]',
        r'saved\s+[£$€]?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|k)?',
        r'generated\s+[£$€]?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion)?',
    ]

    TIME_PATTERNS = [
        r'reduced\s+from\s+(\d+)\s+(hours?|minutes?|days?)\s+to\s+(\d+)',
        r'(\d+(?:\.\d+)?)%\s+faster',
        r'(\d+)\s+(hours?|minutes?)\s+saved\s+per\s+(day|week|month)',
    ]

    METRIC_PATTERNS = [
        r'NPS\s+(?:increased|improved)\s+(?:from\s+)?(\d+)\s+(?:to\s+)?(\d+)?',
        r'CSAT\s+(?:up|improved)\s+(\d+)%',
        r'churn\s+(?:reduced|decreased)\s+from\s+(\d+(?:\.\d+)?)%\s+to\s+(\d+(?:\.\d+)?)%',
        r'(?:FTE|headcount)\s+savings?\s+(?:of\s+)?(\d+)',
    ]

    # Use case to ROI category mapping
    USE_CASE_ROI_CATEGORIES = {
        'network_planning_deployment': 'Network Planning & Deployment',
        'network_optimization_performance': 'Network Optimization & Performance',
        'predictive_maintenance_analytics': 'Predictive Maintenance & Analytics',
        'customer_support_experience': 'Customer Support & Experience',
        'security_fraud_threat': 'Security, Fraud & Threat Detection',
        'internal_productivity_workforce': 'Internal Productivity & Workforce',
        'other': 'Other/General'
    }

    def __init__(self,
                 enhanced_csv_path: str = "../02_analysis/pipelines/unified_ai_analysis_enhanced.csv",
                 output_dir: str = "../03_processed_data"):
        """
        Initialize the ROI analyzer.

        Args:
            enhanced_csv_path: Path to enhanced analysis CSV
            output_dir: Directory for output files
        """
        self.enhanced_csv_path = enhanced_csv_path
        self.output_dir = output_dir
        self.df = None

    def load_data(self) -> pd.DataFrame:
        """Load enhanced analysis data."""
        if not os.path.exists(self.enhanced_csv_path):
            raise FileNotFoundError(f"Enhanced CSV not found: {self.enhanced_csv_path}")

        self.df = pd.read_csv(self.enhanced_csv_path)
        print(f"✓ Loaded {len(self.df)} articles from enhanced analysis")

        # Filter to AI articles with summaries
        ai_articles = self.df[
            (self.df['ai_mention_count'] > 0) &
            (self.df['summary'].notna()) &
            (self.df['summary'] != 'N/A')
        ]
        print(f"✓ Found {len(ai_articles)} AI articles with summaries")

        return self.df

    def extract_percentages(self, text: str) -> List[float]:
        """Extract percentage values from text."""
        percentages = []
        for pattern in self.PERCENTAGE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    pct = float(match.group(1))
                    if 0 < pct <= 100:  # Reasonable percentage range
                        percentages.append(pct)
                except (ValueError, IndexError):
                    continue
        return percentages

    def extract_amounts(self, text: str) -> List[Tuple[float, str]]:
        """Extract monetary amounts from text."""
        amounts = []
        for pattern in self.AMOUNT_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    multiplier_str = match.group(2) if len(match.groups()) > 1 else ''

                    # Apply multiplier
                    multiplier = 1
                    if multiplier_str:
                        mult_lower = multiplier_str.lower()
                        if mult_lower in ['million', 'm']:
                            multiplier = 1_000_000
                        elif mult_lower in ['billion', 'bn']:
                            multiplier = 1_000_000_000
                        elif mult_lower == 'k':
                            multiplier = 1_000

                    final_amount = amount * multiplier

                    # Extract currency if present in original text
                    currency = 'GBP'  # Default
                    if '$' in text[max(0, match.start()-5):match.end()]:
                        currency = 'USD'
                    elif '€' in text[max(0, match.start()-5):match.end()]:
                        currency = 'EUR'

                    amounts.append((final_amount, currency))
                except (ValueError, IndexError):
                    continue
        return amounts

    def extract_roi_claims(self, row: pd.Series) -> Dict:
        """Extract ROI claims from an article."""
        # Combine summary and title for ROI extraction
        text = f"{row.get('title', '')} {row.get('summary', '')}"

        # Extract different types of ROI metrics
        percentages = self.extract_percentages(text)
        amounts = self.extract_amounts(text)

        # Determine ROI type based on keywords
        roi_type = self._classify_roi_type(text)

        # Get use case category
        primary_use_case = row.get('primary_use_case', 'other')
        roi_category = self.USE_CASE_ROI_CATEGORIES.get(primary_use_case, 'Other/General')

        # Calculate credibility score
        credibility_score = self._calculate_credibility(row, percentages, amounts)

        return {
            'url': row.get('url', ''),
            'title': row.get('title', '')[:100],
            'company': row.get('companies_mentioned', ''),
            'use_case': primary_use_case,
            'roi_category': roi_category,
            'roi_type': roi_type,
            'has_percentage_claim': len(percentages) > 0,
            'max_percentage': max(percentages) if percentages else None,
            'percentages': ','.join([f"{p:.1f}%" for p in percentages]),
            'has_amount_claim': len(amounts) > 0,
            'max_amount': max([a[0] for a in amounts]) if amounts else None,
            'amounts': ','.join([f"{a[0]:,.0f} {a[1]}" for a in amounts]),
            'credibility_score': credibility_score,
            'source': row.get('source', ''),
            'date': row.get('date', ''),
            'sentiment': row.get('sentiment', ''),
            'ai_mention_count': row.get('ai_mention_count', 0)
        }

    def _classify_roi_type(self, text: str) -> str:
        """Classify the type of ROI claim."""
        text_lower = text.lower()

        if any(word in text_lower for word in ['cost', 'savings', 'reduced', 'opex', 'capex', 'expense']):
            return 'cost_reduction'
        elif any(word in text_lower for word in ['revenue', 'sales', 'income', 'arpu', 'growth']):
            return 'revenue_growth'
        elif any(word in text_lower for word in ['time', 'productivity', 'efficiency', 'faster', 'hours']):
            return 'time_savings'
        elif any(word in text_lower for word in ['nps', 'csat', 'satisfaction', 'experience', 'churn']):
            return 'customer_impact'
        elif any(word in text_lower for word in ['competitive', 'advantage', 'leadership', 'innovation']):
            return 'strategic_value'
        else:
            return 'general_improvement'

    def _calculate_credibility(self, row: pd.Series, percentages: List, amounts: List) -> int:
        """Calculate credibility score (0-100) for ROI claim."""
        score = 40  # Base score

        # Source credibility (+20 for known reliable sources)
        source = row.get('source', '').lower()
        if 'ispreview' in source or 'fibrenews' in source or 'thinkbroadband' in source:
            score += 15  # Industry-specific sources

        # Specificity bonus (+20 for specific numbers)
        if percentages or amounts:
            score += 20

        # Sentiment bonus (+10 for positive, -5 for negative)
        sentiment = row.get('sentiment', '')
        if sentiment == 'positive':
            score += 10
        elif sentiment == 'negative':
            score -= 5

        # Confidence bonus (+15 for high confidence use case classification)
        confidence = row.get('primary_use_case_confidence', 0)
        if confidence >= 0.8:
            score += 15
        elif confidence >= 0.6:
            score += 10

        # AI mention count bonus (+5 for detailed articles)
        ai_mentions = row.get('ai_mention_count', 0)
        if ai_mentions >= 5:
            score += 5

        return min(100, max(0, score))  # Clamp to 0-100

    def analyze_roi_impact(self) -> pd.DataFrame:
        """Analyze ROI impact across all articles."""
        roi_claims = []

        print("\n📊 Extracting ROI claims from articles...")
        for idx, row in self.df.iterrows():
            # Only analyze AI articles with content
            if row.get('ai_mention_count', 0) == 0:
                continue
            if pd.isna(row.get('summary')) or row.get('summary') == 'N/A':
                continue

            claim = self.extract_roi_claims(row)

            # Only include if we found some ROI indication
            if claim['has_percentage_claim'] or claim['has_amount_claim'] or claim['roi_type'] != 'general_improvement':
                roi_claims.append(claim)

        df = pd.DataFrame(roi_claims)
        print(f"✓ Extracted {len(df)} ROI claims from {len(self.df)} articles")

        return df

    def aggregate_by_company(self, roi_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate ROI claims by company."""
        company_stats = []

        for company_str in roi_df['company'].unique():
            if not company_str or pd.isna(company_str):
                continue

            # Handle comma-separated companies
            companies = [c.strip() for c in str(company_str).split(',') if c.strip()]

            for company in companies:
                company_rows = roi_df[roi_df['company'].str.contains(company, case=False, na=False)]

                if len(company_rows) == 0:
                    continue

                stats = {
                    'company': company,
                    'total_roi_claims': len(company_rows),
                    'claims_with_percentage': len(company_rows[company_rows['has_percentage_claim']]),
                    'claims_with_amount': len(company_rows[company_rows['has_amount_claim']]),
                    'avg_credibility': company_rows['credibility_score'].mean(),
                    'max_credibility': company_rows['credibility_score'].max(),
                    'cost_reduction_claims': len(company_rows[company_rows['roi_type'] == 'cost_reduction']),
                    'revenue_growth_claims': len(company_rows[company_rows['roi_type'] == 'revenue_growth']),
                    'time_savings_claims': len(company_rows[company_rows['roi_type'] == 'time_savings']),
                    'customer_impact_claims': len(company_rows[company_rows['roi_type'] == 'customer_impact']),
                    'primary_roi_type': company_rows['roi_type'].mode()[0] if len(company_rows) > 0 else '',
                    'most_common_use_case': company_rows['use_case'].mode()[0] if len(company_rows) > 0 else ''
                }

                company_stats.append(stats)

        df = pd.DataFrame(company_stats)
        df = df.sort_values('total_roi_claims', ascending=False)

        return df

    def aggregate_by_use_case(self, roi_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate ROI claims by use case."""
        use_case_stats = []

        for use_case in roi_df['use_case'].unique():
            if not use_case or pd.isna(use_case):
                continue

            uc_rows = roi_df[roi_df['use_case'] == use_case]

            stats = {
                'use_case': use_case,
                'roi_category': self.USE_CASE_ROI_CATEGORIES.get(use_case, 'Other'),
                'total_roi_claims': len(uc_rows),
                'avg_credibility': uc_rows['credibility_score'].mean(),
                'claims_with_percentage': len(uc_rows[uc_rows['has_percentage_claim']]),
                'claims_with_amount': len(uc_rows[uc_rows['has_amount_claim']]),
                'avg_percentage': uc_rows[uc_rows['has_percentage_claim']]['max_percentage'].mean(),
                'median_percentage': uc_rows[uc_rows['has_percentage_claim']]['max_percentage'].median(),
                'cost_reduction_claims': len(uc_rows[uc_rows['roi_type'] == 'cost_reduction']),
                'revenue_growth_claims': len(uc_rows[uc_rows['roi_type'] == 'revenue_growth']),
                'time_savings_claims': len(uc_rows[uc_rows['roi_type'] == 'time_savings']),
                'unique_companies': len([c for c in uc_rows['company'].unique() if c and not pd.isna(c)])
            }

            use_case_stats.append(stats)

        df = pd.DataFrame(use_case_stats)
        df = df.sort_values('total_roi_claims', ascending=False)

        return df

    def generate_reports(self):
        """Generate all ROI impact analysis reports."""
        print("\n" + "="*80)
        print("ROI IMPACT ANALYSIS")
        print("="*80)

        # Load data
        self.load_data()

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # 1. Extract ROI claims
        roi_df = self.analyze_roi_impact()

        if len(roi_df) == 0:
            print("\n⚠ No ROI claims found in articles")
            return None

        # Save detailed ROI claims
        roi_output = os.path.join(self.output_dir, "roi_impact_analysis.csv")
        roi_df.to_csv(roi_output, index=False)
        print(f"\n✓ Saved ROI claims to: {roi_output}")
        print(f"  - Total ROI claims: {len(roi_df)}")
        print(f"  - Claims with percentages: {len(roi_df[roi_df['has_percentage_claim']])} ({len(roi_df[roi_df['has_percentage_claim']])/len(roi_df)*100:.1f}%)")
        print(f"  - Claims with amounts: {len(roi_df[roi_df['has_amount_claim']])} ({len(roi_df[roi_df['has_amount_claim']])/len(roi_df)*100:.1f}%)")
        print(f"  - Average credibility: {roi_df['credibility_score'].mean():.1f}/100")

        # 2. Aggregate by company
        company_df = self.aggregate_by_company(roi_df)
        company_output = os.path.join(self.output_dir, "roi_by_company.csv")
        company_df.to_csv(company_output, index=False)
        print(f"\n✓ Saved company ROI analysis to: {company_output}")
        print(f"  - Companies with ROI claims: {len(company_df)}")
        if len(company_df) > 0:
            print(f"  - Top 5 companies by ROI claim count:")
            for _, row in company_df.head(5).iterrows():
                print(f"    - {row['company']}: {row['total_roi_claims']} claims "
                      f"(avg credibility: {row['avg_credibility']:.1f}/100, "
                      f"primary type: {row['primary_roi_type']})")

        # 3. Aggregate by use case
        use_case_df = self.aggregate_by_use_case(roi_df)
        use_case_output = os.path.join(self.output_dir, "roi_by_use_case.csv")
        use_case_df.to_csv(use_case_output, index=False)
        print(f"\n✓ Saved use case ROI analysis to: {use_case_output}")
        print(f"  - Use cases with ROI claims: {len(use_case_df)}")
        if len(use_case_df) > 0:
            print(f"  - Top 5 use cases by ROI claim count:")
            for _, row in use_case_df.head(5).iterrows():
                print(f"    - {row['roi_category']}: {row['total_roi_claims']} claims "
                      f"(avg credibility: {row['avg_credibility']:.1f}/100)")
                if not pd.isna(row.get('avg_percentage')):
                    print(f"      Average improvement: {row['avg_percentage']:.1f}%")

        print("\n" + "="*80)
        print("✓ ROI IMPACT ANALYSIS COMPLETE")
        print("="*80)

        return {
            'roi_claims': roi_df,
            'company_roi': company_df,
            'use_case_roi': use_case_df
        }


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze ROI impact from enhanced article analysis'
    )
    parser.add_argument('--input', type=str,
                       default='../02_analysis/pipelines/unified_ai_analysis_enhanced.csv',
                       help='Path to enhanced analysis CSV')
    parser.add_argument('--output-dir', type=str,
                       default='../03_processed_data',
                       help='Output directory for reports')

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = ROIImpactAnalyzer(
        enhanced_csv_path=args.input,
        output_dir=args.output_dir
    )

    # Generate reports
    try:
        results = analyzer.generate_reports()
        if results:
            print("\n✓ All ROI reports generated successfully!")
        else:
            print("\n⚠ No ROI claims found in data")
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease ensure you've run the enhanced LLM pipeline first:")
        print("  cd 02_analysis/pipelines")
        print("  python llm_analysis_pipeline_enhanced.py")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
