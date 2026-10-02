"""Seed the task library with all preloaded tasks from the spec."""

from app.database import async_session, Task, ReminderConfig
from sqlalchemy import select


async def seed_all():
    """Seed tasks and reminder configs if not already present."""
    async with async_session() as session:
        existing = await session.scalar(select(Task).limit(1))
        if existing:
            return  # Already seeded

        tasks = _build_task_list()
        session.add_all(tasks)

        reminders = _build_reminder_configs()
        session.add_all(reminders)

        await session.commit()


def _build_task_list() -> list[Task]:
    tasks = []

    # ============================================================
    # DAILY ANCHORS (~10 min each)
    # ============================================================
    daily_tasks = [
        ("Unload dishwasher", "Kitchen", 10, True, 90),
        ("Load + run dishwasher", "Kitchen", 10, True, 85),
        ("Wipe kitchen counters", "Kitchen", 10, True, 80),
        ("Quick kitchen floor sweep", "Kitchen", 10, False, 0),
        ("Scoop litter boxes", "Animal food area", 10, True, 75),
        ("Feed cats + fresh water", "Animal food area", 10, True, 95),
        ("Feed Sara + fresh water", "Animal food area", 10, True, 95),
        ("Take Sara out (quick yard run)", "Outdoor", 10, True, 70),
        ("5-minute surface tidy -- living room", "Living room", 5, True, 60),
        ("Make bed", "Master bedroom", 5, True, 40),
        ("Gather trash from bathrooms", "All bathrooms", 10, True, 65),
        ("Wipe down kitchen sink", "Kitchen", 5, True, 50),
    ]
    for i, (title, zone, mins, pain, prio) in enumerate(daily_tasks):
        tasks.append(Task(
            title=title, description="", category="daily", zone=zone,
            estimated_minutes=mins, pain_day_eligible=pain, pain_day_priority=prio,
            sort_order=i,
        ))

    # ============================================================
    # WEEKLY RHYTHM (assigned to specific days)
    # ============================================================
    weekly_tasks = [
        # Monday -- Surfaces & Dust
        (0, None, "Dust living room surfaces", "Living room", 10),
        (0, None, "Wipe dining table + chairs", "Dining area", 10),
        (0, None, "Dust master bedroom surfaces", "Master bedroom", 10),
        (0, None, "Quick wipe of toy room surfaces", "Toy room", 10),
        # Tuesday -- Floors
        (1, None, "Vacuum upstairs hallway + stairs", "Stairs", 15),
        (1, None, "Vacuum living room rug", "Living room", 10),
        (1, None, "Vacuum master bedroom", "Master bedroom", 10),
        (1, None, "Quick mop kitchen floor", "Kitchen", 10),
        # Wednesday -- Trash & Paper
        (2, None, "Take all trash + recycling to curb", "Outdoor", 10),
        (2, None, "Sort mail / deal with paper pile", "Entry", 10),
        (2, None, "Check fridge for old food -- toss", "Kitchen", 5),
        (2, None, "Quick sweep garage doorway", "Garage", 5),
        # Thursday -- Bathrooms (rotate A/B/C)
        (3, "A", "Main bath -- sink + mirror", "Main bath", 10),
        (3, "A", "Main bath -- toilet", "Main bath", 10),
        (3, "A", "Main bath -- quick shower spray", "Main bath", 5),
        (3, "B", "Upstairs bath -- sink + mirror", "Upstairs bath", 10),
        (3, "B", "Upstairs bath -- toilet", "Upstairs bath", 10),
        (3, "B", "Upstairs bath -- quick shower spray", "Upstairs bath", 5),
        (3, "C", "Third bath -- sink + mirror", "Third bath", 10),
        (3, "C", "Third bath -- toilet", "Third bath", 10),
        (3, "C", "Third bath -- quick shower spray", "Third bath", 5),
        # Friday -- Catch-All / Laundry
        (4, None, "Start one laundry load (sort + wash)", "Laundry room", 10),
        (4, None, "Move laundry to dryer", "Laundry room", 5),
        (4, None, "Fold + put away laundry", "Laundry room", 15),
        (4, None, "Wipe kitchen cabinet fronts", "Kitchen", 10),
        (4, None, "Clean Sara's bowls + feeding area", "Animal food area", 10),
        # Saturday -- Deeper Clean Rotation (A/B/C/D)
        (5, "A", "Scrub main shower/tub", "Main bath", 20),
        (5, "B", "Scrub upstairs shower/tub", "Upstairs bath", 20),
        (5, "C", "Mop bathroom floors", "All bathrooms", 15),
        (5, "D", "Deep vacuum living room (under furniture)", "Living room", 20),
        # Sunday -- Reset & Prep
        (6, None, "Clear upstairs landing", "Stairs landing", 10),
        (6, None, "Quick toy room tidy", "Toy room", 10),
        (6, None, "Check supplies (TP, paper towels, cleaners, pet food)", "Kitchen", 10),
        (6, None, "Wipe laundry room surfaces", "Laundry room", 5),
    ]
    for i, (dow, pattern, title, zone, mins) in enumerate(weekly_tasks):
        tasks.append(Task(
            title=title, description="", category="weekly", zone=zone,
            estimated_minutes=mins, pain_day_eligible=False, pain_day_priority=0,
            day_of_week=dow, week_pattern=pattern, sort_order=i,
        ))

    # ============================================================
    # WEEKLY ZONE ROTATION (12-week cycle, one zone per week)
    # ============================================================
    zone_tasks = [
        (1, "Entry / Behind the door", [
            "Sort items -- keep/donate/trash",
            "Wipe hooks + shelf",
            "Put away what stays",
        ]),
        (2, "Top of stairs landing", [
            "Clear all items",
            "Dust/vacuum landing",
            "Return only what belongs",
        ]),
        (3, "Medicine cabinet (main bath)", [
            "Pull everything out",
            "Check expiration dates",
            "Wipe shelves",
            "Reorganize",
        ]),
        (4, "Cat nook", [
            "Vacuum cat hair",
            "Wash blankets/pads",
            "Tidy surrounding area",
        ]),
        (5, "Under kitchen sink", [
            "Pull out items",
            "Wipe cabinet bottom",
            "Toss empties",
            "Reorganize",
        ]),
        (6, "Sara's room", [
            "Vacuum floor",
            "Wash bedding if needed",
            "Tidy toys/supplies",
        ]),
        (7, "Laundry room", [
            "Wipe machines",
            "Check/clean lint trap + dryer vent",
            "Tidy supplies",
        ]),
        (8, "Upstairs closet", [
            "Pull items not used in 6 months",
            "Dust shelves",
            "Donate/trash",
            "Reorganize",
        ]),
        (9, "Animal food area + closet", [
            "Wipe food containers",
            "Sweep spillage",
            "Check supply levels",
            "Tidy closet",
        ]),
        (10, "Utility closet / hall", [
            "Clear area",
            "Dust/vacuum",
            "Check for items that don't belong",
        ]),
        (11, "Garage doorway / entry zone", [
            "Sweep entry",
            "Tidy shoes/coats",
            "Quick declutter",
        ]),
        (12, "Toy room", [
            "Sort toys into bins",
            "Vacuum",
            "Wipe surfaces",
            "Rotate out unused toys",
        ]),
    ]
    sort_idx = 0
    for zone_week, zone_name, task_list in zone_tasks:
        for task_title in task_list:
            tasks.append(Task(
                title=task_title, description=f"Zone: {zone_name}", category="zone",
                zone=zone_name, estimated_minutes=10, pain_day_eligible=False,
                pain_day_priority=0, zone_week=zone_week, sort_order=sort_idx,
            ))
            sort_idx += 1

    # ============================================================
    # MONTHLY ROTATIONS (assigned to weeks of the month)
    # ============================================================
    monthly_tasks = [
        (1, 0, "Wipe baseboards -- one room", "Whole house", 10),
        (1, 1, "Clean inside microwave", "Kitchen", 10),
        (2, 0, "Dust blinds / window sills -- one floor", "Whole house", 10),
        (2, 1, "Clean coffee maker / kettle", "Kitchen", 10),
        (3, 0, "Wipe light switches + doorknobs -- whole house", "Whole house", 10),
        (3, 1, "Vacuum under couch cushions", "Living room", 10),
        (4, 0, "Clean fridge shelves + drawers", "Kitchen", 15),
        (4, 1, "Wipe down washer/dryer + check filter", "Laundry room", 10),
    ]
    for i, (week, weekend, title, zone, mins) in enumerate(monthly_tasks):
        tasks.append(Task(
            title=title, description="", category="monthly", zone=zone,
            estimated_minutes=mins, pain_day_eligible=False, pain_day_priority=0,
            month_week=week, sort_order=i,
        ))

    # ============================================================
    # MAINTENANCE CALENDAR
    # ============================================================
    maintenance_tasks = [
        ("Change HVAC air filter", "HVAC", 10, 60),
        ("Check smoke detector batteries", "Whole house", 10, 180),
        ("Drain water heater (sediment flush)", "Utility", 20, 180),
        ("Clean dryer vent + duct", "Laundry room", 20, 180),
        ("HVAC service check", "HVAC", 60, 365),
        ("Check gutters / downspouts", "Outdoor", 30, 365),
        ("Test sump pump", "Utility", 10, 365),
        ("Re-seal grout in bathrooms", "All bathrooms", 30, 365),
        ("Wash curtains / drapes", "Whole house", 30, 180),
        ("Rotate mattress", "Master bedroom", 10, 180),
        ("Deep clean Sara's crate / bedding", "Sara's room", 20, 90),
        ("Garage pest check + tidy", "Garage", 20, 90),
    ]
    for i, (title, zone, mins, freq) in enumerate(maintenance_tasks):
        tasks.append(Task(
            title=title, description="", category="maintenance", zone=zone,
            estimated_minutes=mins, pain_day_eligible=False, pain_day_priority=0,
            frequency_days=freq, sort_order=i,
        ))

    return tasks


def _build_reminder_configs() -> list[ReminderConfig]:
    return [
        ReminderConfig(category="daily", enabled=True, time_of_day="09:00"),
        ReminderConfig(category="weekly", enabled=True, time_of_day="08:00"),
        ReminderConfig(category="zone", enabled=True, time_of_day="09:00", day_of_week=5),  # Saturday
        ReminderConfig(category="monthly", enabled=True, time_of_day="09:00", day_of_week=5),
        ReminderConfig(category="maintenance", enabled=True, time_of_day="09:00", day_of_week=5),
        # Special: Wednesday trash reminder (evening before pickup)
        ReminderConfig(category="trash", enabled=True, time_of_day="19:00", day_of_week=2),
    ]
