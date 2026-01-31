"""
Database Initialization
"""
import logging
from sqlalchemy import text
from db.session import engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Initialize and verify database"""
    async with engine.begin() as conn:
        # Verify connection
        await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")

        # Check timezone
        result = await conn.execute(text("SHOW timezone"))
        tz = result.scalar()
        logger.info(f"Database timezone: {tz}")

        if tz.upper() != "UTC":
            logger.warning(f"Database timezone is {tz}, not UTC!")


async def check_db_health() -> bool:
    """Check database health"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False