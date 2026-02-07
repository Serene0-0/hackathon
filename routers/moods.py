from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from deps import get_db, get_current_user_demo
from models.user import User

from schemas.moods import MoodCreateRequest, ApiResponseMood, MoodRecordList, MoodRecord, ApiResponseMoodList
from services.moods_service import create_today_mood, get_today_mood, list_moods
from .resolve_tz import resolve_tz

router = APIRouter(tags=["Moods"])

@router.post("/moods", response_model=ApiResponseMood, status_code=status.HTTP_201_CREATED)
async def create_mood(
        payload: MoodCreateRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_demo),
        x_user_timezone: Optional[str] = Header(None, alias="X-User-Timezone")
):
    tz = await resolve_tz(db, current_user, x_user_timezone)

    obj = await create_today_mood(db, current_user.user_id, payload.score, tz)

    await db.commit()
    await db.refresh(obj)

    data = MoodRecord.model_validate(obj)
    return ApiResponseMood(data=data, message="Mood created successfully")


@router.get("/moods/today", response_model=ApiResponseMood)
async def get_mood_today(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_demo),
    x_user_timezone: Optional[str] = Header(None, alias="X-User-Timezone"),
):
    tz = await resolve_tz(db, user, x_user_timezone)

    obj = await get_today_mood(db, user.user_id, tz)

    if obj is None:
        raise HTTPException(status_code=404, detail="No mood recorded today")

    data = MoodRecord.model_validate(obj)
    return ApiResponseMood(data=data, message="OK")


@router.get("/moods", response_model=ApiResponseMoodList)
async def get_moods(
    date_from: Optional[date] = Query(None, alias="from", description="Start local date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, alias="to", description="End local date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_demo),
    x_user_timezone: Optional[str] = Header(None, alias="X-User-Timezone")
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' must be <= 'to'")

    rows = await list_moods(db, user.user_id, date_from, date_to)
    items = [MoodRecord.model_validate(r) for r in rows]

    data = MoodRecordList(items=items, count=len(items))

    return ApiResponseMoodList(data=data, message="OK")