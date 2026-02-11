"""
Analyze the actual uploaded RIS files to find the "Using AI..." paper.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import parse_ris_file, entries_to_df
from src.comparator import compare_datasets, normalize_title_for_key

# Parse both files
with open('uploads/My Best Screening.ris', 'r', encoding='utf-8') as f:
    entries_a = parse_ris_file(f.read())

with open('uploads/Google Scholar - automated.ris', 'r', encoding='utf-8') as f:
    entries_b = parse_ris_file(f.read())

df_a = entries_to_df(entries_a)
df_b = entries_to_df(entries_b)

print("="*80)
print("ANALYZING ACTUAL UPLOADED FILES")
print("="*80)
print(f"\nFile A (My Best Screening.ris): {len(df_a)} entries")
print(f"File B (Google Scholar - automated.ris): {len(df_b)} entries")

# Search for papers with "artificial" in the title
ai_papers_a = [r for r in df_a.to_dict('records') if 'artificial' in str(r.get('title', '')).lower()]
ai_papers_b = [r for r in df_b.to_dict('records') if 'artificial' in str(r.get('title', '')).lower()]

print(f"\nPapers with 'artificial' in File A: {len(ai_papers_a)}")
for p in ai_papers_a[:3]:
    title = p.get('title', 'N/A')
    year = p.get('year', 'N/A')
    print(f"  - {title[:70]}... (Year: {year})")

print(f"\nPapers with 'artificial' in File B: {len(ai_papers_b)}")
for p in ai_papers_b[:3]:
    title = p.get('title', 'N/A')
    year = p.get('year', 'N/A')
    print(f"  - {title[:70]}... (Year: {year})")

# Look specifically for the "Using Artificial Intelligence..." paper
target_keywords = ["using", "artificial", "intelligence", "automated", "risk", "bias"]

print(f"\n" + "="*80)
print("SEARCHING FOR TARGET PAPER")
print("="*80)

for idx, row in df_a.iterrows():
    title = str(row.get('title', '')).lower()
    if all(kw in title for kw in target_keywords):
        print(f"\nFOUND IN FILE A:")
        print(f"  Title: {row.get('title', 'N/A')}")
        print(f"  Year: {row.get('year', 'N/A')}")
        print(f"  Normalized: {normalize_title_for_key(row.get('title', ''))[:70]}...")
        break
else:
    print("\nNOT FOUND IN FILE A")

for idx, row in df_b.iterrows():
    title = str(row.get('title', '')).lower()
    if all(kw in title for kw in target_keywords):
        print(f"\nFOUND IN FILE B:")
        print(f"  Title: {row.get('title', 'N/A')}")
        print(f"  Year: {row.get('year', 'N/A')}")
        print(f"  Normalized: {normalize_title_for_key(row.get('title', ''))[:70]}...")
        break
else:
    print("\nNOT FOUND IN FILE B")

# Run full comparison
print(f"\n" + "="*80)
print("RUNNING COMPARISON")
print("="*80)

overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)

print(f"\nResults:")
print(f"  Overlap: {len(overlap)}")
print(f"  Unique to A: {len(unique_a)}")
print(f"  Unique to B: {len(unique_b)}")

# Check if target paper is in overlap
for item in overlap:
    title = str(item.get('title', '')).lower()
    if all(kw in title for kw in target_keywords):
        print(f"\n✅ TARGET PAPER IS IN OVERLAP!")
        break
else:
    # Check if it's in unique sets
    for item in unique_a:
        title = str(item.get('title', '')).lower()
        if all(kw in title for kw in target_keywords):
            print(f"\n❌ TARGET PAPER IS IN UNIQUE_A (should be in overlap!)")
            break
    
    for item in unique_b:
        title = str(item.get('title', '')).lower()
        if all(kw in title for kw in target_keywords):
            print(f"\n❌ TARGET PAPER IS IN UNIQUE_B (should be in overlap!)")
            break
