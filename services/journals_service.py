import random
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.journal import Journal
from utils.time_utils import local_today

async def create_journal(db: AsyncSession, user_id, content: str,
                         title: str | None,tz: str) -> Journal:
    today = local_today(tz)
    obj = Journal(
        user_id = user_id,
        content = content,
        title = title,
        timezone_used=tz,
        local_date = today
    )

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_today_journals(db: AsyncSession, user_id, tz: str) -> list[Journal]:

    today = local_today(tz)
    stmt = select(Journal).where(Journal.user_id == user_id, Journal.local_date == today)

    result = await db.scalars(stmt)
    return list(result.all())


async def get_random_journal(db: AsyncSession, user_id,
                             tz: str, exclude_today: bool = True) -> Journal | None:
    today = local_today(tz)
    stmt = select(Journal).where(Journal.user_id == user_id)
    if exclude_today:
        stmt = select(Journal).where(Journal.local_date != today)
    stmt = stmt.order_by(func.random()).limit(1)

    result = (await db.execute(stmt)).scalars().first()

    if not result:
        return None

    return result


async def list_journals_by_date(db: AsyncSession, user_id,
                                date_from=None, date_to=None,
                                limit: int = 50, offset: int=0) -> list[Journal]:
    stmt = select(Journal).where(Journal.user_id == user_id)

    if date_from:
        stmt = stmt.where(Journal.local_date >= date_from)
    if date_to:
        stmt = stmt.where(Journal.local_date <= date_to)

    stmt = (
        stmt.order_by(Journal.local_date.asc(), Journal.created_at.asc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.scalars(stmt)
    return list(result.all())