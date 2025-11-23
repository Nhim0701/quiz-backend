# Docker Deployment Guide

This guide explains how to containerize and deploy the Quiz Backend API using Docker.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Step 1: Create Dockerfile](#step-1-create-dockerfile)
4. [Step 2: Create Docker Compose](#step-2-create-docker-compose)
5. [Step 3: Create Environment File](#step-3-create-environment-file)
6. [Step 4: Create .dockerignore](#step-4-create-dockerignore)
7. [Step 5: Build and Run](#step-5-build-and-run)
8. [Step 6: Database Migration](#step-6-database-migration)
9. [Step 7: Import Data](#step-7-import-data)
10. [Common Commands](#common-commands)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Install Docker Compose](https://docs.docker.com/compose/install/))
- Git (optional, for version control)

Check installations:
```bash
docker --version
docker-compose --version
```

---

## Project Structure

After setup, your project will look like this:

```
quiz/
├── app/
│   ├── api/
│   ├── db/
│   ├── models/
│   ├── repository/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
├── alembic/
├── data/
├── Dockerfile           # NEW
├── docker-compose.yml   # NEW
├── .env                 # Environment variables
├── .env.docker          # NEW - Docker environment
├── .dockerignore        # NEW
├── pyproject.toml
└── poetry.lock
```

---

## Step 1: Create Dockerfile

Create `Dockerfile` in the `quiz/` directory:

```dockerfile
# Dockerfile

# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only main

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Step 2: Create Docker Compose

Create `docker-compose.yml` in the `quiz/` directory:

```yaml
# docker-compose.yml

version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: quiz_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-quizuser}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-quizpass}
      POSTGRES_DB: ${POSTGRES_DB:-quiz_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-quizuser} -d ${POSTGRES_DB:-quiz_db}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: quiz_api
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+psycopg2://${POSTGRES_USER:-quizuser}:${POSTGRES_PASSWORD:-quizpass}@db:5432/${POSTGRES_DB:-quiz_db}
      SECRET_KEY: ${SECRET_KEY:-your-super-secret-key-change-in-production}
      ALGORITHM: ${ALGORITHM:-HS256}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES:-30}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./data:/app/data  # Mount data folder for imports

  # Optional: pgAdmin for database management
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: quiz_pgadmin
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL:-admin@quiz.com}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin}
    ports:
      - "5050:80"
    depends_on:
      - db
    profiles:
      - tools  # Only start with: docker-compose --profile tools up

volumes:
  postgres_data:
```

---

## Step 3: Create Environment File

Create `.env.docker` in the `quiz/` directory:

```env
# .env.docker

# Database Configuration
POSTGRES_USER=quizuser
POSTGRES_PASSWORD=quizpass
POSTGRES_DB=quiz_db

# Application Configuration
DATABASE_URL=postgresql+psycopg2://quizuser:quizpass@db:5432/quiz_db
SECRET_KEY=your-super-secret-key-change-this-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# pgAdmin (optional)
PGADMIN_EMAIL=admin@quiz.com
PGADMIN_PASSWORD=admin
```

**Important:** For production, generate a secure SECRET_KEY:
```bash
openssl rand -hex 32
```

---

## Step 4: Create .dockerignore

Create `.dockerignore` in the `quiz/` directory:

```
# .dockerignore

# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
.env
.venv
env/
venv/
ENV/

# Poetry
.poetry

# IDE
.idea
.vscode
*.swp
*.swo

# Testing
.pytest_cache
.coverage
htmlcov/
.tox

# Documentation
*.md
!README.md

# Docker
Dockerfile
docker-compose*.yml
.docker

# Misc
*.log
*.tmp
.DS_Store
```

---

## Step 5: Build and Run

### Option A: Using docker-compose (Recommended)

```bash
# Navigate to quiz directory
cd quiz/

# Build and start all services
docker-compose --env-file .env.docker up --build

# Or run in background (detached mode)
docker-compose --env-file .env.docker up --build -d
```

### Option B: Build and run separately

```bash
# Build the image
docker-compose --env-file .env.docker build

# Start services
docker-compose --env-file .env.docker up -d

# Check status
docker-compose ps
```

### Verify Services

```bash
# Check running containers
docker ps

# Expected output:
# CONTAINER ID   IMAGE        STATUS         PORTS
# xxx            quiz_api     Up             0.0.0.0:8000->8000/tcp
# xxx            postgres:15  Up (healthy)   0.0.0.0:5432->5432/tcp
```

### Test API

```bash
# Test root endpoint
curl http://localhost:8000/

# Expected: {"message":"Welcome to My FastAPI Project"}

# Test API docs
# Open in browser: http://localhost:8000/docs
```

---

## Step 6: Database Migration

After containers are running, apply database migrations:

```bash
# Run migrations inside the container
docker-compose exec api alembic upgrade head

# Or run as one-off command
docker-compose run --rm api alembic upgrade head
```

### Verify Migration

```bash
# Check migration history
docker-compose exec api alembic history

# Check current revision
docker-compose exec api alembic current
```

---

## Step 7: Import Data

### Import Questions from YAML

```bash
# Import questions using the import script
docker-compose exec api python data/import_questions.py data/20251102/questions.yaml
```

### Import Questions from CSV

```bash
# Copy CSV file to container (if not in data/ folder)
docker cp "My aws - Sheet3 (1).csv" quiz_api:/app/

# Import from CSV
docker-compose exec api python data/csv_to_yaml_import.py "/app/My aws - Sheet3 (1).csv" \
  --start-id 1000 \
  --category aws \
  --question-set "AWS DVA-C02 Dump 1"
```

### Create Initial User

```bash
# Access Python shell in container
docker-compose exec api python

# In Python shell:
>>> from app.db.session import SessionLocal
>>> from app.models.users import User
>>> from app.utils.security import get_password_hash
>>>
>>> db = SessionLocal()
>>> user = User(
...     user_email="admin@quiz.com",
...     account_name="Admin",
...     user_password=get_password_hash("admin123")
... )
>>> db.add(user)
>>> db.commit()
>>> print("User created!")
>>> exit()
```

---

## Common Commands

### Container Management

```bash
# Start services
docker-compose --env-file .env.docker up -d

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data!)
docker-compose down -v

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Logs

```bash
# View all logs
docker-compose logs

# View API logs
docker-compose logs api

# Follow logs (live)
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100 api
```

### Shell Access

```bash
# Access API container shell
docker-compose exec api bash

# Access database shell
docker-compose exec db psql -U quizuser -d quiz_db

# Run Python commands
docker-compose exec api python -c "print('Hello from container!')"
```

### Database Operations

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U quizuser -d quiz_db

# Backup database
docker-compose exec db pg_dump -U quizuser quiz_db > backup.sql

# Restore database
docker-compose exec -T db psql -U quizuser quiz_db < backup.sql
```

### Rebuild

```bash
# Rebuild without cache
docker-compose build --no-cache

# Rebuild and restart
docker-compose up --build -d
```

---

## Troubleshooting

### Issue: Container won't start

```bash
# Check logs for errors
docker-compose logs api

# Common fixes:
# 1. Check if port 8000 is already in use
lsof -i :8000

# 2. Check if database is healthy
docker-compose ps
```

### Issue: Database connection error

```bash
# Ensure database is running and healthy
docker-compose ps

# Check database logs
docker-compose logs db

# Verify connection from API container
docker-compose exec api python -c "
from app.db.session import SessionLocal
db = SessionLocal()
print('Connection successful!')
db.close()
"
```

### Issue: Migration fails

```bash
# Check current migration state
docker-compose exec api alembic current

# Show migration history
docker-compose exec api alembic history

# Reset migrations (WARNING: data loss!)
docker-compose exec api alembic downgrade base
docker-compose exec api alembic upgrade head
```

### Issue: Permission denied

```bash
# Fix file permissions
chmod -R 755 data/

# Or run with specific user in Dockerfile
# Add to Dockerfile:
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser
```

### Issue: Out of disk space

```bash
# Clean up Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune

# Check disk usage
docker system df
```

---

## Production Considerations

### 1. Use Production-Ready Settings

```yaml
# In docker-compose.prod.yml
services:
  api:
    environment:
      - DEBUG=false
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. Use Gunicorn for Production

Update Dockerfile CMD:
```dockerfile
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### 3. Add Health Check to API

```yaml
# In docker-compose.yml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 4. Use Secrets for Sensitive Data

```yaml
# docker-compose.yml
services:
  api:
    secrets:
      - db_password
      - secret_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  secret_key:
    file: ./secrets/secret_key.txt
```

### 5. Add Nginx Reverse Proxy

```yaml
# Add to docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
```

---

## Quick Start Summary

```bash
# 1. Navigate to project
cd quiz/

# 2. Create environment file
cp .env.docker.example .env.docker
# Edit .env.docker with your settings

# 3. Build and start
docker-compose --env-file .env.docker up --build -d

# 4. Run migrations
docker-compose exec api alembic upgrade head

# 5. Import data (optional)
docker-compose exec api python data/import_questions.py data/20251102/questions.yaml

# 6. Test
curl http://localhost:8000/
# Open: http://localhost:8000/docs

# 7. View logs
docker-compose logs -f api
```

---

## Related Documentation

- [Question Import Guide](README.md)
- [CSV Import Guide](CSV_IMPORT_GUIDE.md)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
