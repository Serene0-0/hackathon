from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.mood import Mood
from utils.time_utils import local_today

async def create_today_mood(db: AsyncSession, user_id, score: int, tz: str) -> Mood:
    today = local_today(tz)

    stmt = select(Mood).where(Mood.user_id == user_id, Mood.local_date == today)
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mood already recorded today" )

    obj = Mood(user_id=user_id, local_date=today, score=score, timezone_used=tz)

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_today_mood(db: AsyncSession, user_id, tz: str) -> Mood | None:
    today = local_today(tz)
    stmt = select(Mood).where(Mood.user_id == user_id, Mood.local_date == today)
    exists = (await db.execute(stmt)).scalar_one_or_none()

    return exists


async def list_moods(db: AsyncSession, user_id, date_from=None, date_to=None) -> list[Mood]:
    stmt = select(Mood).where(Mood.user_id == user_id)
    if date_from:
        stmt = stmt.where(Mood.local_date >= date_from)
    if date_to:
        stmt = stmt.where(Mood.local_date <= date_to)
    stmt = stmt.order_by(Mood.local_date.asc())

    result = await db.scalars(stmt)
    return list(result.all())