import pandas as pd
from difflib import SequenceMatcher

def robust_title_match(title1, title2):
    """
    Check if two titles are similar enough to be considered the same.
    """
    if not isinstance(title1, str) or not isinstance(title2, str):
        return False
    
    # Normalize: lowercase, remove non-alphanumeric chars (simple version)
    t1 = ''.join(e for e in title1.lower() if e.isalnum())
    t2 = ''.join(e for e in title2.lower() if e.isalnum())
    
    if t1 == t2:
        return True
    
    # Fuzzy match for slight variations
    return SequenceMatcher(None, t1, t2).ratio() > 0.9

def compare_datasets(df_a, df_b):
    """
    Compare two DataFrames of references.
    Returns: overlap, unique_a, unique_b (lists of dicts)
    """
    if df_a.empty:
        return [], [], df_b.to_dict('records')
    if df_b.empty:
        return [], df_a.to_dict('records'), []

    # Create a unique key for comparison if possible
    # Priority: DOI -> Title + Year -> Title
    
    # Helper to generate a fuzzy key
    def generate_key(row):
        doi = row.get('doi') or row.get('do')
        if pd.notna(doi) and str(doi).strip():
            return f"DOI:{str(doi).strip().lower()}"
        
        title = row.get('title') or row.get('primary_title') or row.get('ti') or ""
        year = row.get('year') or row.get('py') or ""
        
        # Simple normalization for key
        title_norm = ''.join(e for e in str(title).lower() if e.isalnum())
        year_str = str(year)[:4] if pd.notna(year) else ""
        
        return f"TY:{title_norm}_{year_str}"

    df_a['temp_key'] = df_a.apply(generate_key, axis=1)
    df_b['temp_key'] = df_b.apply(generate_key, axis=1)

    # Convert to dicts for easier manual processing if needed, but let's use sets of keys first
    keys_a = set(df_a['temp_key'])
    keys_b = set(df_b['temp_key'])

    overlap_keys = keys_a.intersection(keys_b)
    unique_a_keys = keys_a - keys_b
    unique_b_keys = keys_b - keys_a

    # Extract records
    overlap = df_a[df_a['temp_key'].isin(overlap_keys)].to_dict('records')
    # Note: For overlap, we take from A. We could merge, but taking A is simpler for display.
    
    unique_a = df_a[df_a['temp_key'].isin(unique_a_keys)].to_dict('records')
    unique_b = df_b[df_b['temp_key'].isin(unique_b_keys)].to_dict('records')

    # Cleanup temp column from the result dicts (optional, but good for cleanliness)
    for rec in overlap + unique_a + unique_b:
        rec.pop('temp_key', None)

    return overlap, unique_a, unique_b
