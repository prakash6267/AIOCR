import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    role = Column(String(50), nullable=False, default="examiner")  # admin, examiner, moderator
    avatar = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    subject = Column(String(120), nullable=False)
    total_marks = Column(Float, default=50.0)
    passing_marks = Column(Float, default=20.0)
    instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    answer_sheets = relationship("AnswerSheet", back_populates="exam")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    max_marks = Column(Float, nullable=False, default=10.0)
    model_answer = Column(Text, nullable=False)
    key_concepts = Column(Text, nullable=False)  # JSON list of concepts
    rubric = Column(Text, nullable=True)        # JSON criteria breakdown

    exam = relationship("Exam", back_populates="questions")
    evaluations = relationship("QuestionEvaluation", back_populates="question")

class AnswerSheet(Base):
    __tablename__ = "answer_sheets"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_roll = Column(String(100), nullable=False)
    student_name = Column(String(120), nullable=False)
    file_path = Column(String(255), nullable=False)
    pages = Column(Integer, default=1)
    status = Column(String(50), default="pending")  # pending, in_progress, evaluated, flagged_moderation, moderated, approved
    assigned_examiner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    total_score = Column(Float, nullable=True)
    ai_total_score = Column(Float, nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    submitted_at = Column(DateTime, nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    exam = relationship("Exam", back_populates="answer_sheets")
    assigned_examiner = relationship("User", foreign_keys=[assigned_examiner_id])
    evaluations = relationship("QuestionEvaluation", back_populates="answer_sheet", cascade="all, delete-orphan")
    anomalies = relationship("AnomalyFlag", back_populates="answer_sheet", cascade="all, delete-orphan")
    ai_summary = relationship("AIStudentSummary", back_populates="answer_sheet", uselist=False, cascade="all, delete-orphan")

class QuestionEvaluation(Base):
    __tablename__ = "question_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    answer_sheet_id = Column(Integer, ForeignKey("answer_sheets.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    student_answer_ocr = Column(Text, nullable=True)
    page_number = Column(Integer, default=1)
    ai_suggested_marks = Column(Float, nullable=True)
    ai_confidence = Column(Float, nullable=True)  # Percentage 0-100
    detected_concepts = Column(Text, nullable=True)  # JSON list
    missing_concepts = Column(Text, nullable=True)   # JSON list
    ai_explanation = Column(Text, nullable=True)
    examiner_marks = Column(Float, nullable=True)
    examiner_comments = Column(Text, nullable=True)
    is_ai_accepted = Column(Boolean, default=False)
    status = Column(String(50), default="unchecked")  # unchecked, evaluated, modified
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    answer_sheet = relationship("AnswerSheet", back_populates="evaluations")
    question = relationship("Question", back_populates="evaluations")

class AnomalyFlag(Base):
    __tablename__ = "anomaly_flags"

    id = Column(Integer, primary_key=True, index=True)
    answer_sheet_id = Column(Integer, ForeignKey("answer_sheets.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    flag_type = Column(String(80), nullable=False)  # score_discrepancy, rapid_evaluation, extreme_score
    severity = Column(String(30), default="medium") # low, medium, high
    details = Column(Text, nullable=False)
    ai_score = Column(Float, nullable=True)
    examiner_score = Column(Float, nullable=True)
    resolved = Column(Boolean, default=False)
    moderator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    moderator_notes = Column(Text, nullable=True)
    final_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    answer_sheet = relationship("AnswerSheet", back_populates="anomalies")
    question = relationship("Question")
    moderator = relationship("User", foreign_keys=[moderator_id])

class AIStudentSummary(Base):
    __tablename__ = "ai_student_summaries"

    id = Column(Integer, primary_key=True, index=True)
    answer_sheet_id = Column(Integer, ForeignKey("answer_sheets.id"), unique=True, nullable=False)
    strengths = Column(Text, nullable=False)   # JSON list
    weak_areas = Column(Text, nullable=False)  # JSON list
    overall_summary = Column(Text, nullable=False)
    recommended_grade = Column(String(20), default="B+")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    answer_sheet = relationship("AnswerSheet", back_populates="ai_summary")
