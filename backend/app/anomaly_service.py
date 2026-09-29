import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from .models import AnswerSheet, QuestionEvaluation, AnomalyFlag, Question

logger = logging.getLogger("ai_osm.anomaly")

class AnomalyService:
    @staticmethod
    def check_unchecked_answers(sheet: AnswerSheet, evaluations: List[QuestionEvaluation]) -> Dict[str, Any]:
        """
        Detects questions where student text exists or question is present but examiner has not graded it yet.
        Prevents submission until all answers are reviewed.
        """
        unchecked = []
        for ev in evaluations:
            # Check if examiner hasn't awarded marks
            if ev.examiner_marks is None:
                has_text = bool(ev.student_answer_ocr and len(ev.student_answer_ocr.strip()) > 5)
                unchecked.append({
                    "question_id": ev.question_id,
                    "question_number": ev.question.question_number if ev.question else ev.question_id,
                    "has_ocr_text": has_text,
                    "status": "missing_marks"
                })

        can_submit = len(unchecked) == 0
        message = (
            "All questions have been evaluated. Ready for final submission."
            if can_submit
            else f"Submission blocked: {len(unchecked)} question(s) require evaluation before submitting."
        )

        return {
            "can_submit": can_submit,
            "unchecked_count": len(unchecked),
            "unchecked_questions": unchecked,
            "message": message
        }

    @staticmethod
    def detect_anomalies(
        db: Session,
        sheet: AnswerSheet,
        evaluations: List[QuestionEvaluation],
        time_spent_seconds: int
    ) -> List[AnomalyFlag]:
        """
        Analyzes the submitted evaluation for:
        1. Score discrepancies between AI suggestion and human examiner.
        2. Rapid evaluation speed anomaly.
        3. Extreme score outliers.
        """
        flags = []
        total_examiner = 0.0
        total_ai = 0.0
        max_total = 0.0

        # Check question-level discrepancies
        for ev in evaluations:
            ex_marks = ev.examiner_marks if ev.examiner_marks is not None else 0.0
            ai_marks = ev.ai_suggested_marks if ev.ai_suggested_marks is not None else 0.0
            q_max = ev.question.max_marks if ev.question else 10.0

            total_examiner += ex_marks
            total_ai += ai_marks
            max_total += q_max

            diff = abs(ex_marks - ai_marks)
            diff_ratio = diff / max(q_max, 1.0)

            # Flag if difference is >= 25% on a question
            if diff_ratio >= 0.25 and diff >= 2.0:
                flag = AnomalyFlag(
                    answer_sheet_id=sheet.id,
                    question_id=ev.question_id,
                    flag_type="score_discrepancy",
                    severity="high" if diff_ratio >= 0.4 else "medium",
                    details=(
                        f"Significant divergence on Question {ev.question.question_number}: "
                        f"Examiner gave {ex_marks:.1f}/{q_max:.1f}, while AI suggested {ai_marks:.1f}/{q_max:.1f} "
                        f"(Diff: {diff:+.1f} marks, {diff_ratio*100:.0f}% variance)."
                    ),
                    ai_score=ai_marks,
                    examiner_score=ex_marks,
                    resolved=False
                )
                flags.append(flag)
                db.add(flag)

        # Check rapid evaluation speed anomaly (e.g., under 15 seconds for a multi-question exam)
        if time_spent_seconds < 15:
            flag = AnomalyFlag(
                answer_sheet_id=sheet.id,
                question_id=None,
                flag_type="rapid_evaluation",
                severity="high",
                details=(
                    f"Unusually rapid evaluation: entire paper completed in only {time_spent_seconds} seconds "
                    f"(expected minimum 60s for {len(evaluations)} technical questions). Possible hasty grading."
                ),
                ai_score=total_ai,
                examiner_score=total_examiner,
                resolved=False
            )
            flags.append(flag)
            db.add(flag)

        # Check overall extreme score discrepancy
        total_diff = abs(total_examiner - total_ai)
        if total_diff >= (max_total * 0.20) and not any(f.flag_type == "score_discrepancy" for f in flags):
            flag = AnomalyFlag(
                answer_sheet_id=sheet.id,
                question_id=None,
                flag_type="score_discrepancy",
                severity="medium",
                details=(
                    f"Cumulative total score discrepancy: Examiner total is {total_examiner:.1f}/{max_total:.1f} "
                    f"vs AI total {total_ai:.1f}/{max_total:.1f} (Δ {total_diff:.1f} marks)."
                ),
                ai_score=total_ai,
                examiner_score=total_examiner,
                resolved=False
            )
            flags.append(flag)
            db.add(flag)

        # Update sheet status based on flags
        if flags:
            sheet.status = "flagged_moderation"
        else:
            sheet.status = "completed"

        sheet.total_score = total_examiner
        sheet.ai_total_score = total_ai
        sheet.time_spent_seconds = time_spent_seconds

        db.commit()
        return flags
