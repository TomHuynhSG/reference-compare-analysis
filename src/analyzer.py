import pandas as pd
from collections import Counter

def analyze_references(df):
    """
    Analyze the references DataFrame and return statistics.
    """
    if df.empty:
        return {
            "total_references": 0,
            "years_distribution": {},
            "top_authors": {},
            "top_journals": {}
        }

    # Total references
    total_references = len(df)

    # Years distribution
    if 'year' in df.columns:
        years_dist = df['year'].value_counts().sort_index().to_dict()
    elif 'py' in df.columns:
        years_dist = df['py'].apply(lambda x: str(x)[:4] if pd.notna(x) else 'Unknown').value_counts().sort_index().to_dict()
    else:
        years_dist = {}

    # Top Authors
    # Authors are often lists in rispy, we need to flatten
    all_authors = []
    if 'authors' in df.columns:
        for authors_list in df['authors'].dropna():
            if isinstance(authors_list, list):
                all_authors.extend(authors_list)
            elif isinstance(authors_list, str):
                all_authors.append(authors_list)
    elif 'au' in df.columns: # fallback if 'authors' not present but 'au' is
         for authors_list in df['au'].dropna():
            if isinstance(authors_list, list):
                all_authors.extend(authors_list)
            elif isinstance(authors_list, str):
                all_authors.append(authors_list)
    
    top_authors = dict(Counter(all_authors).most_common(10))

    # Top Journals
    # RIS tags for journal: 'journal_name', 'secondary_title', 't2', 'jo'
    journal_col = None
    for col in ['journal_name', 'secondary_title', 't2', 'jo']:
        if col in df.columns:
            journal_col = col
            break
    
    top_journals = {}
    if journal_col:
        top_journals = df[journal_col].value_counts().head(10).to_dict()

    return {
        "total_references": total_references,
        "years_distribution": years_dist,
        "top_authors": top_authors,
        "top_journals": top_journals
    }
