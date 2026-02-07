from typing import Optional

from utils.timezone import validate_timezone, update_user_timezone_if_needed


async def resolve_tz(db, user, x_user_timezone: Optional[str]) -> str:
    if x_user_timezone and validate_timezone(x_user_timezone):
        await update_user_timezone_if_needed(db, user, x_user_timezone)
        return x_user_timezone

    if user.timezone and validate_timezone(user.timezone):
        return user.timezone

    return "UTC"