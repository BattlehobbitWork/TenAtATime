"""APScheduler for periodic reminder checks."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

_scheduler: AsyncIOScheduler | None = None


def start_scheduler():
    """Start the reminder scheduler. Checks every 15 minutes for due reminders."""
    global _scheduler
    _scheduler = AsyncIOScheduler()

    # Check reminders every 15 minutes
    _scheduler.add_job(
        _check_and_send_reminders,
        CronTrigger(minute="*/15"),
        id="reminders",
        replace_existing=True,
    )

    _scheduler.start()


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None


async def _check_and_send_reminders():
    """Check what reminders are due and send push notifications."""
    import httpx
    from app.config import settings

    try:
        async with httpx.AsyncClient() as client:
            # Call our own endpoint
            base = "http://localhost:8000"
            await client.post(f"{base}/api/push/send-reminders", timeout=10)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Reminder check failed: {e}")
