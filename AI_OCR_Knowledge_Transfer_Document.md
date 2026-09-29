# 📘 AI-OSM & Student Answer Sheet Evaluator — Knowledge Transfer (KT) Document

**Document Version:** 2.0 Pro  
**Date:** September 2026  
**Status:** Complete & Operational  
**Project:** `AIOCR`  
**PDF Document:** [`AI_OCR_Knowledge_Transfer_Document.pdf`](./AI_OCR_Knowledge_Transfer_Document.pdf)

---

## 1. Executive Summary

The **AI-OSM Student Answer Sheet Evaluator** is an automated answer paper grading, IP camera snapshot capture, multi-format master key parsing, and class analytics platform. The system bridges physical paper examination booklets and digital AI evaluation by providing:

- 📹 **IP Camera Connectivity & 1-Click Snapshot Capture**: Connects to HTTP snapshot URLs (e.g. *IP Webcam app*, *ESP32-CAM*), RTSP camera streams, and USB webcams.
- 🔑 **Multi-Format Master Key Importer**: Parses solution keys from PDF (`.pdf`), Word (`.docx`, `.doc`), Plain Text (`.txt`), Written Notes, JSON (`.json`), or Images (`.png`, `.jpg`).
- 🔍 **Smart Header Auto-OCR**: Automatically extracts Roll Numbers and Candidate Names directly from page headers using OCR regex pattern matching.
- 📐 **Camera Auto-Deskew & Contrast Enhancer**: Auto-boosts image contrast (+45%) and sharpens camera photos for maximum OCR accuracy.
- 📚 **Multi-Page Booklet Continuous Scanner**: Allows sequential scanning of Page 1, Page 2, Page 3 to combine multi-page student answer booklets.
- 🕵️‍♂️ **Class Plagiarism & Copying Detector Matrix**: Performs pairwise text sequence matching across the class batch to flag copied/identical answers (`HIGH SIMILARITY 🔴`).
- 📜 **Official Printable & Downloadable Report Cards**: Generates printable scorecards with matched concept highlights (`<mark style='background:#BBF7D0'>`) and downloadable `.docx` / `.txt` reports.

---

## 2. Technology Stack & Component Overview

| Layer / Component | Technology | Primary Function & Responsibility |
|---|---|---|
| **Main Web App** | Streamlit Pro (`app.py`) | Interactive multi-tab web portal, live camera viewport, leaderboards, report card generator |
| **REST Backend API** | FastAPI + Uvicorn (`backend/app/main.py`) | Async REST API endpoints, image uploading, static file serving (`/uploads/`) |
| **Database Engine** | SQLAlchemy + SQLite / MySQL (`models.py`) | Persistent database models for User roles, Exams, Answer Sheets, Evaluations, and Anomaly Flags |
| **Camera Connectivity** | `CameraService` (`camera_service.py`) | HTTP snapshot request handler, RTSP stream connector, WebCam reader, and simulated camera generator |
| **OCR & Doc Parser** | `OCRService` (`ocr_service.py`) | PyMuPDF (PDF direct), python-docx + XML parser (Word), PyTesseract (Images), Header OCR |
| **Image Enhancement** | PIL (ImageEnhance) + OpenCV | Contrast boosting, text sharpening, auto-deskewing for camera photos |
| **AI Evaluation Engine** | `AIEvaluator` (`ai_evaluator.py`) | Concept keyword matching, partial mark allocation, grade determination, feedback generation |
| **Plagiarism Detector** | SequenceMatcher Similarity | Pairwise sequence overlap matrix calculation across class student answers |

---

## 3. Directory Structure

```
AIOCR/
├── app.py                      # Main Streamlit Web Application (Multi-tab UI & Camera Viewport)
├── run.py                      # One-click app launcher script (starts Streamlit on http://localhost:8501)
├── generate_kt_pdf.py          # PDF Knowledge Transfer Document generator script
├── AI_OCR_Knowledge_Transfer_Document.pdf # Output Executive KT PDF Document
├── AI_OCR_Knowledge_Transfer_Document.md  # Output Markdown KT Document
├── backend/
│   ├── requirements.txt        # Python backend dependencies
│   ├── uploads/                # Static storage for uploaded & captured answer sheet photos
│   └── app/
│       ├── main.py             # FastAPI backend API entrypoint & endpoints
│       ├── camera_service.py   # IP Camera connectivity, snapshot capture, & simulated streams
│       ├── ocr_service.py      # Image OCR, PDF parser, DOCX parser, Header OCR, Plagiarism matrix
│       ├── ai_evaluator.py     # AI evaluation logic, concept keyword matching, grade assignment
│       ├── anomaly_service.py  # Anomaly detection & moderation rule engine
│       ├── database.py         # SQLAlchemy database connection setup
│       ├── models.py           # Database models (User, Exam, AnswerSheet, QuestionEvaluation, etc.)
│       ├── schemas.py          # Pydantic request/response schemas
│       └── seed_data.py        # Demo seed data generator
```

