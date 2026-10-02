"""Pydantic schemas for API request/response."""

from pydantic import BaseModel
from datetime import datetime


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    zone: str
    estimated_minutes: int
    pain_day_eligible: bool
    pain_day_priority: int
    day_of_week: int | None = None
    week_pattern: str | None = None
    zone_week: int | None = None
    month_week: int | None = None
    frequency_days: int | None = None
    sort_order: int
    is_active: bool
    is_done_today: bool = False


class MaintenanceOut(BaseModel):
    task: TaskOut
    last_completed: datetime | None = None
    due_date: datetime | None = None
    days_until_due: int = 0
    is_due_soon: bool = False
    is_done_today: bool = False


class TodaySummary(BaseModel):
    date: str
    daily: list[TaskOut]
    weekly: list[TaskOut]
    zone: list[TaskOut]
    monthly: list[TaskOut]
    maintenance: list[MaintenanceOut]
    completed_count: int


class CompleteTaskRequest(BaseModel):
    task_id: int
    occurrence_date: str | None = None  # YYYY-MM-DD, defaults to today


class CompleteTaskResponse(BaseModel):
    success: bool
    message: str


class UndoCompletionRequest(BaseModel):
    completion_id: int


class PainDayTask(BaseModel):
    task: TaskOut | None
    message: str


class SettingsOut(BaseModel):
    pain_day_mode: bool = False
    reminder_time_daily: str = "09:00"
    reminder_time_weekly: str = "08:00"
    trash_reminder_enabled: bool = True
    trash_reminder_time: str = "19:00"
    user_name: str = "Amy"


class SettingsUpdate(BaseModel):
    pain_day_mode: bool | None = None
    reminder_time_daily: str | None = None
    reminder_time_weekly: str | None = None
    trash_reminder_enabled: bool | None = None
    trash_reminder_time: str | None = None
    user_name: str | None = None


class PushSubscriptionRequest(BaseModel):
    endpoint: str
    keys: dict  # {p256dh: ..., auth: ...}


class PushSubscribeResponse(BaseModel):
    success: bool
    message: str


class AuthLogin(BaseModel):
    password: str


class AuthToken(BaseModel):
    token: str
    expires_in: int


class HistoryEntry(BaseModel):
    task_id: int
    task_title: str
    category: str
    zone: str
    completed_at: datetime
    completed_by: str


class HistoryResponse(BaseModel):
    entries: list[HistoryEntry]
    total: int
    date_range: tuple[datetime | None, datetime | None]
