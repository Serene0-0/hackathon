from __future__ import annotations
from datetime import datetime, date
from zoneinfo import ZoneInfo

def utc_now() -> datetime:
    return datetime.utcnow()

def local_today(tz: str) -> date:
    # tz must be IANA, e.g. "America/New_York"
    now_local = datetime.now(ZoneInfo(tz))
    return now_local.date()
