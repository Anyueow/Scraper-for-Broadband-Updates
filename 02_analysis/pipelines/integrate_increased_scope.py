#!/usr/bin/env python3
"""
Integrate Increased Scope CSV into Unified Analysis
====================================================

This script merges the increased_scope.csv (expanded company and geographic coverage)
into the existing unified_ai_analysis.csv master dataset.

Purpose:
- Integrate manually curated articles covering B2B infrastructure companies
- Expand geographic scope beyond UK (Europe, North America)
- Maintain data integrity (no duplicates, consistent schema)

Usage:
    python integrate_increased_scope.py

Author: Telco AI Analysis Project
Date: December 2025
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

# Input files
INCREASED_SCOPE_CSV = Path("../../01_data_collection/manual_inputs/increased_scope.csv")
UNIFIED_ANALYSIS_CSV = Path("../../03_processed_data/unified_ai_analysis.csv")

# Output files
OUTPUT_CSV = Path("../../03_processed_data/unified_ai_analysis.csv")
BACKUP_CSV = Path("../../03_processed_data/unified_ai_analysis_backup_{timestamp}.csv")
INTEGRATION_REPORT = Path("../../03_processed_data/integration_report_{timestamp}.json")

# Expected columns (master schema)
EXPECTED_COLUMNS = [
    'source', 'date', 'title', 'url',
    'primary_use_case', 'primary_use_case_confidence',
    'ai_use_cases', 'sentiment',
    'ai_mention_count', 'ai_mentions',
    'title_ai_mention_count', 'title_ai_mentions',
    'word_count', 'summary'
]

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_script_dir():
    """Get the directory containing this script."""
    return Path(__file__).parent.resolve()

def resolve_path(relative_path: Path) -> Path:
    """Resolve relative path from script directory."""
    script_dir = get_script_dir()
    return (script_dir / relative_path).resolve()

def create_backup(filepath: Path, timestamp: str) -> Path:
    """
    Create a timestamped backup of a file.

    Args:
        filepath: Path to file to backup
        timestamp: Timestamp string for backup filename

    Returns:
        Path to backup file
    """
    backup_path = filepath.parent / f"{filepath.stem}_backup_{timestamp}{filepath.suffix}"

    if filepath.exists():
        df = pd.read_csv(filepath)
        df.to_csv(backup_path, index=False, encoding='utf-8')
        print(f"✓ Backup created: {backup_path.name}")
        return backup_path
    else:
        print(f"⚠ Warning: {filepath} does not exist, no backup created")
        return None

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to match expected schema.

    Some CSV files may have extra columns (like 'AI' binary flag).
    This function ensures we only keep the standard columns.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with normalized columns
    """
    # Keep only expected columns that exist in the DataFrame
    existing_cols = [col for col in EXPECTED_COLUMNS if col in df.columns]

    # Add missing columns with None values
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = None
            print(f"  ⚠ Added missing column: {col}")

    # Return DataFrame with columns in expected order
    return df[EXPECTED_COLUMNS]

def clean_url(url: str) -> str:
    """
    Clean and normalize URL for duplicate detection.

    - Remove trailing slashes
    - Strip whitespace
    - Convert to lowercase

    Args:
        url: Raw URL string

    Returns:
        Cleaned URL string
    """
    if pd.isna(url):
        return ""

    url = str(url).strip().lower()

    # Remove trailing slashes
    url = url.rstrip('/')

    return url

