# app/api/v1/response.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.response import DashboardData, ResponseCreate, ResponseBulkCreate, ResponseOut
from app.services import response_service
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User

router = APIRouter()


@router.post("/submit", response_model=ResponseOut)
def submit_response(
    response_data: ResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a single quiz response.
    Requires authentication.
    """
    return response_service.submit_response(db, current_user.id, response_data)


@router.post("/submit-bulk", response_model=List[ResponseOut])
def submit_responses_bulk(
    bulk_data: ResponseBulkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit multiple quiz responses at once.
    Requires authentication.
    """
    return response_service.submit_responses_bulk(db, current_user.id, bulk_data.responses)


@router.get("/dashboard", response_model=DashboardData)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's dashboard data including statistics and recent activity.
    Requires authentication.
    """
    return response_service.get_user_dashboard_data(db, current_user.id)
