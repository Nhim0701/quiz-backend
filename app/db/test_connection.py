import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()  # load file .env
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Database connection successful:", result.scalar())
except Exception as e:
    print("Database connection failed:", e)
