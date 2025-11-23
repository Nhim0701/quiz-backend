from pydantic import BaseModel
from typing import List


class CategoryOut(BaseModel):
    category: str
    question_count: int

    class Config:
        from_attributes = True


class QuestionSetOut(BaseModel):
    """Represents a set/dump of questions within a category"""
    question_set: str
    question_count: int
    question_range: str  # e.g., "1-50"

    class Config:
        from_attributes = True


class CategoryWithSetsOut(BaseModel):
    """Category with all its question sets"""
    category: str
    total_questions: int
    question_sets: List[QuestionSetOut]

    class Config:
        from_attributes = True


class AnswerOut(BaseModel):
    id: int
    content: str
    is_correct: bool
    explanation: str | None = None

    class Config:
        from_attributes = True


class QuestionWithAnswers(BaseModel):
    id: int
    content: str
    image_url: str | None = None
    category: str | None = None
    answers: List[AnswerOut]

    class Config:
        from_attributes = True


class QuestionOut(BaseModel):
    id: int
    content: str
    image_url: str | None = None
    category: str | None = None

    class Config:
        from_attributes = True
