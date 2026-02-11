import pandas as pd
from difflib import SequenceMatcher


def normalize_title_for_key(title):
    """
    Normalize title for matching key generation.
    
    Improvements:
    - Removes common article prefixes (the, a, an)
    - Removes all non-alphanumeric characters
    - Converts to lowercase
    
    Args:
        title: Title string to normalize
        
    Returns:
        Normalized title string suitable for matching
    """
    if not isinstance(title, str):
        return ""
    
    # Convert to lowercase and strip whitespace
    title_lower = title.lower().strip()
    
    # Remove common article prefixes (English)
    # This fixes the issue where "The Impact of AI" vs "Impact of AI" wouldn't match
    article_prefixes = ['the ', 'a ', 'an ']
    for prefix in article_prefixes:
        if title_lower.startswith(prefix):
            title_lower = title_lower[len(prefix):]
            break
    
    # Remove all non-alphanumeric characters
    title_clean = ''.join(c for c in title_lower if c.isalnum())
    
    return title_clean


def generate_key(row):
    """
    Generate matching keys for a reference.
    
    FIXED: Now generates BOTH DOI and Title+Year keys to solve DOI asymmetry bug.
    Previously, when File A had DOI but File B didn't, they used incompatible
    key formats and could never match.
    
    Improvements:
    - Returns tuple of (doi_key, title_year_key) for hybrid matching
    - Uses improved title normalization (removes "The", "A", "An")
    - Validates year exists before using it
    - Prevents false matches when year is missing
    
    Args:
        row: Pandas Series representing a reference
        
    Returns:
        Tuple of (doi_key, title_year_key) - either can be None
    """
    # Generate DOI key if available
    doi = row.get('doi') or row.get('do')
    doi_key = None
    if pd.notna(doi) and str(doi).strip():
        doi_key = f"DOI:{str(doi).strip().lower()}"
    
    # Always generate Title + Year key as fallback
    title = row.get('title') or row.get('primary_title') or row.get('ti') or ""
    year = row.get('year') or row.get('py') or ""
    
    # Use improved normalization (removes article prefixes)
    title_norm = normalize_title_for_key(title)
    
    # Validate year exists - prevents false matches for papers without years
    if pd.notna(year) and str(year).strip():
        year_str = str(year)[:4]
    else:
        # Use title length as weak discriminator to prevent false matches
        # Papers with same title but no year won't match unless same length
        year_str = f"NOYEAR_{len(title_norm)}"
    
    title_year_key = f"TY:{title_norm}_{year_str}"
    
    return (doi_key, title_year_key)


