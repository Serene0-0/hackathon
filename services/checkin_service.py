from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.checkin import CheckinRecord
from models.checkin_settings import PauseStatus
from utils.time_utils import local_today


class CheckinService:
    def __init__(self, db: AsyncSession, user_id, tz: str):
        self.db = db
        self.user_id = user_id
        self.tz = tz

    async def _ensure_not_paused(self) -> None:
        stmt = select(PauseStatus).where(PauseStatus.user_id == self.user_id)
        pause = (await self.db.execute(stmt)).scalar_one_or_none()
        if pause and pause.paused:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    async def get_today_checkins(self) -> CheckinRecord | None:
        today = local_today(tz=self.tz)
        stmt = select(CheckinRecord).where(
            CheckinRecord.user_id == self.user_id,
            CheckinRecord.local_date == today,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()


    async def create_today_checkin(self) -> CheckinRecord:
        await self._ensure_not_paused()

        existing = await self.get_today_checkins()
        if existing:
            raise HTTPException(status_code=400, detail="Checkin already exists")

        today = local_today(tz=self.tz)
        obj = CheckinRecord(
            user_id=self.user_id,
            local_date=today,
            timezone_used=self.tz,
        )

        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj