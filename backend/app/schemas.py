from typing import List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    role: Optional[str] = None

class QuestionOut(BaseModel):
    id: int
    question_number: int
    question_text: str
    max_marks: float
    model_answer: str
    key_concepts: List[str]
    rubric: Optional[dict] = None

    class Config:
        from_attributes = True

class QuestionEvaluationOut(BaseModel):
    id: int
    question_id: int
    question_number: int
    question_text: str
    max_marks: float
    student_answer_ocr: Optional[str] = None
    page_number: int = 1
    ai_suggested_marks: Optional[float] = None
    ai_confidence: Optional[float] = None
    detected_concepts: List[str] = []
    missing_concepts: List[str] = []
    ai_explanation: Optional[str] = None
    examiner_marks: Optional[float] = None
    examiner_comments: Optional[str] = None
    is_ai_accepted: bool = False
    status: str = "unchecked"

    class Config:
        from_attributes = True

class QuestionEvaluationUpdate(BaseModel):
    examiner_marks: float
    examiner_comments: Optional[str] = None
    is_ai_accepted: bool = False
    student_answer_ocr: Optional[str] = None

class AnomalyFlagOut(BaseModel):
    id: int
    answer_sheet_id: int
    student_roll: Optional[str] = None
    student_name: Optional[str] = None
    question_id: Optional[int] = None
    question_number: Optional[int] = None
    flag_type: str
    severity: str
    details: str
    ai_score: Optional[float] = None
    examiner_score: Optional[float] = None
    resolved: bool = False
    moderator_id: Optional[int] = None
    moderator_notes: Optional[str] = None
    final_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AnomalyResolveRequest(BaseModel):
    moderator_id: int
    moderator_notes: str
    final_score: float

class AIStudentSummaryOut(BaseModel):
    strengths: List[str]
    weak_areas: List[str]
    overall_summary: str
    recommended_grade: str

    class Config:
        from_attributes = True

class AnswerSheetListItem(BaseModel):
    id: int
    exam_id: int
    exam_title: str
    student_roll: str
    student_name: str
    pages: int
    status: str
    total_score: Optional[float] = None
    ai_total_score: Optional[float] = None
    max_total_marks: float
    time_spent_seconds: int = 0
    assigned_examiner_name: Optional[str] = None
    has_anomalies: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class AnswerSheetDetail(BaseModel):
    id: int
    exam_id: int
    exam_title: str
    exam_subject: str
    exam_code: str
    student_roll: str
    student_name: str
    file_path: str
    pages: int
    status: str
    assigned_examiner_id: Optional[int] = None
    total_score: Optional[float] = None
    ai_total_score: Optional[float] = None
    max_total_marks: float
    time_spent_seconds: int = 0
    evaluations: List[QuestionEvaluationOut]
    anomalies: List[AnomalyFlagOut] = []
    ai_summary: Optional[AIStudentSummaryOut] = None

    class Config:
        from_attributes = True

class UncheckedItem(BaseModel):
    question_id: int
    question_number: int
    has_ocr_text: bool
    status: str

class UncheckedCheckResponse(BaseModel):
    can_submit: bool
    unchecked_count: int
    unchecked_questions: List[UncheckedItem]
    message: str

class AnswerSheetSubmitRequest(BaseModel):
    time_spent_seconds: int
    force_submit: bool = False

class ExaminerAnalytics(BaseModel):
    total_papers: int
    completed_papers: int
    pending_papers: int
    moderation_papers: int
    average_score: float
    average_time_seconds: int
    ai_acceptance_rate: float
    anomaly_rate: float
    score_distribution: List[dict]
    recent_evaluations: List[dict]

class OCRRequest(BaseModel):
    image_base64: Optional[str] = None
    page_number: int = 1

class OCRResponse(BaseModel):
    extracted_text: str
    confidence: float
    source: str
