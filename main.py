# main.py
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from core.config import settings
from core.security import hash_password
from models import User
from routers import api_router
from db.session import AsyncSessionLocal

DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_EMAIL = "demo@test.com"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: ensure demo user exists (idempotent)
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.user_id == DEMO_USER_ID))).scalar_one_or_none()
        if not user:
            user = User(user_id=DEMO_USER_ID,
                        email=DEMO_EMAIL,
                        hashed_password="demo_no_login",
                        timezone="America/New_York"
            )
            db.add(user)
            await db.commit()
    yield


app = FastAPI(
    title=getattr(settings, "PROJECT_NAME", "Mood Tracker API"),
    version=getattr(settings, "VERSION", "1.0.0"),
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api/v1")
