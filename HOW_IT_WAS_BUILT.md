# 📝 How the Document Text Summarizer Was Built

A comprehensive step-by-step guide explaining the development process of this project.

---

## 🎯 Overview

This project is a full-stack document summarization application featuring:
- **Flask backend** for API handling
- **HTML/CSS/JavaScript frontend** for the web interface
- **Python CLI** for command-line usage
- **SQLite database** for storing summaries

---

## 📁 Project Structure

```
text_summarizer/
├── app.py              # Flask API server (main entry point)
├── cli.py              # Command-line interface
├── parsers.py          # Document parsing (PDF, DOCX, TXT)
├── summarizers.py      # Summarization algorithms
├── storage.py          # SQLite database operations
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment configuration
├── static/             # Frontend files
│   ├── index.html      # Web interface
│   ├── style.css       # Styling
│   └── app.js          # Frontend JavaScript
└── README.md           # Project documentation
```

---

## Step 1: Project Planning & Architecture

### Design Decisions
- **Modular Architecture**: Each Python file handles a specific responsibility
- **Separation of Concerns**: Parsing, summarization, storage, and API are independent modules
- **Dual Interface**: Both web UI and CLI for different use cases
- **Offline-First**: Local summarization works without internet/API keys

### File Responsibility

| File | Purpose |
|------|---------|
| `app.py` | Flask server & API endpoints |
| `parsers.py` | Extract text from documents |
| `summarizers.py` | Generate summaries |
| `storage.py` | Database operations |
| `cli.py` | Command-line interface |

---

## Step 2: Document Parsers (`parsers.py`)

Created parsers to extract text from different file formats:

### Supported Formats

| File Type | Library Used | Function |
|-----------|-------------|----------|
| **PDF** | `PyPDF2` | `parse_pdf()` |
| **Word (.docx)** | `python-docx` | `parse_docx()` |
| **Text/Markdown** | Built-in Python | `parse_text_file()` |

### Key Functions

```python
# Auto-detect file type and parse
def detect_and_parse(file_path: str) -> Tuple[str, str]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return parse_pdf(file_path), 'pdf'
    elif ext == '.docx':
        return parse_docx(file_path), 'docx'
    else:
        return parse_text_file(file_path), 'text'

# Parse uploaded files from Flask requests
def parse_uploaded_file(file_storage, filename: str) -> Tuple[str, str]:
    # Saves to temp file, parses, then cleans up
```

### PDF Parsing
- Uses `PyPDF2.PdfReader` to read PDF files
- Iterates through all pages and extracts text
- Combines text from all pages with newlines

### Word Document Parsing
- Uses `python-docx.Document` to read .docx files
- Extracts text from paragraphs
- Also extracts text from tables

---

## Step 3: Summarization Engine (`summarizers.py`)

Implemented two summarization modes:

### 1. LocalSummarizer (Offline - TextRank)

```python
class LocalSummarizer:
    def summarize(self, text: str, length: str = 'medium') -> str:
        # Uses TextRank algorithm from Sumy library
        
    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        # Uses LSA (Latent Semantic Analysis)
```

**Technologies Used:**
- **NLTK** - Natural Language Toolkit for tokenization and stopwords
- **Sumy** - Library implementing TextRank algorithm

**Summary Length Options:**
| Length | Sentences |
|--------|-----------|
| Short | 3 sentences |
| Medium | 5 sentences |
| Long | 8 sentences |

### 2. OnlineSummarizer (Optional - Gemini API)

```python
class OnlineSummarizer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        
    def summarize(self, text: str, length: str = 'medium') -> str:
        # Uses Google Gemini AI for abstractive summarization
```

**Features:**
- AI-powered abstractive summarization
- More natural and cohesive summaries
- Requires Google Gemini API key

### Factory Pattern

```python
def get_summarizer(mode: str = 'local', api_key: Optional[str] = None):
    if mode == 'online':
        return OnlineSummarizer(api_key)
    return LocalSummarizer()
```

---

