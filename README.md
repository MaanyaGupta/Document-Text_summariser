# 📝 Document Text Summarizer

A powerful document summarization tool with a beautiful web interface and CLI support. Summarize text, PDFs, and Word documents instantly using advanced NLP techniques.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 📄 **Multi-Format Support** - Text, PDF (.pdf), and Word (.docx) documents
- 🧠 **Smart Summarization** - Local (offline) summarization using TextRank algorithm
- 📌 **Key Points Extraction** - Automatically extract important key points
- 📏 **Adjustable Length** - Short, medium, or long summary options
- 💾 **Save & Manage** - Save summaries for later reference
- 📤 **Export Options** - Export summaries as TXT or JSON
- 🌐 **Beautiful Web UI** - Modern, responsive web interface
- ⌨️ **CLI Support** - Command-line interface for automation

## 🚀 Live Demo

🔗 **[Try it on Render](https://document-text-summariser.onrender.com)** *(Update with your actual URL)*

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/MaanyaGupta/text_summarizer.git
   cd text_summarizer
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:5000`

## 🖥️ Usage

### Web Interface

1. Open the web app in your browser
2. Either **paste text** directly or **upload a file** (PDF, DOCX, or TXT)
3. Select your preferred summary length (Short, Medium, Long)
4. Click **Summarize** to generate the summary
5. Optionally save or export the summary

### Command Line Interface

```bash
# Summarize a text file
python cli.py summarize document.txt

# Summarize with specific length
python cli.py summarize document.pdf --length short

# Summarize and save to output file
python cli.py summarize document.docx --output summary.txt

# List saved summaries
python cli.py list

# Export a saved summary
python cli.py export <summary_id> --format json
```

## 📁 Project Structure

```
text_summarizer/
├── app.py              # Flask API server
├── cli.py              # Command-line interface
├── parsers.py          # Document parsing (PDF, DOCX, TXT)
├── summarizers.py      # Summarization algorithms
├── storage.py          # SQLite database operations
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── static/
│   ├── index.html      # Web interface
│   ├── style.css       # Styles
│   └── app.js          # Frontend JavaScript
└── README.md
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve web interface |
| `/api/summarize` | POST | Summarize text or file |
| `/api/summaries` | GET | List all saved summaries |
| `/api/summaries/<id>` | GET | Get specific summary |
| `/api/summaries/<id>` | DELETE | Delete a summary |
| `/api/summaries/<id>/export` | GET | Export summary (txt/json) |
| `/api/health` | GET | Health check |

### Example API Usage

```bash
# Summarize text
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here..."}'

# Summarize with options
curl -X POST "http://localhost:5000/api/summarize?length=short&save=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here..."}'
```

## 🛠️ Technologies Used

- **Backend**: Flask, Python
- **NLP**: NLTK, Sumy (TextRank)
- **Document Parsing**: PyPDF2, python-docx
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Render, Gunicorn

## 🌐 Deployment

### Deploy to Render

1. Push your code to GitHub
2. Create a new Web Service on [Render](https://render.com)
3. Connect your repository
4. Set the following:
   - **Build Command**: `pip install -r requirements.txt && python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"`
   - **Start Command**: `gunicorn app:app`
5. Deploy!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Maanya Gupta**

- GitHub: [@MaanyaGupta](https://github.com/MaanyaGupta)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/MaanyaGupta/text_summarizer/issues).

## ⭐ Show Your Support

Give a ⭐ if this project helped you!

---

Made with ❤️ by Maanya Gupta
