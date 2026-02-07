from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from zoneinfo import ZoneInfo

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.checkin import CheckinRecord
from models.checkin_settings import MissCheckinRule, PauseStatus
from models.emergency_contact import EmergencyContact
from models.miss_checkin_alert_log import MissCheckinAlertLog
from services.email_service import EmailService


def local_today(tz: str) -> date:
    return datetime.now(ZoneInfo(tz)).date()


@dataclass
class ScanResult:
    user_id: str
    triggered: bool
    days_missed: int | None
    last_checkin_date: date | None
    email_sent_to: str | None
    reason: str


class MissCheckinScanService:
    def __init__(self, db: AsyncSession, email_svc: EmailService):
        self.db = db
        self.email_svc = email_svc

    async def scan_all(self) -> list[ScanResult]:
        """
        Scan all users who have:
        - MissCheckinRule
        - EmergencyContact
        Skip paused users
        """
        # Join required tables; PauseStatus is optional but we’ll treat paused=True as skip.
        stmt = (
            select(User, MissCheckinRule, EmergencyContact, PauseStatus)
            .join(MissCheckinRule, MissCheckinRule.user_id == User.user_id)
            .join(EmergencyContact, EmergencyContact.user_id == User.user_id)
            .outerjoin(PauseStatus, PauseStatus.user_id == User.user_id)
        )

        rows = (await self.db.execute(stmt)).all()
        results: list[ScanResult] = []

        for user, rule, contact, pause in rows:
            # 1) Skip paused
            if pause is not None and pause.paused:
                results.append(
                    ScanResult(
                        user_id=str(user.user_id),
                        triggered=False,
                        days_missed=None,
                        last_checkin_date=None,
                        email_sent_to=None,
                        reason="paused",
                    )
                )
                continue

            tz = user.timezone or "UTC"
            today = local_today(tz)

            # 2) Find last checkin (max local_date)
            last_stmt = select(func.max(CheckinRecord.local_date)).where(CheckinRecord.user_id == user.user_id)
            last_checkin = (await self.db.execute(last_stmt)).scalar_one()

            # 2.1) Never checked in => do not trigger (your rule)
            if last_checkin is None:
                results.append(
                    ScanResult(
                        user_id=str(user.user_id),
                        triggered=False,
                        days_missed=None,
                        last_checkin_date=None,
                        email_sent_to=None,
                        reason="no_checkin_record",
                    )
                )
                continue

            # 3) Compute missed days
            days_missed = (today - last_checkin).days

            # last_checkin is today => not missed
            if days_missed < rule.threshold_days:
                results.append(
                    ScanResult(
                        user_id=str(user.user_id),
                        triggered=False,
                        days_missed=days_missed,
                        last_checkin_date=last_checkin,
                        email_sent_to=None,
                        reason="below_threshold",
                    )
                )
                continue

            # 4) Ensure alert only once per (user_id, last_checkin_date)
            already_stmt = select(MissCheckinAlertLog.alert_id).where(
                MissCheckinAlertLog.user_id == user.user_id,
                MissCheckinAlertLog.last_checkin_date == last_checkin,
            )
            already = (await self.db.execute(already_stmt)).scalar_one_or_none()
            if already is not None:
                results.append(
                    ScanResult(
                        user_id=str(user.user_id),
                        triggered=False,
                        days_missed=days_missed,
                        last_checkin_date=last_checkin,
                        email_sent_to=None,
                        reason="already_alerted_for_this_window",
                    )
                )
                continue

            # 5) Render message template (use your model placeholders)
            body = rule.message_template.format(
                contact_name=contact.name,
                username=user.username,
                interval_days=days_missed,
            )

            subject = f"[Lumenary] Missed check-in alert ({days_missed} days)"

            # 6) Send email
            self.email_svc.send_email(contact.email, subject, body)

            # 7) Write alert log
            self.db.add(
                MissCheckinAlertLog(
                    user_id=user.user_id,
                    last_checkin_date=last_checkin,
                    triggered_at=datetime.now(tz=ZoneInfo("UTC")),
                )
            )
            await self.db.commit()

            results.append(
                ScanResult(
                    user_id=str(user.user_id),
                    triggered=True,
                    days_missed=days_missed,
                    last_checkin_date=last_checkin,
                    email_sent_to=contact.email,
                    reason="sent",
                )
            )

        return results
