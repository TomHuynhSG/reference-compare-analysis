from flask import Flask, render_template, request, redirect, url_for, Response, session
from src.parser import parse_ris_file, entries_to_df
from src.analyzer import analyze_references
from src.comparator import compare_datasets
from src.deduplicator import deduplicate_multiple_files, get_deduplication_stats
from src.exporter import export_to_ris_string
from src.search_engine import search_references
import os
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session or flash messages if used

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'ris_file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['ris_file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        entries = parse_ris_file(file.stream.read())
        df = entries_to_df(entries)
        stats = analyze_references(df)
        records = df.to_dict('records') if not df.empty else []
    return render_template('analyze.html', stats=stats, records=records, filename=file.filename)


UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/compare', methods=['POST'])
def compare():
    if 'file_a' not in request.files or 'file_b' not in request.files:
        return redirect(url_for('index'))
    
    file_a = request.files['file_a']
    file_b = request.files['file_b']
    
    if file_a.filename == '' or file_b.filename == '':
        return redirect(url_for('index'))

    # Save files for export functionality
    path_a = os.path.join(app.config['UPLOAD_FOLDER'], file_a.filename)
    path_b = os.path.join(app.config['UPLOAD_FOLDER'], file_b.filename)
    
    file_a.save(path_a)
    file_b.save(path_b)
    
    # Read back for parsing
    with open(path_a, 'r', encoding='utf-8', errors='ignore') as f:
        entries_a = parse_ris_file(f.read())
        
    with open(path_b, 'r', encoding='utf-8', errors='ignore') as f:
        entries_b = parse_ris_file(f.read())
    
    df_a = entries_to_df(entries_a)
    df_b = entries_to_df(entries_b)
    
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b)
    
    stats = {
        "overlap_count": len(overlap),
        "unique_a_count": len(unique_a),
        "unique_b_count": len(unique_b),
        "total_a": len(df_a),
        "total_b": len(df_b)
    }

    return render_template('compare.html', 
                           overlap=overlap, 
                           unique_a=unique_a, 
                           unique_b=unique_b, 
                           stats=stats,
                           filename_a=file_a.filename,
                           filename_b=file_b.filename)

@app.route('/export_ris')
def export_ris():
    from src.exporter import export_to_ris_string
    from flask import Response

    filename_a = request.args.get('filename_a')
    filename_b = request.args.get('filename_b')
    subset = request.args.get('subset') # 'overlap', 'unique_a', 'unique_b'
    
    if not filename_a or not filename_b or not subset:
        return "Missing arguments", 400
        
    path_a = os.path.join(app.config['UPLOAD_FOLDER'], filename_a)
    path_b = os.path.join(app.config['UPLOAD_FOLDER'], filename_b)
    
    if not os.path.exists(path_a) or not os.path.exists(path_b):
        return "Files expired or missing. Please re-upload.", 404
        
    # Re-process to get the subset
    with open(path_a, 'r', encoding='utf-8', errors='ignore') as f:
        entries_a = parse_ris_file(f.read())
    with open(path_b, 'r', encoding='utf-8', errors='ignore') as f:
        entries_b = parse_ris_file(f.read())
        
    df_a = entries_to_df(entries_a)
    df_b = entries_to_df(entries_b)
    
    overlap, unique_a, unique_b = compare_datasets(df_a, df_b)
    
    target_data = []
    export_filename = "export.ris"
    
    if subset == 'unique_a':
        target_data = unique_a
        export_filename = f"unique_to_{filename_a}"
    elif subset == 'unique_b':
        target_data = unique_b
        export_filename = f"unique_to_{filename_b}"
    elif subset == 'overlap':
        target_data = overlap
        export_filename = f"overlap_{filename_a}_{filename_b}.ris"
        
    if not export_filename.endswith('.ris'):
        export_filename += '.ris'
        
    ris_content = export_to_ris_string(target_data)
    
    return Response(
        ris_content,
        mimetype="application/x-research-info-systems",
        headers={"Content-Disposition": f"attachment;filename={export_filename}"}
    )


@app.route('/deduplicate', methods=['POST'])
def deduplicate():
    """
    Handle multi-file deduplication.
    Upload multiple RIS files and remove duplicates across all files.
    """
    # Get all uploaded files
    files = request.files.getlist('ris_files')
    
    if not files or all(f.filename == '' for f in files):
        return redirect(url_for('index'))
    
    # Parse all files
    file_data_list = []
    filenames = []
    
    for file in files:
        if file.filename == '':
            continue
            
        # Save file for potential re-export
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Parse file
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            entries = parse_ris_file(f.read())
            df = entries_to_df(entries)
            
        if not df.empty:
            file_data_list.append((file.filename, df))
            filenames.append(file.filename)
    
    if not file_data_list:
        return redirect(url_for('index'))
    
    # Perform deduplication
    unique_refs, duplicates = deduplicate_multiple_files(file_data_list)
    
    # Calculate statistics
    stats = get_deduplication_stats(unique_refs, duplicates, file_data_list)
    
    return render_template(
        'deduplicate.html',
        unique_refs=unique_refs,
        duplicates=duplicates,
        stats=stats,
        filenames=filenames
    )


