# app/schemas/response.py
from pydantic import BaseModel
from typing import List
from datetime import datetime


class ResponseCreate(BaseModel):
    question_id: int
    selected_option_id: int
    is_correct: bool


class ResponseBulkCreate(BaseModel):
    responses: List[ResponseCreate]


class ResponseOut(BaseModel):
    id: int
    user_id: int
    question_id: int
    selected_option_id: int
    is_correct: bool
    answered_at: datetime | None

    class Config:
        from_attributes = True


class CategoryStatistics(BaseModel):
    category: str
    total_answered: int
    correct_answers: int
    wrong_answers: int
    accuracy: float
    last_attempt: str | None


class RecentActivity(BaseModel):
    id: int
    category: str
    question_preview: str
    is_correct: bool
    answered_at: str | None


class OverallStatistics(BaseModel):
    total_answered: int
    total_correct: int
    total_wrong: int
    overall_accuracy: float


class DashboardData(BaseModel):
    overall: OverallStatistics
    by_category: List[CategoryStatistics]
    recent_activity: List[RecentActivity]
