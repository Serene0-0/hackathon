"""
Timezone Utilities
"""
from typing import Optional
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger(__name__)

def validate_timezone(tz_string: str) -> bool:
    """
    Validate IANA timezone identifier
    :return: boolean, True if valid, False if not
    """
    try:
        ZoneInfo(tz_string)
        return True
    except Exception:
        return False

async def update_user_timezone_if_needed(db, user, header_timezone: Optional[str]) -> bool:
    """
    Update user timezone when app launch
    :param db: AsyncSession
    :param user: User object
    :param header_timezone: Timezone from X-User-Timezone header
    :return: boolean: True if user timezone is updated; else return False
    """
    if not header_timezone:
        return False

    if not validate_timezone(header_timezone):
        logger.warning(f"Invalid timezone {header_timezone}")
        return False

    # check if timezone is different
    old_timezone = user.timezone

    if old_timezone == header_timezone:
        return False

    # update timezone
    user.timezone = header_timezone
    user.last_known_timezone = header_timezone

    await db.commit()
    await db.refresh(user)

    logger.info(f"User{user.user_id} timezone updated: {old_timezone} -> {header_timezone}")
    return True