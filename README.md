# Lives Tracker API

Backend API for Mood Tracker - AI-powered mood tracking app for international students.

## Tech Stack

- **FastAPI** 0.109 - Web framework
- **PostgreSQL** 16 - Database
- **SQLAlchemy** 2.0 - ORM (async)
- **Alembic** - Database migrations
- **Claude API** - AI-generated insights
- **Docker** - Containerization

## activate virtual environment
source .venv/bin/activate

## using venv install
```bash
PKG=(pytest-mock)
uv pip install "$PKG" --python ../venv/bin/python
```

## generate key/token pepper
```bash
openssl rand -base64 32
```

## Local Setup & Run
```bash
uvicorn main:app --reload
```

## Quick Start with docker

1. copy env.example
```bash
cp env.example .env
```
2. Build all containers
```bash
docker compose up -d --build
```
3. Start the database and backend containers
```bash
docker compose up -d db app
```
4. Run database migration with Alembic
```bash
docker compose run --rm app alembic upgrade head
```
5. Check running services
```bash
docker compose ps
```
5. View logs if needed
```bash
docker compose logs -f db app
```
6. Rebuild after updating code
```bash
docker compose up -d --build
```

## Database Migrations
Alembic is used for managing database schema changes.
- Generate a new migration when models change:
```bash
docker compose run --rm app alembic revision --autogenerate -m "describe change"
```
- Apply migrations to bring the database to the latest state:
```bash
docker compose run --rm app alembic upgrade head
```
- Check current version:
```bash
docker compose run --rm app alembic current
```