## Step 4: Storage Layer (`storage.py`)

Built SQLite-based persistence for saving summaries.

### Database Schema

```sql
CREATE TABLE summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    original_text TEXT,
    summary TEXT,
    key_points TEXT,          -- JSON array
    mode TEXT,                -- 'local' or 'online'
    length TEXT,              -- 'short', 'medium', 'long'
    file_type TEXT,           -- 'pdf', 'docx', 'text'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `init_db()` | Creates table if not exists |
| `save_summary()` | Stores a new summary |
| `get_summary(id)` | Retrieves specific summary |
| `list_summaries()` | Lists all summaries (with preview) |
| `delete_summary(id)` | Removes a summary |
| `export_summary(id, format)` | Exports as TXT or JSON |

### Export Formats

**TXT Format:**
```
Document: example.pdf
Date: 2026-01-15 12:00:00
Mode: local | Length: medium

==================================================
SUMMARY
==================================================
[Summary text here]

==================================================
KEY POINTS
==================================================
1. First key point
2. Second key point
```

**JSON Format:**
```json
{
  "id": 1,
  "filename": "example.pdf",
  "summary": "...",
  "key_points": ["point 1", "point 2"],
  "created_at": "2026-01-15 12:00:00"
}
```

---

## Step 5: Flask API Server (`app.py`)

Created RESTful API endpoints for the application.

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves web interface |
| `/api/summarize` | POST | Main summarization endpoint |
| `/api/summaries` | GET | List all saved summaries |
| `/api/summaries/<id>` | GET | Get specific summary |
| `/api/summaries/<id>` | DELETE | Delete a summary |
| `/api/summaries/<id>/export` | GET | Export summary (txt/json) |
| `/api/health` | GET | Health check |

### Summarize Endpoint Flow

```python
@app.route('/api/summarize', methods=['POST'])
def summarize():
    # 1. Get parameters (length, save)
    length = request.args.get('length', 'medium')
    should_save = request.args.get('save', 'false').lower() == 'true'
    
    # 2. Extract text from request
    if request.is_json:
        text = request.get_json().get('text', '')
    elif 'file' in request.files:
        text, file_type = parse_uploaded_file(file, filename)
    
    # 3. Get summarizer and generate summary
    summarizer = get_summarizer('local')
    summary = summarizer.summarize(text, length)
    key_points = summarizer.extract_key_points(text)
    
    # 4. Optionally save to database
    if should_save:
        summary_id = save_summary(...)
    
    # 5. Return JSON response
    return jsonify(result)
```

### Configuration

```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
CORS(app)  # Enable cross-origin requests
```

---

## Step 6: Frontend Development (`static/`)

### HTML Structure (`index.html`)

**Main Components:**
1. **Sidebar** - Shows saved summaries history
2. **Header** - Logo and navigation
3. **Input Section**
   - Tabs: Upload File / Paste Text
   - Dropzone for file upload
   - Textarea for pasting text
   - Summary length selector
   - Summarize button with save checkbox
4. **Results Section**
   - Summary card with copy button
   - Key points list with copy button
   - Export buttons (TXT/JSON)
5. **Loading Overlay** - Shown during processing
6. **Toast Notifications** - For user feedback

### CSS Styling (`style.css`)

**Design Features:**
- Modern Inter font family
- Responsive flexbox layout
- Glassmorphism effects
- Smooth transitions and animations
- Dark theme with accent colors
- Mobile-responsive design

**Key Style Elements:**
```css
/* Card styling with glass effect */
.result-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Dropzone hover effect */
.dropzone:hover {
    border-color: var(--primary-color);
    background: rgba(99, 102, 241, 0.1);
}
```

### JavaScript Logic (`app.js`)

**Core Functionality:**
1. **File Upload Handling**
   - Drag and drop support
   - Click to browse
   - File type validation

2. **API Communication**
   ```javascript
   async function summarize() {
       const formData = new FormData();
       formData.append('file', selectedFile);
       
       const response = await fetch('/api/summarize?length=' + length);
       const data = await response.json();
       displayResults(data);
   }
   ```

3. **UI Updates**
   - Tab switching
   - Results display
   - Loading states

4. **Utility Functions**
   - Copy to clipboard
   - Toast notifications
   - Export downloads

---

## Step 7: Command Line Interface (`cli.py`)

Built a CLI using Python's `argparse` for automation and scripting.

### Commands

```bash
# Summarize a file
python cli.py summarize document.pdf

