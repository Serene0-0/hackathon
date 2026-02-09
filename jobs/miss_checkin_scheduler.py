from __future__ import annotations

import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db import AsyncSessionLocal
from services.email_service import EmailService
from services.miss_checkin_scan_service import MissCheckinScanService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def miss_checkin_job():
    try:
        async with AsyncSessionLocal() as db:
            email_svc = EmailService()
            svc = MissCheckinScanService(db, email_svc)
            await svc.scan_all()
    except Exception:
        logger.exception("miss_checkin_job failed")

def start_miss_checkin_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        miss_checkin_job,
        trigger=IntervalTrigger(minutes=5),
        id="miss_checkin_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    logger.info("Miss checkin scheduler started")


def stop_miss_checkin_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Miss checkin scheduler stopped")
