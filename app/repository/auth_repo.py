# app/repository/auth_repo.py
from sqlalchemy.orm import Session
from app.models.users import User


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get a user by email address."""
    return db.query(User).filter(User.user_email == email).first()


def create_user(db: Session, user_email: str, account_name: str, hashed_password: str) -> User:
    """Create a new user."""
    user = User(
        user_email=user_email,
        account_name=account_name,
        user_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def email_exists(db: Session, email: str) -> bool:
    """Check if an email already exists."""
    return db.query(User).filter(User.user_email == email).first() is not None
