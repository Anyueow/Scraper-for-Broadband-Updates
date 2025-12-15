#!/usr/bin/env python3
"""
Company Name Normalizer
=======================

Normalizes company names across the dataset using taxonomy and pairing rules.

Purpose:
- Standardize company name variations (e.g., "BT plc" → "BT")
- Apply company pairing rules (e.g., merge BT + Openreach when appropriate)
- Support both paired and unpaired analysis modes

Usage:
    from company_normalizer import CompanyNormalizer

    normalizer = CompanyNormalizer()

    # Normalize a single company name
    canonical = normalizer.normalize("BT plc")  # Returns: "BT"

    # Normalize with pairing
    paired = normalizer.normalize("Openreach", apply_pairing=True)  # Returns: "BT / Openreach"

    # Normalize a list of companies
    companies = normalizer.normalize_list(["bt.com", "Openreach", "Sky UK"])

Author: Telco AI Analysis Project
Date: December 2025
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd

class CompanyNormalizer:
    """
    Normalizes company names using taxonomy and pairing rules.
    """

    def __init__(self,
                 taxonomy_path: Optional[Path] = None,
                 pairs_path: Optional[Path] = None):
        """
        Initialize the normalizer.

        Args:
            taxonomy_path: Path to company_taxonomy.json
            pairs_path: Path to company_pairs.json
        """
        # Default paths (relative to this file)
        if taxonomy_path is None:
            taxonomy_path = Path(__file__).parent.parent / "configs" / "company_taxonomy.json"
        if pairs_path is None:
            pairs_path = Path(__file__).parent.parent / "configs" / "company_pairs.json"

        # Load configurations
        self.taxonomy = self._load_json(taxonomy_path)
        self.pairs_config = self._load_json(pairs_path)

        # Build normalization lookup table
        self.normalization_map = self._build_normalization_map()

        # Build pairing lookup table
        self.pairing_map = self._build_pairing_map()

    def _load_json(self, path: Path) -> Dict:
        """Load JSON configuration file."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _build_normalization_map(self) -> Dict[str, str]:
        """
        Build a lookup table mapping all aliases to canonical company names.

        Returns:
            Dict mapping lowercase alias → canonical name
        """
        norm_map = {}

        # From company_pairs.json normalization_rules
        if 'normalization_rules' in self.pairs_config:
            for canonical, aliases in self.pairs_config['normalization_rules'].items():
                # Map canonical name to itself (case-insensitive)
                norm_map[canonical.lower()] = canonical

                # Map all aliases to canonical
                for alias in aliases:
                    norm_map[alias.lower()] = canonical

        # From company_taxonomy.json (fallback/additional coverage)
        for category_name, companies in self.taxonomy.items():
            if category_name.startswith('_') or category_name in ['company_pairing_rules', 'extraction_hints']:
                continue

            for canonical, details in companies.items():
                # Map canonical name to itself
                norm_map[canonical.lower()] = canonical

                # Map aliases if present
                if 'aliases' in details:
                    for alias in details['aliases']:
                        norm_map[alias.lower()] = canonical

        return norm_map

    def _build_pairing_map(self) -> Dict[str, Tuple[str, str]]:
        """
        Build a lookup table for company pairing.

        Returns:
            Dict mapping canonical name → (primary_name, combined_name)
        """
        pair_map = {}

        if 'pairing_rules' in self.pairs_config:
            for rule in self.pairs_config['pairing_rules']:
                # Only apply active pairing rules
                if not rule.get('active', False):
                    continue

                primary = rule['primary_name']
                combined = rule['combined_name']
                merge_with = rule.get('merge_with', [])

                # Map primary to itself (for consistency)
                pair_map[primary] = (primary, combined)

                # Map all companies to be merged to the combined name
                for company in merge_with:
                    pair_map[company] = (primary, combined)

        return pair_map

    def normalize(self, company_name: str, apply_pairing: bool = False) -> str:
        """
        Normalize a single company name.

        Args:
            company_name: Raw company name (may be alias or variation)
            apply_pairing: If True, apply company pairing rules

        Returns:
            Canonical company name (paired or unpaired)
        """
        if not company_name or pd.isna(company_name):
            return ""

        # Clean input
        company_clean = str(company_name).strip()

        # Step 1: Normalize to canonical name
        canonical = self.normalization_map.get(company_clean.lower(), company_clean)

        # Step 2: Apply pairing if requested
        if apply_pairing and canonical in self.pairing_map:
            _, combined = self.pairing_map[canonical]
            return combined

        return canonical

    def normalize_list(self,
                      company_names: List[str],
                      apply_pairing: bool = False,
                      deduplicate: bool = True) -> List[str]:
        """
        Normalize a list of company names.

        Args:
            company_names: List of raw company names
            apply_pairing: If True, apply company pairing rules
            deduplicate: If True, remove duplicates after normalization

        Returns:
            List of normalized company names
        """
        normalized = [self.normalize(name, apply_pairing) for name in company_names]

        # Remove empty strings
        normalized = [n for n in normalized if n]

        # Deduplicate if requested
        if deduplicate:
            # Preserve order while deduplicating
            seen = set()
            unique = []
            for name in normalized:
                if name not in seen:
                    seen.add(name)
                    unique.append(name)
            return unique

        return normalized

    def get_company_metadata(self, company_name: str) -> Optional[Dict]:
        """
        Get metadata for a company from the taxonomy.

        Args:
            company_name: Canonical company name

        Returns:
            Dictionary with company metadata (category, business_model, etc.) or None
        """
        # Search all categories in taxonomy
        for category_name, companies in self.taxonomy.items():
            if category_name.startswith('_') or category_name in ['company_pairing_rules', 'extraction_hints']:
                continue

            if company_name in companies:
                metadata = companies[company_name].copy()
                metadata['taxonomy_category'] = category_name
                return metadata

        return None

    def is_paired_company(self, company_name: str) -> bool:
        """
        Check if a company is part of an active pairing rule.

        Args:
            company_name: Canonical company name

        Returns:
            True if company is part of a pairing rule
        """
        canonical = self.normalize(company_name)
        return canonical in self.pairing_map

    def get_pairing_info(self, company_name: str) -> Optional[Dict]:
        """
        Get pairing information for a company.

        Args:
            company_name: Canonical company name

        Returns:
            Dictionary with pairing details or None
        """
        canonical = self.normalize(company_name)

        if canonical not in self.pairing_map:
            return None

        primary, combined = self.pairing_map[canonical]

        # Find the full pairing rule
        for rule in self.pairs_config.get('pairing_rules', []):
            if rule['primary_name'] == primary:
                return {
                    'primary_name': primary,
                    'combined_name': combined,
                    'is_primary': (canonical == primary),
                    'reason': rule.get('reason', ''),
                    'pair_id': rule.get('pair_id', '')
                }

        return None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def normalize_companies_in_dataframe(df: pd.DataFrame,
                                    column: str = 'companies_mentioned',
                                    apply_pairing: bool = False,
                                    output_column: Optional[str] = None) -> pd.DataFrame:
    """
    Normalize company names in a DataFrame column.

    Args:
        df: Input DataFrame
        column: Column containing company names (can be comma-separated string or list)
        apply_pairing: If True, apply company pairing rules
        output_column: Name of output column (default: overwrite input column)

    Returns:
        DataFrame with normalized company names
    """
    normalizer = CompanyNormalizer()

    if output_column is None:
        output_column = column

    def normalize_row(value):
        """Normalize company names in a single row."""
        if pd.isna(value) or not value:
            return []

        # Handle both string and list inputs
        if isinstance(value, str):
            # Split comma-separated string
            companies = [c.strip() for c in value.split(',')]
        elif isinstance(value, list):
            companies = value
        else:
            return []

        # Normalize
        normalized = normalizer.normalize_list(companies, apply_pairing=apply_pairing)

        return normalized

    # Apply normalization
    df[output_column] = df[column].apply(normalize_row)

    return df


