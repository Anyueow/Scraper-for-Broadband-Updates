#!/usr/bin/env python3
"""
UK Broadband AI Trends Analysis - Main Pipeline Orchestrator

Runs the complete analysis pipeline in waterfall manner:
1. Enhanced LLM Analysis (extract companies & technologies)
2. Tech Stack Analysis (vendor market share, maturity, build vs buy)
3. ROI Impact Analysis (extract and analyze ROI claims)
4. Visualizations (generate charts)

Usage:
    python main.py                    # Run full pipeline
    python main.py --skip-llm         # Skip LLM analysis (use existing CSV)
    python main.py --sample-size 10   # Run on sample data for testing
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import subprocess

class AnalysisPipeline:
    """Orchestrates the complete UK Broadband AI trends analysis pipeline."""

    def __init__(self, skip_llm=False, sample_size=None, verbose=True):
        """
        Initialize the pipeline.

        Args:
            skip_llm: Skip LLM analysis and use existing enhanced CSV
            sample_size: Limit analysis to N articles (for testing)
            verbose: Print detailed progress
        """
        self.skip_llm = skip_llm
        self.sample_size = sample_size
        self.verbose = verbose
        self.start_time = None
        self.results = {}

    def print_header(self, title):
        """Print a formatted section header."""
        if self.verbose:
            print("\n" + "="*80)
            print(f"  {title}")
            print("="*80)

    def print_step(self, step_num, step_name, status="RUNNING"):
        """Print step progress."""
        if self.verbose:
            symbols = {"RUNNING": "⏳", "COMPLETE": "✅", "SKIPPED": "⏭", "FAILED": "❌"}
            symbol = symbols.get(status, "•")
            print(f"\n{symbol} Step {step_num}: {step_name}")
            if status == "RUNNING":
                print("-" * 80)

    def run_command(self, cmd, cwd=None, description=""):
        """Run a subprocess command and capture output."""
        try:
            if self.verbose and description:
                print(f"Running: {description}")

            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )

            if self.verbose and result.stdout:
                # Print last 20 lines of output
                lines = result.stdout.strip().split('\n')
                for line in lines[-20:]:
                    print(f"  {line}")

            return True, result.stdout

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error running command:")
            print(f"  Command: {' '.join(cmd)}")
            print(f"  Exit code: {e.returncode}")
            if e.stdout:
                print(f"  Output: {e.stdout[-500:]}")
            if e.stderr:
                print(f"  Error: {e.stderr[-500:]}")
            return False, str(e)

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False, str(e)

    def step_1_enhanced_llm_analysis(self):
        """Step 1: Run enhanced LLM analysis to extract companies and technologies."""
        self.print_step(1, "Enhanced LLM Analysis (Company & Technology Extraction)",
                       "SKIPPED" if self.skip_llm else "RUNNING")

        if self.skip_llm:
            # Check if enhanced CSV exists
            enhanced_csv = Path("02_analysis/pipelines/unified_ai_analysis_enhanced.csv")
            if enhanced_csv.exists():
                print(f"  Using existing enhanced CSV: {enhanced_csv}")
                self.results['llm_csv'] = str(enhanced_csv)
                return True
            else:
                print(f"  ❌ Enhanced CSV not found: {enhanced_csv}")
                print("  Cannot skip LLM analysis - file doesn't exist")
                return False

        # Run enhanced LLM pipeline
        success, output = self.run_command(
            ["python", "llm_analysis_pipeline_enhanced.py"],
            cwd="02_analysis/pipelines",
            description="Processing articles through enhanced LLM pipeline..."
        )

        if success:
            self.print_step(1, "Enhanced LLM Analysis", "COMPLETE")
            self.results['llm_csv'] = "02_analysis/pipelines/unified_ai_analysis_enhanced.csv"
        else:
            self.print_step(1, "Enhanced LLM Analysis", "FAILED")

        return success

    def step_2_tech_stack_analysis(self):
        """Step 2: Analyze technology adoption patterns."""
        self.print_step(2, "Tech Stack Analysis (Vendor Market Share, Maturity, Build vs Buy)", "RUNNING")

        success, output = self.run_command(
            ["python", "tech_stack_analysis.py"],
            cwd="04_advanced_analysis",
            description="Analyzing technology adoption patterns..."
        )

        if success:
            self.print_step(2, "Tech Stack Analysis", "COMPLETE")
            self.results['tech_outputs'] = [
                "03_processed_data/technology_mentions.csv",
                "03_processed_data/vendor_market_share.csv",
                "03_processed_data/build_vs_buy_analysis.csv"
            ]
        else:
            self.print_step(2, "Tech Stack Analysis", "FAILED")

        return success

    def step_3_roi_impact_analysis(self):
        """Step 3: Extract and analyze ROI claims."""
        self.print_step(3, "ROI Impact Analysis (Extract and Quantify Business Impact)", "RUNNING")

        success, output = self.run_command(
            ["python", "roi_impact_analysis.py"],
            cwd="04_advanced_analysis",
            description="Extracting ROI claims from articles..."
        )

        if success:
            self.print_step(3, "ROI Impact Analysis", "COMPLETE")
            self.results['roi_outputs'] = [
                "03_processed_data/roi_impact_analysis.csv",
                "03_processed_data/roi_by_company.csv",
                "03_processed_data/roi_by_use_case.csv"
            ]
        else:
            self.print_step(3, "ROI Impact Analysis", "FAILED")

        return success

    def step_4_visualizations(self):
        """Step 4: Generate visualizations."""
        self.print_step(4, "Generate Visualizations (Tech Stack Charts)", "RUNNING")

        success, output = self.run_command(
            ["python", "tech_stack_visualizations.py"],
            cwd="05_visualizations",
            description="Creating technology stack visualizations..."
        )

        if success:
            self.print_step(4, "Generate Visualizations", "COMPLETE")
            self.results['viz_dir'] = "06_outputs/visualizations"
        else:
            self.print_step(4, "Generate Visualizations", "FAILED")

        return success

    def generate_final_report(self):
        """Generate a summary report of the analysis."""
        self.print_header("GENERATING FINAL SUMMARY REPORT")

        try:
            # Load key results
            import pandas as pd

            report = []
            report.append("="*80)
            report.append("UK BROADBAND AI TRENDS ANALYSIS - FINAL REPORT")
            report.append("="*80)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")

            # 1. Tech Stack Summary
            if os.path.exists("03_processed_data/technology_mentions.csv"):
                tech_df = pd.read_csv("03_processed_data/technology_mentions.csv")
                report.append("1. TECHNOLOGY STACK ANALYSIS")
                report.append("-" * 80)
                report.append(f"  Total unique technologies found: {len(tech_df)}")
                report.append(f"  Top 5 technologies:")
                for idx, row in tech_df.head(5).iterrows():
                    report.append(f"    {idx+1}. {row['technology']} - {row['article_count']} articles ({row['adoption_rate_pct']:.1f}% adoption)")
                report.append("")

            # 2. Vendor Market Share
            if os.path.exists("03_processed_data/vendor_market_share.csv"):
                vendor_df = pd.read_csv("03_processed_data/vendor_market_share.csv")
                if len(vendor_df) > 0:
                    report.append("2. VENDOR MARKET SHARE")
                    report.append("-" * 80)
                    report.append(f"  Total vendors identified: {len(vendor_df)}")
                    report.append(f"  Top 5 vendors:")
                    for idx, row in vendor_df.head(5).iterrows():
                        report.append(f"    {idx+1}. {row['vendor']} - {row['mention_count']} mentions ({row['market_share_pct']:.1f}% market share)")
                    report.append("")

            # 3. Build vs Buy
            if os.path.exists("03_processed_data/build_vs_buy_analysis.csv"):
                build_buy_df = pd.read_csv("03_processed_data/build_vs_buy_analysis.csv")
                if len(build_buy_df) > 0:
                    report.append("3. BUILD VS BUY STRATEGY")
                    report.append("-" * 80)
                    report.append(f"  Companies analyzed: {len(build_buy_df)}")
                    avg_build = build_buy_df['build_pct'].mean()
                    avg_buy = build_buy_df['buy_pct'].mean()
                    avg_hybrid = build_buy_df['hybrid_pct'].mean()
                    report.append(f"  Industry average: {avg_build:.1f}% Build, {avg_buy:.1f}% Buy, {avg_hybrid:.1f}% Hybrid")
                    report.append(f"  Top 5 companies by AI activity:")
                    for idx, row in build_buy_df.head(5).iterrows():
                        report.append(f"    - {row['company']}: {row['total_articles']} articles")
                    report.append("")

            # 4. ROI Impact
            if os.path.exists("03_processed_data/roi_impact_analysis.csv"):
                roi_df = pd.read_csv("03_processed_data/roi_impact_analysis.csv")
                if len(roi_df) > 0:
                    report.append("4. ROI IMPACT ANALYSIS")
                    report.append("-" * 80)
                    report.append(f"  Total ROI claims found: {len(roi_df)}")
                    claims_with_pct = len(roi_df[roi_df['has_percentage_claim'] == True])
                    claims_with_amt = len(roi_df[roi_df['has_amount_claim'] == True])
                    report.append(f"  Claims with percentage metrics: {claims_with_pct}")
                    report.append(f"  Claims with monetary amounts: {claims_with_amt}")
                    avg_cred = roi_df['credibility_score'].mean()
                    report.append(f"  Average credibility score: {avg_cred:.1f}/100")
                    report.append("")

            # 5. Use Case Summary
            if os.path.exists("03_processed_data/roi_by_use_case.csv"):
                use_case_df = pd.read_csv("03_processed_data/roi_by_use_case.csv")
                if len(use_case_df) > 0:
                    report.append("5. ROI BY USE CASE")
                    report.append("-" * 80)
                    for idx, row in use_case_df.head(5).iterrows():
                        report.append(f"  - {row['roi_category']}: {row['total_roi_claims']} ROI claims")
                        if not pd.isna(row.get('avg_percentage')):
                            report.append(f"    Average improvement: {row['avg_percentage']:.1f}%")
                    report.append("")

            # 6. Output Files
            report.append("6. OUTPUT FILES GENERATED")
            report.append("-" * 80)
            output_files = [
                "02_analysis/pipelines/unified_ai_analysis_enhanced.csv",
                "03_processed_data/technology_mentions.csv",
                "03_processed_data/vendor_market_share.csv",
                "03_processed_data/build_vs_buy_analysis.csv",
                "03_processed_data/roi_impact_analysis.csv",
                "03_processed_data/roi_by_company.csv",
                "03_processed_data/roi_by_use_case.csv",
            ]
            for file in output_files:
                if os.path.exists(file):
                    size_kb = os.path.getsize(file) / 1024
                    report.append(f"  ✓ {file} ({size_kb:.1f} KB)")

            viz_dir = "06_outputs/visualizations"
            if os.path.exists(viz_dir):
                viz_files = [f for f in os.listdir(viz_dir) if f.endswith('.png')]
                if viz_files:
                    report.append(f"  ✓ {len(viz_files)} visualization(s) in {viz_dir}")

            report.append("")
            report.append("="*80)
            report.append("ANALYSIS PIPELINE COMPLETE")
            report.append("="*80)

            # Save report
            report_path = "06_outputs/FINAL_ANALYSIS_REPORT.txt"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w') as f:
                f.write('\n'.join(report))

            # Print report
            print('\n'.join(report))
            print(f"\n📄 Full report saved to: {report_path}")

            return True

        except Exception as e:
            print(f"❌ Error generating final report: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self):
        """Run the complete analysis pipeline."""
        self.start_time = time.time()

        self.print_header("UK BROADBAND AI TRENDS ANALYSIS PIPELINE")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Configuration:")
        print(f"  - Skip LLM Analysis: {self.skip_llm}")
        print(f"  - Sample Size: {self.sample_size or 'Full dataset'}")

        # Run pipeline steps
        steps = [
            ("Enhanced LLM Analysis", self.step_1_enhanced_llm_analysis),
            ("Tech Stack Analysis", self.step_2_tech_stack_analysis),
            ("ROI Impact Analysis", self.step_3_roi_impact_analysis),
            ("Generate Visualizations", self.step_4_visualizations),
        ]

        failed_steps = []

        for step_name, step_func in steps:
            try:
                success = step_func()
                if not success:
                    failed_steps.append(step_name)
                    print(f"\n⚠ Warning: {step_name} failed, but continuing pipeline...")
            except Exception as e:
                print(f"\n❌ Critical error in {step_name}: {e}")
                import traceback
                traceback.print_exc()
                failed_steps.append(step_name)

        # Generate final report
        self.generate_final_report()

        # Summary
        elapsed_time = time.time() - self.start_time
        self.print_header("PIPELINE SUMMARY")
        print(f"Total execution time: {elapsed_time/60:.1f} minutes")
        print(f"Steps completed: {len(steps) - len(failed_steps)}/{len(steps)}")

        if failed_steps:
            print(f"\n⚠ Failed steps ({len(failed_steps)}):")
            for step in failed_steps:
                print(f"  - {step}")
        else:
            print("\n✅ All pipeline steps completed successfully!")

        print("\n" + "="*80)
        return len(failed_steps) == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='UK Broadband AI Trends Analysis - Complete Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Run full pipeline
  python main.py --skip-llm          # Skip LLM analysis (use existing CSV)
  python main.py --sample-size 100   # Test on 100 articles
  python main.py --quiet             # Minimal output

Pipeline Steps:
  1. Enhanced LLM Analysis - Extract companies & technologies from articles
  2. Tech Stack Analysis - Analyze vendor market share, maturity, build vs buy
  3. ROI Impact Analysis - Extract and quantify ROI claims
  4. Visualizations - Generate charts and graphs

Outputs:
  - 02_analysis/pipelines/unified_ai_analysis_enhanced.csv
  - 03_processed_data/*.csv (technology, vendor, ROI analyses)
  - 06_outputs/visualizations/*.png (charts)
  - 06_outputs/FINAL_ANALYSIS_REPORT.txt (summary report)
        """
    )

    parser.add_argument('--skip-llm', action='store_true',
                       help='Skip LLM analysis and use existing enhanced CSV')
    parser.add_argument('--sample-size', type=int, default=None,
                       help='Limit analysis to N articles (for testing)')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimize output')

    args = parser.parse_args()

    # Initialize and run pipeline
    pipeline = AnalysisPipeline(
        skip_llm=args.skip_llm,
        sample_size=args.sample_size,
        verbose=not args.quiet
    )

    try:
        success = pipeline.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
