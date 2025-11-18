#!/usr/bin/env python3
"""
Title Analysis Script

Parses through all CSV files in the output directory and analyzes article titles
for mentions of AI-related keywords including specific companies and technologies.

Usage:
    python title_analysis.py [--directory PATH] [--export]
"""
import argparse
import csv
import re
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict, Counter
import sys

# AI-related keywords to search for in titles
AI_KEYWORDS = [
    "AI",
    "artificial intelligence",
    "machine learning",
    "LLMs",
    "LLM",
    "large language models",
    "large language model",
    "openAI",
    "anthropic",
    "claude",
    "chatGPT",
    "GPT",
    "neural network",
    "deep learning",
    "automation"
]


class TitleAnalyzer:
    """Analyzes article titles for AI-related keyword mentions"""

    def __init__(self, keywords: List[str] = None):
        """
        Initialize the analyzer

        Args:
            keywords: List of keywords to search for (case-insensitive)
        """
        self.keywords = keywords or AI_KEYWORDS
        # Compile regex patterns for efficient matching (case-insensitive)
        self.patterns = [
            re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            for keyword in self.keywords
        ]

    def find_keywords_in_title(self, title: str) -> List[str]:
        """
        Find all keywords present in a title

        Args:
            title: Article title to analyze

        Returns:
            List of keywords found (maintaining original case from keyword list)
        """
        found_keywords = []
        for keyword, pattern in zip(self.keywords, self.patterns):
            if pattern.search(title):
                found_keywords.append(keyword)
        return found_keywords

    def analyze_csv_file(self, csv_path: Path) -> Dict:
        """
        Analyze a single CSV file

        Args:
            csv_path: Path to CSV file

        Returns:
            Dictionary with analysis results
        """
        results = {
            'file': csv_path.name,
            'total_articles': 0,
            'articles_with_ai_keywords': 0,
            'keyword_counts': Counter(),
            'articles': []  # List of articles with AI mentions
        }

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Verify 'title' column exists
                if 'title' not in reader.fieldnames:
                    print(f"Warning: 'title' column not found in {csv_path.name}")
                    print(f"Available columns: {', '.join(reader.fieldnames)}")
                    return results

                for row in reader:
                    results['total_articles'] += 1
                    title = row.get('title', '')

                    # Find keywords in title
                    found_keywords = self.find_keywords_in_title(title)

                    if found_keywords:
                        results['articles_with_ai_keywords'] += 1
                        results['keyword_counts'].update(found_keywords)
                        results['articles'].append({
                            'title': title,
                            'source': row.get('source', 'Unknown'),
                            'date': row.get('date', 'Unknown'),
                            'url': row.get('url', ''),
                            'keywords_found': found_keywords
                        })

        except FileNotFoundError:
            print(f"Error: File not found: {csv_path}")
        except Exception as e:
            print(f"Error processing {csv_path}: {e}")

        return results

    def analyze_directory(self, directory: Path) -> Dict:
        """
        Analyze all CSV files in a directory

        Args:
            directory: Path to directory containing CSV files

        Returns:
            Dictionary with aggregated results
        """
        if not directory.exists():
            print(f"Error: Directory not found: {directory}")
            return None

        # Find all CSV files
        csv_files = list(directory.glob('*.csv'))

        if not csv_files:
            print(f"Warning: No CSV files found in {directory}")
            return None

        print(f"Found {len(csv_files)} CSV file(s) to analyze\n")

        # Aggregate results
        aggregated = {
            'files_analyzed': len(csv_files),
            'total_articles': 0,
            'total_with_ai_keywords': 0,
            'keyword_counts': Counter(),
            'file_results': [],
            'all_articles': []  # All articles with AI mentions across files
        }

        for csv_file in csv_files:
            print(f"Analyzing: {csv_file.name}")
            file_result = self.analyze_csv_file(csv_file)
            aggregated['file_results'].append(file_result)
            aggregated['total_articles'] += file_result['total_articles']
            aggregated['total_with_ai_keywords'] += file_result['articles_with_ai_keywords']
            aggregated['keyword_counts'].update(file_result['keyword_counts'])
            aggregated['all_articles'].extend(file_result['articles'])

        return aggregated

    def print_summary(self, results: Dict):
        """
        Print a summary of analysis results

        Args:
            results: Results dictionary from analyze_directory
        """
        if not results:
            return

        print("\n" + "=" * 80)
        print("TITLE ANALYSIS SUMMARY")
        print("=" * 80)

        print(f"\nFiles Analyzed: {results['files_analyzed']}")
        print(f"Total Articles: {results['total_articles']}")
        print(f"Articles with AI Keywords in Title: {results['total_with_ai_keywords']}")

        if results['total_articles'] > 0:
            percentage = (results['total_with_ai_keywords'] / results['total_articles']) * 100
            print(f"Percentage: {percentage:.1f}%")

        print("\n" + "-" * 80)
        print("KEYWORD FREQUENCY (in titles)")
        print("-" * 80)

        if results['keyword_counts']:
            # Sort by frequency (descending)
            for keyword, count in results['keyword_counts'].most_common():
                print(f"  {keyword:30s} : {count:4d} mentions")
        else:
            print("  No AI keywords found in titles")

        print("\n" + "-" * 80)
        print("ARTICLES WITH AI KEYWORDS IN TITLE")
        print("-" * 80)

        if results['all_articles']:
            for i, article in enumerate(results['all_articles'], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article['source']}")
                print(f"   Date: {article['date']}")
                print(f"   Keywords: {', '.join(article['keywords_found'])}")
                if article['url']:
                    print(f"   URL: {article['url']}")
        else:
            print("\n  No articles found with AI keywords in titles")

        print("\n" + "=" * 80)

    def export_results(self, results: Dict, output_path: Path):
        """
        Export detailed results to CSV

        Args:
            results: Results dictionary from analyze_directory
            output_path: Path for output CSV file
        """
        if not results or not results['all_articles']:
            print("No results to export")
            return

        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['source', 'date', 'title', 'keywords_found', 'keyword_count', 'url']
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                writer.writeheader()
                for article in results['all_articles']:
                    writer.writerow({
                        'source': article['source'],
                        'date': article['date'],
                        'title': article['title'],
                        'keywords_found': ', '.join(article['keywords_found']),
                        'keyword_count': len(article['keywords_found']),
                        'url': article['url']
                    })

            print(f"\nResults exported to: {output_path}")

        except Exception as e:
            print(f"Error exporting results: {e}")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Analyze article titles in CSV files for AI-related keywords'
    )

    parser.add_argument(
        '--directory',
        type=Path,
        default=Path('output'),
        help='Directory containing CSV files (default: output/)'
    )

    parser.add_argument(
        '--export',
        action='store_true',
        help='Export results to CSV file'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('title_analysis_results.csv'),
        help='Output file for exported results (default: title_analysis_results.csv)'
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    print("=" * 80)
    print("ARTICLE TITLE ANALYSIS - AI KEYWORD DETECTOR")
    print("=" * 80)
    print(f"\nSearching directory: {args.directory}")
    print(f"Keywords: {', '.join(AI_KEYWORDS[:5])}... (and {len(AI_KEYWORDS)-5} more)")
    print()

    # Create analyzer
    analyzer = TitleAnalyzer()

    # Analyze directory
    results = analyzer.analyze_directory(args.directory)

    if results:
        # Print summary
        analyzer.print_summary(results)

        # Export if requested
        if args.export:
            analyzer.export_results(results, args.output)
    else:
        print("\nNo analysis performed. Please check the directory path and try again.")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
