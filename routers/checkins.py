from typing import Optional
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_db, get_current_user_demo
from models.user import User
from schemas.checkins import ApiResponseCheckinStatus, CheckinStatus
from services.checkin_service import CheckinService
from utils.time_utils import local_today
from .resolve_tz import resolve_tz

router = APIRouter(tags=["Checkin"])

@router.get("/checkins/today", response_model=ApiResponseCheckinStatus)
async def get_checkin_today_entry(
        db_session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_demo),
        x_user_timezone: Optional[str] = Header(None, alias="X-User-Timezone"),
):
    tz = await resolve_tz(db_session, current_user, x_user_timezone)
    today = local_today(tz)

    svc = CheckinService(db_session, current_user.user_id, tz)
    obj = await svc.get_today_checkins()

    data = CheckinStatus(
        checkin_id=obj.checkin_id if obj else None,
        local_date=today,
        checked_in_today=bool(obj),
        timezone_used=str(tz),
    )

    return ApiResponseCheckinStatus(data=data, message="OK")


@router.post("/checkins", response_model=ApiResponseCheckinStatus, status_code=status.HTTP_201_CREATED)
async def create_checkin_today(
        db_session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_demo),
        x_user_timezone: Optional[str] = Header(None, alias="X-User-Timezone"),
):
    tz = await resolve_tz(db_session, current_user, x_user_timezone)

    svc = CheckinService(db_session, current_user.user_id, tz)
    obj = await svc.create_today_checkin()

    data = CheckinStatus(
        checkin_id=obj.checkin_id,
        local_date=obj.local_date,
        checked_in_today=True,
        timezone_used=str(tz),
    )

    return ApiResponseCheckinStatus(data=data, message="OK")

