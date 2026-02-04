"""
Test highlighting with maximized match count strategy
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.search_engine import highlight_text

# Test case 1: User's example - should maximize count
title1 = "Automated Risk-of-Bias Assessment of Randomized Controlled Trials"
matched_terms1 = {
    "Automated",         # from "automat*"
    "Risk-of-Bias",      # from "Risk-of-bias"
    "Bias Assessment",   # from "bias assessment*" - OVERLAPS with Risk-of-Bias + Assessment
    "Assessment",        # from "assess*"
}

print("=" * 70)
print("TEST 1: Maximize match count")
print("=" * 70)
print(f"Title: {title1}")
print(f"\nMatched terms:")
for term in sorted(matched_terms1, key=len, reverse=True):
    print(f"  - '{term}' (len: {len(term)})")

result1 = highlight_text(title1, matched_terms1)
print(f"\nResult: {result1}")

import re
highlights1 = re.findall(r'<mark>(.*?)</mark>', result1)
print(f"\nHighlights ({len(highlights1)}):")
for h in highlights1:
    print(f"  - '{h}'")

print(f"\nExpected: 'Automated', 'Risk-of-Bias', 'Assessment' (3 highlights)")
print(f"Got: {len(highlights1)} highlights")
if len(highlights1) == 3:
    print("✓ PASS: Maximized match count!")
else:
    print("✗ FAIL: Did not maximize match count")

# Test case 2: Another example
title2 = "ChatGPT-4o in Risk-of-Bias Assessments in Neonatology"
matched_terms2 = {
    "ChatGPT",
    "Risk-of-Bias",
    "Bias Assessments",  # overlaps with both
    "Assessments",
}

print("\n" + "=" * 70)
print("TEST 2: Multiple overlapping options")
print("=" * 70)
print(f"Title: {title2}")

result2 = highlight_text(title2, matched_terms2)
highlights2 = re.findall(r'<mark>(.*?)</mark>', result2)
print(f"\nHighlights ({len(highlights2)}):")
for h in highlights2:
    print(f"  - '{h}'")

print(f"\nExpected: Should prioritize more matches over longer ones")
print("=" * 70)
