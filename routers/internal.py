from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import MessageResponse
from .resolve_tz import resolve_tz
from db.session import get_db
from deps import get_current_user_demo
from models.checkin import CheckinRecord
from models.mood import Mood
from models.journal import Journal
from utils.time_utils import local_today

router = APIRouter(tags=["Internal"])

@router.post("/internal/test/reset-today")
async def reset_today(
        db: AsyncSession = Depends(get_db),
        user = Depends(get_current_user_demo),
        x_user_timezone: str | None = Header(None, alias="X-User-Timezone")
):
    tz = await resolve_tz(db, user, x_user_timezone)
    today = local_today(tz)

    # delete today's checkin
    await db.execute(
        delete(CheckinRecord).where(CheckinRecord.user_id == user.user_id).
                     where(CheckinRecord.checkin_id == CheckinRecord.checkin_id,
                           CheckinRecord.local_date == today))

    # delete today's mood
    await db.execute(
        delete(Mood).where(Mood.user_id == user.user_id, Mood.local_date == today))

    # delete today's journals
    await db.execute(
        delete(Journal).where(Journal.user_id == user.user_id, Journal.local_date == today)
    )

    await db.commit()

    return MessageResponse(message="OK")


