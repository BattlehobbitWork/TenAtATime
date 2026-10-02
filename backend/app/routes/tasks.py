"""Task routes — get today's tasks, complete tasks, pain day mode."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, Task, TaskCompletion, UserSetting
from app.services import rotation
from app.models.schemas import (
    TodaySummary, TaskOut, CompleteTaskRequest, CompleteTaskResponse,
    UndoCompletionRequest, PainDayTask, MaintenanceOut,
)

router = APIRouter()


def _task_to_out(t: Task) -> TaskOut:
    return TaskOut(
        id=t.id, title=t.title, description=t.description or "",
        category=t.category, zone=t.zone or "",
        estimated_minutes=t.estimated_minutes,
        pain_day_eligible=t.pain_day_eligible,
        pain_day_priority=t.pain_day_priority,
        day_of_week=t.day_of_week, week_pattern=t.week_pattern,
        zone_week=t.zone_week, month_week=t.month_week,
        frequency_days=t.frequency_days, sort_order=t.sort_order,
        is_active=t.is_active,
        is_done_today=getattr(t, "is_done_today", False),
    )


@router.get("/tasks/today", response_model=TodaySummary)
async def get_today(db: AsyncSession = Depends(get_db)):
    """Get all tasks active today with completion status."""
    tasks = (await db.execute(select(Task))).scalars().all()
    completions = (await db.execute(select(TaskCompletion))).scalars().all()

    summary = rotation.get_today_summary(list(tasks), list(completions))

    return TodaySummary(
        date=summary["date"],
        daily=[_task_to_out(t) for t in summary["daily"]],
        weekly=[_task_to_out(t) for t in summary["weekly"]],
        zone=[_task_to_out(t) for t in summary["zone"]],
        monthly=[_task_to_out(t) for t in summary["monthly"]],
        maintenance=[
            MaintenanceOut(
                task=_task_to_out(m["task"]),
                last_completed=m.get("last_completed"),
                due_date=m.get("due_date"),
                days_until_due=m["days_until_due"],
                is_due_soon=m["is_due_soon"],
                is_done_today=m.get("is_done_today", False),
            )
            for m in summary["maintenance"]
        ],
        completed_count=summary["completed_count"],
    )


@router.post("/tasks/complete", response_model=CompleteTaskResponse)
async def complete_task(req: CompleteTaskRequest, db: AsyncSession = Depends(get_db)):
    """Mark a task as complete for today (or a specific date)."""
    occ_date = req.occurrence_date or date.today().isoformat()

    # Check if already completed for this occurrence
    existing = await db.execute(
        select(TaskCompletion).where(
            TaskCompletion.task_id == req.task_id,
            TaskCompletion.occurrence_date == occ_date,
        )
    )
    if existing.scalar_one_or_none():
        return CompleteTaskResponse(success=True, message="Already done -- nice.")

    completion = TaskCompletion(
        task_id=req.task_id,
        occurrence_date=occ_date,
        completed_by="amy",
    )
    db.add(completion)
    await db.commit()

    # Check if this was a pain day task
    pain_setting = await db.scalar(
        select(UserSetting).where(UserSetting.key == "pain_day_mode")
    )
    is_pain_day = pain_setting and pain_setting.value == "true"

    if is_pain_day:
        return CompleteTaskResponse(success=True, message="This is enough. You took care of something. The rest can wait.")
    return CompleteTaskResponse(success=True, message="Done.")


@router.delete("/tasks/complete/{completion_id}", response_model=CompleteTaskResponse)
async def undo_completion(completion_id: int, db: AsyncSession = Depends(get_db)):
    """Undo a task completion (if you accidentally marked it done)."""
    result = await db.execute(
        delete(TaskCompletion).where(TaskCompletion.id == completion_id)
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Completion not found")
    return CompleteTaskResponse(success=True, message="Undone. No worries.")


@router.get("/tasks/pain-day", response_model=PainDayTask)
async def get_pain_day_task(db: AsyncSession = Depends(get_db)):
    """Get the single highest-impact task for pain day mode."""
    tasks = (await db.execute(select(Task))).scalars().all()
    completions = (await db.execute(select(TaskCompletion))).scalars().all()

    task = rotation.get_pain_day_task(list(tasks), list(completions))

    if task is None:
        return PainDayTask(task=None, message="Everything pain-day-eligible is done. Rest is okay too.")

    return PainDayTask(
        task=_task_to_out(task),
        message="One small thing. This is enough.",
    )


@router.get("/tasks/history")
async def get_history(days: int = 30, db: AsyncSession = Depends(get_db)):
    """Get completion history for patterns. Never punitive -- just facts."""
    from datetime import datetime, timedelta, timezone
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    completions = (await db.execute(
        select(TaskCompletion, Task)
        .join(Task, TaskCompletion.task_id == Task.id)
        .where(TaskCompletion.completed_at >= cutoff)
        .order_by(TaskCompletion.completed_at.desc())
    )).all()

    entries = [
        {
            "task_id": c.task_id,
            "task_title": t.title,
            "category": t.category,
            "zone": t.zone or "",
            "completed_at": c.completed_at.isoformat() if c.completed_at else "",
            "completed_by": c.completed_by,
        }
        for c, t in completions
    ]

    return {
        "entries": entries,
        "total": len(entries),
        "days": days,
    }
