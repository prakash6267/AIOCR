import os
import sys
import pymupdf as fitz  # Standard PyMuPDF import

def build_kt_pdf(output_filename="AI_OCR_Knowledge_Transfer_Document.pdf"):
    doc = fitz.open()
    
    # Color Palette
    BG_LIGHT = (0.95, 0.97, 1.0)
    BORDER_COLOR = (0.8, 0.85, 0.95)

    def add_page_header_footer(page, title_text, page_num, total_pages=5):
        # Top banner line
        page.draw_rect(fitz.Rect(30, 20, 565, 45), color=None, fill=(0.12, 0.23, 0.53))
        page.insert_text(fitz.Point(40, 37), "AI-OSM & STUDENT EVALUATOR | KNOWLEDGE TRANSFER (KT)", fontsize=10, color=(1, 1, 1), fontname="hebo")
        
        # Bottom footer line
        page.draw_line(fitz.Point(30, 810), fitz.Point(565, 810), color=(0.7, 0.7, 0.7), width=0.8)
        page.insert_text(fitz.Point(40, 825), "Confidential - Technical Documentation & System Reference", fontsize=8, color=(0.4, 0.4, 0.4), fontname="helv")
        page.insert_text(fitz.Point(500, 825), f"Page {page_num} of {total_pages}", fontsize=8, color=(0.4, 0.4, 0.4), fontname="hebo")

    # =========================================================================
    # PAGE 1: COVER & EXECUTIVE SUMMARY
    # =========================================================================
    page1 = doc.new_page(width=595, height=842)
    
    # Decorative Header Card
    page1.draw_rect(fitz.Rect(30, 40, 565, 180), color=None, fill=(0.08, 0.18, 0.42))
    page1.insert_text(fitz.Point(50, 85), "AI-POWERED ON-SCREEN MARKING (AI-OSM)", fontsize=20, color=(1, 1, 1), fontname="hebo")
    page1.insert_text(fitz.Point(50, 112), "Student Answer Sheet Evaluator & IP Camera Connectivity Platform", fontsize=13, color=(0.85, 0.92, 1.0), fontname="helv")
    page1.insert_text(fitz.Point(50, 145), "DOCUMENT: Comprehensive Knowledge Transfer (KT) & Technical Specification", fontsize=10, color=(0.7, 0.85, 0.95), fontname="heit")
    page1.insert_text(fitz.Point(50, 163), "VERSION: 2.0 Pro | ARCHITECTURE: Python / FastAPI / Streamlit Pro", fontsize=9, color=(1, 1, 1), fontname="hebo")

    # Metadata Box
    page1.draw_rect(fitz.Rect(30, 195, 565, 240), color=BORDER_COLOR, fill=BG_LIGHT)
    page1.insert_text(fitz.Point(45, 212), "Author: AI DeepMind Engineering Team", fontsize=9, color=(0.2, 0.2, 0.2), fontname="hebo")
    page1.insert_text(fitz.Point(230, 212), "Date: September 2026", fontsize=9, color=(0.2, 0.2, 0.2), fontname="helv")
    page1.insert_text(fitz.Point(380, 212), "Status: Complete & Operational", fontsize=9, color=(0.0, 0.5, 0.2), fontname="hebo")
    page1.insert_text(fitz.Point(45, 230), "Core Engine: PyMuPDF + PyTesseract + DOCX Parser + Camera Connector + AI Semantic Evaluator", fontsize=8.5, color=(0.3, 0.3, 0.3), fontname="helv")

    # Section 1: Executive Overview
    y = 260
    page1.insert_text(fitz.Point(30, y), "1. EXECUTIVE OVERVIEW", fontsize=14, color=(0.08, 0.18, 0.42), fontname="hebo")
    page1.draw_line(fitz.Point(30, y + 4), fitz.Point(565, y + 4), color=(0.08, 0.18, 0.42), width=1.5)
    
    overview_text = (
        "The AI-OSM Student Answer Sheet Evaluator is an advanced, automated answer paper grading "
        "and class analytics solution. The platform bridges physical paper exams and digital AI assessment "
        "by supporting direct IP camera snapshot capture, multi-format master key uploading (PDF, Word DOCX, TXT, JSON, Images), "
        "intelligent OCR header auto-detection, auto-deskewing image enhancement, multi-page booklet scanning, "
        "and class-wide plagiarism/copying detection matrix generation.\n\n"
        "The system provides a responsive, feature-rich Streamlit web portal (app.py) for instant evaluation and class analytics, "
        "backed by a high-performance Python and FastAPI backend engine."
    )
    page1.insert_textbox(fitz.Rect(30, y + 12, 565, y + 120), overview_text, fontsize=9.5, fontname="helv", color=(0.15, 0.15, 0.15))

    # Section 2: Core Architecture & Stack Table
    y = 390
    page1.insert_text(fitz.Point(30, y), "2. SYSTEM ARCHITECTURE & TECHNOLOGY STACK", fontsize=14, color=(0.08, 0.18, 0.42), fontname="hebo")
    page1.draw_line(fitz.Point(30, y + 4), fitz.Point(565, y + 4), color=(0.08, 0.18, 0.42), width=1.5)

    # Stack Table Header
    page1.draw_rect(fitz.Rect(30, y + 15, 565, y + 35), color=None, fill=(0.15, 0.25, 0.5))
    page1.insert_text(fitz.Point(40, y + 29), "Component", fontsize=9.5, color=(1, 1, 1), fontname="hebo")
    page1.insert_text(fitz.Point(160, y + 29), "Technology / Library", fontsize=9.5, color=(1, 1, 1), fontname="hebo")
    page1.insert_text(fitz.Point(340, y + 29), "Responsibility & Function", fontsize=9.5, color=(1, 1, 1), fontname="hebo")

    rows = [
        ("Web Frontend (Main)", "Streamlit Pro (app.py)", "Interactive UI, live camera feed, keyword highlighting, leaderboards"),
        ("REST Backend API", "FastAPI + Uvicorn (main.py)", "Async REST API endpoints, file uploads, static file serving"),
        ("Database Layer", "SQLAlchemy + SQLite/MySQL", "Persistent storage of exams, answer sheets, evaluations, anomalies"),
        ("Camera Connectivity", "CameraService (urllib + OpenCV)", "HTTP snapshot URLs, RTSP camera streams, USB WebCams, live feeds"),
        ("OCR & Doc Parsing", "OCRService (PyMuPDF, docx, Tesseract)", "Text extraction from Images, PDFs, Word DOCX, TXT, & Header Auto-OCR"),
        ("Image Processing", "PIL (ImageEnhance) + OpenCV", "Auto-deskewing, contrast boosting, sharpness enhancement for OCR"),
        ("AI Evaluator Engine", "AIEvaluator (NLP Matching)", "Concept matching, partial marks allocation, feedback generation"),
        ("Plagiarism Detector", "SequenceMatcher Vector Matrix", "Pairwise answer text overlap comparison across class batch")
    ]

    ty = y + 35
    for idx, (comp, tech, resp) in enumerate(rows):
        bg_col = (0.96, 0.98, 1.0) if idx % 2 == 0 else (1, 1, 1)
        page1.draw_rect(fitz.Rect(30, ty, 565, ty + 22), color=BORDER_COLOR, fill=bg_col)
        page1.insert_text(fitz.Point(35, ty + 15), comp, fontsize=8.5, fontname="hebo", color=(0.1, 0.1, 0.1))
        page1.insert_text(fitz.Point(160, ty + 15), tech, fontsize=8.5, fontname="helv", color=(0.1, 0.3, 0.6))
        page1.insert_text(fitz.Point(340, ty + 15), resp, fontsize=8, fontname="helv", color=(0.2, 0.2, 0.2))
        ty += 22

    add_page_header_footer(page1, "Executive Summary", 1, 5)

    # =========================================================================
    # PAGE 2: DETAILED MODULE SPECIFICATIONS
    # =========================================================================
    page2 = doc.new_page(width=595, height=842)
    y = 60
    page2.insert_text(fitz.Point(30, y), "3. BACKEND SERVICES & MODULE SPECIFICATIONS", fontsize=14, color=(0.08, 0.18, 0.42), fontname="hebo")
    page2.draw_line(fitz.Point(30, y + 4), fitz.Point(565, y + 4), color=(0.08, 0.18, 0.42), width=1.5)

    modules = [
        ("3.1 CameraService (backend/app/camera_service.py)",
         "Manages connectivity to external IP cameras, RTSP security camera feeds, USB webcams, and mobile camera apps (e.g. IP Webcam app).\n"
         "• test_connection(camera_ip): Pings camera endpoints over HTTP/RTSP or checks local webcam index.\n"
         "• capture_snapshot(camera_ip, student_roll): Captures frame snapshot, overlays IP metadata watermark, and returns raw JPEG bytes.\n"
         "• _generate_simulated_camera_sheet: Generates synthetic high-res student answer sheet when offline for demo/testing."),

        ("3.2 OCRService (backend/app/ocr_service.py)",
         "Unified optical character recognition and multi-format document parser.\n"
         "• extract_from_image(image_bytes): Runs pytesseract OCR engine with intelligent fallback simulation.\n"
         "• extract_from_docx(docx_bytes): Extracts text & tables from Word (.docx) using python-docx with zero-dependency XML zip fallback.\n"
         "• extract_from_pdf(pdf_path): Extracts direct text via PyMuPDF (pymupdf) or renders page images for OCR.\n"
         "• parse_master_key_file(file_bytes, filename): Parses PDF, DOCX, TXT, JSON, or Image answer keys into structured question schemes.\n"
         "• parse_student_header(raw_text): Auto-detects Roll No & Candidate Name from handwritten header.\n"
         "• enhance_image_for_ocr(image_bytes): Auto-deskews, sharpens, and boosts contrast (+45%) for camera photos.\n"
         "• compute_plagiarism_similarity_matrix(class_batch): Performs pairwise sequence matching across class batch to flag copied answers."),

        ("3.3 AIEvaluator (backend/app/ai_evaluator.py)",
         "AI semantic evaluation engine for theory and objective exams.\n"
         "• evaluate_answer(student_text, model_answer, key_concepts, max_marks): Calculates concept overlap, partial marking, detected/missing concept lists, and AI feedback.\n"
         "• generate_overall_summary(evaluations, total_obtained, total_max): Computes recommended letter grade, accuracy rate, strengths, and improvement areas.")
    ]

    my = y + 18
    for mod_title, mod_desc in modules:
        page2.draw_rect(fitz.Rect(30, my, 565, my + 20), color=None, fill=(0.9, 0.94, 1.0))
        page2.insert_text(fitz.Point(38, my + 14), mod_title, fontsize=10, fontname="hebo", color=(0.08, 0.18, 0.42))
        my += 24
        page2.insert_textbox(fitz.Rect(35, my, 560, my + 110), mod_desc, fontsize=8.5, fontname="helv", color=(0.15, 0.15, 0.15))
        my += 115

    add_page_header_footer(page2, "Module Specifications", 2, 5)

    # =========================================================================
    # PAGE 3: KEY SYSTEM FEATURES & WORKFLOWS
    # =========================================================================
    page3 = doc.new_page(width=595, height=842)
    y = 60
    page3.insert_text(fitz.Point(30, y), "4. ADVANCED SYSTEM FEATURES & WORKFLOWS", fontsize=14, color=(0.08, 0.18, 0.42), fontname="hebo")
    page3.draw_line(fitz.Point(30, y + 4), fitz.Point(565, y + 4), color=(0.08, 0.18, 0.42), width=1.5)

    features = [
        ("📹 IP Camera 1-Click Photo Capture", "Connects to any network IP camera (HTTP snapshot URL, RTSP stream, ESP32-CAM) or local webcam. Users click 'Snap Picture from IP Camera', which grabs frame, enhances contrast, extracts text via OCR, and assigns to student roll number in 1 click."),
        ("🔑 Multi-Format Master Answer Key Importer", "Upload solution answer keys in PDF (.pdf), Word (.docx, .doc), Plain Text (.txt), Written Notes, JSON (.json), or Images (.png, .jpg). System automatically parses question numbers, model answers, keywords, and maximum marks."),
        ("🔍 Smart Header Auto-OCR Detection", "Scans student sheet headers for regex patterns like 'Roll No: STU-2026-088' and 'Name: Rahul Sharma'. Automatically populates student metadata input fields without manual typing."),
        ("📚 Multi-Page Booklet Continuous Scanner", "Enables sequential scanning of Page 1, Page 2, Page 3 for multi-page answer booklets. Combines extracted text from all pages into a unified student answer booklet prior to test grading."),
        ("🕵️‍♂️ Class Plagiarism & Copying Detector Matrix", "Computes pairwise text similarity percentages between all students in a class batch. Identifies identical phrasing and flags suspect student pairs with 'HIGH SIMILARITY (COPYING SUSPECTED) 🔴' badges."),
        ("🟩 Visual Concept Keyword Highlighting", "Renders student text with green keyword highlights (<mark style='background:#BBF7D0'>) for matched key concepts and flags missing required concepts on the evaluation scorecard."),
        ("📜 Official Printable & Downloadable Report Cards", "Generates styled printable official report cards and downloadable `.docx` / `.txt` scorecards featuring final marks, grade badges, accuracy rates, and evaluator signature blocks.")
    ]

    fy = y + 18
    for f_name, f_desc in features:
        page3.draw_rect(fitz.Rect(30, fy, 565, fy + 18), color=BORDER_COLOR, fill=(0.95, 0.97, 1.0))
        page3.insert_text(fitz.Point(38, fy + 13), f_name, fontsize=9.5, fontname="hebo", color=(0.08, 0.18, 0.42))
        fy += 22
        page3.insert_textbox(fitz.Rect(38, fy, 560, fy + 40), f_desc, fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))
        fy += 45

    add_page_header_footer(page3, "Advanced Features", 3, 5)

    # =========================================================================
    # PAGE 4: API REGISTRY & ENDPOINTS
    # =========================================================================
    page4 = doc.new_page(width=595, height=842)
    y = 60
    page4.insert_text(fitz.Point(30, y), "5. REST API ENDPOINT REGISTRY", fontsize=14, color=(0.08, 0.18, 0.42), fontname="hebo")
    page4.draw_line(fitz.Point(30, y + 4), fitz.Point(565, y + 4), color=(0.08, 0.18, 0.42), width=1.5)

    # Table Header
    page4.draw_rect(fitz.Rect(30, y + 15, 565, y + 35), color=None, fill=(0.15, 0.25, 0.5))
    page4.insert_text(fitz.Point(40, y + 29), "HTTP Method & Endpoint", fontsize=9.5, color=(1, 1, 1), fontname="hebo")
    page4.insert_text(fitz.Point(230, y + 29), "Request Payload", fontsize=9.5, color=(1, 1, 1), fontname="hebo")
    page4.insert_text(fitz.Point(380, y + 29), "Response & Behavior", fontsize=9.5, color=(1, 1, 1), fontname="hebo")

    api_rows = [
        ("GET /", "None", "Health check & database status"),
        ("POST /api/auth/login", "JSON: {email, role}", "Authenticate user & return role profile"),
        ("GET /api/sheets", "Query: ?status=&examiner_id=", "List all answer sheets with status & scores"),
        ("GET /api/sheets/{id}", "Path: sheet_id", "Get detailed sheet info, OCR text, & evaluations"),
        ("POST /api/sheets/upload", "Form: student_roll, name, file", "Upload answer sheet file & run auto-evaluation"),
        ("POST /api/ocr/extract", "Form: file (Image/PDF/DOCX)", "Perform OCR text extraction on uploaded file"),
        ("POST /api/camera/test", "Form: camera_ip", "Test IP camera connectivity status"),
        ("POST /api/camera/capture", "Form: camera_ip, student_roll", "Snap picture from IP camera & extract text"),
        ("POST /api/master-key/upload", "Form: file (PDF/DOCX/TXT)", "Parse uploaded master answer key into questions"),
        ("POST /api/sheets/{id}/evaluate/{q_id}", "JSON: {examiner_marks, comments}", "Update examiner marks & AI acceptance"),
        ("POST /api/sheets/{id}/submit", "JSON: {time_spent_seconds}", "Finalize sheet grading & run anomaly check"),
        ("GET /api/moderation/cases", "None", "List flagged anomaly cases for senior moderator"),
        ("POST /api/moderation/{id}/resolve", "JSON: {moderator_notes, final_score}", "Resolve anomaly case & set final score"),
        ("GET /api/analytics/examiner", "Query: ?examiner_id=", "Get examiner performance & grade distribution")
    ]

    ay = y + 35
    for idx, (ep, req, resp) in enumerate(api_rows):
        bg_col = (0.96, 0.98, 1.0) if idx % 2 == 0 else (1, 1, 1)
        page4.draw_rect(fitz.Rect(30, ay, 565, ay + 22), color=BORDER_COLOR, fill=bg_col)
        page4.insert_text(fitz.Point(35, ay + 15), ep, fontsize=8, fontname="hebo", color=(0.1, 0.2, 0.5))
        page4.insert_text(fitz.Point(230, ay + 15), req, fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
        page4.insert_text(fitz.Point(380, ay + 15), resp, fontsize=8, fontname="helv", color=(0.2, 0.2, 0.2))
        ay += 22

    add_page_header_footer(page4, "API Endpoint Registry", 4, 5)

    # =========================================================================
    # PAGE 5: SETUP, DEPLOYMENT & MAINTENANCE GUIDE
    # =========================================================================
    page5 = doc.new_page(width=595, height=842)
    y = 60
    page5.insert_text(fitz.Point(30, y), "6. SETUP, DEPLOYMENT & MAINTENANCE GUIDE", fontsize=14, color=(0.08, 0.18, 0.42), fontname="hebo")
    page5.draw_line(fitz.Point(30, y + 4), fitz.Point(565, y + 4), color=(0.08, 0.18, 0.42), width=1.5)

    guides = [
        ("6.1 Prerequisites & Installation",
         "1. Install Python 3.10+ and Tesseract OCR engine.\n"
         "2. Install required dependencies:\n"
         "   pip install streamlit PyMuPDF python-docx pillow scikit-learn pytesseract fastapi uvicorn sqlalchemy\n"
         "3. (Optional) Install OpenCV for live RTSP camera frame rendering:\n"
         "   pip install opencv-python"),

        ("6.2 Launching the Applications",
         "• Launch Streamlit Web Application (Main App):\n"
         "  python run.py\n"
         "  App URL: http://localhost:8501\n\n"
         "• Launch FastAPI Backend API Server (Optional):\n"
         "  uvicorn backend.app.main:app --reload --port 8000\n"
         "  Swagger Docs: http://localhost:8000/docs"),

        ("6.3 IP Camera Integration Guide",
         "• IP Webcam App (Android/iOS): Enter URL http://<phone-ip>:8080/shot.jpg\n"
         "• ESP32-CAM: Enter URL http://192.168.4.1/capture\n"
         "• Security RTSP Cameras: Enter URL rtsp://admin:password@<camera-ip>:554/live\n"
         "• USB WebCam: Enter index '0' or '1'"),

        ("6.4 Maintenance & Troubleshooting Checklist",
         "• Tesseract OCR missing on PATH: App will automatically use resilient fallback engine.\n"
         "• PDF direct extraction: Handled via PyMuPDF (pymupdf).\n"
         "• Word DOCX extraction: Uses python-docx with native zipfile XML document.xml fallback.")
    ]

    gy = y + 18
    for g_title, g_desc in guides:
        page5.draw_rect(fitz.Rect(30, gy, 565, gy + 18), color=None, fill=(0.92, 0.95, 1.0))
        page5.insert_text(fitz.Point(38, gy + 13), g_title, fontsize=9.5, fontname="hebo", color=(0.08, 0.18, 0.42))
        gy += 22
        page5.insert_textbox(fitz.Rect(38, gy, 560, gy + 85), g_desc, fontsize=8.5, fontname="helv", color=(0.15, 0.15, 0.15))
        gy += 90

    # Final Signoff Block
    page5.draw_rect(fitz.Rect(30, 720, 565, 785), color=BORDER_COLOR, fill=(0.95, 0.98, 0.95))
    page5.insert_text(fitz.Point(45, 740), "DOCUMENT SIGN-OFF & APPROVAL", fontsize=10, fontname="hebo", color=(0.0, 0.4, 0.1))
    page5.insert_text(fitz.Point(45, 760), "Lead Systems Architect: ______________________", fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))
    page5.insert_text(fitz.Point(320, 760), "Quality Assurance Manager: ______________________", fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))
    page5.insert_text(fitz.Point(45, 775), "Date of Approval: September 26, 2026", fontsize=8.5, fontname="heit", color=(0.4, 0.4, 0.4))

    add_page_header_footer(page5, "Setup & Deployment Guide", 5, 5)

    # Save PDF
    output_path = os.path.join(os.getcwd(), output_filename)
    doc.save(output_path)
    doc.close()
    print(f"✅ KT PDF Document generated successfully at: {output_path}")
    return output_path

if __name__ == "__main__":
    build_kt_pdf()
