import os
import json
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import engine, get_db, active_db_type
from .models import User, Exam, Question, AnswerSheet, QuestionEvaluation, AnomalyFlag, AIStudentSummary
from .schemas import (
    UserOut, UserLogin, AnswerSheetListItem, AnswerSheetDetail, QuestionEvaluationOut,
    QuestionEvaluationUpdate, UncheckedCheckResponse, AnswerSheetSubmitRequest,
    AnomalyFlagOut, AnomalyResolveRequest, ExaminerAnalytics, OCRResponse, AIStudentSummaryOut
)
from .ai_evaluator import AIEvaluator
from .anomaly_service import AnomalyService
from .ocr_service import OCRService
from .camera_service import CameraService
from .seed_data import seed_database

import create_aiml_docx

logger = logging.getLogger("ai_osm.api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI-OSM API",
    description="AI-Powered On-Screen Marking Backend with Automated Evaluation & Anomaly Detection",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads
uploads_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(uploads_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

@app.get("/api/generate-aiml-docx")
def api_generate_aiml_docx():
    import create_aiml_docx
    create_aiml_docx.build_all_docx()
    return {"status": "success", "message": "DOCX files generated"}

@app.on_event("startup")
def on_startup():
    logger.info(f"AI-OSM Backend initialized with database: {active_db_type}")
    try:
        seed_database()
    except Exception as e:
        logger.error(f"Startup seeding check: {e}")

@app.get("/")
def root():
    return {
        "app": "AI-OSM On-Screen Marking API",
        "status": "online",
        "database": active_db_type,
        "docs_url": "/docs"
    }

# ================= AUTH & USER MANAGEMENT =================

@app.get("/api/auth/users", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/api/auth/login", response_model=UserOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=payload.email).first()
    if not user:
        # Fallback to role if provided
        if payload.role:
            user = db.query(User).filter_by(role=payload.role).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ================= ANSWER SHEETS =================

@app.get("/api/sheets", response_model=List[AnswerSheetListItem])
def list_answer_sheets(
    status: Optional[str] = None,
    examiner_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AnswerSheet)
    if status:
        query = query.filter(AnswerSheet.status == status)
    if examiner_id:
        query = query.filter(AnswerSheet.assigned_examiner_id == examiner_id)

    sheets = query.order_by(AnswerSheet.id.asc()).all()
    results = []

    for s in sheets:
        max_marks = sum(q.max_marks for q in s.exam.questions) if s.exam else 50.0
        has_anom = any(not a.resolved for a in s.anomalies)
        ex_name = s.assigned_examiner.name if s.assigned_examiner else "Unassigned"

        results.append(AnswerSheetListItem(
            id=s.id,
            exam_id=s.exam_id,
            exam_title=s.exam.title if s.exam else "Examination",
            student_roll=s.student_roll,
            student_name=s.student_name,
            pages=s.pages,
            status=s.status,
            total_score=s.total_score,
            ai_total_score=s.ai_total_score,
            max_total_marks=max_marks,
            time_spent_seconds=s.time_spent_seconds,
            assigned_examiner_name=ex_name,
            has_anomalies=has_anom,
            created_at=s.created_at
        ))

    return results

@app.get("/api/sheets/{sheet_id}", response_model=AnswerSheetDetail)
def get_answer_sheet(sheet_id: int, db: Session = Depends(get_db)):
    sheet = db.query(AnswerSheet).filter_by(id=sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Answer sheet not found")

    exam = sheet.exam
    max_marks = sum(q.max_marks for q in exam.questions) if exam else 50.0

    # Build evaluations list
    eval_outs = []
    for ev in sorted(sheet.evaluations, key=lambda x: x.question.question_number if x.question else 0):
        det_c = json.loads(ev.detected_concepts) if ev.detected_concepts else []
        mis_c = json.loads(ev.missing_concepts) if ev.missing_concepts else []
        
        eval_outs.append(QuestionEvaluationOut(
            id=ev.id,
            question_id=ev.question_id,
            question_number=ev.question.question_number if ev.question else 0,
            question_text=ev.question.question_text if ev.question else "",
            max_marks=ev.question.max_marks if ev.question else 10.0,
            student_answer_ocr=ev.student_answer_ocr,
            page_number=ev.page_number,
            ai_suggested_marks=ev.ai_suggested_marks,
            ai_confidence=ev.ai_confidence,
            detected_concepts=det_c,
            missing_concepts=mis_c,
            ai_explanation=ev.ai_explanation,
            examiner_marks=ev.examiner_marks,
            examiner_comments=ev.examiner_comments,
            is_ai_accepted=ev.is_ai_accepted,
            status=ev.status
        ))

    # Anomalies
    anom_outs = []
    for a in sheet.anomalies:
        anom_outs.append(AnomalyFlagOut(
            id=a.id,
            answer_sheet_id=a.answer_sheet_id,
            student_roll=sheet.student_roll,
            student_name=sheet.student_name,
            question_id=a.question_id,
            question_number=a.question.question_number if a.question else None,
            flag_type=a.flag_type,
            severity=a.severity,
            details=a.details,
            ai_score=a.ai_score,
            examiner_score=a.examiner_score,
            resolved=a.resolved,
            moderator_id=a.moderator_id,
            moderator_notes=a.moderator_notes,
            final_score=a.final_score,
            created_at=a.created_at
        ))

    # AI Summary
    summary_out = None
    if sheet.ai_summary:
        summary_out = AIStudentSummaryOut(
            strengths=json.loads(sheet.ai_summary.strengths) if sheet.ai_summary.strengths else [],
            weak_areas=json.loads(sheet.ai_summary.weak_areas) if sheet.ai_summary.weak_areas else [],
            overall_summary=sheet.ai_summary.overall_summary,
            recommended_grade=sheet.ai_summary.recommended_grade
        )

    return AnswerSheetDetail(
        id=sheet.id,
        exam_id=sheet.exam_id,
        exam_title=exam.title if exam else "",
        exam_subject=exam.subject if exam else "",
        exam_code=exam.code if exam else "",
        student_roll=sheet.student_roll,
        student_name=sheet.student_name,
        file_path=sheet.file_path,
        pages=sheet.pages,
        status=sheet.status,
        assigned_examiner_id=sheet.assigned_examiner_id,
        total_score=sheet.total_score,
        ai_total_score=sheet.ai_total_score,
        max_total_marks=max_marks,
        time_spent_seconds=sheet.time_spent_seconds,
        evaluations=eval_outs,
        anomalies=anom_outs,
        ai_summary=summary_out
    )

# ================= EVALUATION WORKFLOW =================

@app.post("/api/sheets/{sheet_id}/evaluate/{question_id}")
def update_question_evaluation(
    sheet_id: int,
    question_id: int,
    payload: QuestionEvaluationUpdate,
    db: Session = Depends(get_db)
):
    ev = db.query(QuestionEvaluation).filter_by(
        answer_sheet_id=sheet_id,
        question_id=question_id
    ).first()

    if not ev:
        raise HTTPException(status_code=404, detail="Question evaluation record not found")

    ev.examiner_marks = payload.examiner_marks
    ev.examiner_comments = payload.examiner_comments
    ev.is_ai_accepted = payload.is_ai_accepted
    ev.status = "evaluated"

    if payload.student_answer_ocr:
        ev.student_answer_ocr = payload.student_answer_ocr

    db.commit()

    # Recalculate sheet running total
    sheet = db.query(AnswerSheet).filter_by(id=sheet_id).first()
    scored = [e.examiner_marks for e in sheet.evaluations if e.examiner_marks is not None]
    if scored:
        sheet.total_score = sum(scored)
        if sheet.status == "pending":
            sheet.status = "in_progress"
        db.commit()

    return {"message": "Question evaluated successfully", "examiner_marks": ev.examiner_marks}

@app.get("/api/sheets/{sheet_id}/unchecked-check", response_model=UncheckedCheckResponse)
def check_unchecked_answers(sheet_id: int, db: Session = Depends(get_db)):
    sheet = db.query(AnswerSheet).filter_by(id=sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Answer sheet not found")

    res = AnomalyService.check_unchecked_answers(sheet, sheet.evaluations)
    return UncheckedCheckResponse(**res)

@app.post("/api/sheets/{sheet_id}/submit")
def submit_evaluation(
    sheet_id: int,
    payload: AnswerSheetSubmitRequest,
    db: Session = Depends(get_db)
):
    sheet = db.query(AnswerSheet).filter_by(id=sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Answer sheet not found")

    # 1. Unchecked Answer Detection
    if not payload.force_submit:
        unchecked_res = AnomalyService.check_unchecked_answers(sheet, sheet.evaluations)
        if not unchecked_res["can_submit"]:
            return {
                "success": False,
                "blocked": True,
                "reason": "unchecked_answers",
                "details": unchecked_res
            }

    # 2. Run Anomaly Detection
    flags = AnomalyService.detect_anomalies(
        db=db,
        sheet=sheet,
        evaluations=sheet.evaluations,
        time_spent_seconds=payload.time_spent_seconds
    )

    # 3. Generate AI Overall Summary
    eval_dicts = []
    for ev in sheet.evaluations:
        eval_dicts.append({
            "detected_concepts": ev.detected_concepts,
            "missing_concepts": ev.missing_concepts
        })

    max_marks = sum(q.max_marks for q in sheet.exam.questions) if sheet.exam else 50.0
    summary_data = AIEvaluator.generate_overall_summary(
        evaluations=eval_dicts,
        total_score=sheet.total_score or 0.0,
        max_total_marks=max_marks
    )

    # Save AI summary
    if sheet.ai_summary:
        sheet.ai_summary.strengths = json.dumps(summary_data["strengths"])
        sheet.ai_summary.weak_areas = json.dumps(summary_data["weak_areas"])
        sheet.ai_summary.overall_summary = summary_data["overall_summary"]
        sheet.ai_summary.recommended_grade = summary_data["recommended_grade"]
    else:
        new_summary = AIStudentSummary(
            answer_sheet_id=sheet.id,
            strengths=json.dumps(summary_data["strengths"]),
            weak_areas=json.dumps(summary_data["weak_areas"]),
            overall_summary=summary_data["overall_summary"],
            recommended_grade=summary_data["recommended_grade"]
        )
        db.add(new_summary)

    db.commit()

    return {
        "success": True,
        "blocked": False,
        "status": sheet.status,
        "total_score": sheet.total_score,
        "anomalies_detected": len(flags),
        "flags": [f.details for f in flags],
        "summary": summary_data
    }

# ================= MODERATION WORKFLOW =================

@app.get("/api/moderation/cases", response_model=List[AnomalyFlagOut])
def get_moderation_cases(db: Session = Depends(get_db)):
    flags = db.query(AnomalyFlag).filter_by(resolved=False).order_by(AnomalyFlag.created_at.desc()).all()
    results = []
    for f in flags:
        sheet = f.answer_sheet
        results.append(AnomalyFlagOut(
            id=f.id,
            answer_sheet_id=f.answer_sheet_id,
            student_roll=sheet.student_roll if sheet else "",
            student_name=sheet.student_name if sheet else "",
            question_id=f.question_id,
            question_number=f.question.question_number if f.question else None,
            flag_type=f.flag_type,
            severity=f.severity,
            details=f.details,
            ai_score=f.ai_score,
            examiner_score=f.examiner_score,
            resolved=f.resolved,
            moderator_id=f.moderator_id,
            moderator_notes=f.moderator_notes,
            final_score=f.final_score,
            created_at=f.created_at
        ))
    return results

@app.post("/api/moderation/{sheet_id}/resolve")
def resolve_moderation_case(
    sheet_id: int,
    payload: AnomalyResolveRequest,
    db: Session = Depends(get_db)
):
    sheet = db.query(AnswerSheet).filter_by(id=sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Answer sheet not found")

    # Mark flags resolved
    for f in sheet.anomalies:
        f.resolved = True
        f.moderator_id = payload.moderator_id
        f.moderator_notes = payload.moderator_notes
        f.final_score = payload.final_score

    sheet.total_score = payload.final_score
    sheet.status = "completed"
    sheet.moderated_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": f"Answer sheet {sheet.student_roll} successfully moderated with final score {payload.final_score:.1f}",
        "final_score": sheet.total_score,
        "status": sheet.status
    }

# ================= ANALYTICS =================

@app.get("/api/analytics/examiner", response_model=ExaminerAnalytics)
def get_examiner_analytics(examiner_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(AnswerSheet)
    if examiner_id:
        query = query.filter(AnswerSheet.assigned_examiner_id == examiner_id)

    sheets = query.all()
    total = len(sheets)
    completed = sum(1 for s in sheets if s.status == "completed")
    pending = sum(1 for s in sheets if s.status in ("pending", "in_progress"))
    moderation = sum(1 for s in sheets if s.status == "flagged_moderation")

    completed_sheets = [s for s in sheets if s.total_score is not None]
    avg_score = round(sum(s.total_score for s in completed_sheets) / len(completed_sheets), 1) if completed_sheets else 0.0
    avg_time = int(sum(s.time_spent_seconds for s in completed_sheets) / len(completed_sheets)) if completed_sheets else 90

    # Calculate AI acceptance rate
    all_evals = db.query(QuestionEvaluation).all()
    ai_accepted_count = sum(1 for e in all_evals if e.is_ai_accepted)
    ai_acc_rate = round((ai_accepted_count / max(len(all_evals), 1)) * 100, 1)

    # Anomaly rate
    total_anoms = db.query(AnomalyFlag).count()
    anom_rate = round((total_anoms / max(total, 1)) * 100, 1)

    # Score distribution bands
    distribution = [
        {"range": "0-20", "count": sum(1 for s in completed_sheets if s.total_score < 20)},
        {"range": "21-30", "count": sum(1 for s in completed_sheets if 20 <= s.total_score <= 30)},
        {"range": "31-40", "count": sum(1 for s in completed_sheets if 30 < s.total_score <= 40)},
        {"range": "41-50", "count": sum(1 for s in completed_sheets if s.total_score > 40)},
    ]

    recent = [
        {
            "roll": s.student_roll,
            "name": s.student_name,
            "score": s.total_score,
            "status": s.status,
            "time_spent": f"{s.time_spent_seconds}s"
        }
        for s in sheets[:5]
    ]

    return ExaminerAnalytics(
        total_papers=total,
        completed_papers=completed,
        pending_papers=pending,
        moderation_papers=moderation,
        average_score=avg_score,
        average_time_seconds=avg_time,
        ai_acceptance_rate=ai_acc_rate,
        anomaly_rate=anom_rate,
        score_distribution=distribution,
        recent_evaluations=recent
    )

# ================= OCR DIRECT & UPLOAD =================

@app.post("/api/ocr/extract", response_model=OCRResponse)
async def direct_ocr_extract(file: UploadFile = File(...)):
    content = await file.read()
    res = OCRService.extract_from_image(content)
    return OCRResponse(
        extracted_text=res["text"],
        confidence=res["confidence"],
        source=res["source"]
    )

@app.post("/api/sheets/upload")
async def upload_new_answer_sheet(
    student_roll: str = Form(...),
    student_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    exam = db.query(Exam).first()
    if not exam:
        raise HTTPException(status_code=400, detail="No exam found to attach sheet to")

    filename = f"sheet_{student_roll.lower().replace('-', '_')}_{file.filename}"
    save_path = os.path.join(uploads_path, filename)

    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    # Perform OCR extraction on the sheet
    ocr_res = OCRService.extract_from_image(contents)
    extracted_text = ocr_res["text"]

    examiner = db.query(User).filter_by(role="examiner").first()

    # Create new AnswerSheet
    sheet = AnswerSheet(
        exam_id=exam.id,
        student_roll=student_roll,
        student_name=student_name,
        file_path=f"/uploads/{filename}",
        pages=1,
        status="pending",
        assigned_examiner_id=examiner.id if examiner else None
    )
    db.add(sheet)
    db.flush()

    # Populate question evaluations with AI suggestions
    questions = db.query(Question).filter_by(exam_id=exam.id).order_by(Question.question_number).all()
    for q in questions:
        eval_data = AIEvaluator.evaluate_answer(
            student_text=extracted_text,
            model_answer=q.model_answer,
            key_concepts=json.loads(q.key_concepts),
            max_marks=q.max_marks
        )
        qe = QuestionEvaluation(
            answer_sheet_id=sheet.id,
            question_id=q.id,
            student_answer_ocr=extracted_text,
            ai_suggested_marks=eval_data["suggested_marks"],
            ai_confidence=eval_data["confidence"],
            detected_concepts=json.dumps(eval_data["detected_concepts"]),
            missing_concepts=json.dumps(eval_data["missing_concepts"]),
            ai_explanation=eval_data["ai_explanation"],
            examiner_marks=None,
            is_ai_accepted=False,
            status="unchecked"
        )
        db.add(qe)

    db.commit()
    return {
        "success": True,
        "sheet_id": sheet.id,
        "message": f"Answer sheet for {student_name} ({student_roll}) uploaded and OCR processed successfully!"
    }


# ================= CAMERA CONNECTIVITY & MASTER KEY API =================

@app.post("/api/camera/test")
def test_camera_connection(camera_ip: str = Form(...)):
    """
    Test connectivity to an IP camera or webcam.
    """
    return CameraService.test_connection(camera_ip)


@app.post("/api/camera/capture")
async def capture_from_ip_camera(
    camera_ip: str = Form(...),
    student_roll: str = Form("STU-2026"),
    student_name: str = Form("Student")
):
    """
    Capture student answer sheet directly from connected IP camera or webcam.
    """
    cap_res = CameraService.capture_snapshot(camera_ip, student_roll)
    if cap_res.get("status") != "success":
        raise HTTPException(status_code=400, detail="Failed to capture photo from camera.")

    img_bytes = cap_res["image_bytes"]
    filename = f"camera_{student_roll.lower().replace('-', '_')}_{int(datetime.now().timestamp())}.jpg"
    save_path = os.path.join(uploads_path, filename)
    with open(save_path, "wb") as f:
        f.write(img_bytes)

    # Perform OCR
    ocr_res = OCRService.extract_from_image(img_bytes)

    return {
        "success": True,
        "student_roll": student_roll,
        "student_name": student_name,
        "camera_source": cap_res.get("source"),
        "timestamp": cap_res.get("timestamp"),
        "extracted_text": ocr_res.get("text"),
        "file_url": f"/uploads/{filename}"
    }


@app.post("/api/master-key/upload")
async def upload_master_key(
    file: UploadFile = File(...)
):
    """
    Upload master answer key in PDF, DOCX, TXT, Written format, or Image.
    """
    contents = await file.read()
    parsed = OCRService.parse_master_key_file(contents, file.filename)
    return {
        "success": True,
        "filename": file.filename,
        "source": parsed["source"],
        "scheme": parsed["scheme"],
        "raw_text": parsed["raw_text"]
    }

