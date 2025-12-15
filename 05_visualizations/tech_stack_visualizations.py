"""
Technology Stack Visualizations

Generates charts and visualizations for tech stack analysis results.
Creates static images that can be used in reports or presentations.

Input: technology_mentions.csv, vendor_market_share.csv, build_vs_buy_analysis.csv
Output: PNG charts in 06_outputs/visualizations/
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class TechStackVisualizer:
    """Creates visualizations for technology stack analysis."""

    def __init__(self,
                 data_dir: str = "../03_processed_data",
                 output_dir: str = "../06_outputs/visualizations"):
        """
        Initialize the visualizer.

        Args:
            data_dir: Directory containing analysis CSV files
            output_dir: Directory for output visualizations
        """
        self.data_dir = data_dir
        self.output_dir = output_dir

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10

    def load_data(self) -> dict:
        """Load all tech stack analysis data."""
        data = {}

        # Technology mentions
        tech_path = os.path.join(self.data_dir, "technology_mentions.csv")
        if os.path.exists(tech_path):
            data['technology'] = pd.read_csv(tech_path)
            print(f"✓ Loaded technology mentions: {len(data['technology'])} technologies")
        else:
            print(f"⚠ Technology mentions not found: {tech_path}")

        # Vendor market share
        vendor_path = os.path.join(self.data_dir, "vendor_market_share.csv")
        if os.path.exists(vendor_path):
            data['vendor'] = pd.read_csv(vendor_path)
            print(f"✓ Loaded vendor market share: {len(data['vendor'])} vendors")
        else:
            print(f"⚠ Vendor market share not found: {vendor_path}")

        # Build vs buy
        build_buy_path = os.path.join(self.data_dir, "build_vs_buy_analysis.csv")
        if os.path.exists(build_buy_path):
            data['build_buy'] = pd.read_csv(build_buy_path)
            print(f"✓ Loaded build vs buy: {len(data['build_buy'])} companies")
        else:
            print(f"⚠ Build vs buy not found: {build_buy_path}")

        return data

    def create_vendor_market_share_chart(self, vendor_df: pd.DataFrame) -> str:
        """Create vendor market share pie chart."""
        if len(vendor_df) == 0:
            print("⚠ No vendor data to visualize")
            return None

        # Top 10 vendors
        top_vendors = vendor_df.head(10)

        fig, ax = plt.subplots(figsize=(12, 8))

        colors = sns.color_palette("Set3", len(top_vendors))

        wedges, texts, autotexts = ax.pie(
            top_vendors['mention_count'],
            labels=top_vendors['vendor'],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )

        # Improve text readability
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_weight('bold')

        ax.set_title('Top 10 AI Vendors by Mention Count in UK Telco Articles',
                     fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        # Save
        output_path = os.path.join(self.output_dir, "vendor_market_share.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved vendor market share chart: {output_path}")
        return output_path

    def create_technology_bar_chart(self, tech_df: pd.DataFrame) -> str:
        """Create technology mentions bar chart."""
        if len(tech_df) == 0:
            print("⚠ No technology data to visualize")
            return None

        # Top 15 technologies
        top_tech = tech_df.head(15).sort_values('article_count')

        fig, ax = plt.subplots(figsize=(12, 10))

        # Color by category
        category_colors = {
            'foundation_models': '#FF6B6B',
            'platforms': '#4ECDC4',
            'infrastructure': '#45B7D1',
            'techniques': '#FFA07A'
        }

        colors = [category_colors.get(cat, '#95E1D3') for cat in top_tech['category']]

        bars = ax.barh(range(len(top_tech)), top_tech['article_count'], color=colors)

        ax.set_yticks(range(len(top_tech)))
        ax.set_yticklabels(top_tech['technology'])
        ax.set_xlabel('Number of Articles', fontsize=12, fontweight='bold')
        ax.set_title('Top 15 AI Technologies Mentioned in UK Telco Articles',
                     fontsize=14, fontweight='bold', pad=20)

        # Add value labels
        for i, (idx, row) in enumerate(top_tech.iterrows()):
            ax.text(row['article_count'] + 0.1, i, f"{row['article_count']}",
                   va='center', fontsize=9)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=cat.replace('_', ' ').title())
                          for cat, color in category_colors.items()]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

        plt.tight_layout()

        # Save
        output_path = os.path.join(self.output_dir, "technology_mentions_bar.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved technology bar chart: {output_path}")
        return output_path

    def create_maturity_adoption_scatter(self, tech_df: pd.DataFrame) -> str:
        """Create technology maturity vs adoption scatter plot."""
        if len(tech_df) == 0 or 'maturity' not in tech_df.columns:
            print("⚠ No maturity data to visualize")
            return None

        fig, ax = plt.subplots(figsize=(12, 8))

        # Map maturity to numeric values for y-axis
        maturity_order = {'emerging': 1, 'growing': 2, 'mainstream': 3}
        tech_df['maturity_numeric'] = tech_df['maturity'].map(maturity_order)

        # Filter out any with missing maturity
        tech_df_clean = tech_df[tech_df['maturity_numeric'].notna()]

        if len(tech_df_clean) == 0:
            print("⚠ No valid maturity data")
            return None

        # Color by category
        category_colors = {
            'foundation_models': '#FF6B6B',
            'platforms': '#4ECDC4',
            'infrastructure': '#45B7D1',
            'techniques': '#FFA07A'
        }

        for category in tech_df_clean['category'].unique():
            cat_data = tech_df_clean[tech_df_clean['category'] == category]
            ax.scatter(
                cat_data['adoption_rate_pct'],
                cat_data['maturity_numeric'],
                s=cat_data['article_count'] * 50,
                alpha=0.6,
                color=category_colors.get(category, '#95E1D3'),
                label=category.replace('_', ' ').title(),
                edgecolors='black',
                linewidth=0.5
            )

        ax.set_xlabel('Adoption Rate (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Technology Maturity', fontsize=12, fontweight='bold')
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(['Emerging', 'Growing', 'Mainstream'])
        ax.set_title('Technology Maturity vs. Adoption Rate\n(Bubble size = article mentions)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save
        output_path = os.path.join(self.output_dir, "maturity_adoption_scatter.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved maturity vs adoption scatter: {output_path}")
        return output_path

    def create_build_vs_buy_chart(self, build_buy_df: pd.DataFrame) -> str:
        """Create build vs buy stacked bar chart."""
        if len(build_buy_df) == 0:
            print("⚠ No build vs buy data to visualize")
            return None

        # Top 10 companies by article count
        top_companies = build_buy_df.head(10).sort_values('total_articles')

        fig, ax = plt.subplots(figsize=(12, 8))

        # Stacked bar chart
        bar_width = 0.8
        indices = range(len(top_companies))

        # Build bars
        p1 = ax.barh(indices, top_companies['build_pct'], bar_width,
                     label='Build (In-house)', color='#4ECDC4')

        # Buy bars (stacked on top of build)
        p2 = ax.barh(indices, top_companies['buy_pct'], bar_width,
                     left=top_companies['build_pct'],
                     label='Buy (External)', color='#FF6B6B')

        # Hybrid bars (stacked on top of buy)
        p3 = ax.barh(indices, top_companies['hybrid_pct'], bar_width,
                     left=top_companies['build_pct'] + top_companies['buy_pct'],
                     label='Hybrid', color='#FFA07A')

        ax.set_yticks(indices)
        ax.set_yticklabels(top_companies['company'])
        ax.set_xlabel('Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_title('Build vs Buy Strategy by Company\n(Based on Article Analysis)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='lower right', fontsize=10)
        ax.set_xlim(0, 100)

        # Add article count annotations
        for i, (idx, row) in enumerate(top_companies.iterrows()):
            ax.text(102, i, f"n={row['total_articles']}", va='center',
                   fontsize=8, style='italic')

        plt.tight_layout()

        # Save
        output_path = os.path.join(self.output_dir, "build_vs_buy_stacked.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved build vs buy chart: {output_path}")
        return output_path

    def create_category_distribution_pie(self, tech_df: pd.DataFrame) -> str:
        """Create technology category distribution pie chart."""
        if len(tech_df) == 0:
            print("⚠ No technology data to visualize")
            return None

        # Aggregate by category
        category_counts = tech_df.groupby('category')['article_count'].sum().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 8))

        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#95E1D3']

        wedges, texts, autotexts = ax.pie(
            category_counts.values,
            labels=[cat.replace('_', ' ').title() for cat in category_counts.index],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(category_counts)]
        )

        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')

        ax.set_title('AI Technology Category Distribution\n(by total article mentions)',
                     fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        # Save
        output_path = os.path.join(self.output_dir, "category_distribution.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved category distribution chart: {output_path}")
        return output_path

    def generate_all_visualizations(self):
        """Generate all technology stack visualizations."""
        print("\n" + "="*80)
        print("TECHNOLOGY STACK VISUALIZATIONS")
        print("="*80)

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Load data
        data = self.load_data()

        if len(data) == 0:
            print("\n✗ No data available for visualization")
            print("Please run tech_stack_analysis.py first")
            return None

        created_charts = []

        # 1. Vendor Market Share
        if 'vendor' in data and len(data['vendor']) > 0:
            chart = self.create_vendor_market_share_chart(data['vendor'])
            if chart:
                created_charts.append(chart)

        # 2. Technology Bar Chart
        if 'technology' in data and len(data['technology']) > 0:
            chart = self.create_technology_bar_chart(data['technology'])
            if chart:
                created_charts.append(chart)

        # 3. Maturity vs Adoption
        if 'technology' in data and len(data['technology']) > 0:
            chart = self.create_maturity_adoption_scatter(data['technology'])
            if chart:
                created_charts.append(chart)

        # 4. Build vs Buy
        if 'build_buy' in data and len(data['build_buy']) > 0:
            chart = self.create_build_vs_buy_chart(data['build_buy'])
            if chart:
                created_charts.append(chart)

        # 5. Category Distribution
        if 'technology' in data and len(data['technology']) > 0:
            chart = self.create_category_distribution_pie(data['technology'])
            if chart:
                created_charts.append(chart)

        print("\n" + "="*80)
        print(f"✓ VISUALIZATION COMPLETE - {len(created_charts)} charts created")
        print("="*80)
        print(f"\nCharts saved to: {self.output_dir}")
        for chart in created_charts:
            print(f"  - {os.path.basename(chart)}")

        return created_charts


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate technology stack visualizations'
    )
    parser.add_argument('--data-dir', type=str,
                       default='../03_processed_data',
                       help='Directory containing analysis CSV files')
    parser.add_argument('--output-dir', type=str,
                       default='../06_outputs/visualizations',
                       help='Output directory for charts')

    args = parser.parse_args()

    # Initialize visualizer
    visualizer = TechStackVisualizer(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )

    # Generate visualizations
    try:
        charts = visualizer.generate_all_visualizations()
        if charts:
            print("\n✓ All visualizations generated successfully!")
            return 0
        else:
            print("\n⚠ No visualizations could be created")
            print("Please ensure tech stack analysis has been run first:")
            print("  cd 04_advanced_analysis")
            print("  python tech_stack_analysis.py")
            return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
