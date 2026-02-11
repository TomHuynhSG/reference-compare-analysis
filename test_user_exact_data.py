"""
Test with the EXACT entries from user's actual compare page.
File A = no PY field
File B = has PY field with 2025///
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import parse_ris_file, entries_to_df
from src.comparator import compare_datasets, normalize_title_for_key
import pandas as pd

# EXACT entries from user's compare page
# File A - NO year field
ris_a = """TY  - JOUR
AB  - Abstract Background Risk-of-bias (ROB) assessment is crucial...
AU  - van Blommestein, Chesron Willem John
AU  - Schellekensᵃ, Floris-Jan Peter Antoine Guil
AU  - van Dijk, Bram
AU  - Ciere, Michael
AU  - Forouzanfar, Tymour
L1  - internal-pdf://3045533371/ssrn-5191121.pdf
ST  - Using Artificial Intelligence for Automated Risk of Bias Assessment of Randomized Controlled Trials
T2  - Available at SSRN 5191121
TI  - Using Artificial Intelligence for Automated Risk of Bias Assessment of Randomized Controlled Trials
ID  - 407
ER  - 
"""

# File B - HAS year field
ris_b = """TY  - JOUR
AU  - Blommestein, CWJ van
TI  - Using Artificial Intelligence for Automated Risk of Bias Assessment of Randomized Controlled Trials
JF  - Available at SSRN …
PB  - papers.ssrn.com
UR  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5191121
PY  - 2025///
AB  - … by LLMs could help automate the ROB assessment process.
M1  - Query date: 2026-02-08 14:55:16
ER  - 
"""

print("="*80)
print("TESTING USER'S EXACT COMPARE PAGE DATA")
print("="*80)

entries_a = parse_ris_file(ris_a)
entries_b = parse_ris_file(ris_b)

df_a = entries_to_df(entries_a)
df_b = entries_to_df(entries_b)

print(f"\nFile A (uploaded first):")
if not df_a.empty:
    print(f"  Title: {df_a.iloc[0].get('title', 'N/A')}")
    print(f"  Year: '{df_a.iloc[0].get('year', 'MISSING')}'")
    print(f"  Title normalized: {normalize_title_for_key(df_a.iloc[0].get('title', ''))[:60]}...")

print(f"\nFile B (uploaded second):")
if not df_b.empty:
    print(f"  Title: {df_b.iloc[0].get('title', 'N/A')}")
    print(f"  Year: '{df_b.iloc[0].get('year', 'MISSING')}'")
    print(f"  Title normalized: {normalize_title_for_key(df_b.iloc[0].get('title', ''))[:60]}...")

# Check if titles match after normalization
if not df_a.empty and not df_b.empty:
    title_a_norm = normalize_title_for_key(df_a.iloc[0].get('title', ''))
    title_b_norm = normalize_title_for_key(df_b.iloc[0].get('title', ''))
    print(f"\nTitles identical: {title_a_norm == title_b_norm}")

# Run comparison
overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)

print(f"\nCOMPARISON RESULTS:")
print(f"  Overlap: {len(overlap)}")
print(f"  Unique to A: {len(unique_a)}")
print(f"  Unique to B: {len(unique_b)}")

if len(overlap) == 1:
    print("\n✅ SUCCESS: Papers matched!")
    if overlap[0].get('fuzzy_match'):
        print("   Match type: FUZZY")
else:
    print("\n❌ FAILED: Papers should match but didn't")
    print("\nDEBUGGING:")
    print(f"  Year A type: {type(df_a.iloc[0].get('year'))}")
    print(f"  Year B type: {type(df_b.iloc[0].get('year'))}")
    print(f"  Year A value: {repr(df_a.iloc[0].get('year'))}")
    print(f"  Year B value: {repr(df_b.iloc[0].get('year'))}")
