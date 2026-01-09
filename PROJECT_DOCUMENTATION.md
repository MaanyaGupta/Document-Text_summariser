# Document Summarizer - Project Documentation

## 📋 Overview

**Document Summarizer** is a web application that extracts key information from documents using natural language processing (NLP) techniques. It supports PDF, Word documents (.docx), and plain text files, generating concise summaries and extracting key points.

---

## 🏗️ Project Architecture

```
text_summarizer/
├── app.py              # Flask web application (main entry point)
├── parsers.py          # Document parsing module (PDF, DOCX, TXT)
├── summarizers.py      # Summarization engine (TextRank algorithm)
├── storage.py          # SQLite database for saving summaries
├── cli.py              # Command-line interface
├── requirements.txt    # Python dependencies
├── summaries.db        # SQLite database file (auto-created)
└── static/
    ├── index.html      # Web interface
    ├── style.css       # Modern dark theme styling
    └── app.js          # Frontend JavaScript logic
```

---

## 🛠️ Technologies Used

### Backend
| Technology | Purpose |
|------------|---------|
| **Flask** | Lightweight Python web framework for the REST API |
| **Flask-CORS** | Enable Cross-Origin Resource Sharing |
| **SQLite** | Lightweight database for persisting summaries |
| **NLTK** | Natural Language Toolkit for text processing |
| **Sumy** | Library implementing TextRank summarization algorithm |
| **PyPDF2** | PDF document parsing |
| **python-docx** | Microsoft Word document parsing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5** | Page structure and semantics |
| **CSS3** | Modern styling with CSS variables, glassmorphism effects |
| **Vanilla JavaScript** | Interactive UI without external frameworks |
| **Google Fonts (Inter)** | Modern typography |

---

## 📁 Module Breakdown

### 1. `app.py` - Flask Web Application

The main application entry point that:
- Serves the web interface at `/`
- Provides REST API endpoints:
  - `POST /api/summarize` - Summarize text or uploaded file
  - `GET /api/summaries` - List saved summaries
  - `GET /api/summaries/<id>` - Get specific summary
  - `DELETE /api/summaries/<id>` - Delete a summary
  - `GET /api/summaries/<id>/export` - Export summary as TXT/JSON
  - `GET /api/health` - Health check endpoint

```python
# Key configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
app.run(debug=True, port=5000)
```

---

### 2. `parsers.py` - Document Parsing

Handles extraction of text from different document formats:

| Function | Description |
|----------|-------------|
| `parse_text()` | Parse plain text content |
| `parse_pdf()` | Extract text from PDF using PyPDF2 |
| `parse_docx()` | Extract text from Word documents (paragraphs + tables) |
| `parse_uploaded_file()` | Handle Flask file uploads with temp file management |

**How it works:**
1. Uploaded file is saved to a temporary location
2. File extension determines parsing method
3. Text is extracted and returned
4. Temporary file is cleaned up

---

### 3. `summarizers.py` - Text Summarization

Uses **extractive summarization** with the TextRank algorithm:

#### LocalSummarizer Class
- **TextRank Algorithm**: Graph-based ranking to identify important sentences
- **LSA (Latent Semantic Analysis)**: For key point extraction
- **Lazy Initialization**: NLTK data downloaded only when needed

```python
# Summary length configuration
sentence_counts = {
    'short': 3,    # 3 key sentences
    'medium': 5,   # 5 key sentences  
    'long': 8      # 8 key sentences
}
```

**How TextRank works:**
1. Split text into sentences
2. Build a similarity graph between sentences
3. Apply PageRank algorithm to rank sentences
4. Select top N sentences for the summary

---

### 4. `storage.py` - Data Persistence

SQLite-based storage for saving and retrieving summaries:

| Function | Description |
|----------|-------------|
| `save_summary()` | Store summary with metadata |
| `get_summary()` | Retrieve by ID |
| `list_summaries()` | Get all saved summaries (with preview) |
| `delete_summary()` | Remove a summary |
| `export_summary()` | Format as TXT or JSON |

**Database Schema:**
```sql
CREATE TABLE summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    original_text TEXT,
    summary TEXT,
    key_points TEXT,      -- JSON array
    mode TEXT,
    length TEXT,
    file_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

### 5. Frontend (`static/` folder)

#### `index.html`
- Responsive layout with sidebar for history
- Tab-based input (Upload File / Paste Text)
- Summary length selector (Short/Medium/Long)
- Results display with copy/export options

#### `style.css`
- **CSS Variables**: Centralized theme configuration
- **Dark Theme**: Modern dark color palette
- **Glassmorphism**: Frosted glass effects with `backdrop-filter`
- **Animations**: Smooth transitions and loading spinner
- **Responsive Design**: Mobile-friendly layout

#### `app.js`
- State management for file/text input and options
- Drag-and-drop file handling
- Fetch API calls to backend
- Dynamic results rendering
- Toast notifications for user feedback

---

## 🚀 How to Run

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

```bash
# 1. Navigate to project directory
cd text_summarizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py
```

### Access
Open your browser and navigate to: **http://localhost:5000**

---

## 📦 Dependencies

```
flask>=3.0.0
flask-cors>=4.0.0
PyPDF2>=3.0.0
python-docx>=1.0.0
nltk>=3.8.0
sumy>=0.11.0
click>=8.1.0
```

---

## 🔧 API Reference

### Summarize Document
```http
POST /api/summarize?length=medium&save=true
Content-Type: multipart/form-data

file: <uploaded_file>
```

**Response:**
```json
{
    "summary": "Extracted summary text...",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "filename": "document.pdf",
    "file_type": "pdf",
    "original_length": 5000,
    "summary_length": 500,
    "saved_id": 1
}
```

### Summarize Text
```http
POST /api/summarize?length=short
Content-Type: application/json

{
    "text": "Your text to summarize...",
    "filename": "pasted_text"
}
```

---

## 🎨 UI Features

1. **Drag & Drop Upload**: Drop PDF, DOCX, or TXT files directly
2. **Text Pasting**: Paste content directly for quick summarization
3. **Summary Length Control**: Short (3 sentences), Medium (5), Long (8)
4. **History Sidebar**: View and manage saved summaries
5. **Export Options**: Download as TXT or JSON
6. **Copy to Clipboard**: One-click copy for summary and key points
7. **Responsive Design**: Works on desktop and mobile devices

---

## 📄 License

This project is open source and available for educational and personal use.

---

## 👤 Author

Created with the assistance of AI pair programming.
