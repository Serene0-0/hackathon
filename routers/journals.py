from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from deps import get_db, get_current_user_demo
from models.user import User

from schemas.journals import (JournalCreateRequest, JournalRecord, JournalRecordList,
                              ApiResponseJournal, ApiResponseJournalList)
from services.journals_service import create_journal, get_today_journals, get_random_journal, list_journals_by_date
from .resolve_tz import resolve_tz

router = APIRouter(tags=["Journals"])

@router.post("/journals", response_model=ApiResponseJournal, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
        payload: JournalCreateRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_demo),
        x_user_timezone: Optional[str] = Header(None, alias="X-User-Timezone")
):
    tz = await resolve_tz(db, current_user, x_user_timezone)

    obj = await create_journal(db, current_user.user_id,
                               payload.content, payload.title, tz)

    await db.commit()
    await db.refresh(obj)

    data = JournalRecord.model_validate(obj)
    return ApiResponseJournal(data=data, message="Journal created successfully")


@router.get("/journals/today", response_model=ApiResponseJournalList)
async def get_journals_today_entry(
        db_session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_demo),
        x_user_timezone: Optional[str] = Header(None, alias="X-User-Timezone")
):
    tz = await resolve_tz(db_session, current_user, x_user_timezone)

    rows = await get_today_journals(db_session, current_user.user_id, tz)
    items = [JournalRecord.model_validate(r) for r in rows]

    data = JournalRecordList(items=items, count=len(items), next_cursor=None)
    return ApiResponseJournalList(data=data, message="OK")


@router.get("/journals", response_model=ApiResponseJournalList)
async def get_journals_by_date(
        date_from: Optional[date] = Query(None, alias="from", description="Start local date (YYYY-MM-DD)"),
        date_to: Optional[date] = Query(None, alias="to", description="End local date (YYYY-MM-DD)"),
        limit: int = Query(50, ge=1, le=200),
        db_session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_demo),
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' must be <= 'to'")

    rows = await list_journals_by_date(db_session, current_user.user_id, date_from, date_to, limit)
    items = [JournalRecord.model_validate(r) for r in rows]

    data = JournalRecordList(items=items, count=len(items), next_cursor=None)
    return ApiResponseJournalList(data=data, message="OK")


@router.get("/journals/random", response_model=ApiResponseJournal)
async def get_random_journal_entry(
        exclude_today: bool = Query(True, description="Exclude today's journals"),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user_demo),
        x_user_timezone: Optional[str] = Header(None, alias="X-User-Timezone")
):
    tz = await resolve_tz(db, user, x_user_timezone)

    obj = await get_random_journal(db, user.user_id, tz, exclude_today)
    if obj is None:
        raise HTTPException(status_code=404, detail="Journal not found")

    data = JournalRecord.model_validate(obj)
    return ApiResponseJournal(data=data, message="OK")