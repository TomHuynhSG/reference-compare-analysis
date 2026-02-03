# RIS Reference Compare and Analysis System - Project Overview

## 🎯 Project Purpose

The **RIS Reference Compare and Analysis System** is a Flask-based web application designed for researchers and academics to analyze and compare citation/reference files in RIS format. It solves the common research problem of managing multiple reference libraries, identifying duplicates, and understanding publication patterns.

## 🏗️ Architecture Overview

### Technology Stack
- **Backend**: Python 3.13 + Flask 3.0.0
- **Data Processing**: Pandas 2.2.0
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Visualization**: Chart.js (for analysis charts), Custom SVG (for Venn diagrams)
- **Template Engine**: Jinja2 (comes with Flask)

### Project Structure
```
references_compare_analysis/
├── app.py                    # Main Flask application with routes
├── requirements.txt          # Python dependencies
├── src/                      # Core business logic modules
│   ├── parser.py             # RIS file parsing logic
│   ├── analyzer.py           # Statistical analysis functions
│   ├── comparator.py         # Comparison and deduplication algorithms
│   └── exporter.py           # RIS export functionality
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Base template with layout
│   ├── index.html            # Homepage with upload forms
│   ├── analyze.html          # Analysis results page
│   └── compare.html          # Comparison results page
├── static/                   # Static assets
│   ├── css/
│   │   ├── style.css         # Main stylesheet
│   │   └── variables.css     # CSS custom properties
│   └── js/
│       └── main.js           # Client-side interactions
├── tests/                    # Test files and sample data
│   ├── sample_a.ris
│   ├── sample_b.ris
│   ├── test_logic.py
│   └── test_export_fix.py
└── uploads/                  # Temporary storage for uploaded files
```

## 🔄 Data Flow

### 1. Analysis Workflow
```
User uploads RIS file → Flask receives file → parse_ris_file() → entries_to_df() 
→ analyze_references() → Generate stats & visualizations → Render analyze.html
```

### 2. Comparison Workflow
```
User uploads 2 RIS files → Flask saves both files → parse_ris_file() for each
→ entries_to_df() for each → compare_datasets() → Generate overlap/unique sets
→ Render compare.html with Venn diagram and tables
```

### 3. Export Workflow
```
User clicks export button → Flask /export_ris endpoint → Re-parse files
→ compare_datasets() → Filter subset → export_to_ris_string() 
→ Return as downloadable .ris file
```

## 📊 Core Features

### Feature 1: Single File Analysis
**Purpose**: Analyze a single RIS file to understand its composition

**Key Metrics**:
- Total number of references
- Publication year distribution
- Top 10 authors (by frequency)
- Top 10 journals (by frequency)

**Visualization**:
- Interactive bar chart showing publications over time
- Horizontal bar chart for top authors
- Sortable table with all references
- Abstract viewing in modal popups

**Implementation**:
- Route: `/analyze` (POST)
- Handler: `analyze()` in `app.py`
- Logic: `analyze_references()` in `src/analyzer.py`
- Template: `templates/analyze.html`

### Feature 2: Dataset Comparison
**Purpose**: Compare two RIS files to identify overlaps and unique entries

**Key Outputs**:
- **Overlap**: References present in both files
- **Unique to A**: References only in source A
- **Unique to B**: References only in source B

**Matching Algorithm**:
1. **Primary Key**: DOI (if available) - Exact match after normalization
2. **Fallback Key**: Title + Year - Fuzzy match using normalized strings
3. **Normalization**: Lowercase, remove non-alphanumeric characters

**Visualization**:
- Interactive SVG Venn diagram showing set relationships
- Statistics cards showing counts and percentages
- Three separate tables for each category
- Export buttons for each subset

**Implementation**:
- Route: `/compare` (POST)
- Handler: `compare()` in `app.py`
- Logic: `compare_datasets()` in `src/comparator.py`
- Template: `templates/compare.html`

### Feature 3: RIS Export
**Purpose**: Export any subset of comparison results as a valid RIS file

**Supported Subsets**:
- Overlap set
- Unique to A set
- Unique to B set

**Implementation**:
- Route: `/export_ris` (GET with query params)
- Handler: `export_ris()` in `app.py`
- Logic: `export_to_ris_string()` in `src/exporter.py`
- Output: RFC-compliant RIS formatted text file

## 🔍 Technical Deep Dive

### RIS File Parsing (`src/parser.py`)

**RIS Format**:
RIS (Research Information Systems) is a standardized tag format for citation data:
```
TY  - JOUR
TI  - Article Title
AU  - Last, First
PY  - 2024
DO  - 10.1234/example
AB  - Abstract text here
ER  - 
```

