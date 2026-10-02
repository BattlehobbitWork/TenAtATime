"""Settings routes — pain day mode, reminder times, user preferences."""

import json
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, UserSetting
from app.models.schemas import SettingsOut, SettingsUpdate

router = APIRouter()

DEFAULTS = {
    "pain_day_mode": "false",
    "reminder_time_daily": "09:00",
    "reminder_time_weekly": "08:00",
    "trash_reminder_enabled": "true",
    "trash_reminder_time": "19:00",
    "user_name": "Amy",
}


async def _get_setting(db: AsyncSession, key: str) -> str:
    row = await db.scalar(select(UserSetting).where(UserSetting.key == key))
    return row.value if row else DEFAULTS.get(key, "")


async def _set_setting(db: AsyncSession, key: str, value: str):
    row = await db.scalar(select(UserSetting).where(UserSetting.key == key))
    if row:
        row.value = value
    else:
        db.add(UserSetting(key=key, value=value))


@router.get("/settings", response_model=SettingsOut)
async def get_settings(db: AsyncSession = Depends(get_db)):
    return SettingsOut(
        pain_day_mode=(await _get_setting(db, "pain_day_mode")) == "true",
        reminder_time_daily=await _get_setting(db, "reminder_time_daily"),
        reminder_time_weekly=await _get_setting(db, "reminder_time_weekly"),
        trash_reminder_enabled=(await _get_setting(db, "trash_reminder_enabled")) == "true",
        trash_reminder_time=await _get_setting(db, "trash_reminder_time"),
        user_name=await _get_setting(db, "user_name"),
    )


@router.put("/settings", response_model=SettingsOut)
async def update_settings(req: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    if req.pain_day_mode is not None:
        await _set_setting(db, "pain_day_mode", "true" if req.pain_day_mode else "false")
    if req.reminder_time_daily is not None:
        await _set_setting(db, "reminder_time_daily", req.reminder_time_daily)
    if req.reminder_time_weekly is not None:
        await _set_setting(db, "reminder_time_weekly", req.reminder_time_weekly)
    if req.trash_reminder_enabled is not None:
        await _set_setting(db, "trash_reminder_enabled", "true" if req.trash_reminder_enabled else "false")
    if req.trash_reminder_time is not None:
        await _set_setting(db, "trash_reminder_time", req.trash_reminder_time)
    if req.user_name is not None:
        await _set_setting(db, "user_name", req.user_name)

    await db.commit()
    return await get_settings(db)
