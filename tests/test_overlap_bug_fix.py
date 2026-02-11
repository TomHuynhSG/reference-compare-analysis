"""
Comprehensive test suite for overlap detection bug fixes.

Tests the three critical bugs identified:
1. DOI Asymmetry: File A has DOI, File B doesn't (or vice versa)
2. Year Variation: Same paper with different years (2024 vs 2025)
3. Combined Bug: Papers with identical titles that weren't matching

Uses the exact examples provided by the user.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import parse_ris_file, entries_to_df
from src.comparator import compare_datasets, generate_key, fuzzy_match_pass
import pandas as pd


def test_doi_asymmetry_bug():
    """
    Test Bug #1: DOI in one file but not the other.
    
    Before fix: Papers with same title couldn't match if only one had DOI
    After fix: Match on title+year even when DOI is asymmetric
    """
    print("\n" + "="*80)
    print("TEST 1: DOI Asymmetry Bug")
    print("="*80)
    
    # Claude 2 paper example from user
    df_a = pd.DataFrame([{
        'title': 'Exploring the potential of Claude 2 for risk of bias assessment: Using a large language model to assess randomized controlled trials with RoB 2',
        'year': '2025',
        'doi': '10.1017/rsm.2025.12',  # Has DOI
        'authors': ['Eisele-Metzger, A', 'Lieberum, JL']
    }])
    
    df_b = pd.DataFrame([{
        'title': 'Exploring the potential of Claude 2 for risk of bias assessment: Using a large language model to assess randomized controlled trials with RoB 2',
        'year': '2024',  # Different year
        'doi': None,  # NO DOI
        'authors': ['Eisele-Metzger, A', 'Lieberum, JL']
    }])
    
    # Test key generation
    keys_a = generate_key(df_a.iloc[0])
    keys_b = generate_key(df_b.iloc[0])
    
    print(f"File A keys: {keys_a}")
    print(f"File B keys: {keys_b}")
    print()
    
    # Test comparison
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)
    
    print(f"Results:")
    print(f"  Overlap: {len(overlap)}")
    print(f"  Unique to A: {len(unique_a)}")
    print(f"  Unique to B: {len(unique_b)}")
    
    if len(overlap) == 1:
        print("✅ PASS: DOI asymmetry bug FIXED!")
        print(f"  Match type: {'Fuzzy' if overlap[0].get('fuzzy_match') else 'Exact'}")
        return True
    else:
        print("❌ FAIL: Papers should match despite DOI asymmetry")
        return False


def test_year_variation_bug():
    """
    Test Bug #2: Same paper with different years (2024 vs 2025).
    
    Before fix: Required exact year match
    After fix: Allow ±1 year for highly similar titles
    """
    print("\n" + "="*80)
    print("TEST 2: Year Variation Bug (±1 year tolerance)")
    print("="*80)
    
    # RoBIn paper example from user
    df_a = pd.DataFrame([{
        'title': 'Robin: A Transformer-Based Model for Risk of Bias Inference with Machine Reading Comprehension',
        'year': '2024',
        'doi': None,
        'authors': ['Comba, J', 'Dias, A Corrêa']
    }])
    
    df_b = pd.DataFrame([{
        'title': 'RoBIn: A Transformer-based model for risk of bias inference with machine reading comprehension',
        'year': '2025',  # Different year!
        'doi': None,
        'authors': ['Dias, Abel Corrêa', 'Moreira, Viviane Pereira']
    }])
    
    # Test comparison
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)
    
    print(f"Results:")
    print(f"  Overlap: {len(overlap)}")
    print(f"  Unique to A: {len(unique_a)}")
    print(f"  Unique to B: {len(unique_b)}")
    
    if len(overlap) == 1:
        print("✅ PASS: Year variation bug FIXED!")
        print(f"  Match type: {'Fuzzy' if overlap[0].get('fuzzy_match') else 'Exact'}")
        return True
    else:
        print("❌ FAIL: Papers with ±1 year should match for identical titles")
        return False


def test_exact_ris_examples():
    """
    Test with the exact RIS entries provided by user.
    
    Parses the raw RIS format and verifies matching.
    """
    print("\n" + "="*80)
    print("TEST 3: Exact RIS Examples from User")
    print("="*80)
    
    # RIS Entry 1: RoBIn paper from File A
    ris_a = """TY  - JOUR
