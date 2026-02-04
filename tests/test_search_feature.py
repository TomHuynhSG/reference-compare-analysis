"""
Test search functionality with sample data
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.query_parser import parse_query, QuerySyntaxError
from src.search_engine import search_references
from src.parser import entries_to_df
import pandas as pd

# Test 1: Query Parser
print("=" * 60)
print("TEST 1: Query Parser")
print("=" * 60)

test_queries = [
    'LLM',
    '"Large Language Model"',
    'LLM OR GPT',
    'LLM AND Risk',
    '("Large Language Model*" OR "LLM") AND "Risk of bias"',
    '(A OR B) AND (C OR D)',
]

for query in test_queries:
    print(f"\nQuery: {query}")
    try:
        ast = parse_query(query)
        print(f"✓ Parsed successfully: {ast}")
    except QuerySyntaxError as e:
        print(f"✗ Error: {e}")

# Test 2: Search Engine
print("\n" + "=" * 60)
print("TEST 2: Search Engine with Sample Data")
print("=" * 60)

# Create test data
test_data = pd.DataFrame([
    {
        'title': 'Large Language Models for Medical Risk Assessment',
        'abstract': 'We present a comprehensive study on GPT-4 and Claude for automated risk of bias assessment in clinical trials.',
        'year': 2024,
        'authors': ['Smith, J.', 'Doe, A.']
    },
    {
        'title': 'Transformer Architecture for NLP',
        'abstract': 'A review of transformer models including BERT and GPT.',
        'year': 2023,
        'authors': ['Johnson, M.']
    },
    {
        'title': 'Traditional Machine Learning Methods',
        'abstract': 'Classical approaches to classification and regression without deep learning.',
        'year': 2020,
        'authors': ['Lee, K.']
    },
    {
        'title': 'LLM-based Annotation Tools for Risk Assessment',
        'abstract': 'Developing automated tools using large language models for annotating medical literature.',
        'year': 2025,
        'authors': ['Garcia, P.', 'Zhou, L.']
    }
])

# Test query (similar to user's example)
test_query = '("Large Language Model*" OR "LLM*" OR "GPT*" OR "Transformer*") AND ("Risk" OR "assessment")'

print(f"\nTest Query: {test_query}")
print(f"Search Fields: ['title', 'abstract']")
print(f"Total References: {len(test_data)}")

matched, unmatched, stats = search_references(test_data, test_query, ['title', 'abstract'])

print(f"\n{'='*60}")
print(f"RESULTS:")
print(f"{'='*60}")
print(f"Total: {stats['total_refs']}")
print(f"Matched: {stats['matched_count']} ({stats['match_percentage']}%)")
print(f"Unmatched: {stats['unmatched_count']}")

if stats['error']:
    print(f"\n✗ Error: {stats['error']}")
else:
    print(f"\n✓ Search executed successfully!")

print(f"\n{'='*60}")
print(f"MATCHED REFERENCES:")
print(f"{'='*60}")
for i, ref in enumerate(matched, 1):
    print(f"\n{i}. {ref['title']}")
    print(f"   Year: {ref['year']}")
    print(f"   Matched terms: {ref.get('matched_terms', [])}")
    if ref.get('title_highlighted'):
        print(f"   Title (highlighted): {ref['title_highlighted']}")

print(f"\n{'='*60}")
print(f"UNMATCHED REFERENCES:")
print(f"{'='*60}")
for i, ref in enumerate(unmatched, 1):
    print(f"{i}. {ref['title']} ({ref['year']})")

# Test 3: Wildcard matching
print("\n" + "=" * 60)
print("TEST 3: Wildcard Matching")
print("=" * 60)

wildcard_query = "assess*"
matched_wc, _, stats_wc = search_references(test_data, wildcard_query, ['title', 'abstract'])

print(f"Query: {wildcard_query}")
print(f"Matched: {stats_wc['matched_count']}")
for ref in matched_wc:
    print(f"  - {ref['title']}")
    print(f"    Matched: {ref.get('matched_terms', [])}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED!")
print("=" * 60)
