# 🎓 AI-OSM — AI-Powered On-Screen Marking & Student Answer Sheet Evaluator

> **“AI-OSM is an AI-assisted digital evaluation platform that helps examiners evaluate answer sheets faster and more consistently, automatically identifies unchecked answers and unusual scoring patterns, detects student answer copying, and provides automated rubric scoring — while keeping the final decision with the human examiner.”**

---

## ⚡ Quick Start (1-Command Runner)

To run the complete application (Streamlit Web Interface + OCR Pipeline + Database Seeding):

```bash
python run.py
```

This single command will:
1. Verify and automatically install any missing dependencies (`streamlit`, `PyMuPDF`, `pillow`, `scikit-learn`).
2. Generate benchmark test files (`AIML_Master_Answer_Key.docx` and `AIML_Student_Answer_Sheet.docx`).
3. Launch the **Streamlit Web Application** on `http://localhost:8501`.
4. Automatically open your web browser to `http://localhost:8501`.

---

## 🚀 Live Demo Walkthrough (Streamlit UI)

### Step 1: Open the Application
- Open `http://localhost:8501` in your browser.
- Configure your active Ollama model (e.g., `llama3`, `mistral`, `qwen`, `phi3`) from the sidebar.
- Choose the exam mode: **Full Content / Theory Exam (Descriptive)** or **Objective Exam (MCQ, True/False, Fill-in-the-Blanks, Match Column)**.

### Step 2: Connect IP Camera or Upload Paper
- Navigate to **Tab 0: 📹 IP Camera & Booklet Scan**.
- Enter your mobile IP camera URL (e.g., `http://192.168.1.100:8080/shot.jpg`), RTSP feed, or USB Webcam (`0`).
- Click **"📸 Click Page from Camera"** to capture the page, enhance contrast (+45%), and run **Header Auto-OCR** to automatically extract the student's Roll Number and Name.
- Alternatively, upload student answer sheets directly in PDF, DOCX, PNG, or JPG formats.

### Step 3: Master Key & Marking Scheme
- Switch to **Tab 1: 1️⃣ Student Info & Master Key**.
- Upload a master solution key file (PDF, DOCX, TXT, JSON, or images) or edit the interactive rubric questions, model solutions, and key concepts.

### Step 4: AI Evaluation & Interactive Scoring
- Switch to **Tab 2: 2️⃣ Upload / Capture Student Sheet**.
- Review the extracted student text and click **"🚀 Evaluate Theory Answer Sheet with LLM Engine"**.
- View real-time evaluation with detected concepts highlighted in green (`✓`) and missing concepts highlighted in red (`✗`).

### Step 5: Scorecard & Printable Report Cards
- Switch to **Tab 3: 3️⃣ Scorecard & Report Card**.
- Review the total score, accuracy percentage, grade assigned (A+, A, B, C, D), and visual keyword highlights.
- Download the official printable examination report card in `.docx` / `.txt` format with one click.

### Step 6: Class Batch Analytics & Anti-Plagiarism Matrix
- Switch to **Tab 4: 4️⃣ Class Analytics & Plagiarism Matrix 🏆**.
- Click **"⚡ Run Full Class Batch Evaluation & Plagiarism Check"**.
- View the class leaderboard, topper metrics, question difficulty insights, and the **Class Plagiarism Matrix** that flags copied student answers.
- Export class performance data directly to CSV.

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend UI** | Streamlit Pro (`app.py`) | Interactive multi-tab web application, live camera viewport, leaderboards, and report card generator |
| **Backend REST API** | FastAPI + Uvicorn (`backend/app/main.py`) | Asynchronous REST API endpoints for ingestion, camera testing, and sheet grading |
| **Database & ORM** | SQLAlchemy 2.0 + SQLite / MySQL | Persistent relational models for exams, rubrics, answer sheets, and anomaly flags |
| **Camera Connectivity** | Python `urllib` / OpenCV / HTTP Handler | Connects to network IP cameras (IP Webcam, ESP32-CAM, RTSP, USB webcams) for snapshot capture |
| **OCR & Document Ingestion** | PyMuPDF + python-docx + PyTesseract | Direct vector PDF extraction, Word DOCX parsing, and image OCR |
| **Image Enhancement** | PIL (ImageEnhance) + OpenCV | Contrast boosting (+45%), sharpening, and auto-deskewing for camera photos |
| **AI Evaluation Engine** | Ollama Local LLMs (`llama3`, `mistral`, `qwen`, `phi3`) + Semantic NLP Fallback | Privacy-first local LLM inference, semantic similarity, concept keyword matching, and rubric scoring |
| **Plagiarism Detector** | SequenceMatcher Similarity | Pairwise sequence overlap matrix calculation across class student answers |

---

## 📂 Project Structure

```text
AIOCR/
├── app.py                      # Main Streamlit Web Application (Multi-tab UI & Camera Viewport)
├── run.py                      # One-command unified launcher (runs Streamlit on port 8501)
├── PROJECT_SYNOPSIS.md         # Comprehensive Project Synopsis Document
├── AI_OCR_Knowledge_Transfer_Document.md # Technical Knowledge Transfer (KT) Document
├── AI_OCR_Hackathon_Presentation_Deck.md # Presentation Deck Outline
├── create_aiml_docx.py          # Benchmark AI/ML test paper generator
├── generate_kt_pdf.py          # PDF Knowledge Transfer Document generator
├── generate_presentation_pptx.py # Presentation generator script
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI API endpoints
│   │   ├── database.py         # MySQL connection & SQLite fallback
│   │   ├── models.py           # SQLAlchemy relational models
│   │   ├── schemas.py          # Pydantic validation schemas
│   │   ├── ocr_service.py      # Tesseract, PyMuPDF, DOCX & Plagiarism engine
│   │   ├── ai_evaluator.py     # Concept matching & scoring algorithms
│   │   ├── camera_service.py   # IP Camera connectivity & snapshot capture
│   │   ├── llm_service.py      # Multi-provider LLM evaluation service
│   │   ├── anomaly_service.py  # Discrepancy & speed anomaly checks
│   │   └── seed_data.py        # Demo exam data & sheet images
│   ├── uploads/                # Rendered answer sheet images
│   └── requirements.txt        # Python backend dependencies
└── README.md
```

---

## 🔌 Running the Backend API Server Separately (Optional)

If you wish to run the FastAPI REST backend server independently:

```bash
uvicorn backend.app.main:app --reload --port 8000
```
Swagger API Documentation will be accessible at: `http://localhost:8000/docs`.