def detect_duplicates(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Detect duplicate articles between two DataFrames based on URL.

    Args:
        df1: First DataFrame (existing data)
        df2: Second DataFrame (new data)

    Returns:
        DataFrame containing duplicate articles
    """
    # Clean URLs in both DataFrames
    df1_urls = df1['url'].apply(clean_url)
    df2_urls = df2['url'].apply(clean_url)

    # Find URLs that exist in both
    duplicate_urls = set(df1_urls) & set(df2_urls)

    # Filter df2 to show duplicates
    duplicates_mask = df2_urls.isin(duplicate_urls)

    return df2[duplicates_mask]

# =============================================================================
# MAIN INTEGRATION LOGIC
# =============================================================================

def integrate_datasets():
    """
    Main function to integrate increased_scope.csv into unified_ai_analysis.csv.

    Steps:
    1. Load both datasets
    2. Validate schemas
    3. Detect and report duplicates
    4. Create backup of existing unified dataset
    5. Merge datasets
    6. Save merged dataset
    7. Generate integration report
    """
    print("=" * 80)
    print("INTEGRATING INCREASED SCOPE INTO UNIFIED ANALYSIS")
    print("=" * 80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Resolve paths
    increased_scope_path = resolve_path(INCREASED_SCOPE_CSV)
    unified_analysis_path = resolve_path(UNIFIED_ANALYSIS_CSV)
    output_path = resolve_path(OUTPUT_CSV)

    # =============================================================================
    # STEP 1: Load datasets
    # =============================================================================
    print("\n[1/7] Loading datasets...")

    if not increased_scope_path.exists():
        print(f"✗ Error: {increased_scope_path} not found!")
        return

    if not unified_analysis_path.exists():
        print(f"✗ Error: {unified_analysis_path} not found!")
        return

    # Load increased scope CSV
    increased_scope_df = pd.read_csv(increased_scope_path, encoding='utf-8')
    print(f"  ✓ Loaded increased_scope.csv: {len(increased_scope_df)} articles")

    # Load existing unified analysis CSV
    unified_df = pd.read_csv(unified_analysis_path, encoding='utf-8')
    print(f"  ✓ Loaded unified_ai_analysis.csv: {len(unified_df)} articles")

    # =============================================================================
    # STEP 2: Validate schemas
    # =============================================================================
    print("\n[2/7] Validating schemas...")

    # Check increased_scope.csv columns
    print(f"  Increased scope columns: {list(increased_scope_df.columns)}")
    print(f"  Unified analysis columns: {list(unified_df.columns)}")

    # Normalize both DataFrames to match expected schema
    increased_scope_df = normalize_column_names(increased_scope_df)
    unified_df = normalize_column_names(unified_df)

    print("  ✓ Schemas normalized to expected column set")

    # =============================================================================
    # STEP 3: Detect duplicates
    # =============================================================================
    print("\n[3/7] Detecting duplicates...")

    duplicates_df = detect_duplicates(unified_df, increased_scope_df)

    if len(duplicates_df) > 0:
        print(f"  ⚠ Found {len(duplicates_df)} duplicate articles (will be skipped):")
        for _, dup in duplicates_df.iterrows():
            print(f"    - {dup['title'][:60]}...")
    else:
        print("  ✓ No duplicates found")

    # Filter out duplicates from increased_scope_df
    increased_scope_urls = increased_scope_df['url'].apply(clean_url)
    unified_urls = unified_df['url'].apply(clean_url)

    new_articles_mask = ~increased_scope_urls.isin(unified_urls)
    new_articles_df = increased_scope_df[new_articles_mask].copy()

    print(f"  ✓ New articles to add: {len(new_articles_df)}")

    # =============================================================================
    # STEP 4: Create backup
    # =============================================================================
    print("\n[4/7] Creating backup of unified_ai_analysis.csv...")

    backup_path = create_backup(unified_analysis_path, timestamp)

    # =============================================================================
    # STEP 5: Merge datasets
    # =============================================================================
    print("\n[5/7] Merging datasets...")

    # Concatenate DataFrames
    merged_df = pd.concat([unified_df, new_articles_df], ignore_index=True)

    print(f"  ✓ Merged dataset size: {len(merged_df)} articles")
    print(f"    - Existing articles: {len(unified_df)}")
    print(f"    - New articles added: {len(new_articles_df)}")
    print(f"    - Duplicates skipped: {len(duplicates_df)}")

    # =============================================================================
    # STEP 6: Save merged dataset
    # =============================================================================
    print("\n[6/7] Saving merged dataset...")

    merged_df.to_csv(output_path, index=False, encoding='utf-8')

    print(f"  ✓ Saved to: {output_path}")

    # =============================================================================
    # STEP 7: Generate integration report
    # =============================================================================
    print("\n[7/7] Generating integration report...")

    # Compile statistics
    report = {
        "integration_timestamp": timestamp,
        "input_files": {
            "increased_scope": str(increased_scope_path),
            "unified_analysis": str(unified_analysis_path)
        },
        "output_file": str(output_path),
        "backup_file": str(backup_path) if backup_path else None,
        "statistics": {
            "existing_articles": len(unified_df),
            "new_articles_in_increased_scope": len(increased_scope_df),
            "duplicates_found": len(duplicates_df),
            "new_articles_added": len(new_articles_df),
            "final_total_articles": len(merged_df)
        },
        "new_articles_breakdown": {
            "by_source": new_articles_df['source'].value_counts().to_dict() if len(new_articles_df) > 0 else {},
            "by_primary_use_case": new_articles_df['primary_use_case'].value_counts().to_dict() if len(new_articles_df) > 0 else {},
            "by_sentiment": new_articles_df['sentiment'].value_counts().to_dict() if len(new_articles_df) > 0 else {},
        },
        "sample_new_articles": [
            {
                "title": row['title'],
                "source": row['source'],
                "date": row['date'],
                "primary_use_case": row['primary_use_case'],
                "url": row['url']
            }
            for _, row in new_articles_df.head(10).iterrows()
        ] if len(new_articles_df) > 0 else []
    }

    # Save report
    report_path = resolve_path(INTEGRATION_REPORT).parent / f"integration_report_{timestamp}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Integration report saved: {report_path.name}")

    # =============================================================================
    # SUMMARY
    # =============================================================================
    print("\n" + "=" * 80)
    print("INTEGRATION COMPLETE")
    print("=" * 80)
    print(f"✓ Total articles in merged dataset: {len(merged_df)}")
    print(f"✓ New articles added: {len(new_articles_df)}")
    print(f"✓ Duplicates skipped: {len(duplicates_df)}")
    print(f"✓ Backup created: {backup_path.name if backup_path else 'N/A'}")
    print(f"✓ Output saved: {output_path}")

    if len(new_articles_df) > 0:
        print("\n📊 New Articles Breakdown:")
        print(f"  Sources: {dict(new_articles_df['source'].value_counts())}")
        print(f"  Use Cases: {dict(new_articles_df['primary_use_case'].value_counts())}")
        print(f"  Sentiment: {dict(new_articles_df['sentiment'].value_counts())}")

    print("\n🎯 Next Steps:")
    print("  1. Review integration report: " + report_path.name)
    print("  2. Update dashboard with new data: streamlit run 05_visualizations/dashboard.py")
    print("  3. Run validation suite: python 07_validation/validation_scripts/consistency_checker.py")
    print("=" * 80)

    return report

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        report = integrate_datasets()

        if report:
            print("\n✅ Integration successful!")
        else:
            print("\n❌ Integration failed!")
            exit(1)

    except Exception as e:
        print(f"\n❌ Error during integration: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
