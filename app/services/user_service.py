# app/services/user_service.py
from sqlalchemy.orm import Session
from app.repository import user_repo

def list_users(db: Session):
    return user_repo.get_all_users(db)

def get_user(db: Session, user_id: int):
    return user_repo.get_user_by_id(db, user_id)