AU  - Comba, J
AU  - Dias, A Corrêa
TI  - Robin: A Transformer-Based Model for Risk of Bias Inference with Machine Reading Comprehension
JF  - Available at SSRN …
PB  - papers.ssrn.com
UR  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5031455
PY  - 2024///
AB  - … Using the RoBIn dataset, we trained Transformerbased … classification step that performs RoB assessments.
M1  - Query date: 2026-02-06 16:27:32
ER  - 
"""
    
    # RIS Entry 2: RoBIn paper from File B
    ris_b = """TY  - JOUR
AB  - Objective: Scientific publications are essential for uncovering insights
AU  - Dias, Abel Corrêa
AU  - Moreira, Viviane Pereira
AU  - Comba, João Luiz Dihl
PY  - 2025
SN  - 1532-0464
SP  - 104819
ST  - RoBIn: A Transformer-based model for risk of bias inference with machine reading comprehension
T2  - Journal of Biomedical Informatics
TI  - RoBIn: A Transformer-based model for risk of bias inference with machine reading comprehension
VL  - 166
ID  - 459
ER  - 
"""
    
    entries_a = parse_ris_file(ris_a)
    entries_b = parse_ris_file(ris_b)
    
    df_a = entries_to_df(entries_a)
    df_b = entries_to_df(entries_b)
    
    print(f"Parsed File A: {len(df_a)} entries")
    if not df_a.empty:
        print(f"  Title: {df_a.iloc[0].get('title', 'N/A')[:60]}...")
        print(f"  Year: {df_a.iloc[0].get('year', 'N/A')}")
    
    print(f"Parsed File B: {len(df_b)} entries")
    if not df_b.empty:
        print(f"  Title: {df_b.iloc[0].get('title', 'N/A')[:60]}...")
        print(f"  Year: {df_b.iloc[0].get('year', 'N/A')}")
    
    # Test comparison
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)
    
    print(f"\nResults:")
    print(f"  Overlap: {len(overlap)}")
    print(f"  Unique to A: {len(unique_a)}")
    print(f"  Unique to B: {len(unique_b)}")
    
    if len(overlap) == 1:
        print("✅ PASS: RIS entries matched correctly!")
        return True
    else:
        print("❌ FAIL: RIS entries should match")
        return False


def test_claude2_ris_examples():
    """Test Claude 2 example with exact RIS format."""
    print("\n" + "="*80)
    print("TEST 4: Claude 2 RIS Examples")
    print("="*80)
    
    # Claude 2 from File A (has DOI)
    ris_a = """TY  - JOUR
AB  - Abstract Systematic reviews are essential...
AU  - Eisele-Metzger, Angelika
AU  - Lieberum, Judith-Lisa
AU  - Toews, Markus
DO  - 10.1017/rsm.2025.12
PY  - 2025
TI  - Exploring the potential of Claude 2 for risk of bias assessment: Using a large language model to assess randomized controlled trials with RoB 2
T2  - Research Synthesis Methods
ER  - 
"""
    
    # Claude 2 from File B (no DOI, different year)
    ris_b = """TY  - JOUR
AU  - Eisele-Metzger, A
AU  - Lieberum, JL
AU  - Toews, M
TI  - Exploring the potential of Claude 2 for risk of bias assessment: Using a large language model to assess randomized controlled trials with RoB 2
JF  - Research Synthesis …
PY  - 2024///
ER  - 
"""
    
    entries_a = parse_ris_file(ris_a)
    entries_b = parse_ris_file(ris_b)
    
    df_a = entries_to_df(entries_a)
    df_b = entries_to_df(entries_b)
    
    print(f"Parsed File A: {len(df_a)} entries")
    if not df_a.empty:
        print(f"  Title: {df_a.iloc[0].get('title', 'N/A')[:60]}...")
        print(f"  Year: {df_a.iloc[0].get('year', 'N/A')}")
        print(f"  DOI: {df_a.iloc[0].get('doi', 'None')}")
    
    print(f"Parsed File B: {len(df_b)} entries")
    if not df_b.empty:
        print(f"  Title: {df_b.iloc[0].get('title', 'N/A')[:60]}...")
        print(f"  Year: {df_b.iloc[0].get('year', 'N/A')}")
        print(f"  DOI: {df_b.iloc[0].get('doi', 'None')}")
    
    # Test comparison
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)
    
    print(f"\nResults:")
    print(f"  Overlap: {len(overlap)}")
    print(f"  Unique to A: {len(unique_a)}")
    print(f"  Unique to B: {len(unique_b)}")
    
    if len(overlap) == 1:
        print("✅ PASS: Claude 2 papers matched despite DOI asymmetry!")
        return True
    else:
        print("❌ FAIL: Papers should match")
        return False


def test_no_false_positives():
    """Verify fixes don't introduce false positives."""
    print("\n" + "="*80)
    print("TEST 5: No False Positives")
    print("="*80)
    
    # Different papers that should NOT match
    df_a = pd.DataFrame([{
        'title': 'Machine Learning in Healthcare',
        'year': '2023',
        'doi': None
    }])
    
    df_b = pd.DataFrame([{
        'title': 'Deep Learning in Medicine',  # Different title
        'year': '2023',
        'doi': None
    }])
    
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)
    
    print(f"Results:")
    print(f"  Overlap: {len(overlap)}")
    print(f"  Unique to A: {len(unique_a)}")
    print(f"  Unique to B: {len(unique_b)}")
    
    if len(overlap) == 0:
        print("✅ PASS: Different papers correctly not matched")
        return True
    else:
        print("❌ FAIL: False positive detected!")
        return False


