from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.db.crud import create_task, get_task, get_user_tasks, update_task_status
from app.db.models import TaskStatus, User
from app.auth.dependencies import get_current_user
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse, TaskCreateResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task and start agent processing."""
    task = await create_task(db, current_user.id, task_data.objective)

    # Start agent processing in background
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
        ]
    }
