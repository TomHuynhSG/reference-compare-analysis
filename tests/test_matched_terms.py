"""
Test that matched_terms list is correctly populated with actual terms
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.search_engine import search_references
from src.query_parser import parse_query
import pandas as pd

# Create test data matching user's scenario
test_df = pd.DataFrame([
    {
        'title': 'Automated Risk-of-Bias Assessment of Randomized Controlled Trials',
        'abstract': 'We present a GEPA-trained programmatic prompting framework for automated risk assessment.',
        'year': 2024,
        'authors': ['Smith, J.']
    },
    {
        'title': 'ChatGPT-4o in Risk-of-Bias Assessments in Neonatology',
        'abstract': 'A validity analysis of ChatGPT for assessing bias in clinical trials.',
        'year': 2024,
        'authors': ['Doe, A.']
    }
])

# User's actual query (simplified)
query = '("Risk of bias" OR "Risk-of-bias" OR "bias assessment*" OR "assess*") AND ("automat*" OR "ChatGPT*")'
fields = ['title', 'abstract']

print("=" * 70)
print("TEST: Matched Terms Accuracy")
print("=" * 70)
print(f"Query: {query}")
print(f"Fields: {fields}\n")

matched, unmatched, stats = search_references(test_df, query, fields)

print(f"Total matched: {stats['matched_count']}")
print("=" * 70)

for i, ref in enumerate(matched, 1):
    print(f"\n{i}. {ref['title']}")
    print(f"   Match count: {ref.get('match_count', 0)}")
    print(f"   Matched terms:")
    for term in ref.get('matched_terms', []):
        print(f"     - '{term}'")
    
    # Check which terms are highlighted in title
    if ref.get('title_highlighted'):
        print(f"   Title highlights present: Yes")
    
    # Check which terms are highlighted in abstract
    if ref.get('abstract_highlighted'):
        print(f"   Abstract highlights present: Yes")

print("\n" + "=" * 70)
print("VERIFICATION:")
print("- matched_terms should list all unique terms that matched")
print("- match_count should equal length of matched_terms")
print("- Each reference should track its own specific matches")
print("=" * 70)