def test_year_tolerance_limits():
    """Verify year tolerance doesn't exceed ±1 year."""
    print("\n" + "="*80)
    print("TEST 6: Year Tolerance Limits (should reject >1 year difference)")
    print("="*80)
    
    # Same title but 2 years apart
    df_a = pd.DataFrame([{
        'title': 'Machine Learning Applications',
        'year': '2023',
        'doi': None
    }])
    
    df_b = pd.DataFrame([{
        'title': 'Machine Learning Applications',  # Identical title
        'year': '2025',  # 2 years apart - should NOT match
        'doi': None
    }])
    
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)
    
    print(f"Results:")
    print(f"  Overlap: {len(overlap)}")
    print(f"  Unique to A: {len(unique_a)}")
    print(f"  Unique to B: {len(unique_b)}")
    
    if len(overlap) == 0:
        print("✅ PASS: Papers >1 year apart correctly not matched")
        return True
    else:
        print("⚠️  WARNING: Year tolerance may be too lenient")
        return False


def test_missing_year_asymmetry():
    """
    Test papers with identical titles where one has year and other doesn't.
    
    BUG FIX: Very high title similarity (>98%) should allow match
    even when one paper is missing year data.
    """
    print("\n" + "="*80)
    print("TEST 7: Missing Year Asymmetry (user's example)")
    print("="*80)
    
    # User's exact example
    df_a = pd.DataFrame([{
        'title': 'Using Artificial Intelligence for Automated Risk of Bias Assessment of Randomized Controlled Trials',
        'year': '2025',  # Has year
        'doi': None
    }])
    
    df_b = pd.DataFrame([{
        'title': 'Using Artificial Intelligence for Automated Risk of Bias Assessment of Randomized Controlled Trials',
        'year': None,  # NO YEAR (RIS entry missing PY field)
        'doi': None
    }])
    
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b, use_fuzzy=True)
    
    print(f"Results:")
    print(f"  Overlap: {len(overlap)}")
    print(f"  Unique to A: {len(unique_a)}")
    print(f"  Unique to B: {len(unique_b)}")
    
    if len(overlap) == 1:
        print("✅ PASS: Papers matched despite missing year in one file!")
        print("   This fixes the user's reported issue.")
        return True
    else:
        print("❌ FAIL: Should match - titles are identical")
        return False


def run_all_tests():
    """Run all bug fix tests."""
    print("="*80)
    print("BUG FIX TEST SUITE")
    print("Testing fixes for overlap detection bugs")
    print("="*80)
    
    results = {
        "DOI Asymmetry": test_doi_asymmetry_bug(),
        "Year Variation": test_year_variation_bug(),
        "RoBIn RIS Example": test_exact_ris_examples(),
        "Claude 2 RIS Example": test_claude2_ris_examples(),
        "No False Positives": test_no_false_positives(),
        "Year Tolerance Limits": test_year_tolerance_limits(),
        "Missing Year Asymmetry": test_missing_year_asymmetry(),
    }
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL BUG FIX TESTS PASSED! 🎉")
        print("\nThe following bugs have been fixed:")
        print("  1. ✅ DOI asymmetry (File A has DOI, File B doesn't)")
        print("  2. ✅ Year variations (±1 year for identical titles)")
        print("  3. ✅ Combined issues (both problems together)")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
