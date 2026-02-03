from flask import Flask, render_template, request, redirect, url_for
from src.parser import parse_ris_file, entries_to_df
from src.analyzer import analyze_references
from src.comparator import compare_datasets
import os

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

    return redirect(url_for('index'))

@app.route('/compare', methods=['POST'])
def compare():
    if 'file_a' not in request.files or 'file_b' not in request.files:
        return redirect(url_for('index'))
    
    file_a = request.files['file_a']
    file_b = request.files['file_b']
    
    if file_a.filename == '' or file_b.filename == '':
        return redirect(url_for('index'))

    entries_a = parse_ris_file(file_a.stream.read())
    entries_b = parse_ris_file(file_b.stream.read())
    
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
