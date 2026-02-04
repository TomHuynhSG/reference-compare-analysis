"""
Quick test to validate wildcard matching fix
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.search_engine import match_term

# Test cases for wildcard matching
tests = [
    # (term, text, should_match, description)
    ("assess*", "Assessment of Bias", True, "assess* should match Assessment"),
    ("assess*", "assisting with tasks", True, "assess* should match assisting"),
    ("Large Language Model*", "large language models", True, "Phrase with wildcard should match"),
    ("Large Language Model*", "large language", False, "Should not match incomplete phrase"),
    ("LLM*", "LLMs are useful", True, "LLM* should match LLMs"),
    ("LLM*", "preliminary data", False, "LLM* should NOT match 'llm' inside 'preliminary'"),
    ("GPT*", "GPT-4 and GPT-3.5", True, "GPT* should match GPT-4"),
    ("*model", "language model", True, "*model should match 'model' at end"),
    ("*model", "models are great", False, "*model should NOT match 'models' (different form)"),
]

print("=" * 70)
print("WILDCARD MATCHING TESTS")
print("=" * 70)

passed = 0
failed = 0

for term, text, should_match, description in tests:
    matched, matches = match_term(term, text, is_phrase=('"' in term))
    
    if matched == should_match:
        print(f"✓ PASS: {description}")
        print(f"  Term: '{term}' in '{text}'")
        print(f"  Matches: {matches}")
        passed += 1
    else:
        print(f"✗ FAIL: {description}")
        print(f"  Term: '{term}' in '{text}'")
        print(f"  Expected: {should_match}, Got: {matched}")
        print(f"  Matches: {matches}")
        failed += 1
    print()

print("=" * 70)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 70)