def fuzzy_match_pass(unique_a, unique_b, threshold=0.90, year_tolerance=1):
    """
    Perform fuzzy matching on previously unmatched items.
    
    Uses SequenceMatcher to find titles with minor variations (typos, etc.)
    that should be considered the same reference.
    
    FIXED: Now allows ±year_tolerance for publications with high title similarity.
    This solves the issue where same paper published across year boundary
    (preprint 2024 vs published 2025) wouldn't match.
    
    Improvements:
    - Activates fuzzy matching (was implemented but not used)
    - Catches typos like "Machine Learning" vs "Machine Learing"
    - Allows year tolerance for highly similar titles (>95%)
    
    Args:
        unique_a: List of items unique to dataset A
        unique_b: List of items unique to dataset B
        threshold: Similarity threshold (0.0 to 1.0), default 0.90
        year_tolerance: Max year difference allowed for high-similarity titles, default 1
        
    Returns:
        new_matches: List of (item_a, item_b) tuples that match
        remaining_a: Items from A that still don't match
        remaining_b: Items from B that still don't match
    """
    new_matches = []
    matched_a_indices = set()
    matched_b_indices = set()
    
    for i, item_a in enumerate(unique_a):
        title_a = item_a.get('title') or item_a.get('ti') or ""
        year_a = item_a.get('year') or item_a.get('py') or ""
        
        if not title_a:
            continue
        
        title_a_norm = normalize_title_for_key(title_a)
        
        for j, item_b in enumerate(unique_b):
            if j in matched_b_indices:
                continue
            
            title_b = item_b.get('title') or item_b.get('ti') or ""
            year_b = item_b.get('year') or item_b.get('py') or ""
            
            if not title_b:
                continue
            
            title_b_norm = normalize_title_for_key(title_b)
            
            if not title_a_norm or not title_b_norm:
                continue
            
            # Calculate similarity using SequenceMatcher
            similarity = SequenceMatcher(None, title_a_norm, title_b_norm).ratio()
            
            # Check if titles meet threshold
            if similarity < threshold:
                continue
            
            # Year validation with tolerance for high-similarity matches
            # FIXED: Allow ±year_tolerance for papers with very similar titles (>95%)
            # ENHANCED: Allow missing year for extremely similar titles (>98%)
            # BUG FIX: Properly handle pandas NaN values
            # This catches same publication with different year metadata
            
            # Extract and clean years, handling NaN/None properly
            import pandas as pd
            year_a_clean = ""
            year_b_clean = ""
            
            if year_a and not (pd.isna(year_a) if pd else False):
                year_a_clean = str(year_a)[:4]
            
            if year_b and not (pd.isna(year_b) if pd else False):
                year_b_clean = str(year_b)[:4]
            
            # Case 1: Both have years
            if year_a_clean and year_b_clean:
                try:
                    year_diff = abs(int(year_a_clean) - int(year_b_clean))
                    
                    # For very high similarity (>95%), allow year tolerance
                    if similarity >= 0.95:
                        if year_diff > year_tolerance:
                            continue
                    # For standard similarity, require exact year match
                    elif year_diff > 0:
                        continue
                except ValueError:
                    # If year parsing fails, require exact string match
                    if year_a_clean != year_b_clean:
                        continue
            
            # Case 2: One or both missing year
            elif year_a_clean != year_b_clean:
                # BUG FIX: Allow match if title similarity is VERY high (>98%)
                # This handles cases where one RIS entry is missing year field
                # Example: File A has "PY - 2025///" but File B has no PY tag
                if similarity < 0.98:
                    # If similarity is not extremely high, skip
                    continue
                # else: Allow match even with year asymmetry
            
            # Match found!
            new_matches.append((item_a, item_b))
            matched_a_indices.add(i)
            matched_b_indices.add(j)
            break  # Move to next item_a
    
    # Get remaining unmatched items
    remaining_a = [item for i, item in enumerate(unique_a) if i not in matched_a_indices]
    remaining_b = [item for j, item in enumerate(unique_b) if j not in matched_b_indices]
    
    return new_matches, remaining_a, remaining_b


def calculate_match_confidence(item_a, item_b):
    """
    Calculate confidence score for a match.
    
    Helps users understand match quality and identify potential false matches.
    
    Args:
        item_a: Reference from dataset A
        item_b: Reference from dataset B
        
    Returns:
        float: Confidence score from 0.0 to 1.0
        str: Reason for the score
    """
    # DOI match = highest confidence
    doi_a = item_a.get('doi') or item_a.get('do')
    doi_b = item_b.get('doi') or item_b.get('do')
    
    if doi_a and doi_b and str(doi_a).strip().lower() == str(doi_b).strip().lower():
        return 1.0, "DOI match"
    
    # Title + Year exact match
    title_a = normalize_title_for_key(item_a.get('title', ''))
    title_b = normalize_title_for_key(item_b.get('title', ''))
    year_a = str(item_a.get('year', ''))[:4]
    year_b = str(item_b.get('year', ''))[:4]
    
    if title_a == title_b and year_a == year_b and year_a:
        return 0.95, "Exact title+year match"
    
    # Fuzzy title match
    if title_a and title_b:
        similarity = SequenceMatcher(None, title_a, title_b).ratio()
        
        if similarity >= 0.95 and year_a == year_b:
            return 0.90, f"High similarity ({similarity:.2f})"
        elif similarity >= 0.90 and year_a == year_b:
            return 0.85, f"Good similarity ({similarity:.2f})"
        elif similarity >= 0.85 and year_a == year_b:
            return 0.75, f"Fair similarity ({similarity:.2f})"
    
    return 0.50, "Low confidence match"


def robust_title_match(title1, title2):
    """
    Check if two titles are similar enough to be considered the same.
    
    Uses SequenceMatcher with 90% similarity threshold.
    
    Args:
        title1: First title
        title2: Second title
        
    Returns:
        bool: True if titles match (exact or >90% similar)
    """
    if not isinstance(title1, str) or not isinstance(title2, str):
        return False
    
    # Normalize: lowercase, remove non-alphanumeric chars
    t1 = normalize_title_for_key(title1)
    t2 = normalize_title_for_key(title2)
    
    if t1 == t2:
        return True
    
    # Fuzzy match for slight variations
    return SequenceMatcher(None, t1, t2).ratio() > 0.9


