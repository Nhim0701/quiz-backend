# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import user, auth, question, response

app = FastAPI(
    title="My FastAPI Project",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router từ folder api/v1
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(question.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(response.router, prefix="/api/v1/responses", tags=["responses"])

@app.get("/")
def root():
    return {"message": "Welcome to My FastAPI Project"}

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "quiz-api",
        "version": "1.0.0"
    }
