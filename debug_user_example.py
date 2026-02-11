"""
Test the specific mismatched pair the user reported.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import parse_ris_file, entries_to_df
from src.comparator import compare_datasets, generate_key, normalize_title_for_key
import pandas as pd

# Exact RIS from user
ris_a = """TY  - JOUR
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

ris_b = """TY  - JOUR
AB  - Abstract Background Risk-of-bias (ROB) assessment is crucial...
AU  - van Blommestein, Chesron Willem John
AU  - Schellekensᵃ, Floris-Jan Peter Antoine Guil
L1  - internal-pdf://3045533371/ssrn-5191121.pdf
ST  - Using Artificial Intelligence for Automated Risk of Bias Assessment of Randomized Controlled Trials
T2  - Available at SSRN 5191121
TI  - Using Artificial Intelligence for Automated Risk of Bias Assessment of Randomized Controlled Trials
ID  - 407
ER  - 
"""

print("="*80)
print("INVESTIGATING USER'S MISMATCHED PAIR")
print("="*80)

# Parse both entries
entries_a = parse_ris_file(ris_a)
entries_b = parse_ris_file(ris_b)

print(f"\nParsed File A: {len(entries_a)} entries")
if entries_a:
    print(f"  Title: {entries_a[0].get('title', 'N/A')}")
    print(f"  Year: {entries_a[0].get('year', 'N/A')}")
    print(f"  PY field: {entries_a[0].get('py', 'N/A')}")
    print(f"  DOI: {entries_a[0].get('doi', 'None')}")

print(f"\nParsed File B: {len(entries_b)} entries")
if entries_b:
    print(f"  Title: {entries_b[0].get('title', 'N/A')}")
    print(f"  Year: {entries_b[0].get('year', 'N/A')}")
    print(f"  PY field: {entries_b[0].get('py', 'N/A')}")
    print(f"  DOI: {entries_b[0].get('doi', 'None')}")

# Check title normalization
if entries_a and entries_b:
    title_a = entries_a[0].get('title', '')
    title_b = entries_b[0].get('title', '')
    
    norm_a = normalize_title_for_key(title_a)
    norm_b = normalize_title_for_key(title_b)
    
    print(f"\nTitle normalization:")
    print(f"  A normalized: {norm_a[:80]}...")
    print(f"  B normalized: {norm_b[:80]}...")
    print(f"  Titles match: {norm_a == norm_b}")
    
    # Check key generation
    df_a = entries_to_df(entries_a)
    df_b = entries_to_df(entries_b)
    
    keys_a = generate_key(df_a.iloc[0])
    keys_b = generate_key(df_b.iloc[0])
    
    print(f"\nGenerated keys:")
    print(f"  A: {keys_a}")
    print(f"  B: {keys_b}")
    print(f"  Keys match: {keys_a == keys_b}")
    
    # Test full comparison
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)
    
    print(f"\nComparison results:")
    print(f"  Overlap: {len(overlap)}")
    print(f"  Unique to A: {len(unique_a)}")
    print(f"  Unique to B: {len(unique_b)}")
    
    if len(overlap) == 0:
        print(f"\n❌ BUG CONFIRMED: These papers should match!")
        print(f"\nDEBUG INFO:")
        print(f"  Year A: '{df_a.iloc[0].get('year', 'MISSING')}' (type: {type(df_a.iloc[0].get('year', ''))})")
        print(f"  Year B: '{df_b.iloc[0].get('year', 'MISSING')}' (type: {type(df_b.iloc[0].get('year', ''))})")
    else:
        print(f"\n✅ Papers matched correctly!")
