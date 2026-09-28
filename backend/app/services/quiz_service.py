from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.subject import Subject
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.services.gemini_service import get_gemini_service, GeminiServiceError

def build_quiz_prompt(subject_name: str, topic: str, difficulty: str, num_questions: int) -> str:
    return f"""You are an expert college professor and exam question creator.
Create a high-quality, multiple-choice quiz testing college-level understanding.

Subject: {subject_name}
Topic: {topic}
Difficulty: {difficulty}
Number of Questions: {num_questions}

Requirements:
1. Generate exactly {num_questions} questions.
2. Each question must have exactly 4 plausible options labeled "A", "B", "C", and "D".
3. Provide the single correct option letter ("A", "B", "C", or "D").
4. Provide a clear, educational explanation for why that answer is correct.
5. Do not include duplicate questions or trivial true/false variations.
6. Return JSON ONLY with the exact following schema:
{{
  "questions": [
    {{
      "question": "Question text here (string)",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }},
      "correct_answer": "A",
      "explanation": "Clear explanation of the correct answer."
    }}
  ]
}}"""

def validate_quiz_json(raw_json: Any) -> List[Dict[str, Any]]:
    """Validate structure of AI-generated quiz questions."""
    if not isinstance(raw_json, dict):
        raise ValueError("AI quiz response must be a JSON object.")
    
    questions = raw_json.get("questions")
    if not isinstance(questions, list) or len(questions) == 0:
        raise ValueError("AI quiz response must contain a non-empty 'questions' list.")

    validated = []
    for idx, q in enumerate(questions):
        if not isinstance(q, dict):
            raise ValueError(f"Question at index {idx} must be an object.")
        
        q_text = str(q.get("question", "")).strip()
        if not q_text:
            raise ValueError(f"Question at index {idx} is missing question text.")

        options = q.get("options")
        if not isinstance(options, dict) or not all(k in options for k in ("A", "B", "C", "D")):
            raise ValueError(f"Question at index {idx} must have 4 options: A, B, C, D.")

        correct = str(q.get("correct_answer", "")).strip().upper()
        if correct not in ("A", "B", "C", "D"):
            raise ValueError(f"Question at index {idx} has invalid correct_answer: '{correct}'.")

        explanation = str(q.get("explanation", "Correct answer verified.")).strip()

        validated.append({
            "question": q_text,
            "options": {k: str(options[k]).strip() for k in ("A", "B", "C", "D")},
            "correct_answer": correct,
            "explanation": explanation
        })

    return validated

def generate_quiz_for_subject(
    db: Session,
    current_user: User,
    subject_id: int,
    topic: str,
    difficulty: str = "medium",
    num_questions: int = 5
) -> Quiz:
    # 1. Verify subject ownership
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )

    prompt = build_quiz_prompt(subject.name, topic, difficulty, num_questions)
    gemini = get_gemini_service()

    try:
        raw_json = gemini.generate_json(prompt)
    except GeminiServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to generate AI quiz."
        ) from e

    try:
        validated_questions = validate_quiz_json(raw_json)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid AI quiz structure: {str(e)}"
        ) from e

    quiz = Quiz(
        subject_id=subject.id,
        topic=topic,
        difficulty=difficulty,
        questions_json=validated_questions,
        created_at=datetime.now(timezone.utc)
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

def calculate_and_record_quiz_attempt(
    db: Session,
    current_user: User,
    quiz_id: int,
    answers: Dict[str, str]
) -> Dict[str, Any]:
    """
    Deterministically grade the student's quiz attempt on the backend.
    Never uses LLM for scoring.
    """
    quiz = db.query(Quiz).join(Subject).filter(
        Quiz.id == quiz_id,
        Subject.user_id == current_user.id
    ).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    questions = quiz.questions_json or []
    total_questions = len(questions)
    if total_questions == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz has no questions to grade."
        )

    score = 0
    feedback_list = []

    for idx, q in enumerate(questions):
        correct_answer = q.get("correct_answer", "").upper()
        # Accept string or int key in answers dict
        selected = answers.get(str(idx), answers.get(idx, None))
        if selected:
            selected = str(selected).strip().upper()

        is_correct = (selected == correct_answer)
        if is_correct:
            score += 1

        feedback_list.append({
            "question_index": idx,
            "question": q.get("question", ""),
            "selected_answer": selected,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

    percentage = round((score / total_questions) * 100.0, 2)

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=current_user.id,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        answers_json=answers,
        attempted_at=datetime.now(timezone.utc)
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "quiz_id": quiz.id,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "feedback": feedback_list,
        "attempted_at": attempt.attempted_at
    }
