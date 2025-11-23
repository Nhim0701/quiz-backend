# app/services/response_service.py
from sqlalchemy.orm import Session
from typing import List
from app.repository import response_repo
from app.schemas.response import ResponseCreate
from app.models.responses import Response


def submit_response(db: Session, user_id: int, response_data: ResponseCreate) -> Response:
    """Submit a single quiz response."""
    return response_repo.create_response(db, user_id, response_data)


def submit_responses_bulk(db: Session, user_id: int, responses: List[ResponseCreate]) -> List[Response]:
    """Submit multiple quiz responses at once."""
    return response_repo.create_responses_bulk(db, user_id, responses)


def get_user_dashboard_data(db: Session, user_id: int):
    """Get comprehensive dashboard data for user."""
    statistics = response_repo.get_user_statistics(db, user_id)
    recent_activity = response_repo.get_user_recent_activity(db, user_id, limit=10)

    # Calculate overall statistics
    total_answered = sum(stat['total_answered'] for stat in statistics)
    total_correct = sum(stat['correct_answers'] for stat in statistics)

    return {
        'overall': {
            'total_answered': total_answered,
            'total_correct': total_correct,
            'total_wrong': total_answered - total_correct,
            'overall_accuracy': round(total_correct / total_answered * 100, 1) if total_answered > 0 else 0
        },
        'by_category': statistics,
        'recent_activity': recent_activity
    }
