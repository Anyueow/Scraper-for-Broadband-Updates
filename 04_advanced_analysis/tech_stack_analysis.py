"""
Technology Stack Analysis Script

Analyzes AI technology adoption patterns from enhanced LLM pipeline output.
Produces vendor market share, technology maturity curves, and build vs buy analysis.

Input: unified_ai_analysis_enhanced.csv
Outputs:
- technology_mentions.csv
- vendor_market_share.csv
- build_vs_buy_analysis.csv
"""

import pandas as pd
import json
import os
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import sys

class TechStackAnalyzer:
    """Analyzes technology adoption patterns from article data."""

    def __init__(self,
                 enhanced_csv_path: str = "../02_analysis/pipelines/unified_ai_analysis_enhanced.csv",
                 tech_taxonomy_path: str = "../02_analysis/configs/technology_taxonomy.json",
                 output_dir: str = "../03_processed_data"):
        """
        Initialize the analyzer.

        Args:
            enhanced_csv_path: Path to enhanced analysis CSV
            tech_taxonomy_path: Path to technology taxonomy config
            output_dir: Directory for output files
        """
        self.enhanced_csv_path = enhanced_csv_path
        self.tech_taxonomy_path = tech_taxonomy_path
        self.output_dir = output_dir
        self.tech_taxonomy = self._load_taxonomy()
        self.df = None

    def _load_taxonomy(self) -> Dict:
        """Load technology taxonomy configuration."""
        try:
            with open(self.tech_taxonomy_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load technology taxonomy: {e}")
            return {}

    def load_data(self) -> pd.DataFrame:
        """Load enhanced analysis data."""
        if not os.path.exists(self.enhanced_csv_path):
            raise FileNotFoundError(f"Enhanced CSV not found: {self.enhanced_csv_path}")

        self.df = pd.read_csv(self.enhanced_csv_path)
        print(f"✓ Loaded {len(self.df)} articles from enhanced analysis")

        # Filter to only articles with AI content
        ai_articles = self.df[self.df['ai_mention_count'] > 0]
        print(f"✓ Found {len(ai_articles)} articles with AI content")

        return self.df

    def extract_all_technologies(self) -> pd.DataFrame:
        """
        Extract all technology mentions across all categories.

        Returns:
            DataFrame with columns: technology, category, mention_count, article_count
        """
        tech_counts = defaultdict(lambda: {'category': '', 'articles': set()})

        # Process each row
        for _, row in self.df.iterrows():
            # Skip articles without AI content
            if row['ai_mention_count'] == 0:
                continue

            # Extract from each technology category
            categories = [
                ('foundation_models', row.get('technologies_foundation_models', '')),
                ('platforms', row.get('technologies_platforms', '')),
                ('infrastructure', row.get('technologies_infrastructure', '')),
                ('techniques', row.get('technologies_techniques', ''))
            ]

            for category_name, tech_string in categories:
                if pd.isna(tech_string) or tech_string == '':
                    continue

                # Split comma-separated technologies
                technologies = [t.strip() for t in str(tech_string).split(',') if t.strip()]

                for tech in technologies:
                    tech_counts[tech]['category'] = category_name
                    tech_counts[tech]['articles'].add(row['url'])

        # Convert to DataFrame
        rows = []
        for tech, data in tech_counts.items():
            rows.append({
                'technology': tech,
                'category': data['category'],
                'article_count': len(data['articles']),
                'mention_count': len(data['articles'])  # Simplified: 1 mention per article
            })

        df = pd.DataFrame(rows)
        df = df.sort_values('article_count', ascending=False)

        return df

    def analyze_vendor_market_share(self) -> pd.DataFrame:
        """
        Analyze vendor market share based on mentions.

        Returns:
            DataFrame with vendor market share data
        """
        # Extract vendor-specific technologies (platforms and foundation models)
        vendor_counts = defaultdict(lambda: {'articles': set(), 'category': ''})

        for _, row in self.df.iterrows():
            if row['ai_mention_count'] == 0:
                continue

            # Foundation models
            models = str(row.get('technologies_foundation_models', ''))
            if models and models != 'nan':
                for model in [m.strip() for m in models.split(',') if m.strip()]:
                    vendor_counts[model]['articles'].add(row['url'])
                    vendor_counts[model]['category'] = 'foundation_models'

            # Platforms
            platforms = str(row.get('technologies_platforms', ''))
            if platforms and platforms != 'nan':
                for platform in [p.strip() for p in platforms.split(',') if p.strip()]:
                    vendor_counts[platform]['articles'].add(row['url'])
                    vendor_counts[platform]['category'] = 'platforms'

        # Convert to DataFrame
        rows = []
        total_articles = len(self.df[self.df['ai_mention_count'] > 0])

        for vendor, data in vendor_counts.items():
            mention_count = len(data['articles'])
            market_share = (mention_count / total_articles * 100) if total_articles > 0 else 0

            rows.append({
                'vendor': vendor,
                'category': data['category'],
                'mention_count': mention_count,
                'market_share_pct': round(market_share, 2),
                'rank': 0  # Will be set after sorting
            })

        df = pd.DataFrame(rows)

        # Only sort if we have data
        if len(df) > 0:
            df = df.sort_values('mention_count', ascending=False)
            df['rank'] = range(1, len(df) + 1)

        return df

    def classify_technology_maturity(self) -> pd.DataFrame:
        """
        Classify technologies by maturity level using taxonomy.

        Returns:
            DataFrame with technology maturity classification
        """
        # Get technology mentions
        tech_df = self.extract_all_technologies()

        # Load maturity classifications from taxonomy
        maturity_map = {}
        if 'maturity_classification' in self.tech_taxonomy:
            for maturity_level, techs in self.tech_taxonomy['maturity_classification'].items():
                # Skip metadata fields
                if maturity_level.startswith('_'):
                    continue
                if isinstance(techs, list):
                    for tech in techs:
                        maturity_map[tech.lower()] = maturity_level

        # Classify each technology
        def get_maturity(tech_name):
            tech_lower = tech_name.lower()

            # Direct match
            if tech_lower in maturity_map:
                return maturity_map[tech_lower]

            # Partial match
            for pattern, level in maturity_map.items():
                if pattern in tech_lower or tech_lower in pattern:
                    return level

            # Default classification based on mention count
            # More mentions = more mainstream
            return 'emerging'

        tech_df['maturity'] = tech_df['technology'].apply(get_maturity)

        # Calculate adoption rate (percentage of AI articles mentioning this tech)
        total_ai_articles = len(self.df[self.df['ai_mention_count'] > 0])
        tech_df['adoption_rate_pct'] = (tech_df['article_count'] / total_ai_articles * 100).round(2)

        return tech_df

    def analyze_build_vs_buy(self) -> pd.DataFrame:
        """
        Analyze build vs buy patterns from technology mentions.

        Returns:
            DataFrame with build vs buy breakdown by company
        """
        # Load build vs buy indicators from taxonomy
        build_indicators = self.tech_taxonomy.get('build_vs_buy_indicators', {})
        build_terms = build_indicators.get('build_internal', [])
        buy_terms = build_indicators.get('buy_external', [])
        hybrid_terms = build_indicators.get('hybrid', [])

        # Analyze by company
        company_patterns = defaultdict(lambda: {'build': 0, 'buy': 0, 'hybrid': 0, 'articles': set()})

        for _, row in self.df.iterrows():
            if row['ai_mention_count'] == 0:
                continue

            # Get companies mentioned
            companies = str(row.get('companies_mentioned', ''))
            if companies and companies != 'nan':
                company_list = [c.strip() for c in companies.split(',') if c.strip()]

                # Get article summary/content to check for build vs buy indicators
                summary = str(row.get('summary', '')).lower()
                content = str(row.get('content', '')).lower() if 'content' in row else ''
                text = f"{summary} {content}"

                # Check for indicators
                is_build = any(term.lower() in text for term in build_terms)
                is_buy = any(term.lower() in text for term in buy_terms)
                is_hybrid = any(term.lower() in text for term in hybrid_terms)

                for company in company_list:
                    company_patterns[company]['articles'].add(row['url'])
                    if is_hybrid:
                        company_patterns[company]['hybrid'] += 1
                    elif is_build:
                        company_patterns[company]['build'] += 1
                    elif is_buy:
                        company_patterns[company]['buy'] += 1

        # Convert to DataFrame
        rows = []
        for company, data in company_patterns.items():
            total = data['build'] + data['buy'] + data['hybrid']
            if total > 0:
                rows.append({
                    'company': company,
                    'build_count': data['build'],
                    'buy_count': data['buy'],
                    'hybrid_count': data['hybrid'],
                    'total_articles': len(data['articles']),
                    'build_pct': round(data['build'] / total * 100, 1),
                    'buy_pct': round(data['buy'] / total * 100, 1),
                    'hybrid_pct': round(data['hybrid'] / total * 100, 1)
                })

        df = pd.DataFrame(rows)
        df = df.sort_values('total_articles', ascending=False)

        return df

    def generate_reports(self):
        """Generate all analysis reports."""
        print("\n" + "="*80)
        print("TECHNOLOGY STACK ANALYSIS")
        print("="*80)

        # Load data
        self.load_data()

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # 1. Technology Mentions
        print("\n📊 Analyzing technology mentions...")
        tech_mentions_df = self.classify_technology_maturity()
        tech_output = os.path.join(self.output_dir, "technology_mentions.csv")
        tech_mentions_df.to_csv(tech_output, index=False)
        print(f"✓ Saved technology mentions to: {tech_output}")
        print(f"  - Total unique technologies: {len(tech_mentions_df)}")
        print(f"  - Top 5 technologies:")
        for idx, row in tech_mentions_df.head(5).iterrows():
            print(f"    {row['rank'] if 'rank' in row else idx+1}. {row['technology']} "
                  f"({row['article_count']} articles, {row['adoption_rate_pct']}% adoption, "
                  f"{row['maturity']} maturity)")

        # 2. Vendor Market Share
        print("\n📊 Analyzing vendor market share...")
        vendor_df = self.analyze_vendor_market_share()
        vendor_output = os.path.join(self.output_dir, "vendor_market_share.csv")
        vendor_df.to_csv(vendor_output, index=False)
        print(f"✓ Saved vendor market share to: {vendor_output}")
        print(f"  - Total unique vendors: {len(vendor_df)}")
        print(f"  - Top 5 vendors:")
        for _, row in vendor_df.head(5).iterrows():
            print(f"    {row['rank']}. {row['vendor']} - {row['mention_count']} mentions "
                  f"({row['market_share_pct']}% market share)")

        # 3. Build vs Buy Analysis
        print("\n📊 Analyzing build vs buy patterns...")
        build_buy_df = self.analyze_build_vs_buy()
        build_buy_output = os.path.join(self.output_dir, "build_vs_buy_analysis.csv")
        build_buy_df.to_csv(build_buy_output, index=False)
        print(f"✓ Saved build vs buy analysis to: {build_buy_output}")
        print(f"  - Companies analyzed: {len(build_buy_df)}")
        if len(build_buy_df) > 0:
            print(f"  - Top 5 companies by AI article count:")
            for _, row in build_buy_df.head(5).iterrows():
                print(f"    - {row['company']}: {row['total_articles']} articles "
                      f"(Build: {row['build_pct']}%, Buy: {row['buy_pct']}%, Hybrid: {row['hybrid_pct']}%)")

        print("\n" + "="*80)
        print("✓ TECH STACK ANALYSIS COMPLETE")
        print("="*80)

        return {
            'technology_mentions': tech_mentions_df,
            'vendor_market_share': vendor_df,
            'build_vs_buy': build_buy_df
        }


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze technology stack adoption patterns'
    )
    parser.add_argument('--input', type=str,
                       default='../02_analysis/pipelines/unified_ai_analysis_enhanced.csv',
                       help='Path to enhanced analysis CSV')
    parser.add_argument('--output-dir', type=str,
                       default='../03_processed_data',
                       help='Output directory for reports')
    parser.add_argument('--taxonomy', type=str,
                       default='../02_analysis/configs/technology_taxonomy.json',
                       help='Path to technology taxonomy JSON')

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = TechStackAnalyzer(
        enhanced_csv_path=args.input,
        tech_taxonomy_path=args.taxonomy,
        output_dir=args.output_dir
    )

    # Generate reports
    try:
        results = analyzer.generate_reports()
        print("\n✓ All reports generated successfully!")
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease ensure you've run the enhanced LLM pipeline first:")
        print("  cd 02_analysis/pipelines")
        print("  python llm_analysis_pipeline_enhanced.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
