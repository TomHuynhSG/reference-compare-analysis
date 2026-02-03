"""
Test the multi-file deduplication feature.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import parse_ris_file, entries_to_df
from src.deduplicator import deduplicate_multiple_files, get_deduplication_stats
import pandas as pd


def test_deduplication():
    """Test multi-file deduplication with sample data."""
    print("=" * 70)
    print("MULTI-FILE DEDUPLICATION TEST")
    print("=" * 70)
    
    # Load sample files
    with open('tests/sample_a.ris', 'r') as f:
        entries_a = parse_ris_file(f.read())
    
    with open('tests/sample_b.ris', 'r') as f:
        entries_b = parse_ris_file(f.read())
    
    df_a = entries_to_df(entries_a)
    df_b = entries_to_df(entries_b)
    
    print(f"\nInput Files:")
    print(f"  sample_a.ris: {len(df_a)} references")
    print(f"  sample_b.ris: {len(df_b)} references")
    print(f"  Total: {len(df_a) + len(df_b)} references")
    
    # Perform deduplication
    file_data_list = [
        ('sample_a.ris', df_a),
        ('sample_b.ris', df_b)
    ]
    
    unique_refs, duplicates = deduplicate_multiple_files(file_data_list)
    
    print(f"\nDeduplication Results:")
    print(f"  Unique references: {len(unique_refs)}")
    print(f"  Duplicates removed: {len(duplicates)}")
    
    # Get statistics
    stats = get_deduplication_stats(unique_refs, duplicates, file_data_list)
    
    print(f"\nStatistics:")
    print(f"  Total original: {stats['total_original']}")
    print(f"  Total unique: {stats['total_unique']}")
    print(f"  Reduction: {stats['reduction_count']} ({stats['reduction_percent']:.1f}%)")
    
    print(f"\nUnique References:")
    for i, ref in enumerate(unique_refs, 1):
        title = ref.get('title', ref.get('ti', 'N/A'))
        sources = ref.get('appears_in', [])
        count = ref.get('occurrence_count', 1)
        print(f"  {i}. {title[:60]}")
        print(f"     Sources: {', '.join(sources)}")
        print(f"     Occurrences: {count}x")
    
    if duplicates:
        print(f"\nRemoved Duplicates:")
        for i, dup in enumerate(duplicates, 1):
            title = dup.get('title', dup.get('ti', 'N/A'))
            source = dup.get('source_file', 'Unknown')
            all_sources = dup.get('all_sources', [])
            print(f"  {i}. {title[:60]}")
            print(f"     Removed from: {source}")
            print(f"     Also appears in: {', '.join(all_sources)}")
    
    # Expected: 4 unique (1 from A only, 1 from B only, 2 in both)
    # Expected: 2 duplicates (the 2 that appear in both, removed from B)
    print(f"\n{'='*70}")
    if len(unique_refs) == 4 and len(duplicates) == 2:
        print("✅ TEST PASSED: Deduplication working correctly!")
        return 0
    else:
        print(f"⚠️  Expected 4 unique and 2 duplicates")
        print(f"   Got {len(unique_refs)} unique and {len(duplicates)} duplicates")
        return 1


if __name__ == "__main__":
    exit_code = test_deduplication()
    sys.exit(exit_code)
