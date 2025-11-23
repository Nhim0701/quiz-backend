# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A FastAPI-based quiz application with PostgreSQL database backend. The system manages users, questions, answers, and user responses to quiz questions.

## Development Commands

### Running the Application
```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload

# Run without reload
poetry run uvicorn app.main:app
```

### Database Migrations (Alembic)
```bash
# Create a new migration (after modifying models)
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history
```

### Data Management
```bash
# Import seed data from YAML files
poetry run python data/data_import_script.py
```

## Architecture

### Three-Layer Architecture

The application follows a clean three-layer pattern:

1. **API Layer** (`app/api/v1/`): FastAPI routers that handle HTTP requests/responses
2. **Service Layer** (`app/services/`): Business logic and orchestration
3. **Repository Layer** (`app/repository/`): Database queries and data access

Example flow: `user.py (API)` → `user_service.py` → `user_repo.py` → Database

### Database Models Structure

Models exist in TWO locations with an important distinction:

- **`app/models/`**: Primary SQLAlchemy models used by the application and Alembic migrations
  - Import from `app.db.base` for the Base class
  - These are registered in `app/models/__init__.py`

- **`app/db/models/`**: Secondary/legacy models (appears to be outdated)
  - Import from `app.db.base` for the Base class
  - Only `answers.py` exists here with conflicting relationship name (`options` vs `answers`)

**IMPORTANT**: When working with models:
- Modify files in `app/models/` (primary location)
- The `app/db/models/answers.py` file has a conflicting relationship name (`back_populates="options"`) that should be `back_populates="answers"` to match `app/models/questions.py`
- Alembic env.py imports models from `app/db/models/` which may cause issues

### Core Data Models

- **User**: Quiz participants with email, account name, and password
- **Question**: Quiz questions with optional images and categories
  - Note: `id` field has `autoincrement=False` - IDs are set manually from YAML data
- **Answer**: Multiple choice answers for questions
  - Linked to questions via `question_id` foreign key
  - `is_correct` flag indicates the right answer
  - Optional `explanation` field
- **Response**: Records user answers to questions
  - Tracks `user_id`, `question_id`, `selected_option_id`, and `is_correct`
  - Uses `answered_at` timestamp

### Database Session Management

- Database URL loaded from `.env` file (`DATABASE_URL`)
- Session dependency: `get_db()` from `app.db.session`
- Use `SessionLocal()` for standalone scripts
- FastAPI routes use `db: Session = Depends(get_db)`

### Alembic Configuration

- Alembic environment is in `alembic/env.py`
- Models must be imported in `alembic/env.py` for autogenerate to work
- Currently imports from both `app.db.models.*` and `app.db.base`
- Database URL is loaded from `.env` and set dynamically in `alembic/env.py`

### Pydantic Schemas

- Located in `app/schemas/`
- Use `orm_mode = True` (or `from_attributes = True` in Pydantic v2) for SQLAlchemy compatibility
- Schemas define API request/response shapes
- Currently only `UserOut` and `QuestionOut` schemas exist

## Data Import System

YAML-based data seeding from `data/` directory:
- Organized by date folders (e.g., `data/20251102/`)
- `questions.yaml`: Questions with nested answers
- `users.yaml`: User accounts
- Script: `data/data_import_script.py`

Note: The script imports `app.db.models.results.Result` which doesn't exist (should be `app.models.responses.Response`)

## Authentication System

The application uses JWT (JSON Web Tokens) for authentication:

### Key Components

- **Password Hashing**: Uses bcrypt via passlib for secure password storage
- **JWT Tokens**: Generated using python-jose with HS256 algorithm
- **Security utilities**: Located in `app/utils/security.py`
- **Auth dependency**: `get_current_user()` in `app/api/dependencies/auth.py`

### Environment Variables

Required in `.env` file:
- `SECRET_KEY`: Secret key for JWT signing (generate with `openssl rand -hex 32`)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

### API Endpoints

- `POST /api/v1/auth/register`: Register new user, returns JWT token
- `POST /api/v1/auth/login`: Login with email/password, returns JWT token

### Protected Routes

To protect an endpoint, add `current_user: User = Depends(get_current_user)` to the route parameters:

```python
@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user.account_name}
```

Example: `GET /api/v1/users/me` returns the current authenticated user.

### Authentication Flow

1. User registers or logs in → receives JWT token
2. Client includes token in requests: `Authorization: Bearer <token>`
3. `get_current_user()` dependency validates token and returns User object
4. Route handler can access authenticated user

## Technology Stack

- **Framework**: FastAPI 0.120.4
- **Database**: PostgreSQL (via psycopg2)
- **ORM**: SQLAlchemy 2.0.44
- **Migrations**: Alembic 1.17.1
- **Server**: Uvicorn 0.38.0
- **Package Manager**: Poetry
- **Authentication**: JWT (python-jose) + bcrypt (passlib)
- **Python**: 3.12+
