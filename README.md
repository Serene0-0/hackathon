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

