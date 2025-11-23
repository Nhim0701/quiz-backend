# app/schemas/user.py
from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    account_name: str
    user_email: str

    class Config:
        orm_mode = True  # cho phép convert từ SQLAlchemy model sang Pydantic
