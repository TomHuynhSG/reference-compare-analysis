"""
Test script to investigate why papers with same titles aren't matching
"""
from src.comparator import normalize_title_for_key, generate_key
import pandas as pd

# Test case 1: RoBIn paper
title_a1 = "Robin: A Transformer-Based Model for Risk of Bias Inference with Machine Reading Comprehension"
title_b1 = "RoBIn: A Transformer-based model for risk of bias inference with machine reading comprehension"

print("=" * 80)
print("TEST CASE 1: RoBIn Paper")
print("=" * 80)
print(f"Title A: {title_a1}")
print(f"Title B: {title_b1}")
print()

norm_a1 = normalize_title_for_key(title_a1)
norm_b1 = normalize_title_for_key(title_b1)

print(f"Normalized A: {norm_a1}")
print(f"Normalized B: {norm_b1}")
print(f"Match: {norm_a1 == norm_b1}")
print()

# Test with full rows
row_a1 = pd.Series({
    'title': title_a1,
    'ti': title_a1,
    'year': '2024',
    'py': '2024///',
    'doi': None
})

row_b1 = pd.Series({
    'title': title_b1,
    'ti': title_b1,
    'year': '2025',
    'py': '2025',
    'doi': None
})

key_a1 = generate_key(row_a1)
key_b1 = generate_key(row_b1)

print(f"Key A: {key_a1}")
print(f"Key B: {key_b1}")
print(f"Keys Match: {key_a1 == key_b1}")
print()

# Test case 2: Claude 2 paper
title_a2 = "Exploring the potential of Claude 2 for risk of bias assessment: Using a large language model to assess randomized controlled trials with RoB 2"
title_b2 = "Exploring the potential of Claude 2 for risk of bias assessment: Using a large language model to assess randomized controlled trials with RoB 2"

print("=" * 80)
print("TEST CASE 2: Claude 2 Paper")
print("=" * 80)
print(f"Title A: {title_a2}")
print(f"Title B: {title_b2}")
print()

norm_a2 = normalize_title_for_key(title_a2)
norm_b2 = normalize_title_for_key(title_b2)

print(f"Normalized A: {norm_a2}")
print(f"Normalized B: {norm_b2}")
print(f"Match: {norm_a2 == norm_b2}")
print()

row_a2 = pd.Series({
    'title': title_a2,
    'ti': title_a2,
    'year': '2025',
    'py': '2025',
    'doi': '10.1017/rsm.2025.12'
})

row_b2 = pd.Series({
    'title': title_b2,
    'ti': title_b2,
    'year': '2024',
    'py': '2024///',
    'doi': None
})

key_a2 = generate_key(row_a2)
key_b2 = generate_key(row_b2)

print(f"Key A: {key_a2}")
print(f"Key B: {key_b2}")
print(f"Keys Match: {key_a2 == key_b2}")
print()

print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print("Issue 1: Years are different (2024 vs 2025)")
print("Issue 2: One has DOI, the other doesn't - DOI takes priority in matching!")
print()
