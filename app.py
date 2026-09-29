import os
import sys
import json
import re
from datetime import datetime
import pandas as pd
import streamlit as st

# Ensure backend module is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.ocr_service import OCRService
from backend.app.ai_evaluator import AIEvaluator
from backend.app.camera_service import CameraService
from backend.app.llm_service import LLMService
import importlib
import create_aiml_docx
importlib.reload(create_aiml_docx)

try:
    mb, sb = create_aiml_docx.get_aiml_docx_bytes()
    with open("AIML_Master_Answer_Key.docx", "wb") as _f1:
        _f1.write(mb)
    with open("AIML_Student_Answer_Sheet.docx", "wb") as _f2:
        _f2.write(sb)
except Exception:
    pass

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Student Answer Sheet Evaluator Pro",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, high-aesthetic student-friendly UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 45%, #312E81 100%);
        border-radius: 20px;
        padding: 2.2rem 2.5rem;
        color: #FFFFFF;
        box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.3), 0 8px 10px -6px rgba(15, 23, 42, 0.2);
        border: 1px solid rgba(129, 140, 248, 0.25);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }

    .hero-banner::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(0, 0, 0, 0) 70%);
        pointer-events: none;
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #FFFFFF 0%, #E0E7FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        color: #C7D2FE;
        font-weight: 500;
        max-width: 850px;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 5px 13px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #EEF2FF;
        margin-right: 8px;
        margin-bottom: 6px;
    }

    .report-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .report-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px -5px rgba(0, 0, 0, 0.08);
    }

    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .metric-card-accent {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
    }

    .metric-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
        margin: 0.4rem 0;
    }

    .metric-label {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
    }

    .detected-header-box {
        background-color: #ECFDF5;
        border: 1px solid #A7F3D0;
        padding: 12px 18px;
        border-radius: 12px;
        color: #065F46;
        font-weight: 600;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.05);
    }

    .concept-pill-detected {
        display: inline-block;
        background-color: #D1FAE5;
        color: #047857;
        border: 1px solid #6EE7B7;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 3px;
    }

    .concept-pill-missing {
        display: inline-block;
        background-color: #FFE4E6;
        color: #BE123C;
        border: 1px solid #FCA5A5;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 3px;
    }

    .llm-badge {
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        color: #3730A3;
        border: 1px solid #C7D2FE;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
        padding: 0.5rem 1.2rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# DEFAULT DEMO DATA
# ------------------------------------------------------------------------------

# 1. Descriptive Mode Default Scheme & Student Sheet
DEFAULT_DESCRIPTIVE_SCHEME = [
    {
        "q_num": 1,
        "question": "What is encapsulation in Object-Oriented Programming?",
        "model_answer": "Encapsulation is the mechanism that binds together code and the data it manipulates, keeping both safe from outside interference and misuse. It hides internal implementation details using getter and setter methods.",
        "key_concepts": "encapsulation, binds code and data, data hiding, getter setter",
        "max_marks": 5.0
    },
    {
        "q_num": 2,
        "question": "Explain the difference between a process and a thread.",
        "model_answer": "A process is an independent executing program with its own separate memory space. A thread is a lightweight execution unit within a process that shares memory and resources with other threads of the same process.",
        "key_concepts": "independent memory, lightweight execution unit, shares memory, process vs thread",
        "max_marks": 5.0
    },
    {
        "q_num": 3,
        "question": "What is a Database Index and why is it used?",
        "model_answer": "A database index is a data structure that speeds up data retrieval operations on a database table. It acts like a book index to quickly locate rows without scanning the entire table.",
        "key_concepts": "data structure, speeds up retrieval, quick lookup, book index analogy",
        "max_marks": 5.0
    }
]

DEFAULT_DESCRIPTIVE_STUDENT_TEXT = """Roll No: STU-2026-088
Name: Rahul Sharma
Subject: Computer Science (CS-402)

Q1: Encapsulation is an object-oriented concept that binds code and data together into a single unit. It provides data hiding so outside functions cannot access private variables directly. Getter and setter methods are used for access.

Q2: A process is an independent program running in its own memory space. A thread is a lightweight unit of execution that runs inside a process and shares memory with other threads.

Q3: A database index is a special data structure that speeds up data retrieval on database tables. It allows quick lookups without scanning every row."""

# 2. Objective Mode Default Scheme & Student Sheet
DEFAULT_OBJECTIVE_SCHEME = [
    {
        "q_num": 1,
        "q_type": "MCQ",
        "question": "Which OOP concept binds code and data together?",
        "correct_answer": "B",
        "options": "A) Inheritance  B) Encapsulation  C) Polymorphism  D) Abstraction",
        "max_marks": 1.0,
        "negative_marks": 0.0
    },
    {
        "q_num": 2,
        "q_type": "True/False",
        "question": "Python is a compiled language. (True/False)",
        "correct_answer": "False",
        "options": "True / False",
        "max_marks": 1.0,
        "negative_marks": 0.0
    },
    {
        "q_num": 3,
        "q_type": "Fill in the Blanks",
        "question": "Lightweight unit of execution inside a process is called _____.",
        "correct_answer": "Thread",
        "options": "",
        "max_marks": 1.0,
        "negative_marks": 0.0
    },
    {
        "q_num": 4,
        "q_type": "One Word / Short",
        "question": "What data structure speeds up database table lookups?",
        "correct_answer": "Index",
        "options": "",
        "max_marks": 1.0,
        "negative_marks": 0.0
    },
    {
        "q_num": 5,
        "q_type": "Match the Column",
        "question": "Match Column A with Column B: 1. Python, 2. HTML, 3. SQL",
        "correct_answer": "1-C, 2-A, 3-B",
        "options": "A) Markup  B) Database  C) Programming",
        "max_marks": 2.0,
        "negative_marks": 0.0
    }
]

DEFAULT_OBJECTIVE_STUDENT_TEXT = """Roll No: STU-2026-088
Name: Rahul Sharma

Q1: B
Q2: False
Q3: Thread
Q4: Index
Q5: 1-C, 2-A, 3-B"""

# 3. Default Class Batch Sample Data
DEFAULT_CLASS_BATCH = [
    {
        "roll_no": "STU-2026-001",
        "name": "Rahul Sharma",
        "answers_text": """Q1: Encapsulation binds code and data together into a single unit. It provides data hiding and uses getter setter methods.
Q2: Process has independent memory space. Thread is a lightweight unit of execution sharing memory.
Q3: Index is a data structure that speeds up retrieval without table scanning."""
    },
    {
        "roll_no": "STU-2026-002",
        "name": "Priya Verma",
        "answers_text": """Q1: Encapsulation binds code and data together into a single unit. It provides data hiding and uses getter setter methods.
Q2: Process has independent memory space. Thread is a lightweight unit of execution sharing memory.
Q3: Index is a data structure that speeds up retrieval without table scanning."""
    },
    {
        "roll_no": "STU-2026-003",
        "name": "Amit Patel",
        "answers_text": """Q1: It is object oriented concept for security.
Q2: Process and thread are different running programs.
Q3: Index is used in database for fast query execution."""
    },
    {
        "roll_no": "STU-2026-004",
        "name": "Sneha Gupta",
        "answers_text": """Q1: Encapsulation binds code and data using getter setter for data hiding.
Q2: Process is independent program with memory space. Thread is lightweight execution unit.
Q3: Database index is data structure that speeds up retrieval using book index lookup."""
    }
]

# Initialize Session State
if "student_info" not in st.session_state:
    st.session_state["student_info"] = {
        "roll_no": "STU-2026-088",
        "name": "Rahul Sharma",
        "subject": "Computer Science (CS-402)",
        "exam": "Mid-Term Examination"
    }

if "descriptive_scheme" not in st.session_state:
    st.session_state["descriptive_scheme"] = DEFAULT_DESCRIPTIVE_SCHEME

if "descriptive_student_text" not in st.session_state:
    st.session_state["descriptive_student_text"] = DEFAULT_DESCRIPTIVE_STUDENT_TEXT

if "objective_scheme" not in st.session_state:
    st.session_state["objective_scheme"] = DEFAULT_OBJECTIVE_SCHEME

if "objective_student_text" not in st.session_state:
    st.session_state["objective_student_text"] = DEFAULT_OBJECTIVE_STUDENT_TEXT

if "descriptive_results" not in st.session_state:
    st.session_state["descriptive_results"] = None

if "objective_results" not in st.session_state:
    st.session_state["objective_results"] = None

if "class_batch_data" not in st.session_state:
    st.session_state["class_batch_data"] = DEFAULT_CLASS_BATCH

if "class_batch_results" not in st.session_state:
    st.session_state["class_batch_results"] = None

if "camera_ip" not in st.session_state:
    st.session_state["camera_ip"] = "http://192.168.1.100:8080/shot.jpg"

if "camera_name" not in st.session_state:
    st.session_state["camera_name"] = "Exam Hall IP Camera #1"

if "camera_status" not in st.session_state:
    st.session_state["camera_status"] = None

if "captured_camera_image" not in st.session_state:
    st.session_state["captured_camera_image"] = None

if "camera_history" not in st.session_state:
    st.session_state["camera_history"] = []

if "booklet_pages" not in st.session_state:
    st.session_state["booklet_pages"] = []

if "llm_provider" not in st.session_state:
    st.session_state["llm_provider"] = "ollama"

if "ollama_model_name" not in st.session_state:
    st.session_state["ollama_model_name"] = "llama3"

if "ollama_endpoint" not in st.session_state:
    st.session_state["ollama_endpoint"] = "http://localhost:11434"


# Helper function for Visual Keyword Highlighting in HTML
def highlight_keywords(text: str, detected_keywords: list) -> str:
    if not text:
        return "[Empty Answer]"
    escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
    for kw in detected_keywords:
        if kw and len(kw.strip()) > 2:
            clean_kw = kw.strip()
            pattern = re.compile(re.escape(clean_kw), re.IGNORECASE)
            escaped_text = pattern.sub(
                lambda m: f'<mark style="background-color: #059669; color: #FFFFFF; padding: 3px 8px; border-radius: 6px; font-weight: 700; border: 1px solid #34D399; box-shadow: 0 0 6px rgba(16, 185, 129, 0.3);">{m.group(0)}</mark>',
                escaped_text
            )
    return escaped_text


# Helper function for Objective evaluation
def evaluate_objective_answer(student_text: str, correct_answer: str, q_type: str, max_marks: float, negative_marks: float) -> dict:
    clean_student = (student_text or "").strip()
    clean_correct = (correct_answer or "").strip()

    if not clean_student:
        return {
            "status": "Unattempted",
            "marks": 0.0,
            "badge_color": "#F1F5F9",
            "text_color": "#475569",
            "remark": "⚪ Question unattempted."
        }

    s_norm = clean_student.lower().replace(" ", "").replace(".", "").replace(":", "")
    c_norm = clean_correct.lower().replace(" ", "").replace(".", "").replace(":", "")

    is_correct = False

    if q_type == "MCQ":
        s_letter = s_norm[0] if s_norm else ""
        c_letter = c_norm[0] if c_norm else ""
        is_correct = (s_norm == c_norm) or (s_letter and s_letter == c_letter)
    elif q_type == "True/False":
        s_bool = "true" if "true" in s_norm or s_norm == "t" else ("false" if "false" in s_norm or s_norm == "f" else s_norm)
        c_bool = "true" if "true" in c_norm or c_norm == "t" else ("false" if "false" in c_norm or c_norm == "f" else c_norm)
        is_correct = (s_bool == c_bool)
    elif q_type in ["Fill in the Blanks", "One Word / Short"]:
        is_correct = (s_norm == c_norm) or (c_norm in s_norm) or (s_norm in c_norm)
    elif q_type == "Match the Column":
        is_correct = (s_norm == c_norm)
    else:
        is_correct = (s_norm == c_norm)

    if is_correct:
        return {
            "status": "Correct",
            "marks": max_marks,
            "badge_color": "#DEF7EC",
            "text_color": "#03543F",
            "remark": f"✅ Correct! Awarded +{max_marks:.1f} marks."
        }
    else:
        deduction = abs(negative_marks)
        awarded = -deduction if deduction > 0 else 0.0
        return {
            "status": "Incorrect",
            "marks": awarded,
            "badge_color": "#FDE8E8",
            "text_color": "#9B1C1C",
            "remark": f"❌ Wrong. Correct Answer: '{clean_correct}' ({'-' if deduction > 0 else ''}{deduction:.2f} marks)."
        }


# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/test-passed.png", width=60)
    st.title("Student Evaluator Pro")
    st.caption("AI Answer Sheet & IP Camera Evaluation System")
    st.divider()

    st.subheader("⚡ Quick Controls")
    if st.button("🔄 Reset & Load Sample Data", use_container_width=True):
        st.session_state["student_info"] = {
            "roll_no": "STU-2026-088",
            "name": "Rahul Sharma",
            "subject": "Computer Science (CS-402)",
            "exam": "Mid-Term Examination"
        }
        st.session_state["descriptive_scheme"] = DEFAULT_DESCRIPTIVE_SCHEME
        st.session_state["descriptive_student_text"] = DEFAULT_DESCRIPTIVE_STUDENT_TEXT
        st.session_state["objective_scheme"] = DEFAULT_OBJECTIVE_SCHEME
        st.session_state["objective_student_text"] = DEFAULT_OBJECTIVE_STUDENT_TEXT
        st.session_state["descriptive_results"] = None
        st.session_state["objective_results"] = None
        st.session_state["class_batch_results"] = None
        st.session_state["captured_camera_image"] = None
        st.session_state["booklet_pages"] = []
        st.success("Sample data reset successfully!")
        st.rerun()

    st.divider()

    # Ollama Local LLM Engine Controls
    with st.expander("🦙 Ollama Local LLM Engine", expanded=True):
        st.session_state["ollama_model_name"] = st.text_input(
            "Ollama Model Tag (e.g. llama3, mistral, phi3, qwen):",
            value=st.session_state.get("ollama_model_name", "llama3"),
            key="sb_ollama_model"
        )
        st.session_state["ollama_endpoint"] = st.text_input(
            "Ollama Server Endpoint URL:",
            value=st.session_state.get("ollama_endpoint", "http://localhost:11434"),
            key="sb_ollama_endpoint"
        )
        st.caption(f"Active LLM: **OLLAMA LOCAL LLM ({st.session_state.get('ollama_model_name', 'llama3').upper()})**")
        st.info("🔒 100% Private & Local Inference (No external API keys required)")

    st.divider()
    st.markdown("### 🌟 Included Features:")
    st.markdown("""
    - 🤖 **LLM Answer Sheet Evaluator Engine**
    - 🔍 **Header Auto-OCR (Roll No & Name Auto-Detect)**
    - 📐 **Camera Auto-Deskew & Contrast Enhancer**
    - 📚 **Multi-Page Booklet Continuous Scanning**
    - 🕵️‍♂️ **Class Plagiarism & Copy Detection Matrix**
    - 📹 **IP Camera Connectivity & 1-Click Photo Snap**
    - 🔑 **Master Key File Upload (PDF, DOCX, TXT)**
    - 📜 **Printable Report Cards (.txt / .docx)**
    """)
    st.divider()
    st.caption("AI Engine: ✅ Active (LLM + Auto-Enhance + PyMuPDF + DOCX)")


# Header Section
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">📝 AI On-Screen Marking & Evaluator Pro</div>
    <div class="hero-subtitle">
        Intelligent LLM-powered answer sheet evaluation, RTSP/HTTP IP camera connectivity, continuous multi-page booklet scanning, and automated class plagiarism detection.
    </div>
    <div>
        <span class="pill-badge">🤖 LLM Model Engine</span>
        <span class="pill-badge">📹 RTSP/HTTP IP Camera</span>
        <span class="pill-badge">📚 Continuous Booklet Scan</span>
        <span class="pill-badge">🕵️ Plagiarism Detection</span>
        <span class="pill-badge">📄 DOCX / PDF Master Key</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Mode Selector Radio
exam_mode = st.radio(
    "📋 Select Examination Mode:",
    ["📝 Full Content / Theory Exam (Descriptive)", "🎯 Objective Exam (MCQ, True/False, One-Word, Fill-Blanks, Match Column)"],
    horizontal=True,
    key="global_exam_mode"
)

st.divider()

# Main Navigation Tabs
tab_cam, tab1, tab2, tab3, tab4 = st.tabs([
    "📹 IP Camera & Booklet Scan",
    "1️⃣ Student Info & Master Key (PDF, DOCX, TXT)",
    "2️⃣ Upload / Capture Student Sheet",
    "3️⃣ Scorecard & Report Card",
    "4️⃣ Class Analytics & Plagiarism Matrix 🏆"
])

# ==============================================================================
# TAB 0: IP CAMERA CONNECTIVITY & MULTI-PAGE BOOKLET SCANNER
# ==============================================================================
with tab_cam:
    st.subheader("📹 IP Camera Connectivity & Multi-Page Booklet Scanner")
    st.caption("Connect IP cameras (HTTP Snapshot URL, RTSP, ESP32-CAM, or WebCam) to snap single/multi-page student answer booklets.")

    cam_col1, cam_col2 = st.columns([1, 1], gap="large")

    with cam_col1:
        st.markdown("### ⚙️ IP Camera Settings & Connection Test")
        cam_ip_input = st.text_input(
            "Camera IP Address / Stream URL or WebCam Index:",
            value=st.session_state["camera_ip"],
            help="Example: http://192.168.1.100:8080/shot.jpg or 192.168.1.50 or 0 for USB WebCam",
            key="cam_ip_field"
        )
        cam_name_input = st.text_input("Camera Name / Location Label:", value=st.session_state["camera_name"], key="cam_name_field")
        st.session_state["camera_ip"] = cam_ip_input
        st.session_state["camera_name"] = cam_name_input

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("🔌 Test Camera Connection", use_container_width=True, key="test_cam_btn"):
                res = CameraService.test_connection(cam_ip_input)
                st.session_state["camera_status"] = res
        with col_t2:
            preset_choice = st.selectbox(
                "Presets / Demo Cams:",
                ["IP Webcam App (http://...:8080)", "ESP32-CAM (http://192.168.4.1/capture)", "USB WebCam (Index 0)", "Simulated IP Camera Stream"],
                key="cam_preset_sel"
            )
            if st.button("Apply Preset", use_container_width=True, key="apply_preset_btn"):
                if "IP Webcam" in preset_choice: st.session_state["camera_ip"] = "http://192.168.1.100:8080/shot.jpg"
                elif "ESP32" in preset_choice: st.session_state["camera_ip"] = "http://192.168.4.1/capture"
                elif "USB WebCam" in preset_choice: st.session_state["camera_ip"] = "0"
                else: st.session_state["camera_ip"] = "192.168.1.150:8080"
                st.rerun()

        if st.session_state["camera_status"]:
            c_stat = st.session_state["camera_status"]
            if c_stat.get("connected"):
                st.success(f"🟢 **CONNECTED**: {c_stat.get('message')}")
            else:
                st.error(f"🔴 **DISCONNECTED**: {c_stat.get('message')}")

        st.divider()
        st.markdown("### 📸 Multi-Page Booklet Scanner")
        target_roll = st.text_input("Target Student Roll No:", value=st.session_state["student_info"]["roll_no"], key="cam_target_roll")
        target_name = st.text_input("Target Student Name:", value=st.session_state["student_info"]["name"], key="cam_target_name")

        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("📸 Click Page from Camera", type="primary", use_container_width=True, key="click_cam_pic_btn"):
                with st.spinner("Capturing snapshot, enhancing contrast & running Auto-Header OCR..."):
                    cap_res = CameraService.capture_snapshot(cam_ip_input, student_roll=target_roll)
                    if cap_res.get("status") == "success":
                        raw_bytes = cap_res["image_bytes"]
                        enhanced_bytes = OCRService.enhance_image_for_ocr(raw_bytes)
                        st.session_state["captured_camera_image"] = enhanced_bytes

                        ocr_res = OCRService.extract_from_image(enhanced_bytes)
                        extracted = ocr_res.get("text", "")

                        hdr = OCRService.parse_student_header(extracted)
                        if hdr["has_detected"]:
                            st.session_state["student_info"]["roll_no"] = hdr["roll_no"]
                            st.session_state["student_info"]["name"] = hdr["name"]
                            st.markdown(f'<div class="detected-header-box">🔍 Auto-Detected Header! Roll No: {hdr["roll_no"]} | Name: {hdr["name"]}</div>', unsafe_allow_html=True)
                        else:
                            st.session_state["student_info"]["roll_no"] = target_roll
                            st.session_state["student_info"]["name"] = target_name

                        page_num = len(st.session_state["booklet_pages"]) + 1
                        st.session_state["booklet_pages"].append({
                            "page": page_num,
                            "time": cap_res.get("timestamp"),
                            "text": extracted
                        })

                        full_booklet_text = "\n\n".join([f"--- PAGE {p['page']} ---\n{p['text']}" for p in st.session_state["booklet_pages"]])
                        st.session_state["descriptive_student_text"] = full_booklet_text
                        st.session_state["objective_student_text"] = full_booklet_text

                        st.session_state["camera_history"].append({
                            "roll": st.session_state["student_info"]["roll_no"],
                            "name": st.session_state["student_info"]["name"],
                            "time": cap_res.get("timestamp"),
                            "source": cap_res.get("source"),
                            "text_length": len(extracted)
                        })

                        st.success(f"✅ Added Page #{page_num} to student booklet!")

        with btn_c2:
            if st.button("🧹 Clear Booklet Queue", use_container_width=True, key="clear_booklet_btn"):
                st.session_state["booklet_pages"] = []
                st.session_state["captured_camera_image"] = None
                st.info("Booklet queue reset.")
                st.rerun()

        st.divider()
        st.markdown("### 📁 Or Upload File Directly (Image / PDF / DOCX)")
        cam_uploaded_file = st.file_uploader(
            "Select Answer Sheet File (PNG, JPG, PDF, DOCX)",
            type=["png", "jpg", "jpeg", "pdf", "docx", "doc"],
            key="cam_tab_file_uploader"
        )
        if cam_uploaded_file is not None:
            c_file_bytes = cam_uploaded_file.read()
            c_filename = cam_uploaded_file.name.lower()
            if c_filename.endswith(".docx") or c_filename.endswith(".doc"):
                c_ocr = OCRService.extract_from_docx(c_file_bytes)
            elif c_filename.endswith(".pdf"):
                with open("temp_cam_sheet.pdf", "wb") as f: f.write(c_file_bytes)
                c_ocr = OCRService.extract_from_pdf("temp_cam_sheet.pdf")
            else:
                c_file_bytes = OCRService.enhance_image_for_ocr(c_file_bytes)
                c_ocr = OCRService.extract_from_image(c_file_bytes)

            hdr = OCRService.parse_student_header(c_ocr.get("text", ""))
            if hdr["has_detected"]:
                st.session_state["student_info"]["roll_no"] = hdr["roll_no"]
                st.session_state["student_info"]["name"] = hdr["name"]

            st.session_state["descriptive_student_text"] = c_ocr.get("text", "")
            st.session_state["objective_student_text"] = c_ocr.get("text", "")
            st.success(f"✅ Loaded & extracted text from uploaded file: {cam_uploaded_file.name}!")

    with cam_col2:
        st.markdown("### 🖼️ Live Camera Viewport & Booklet Pages")
        if st.session_state["captured_camera_image"]:
            st.image(st.session_state["captured_camera_image"], caption=f"Latest Page Captured via {st.session_state['camera_name']}", use_container_width=True)
            if st.session_state["booklet_pages"]:
                st.write(f"Booklet Pages Scanned: **{len(st.session_state['booklet_pages'])} Page(s)**")
            with st.expander("📄 View Combined Booklet OCR Text", expanded=True):
                st.text_area("Combined Booklet Text:", value=st.session_state.get("descriptive_student_text", ""), height=180, key="cam_ocr_preview")
        else:
            st.info("💡 Click **'📸 Click Page from Camera'** to take a photo of student answer booklet pages.")
            placeholder_bytes = CameraService._generate_simulated_camera_sheet(st.session_state["camera_ip"], st.session_state["student_info"]["roll_no"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.image(placeholder_bytes, caption="IP Camera Frame Viewport (Live Standby Feed)", use_container_width=True)

        if st.session_state["camera_history"]:
            with st.expander("📜 IP Camera Capture Log / Recent Queue", expanded=False):
                st.dataframe(pd.DataFrame(st.session_state["camera_history"]), use_container_width=True)


# ==============================================================================
# MODE 1: DESCRIPTIVE / FULL THEORY EXAM
# ==============================================================================
if "Descriptive" in exam_mode:

    # TAB 1: Student Info & Descriptive Master Sheet
    with tab1:
        col_a, col_b = st.columns([1, 1], gap="large")

        with col_a:
            st.subheader("👤 Student Information")
            roll_no = st.text_input("Student Roll No / ID", value=st.session_state["student_info"]["roll_no"], key="desc_roll")
            name = st.text_input("Student Full Name", value=st.session_state["student_info"]["name"], key="desc_name")
            subject = st.text_input("Subject / Course Name", value=st.session_state["student_info"]["subject"], key="desc_subj")
            exam = st.text_input("Exam Name", value=st.session_state["student_info"]["exam"], key="desc_exam")

            st.session_state["student_info"] = {"roll_no": roll_no, "name": name, "subject": subject, "exam": exam}

        with col_b:
            st.subheader("🔑 Master Answer Key & Marking Scheme (PDF, DOCX, TXT)")

            # Sample AI/ML DOCX Download Section
            st.markdown("##### 📄 Download AI/ML 10-Question Test Benchmark (.docx):")
            m_bytes, s_bytes = create_aiml_docx.get_aiml_docx_bytes()
            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    "📥 AI/ML Master Key (.docx)",
                    data=m_bytes,
                    file_name="AIML_Master_Answer_Key.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            with d2:
                st.download_button(
                    "📥 AI/ML Student Sheet (.docx)",
                    data=s_bytes,
                    file_name="AIML_Student_Answer_Sheet.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

            st.write("")
            master_mode = st.radio("Master Key Input Method:", ["Manual Form / Preset Data", "Upload Master Key File (PDF / DOCX / TXT / Written / Image)"], horizontal=True, key="desc_master_mode")

            if master_mode == "Upload Master Key File (PDF / DOCX / TXT / Written / Image)":
                master_file = st.file_uploader("Upload Master Solution Sheet (PDF, DOCX, TXT, JSON, Image)", type=["png", "jpg", "jpeg", "pdf", "docx", "doc", "json", "txt"], key="desc_master_uploader")
                if master_file is not None:
                    m_file_bytes = master_file.read()
                    filename = master_file.name.lower()
                    if st.session_state.get("last_uploaded_master_name") != master_file.name:
                        parsed_res = OCRService.parse_master_key_file(m_file_bytes, filename)
                        if parsed_res and parsed_res.get("scheme"):
                            st.session_state["descriptive_scheme"] = parsed_res["scheme"]
                            st.session_state["descriptive_results"] = None  # Reset old evaluation
                            st.session_state["desc_num_q"] = len(parsed_res["scheme"])
                            st.session_state["last_uploaded_master_name"] = master_file.name
                            st.success(f"✅ Loaded {len(parsed_res['scheme'])} Master Key Questions from {master_file.name} ({parsed_res.get('source')})! Old scorecard cleared.")

            st.markdown("**Review & Edit Master Marking Scheme:**")
            num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=len(st.session_state["descriptive_scheme"]), key="desc_num_q")

            current_scheme = st.session_state["descriptive_scheme"]
            while len(current_scheme) < num_questions:
                q_id = len(current_scheme) + 1
                current_scheme.append({"q_num": q_id, "question": f"Question {q_id}", "model_answer": f"Model solution {q_id}", "key_concepts": "concept1, concept2", "max_marks": 5.0})
            current_scheme = current_scheme[:num_questions]

            updated_scheme = []
            for i, item in enumerate(current_scheme):
                with st.expander(f"📌 Q{item.get('q_num', i+1)}: {item.get('question', '')[:35]}...", expanded=(i == 0)):
                    q_num = item.get('q_num', i + 1)
                    q_text = st.text_input(f"Q{q_num} Question", value=item.get('question', f'Question {q_num}'), key=f"desc_q_{i}")
                    m_ans = st.text_area(f"Q{q_num} Model Solution", value=item.get('model_answer', ''), key=f"desc_m_{i}")
                    concepts = st.text_input(f"Q{q_num} Key Concepts", value=item.get('key_concepts', ''), key=f"desc_c_{i}")
                    max_m = st.number_input(f"Q{q_num} Max Marks", min_value=1.0, max_value=100.0, value=float(item.get('max_marks', 5.0)), key=f"desc_max_{i}")

                    updated_scheme.append({"q_num": q_num, "question": q_text, "model_answer": m_ans, "key_concepts": concepts, "max_marks": max_m})

            st.session_state["descriptive_scheme"] = updated_scheme

    # TAB 2: Upload / Capture Student Sheet
    with tab2:
        st.subheader("📄 Student Answer Sheet Input (Descriptive Mode)")
        input_mode = st.radio("Input Method:", ["Upload Answer Sheet (Image / PDF / DOCX)", "📸 Capture via Connected IP Camera", "Type / Paste Student Answers / Written Format"], horizontal=True, key="desc_input_mode")

        if input_mode == "📸 Capture via Connected IP Camera":
            st.info(f"Connected to IP Camera: **{st.session_state['camera_name']}** (`{st.session_state['camera_ip']}`)")
            c1, c2 = st.columns([2, 1])
            with c1:
                target_r = st.text_input("Student Roll No", value=st.session_state["student_info"]["roll_no"], key="tab2_desc_roll")
            with c2:
                st.write("")
                st.write("")
                if st.button("📸 Snap Picture from IP Camera", type="primary", use_container_width=True, key="tab2_desc_cam_btn"):
                    with st.spinner("Capturing frame, enhancing contrast & running auto-header OCR..."):
                        cap_res = CameraService.capture_snapshot(st.session_state["camera_ip"], target_r)
                        if cap_res.get("status") == "success":
                            img_bytes = OCRService.enhance_image_for_ocr(cap_res["image_bytes"])
                            st.session_state["captured_camera_image"] = img_bytes
                            ocr_res = OCRService.extract_from_image(img_bytes)
                            st.session_state["descriptive_student_text"] = ocr_res.get("text", "")

                            hdr = OCRService.parse_student_header(ocr_res.get("text", ""))
                            if hdr["has_detected"]:
                                st.session_state["student_info"]["roll_no"] = hdr["roll_no"]
                                st.session_state["student_info"]["name"] = hdr["name"]
                                st.success(f"🔍 Auto-Detected Header! Roll No: {hdr['roll_no']} | Name: {hdr['name']}")
                            else:
                                st.success("✅ Snapshot captured and OCR extracted!")

            if st.session_state["captured_camera_image"]:
                st.image(st.session_state["captured_camera_image"], caption="Captured Student Sheet Photo", width=500)
            st.text_area("Extracted Answer Sheet Content:", value=st.session_state["descriptive_student_text"], height=200, key="desc_cam_text_preview")

        elif input_mode == "Upload Answer Sheet (Image / PDF / DOCX)":
            uploaded_file = st.file_uploader("Upload Student Sheet (PNG, JPG, PDF, DOCX)", type=["png", "jpg", "jpeg", "pdf", "docx", "doc"], key="desc_student_uploader")
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                filename = uploaded_file.name.lower()
                if st.session_state.get("last_uploaded_student_name") != uploaded_file.name:
                    if filename.endswith(".docx") or filename.endswith(".doc"):
                        ocr_res = OCRService.extract_from_docx(file_bytes)
                    elif filename.endswith(".pdf"):
                        with open("temp_sheet.pdf", "wb") as f: f.write(file_bytes)
                        ocr_res = OCRService.extract_from_pdf("temp_sheet.pdf")
                    else:
                        file_bytes = OCRService.enhance_image_for_ocr(file_bytes)
                        ocr_res = OCRService.extract_from_image(file_bytes)

                    extracted_text = ocr_res.get("text", "")
                    hdr = OCRService.parse_student_header(extracted_text)
                    if hdr["has_detected"]:
                        st.session_state["student_info"]["roll_no"] = hdr["roll_no"]
                        st.session_state["student_info"]["name"] = hdr["name"]
                        st.success(f"🔍 Header Auto-Detected: Roll No: {hdr['roll_no']} | Name: {hdr['name']}")

                    st.session_state["descriptive_student_text"] = extracted_text
                    st.session_state["descriptive_results"] = None  # Reset old evaluation
                    st.session_state["last_uploaded_student_name"] = uploaded_file.name
                    st.success(f"✅ Loaded new student sheet ({uploaded_file.name})! Click '🚀 Evaluate Theory Answer Sheet with LLM Engine' below to grade.")

                st.text_area("Extracted Student Text:", value=st.session_state["descriptive_student_text"], height=200, key="desc_ocr_area")
            else:
                st.text_area("Current Text Preview:", value=st.session_state["descriptive_student_text"], height=180, disabled=True, key="desc_preview")
        else:
            pasted_text = st.text_area("Type or paste student answer sheet content (written format):", value=st.session_state["descriptive_student_text"], height=250, key="desc_pasted")
            st.session_state["descriptive_student_text"] = pasted_text

        st.divider()

        if st.button("🚀 Evaluate Theory Answer Sheet with LLM Engine", type="primary", use_container_width=True, key="desc_eval_btn"):
            raw_text = st.session_state["descriptive_student_text"]
            marking_scheme = st.session_state["descriptive_scheme"]
            parsed_answers = OCRService.parse_answers_by_question(raw_text)

            evaluations = []
            total_obtained = 0.0
            total_max = 0.0

            for item in marking_scheme:
                q_num = item["q_num"]
                student_ans = parsed_answers.get(q_num, "")
                if not student_ans and raw_text:
                    lines = [l for l in raw_text.split('\n') if l.strip()]
                    student_ans = lines[q_num - 1] if len(lines) >= q_num else raw_text

                concepts_list = [c.strip() for c in item["key_concepts"].split(",") if c.strip()]
                max_m = float(item["max_marks"])

                res = AIEvaluator.evaluate_answer(
                    student_text=student_ans,
                    model_answer=item["model_answer"],
                    key_concepts=concepts_list,
                    max_marks=max_m,
                    question_text=item.get("question", ""),
                    model_name=st.session_state.get("ollama_model_name", "llama3"),
                    endpoint=st.session_state.get("ollama_endpoint", "http://localhost:11434")
                )
                res["q_num"] = q_num
                res["question"] = item["question"]
                res["model_answer"] = item["model_answer"]
                res["student_text"] = student_ans
                res["max_marks"] = max_m

                total_obtained += res["suggested_marks"]
                total_max += max_m
                evaluations.append(res)

            summary = AIEvaluator.generate_overall_summary(evaluations, total_obtained, total_max)
            accuracy = (total_obtained / max(total_max, 1.0)) * 100.0

            st.session_state["descriptive_results"] = {
                "evaluations": evaluations, "total_obtained": total_obtained, "total_max": total_max, "accuracy": accuracy, "summary": summary
            }
            st.success("✅ LLM Evaluation complete! Switch to 'Scorecard & Report Card' tab.")

    # TAB 3: Descriptive Scorecard & Report Card
    with tab3:
        eval_data = st.session_state["descriptive_results"]
        student_info = st.session_state["student_info"]

        if eval_data is None:
            st.info("💡 Go to Tab 2 and click **'Evaluate Theory Answer Sheet'**.")
        else:
            total_obtained = eval_data["total_obtained"]
            total_max = eval_data["total_max"]
            accuracy = eval_data["accuracy"]
            summary = eval_data["summary"]
            evaluations = eval_data["evaluations"]

            st.markdown(f"""
            <div class="report-card" style="margin-bottom:1rem; padding: 1.4rem 1.8rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div>
                        <h2 style="font-family:'Outfit',sans-serif; margin:0; color:#0F172A; font-weight:800; font-size:1.7rem;">🎓 Theory Exam Scorecard: {student_info['name']}</h2>
                        <p style="margin:0.4rem 0 0 0; color:#64748B; font-weight:600;">
                            <b>Roll No:</b> {student_info['roll_no']} &nbsp;|&nbsp; <b>Subject:</b> {student_info['subject']} &nbsp;|&nbsp; <b>Exam:</b> {student_info['exam']}
                        </p>
                    </div>
                    <div>
                        <span class="llm-badge">🤖 Engine: {evaluations[0].get('llm_provider', 'LLM Engine')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-accent" style="background: linear-gradient(90deg, #10B981, #059669);"></div>
                    <div class="metric-label">Total Score</div>
                    <div class="metric-value" style="color:#059669;">{total_obtained:.1f} <span style="font-size:1.1rem; color:#64748B;">/ {total_max:.1f}</span></div>
                </div>
                """, unsafe_allow_html=True)

            with m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-accent" style="background: linear-gradient(90deg, #6366F1, #4F46E5);"></div>
                    <div class="metric-label">Accuracy Rate</div>
                    <div class="metric-value" style="color:#4F46E5;">{accuracy:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-accent" style="background: linear-gradient(90deg, #8B5CF6, #7C3AED);"></div>
                    <div class="metric-label">Grade Assigned</div>
                    <div class="metric-value" style="color:#7C3AED; font-size:1.5rem; margin-top:0.6rem;">{summary['recommended_grade']}</div>
                </div>
                """, unsafe_allow_html=True)

            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-accent" style="background: linear-gradient(90deg, #0EA5E9, #0284C7);"></div>
                    <div class="metric-label">Evaluated Qs</div>
                    <div class="metric-value" style="color:#0284C7;">{len(evaluations)}</div>
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.progress(min(1.0, max(0.0, accuracy / 100.0)))
            st.divider()

            st.subheader("🔍 Question Breakdown with Visual Keyword Highlights (🟩 Matched / 🟥 Missing)")
            for ev in evaluations:
                q_num = ev["q_num"]
                marks = ev["suggested_marks"]
                max_m = ev["max_marks"]
                pct = (marks / max(max_m, 1.0)) * 100

                detected = ev.get("detected_concepts", [])
                missing = ev.get("missing_concepts", [])
                highlighted_text = highlight_keywords(ev["student_text"], detected)

                with st.expander(f"Q{q_num}: {ev['question']} — Score: {marks:.1f}/{max_m:.1f} ({pct:.0f}%)", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Student Answer (🟩 Matched Concepts Highlighted):**")
                        st.markdown(f'<div style="background-color: #0F172A; color: #F8FAFC; border: 1px solid #334155; padding: 1rem 1.2rem; border-radius: 10px; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0.8rem;">{highlighted_text}</div>', unsafe_allow_html=True)
                        st.markdown("**Model Solution:**")
                        st.caption(ev["model_answer"])
                    with c2:
                        st.markdown(f"**Awarded Marks**: `{marks:.1f} / {max_m:.1f}`")
                        st.markdown(f"**LLM Model Engine**: `{ev.get('llm_provider', 'Hybrid LLM')} ({ev.get('model_name', '')})`")
                        st.markdown(f"**Matched Concepts**: {', '.join([f'`✓ {c}`' for c in detected]) or 'None'}")
                        if missing:
                            st.markdown(f"**Missing Concepts**: {', '.join([f'`✗ {c}`' for c in missing])}")
                        st.info(ev["ai_explanation"])

            st.divider()

            # Printable & Downloadable Report Card Preview
            report_text = f"""==================================================
OFFICIAL STUDENT EXAM REPORT CARD
==================================================
Student Name: {student_info['name']}
Roll Number:  {student_info['roll_no']}
Subject:      {student_info['subject']}
Exam:         {student_info['exam']}
Date:         {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
--------------------------------------------------
Total Marks:  {total_obtained:.1f} / {total_max:.1f}
Accuracy:     {accuracy:.1f}%
Final Grade:  {summary['recommended_grade']}
--------------------------------------------------
QUESTION BREAKDOWN & EVALUATION FEEDBACK:
"""
            for ev in evaluations:
                report_text += f"\nQ{ev['q_num']}: {ev['question']}\n"
                report_text += f"   Student Answer: {ev['student_text']}\n"
                report_text += f"   Model Solution: {ev['model_answer']}\n"
                report_text += f"   Awarded Marks:  {ev['suggested_marks']:.1f} / {ev['max_marks']:.1f}\n"
                report_text += f"   LLM Model:      {ev.get('llm_provider', 'Hybrid LLM')}\n"
                report_text += f"   Feedback:       {ev['ai_explanation']}\n"

            report_text += "\n==================================================\nEvaluator: AI-OSM Answer Sheet Evaluator Engine\n"

            col_down1, col_down2 = st.columns(2)
            with col_down1:
                st.download_button(
                    label="📥 Download Official Report Card (.docx / .txt format)",
                    data=report_text.encode("utf-8"),
                    file_name=f"Report_Card_{student_info['roll_no']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with st.expander("📜 View Printable Official Student Report Card", expanded=False):
                st.markdown(f"""
                <div class="report-card">
                    <div style="text-align: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 1rem; margin-bottom: 1.5rem;">
                        <h2 style="margin:0; color:#0F172A;">OFFICIAL EXAM REPORT CARD</h2>
                        <p style="margin:0; color:#64748B;">Automated AI Answer Sheet Evaluation System</p>
                    </div>
                    <table style="width:100%; border-collapse:collapse; margin-bottom: 1.5rem;">
                        <tr><td><b>Student Name:</b> {student_info['name']}</td><td><b>Roll No:</b> {student_info['roll_no']}</td></tr>
                        <tr><td><b>Subject:</b> {student_info['subject']}</td><td><b>Exam:</b> {student_info['exam']}</td></tr>
                        <tr><td><b>Final Marks:</b> {total_obtained:.1f} / {total_max:.1f}</td><td><b>Grade:</b> {summary['recommended_grade']}</td></tr>
                    </table>
                    <div style="margin-top: 2rem; display: flex; justify-content: space-between; border-top: 1px dashed #CBD5E1; padding-top: 1rem;">
                        <div><b>AI System Accuracy:</b> {accuracy:.1f}%</div>
                        <div><b>Evaluator Signature:</b> ____________________</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# MODE 2: OBJECTIVE EXAM (MCQ, True/False, One-Word, Fill-Blanks, Match Column)
# ==============================================================================
else:

    # TAB 1: Student Info & Objective Master Sheet
    with tab1:
        col_a, col_b = st.columns([1, 1], gap="large")

        with col_a:
            st.subheader("👤 Student Information")
            roll_no = st.text_input("Student Roll No / ID", value=st.session_state["student_info"]["roll_no"], key="obj_roll")
            name = st.text_input("Student Full Name", value=st.session_state["student_info"]["name"], key="obj_name")
            subject = st.text_input("Subject / Course Name", value=st.session_state["student_info"]["subject"], key="obj_subj")
            exam = st.text_input("Exam Name", value=st.session_state["student_info"]["exam"], key="obj_exam")

            st.session_state["student_info"] = {"roll_no": roll_no, "name": name, "subject": subject, "exam": exam}

        with col_b:
            st.subheader("🎯 Objective Answer Key & Marking Scheme (PDF, DOCX, TXT)")
            master_mode = st.radio("Input Method:", ["Manual Form / Preset Data", "Upload Objective Key File (PDF / DOCX / JSON / TXT)"], horizontal=True, key="obj_master_mode")

            if master_mode == "Upload Objective Key File (PDF / DOCX / JSON / TXT)":
                obj_file = st.file_uploader("Upload Objective Key File (PDF, DOCX, JSON, TXT)", type=["json", "txt", "docx", "pdf"], key="obj_file_uploader")
                if obj_file is not None:
                    bytes_data = obj_file.read()
                    parsed_res = OCRService.parse_master_key_file(bytes_data, obj_file.name)
                    if parsed_res and parsed_res.get("scheme"):
                        st.session_state["objective_scheme"] = parsed_res["scheme"]
                        st.success(f"✅ Loaded {len(parsed_res['scheme'])} objective questions from {obj_file.name}!")

            num_obj_q = st.number_input("Number of Questions", min_value=1, max_value=20, value=len(st.session_state["objective_scheme"]), key="obj_num_q")

            current_obj = st.session_state["objective_scheme"]
            while len(current_obj) < num_obj_q:
                q_id = len(current_obj) + 1
                current_obj.append({"q_num": q_id, "q_type": "MCQ", "question": f"Question {q_id}", "correct_answer": "A", "options": "A) Opt1  B) Opt2", "max_marks": 1.0, "negative_marks": 0.0})
            current_obj = current_obj[:num_obj_q]

            updated_obj = []
            for i, item in enumerate(current_obj):
                with st.expander(f"🎯 Q{item.get('q_num', i+1)} ({item.get('q_type', 'MCQ')}): {item.get('question', '')[:35]}...", expanded=(i == 0)):
                    c1, c2 = st.columns(2)
                    with c1:
                        q_num = item.get('q_num', i + 1)
                        q_type = st.selectbox(f"Q{q_num} Type", ["MCQ", "True/False", "Fill in the Blanks", "One Word / Short", "Match the Column"], index=["MCQ", "True/False", "Fill in the Blanks", "One Word / Short", "Match the Column"].index(item.get("q_type", "MCQ")), key=f"obj_type_{i}")
                        q_text = st.text_input(f"Q{q_num} Question Text", value=item.get('question', ''), key=f"obj_q_{i}")
                        options = st.text_input(f"Q{q_num} Options / Column Ref", value=item.get('options', ''), key=f"obj_opt_{i}")
                    with c2:
                        ans = st.text_input(f"Q{q_num} Correct Answer Key", value=item.get('correct_answer', ''), key=f"obj_ans_{i}")
                        max_m = st.number_input(f"Q{q_num} Marks", min_value=0.5, max_value=10.0, value=float(item.get('max_marks', 1.0)), key=f"obj_marks_{i}")
                        neg_m = st.number_input(f"Q{q_num} Negative Marks", min_value=0.0, max_value=5.0, value=float(item.get('negative_marks', 0.0)), step=0.25, key=f"obj_neg_{i}")

                    updated_obj.append({"q_num": q_num, "q_type": q_type, "question": q_text, "correct_answer": ans, "options": options, "max_marks": max_m, "negative_marks": neg_m})

            st.session_state["objective_scheme"] = updated_obj

    # TAB 2: Objective Student Sheet Input
    with tab2:
        st.subheader("📄 Student Answer Sheet (Objective Mode)")
        obj_input_mode = st.radio("Input Method:", ["Upload Answer Sheet (Image / PDF / DOCX)", "📸 Capture via Connected IP Camera", "Type / Paste Answers / Written Format"], horizontal=True, key="obj_input_mode")

        if obj_input_mode == "📸 Capture via Connected IP Camera":
            st.info(f"Connected to IP Camera: **{st.session_state['camera_name']}** (`{st.session_state['camera_ip']}`)")
            c1, c2 = st.columns([2, 1])
            with c1:
                target_r = st.text_input("Student Roll No", value=st.session_state["student_info"]["roll_no"], key="tab2_obj_roll")
            with c2:
                st.write("")
                st.write("")
                if st.button("📸 Snap Picture from IP Camera", type="primary", use_container_width=True, key="tab2_obj_cam_btn"):
                    with st.spinner("Capturing frame, enhancing contrast & running auto-header OCR..."):
                        cap_res = CameraService.capture_snapshot(st.session_state["camera_ip"], target_r)
                        if cap_res.get("status") == "success":
                            img_bytes = OCRService.enhance_image_for_ocr(cap_res["image_bytes"])
                            st.session_state["captured_camera_image"] = img_bytes
                            ocr_res = OCRService.extract_from_image(img_bytes)
                            st.session_state["objective_student_text"] = ocr_res.get("text", "")

                            hdr = OCRService.parse_student_header(ocr_res.get("text", ""))
                            if hdr["has_detected"]:
                                st.session_state["student_info"]["roll_no"] = hdr["roll_no"]
                                st.session_state["student_info"]["name"] = hdr["name"]
                                st.success(f"🔍 Auto-Detected Header! Roll No: {hdr['roll_no']} | Name: {hdr['name']}")
                            else:
                                st.success("✅ Snapshot captured and OCR extracted!")

            if st.session_state["captured_camera_image"]:
                st.image(st.session_state["captured_camera_image"], caption="Captured Objective Sheet Photo", width=500)
            st.text_area("Extracted Objective Sheet Content:", value=st.session_state["objective_student_text"], height=200, key="obj_cam_text_preview")

        elif obj_input_mode == "Upload Answer Sheet (Image / PDF / DOCX)":
            uploaded_obj = st.file_uploader("Upload OMR / Objective Answer Sheet", type=["png", "jpg", "jpeg", "pdf", "docx", "doc"], key="obj_sheet_uploader")
            if uploaded_obj is not None:
                bytes_data = uploaded_obj.read()
                filename = uploaded_obj.name.lower()
                if filename.endswith(".docx") or filename.endswith(".doc"):
                    ocr_res = OCRService.extract_from_docx(bytes_data)
                elif filename.endswith(".pdf"):
                    with open("temp_obj_sheet.pdf", "wb") as f: f.write(bytes_data)
                    ocr_res = OCRService.extract_from_pdf("temp_obj_sheet.pdf")
                else:
                    bytes_data = OCRService.enhance_image_for_ocr(bytes_data)
                    ocr_res = OCRService.extract_from_image(bytes_data)

                extracted_obj_text = ocr_res.get("text", "")
                hdr = OCRService.parse_student_header(extracted_obj_text)
                if hdr["has_detected"]:
                    st.session_state["student_info"]["roll_no"] = hdr["roll_no"]
                    st.session_state["student_info"]["name"] = hdr["name"]

                st.session_state["objective_student_text"] = extracted_obj_text
                st.text_area("Extracted Objective Sheet Text:", value=extracted_obj_text, height=200, key="obj_ocr_area")
            else:
                st.text_area("Current Objective Text Preview:", value=st.session_state["objective_student_text"], height=180, disabled=True, key="obj_preview")
        else:
            pasted_obj = st.text_area("Type / Paste Objective Answers (written format):", value=st.session_state["objective_student_text"], height=250, key="obj_pasted")
            st.session_state["objective_student_text"] = pasted_obj

        st.divider()

        if st.button("🚀 Evaluate Objective Sheet & Generate Scorecard", type="primary", use_container_width=True, key="obj_eval_btn"):
            raw_text = st.session_state["objective_student_text"]
            scheme = st.session_state["objective_scheme"]
            parsed_answers = OCRService.parse_answers_by_question(raw_text)

            evaluations = []
            total_obtained = 0.0
            total_max = 0.0
            correct_cnt = 0
            wrong_cnt = 0
            unatt_cnt = 0

            for item in scheme:
                q_num = item["q_num"]
                s_ans = parsed_answers.get(q_num, "")

                if not s_ans and raw_text:
                    lines = [l for l in raw_text.split('\n') if l.strip()]
                    s_ans = lines[q_num - 1] if len(lines) >= q_num else ""

                res = evaluate_objective_answer(
                    student_text=s_ans,
                    correct_answer=item["correct_answer"],
                    q_type=item["q_type"],
                    max_marks=float(item["max_marks"]),
                    negative_marks=float(item["negative_marks"])
                )

                res["q_num"] = q_num
                res["q_type"] = item["q_type"]
                res["question"] = item["question"]
                res["correct_answer"] = item["correct_answer"]
                res["student_text"] = s_ans
                res["max_marks"] = float(item["max_marks"])

                if res["status"] == "Correct": correct_cnt += 1
                elif res["status"] == "Incorrect": wrong_cnt += 1
                else: unatt_cnt += 1

                total_obtained += res["marks"]
                total_max += float(item["max_marks"])
                evaluations.append(res)

            accuracy = (total_obtained / max(total_max, 1.0)) * 100.0

            st.session_state["objective_results"] = {
                "evaluations": evaluations, "total_obtained": max(0.0, total_obtained), "total_max": total_max,
                "accuracy": max(0.0, accuracy), "correct_cnt": correct_cnt, "wrong_cnt": wrong_cnt, "unatt_cnt": unatt_cnt
            }
            st.success("✅ Objective sheet evaluated! Switch to 'Scorecard & Report Card' tab.")

    # TAB 3: Objective Scorecard
    with tab3:
        obj_eval = st.session_state["objective_results"]
        student_info = st.session_state["student_info"]

        if obj_eval is None:
            st.info("💡 Go to Tab 2 and click **'Evaluate Objective Sheet'**.")
        else:
            total_obtained = obj_eval["total_obtained"]
            total_max = obj_eval["total_max"]
            accuracy = obj_eval["accuracy"]
            evaluations = obj_eval["evaluations"]

            st.markdown(f"""
            <div style="background-color:#F0FDF4; border: 1px solid #BBF7D0; padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;">
                <h3 style="margin: 0; color: #166534;">🎯 Objective Exam Scorecard: {student_info['name']}</h3>
                <p style="margin: 0.3rem 0 0 0; color: #15803D;"><b>Roll No:</b> {student_info['roll_no']} | <b>Subject:</b> {student_info['subject']} | <b>Exam:</b> {student_info['exam']}</p>
            </div>
            """, unsafe_allow_html=True)

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Score", f"{total_obtained:.1f} / {total_max:.1f}")
            m2.metric("Accuracy (%)", f"{accuracy:.1f}%")
            m3.metric("Correct ✅", f"{obj_eval['correct_cnt']}")
            m4.metric("Incorrect ❌", f"{obj_eval['wrong_cnt']}")
            m5.metric("Unattempted ⚪", f"{obj_eval['unatt_cnt']}")

            st.progress(min(1.0, max(0.0, accuracy / 100.0)))
            st.divider()

            table_rows = []
            for ev in evaluations:
                status_icon = "✅ Correct" if ev["status"] == "Correct" else ("❌ Incorrect" if ev["status"] == "Incorrect" else "⚪ Unattempted")
                table_rows.append({
                    "Q#": ev["q_num"], "Type": ev["q_type"], "Question": ev["question"],
                    "Student Answer": ev["student_text"] if ev["student_text"] else "-",
                    "Correct Answer Key": ev["correct_answer"], "Result": status_icon, "Marks": f"{ev['marks']:.1f} / {ev['max_marks']:.1f}"
                })

            st.dataframe(table_rows, use_container_width=True)

# ==============================================================================
# TAB 4: CLASS BATCH ANALYTICS & PLAGIARISM MATRIX 🏆
# ==============================================================================
with tab4:
    st.subheader("🏆 Class Batch Evaluation & Plagiarism Similarity Matrix")
    st.caption("Evaluate multiple student answer sheets, rank top performers, and detect copied/plagiarized student answers.")

    col_b1, col_b2 = st.columns([1, 1])

    with col_b1:
        st.markdown("**Class Student Batch List:**")
        batch_items = st.session_state["class_batch_data"]
        st.write(f"Total Students in Batch: **{len(batch_items)}**")

    with col_b2:
        if st.button("⚡ Run Full Class Batch Evaluation & Plagiarism Check", type="primary", use_container_width=True, key="run_batch_btn"):
            scheme = st.session_state["descriptive_scheme"]
            batch_results = []
            q_accuracy_map = {item["q_num"]: 0 for item in scheme}

            for student in batch_items:
                raw_text = student["answers_text"]
                parsed_answers = OCRService.parse_answers_by_question(raw_text)

                s_obtained = 0.0
                s_max = 0.0

                for item in scheme:
                    q_num = item["q_num"]
                    student_ans = parsed_answers.get(q_num, "")
                    if not student_ans and raw_text:
                        lines = [l for l in raw_text.split('\n') if l.strip()]
                        student_ans = lines[q_num - 1] if len(lines) >= q_num else raw_text

                    concepts_list = [c.strip() for c in item["key_concepts"].split(",") if c.strip()]
                    max_m = float(item["max_marks"])

                    res = AIEvaluator.evaluate_answer(
                        student_text=student_ans,
                        model_answer=item["model_answer"],
                        key_concepts=concepts_list,
                        max_marks=max_m,
                        question_text=item.get("question", ""),
                        model_name=st.session_state.get("ollama_model_name", "llama3"),
                        endpoint=st.session_state.get("ollama_endpoint", "http://localhost:11434")
                    )
                    s_obtained += res["suggested_marks"]
                    s_max += max_m

                    if (res["suggested_marks"] / max(max_m, 1.0)) >= 0.7:
                        q_accuracy_map[q_num] += 1

                acc = (s_obtained / max(s_max, 1.0)) * 100.0
                grade = "A+ (Outstanding)" if acc >= 85 else ("A (Very Good)" if acc >= 75 else ("B (Good)" if acc >= 60 else "C (Pass)"))
                status = "PASS ✅" if acc >= 50 else "REMEDIAL NEEDED ⚠️"

                batch_results.append({
                    "Roll No": student["roll_no"],
                    "Student Name": student["name"],
                    "Score": f"{s_obtained:.1f} / {s_max:.1f}",
                    "Accuracy (%)": round(acc, 1),
                    "Grade": grade,
                    "Status": status,
                    "raw_acc": acc
                })

            # Sort by Accuracy desc
            batch_results = sorted(batch_results, key=lambda x: x["raw_acc"], reverse=True)
            for idx, r in enumerate(batch_results):
                r["Rank"] = f"#{idx + 1}"

            # Calculate Plagiarism Matrix
            plagiarism_matrix = OCRService.compute_plagiarism_similarity_matrix(batch_items)

            st.session_state["class_batch_results"] = {
                "results": batch_results,
                "q_accuracy": q_accuracy_map,
                "plagiarism_matrix": plagiarism_matrix
            }
            st.success("✅ Class evaluation and anti-plagiarism check complete!")

    # Display Class Leaderboard & Metrics
    if st.session_state["class_batch_results"] is not None:
        batch_res = st.session_state["class_batch_results"]["results"]
        q_map = st.session_state["class_batch_results"]["q_accuracy"]
        plag_matrix = st.session_state["class_batch_results"].get("plagiarism_matrix", [])

        st.divider()

        # Class Metrics Row
        total_students = len(batch_res)
        avg_acc = sum([r["raw_acc"] for r in batch_res]) / max(total_students, 1)
        topper = batch_res[0]
        pass_rate = (sum([1 for r in batch_res if "PASS" in r["Status"]]) / max(total_students, 1)) * 100

        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        with c_m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-accent" style="background: linear-gradient(90deg, #3B82F6, #1D4ED8);"></div>
                <div class="metric-label">Class Size</div>
                <div class="metric-value" style="color:#1D4ED8;">{total_students} <span style="font-size:1.1rem; color:#64748B;">Students</span></div>
            </div>
            """, unsafe_allow_html=True)

        with c_m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-accent" style="background: linear-gradient(90deg, #10B981, #047857);"></div>
                <div class="metric-label">Class Average</div>
                <div class="metric-value" style="color:#047857;">{avg_acc:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with c_m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-accent" style="background: linear-gradient(90deg, #F59E0B, #D97706);"></div>
                <div class="metric-label">Class Topper 🥇</div>
                <div class="metric-value" style="color:#D97706; font-size:1.3rem; margin-top:0.6rem;">{topper['Student Name']} ({topper['Accuracy (%)']}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with c_m4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-accent" style="background: linear-gradient(90deg, #8B5CF6, #6D28D9);"></div>
                <div class="metric-label">Pass Rate</div>
                <div class="metric-value" style="color:#6D28D9;">{pass_rate:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.subheader("🥇 Class Leaderboard")
        df_leaderboard = pd.DataFrame(batch_res)[["Rank", "Roll No", "Student Name", "Score", "Accuracy (%)", "Grade", "Status"]]
        st.dataframe(df_leaderboard, use_container_width=True)

        st.divider()

        # Plagiarism Similarity Matrix Table
        st.subheader("🕵️‍♂️ Class Answer Plagiarism & Copying Detector Matrix")
        if plag_matrix:
            df_plag = pd.DataFrame(plag_matrix)
            st.dataframe(df_plag, use_container_width=True)
        else:
            st.info("No plagiarism overlap detected across student answers.")

        st.divider()

        # Question Difficulty Analytics
        st.subheader("📈 Question Difficulty Insights")
        diff_data = []
        for q_num, cnt in q_map.items():
            pct = (cnt / max(total_students, 1)) * 100
            diff_level = "Easy ✅" if pct >= 75 else ("Moderate ⚠️" if pct >= 50 else "Hard 🔴 (Needs Revision)")
            diff_data.append({
                "Question #": f"Q{q_num}",
                "Students Mastered (%)": f"{pct:.0f}%",
                "Difficulty Level": diff_level
            })
        st.dataframe(diff_data, use_container_width=True)

        st.divider()

        # Export Class Results to CSV
        csv_data = df_leaderboard.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Class Leaderboard Report (.csv)",
            data=csv_data,
            file_name="Class_Leaderboard_Report.csv",
            mime="text/csv",
            use_container_width=True
        )
