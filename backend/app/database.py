"""Database setup — SQLite with async SQLAlchemy."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text, Integer, String, Boolean, DateTime, JSON, ForeignKey, UniqueConstraint, select
from datetime import datetime, timezone
import json

from app.config import settings


class Base(DeclarativeBase):
    pass


class Task(Base):
    """The task library — preloaded tasks that don't change."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50))  # daily, weekly, zone, monthly, maintenance
    zone: Mapped[str] = mapped_column(String(100), default="")  # kitchen, main bath, etc.
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=10)
    pain_day_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    pain_day_priority: Mapped[int] = mapped_column(Integer, default=0)  # higher = more impactful
    # For weekly tasks: which day of week (0=Monday)
    day_of_week: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    # For weekly tasks with sub-rotation (e.g., bathroom A/B/C): which week pattern
    week_pattern: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)  # A, B, C, D
    # For zone tasks: which zone number (1-12)
    zone_week: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    # For monthly tasks: which week of month (1-4)
    month_week: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    # For maintenance: frequency in days
    frequency_days: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    # Sort order within category
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class TaskCompletion(Base):
    """When a task was completed."""
    __tablename__ = "task_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"))
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    # For rotation-based tasks, which specific occurrence (date string YYYY-MM-DD)
    occurrence_date: Mapped[str] = mapped_column(String(20), default="")
    # Who completed it (for future multi-user)
    completed_by: Mapped[str] = mapped_column(String(50), default="amy")


class UserSetting(Base):
    """Key-value settings store."""
    __tablename__ = "user_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")

    def get_json(self):
        return json.loads(self.value) if self.value else None

    def set_json(self, val):
        self.value = json.dumps(val)


class PushSubscription(Base):
    """Web Push subscription endpoints."""
    __tablename__ = "push_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    endpoint: Mapped[str] = mapped_column(String(500))
    keys_json: Mapped[str] = mapped_column(Text)  # JSON: {p256dh: ..., auth: ...}
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ReminderConfig(Base):
    """Per-category reminder time configuration."""
    __tablename__ = "reminder_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50))  # daily, weekly, zone, monthly, maintenance
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    time_of_day: Mapped[str] = mapped_column(String(5), default="09:00")  # HH:MM
    # For weekly: which day to remind (0=Monday). For maintenance: days before due
    day_of_week: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    last_sent: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)


engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create tables and seed initial data."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed data
    from app.services.seed import seed_all
    await seed_all()


async def get_db():
    async with async_session() as session:
        yield session
