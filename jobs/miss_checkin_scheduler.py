from __future__ import annotations

import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import AsyncSessionLocal
from services.email_service import EmailService
from services.miss_checkin_scan_service import MissCheckinScanService

logger = logging.getLogger(__name__)

def start_miss_checkin_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    async def job():
        async with AsyncSessionLocal as db:
            svc = MissCheckinScanService(db=db, email_svc=EmailService())
            results = await svc.scan_all()
            triggered = [r for r in results if r.triggered]
            if triggered:
                logger.info("MissCheckinScan triggered=%d", len(triggered))

    def job_wrapper():
        asyncio.create_task(job())

    scheduler.add_job(job_wrapper, "interval", minutes=5, id="miss_checkin_scan")
    scheduler.start()
    return scheduler