**Parsing Strategy**:
1. **Line-by-line processing**: Each line has a 2-letter tag + value
2. **Multi-value handling**: Authors (AU) are accumulated into lists
3. **Continuation lines**: Multi-line abstracts are concatenated
4. **Tag mapping**: Both standard (TI, PY, AU) and alternate (T1, Y1, A1) tags are supported
5. **Entry separation**: `ER  -` marks the end of each reference

**Key Functions**:
- `parse_ris_lines(lines)`: Core parser logic
- `parse_ris_file(file_stream)`: Wrapper handling different input types
- `entries_to_df(entries)`: Convert parsed entries to Pandas DataFrame

### Comparison Algorithm (`src/comparator.py`)

**Problem**: How to identify the same reference across different sources?

**Solution**: Multi-tiered key generation strategy

**Key Generation** (`generate_key()` function):
```python
def generate_key(row):
    # Priority 1: DOI (most reliable)
    if has_doi:
        return f"DOI:{normalized_doi}"
    
    # Priority 2: Title + Year (fuzzy-matched)
    title_normalized = ''.join(alphanumeric_chars_only).lower()
    year_4_digits = extract_year(year_field)
    return f"TY:{title_normalized}_{year_4_digits}"
```

**Why This Works**:
- DOIs are globally unique identifiers → Perfect for exact matching
- Title+Year combo is usually unique → Catches items without DOIs
- Normalization handles minor formatting differences

**Set Operations**:
```python
keys_a = set(df_a['temp_key'])
keys_b = set(df_b['temp_key'])

overlap_keys = keys_a.intersection(keys_b)    # A ∩ B
unique_a_keys = keys_a - keys_b               # A - B  
unique_b_keys = keys_b - keys_a               # B - A
```

**Fuzzy Matching** (`robust_title_match()` function):
- Uses `difflib.SequenceMatcher` for similarity scoring
- Threshold: 90% similarity (0.9 ratio)
- Currently available but not actively used (can be integrated for edge cases)

### Statistical Analysis (`src/analyzer.py`)

**Metrics Calculated**:

1. **Total References**: Simple row count
2. **Year Distribution**: 
   - Extracts first 4 digits from year field
   - Groups and counts by year
   - Returns sorted dictionary for chronological display
3. **Top Authors**:
   - Flattens author lists (since each reference can have multiple authors)
   - Uses `Counter` to tally frequency
   - Returns top 10
4. **Top Journals**:
   - Checks multiple possible journal tag names (journal_name, t2, jo)
   - Counts occurrences
   - Returns top 10

**Resilience Features**:
- Handles missing fields gracefully
- Supports both raw tags (`py`, `au`) and normalized fields (`year`, `authors`)
- Returns empty structures for empty DataFrames

### RIS Export (`src/exporter.py`)

**Challenge**: Convert Python dictionaries back to valid RIS format

**Approach**:
1. Iterate through each record
2. Map dictionary keys to RIS tags
3. Handle special cases:
   - Lists (authors) → Multiple lines with same tag
   - Missing fields → Skip entirely
   - Float/NaN values → Filter out
4. Ensure proper formatting: `TAG  - VALUE`
5. Always end with `ER  - `

**Supported Tags**:
- TY: Type of reference
- TI: Title
- AU: Authors (one per line)
- PY: Publication year
- JO: Journal
- DO: DOI
- AB: Abstract

## 🎨 Frontend Design

### Design System (`static/css/`)

**CSS Variables** (`variables.css`):
```css
--color-background: Gradient (#0f0c29 → #302b63 → #24243e)
--color-surface: rgba(255, 255, 255, 0.03)  /* Glassmorphism */
--color-primary: #42d4f4     /* Cyan accent */
--color-secondary: #ff6ec4    /* Pink accent */
--color-accent: #00FFAA       /* Green for overlap */
```

**Design Principles**:
- **Dark Mode**: Deep gradient background for premium feel
- **Glassmorphism**: Semi-transparent cards with backdrop blur
- **Responsive Grid**: 2-column layout on desktop, stacks on mobile
- **Interactive Elements**: Hover effects, smooth transitions
- **Typography**: Clean, readable sans-serif with proper hierarchy

### JavaScript Functionality (`static/js/main.js`)

**Key Features**:
1. **Table Sorting**: Click column headers to sort
2. **Abstract Modal**: Popup to view full abstracts
3. **Venn Diagram**: SVG-based interactive visualization
4. **Responsive Helpers**: Utility classes for layout