@app.route('/export_dedup/<table_type>', methods=['POST'])
def export_dedup(table_type):
    """
    Export deduplication results (either unique or duplicates table).
    
    Args:
        table_type: 'unique' or 'duplicates'
    """
    # Re-process files from uploads folder
    filenames = request.form.getlist('filenames')
    
    if not filenames:
        return redirect(url_for('index'))
    
    # Reload and re-deduplicate
    file_data_list = []
    for filename in filenames:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            entries = parse_ris_file(f.read())
            df = entries_to_df(entries)
            
        if not df.empty:
            file_data_list.append((filename, df))
    
    unique_refs, duplicates = deduplicate_multiple_files(file_data_list)
    
    # Select export data based on type
    if table_type == 'unique':
        export_data = unique_refs
        export_filename = 'unique_references.ris'
    else:  # duplicates
        export_data = duplicates
        export_filename = 'removed_duplicates.ris'
    
    # Clean up metadata fields before export
    clean_data = []
    for ref in export_data:
        clean_ref = ref.copy()
        # Remove deduplication metadata
        clean_ref.pop('source_file', None)
        clean_ref.pop('appears_in', None)
        clean_ref.pop('occurrence_count', None)
        clean_ref.pop('duplicate_of', None)
        clean_ref.pop('all_sources', None)
        clean_data.append(clean_ref)
    
    ris_content = export_to_ris_string(clean_data)
    
    return Response(
        ris_content,
        mimetype="application/x-research-info-systems",
        headers={"Content-Disposition": f"attachment;filename={export_filename}"}
    )


@app.route('/search', methods=['POST'])
def search():
    """
    Handle initial search query with file upload.
    Parse RIS file, execute search, and store file in session for re-querying.
    """
    if 'ris_file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['ris_file']
    query = request.form.get('query', '').strip()
    fields = request.form.getlist('fields')  # List of selected fields
    
    if file.filename == '' or not query:
        return redirect(url_for('index'))
    
    if not fields:
        fields = ['title', 'abstract']  # Default fields
    
    # Generate unique ID for this search session
    search_id = str(uuid.uuid4())
    
    # Save file for re-querying
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"search_{search_id}_{file.filename}")
    file.save(filepath)
    
    # Parse RIS file
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        entries = parse_ris_file(f.read())
    
    df = entries_to_df(entries)
    
    # Execute search
    matched_refs, unmatched_refs, stats = search_references(df, query, fields)
    
    # Store in session for re-querying
    session['search_file_id'] = search_id
    session['search_filename'] = file.filename
    session['search_filepath'] = filepath
    
    return render_template(
        'search.html',
        matched_refs=matched_refs,
        unmatched_refs=unmatched_refs,
        stats=stats,
        query=query,
        fields=fields,
        filename=file.filename
    )


@app.route('/search/requery', methods=['POST'])
def search_requery():
    """
    Re-search with new query using cached file from session.
    """
    query = request.form.get('query', '').strip()
    fields = request.form.getlist('fields')
    
    # Get cached file from session
    search_filepath = session.get('search_filepath')
    search_filename = session.get('search_filename')
    
    if not search_filepath or not os.path.exists(search_filepath):
        # Session expired or file deleted, redirect to home
        return redirect(url_for('index'))
    
    if not query:
        return redirect(url_for('index'))
    
    if not fields:
        fields = ['title', 'abstract']
    
    # Re-parse file (could be optimized with caching)
    with open(search_filepath, 'r', encoding='utf-8', errors='ignore') as f:
        entries = parse_ris_file(f.read())
    
    df = entries_to_df(entries)
    
    # Execute new search
    matched_refs, unmatched_refs, stats = search_references(df, query, fields)
    
    return render_template(
        'search.html',
        matched_refs=matched_refs,
        unmatched_refs=unmatched_refs,
        stats=stats,
        query=query,
        fields=fields,
        filename=search_filename
    )


@app.route('/export_search')
def export_search():
    """
    Export search results (matched or unmatched references) as RIS.
    """
    subset = request.args.get('subset')  # 'matched' or 'unmatched'
    query = request.args.get('query', '')
    fields_str = request.args.get('fields', 'title,abstract')
    fields = fields_str.split(',') if fields_str else ['title', 'abstract']
    
    # Get cached file from session
    search_filepath = session.get('search_filepath')
    search_filename = session.get('search_filename', 'export.ris')
    
    if not search_filepath or not os.path.exists(search_filepath):
        return "Session expired. Please re-upload your file.", 404
    
    # Re-execute search
    with open(search_filepath, 'r', encoding='utf-8', errors='ignore') as f:
        entries = parse_ris_file(f.read())
    
    df = entries_to_df(entries)
    matched_refs, unmatched_refs, stats = search_references(df, query, fields)
    
    # Select export data
    if subset == 'matched':
        export_data = matched_refs
        export_filename = f"matched_{search_filename}"
    else:
        export_data = unmatched_refs
        export_filename = f"unmatched_{search_filename}"
    
    # Clean up search-specific metadata
    clean_data = []
    for ref in export_data:
        clean_ref = ref.copy()
        clean_ref.pop('title_highlighted', None)
        clean_ref.pop('ti_highlighted', None)
        clean_ref.pop('abstract_highlighted', None)
        clean_ref.pop('ab_highlighted', None)
        clean_ref.pop('n2_highlighted', None)
        clean_ref.pop('matched_terms', None)
        clean_ref.pop('match_count', None)
        clean_data.append(clean_ref)
    
    if not export_filename.endswith('.ris'):
        export_filename += '.ris'
    
    ris_content = export_to_ris_string(clean_data)
    
    return Response(
        ris_content,
        mimetype="application/x-research-info-systems",
        headers={"Content-Disposition": f"attachment;filename={export_filename}"}
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)