# Summarize with options
python cli.py summarize document.pdf --length short --output summary.txt

# List saved summaries
python cli.py list

# View a specific summary
python cli.py view <summary_id>

# Export a summary
python cli.py export <summary_id> --format json

# Delete a summary
python cli.py delete <summary_id>
```

### CLI Structure

```python
def main():
    parser = argparse.ArgumentParser(description='Document Summarizer CLI')
    subparsers = parser.add_subparsers(dest='command')
    
    # Summarize command
    summarize_parser = subparsers.add_parser('summarize')
    summarize_parser.add_argument('file', help='Path to document')
    summarize_parser.add_argument('--length', choices=['short', 'medium', 'long'])
    summarize_parser.add_argument('--output', help='Output file path')
    
    # List command
    list_parser = subparsers.add_parser('list')
    
    # Export command
    export_parser = subparsers.add_parser('export')
    export_parser.add_argument('id', type=int)
    export_parser.add_argument('--format', choices=['txt', 'json'])
```

---

## Step 8: Dependencies (`requirements.txt`)

```txt
flask>=3.0.0
flask-cors>=4.0.0
sumy>=0.11.0
nltk>=3.8
PyPDF2>=3.0.0
python-docx>=1.0.0
gunicorn>=21.0.0
google-generativeai>=0.3.0
```

### Dependency Breakdown

| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `flask-cors` | Cross-origin request handling |
| `sumy` | TextRank summarization algorithm |
| `nltk` | Natural language processing |
| `PyPDF2` | PDF parsing |
| `python-docx` | Word document parsing |
| `gunicorn` | Production WSGI server |
| `google-generativeai` | Gemini AI API (optional) |

---

## Step 9: Deployment Configuration

### Render Configuration (`render.yaml`)

```yaml
services:
  - type: web
    name: document-text-summariser
    env: python
    buildCommand: |
      pip install -r requirements.txt && 
      python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
    startCommand: gunicorn app:app
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `PORT` | Server port (auto-set by Render) |
| `GEMINI_API_KEY` | Optional API key for online mode |

---

## 🔄 Application Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      User Input                              │
│            (File Upload or Pasted Text)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      parsers.py                              │
│         (Extract text from PDF, DOCX, or TXT)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    summarizers.py                            │
│              (TextRank Algorithm / Gemini AI)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Summary + Key Points Generated                 │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    Return Response      │     │      storage.py         │
│    (JSON via API)       │     │   (Save to SQLite)      │
└─────────────────────────┘     └─────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Display                          │
│           (Summary Card + Key Points List)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technologies Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Flask | Web framework & API |
| **NLP** | NLTK + Sumy | Text processing & summarization |
| **Document Parsing** | PyPDF2, python-docx | Extract text from files |
| **Database** | SQLite | Persistent storage |
| **Frontend** | HTML5, CSS3, JavaScript | User interface |
| **Deployment** | Render, Gunicorn | Cloud hosting |

---

## 🎓 Key Learnings

1. **Modular Design**: Separating concerns makes code maintainable
2. **Factory Pattern**: Used for creating appropriate summarizer instances
3. **RESTful API**: Clean endpoint design for frontend-backend communication
4. **Progressive Enhancement**: Works offline, enhanced with API
5. **User Experience**: Loading states, toast notifications, smooth animations

---

## 👤 Author

**Maanya Gupta**
- GitHub: [@MaanyaGupta](https://github.com/MaanyaGupta)

---

Made with ❤️ as a learning project in full-stack development
