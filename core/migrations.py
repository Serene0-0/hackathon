# core/migrations.py
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

def run_migrations_if_enabled() -> None:
    """
    Run alembic migrations at startup (idempotent).
    Only runs when RUN_MIGRATIONS=true.
    Raises on failure to prevent app from starting with wrong schema.
    """
    enabled = os.getenv("RUN_MIGRATIONS", "").lower() in {"1", "true", "yes", "on"}
    if not enabled:
        logger.info("RUN_MIGRATIONS not enabled; skip alembic upgrade.")
        return

    workdir = os.getenv("APP_WORKDIR", "/app")

    logger.info("Running alembic upgrade head...")
    # Important: run inside container/app working directory where alembic.ini exists
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=workdir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        logger.error("Alembic upgrade failed.\nSTDOUT:\n%s\nSTDERR:\n%s", result.stdout, result.stderr)
        raise RuntimeError("Alembic migration failed")
    logger.info("Alembic upgrade succeeded.\n%s", result.stdout)
