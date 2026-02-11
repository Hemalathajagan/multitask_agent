import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler = None


def init_scheduler(db_url: str):
    """Initialize the APScheduler with a persistent SQLAlchemy job store."""
    global _scheduler

    # Convert async URL to sync for APScheduler job store
    sync_url = db_url.replace("sqlite+aiosqlite", "sqlite")

    jobstores = {
        "default": SQLAlchemyJobStore(url=sync_url)
    }

    _scheduler = AsyncIOScheduler(jobstores=jobstores)
    _scheduler.start()
    logger.info("Scheduler started with persistent job store")


async def _execute_scheduled_task(task_id: int):
    """Job function that runs when a scheduled task fires."""
    from app.db.database import AsyncSessionLocal
    from app.db.crud import update_task_status
    from app.db.models import TaskStatus
    from app.agents.orchestrator import process_task

    logger.info(f"Scheduled task {task_id} firing now")

    # Update status from SCHEDULED to PENDING
    async with AsyncSessionLocal() as db:
        await update_task_status(db, task_id, TaskStatus.PENDING)

    # Run the task
    await process_task(task_id)


def schedule_task_execution(task_id: int, run_at: datetime):
    """Register a task to run at a specific time."""
    global _scheduler
    if _scheduler is None:
        raise RuntimeError("Scheduler not initialized")

    job_id = f"task_{task_id}"

    # Remove existing job if any
    try:
        _scheduler.remove_job(job_id)
    except Exception:
        pass

    _scheduler.add_job(
        _execute_scheduled_task,
        trigger="date",
        run_date=run_at,
        args=[task_id],
        id=job_id,
        replace_existing=True,
    )
    logger.info(f"Task {task_id} scheduled for {run_at}")


def cancel_scheduled_task(task_id: int) -> bool:
    """Cancel a scheduled task job."""
    global _scheduler
    if _scheduler is None:
        return False

    job_id = f"task_{task_id}"
    try:
        _scheduler.remove_job(job_id)
        logger.info(f"Cancelled scheduled task {task_id}")
        return True
    except Exception:
        return False


async def load_pending_scheduled_tasks():
    """On startup, re-register all SCHEDULED tasks from the database."""
    from app.db.database import AsyncSessionLocal
    from app.db.crud import get_all_scheduled_tasks

    async with AsyncSessionLocal() as db:
        tasks = await get_all_scheduled_tasks(db)

    now = datetime.utcnow()
    for task in tasks:
        if task.scheduled_for and task.scheduled_for > now:
            schedule_task_execution(task.id, task.scheduled_for)
            logger.info(f"Re-registered scheduled task {task.id} for {task.scheduled_for}")
        elif task.scheduled_for:
            # Past due — execute immediately
            logger.info(f"Scheduled task {task.id} is past due, executing now")
            schedule_task_execution(task.id, now)


def shutdown_scheduler():
    """Gracefully shutdown the scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
