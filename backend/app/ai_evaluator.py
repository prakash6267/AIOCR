import json
import logging
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .llm_service import LLMService

logger = logging.getLogger("ai_osm.ai_evaluator")

class AIEvaluator:
    @staticmethod
    def evaluate_answer(
        student_text: str,
        model_answer: str,
        key_concepts: List[str],
        max_marks: float,
        question_text: str = "",
        model_name: str = "llama3",
        endpoint: str = "http://localhost:11434"
    ) -> Dict[str, Any]:
        """
        Evaluate student's OCR answer against model answer using local Ollama LLM Service.
        """
        return LLMService.evaluate_with_llm(
            student_text=student_text,
            model_answer=model_answer,
            key_concepts=key_concepts,
            max_marks=max_marks,
            question_text=question_text,
            provider="ollama",
            model_name=model_name,
            endpoint=endpoint
        )


    @staticmethod
    def generate_overall_summary(
        evaluations: List[Dict[str, Any]],
        total_score: float,
        max_total_marks: float
    ) -> Dict[str, Any]:
        """
        Generate student strengths, weak areas, and overall evaluation summary.
        """
        all_detected = []
        all_missing = []
        
        for ev in evaluations:
            det = ev.get("detected_concepts") or []
            mis = ev.get("missing_concepts") or []
            if isinstance(det, str):
                try:
                    det = json.loads(det)
                except Exception:
                    det = []
            if isinstance(mis, str):
                try:
                    mis = json.loads(mis)
                except Exception:
                    mis = []
            all_detected.extend(det)
            all_missing.extend(mis)

        percentage = (total_score / max(max_total_marks, 1.0)) * 100.0

        if percentage >= 85:
            grade = "A+ (Outstanding)"
        elif percentage >= 75:
            grade = "A (Very Good)"
        elif percentage >= 60:
            grade = "B+ (Good)"
        elif percentage >= 50:
            grade = "B (Satisfactory)"
        elif percentage >= 40:
            grade = "C (Pass)"
        else:
            grade = "D / Remedial Needed"

        # Deduplicate while preserving order
        unique_strengths = list(dict.fromkeys(all_detected))[:5]
        unique_weaknesses = list(dict.fromkeys(all_missing))[:4]

        if not unique_strengths:
            unique_strengths = ["Attempted basic questions", "Followed answer sheet structure"]
        if not unique_weaknesses:
            unique_weaknesses = ["Could include more real-world examples", "Minor code formatting tweaks"]

        overall = (
            f"Candidate scored {total_score:.1f}/{max_total_marks:.1f} ({percentage:.1f}%). "
            f"Demonstrated solid proficiency in core theoretical concepts ({', '.join(unique_strengths[:2])}). "
            f"Recommended focus areas for improvement: {', '.join(unique_weaknesses[:2])}."
        )

        return {
            "strengths": unique_strengths,
            "weak_areas": unique_weaknesses,
            "overall_summary": overall,
            "recommended_grade": grade
        }