## 🐛 Bug Fixed During Review

**Issue**: Jinja2 Template Syntax Error
- **Location**: `templates/compare.html`, line 62
- **Error**: `{{ stats.unique_a_count }` (missing closing brace)
- **Fix**: Changed to `{{ stats.unique_a_count }},`
- **Root Cause**: JavaScript object literal inside Jinja2 template - typo in template code
- **Impact**: `/compare` route was completely broken (500 error)

## 🚀 Running the Application

### Prerequisites
```bash
# Python 3.13 (or 3.8+)
# Virtual environment recommended
```

### Installation
```bash
cd /Users/tom/Desktop/references_compare_analysis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Development Server
```bash
python app.py
# Visit http://127.0.0.1:5000
```

### Debug Mode
- Automatically enabled in `app.py` (`debug=True`)
- Auto-reloads on code changes
- Provides interactive debugger in browser on errors

## 📝 Usage Workflow

### Scenario 1: Analyze Your Library
1. Go to http://127.0.0.1:5000
2. Click "Analyze RIS" section
3. Upload your `.ris` file
4. View statistics, charts, and sortable table
5. Click "View" on any row to read the abstract

### Scenario 2: Merge Two Libraries
1. Go to http://127.0.0.1:5000
2. Click "Compare Datasets" section
3. Upload Source A (e.g., Zotero library)
4. Upload Source B (e.g., Mendeley library)
5. View Venn diagram and three category tables
6. Export deduplicated sets as needed:
   - Click "Export RIS" under "Overlap" to get common references
   - Click "Export RIS" under "Unique to A" to get A-only references

### Scenario 3: Identify Missing References
1. Compare your library (A) with a colleague's library (B)
2. Check "Unique to B" table
3. Export as RIS
4. Import into your reference manager

## 🔒 Security Considerations

**Current State** (Development):
- Files saved to `uploads/` directory
- No authentication/authorization
- Session management minimal
- Secret key hardcoded

**Production Recommendations**:
1. Use environment variables for secret key
2. Implement file upload size limits
3. Add CSRF protection
4. Sanitize filenames
5. Implement rate limiting
6. Add user authentication if multi-user
7. Clean up `uploads/` directory periodically
8. Use HTTPS
9. Deploy with WSGI server (Gunicorn, uWSGI)

## 🧪 Testing

**Test Files**:
- `tests/sample_a.ris`: Sample dataset A
- `tests/sample_b.ris`: Sample dataset B
- `tests/test_logic.py`: Unit tests for core logic
- `tests/test_export_fix.py`: Export functionality tests

**Manual Testing Checklist**:
- [ ] Upload valid RIS file → Analyze works
- [ ] Upload invalid file → Graceful error handling
- [ ] Compare two files → Correct overlap detection
- [ ] Export each subset → Valid RIS output
- [ ] Sort tables → Correct ordering
- [ ] View abstracts → Modal displays correctly
- [ ] Responsive design → Works on mobile

## 🎯 Future Enhancement Ideas

1. **Advanced Matching**:
   - Enable fuzzy title matching by default
   - Add author-based matching
   - Support for ISBN/ISSN matching

2. **Batch Operations**:
   - Compare 3+ files at once
   - Merge multiple sources into one

3. **Visualization Enhancements**:
   - Network graph of co-authorship
   - Timeline view of publications
   - Geographic distribution of authors

4. **Export Formats**:
   - BibTeX export
   - CSV/Excel export
   - Copy-paste formatted citations

5. **User Features**:
   - Save comparison sessions
   - User accounts and saved libraries
   - Collaboration features
   - Annotation/notes on references

6. **Performance**:
   - Async processing for large files
   - Progress indicators
   - Caching layer (Redis)
   - Database backend (PostgreSQL)

## 📚 Key Learnings from This Project

1. **RIS Format**: Standardized format for citations, widely used in academia
2. **Fuzzy Matching**: Essential for deduplication across heterogeneous sources
3. **Pandas for Research Data**: Excellent choice for tabular reference data
4. **Flask Template Debugging**: Jinja2 errors can be cryptic - always check syntax carefully
5. **Glassmorphism**: Modern design trend - semi-transparent UI elements
6. **SVG for Diagrams**: Better than canvas for interactive, scalable visualizations

## 👤 Author

**Tom Huynh** (created with ❤️, 2026)

---

**Last Updated**: 2026-02-03  
**Status**: ✅ Fully Functional (Bug Fixed)
**Version**: 1.0.0
