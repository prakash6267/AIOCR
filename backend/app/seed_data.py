import os
import json
import logging
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .models import User, Exam, Question, AnswerSheet, QuestionEvaluation, AnomalyFlag, AIStudentSummary
from .ai_evaluator import AIEvaluator

logger = logging.getLogger("ai_osm.seed")

def generate_sample_sheet_image(filepath: str, student_roll: str, student_name: str, exam_code: str):
    """
    Creates a realistic handwritten-style answer sheet page using Pillow.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    width, height = 900, 1250
    img = Image.new("RGB", (width, height), color=(253, 252, 248))
    draw = ImageDraw.Draw(img)

    # Margins and header box
    margin_left = 60
    margin_top = 40
    
    # Paper border & ruled lines
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(210, 215, 220), width=2)
    draw.line([(margin_left, 20), (margin_left, height - 20)], fill=(240, 160, 160), width=2)  # Pink left margin line

    # Horizontal faint notebook lines
    for y in range(160, height - 40, 36):
        draw.line([(margin_left, y), (width - 25, y)], fill=(232, 238, 245), width=1)

    # University header
    draw.text((margin_left + 40, margin_top + 5), "INSTITUTE OF ADVANCED TECHNOLOGY - SEMESTER EXAMINATION", fill=(30, 41, 59))
    draw.text((margin_left + 40, margin_top + 28), f"COURSE: {exam_code} - AI & DISTRIBUTED SYSTEMS   |   DATE: OCT 2026", fill=(71, 85, 105))
    draw.rectangle([(margin_left + 35, margin_top + 55), (width - 50, margin_top + 95)], outline=(148, 163, 184), width=1)
    draw.text((margin_left + 45, margin_top + 65), f"STUDENT ROLL: {student_roll}     CANDIDATE: {student_name}     PAGE: 01 of 02", fill=(15, 23, 42))

    # Handwritten-style text simulation for answers
    y_pos = 175
    answers = [
        ("Ans 1:", "Encapsulation is the OOP technique where data (variables) and methods operating on them are bundled together. Data hiding is achieved by declaring member fields private so unauthorized classes cannot directly access them. We use public get/set functions for validation."),
        ("Ans 2:", "Backpropagation uses the calculus chain rule to calculate the partial derivative of the error function with respect to every weight in the network. During the backward pass, gradients flow backwards from the output layer to adjust weights via gradient descent."),
        ("Ans 3:", "Database normalization prevents insertion and deletion anomalies. 2NF removes partial functional dependencies on candidate keys. 3NF additionally eliminates transitive dependencies (X -> Y and Y -> Z)."),
        ("Ans 4:", "The CAP Theorem proves that a distributed data store can provide at most two out of three guarantees: Consistency, Availability, and Partition Tolerance. In practice, network partitions (P) are unavoidable, forcing a trade-off between CP and AP."),
        ("Ans 5:", "Supervised learning relies on labeled training sets with ground truth to predict outcomes (classification & regression). Unsupervised learning detects hidden structures and clusters in unlabeled data without prior feedback.")
    ]

    for q_label, text in answers:
        draw.text((margin_left + 10, y_pos), q_label, fill=(30, 58, 138))
        y_pos += 26
        
        # Word wrap
        words = text.split()
        line = ""
        for word in words:
            if len(line + " " + word) < 65:
                line += " " + word if line else word
            else:
                draw.text((margin_left + 30, y_pos), line, fill=(30, 41, 75))
                y_pos += 36
                line = word
        if line:
            draw.text((margin_left + 30, y_pos), line, fill=(30, 41, 75))
            y_pos += 50

    img.save(filepath, format="PNG")
    logger.info(f"Generated sample answer sheet image: {filepath}")

def seed_database():
    """Initializes tables and populates sample users, exams, and answer sheets."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Seed Users if not existing
        if db.query(User).count() == 0:
            examiner = User(
                name="Dr. Ramesh Sharma",
                email="dr.ramesh@univ.edu",
                role="examiner",
                avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Ramesh"
            )
            moderator = User(
                name="Prof. Anita Rao",
                email="prof.anita@univ.edu",
                role="moderator",
                avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Anita"
            )
            admin = User(
                name="Office of the Controller",
                email="admin@univ.edu",
                role="admin",
                avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Admin"
            )
            db.add_all([examiner, moderator, admin])
            db.commit()
            logger.info("Seeded default users (Examiner, Moderator, Admin).")
        else:
            examiner = db.query(User).filter_by(role="examiner").first()
            moderator = db.query(User).filter_by(role="moderator").first()
            admin = db.query(User).filter_by(role="admin").first()

        # 2. Seed Exam if not existing
        if db.query(Exam).count() == 0:
            exam = Exam(
                title="Distributed Systems & Machine Learning - Midterm 2026",
                code="CS-402",
                subject="Computer Science & Engineering",
                total_marks=50.0,
                passing_marks=20.0,
                instructions="Attempt all 5 questions. Each question carries 10 marks. Write legible answers with proper technical terminology."
            )
            db.add(exam)
            db.flush()

            # Seed Questions
            q1 = Question(
                exam_id=exam.id,
                question_number=1,
                question_text="Explain Object-Oriented Encapsulation and Data Hiding with an illustrative code example.",
                max_marks=10.0,
                model_answer="Encapsulation is the mechanism that binds together code and the data it manipulates. Data hiding is achieved by making member variables private and providing public getter and setter methods. This protects the internal state from unauthorized direct modifications and enforces data integrity.",
                key_concepts=json.dumps(["Encapsulation", "Data Hiding", "Private Access Specifiers", "Getter/Setter Methods", "Data Protection"]),
                rubric=json.dumps({"definition": 3.0, "data_hiding": 3.0, "code_example": 4.0})
            )
            q2 = Question(
                exam_id=exam.id,
                question_number=2,
                question_text="Describe the Backpropagation algorithm in Deep Neural Networks. How is the gradient computed?",
                max_marks=10.0,
                model_answer="Backpropagation computes the gradient of the loss function with respect to each weight using the multivariable chain rule. The forward pass calculates network activations and final loss. The backward pass propagates error gradients backwards through layers, updating weights via gradient descent to minimize overall loss.",
                key_concepts=json.dumps(["Chain Rule", "Loss Function", "Gradient Descent", "Weight Update", "Forward Pass", "Backward Pass"]),
                rubric=json.dumps({"chain_rule": 3.0, "gradient_descent": 3.0, "flow_diagram": 4.0})
            )
            q3 = Question(
                exam_id=exam.id,
                question_number=3,
                question_text="What is Database Normalization? Differentiate between 2NF and 3NF with transitive dependencies.",
                max_marks=10.0,
                model_answer="Database normalization reduces data redundancy and prevents insertion, update, and deletion anomalies. A relation is in 2NF if it is in 1NF and no non-prime attribute is partially dependent on any candidate key. A relation is in 3NF if it is in 2NF and has no transitive dependencies (no non-prime attribute depends on another non-prime attribute).",
                key_concepts=json.dumps(["Functional Dependency", "Transitive Dependency", "Candidate Key", "Partial Dependency", "Redundancy Elimination"]),
                rubric=json.dumps({"normalization_purpose": 2.0, "2nf_definition": 4.0, "3nf_transitive": 4.0})
            )
            q4 = Question(
                exam_id=exam.id,
                question_number=4,
                question_text="Explain the CAP Theorem for Distributed Storage systems with real-world database examples.",
                max_marks=10.0,
                model_answer="Eric Brewer's CAP Theorem states that a distributed data system can simultaneously guarantee at most two out of three properties: Consistency, Availability, and Partition Tolerance. Because network partitions (P) are inevitable in physical distributed networks, architects must choose between CP (e.g., MongoDB, HBase) and AP (e.g., Cassandra, DynamoDB).",
                key_concepts=json.dumps(["Consistency", "Availability", "Partition Tolerance", "Network Partitions", "CP vs AP Tradeoff"]),
                rubric=json.dumps({"cap_definitions": 3.0, "partition_reality": 3.0, "db_examples": 4.0})
            )
            q5 = Question(
                exam_id=exam.id,
                question_number=5,
                question_text="Compare Supervised Learning vs Unsupervised Learning with clustering and classification applications.",
                max_marks=10.0,
                model_answer="Supervised learning uses labeled input-output pairs with ground truth labels to train models for classification and regression tasks. Unsupervised learning analyzes unlabeled datasets without human supervision to discover inherent groupings, clusters, or dimensionality reductions such as K-Means or PCA.",
                key_concepts=json.dumps(["Labeled Data", "Ground Truth", "Clustering", "Classification", "Feature Vectors", "Unlabeled Patterns"]),
                rubric=json.dumps({"supervised_def": 3.0, "unsupervised_def": 3.0, "examples": 4.0})
            )
            db.add_all([q1, q2, q3, q4, q5])
            db.commit()
            logger.info("Seeded CS-402 Midterm Exam with 5 comprehensive questions.")
        else:
            exam = db.query(Exam).first()

        questions = db.query(Question).filter_by(exam_id=exam.id).order_by(Question.question_number).all()

        # 3. Seed Answer Sheets
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
        os.makedirs(uploads_dir, exist_ok=True)

        sheet1_file = os.path.join(uploads_dir, "sheet_2026_cs_041.png")
        sheet2_file = os.path.join(uploads_dir, "sheet_2026_cs_042.png")
        sheet3_file = os.path.join(uploads_dir, "sheet_2026_cs_043.png")

        generate_sample_sheet_image(sheet1_file, "2026-CS-041", "Aarav Sharma", exam.code)
        generate_sample_sheet_image(sheet2_file, "2026-CS-042", "Priya Nair", exam.code)
        generate_sample_sheet_image(sheet3_file, "2026-CS-043", "Rohan Verma", exam.code)

        if db.query(AnswerSheet).count() == 0:
            # Sheet #1: Evaluated & Completed
            s1 = AnswerSheet(
                exam_id=exam.id,
                student_roll="2026-CS-041",
                student_name="Aarav Sharma",
                file_path="/uploads/sheet_2026_cs_041.png",
                pages=1,
                status="completed",
                assigned_examiner_id=examiner.id,
                total_score=43.0,
                ai_total_score=42.0,
                time_spent_seconds=145
            )
            db.add(s1)
            db.flush()

            # Seed evaluations for Sheet #1
            for q in questions:
                eval_res = AIEvaluator.evaluate_answer(
                    student_text=q.model_answer,
                    model_answer=q.model_answer,
                    key_concepts=json.loads(q.key_concepts),
                    max_marks=q.max_marks
                )
                qe = QuestionEvaluation(
                    answer_sheet_id=s1.id,
                    question_id=q.id,
                    student_answer_ocr=q.model_answer,
                    ai_suggested_marks=eval_res["suggested_marks"],
                    ai_confidence=eval_res["confidence"],
                    detected_concepts=json.dumps(eval_res["detected_concepts"]),
                    missing_concepts=json.dumps(eval_res["missing_concepts"]),
                    ai_explanation=eval_res["ai_explanation"],
                    examiner_marks=eval_res["suggested_marks"],
                    examiner_comments="Well structured answer with proper examples.",
                    is_ai_accepted=True,
                    status="evaluated"
                )
                db.add(qe)

            # AI Summary for Sheet #1
            s1_summary = AIStudentSummary(
                answer_sheet_id=s1.id,
                strengths=json.dumps(["Encapsulation", "Chain Rule", "Functional Dependency", "CAP Theorem"]),
                weak_areas=json.dumps(["Could add code snippet for transitive dependency"]),
                overall_summary="Candidate demonstrated superior conceptual clarity across OOP, deep learning backpropagation, and distributed storage systems.",
                recommended_grade="A+ (Outstanding)"
            )
            db.add(s1_summary)

            # Sheet #2: Flagged for Moderation (High Score Discrepancy Anomaly)
            s2 = AnswerSheet(
                exam_id=exam.id,
                student_roll="2026-CS-042",
                student_name="Priya Nair",
                file_path="/uploads/sheet_2026_cs_042.png",
                pages=1,
                status="flagged_moderation",
                assigned_examiner_id=examiner.id,
                total_score=44.0,
                ai_total_score=31.5,
                time_spent_seconds=55
            )
            db.add(s2)
            db.flush()

            for idx, q in enumerate(questions):
                # On Q2, create a sharp discrepancy
                if idx == 1:
                    ocr_text = "Backprop algorithm computes gradients by multiplying matrices. Weight updates occur through backward pass."
                    ai_sugg = 4.0
                    ex_mark = 9.5
                    det_c = ["Weight Update", "Backward Pass"]
                    mis_c = ["Chain Rule", "Loss Function", "Gradient Descent"]
                    expl = "Student missed key mathematical justification (Chain Rule & Loss Function gradient). Awarded partial credit."
                else:
                    ocr_text = q.model_answer
                    ai_sugg = 8.5
                    ex_mark = 8.5
                    det_c = json.loads(q.key_concepts)[:3]
                    mis_c = json.loads(q.key_concepts)[3:]
                    expl = "Satisfactory conceptual explanation."

                qe2 = QuestionEvaluation(
                    answer_sheet_id=s2.id,
                    question_id=q.id,
                    student_answer_ocr=ocr_text,
                    ai_suggested_marks=ai_sugg,
                    ai_confidence=87.0,
                    detected_concepts=json.dumps(det_c),
                    missing_concepts=json.dumps(mis_c),
                    ai_explanation=expl,
                    examiner_marks=ex_mark,
                    examiner_comments="Awarded high marks.",
                    is_ai_accepted=(idx != 1),
                    status="evaluated"
                )
                db.add(qe2)

            # Anomaly Flag for Sheet #2
            flag2 = AnomalyFlag(
                answer_sheet_id=s2.id,
                question_id=questions[1].id,
                flag_type="score_discrepancy",
                severity="high",
                details="Significant divergence on Question 2: Examiner awarded 9.5/10, while AI suggested 4.0/10 (Δ +5.5 marks variance). Student omitted Chain Rule formulation.",
                ai_score=4.0,
                examiner_score=9.5,
                resolved=False
            )
            db.add(flag2)

            # Sheet #3: Ready for Live Evaluation Demo (Pending with Q3 Unchecked)
            s3 = AnswerSheet(
                exam_id=exam.id,
                student_roll="2026-CS-043",
                student_name="Rohan Verma",
                file_path="/uploads/sheet_2026_cs_043.png",
                pages=1,
                status="in_progress",
                assigned_examiner_id=examiner.id,
                total_score=None,
                ai_total_score=38.5,
                time_spent_seconds=0
            )
            db.add(s3)
            db.flush()

            # Prepopulate evaluations with AI suggestions ready for examiner review
            sample_answers = [
                "Encapsulation is the fundamental principle where member variables are declared private to ensure data hiding. Public methods called getters and setters provide controlled read and write access, safeguarding class invariants.",
                "Backpropagation calculates gradients through the neural network using the multivariable chain rule. The gradient of the loss function is propagated backwards to update synaptic weights with gradient descent.",
                "Database normalization is used to eliminate redundancy. 2NF removes partial functional dependencies, and 3NF removes transitive dependencies where non-prime attributes depend on other non-prime fields.",
                "The CAP theorem states that distributed storage systems cannot guarantee Consistency, Availability, and Partition tolerance all at once. Networks inevitably face partitions, forcing a choice between CP and AP.",
                "Supervised learning trains on labeled datasets for classification and regression. Unsupervised learning clusters unlabeled data to discover hidden patterns."
            ]

            for i, q in enumerate(questions):
                eval_data = AIEvaluator.evaluate_answer(
                    student_text=sample_answers[i],
                    model_answer=q.model_answer,
                    key_concepts=json.loads(q.key_concepts),
                    max_marks=q.max_marks
                )
                
                # Let Q1 be pre-evaluated for quick demo, Q2 partially, and Q3, Q4, Q5 pending
                ex_m = 9.0 if i == 0 else None
                status_val = "evaluated" if i == 0 else "unchecked"
                
                qe3 = QuestionEvaluation(
                    answer_sheet_id=s3.id,
                    question_id=q.id,
                    student_answer_ocr=sample_answers[i],
                    ai_suggested_marks=eval_data["suggested_marks"],
                    ai_confidence=eval_data["confidence"],
                    detected_concepts=json.dumps(eval_data["detected_concepts"]),
                    missing_concepts=json.dumps(eval_data["missing_concepts"]),
                    ai_explanation=eval_data["ai_explanation"],
                    examiner_marks=ex_m,
                    examiner_comments=None,
                    is_ai_accepted=(i == 0),
                    status=status_val
                )
                db.add(qe3)

            db.commit()
            logger.info("Successfully seeded 3 demo Answer Sheets with evaluations and moderation flags.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
