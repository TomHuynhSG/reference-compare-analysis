"""
Multi-file deduplication module.

Handles deduplication across multiple RIS files, tracking which files
each reference appears in and which duplicates were removed.
"""

import pandas as pd
from src.comparator import generate_key, normalize_title_for_key


def deduplicate_multiple_files(file_data_list):
    """
    Deduplicate references across multiple RIS files.
    
    Args:
        file_data_list: List of tuples (filename, dataframe)
        
    Returns:
        unique_refs: List of dicts - unique references with source info
        duplicates: List of dicts - removed duplicates with source info
    """
    if not file_data_list:
        return [], []
    
    # Track all references with their source files
    all_refs = []
    
    for filename, df in file_data_list:
        if df.empty:
            continue
            
        # Add source filename to each reference
        refs = df.to_dict('records')
        for ref in refs:
            ref['source_file'] = filename
            ref['match_key'] = generate_key(pd.Series(ref))
        
        all_refs.extend(refs)
    
    if not all_refs:
        return [], []
    
    # Group by match key to find duplicates
    key_to_refs = {}
    for ref in all_refs:
        key = ref['match_key']
        if key not in key_to_refs:
            key_to_refs[key] = []
        key_to_refs[key].append(ref)
    
    # Separate unique and duplicate references
    unique_refs = []
    duplicates = []
    
    for key, refs in key_to_refs.items():
        if len(refs) == 1:
            # Unique reference (appears in only one file)
            ref = refs[0].copy()
            ref['appears_in'] = [ref['source_file']]
            ref['occurrence_count'] = 1
            unique_refs.append(ref)
        else:
            # Duplicate reference (appears in multiple files)
            # Keep the first occurrence as the "master"
            master_ref = refs[0].copy()
            master_ref['appears_in'] = [r['source_file'] for r in refs]
            master_ref['occurrence_count'] = len(refs)
            unique_refs.append(master_ref)
            
            # Track removed duplicates (all occurrences after the first)
            for ref in refs[1:]:
                dup_ref = ref.copy()
                dup_ref['duplicate_of'] = refs[0]['source_file']
                dup_ref['all_sources'] = [r['source_file'] for r in refs]
                duplicates.append(dup_ref)
    
    # Clean up match_key from results
    for ref in unique_refs + duplicates:
        ref.pop('match_key', None)
    
    # Sort results
    unique_refs.sort(key=lambda x: (
        x.get('year') or x.get('py') or '0000',
        x.get('title') or x.get('ti') or ''
    ), reverse=True)
    
    duplicates.sort(key=lambda x: x.get('source_file', ''))
    
    return unique_refs, duplicates


def get_deduplication_stats(unique_refs, duplicates, file_data_list):
    """
    Calculate statistics for deduplication results.
    
    Args:
        unique_refs: List of unique references
        duplicates: List of removed duplicates
        file_data_list: Original file data
        
    Returns:
        Dictionary of statistics
    """
    total_refs = sum(len(df) for _, df in file_data_list if not df.empty)
    
    # Count references by file
    file_counts = {}
    for filename, df in file_data_list:
        file_counts[filename] = len(df)
    
    # Count duplicates by file
    dup_by_file = {}
    for dup in duplicates:
        source = dup.get('source_file', 'Unknown')
        dup_by_file[source] = dup_by_file.get(source, 0) + 1
    
    return {
        'total_original': total_refs,
        'total_unique': len(unique_refs),
        'total_duplicates': len(duplicates),
        'reduction_count': len(duplicates),
        'reduction_percent': (len(duplicates) / total_refs * 100) if total_refs > 0 else 0,
        'file_counts': file_counts,
        'duplicates_by_file': dup_by_file,
        'num_files': len(file_data_list)
    }
