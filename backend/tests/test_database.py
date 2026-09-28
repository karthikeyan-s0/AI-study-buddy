from datetime import date
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.profile import Profile
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.progress import Progress

def test_database_initialization_all_eight_tables(test_engine):
    """Verify that all 8 tables are created and registered in the database metadata."""
    inspector = inspect(test_engine)
    table_names = inspector.get_table_names()

    expected_tables = {
        "users",
        "profiles",
        "subjects",
        "topics",
        "study_plans",
        "quizzes",
        "quiz_attempts",
        "progress",
    }
    for table in expected_tables:
        assert table in table_names, f"Table '{table}' should exist in database tables: {table_names}"

def test_insert_user(db_session):
    """Verify creating and persisting a User record."""
    user = User(
        name="Karthi",
        email="karthi@example.com",
        password_hash="hashed_pw_placeholder_phase2"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == "karthi@example.com"
    assert user.name == "Karthi"
    assert user.created_at is not None

def test_unique_user_email(db_session):
    """Verify that the unique constraint on user email is enforced."""
    user1 = User(
        name="User One",
        email="duplicate@example.com",
        password_hash="pw1"
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        name="User Two",
        email="duplicate@example.com",
        password_hash="pw2"
    )
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_user_profile_relationship(db_session):
    """Verify 1-to-1 relationship between User and Profile."""
    user = User(
        name="Alex Smith",
        email="alex@example.com",
        password_hash="hash123"
    )
    profile = Profile(
        education_level="College",
        daily_study_hours=3.5,
        learning_preference="Visual",
        user=user
    )
    db_session.add(user)
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(user)

    assert user.profile is not None
    assert user.profile.education_level == "College"
    assert user.profile.daily_study_hours == 3.5
    assert user.profile.user.email == "alex@example.com"

def test_user_subject_relationship(db_session):
    """Verify 1-to-many relationship between User and Subjects."""
    user = User(
        name="John Doe",
        email="john@example.com",
        password_hash="hash123"
    )
    sub1 = Subject(name="Operating Systems", description="OS concepts", exam_date=date(2026, 10, 15), difficulty="medium", user=user)
    sub2 = Subject(name="Database Management", description="DBMS concepts", exam_date=date(2026, 11, 20), difficulty="hard", user=user)
    
    db_session.add(user)
    db_session.add_all([sub1, sub2])
    db_session.commit()
    db_session.refresh(user)

    assert len(user.subjects) == 2
    names = [s.name for s in user.subjects]
    assert "Operating Systems" in names
    assert "Database Management" in names

def test_subject_topic_relationship(db_session):
    """Verify 1-to-many relationship between Subject and Topics."""
    user = User(name="Jane Doe", email="jane@example.com", password_hash="hash123")
    subject = Subject(name="Computer Networks", difficulty="hard", user=user)
    topic1 = Topic(name="OSI Model", status="completed", difficulty="medium", subject=subject)
    topic2 = Topic(name="TCP/IP Handshake", status="in_progress", difficulty="hard", subject=subject)
    
    db_session.add_all([user, subject, topic1, topic2])
    db_session.commit()
    db_session.refresh(subject)

    assert len(subject.topics) == 2
    assert subject.topics[0].subject.name == "Computer Networks"

def test_study_plan_relationships_and_json(db_session):
    """Verify StudyPlan links with User & Subject and persists JSON structured plan."""
    user = User(name="Plan User", email="plan@example.com", password_hash="hash123")
    subject = Subject(name="Algorithms", difficulty="hard", user=user)
    
    sample_plan = {
        "plan": [
            {
                "day": 1,
                "topic": "Sorting Algorithms",
                "duration_minutes": 120,
                "tasks": ["Merge Sort", "Quick Sort", "Practice LeetCode"]
            },
            {
                "day": 2,
                "topic": "Graph Algorithms",
                "duration_minutes": 120,
                "tasks": ["BFS", "DFS", "Dijkstra"]
            }
        ]
    }
    
    study_plan = StudyPlan(
        title="14-Day Algorithms Mastery",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 14),
        plan_json=sample_plan,
        user=user,
        subject=subject
    )
    db_session.add_all([user, subject, study_plan])
    db_session.commit()
    db_session.refresh(study_plan)

    assert study_plan.id is not None
    assert study_plan.user.email == "plan@example.com"
    assert study_plan.subject.name == "Algorithms"
    assert isinstance(study_plan.plan_json, dict)
    assert len(study_plan.plan_json["plan"]) == 2
    assert study_plan.plan_json["plan"][0]["topic"] == "Sorting Algorithms"

def test_quiz_and_quiz_attempt_relationships_and_json(db_session):
    """Verify Quiz and QuizAttempt models, cascades, and JSON storage."""
    user = User(name="Quiz Student", email="quizuser@example.com", password_hash="hash123")
    subject = Subject(name="Data Structures", difficulty="medium", user=user)
    
    questions = [
        {
            "question": "What is the time complexity of binary search?",
            "options": {"A": "O(1)", "B": "O(n)", "C": "O(log n)", "D": "O(n^2)"},
            "correct_answer": "C",
            "explanation": "Binary search halves the search space each step."
        }
    ]
    
    quiz = Quiz(
        topic="Binary Search",
        difficulty="medium",
        questions_json=questions,
        subject=subject
    )
    db_session.add_all([user, subject, quiz])
    db_session.commit()
    db_session.refresh(quiz)

    assert quiz.id is not None
    assert quiz.subject.name == "Data Structures"
    assert len(quiz.questions_json) == 1

    # Record an attempt
    attempt = QuizAttempt(
        quiz=quiz,
        user=user,
        score=1,
        total_questions=1,
        percentage=100.0,
        answers_json={"1": "C"}
    )
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(attempt)

    assert attempt.id is not None
    assert attempt.percentage == 100.0
    assert attempt.answers_json == {"1": "C"}
    assert attempt.quiz.topic == "Binary Search"
    assert attempt.user.email == "quizuser@example.com"

def test_progress_relationships(db_session):
    """Verify Progress model links with User, Subject, and optional Topic."""
    user = User(name="Progress User", email="progress@example.com", password_hash="hash123")
    subject = Subject(name="System Design", difficulty="hard", user=user)
    topic = Topic(name="Load Balancing", status="in_progress", difficulty="medium", subject=subject)
    
    progress = Progress(
        user=user,
        subject=subject,
        topic=topic,
        completion_percentage=65.5,
        study_minutes=150
    )
    db_session.add_all([user, subject, topic, progress])
    db_session.commit()
    db_session.refresh(progress)

    assert progress.id is not None
    assert progress.completion_percentage == 65.5
    assert progress.study_minutes == 150
    assert progress.user.email == "progress@example.com"
    assert progress.subject.name == "System Design"
    assert progress.topic.name == "Load Balancing"

def test_api_health_and_docs_endpoints(client):
    """Verify that GET /health and GET /docs work as expected."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "AI StudyBuddy API"

    docs_response = client.get("/docs")
    assert docs_response.status_code == 200
    assert "swagger" in docs_response.text.lower() or "openapi" in docs_response.text.lower()