---

## 4. System Workflows

```mermaid
flowchart TD
    A[Input Answer Sheet] --> B{Input Source}
    B -->|IP Camera / WebCam| C[CameraService.capture_snapshot]
    B -->|Upload File| D[Upload PDF / DOCX / Image]
    B -->|Written Text| E[Type / Paste Text]
    
    C --> F[OCRService.enhance_image_for_ocr]
    D --> F
    F --> G[OCRService.extract_from_image / docx / pdf]
    
    G --> H[OCRService.parse_student_header]
    H --> I[Auto-Detect Student Roll No & Name]
    
    G --> J[AIEvaluator.evaluate_answer]
    J --> K[Match Key Concepts & Assign Marks]
    K --> L[Generate Scorecard with Keyword Highlights]
    
    G --> M[OCRService.compute_plagiarism_similarity_matrix]
    M --> N[Class Plagiarism Matrix & Leaderboard]
```

---

## 5. REST API Endpoint Registry

| Method | Endpoint | Payload / Params | Description |
|---|---|---|---|
| `GET` | `/` | None | API Health Check & Database Info |
| `POST` | `/api/auth/login` | `JSON: {email, role}` | Authenticate user & return role profile |
| `GET` | `/api/sheets` | `Query: ?status=&examiner_id=` | List all answer sheets with scores & status |
| `GET` | `/api/sheets/{id}` | `Path: sheet_id` | Get detailed sheet evaluations & OCR text |
| `POST` | `/api/sheets/upload` | `Form: student_roll, name, file` | Upload sheet file & run auto-grading |
| `POST` | `/api/ocr/extract` | `Form: file (Image/PDF/DOCX)` | Extract text from uploaded document |
| `POST` | `/api/camera/test` | `Form: camera_ip` | Test IP camera connectivity status |
| `POST` | `/api/camera/capture` | `Form: camera_ip, student_roll` | Snap photo from IP camera & run OCR |
| `POST` | `/api/master-key/upload` | `Form: file (PDF/DOCX/TXT)` | Parse master answer key into questions |
| `POST` | `/api/sheets/{id}/evaluate/{q_id}` | `JSON: {examiner_marks, comments}` | Update examiner marks & AI acceptance |
| `POST` | `/api/sheets/{id}/submit` | `JSON: {time_spent_seconds}` | Finalize sheet grading & run anomaly rules |
| `GET` | `/api/moderation/cases` | None | List flagged anomaly cases for moderator |
| `POST` | `/api/moderation/{id}/resolve` | `JSON: {notes, final_score}` | Resolve anomaly case & set final score |
| `GET` | `/api/analytics/examiner` | `Query: ?examiner_id=` | Examiner performance & grade distribution |

---

## 6. How to Run & Maintain

### 6.1 Setup & Installation
```bash
# 1. Install Dependencies
pip install streamlit PyMuPDF python-docx pillow scikit-learn pytesseract fastapi uvicorn sqlalchemy

# 2. Launch Main Web App
python run.py
# App URL: http://localhost:8501

# 3. Launch Backend API Server (Optional)
uvicorn backend.app.main:app --reload --port 8000
# Swagger API Docs: http://localhost:8000/docs
```

### 6.2 IP Camera Setup Instructions
- **IP Webcam App (Mobile)**: Enter IP `http://192.168.1.100:8080/shot.jpg` in camera field.
- **ESP32-CAM**: Enter IP `http://192.168.4.1/capture`.
- **RTSP Security Camera**: Enter URL `rtsp://admin:pass@192.168.1.50:554/live`.
- **USB WebCam**: Enter index `0`.

---

*Document approved by Lead AI Systems Architect & System Engineering Team.*
