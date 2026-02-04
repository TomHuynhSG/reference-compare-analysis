"""
Test highlighting prioritization with overlapping matches
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.search_engine import highlight_text

# Test case: your example
title = "ChatGPT-4o in Risk-of-Bias Assessments in Neonatology: A Validity Analysis"

# These are the matched terms that might be found
matched_terms = {
    "ChatGPT",           # from "ChatGPT*"
    "Risk-of-Bias",      # from "Risk-of-bias" (exact phrase)
    "Bias Assessments",  # from "bias assessment*" (phrase with wildcard)
    "Assessments",       # from "assess*" (wildcard)
}

print("=" * 70)
print("HIGHLIGHTING PRIORITIZATION TEST")
print("=" * 70)
print(f"\nOriginal title:")
print(f"  {title}")
print(f"\nMatched terms:")
for term in sorted(matched_terms, key=len, reverse=True):
    print(f"  - '{term}' (length: {len(term)})")

print(f"\nHighlighted result:")
result = highlight_text(title, matched_terms)
print(f"  {result}")

# Count mark tags
mark_count = result.count('<mark>')
print(f"\nNumber of highlights: {mark_count}")

# Extract what was highlighted
import re
highlighted_words = re.findall(r'<mark>(.*?)</mark>', result)
print(f"Highlighted terms:")
for hw in highlighted_words:
    print(f"  - '{hw}'")

print("\n" + "=" * 70)
print("EXPECTED BEHAVIOR:")
print("=" * 70)
print("Should prioritize longer matches and avoid overlaps:")
print("  ✓ 'ChatGPT' should be highlighted (longest match at that position)")
print("  ✓ 'Risk-of-Bias' should be highlighted (longer than 'Bias Assessments')")
print("  ✓ Should NOT highlight 'Bias Assessments' if 'Risk-of-Bias' is already highlighted")
print("  ? May or may not highlight 'Assessments' depending on overlap")
print("=" * 70)