def compare_datasets(df_a, df_b, use_fuzzy=True):
    """
    Compare two DataFrames of references with improved matching.
    
    FIXED: Now uses hybrid key matching to solve DOI asymmetry bug.
    Papers can match on either DOI or Title+Year, preventing false negatives
    when only one file has a DOI.
    
    Improvements over original version:
    1. Hybrid key generation (both DOI and Title+Year)
    2. Article prefix removal in titles ("The", "A", "An")
    3. Active fuzzy matching for typos and variations
    4. Year tolerance for publication variations (±1 year for high similarity)
    5. Better handling of missing years
    6. Match confidence scoring
    
    Algorithm:
    1. Generate (doi_key, title_year_key) tuples for all references
    2. Match on EITHER DOI key OR title+year key (hybrid matching)
    3. Perform set operations to find overlap and unique items
    4. Apply fuzzy matching to unmatched items (optional)
    5. Return results with temp keys cleaned up
    
    Args:
        df_a: DataFrame of references from source A
        df_b: DataFrame of references from source B
        use_fuzzy: Enable fuzzy matching for unmatched items (default: True)
        
    Returns:
        overlap: List of dicts - references in both A and B
        unique_a: List of dicts - references only in A
        unique_b: List of dicts - references only in B
    """
    if df_a.empty:
        return [], [], df_b.to_dict('records')
    if df_b.empty:
        return [], df_a.to_dict('records'), []

    # Step 1: Generate hybrid keys (doi_key, title_year_key) for all references
    df_a['temp_keys'] = df_a.apply(generate_key, axis=1)
    df_b['temp_keys'] = df_b.apply(generate_key, axis=1)

    # Step 2: Build lookup dictionaries for hybrid matching
    # For each reference, create entries for both DOI and Title+Year keys
    index_a_by_key = {}  # key -> list of indices in df_a
    index_b_by_key = {}  # key -> list of indices in df_b
    
    for idx, keys in enumerate(df_a['temp_keys']):
        doi_key, title_year_key = keys
        if doi_key:
            if doi_key not in index_a_by_key:
                index_a_by_key[doi_key] = []
            index_a_by_key[doi_key].append(idx)
        if title_year_key:
            if title_year_key not in index_a_by_key:
                index_a_by_key[title_year_key] = []
            index_a_by_key[title_year_key].append(idx)
    
    for idx, keys in enumerate(df_b['temp_keys']):
        doi_key, title_year_key = keys
        if doi_key:
            if doi_key not in index_b_by_key:
                index_b_by_key[doi_key] = []
            index_b_by_key[doi_key].append(idx)
        if title_year_key:
            if title_year_key not in index_b_by_key:
                index_b_by_key[title_year_key] = []
            index_b_by_key[title_year_key].append(idx)
    
    # Step 3: Find overlaps - match on ANY common key (DOI or Title+Year)
    all_keys_a = set(index_a_by_key.keys())
    all_keys_b = set(index_b_by_key.keys())
    overlap_keys = all_keys_a.intersection(all_keys_b)
    
    # Collect matched indices
    matched_indices_a = set()
    matched_indices_b = set()
    
    for key in overlap_keys:
        if key in index_a_by_key:
            matched_indices_a.update(index_a_by_key[key])
        if key in index_b_by_key:
            matched_indices_b.update(index_b_by_key[key])
    
    # Step 4: Extract records
    overlap = df_a.iloc[list(matched_indices_a)].to_dict('records')
    unique_a_indices = [i for i in range(len(df_a)) if i not in matched_indices_a]
    unique_b_indices = [i for i in range(len(df_b)) if i not in matched_indices_b]
    unique_a = df_a.iloc[unique_a_indices].to_dict('records')
    unique_b = df_b.iloc[unique_b_indices].to_dict('records')

    # Step 5: Fuzzy matching pass (catches typos and year variations)
    if use_fuzzy and unique_a and unique_b:
        fuzzy_matches, unique_a, unique_b = fuzzy_match_pass(unique_a, unique_b)
        
        # Add fuzzy matches to overlap (take from A for consistency)
        for item_a, item_b in fuzzy_matches:
            # Mark as fuzzy match for user visibility
            item_a['fuzzy_match'] = True
            overlap.append(item_a)

    # Cleanup temp column from result dicts
    for rec in overlap + unique_a + unique_b:
        rec.pop('temp_keys', None)

    return overlap, unique_a, unique_b
