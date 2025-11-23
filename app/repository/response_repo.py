# app/repository/response_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.responses import Response
from app.models.questions import Question
from app.models.users import User
from app.schemas.response import ResponseCreate


def create_response(db: Session, user_id: int, response_data: ResponseCreate) -> Response:
    """Create a single response record."""
    db_response = Response(
        user_id=user_id,
        question_id=response_data.question_id,
        selected_option_id=response_data.selected_option_id,
        is_correct=response_data.is_correct
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response


def create_responses_bulk(db: Session, user_id: int, responses: List[ResponseCreate]) -> List[Response]:
    """Create multiple response records at once."""
    db_responses = [
        Response(
            user_id=user_id,
            question_id=r.question_id,
            selected_option_id=r.selected_option_id,
            is_correct=r.is_correct
        )
        for r in responses
    ]
    db.add_all(db_responses)
    db.commit()
    for r in db_responses:
        db.refresh(r)
    return db_responses


def get_user_statistics(db: Session, user_id: int):
    """Get user's quiz statistics grouped by category."""
    from sqlalchemy import Integer, case

    stats = db.query(
        Question.category,
        func.count(Response.id).label('total_answered'),
        func.sum(case((Response.is_correct == True, 1), else_=0)).label('correct_answers'),
        func.max(Response.answered_at).label('last_attempt')
    ).join(
        Response, Response.question_id == Question.id
    ).filter(
        Response.user_id == user_id,
        Question.deleted_at.is_(None)
    ).group_by(
        Question.category
    ).all()

    return [
        {
            'category': stat[0],
            'total_answered': stat[1],
            'correct_answers': stat[2] or 0,
            'wrong_answers': stat[1] - (stat[2] or 0),
            'accuracy': round((stat[2] or 0) / stat[1] * 100, 1) if stat[1] > 0 else 0,
            'last_attempt': stat[3].isoformat() if stat[3] else None
        }
        for stat in stats
    ]


def get_user_recent_activity(db: Session, user_id: int, limit: int = 10):
    """Get user's recent quiz activity."""
    activities = db.query(
        Response.id,
        Question.category,
        Question.content,
        Response.is_correct,
        Response.answered_at
    ).join(
        Question, Response.question_id == Question.id
    ).filter(
        Response.user_id == user_id,
        Question.deleted_at.is_(None)
    ).order_by(
        Response.answered_at.desc()
    ).limit(limit).all()

    return [
        {
            'id': activity[0],
            'category': activity[1],
            'question_preview': activity[2][:100] + '...' if len(activity[2]) > 100 else activity[2],
            'is_correct': activity[3],
            'answered_at': activity[4].isoformat() if activity[4] else None
        }
        for activity in activities
    ]
