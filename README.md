# 📄 Resume Parser API

An AI-powered Resume Parser built with **FastAPI** and **Groq LLaMA 3** that extracts structured information from **PDF** and **DOCX** resumes into a clean JSON format.

---

## ✨ Features

- 📄 Upload PDF and DOCX resume files
- 🤖 AI-powered resume parsing using **Groq LLaMA 3**
- 📊 Structured JSON output with **14 fields**
- ✅ Pydantic schema validation
- 🎨 Modern drag-and-drop web interface
- 📈 Detailed metadata in every response
- 🗑️ Automatic uploaded file cleanup
- 📝 Comprehensive logging
- ⚠️ Robust error handling
- 📚 Interactive Swagger API documentation

---

# 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Core language |
| FastAPI | Web API Framework |
| Groq API | LLM Inference |
| LLaMA 3.3 70B | Resume Parsing |
| Pydantic | Data Validation |
| pdfplumber | PDF Text Extraction |
| python-docx | DOCX Text Extraction |
| Jinja2 | HTML Templates |
| HTML/CSS/JavaScript | Frontend |

---

# 📂 Project Structure

```text
resume_parser/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── resume.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   └── parser.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── file_utils.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── templates/
│   └── index.html
│
├── tests/
│   ├── sample_resumes/
│   └── test_parser.py
│
├── uploads/
│   └── .gitkeep
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🚀 Setup Instructions

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/resume-parser.git
cd resume-parser
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
MAX_FILE_SIZE_MB=5
```

Get your free Groq API key:

> https://console.groq.com

---

## 5. Run the Server

```bash
uvicorn app.main:app --reload
```

---

## 6. Open in Browser

| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:8000 |
| Swagger Docs | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/api/v1/health |

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Frontend UI |
| GET | `/api/v1/health` | Health Check |
| POST | `/api/v1/parse-resume` | Parse Resume |

---

# 📦 Example Response

```json
{
  "status": "success",
  "message": "Resume parsed successfully",
  "metadata": {
    "original_filename": "resume.pdf",
    "file_size_mb": 0.23,
    "word_count": 412,
    "character_count": 2847,
    "model_used": "llama-3.3-70b-versatile",
    "processing_time_seconds": 3.24
  },
  "data": {
    "full_name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+1-555-0101",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/alicejohnson",
    "github": "github.com/alicejohnson",
    "portfolio": "alicejohnson.dev",
    "summary": "Experienced software engineer...",
    "skills": [
      "Python",
      "FastAPI",
      "SQL"
    ],
    "education": [],
    "experience": [],
    "projects": [],
    "certifications": [],
    "languages": []
  }
}
```

---

# 📝 Sample Server Logs

```text
[2024-01-15 10:23:41] INFO  | New parse request — File: 'alice_resume.pdf'
[2024-01-15 10:23:41] DEBUG | Validating uploaded file...
[2024-01-15 10:23:41] DEBUG | File validation passed
[2024-01-15 10:23:41] INFO  | File saved — uploads/a3f8c2d1.pdf
[2024-01-15 10:23:41] INFO  | Starting PDF extraction
[2024-01-15 10:23:41] INFO  | Extraction successful
[2024-01-15 10:23:41] INFO  | Sending request to Groq API...
[2024-01-15 10:23:44] INFO  | Groq API responded in 3.21s
[2024-01-15 10:23:44] INFO  | Validation successful
[2024-01-15 10:23:44] INFO  | Parse complete
[2024-01-15 10:23:44] DEBUG | Uploaded file deleted
```

---

# ✅ Security Best Practices

| Practice | Implementation |
|----------|----------------|
| API keys hidden | `.env` configuration |
| File type validation | PDF & DOCX only |
| File size validation | Maximum 5 MB |
| Safe filenames | UUID-based filenames |
| Automatic cleanup | Delete files after processing |
| Secrets ignored | `.gitignore` excludes `.env` |

---

# ✅ Code Quality

| Practice | Implementation |
|----------|----------------|
| Separation of concerns | Modular architecture |
| Single responsibility | One job per function |
| Type hints | Used throughout |
| Docstrings | Every function documented |
| Logging | Comprehensive logging |
| Standardized errors | Consistent response structure |

---

# ✅ API Design

| Practice | Implementation |
|----------|----------------|
| Versioning | `/api/v1/` |
| Swagger docs | `/docs` |
| Health endpoint | `/health` |
| Response models | Pydantic |
| HTTP status codes | Proper REST conventions |

---

# ✅ Resume Parsing Best Practices

| Practice | Implementation |
|----------|----------------|
| Separate extraction & parsing | Dedicated services |
| Temperature = 0 | Deterministic extraction |
| Pydantic validation | Validate LLM output |
| Optional fields | Safe defaults |
| Hallucination prevention | Strict system prompt |
| OCR detection | Clear error for scanned PDFs |

---

# ⚠️ Common Problems Handled

| Problem | Solution |
|----------|----------|
| Scanned PDF | Return helpful OCR error |
| Old `.doc` file | Reject unsupported format |
| Missing fields | Return `null` or `[]` |
| Large uploads | File size validation |
| LLM downtime | HTTP 503 response |
| Invalid JSON | Pydantic validation |
| Duplicate skills | Prompt normalization |

---

# ⚠️ Limitations

- OCR is **not supported** (image/scanned PDFs)
- `.doc` files are **not supported**
- Internet connection required
- Groq free tier has request limits

---

# 🧪 Running Tests

```bash
python tests/test_parser.py
```

---

# ▶️ Quick Start

```bash
# Activate virtual environment

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Start server
uvicorn app.main:app --reload

# Run tests
python tests/test_parser.py
```

---

# 📌 Future Improvements

- OCR support for scanned resumes
- Batch resume parsing
- Multiple LLM provider support
- Docker deployment
- Authentication & rate limiting
- Resume scoring
- ATS compatibility analysis
- Export parsed data to CSV & Excel

---

# 📄 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

Built with ❤️ using **FastAPI**, **Groq**, and **LLaMA 3**.