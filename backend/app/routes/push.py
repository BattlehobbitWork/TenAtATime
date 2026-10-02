"""Push notification routes — subscribe, unsubscribe, and send reminders."""

import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, PushSubscription, ReminderConfig, Task, TaskCompletion, UserSetting
from app.models.schemas import PushSubscriptionRequest, PushSubscribeResponse
from app.config import settings
from app.services import rotation

router = APIRouter()


@router.post("/push/subscribe", response_model=PushSubscribeResponse)
async def subscribe(req: PushSubscriptionRequest, db: AsyncSession = Depends(get_db)):
    """Store a web push subscription from the browser."""
    # Check if already exists
    existing = await db.scalar(
        select(PushSubscription).where(PushSubscription.endpoint == req.endpoint)
    )
    if existing:
        existing.is_active = True
        existing.keys_json = json.dumps(req.keys)
    else:
        sub = PushSubscription(
            endpoint=req.endpoint,
            keys_json=json.dumps(req.keys),
            is_active=True,
        )
        db.add(sub)
    await db.commit()
    return PushSubscribeResponse(success=True, message="Subscribed.")


@router.delete("/push/subscribe", response_model=PushSubscribeResponse)
async def unsubscribe(endpoint: str, db: AsyncSession = Depends(get_db)):
    """Remove a push subscription."""
    await db.execute(
        delete(PushSubscription).where(PushSubscription.endpoint == endpoint)
    )
    await db.commit()
    return PushSubscribeResponse(success=True, message="Unsubscribed.")


@router.post("/push/test", response_model=PushSubscribeResponse)
async def send_test_push(db: AsyncSession = Depends(get_db)):
    """Send a test push notification to verify setup."""
    subs = (await db.execute(
        select(PushSubscription).where(PushSubscription.is_active == True)
    )).scalars().all()

    if not subs:
        return PushSubscribeResponse(success=False, message="No active subscriptions.")

    from app.services.push import send_push
    for sub in subs:
        await send_push(sub, "Ten at a Time", "Ready when you are. This is a test notification.")

    return PushSubscribeResponse(success=True, message=f"Sent to {len(subs)} device(s).")


@router.post("/push/send-reminders")
async def send_reminders(db: AsyncSession = Depends(get_db)):
    """Check what reminders are due and send them. Called by scheduler."""
    from app.services.push import send_push
    from datetime import date

    now = datetime.now(timezone.utc)
    today = date.today()
    today_str = today.isoformat()

    # Get all active subscriptions
    subs = (await db.execute(
        select(PushSubscription).where(PushSubscription.is_active == True)
    )).scalars().all()

    if not subs:
        return {"sent": 0, "message": "No subscriptions."}

    # Get today's tasks
    tasks = (await db.execute(select(Task))).scalars().all()
    completions = (await db.execute(select(TaskCompletion))).scalars().all()
    summary = rotation.get_today_summary(list(tasks), list(completions), today)

    # Build reminder messages
    messages = []

    # Daily reminder
    daily_setting = await db.scalar(select(UserSetting).where(UserSetting.key == "reminder_time_daily"))
    if daily_setting and daily_setting.value == now.strftime("%H:%M"):
        undone_daily = [t for t in summary["daily"] if not t.is_done_today]
        if undone_daily:
            messages.append("Ready when you are. A few small things on the list today.")

    # Wednesday trash reminder
    trash_enabled = await db.scalar(select(UserSetting).where(UserSetting.key == "trash_reminder_enabled"))
    trash_time = await db.scalar(select(UserSetting).where(UserSetting.key == "trash_reminder_time"))
    if (trash_enabled and trash_enabled.value == "true"
            and trash_time and trash_time.value == now.strftime("%H:%M")
            and today.weekday() == 2):  # Wednesday
        messages.append("Wednesday reminder -- trash night. One trip to the curb.")

    # Zone reminder (Saturday)
    zone_tasks = summary["zone"]
    if zone_tasks and today.weekday() == 5:  # Saturday
        zone_name = zone_tasks[0].zone if zone_tasks else "this week's zone"
        messages.append(f"Weekend zone: {zone_name}. Pick one or two things, that's plenty.")

    # Maintenance due soon
    for m in summary["maintenance"]:
        if m["is_due_soon"] and not m.get("is_done_today"):
            messages.append(f"It's been a while -- {m['task'].title}? Only when you're ready.")
            break  # Just one maintenance reminder, don't overwhelm

    sent = 0
    for msg in messages:
        for sub in subs:
            await send_push(sub, "Ten at a Time", msg)
            sent += 1

    return {"sent": sent, "messages": messages}
