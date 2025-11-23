# app/repository/user_repo.py
from sqlalchemy.orm import Session
from app.models.users import User

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
