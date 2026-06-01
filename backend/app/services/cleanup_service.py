"""Background cleanup service for expired script generation records."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.script_job import GeneratedScript, ScriptGenerationJob

logger = logging.getLogger(__name__)

SCRIPT_GENERATION_JOBS_RETENTION_DAYS = 30
GENERATED_SCRIPTS_RETENTION_DAYS = 7


async def delete_expired_records(db: AsyncSession) -> dict[str, Any]:
    """Delete expired records based on retention policy."""
    now = datetime.now(UTC)
    jobs_cutoff = now - timedelta(days=SCRIPT_GENERATION_JOBS_RETENTION_DAYS)
    scripts_cutoff = now - timedelta(days=GENERATED_SCRIPTS_RETENTION_DAYS)

    # Delete generated_scripts first (child records)
    scripts_result = await db.execute(
        delete(GeneratedScript).where(GeneratedScript.created_at < scripts_cutoff)
    )
    deleted_scripts: int = scripts_result.rowcount  # type: ignore[attr-defined]

    # Delete script_generation_jobs (parent records)
    jobs_result = await db.execute(
        delete(ScriptGenerationJob).where(ScriptGenerationJob.created_at < jobs_cutoff)
    )
    deleted_jobs: int = jobs_result.rowcount  # type: ignore[attr-defined]

    await db.commit()

    summary: dict[str, Any] = {
        "deleted_scripts": deleted_scripts,
        "deleted_jobs": deleted_jobs,
        "ran_at": now.isoformat(),
    }
    logger.info(f"Cleanup completed: {summary}")
    return summary


async def run_cleanup() -> None:
    """Entry point for the scheduler — manages its own DB session."""
    logger.info("Running scheduled database cleanup...")
    async with AsyncSessionLocal() as db:
        try:
            result = await delete_expired_records(db)
            logger.info(f"Cleanup result: {result}")
        except Exception as e:
            logger.error(f"Cleanup task failed: {e}", exc_info=True)
            await db.rollback()