def generate_company_pairing_report(df: pd.DataFrame,
                                    company_column: str = 'companies_mentioned') -> pd.DataFrame:
    """
    Generate a report showing how company pairing affects counts.

    Args:
        df: Input DataFrame with company mentions
        company_column: Column containing company names

    Returns:
        DataFrame with pairing impact analysis
    """
    normalizer = CompanyNormalizer()

    # Collect all company mentions (unpaired)
    unpaired_counts = {}
    paired_counts = {}

    for _, row in df.iterrows():
        companies = row[company_column]

        if pd.isna(companies) or not companies:
            continue

        # Handle string or list
        if isinstance(companies, str):
            companies = [c.strip() for c in companies.split(',')]

        # Count unpaired
        for company in companies:
            canonical = normalizer.normalize(company, apply_pairing=False)
            unpaired_counts[canonical] = unpaired_counts.get(canonical, 0) + 1

            # Count paired
            paired = normalizer.normalize(company, apply_pairing=True)
            paired_counts[paired] = paired_counts.get(paired, 0) + 1

    # Build comparison DataFrame
    all_companies = set(unpaired_counts.keys()) | set(paired_counts.keys())

    report_data = []
    for company in sorted(all_companies):
        unpaired_count = unpaired_counts.get(company, 0)
        paired_count = paired_counts.get(company, 0)

        # Check if this company is part of a pairing
        pairing_info = normalizer.get_pairing_info(company)

        report_data.append({
            'company': company,
            'unpaired_mentions': unpaired_count,
            'paired_mentions': paired_count,
            'is_paired': pairing_info is not None,
            'paired_as': pairing_info['combined_name'] if pairing_info else company,
            'pairing_reason': pairing_info['reason'] if pairing_info else ''
        })

    return pd.DataFrame(report_data)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI tool for testing company normalization."""
    import sys

    normalizer = CompanyNormalizer()

    if len(sys.argv) < 2:
        print("Usage: python company_normalizer.py <company_name> [--paired]")
        print("\nExamples:")
        print("  python company_normalizer.py 'BT plc'")
        print("  python company_normalizer.py 'Openreach' --paired")
        return

    company_name = sys.argv[1]
    apply_pairing = '--paired' in sys.argv

    # Normalize
    normalized = normalizer.normalize(company_name, apply_pairing=apply_pairing)

    print(f"Input: {company_name}")
    print(f"Normalized: {normalized}")
    print(f"Pairing applied: {apply_pairing}")

    # Show metadata
    metadata = normalizer.get_company_metadata(normalized)
    if metadata:
        print(f"\nMetadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

    # Show pairing info
    pairing_info = normalizer.get_pairing_info(company_name)
    if pairing_info:
        print(f"\nPairing Info:")
        for key, value in pairing_info.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
