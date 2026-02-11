from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.db.crud import (
    create_task, get_task, get_user_tasks, update_task_status,
    update_task_objective, reset_task_for_rerun, delete_task_messages,
    get_scheduled_tasks
)
from app.db.models import TaskStatus, User
from app.scheduler import schedule_task_execution, cancel_scheduled_task
from app.auth.dependencies import get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskCreateResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task and start agent processing (or schedule for later)."""
    task = await create_task(
        db, current_user.id, task_data.objective,
        scheduled_for=task_data.scheduled_for
    )

    if task_data.scheduled_for:
        # Schedule for future execution
        schedule_task_execution(task.id, task_data.scheduled_for)
    else:
        # Start agent processing immediately
        from app.agents.orchestrator import process_task
        background_tasks.add_task(process_task, task.id)

    return task


@router.get("/", response_model=List[TaskListResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """List all tasks for the current user."""
    tasks = await get_user_tasks(db, current_user.id, limit=limit)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_details(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific task."""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    # Manually construct response to avoid async serialization issues
    return {
        "id": task.id,
        "objective": task.objective,
        "status": task.status,
        "plan": task.plan,
        "execution_result": task.execution_result,
        "review_result": task.review_result,
        "scheduled_for": task.scheduled_for,
        "is_scheduled": task.is_scheduled or False,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "messages": [
            {
                "id": msg.id,
                "agent_name": msg.agent_name,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in task.messages
        ],
        "files": [
            {
                "id": f.id,
                "filename": f.filename,
                "file_path": f.file_path,
                "file_type": f.file_type,
                "size_bytes": f.size_bytes,
                "created_at": f.created_at
            }
            for f in (task.files or [])
        ]
    }


@router.put("/{task_id}", response_model=TaskCreateResponse)
async def rename_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rename a task (update objective)."""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task"
        )

    updated_task = await update_task_objective(db, task_id, task_data.objective)
    return updated_task


@router.post("/{task_id}/rerun", response_model=TaskCreateResponse)
async def rerun_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Re-run an existing task with the same objective."""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task"
        )

    # Delete old messages
    await delete_task_messages(db, task_id)

    # Reset task for re-running
    updated_task = await reset_task_for_rerun(db, task_id)

    # Start agent processing in background
    from app.agents.orchestrator import process_task
    background_tasks.add_task(process_task, task_id)

    return updated_task


@router.post("/{task_id}/continue", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
async def continue_task(
    task_id: int,
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a follow-up task based on a previous task."""
    original_task = await get_task(db, task_id)
    if not original_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original task not found"
        )
    if original_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    # Create context from previous task
    context = f"[Continue from previous task: {original_task.objective}]\n\n"
    if original_task.review_result:
        context += f"Previous result summary:\n{original_task.review_result[:500]}\n\n"
    context += f"New objective: {task_data.objective}"

    # Create new task with context
    new_task = await create_task(db, current_user.id, context)

    # Start agent processing in background
    from app.agents.orchestrator import process_task
    background_tasks.add_task(process_task, new_task.id)

    return new_task


@router.get("/scheduled/list", response_model=List[TaskListResponse])
async def list_scheduled_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all scheduled (future) tasks for the current user."""
    tasks = await get_scheduled_tasks(db, current_user.id)
    return tasks


@router.post("/{task_id}/cancel-schedule", response_model=TaskCreateResponse)
async def cancel_task_schedule(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a scheduled task before it runs."""
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if task.status != TaskStatus.SCHEDULED:
        raise HTTPException(status_code=400, detail="Task is not in scheduled state")

    cancel_scheduled_task(task_id)
    task.status = TaskStatus.FAILED
    task.is_scheduled = False
    task.review_result = "Cancelled by user before execution."
    await db.commit()
    await db.refresh(task)
    return task
