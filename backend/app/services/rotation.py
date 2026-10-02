"""Rotation engine — figures out which tasks are active on any given day.

Core principles:
- Missed tasks expire quietly, never roll forward
- No stacking, no guilt
- "Ready when you are" means today's tasks, not yesterday's backlog
"""

from datetime import date, datetime, timedelta
from app.database import Task, TaskCompletion


def _today() -> date:
    return date.today()


def _week_of_month(d: date) -> int:
    """Which week of the month (1-4). First week starts on the 1st."""
    return ((d.day - 1) // 7) + 1


def _week_of_year(d: date) -> int:
    """ISO week number (1-53)."""
    return d.isocalendar()[1]


def _rotation_week(d: date) -> str:
    """A/B/C/D rotation based on week of year.
    Week A = even weeks, B = odd, etc. Actually we cycle A,B,C,D."""
    week = _week_of_year(d)
    cycle = week % 4
    return ["A", "B", "C", "D"][cycle]


def _zone_rotation_week(d: date) -> int:
    """Which zone (1-12) is active this week. 12-week cycle from a fixed start."""
    # Start from the first week of the year for determinism
    jan1 = date(d.year, 1, 1)
    days_since = (d - jan1).days
    week_since = days_since // 7
    return (week_since % 12) + 1


def get_daily_tasks(tasks: list[Task]) -> list[Task]:
    """All daily anchor tasks — user picks 2-3."""
    return sorted(
        [t for t in tasks if t.category == "daily" and t.is_active],
        key=lambda t: t.sort_order,
    )


def get_weekly_tasks_for_day(tasks: list[Task], d: date | None = None) -> list[Task]:
    """Weekly tasks assigned to this day of week, respecting A/B/C/D rotation."""
    if d is None:
        d = _today()
    dow = d.weekday()  # 0=Monday
    pattern = _rotation_week(d)

    result = []
    for t in tasks:
        if t.category != "weekly" or not t.is_active:
            continue
        if t.day_of_week != dow:
            continue
        # If task has a week_pattern (A/B/C/D), only show on matching weeks
        if t.week_pattern and t.week_pattern != pattern:
            continue
        result.append(t)

    return sorted(result, key=lambda t: t.sort_order)


def get_zone_tasks_for_week(tasks: list[Task], d: date | None = None) -> list[Task]:
    """Zone rotation tasks for the current week."""
    if d is None:
        d = _today()
    zone_week = _zone_rotation_week(d)

    result = [t for t in tasks if t.category == "zone" and t.is_active and t.zone_week == zone_week]
    return sorted(result, key=lambda t: t.sort_order)


def get_monthly_tasks_for_week(tasks: list[Task], d: date | None = None) -> list[Task]:
    """Monthly tasks assigned to this week of the month."""
    if d is None:
        d = _today()
    wom = _week_of_month(d)

    result = [t for t in tasks if t.category == "monthly" and t.is_active and t.month_week == wom]
    return sorted(result, key=lambda t: t.sort_order)


def get_maintenance_tasks(tasks: list[Task], completions: list[TaskCompletion], d: date | None = None) -> list[dict]:
    """Maintenance tasks that are due based on last completion date.

    Returns list of {task, last_completed, due_date, is_overdue} dicts.
    Overdue is a soft concept here — we just show them without shouting.
    """
    if d is None:
        d = _today()

    result = []
    for t in tasks:
        if t.category != "maintenance" or not t.is_active:
            continue

        # Find last completion for this task
        task_completions = [c for c in completions if c.task_id == t.id]
        if task_completions:
            last = max(task_completions, key=lambda c: c.completed_at)
            last_date = last.completed_at.replace(tzinfo=None)
            due_date = last_date + timedelta(days=t.frequency_days or 365)
        else:
            # Never completed — due now (but gently)
            due_date = d

        days_until_due = (due_date.date() - d).days if hasattr(due_date, 'date') else (due_date - d).days

        result.append({
            "task": t,
            "last_completed": task_completions[-1].completed_at if task_completions else None,
            "due_date": due_date,
            "days_until_due": days_until_due,
            "is_due_soon": days_until_due <= 7,
        })

    # Sort by most overdue/due soonest first
    result.sort(key=lambda x: x["days_until_due"])
    return result


def get_pain_day_task(tasks: list[Task], completions: list[TaskCompletion]) -> Task | None:
    """Select the single highest-impact pain-day-eligible task not yet done today."""
    today_str = _today().isoformat()

    # Which pain-day tasks have been completed today?
    completed_today_ids = {
        c.task_id for c in completions
        if c.occurrence_date == today_str
    }

    candidates = [
        t for t in tasks
        if t.pain_day_eligible and t.is_active and t.id not in completed_today_ids
    ]

    if not candidates:
        # Everything pain-day-eligible is done — pick the highest priority daily task
        candidates = [
            t for t in tasks
            if t.category == "daily" and t.is_active and t.id not in completed_today_ids
        ]

    if not candidates:
        return None

    # Sort by pain_day_priority (highest first)
    candidates.sort(key=lambda t: t.pain_day_priority, reverse=True)
    return candidates[0]


def get_today_summary(tasks: list[Task], completions: list[TaskCompletion], d: date | None = None) -> dict:
    """Get all tasks active today, with completion status."""
    if d is None:
        d = _today()
    today_str = d.isoformat()

    completed_today_ids = {
        c.task_id for c in completions
        if c.occurrence_date == today_str
    }

    daily = get_daily_tasks(tasks)
    weekly = get_weekly_tasks_for_day(tasks, d)
    zone = get_zone_tasks_for_week(tasks, d)
    monthly = get_monthly_tasks_for_week(tasks, d)
    maintenance = get_maintenance_tasks(tasks, completions, d)

    def mark_done(task_list):
        for t in task_list:
            t.is_done_today = t.id in completed_today_ids
        return task_list

    return {
        "date": today_str,
        "daily": mark_done(daily),
        "weekly": mark_done(weekly),
        "zone": mark_done(zone),
        "monthly": mark_done(monthly),
        "maintenance": [
            {**m, "is_done_today": m["task"].id in completed_today_ids}
            for m in maintenance
        ],
        "completed_count": len(completed_today_ids),
    }
