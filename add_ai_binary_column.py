"""
Quick script to add binary AI column to both unified CSV files.
"""

import pandas as pd

# Process unified_ai_analysis.csv
print("Processing output/unified_ai_analysis.csv...")
df1 = pd.read_csv('output/unified_ai_analysis.csv')

# Add AI column: 0 if ai_mention_count is 0 or sentiment is not_applicable, otherwise 1
df1['AI'] = ((df1['ai_mention_count'] > 0) & (df1['sentiment'] != 'not_applicable')).astype(int)

# Save back
df1.to_csv('output/unified_ai_analysis.csv', index=False)
print(f"✓ Added AI column to unified_ai_analysis.csv")
print(f"  - AI=1: {df1['AI'].sum()} articles")
print(f"  - AI=0: {(df1['AI'] == 0).sum()} articles")

# Process big_firm_unified_analysis.csv
print("\nProcessing big firm analysis/big_firm_unified_analysis.csv...")
df2 = pd.read_csv('big firm analysis/big_firm_unified_analysis.csv')

# Add AI column: 0 if title is "No Mentions Identified", otherwise 1
df2['AI'] = (df2['title'] != 'No Mentions Identified').astype(int)

# Save back
df2.to_csv('big firm analysis/big_firm_unified_analysis.csv', index=False)
print(f"✓ Added AI column to big_firm_unified_analysis.csv")
print(f"  - AI=1: {df2['AI'].sum()} articles")
print(f"  - AI=0: {(df2['AI'] == 0).sum()} articles")

print("\n✓ Done!")
