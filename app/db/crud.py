from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List

from datetime import datetime
from app.db.models import User, Task, AgentMessage, TaskFile, InteractionRequest, TaskStatus, InteractionType


# User CRUD
async def create_user(db: AsyncSession, email: str, username: str, hashed_password: str) -> User:
    user = User(email=email, username=username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user_profile(
    db: AsyncSession,
    user_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None
) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if user:
        if username:
            user.username = username
        if email:
            user.email = email
        await db.commit()
        await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user_id: int, hashed_password: str) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if user:
        user.hashed_password = hashed_password
        await db.commit()
        await db.refresh(user)
    return user


async def update_user_photo(db: AsyncSession, user_id: int, profile_photo: str) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if user:
        user.profile_photo = profile_photo
        await db.commit()
        await db.refresh(user)
    return user


# Task CRUD
async def create_task(db: AsyncSession, user_id: int, objective: str) -> Task:
    task = Task(user_id=user_id, objective=objective, status=TaskStatus.PENDING)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.messages), selectinload(Task.files))
        .where(Task.id == task_id)
    )
    return result.scalar_one_or_none()


async def get_user_tasks(db: AsyncSession, user_id: int, limit: int = 50) -> List[Task]:
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def update_task_status(db: AsyncSession, task_id: int, status: TaskStatus) -> Optional[Task]:
    task = await get_task(db, task_id)
    if task:
        task.status = status
        await db.commit()
        await db.refresh(task)
    return task


async def update_task_plan(db: AsyncSession, task_id: int, plan: str) -> Optional[Task]:
    task = await get_task(db, task_id)
    if task:
        task.plan = plan
        await db.commit()
        await db.refresh(task)
    return task


async def update_task_execution(db: AsyncSession, task_id: int, execution_result: str) -> Optional[Task]:
    task = await get_task(db, task_id)
    if task:
        task.execution_result = execution_result
        await db.commit()
        await db.refresh(task)
    return task


async def update_task_review(db: AsyncSession, task_id: int, review_result: str) -> Optional[Task]:
    task = await get_task(db, task_id)
    if task:
        task.review_result = review_result
        await db.commit()
        await db.refresh(task)
    return task


async def update_task_objective(db: AsyncSession, task_id: int, objective: str) -> Optional[Task]:
    """Update the task objective (rename)."""
    task = await get_task(db, task_id)
    if task:
        task.objective = objective
        await db.commit()
        await db.refresh(task)
    return task


async def reset_task_for_rerun(db: AsyncSession, task_id: int, new_objective: Optional[str] = None) -> Optional[Task]:
    """Reset a task to pending state for re-running."""
    task = await get_task(db, task_id)
    if task:
        if new_objective:
            task.objective = new_objective
        task.status = TaskStatus.PENDING
        task.plan = None
        task.execution_result = None
        task.review_result = None
        await db.commit()
        await db.refresh(task)
    return task


async def delete_task_messages(db: AsyncSession, task_id: int):
    """Delete all messages for a task."""
    from sqlalchemy import delete
    await db.execute(delete(AgentMessage).where(AgentMessage.task_id == task_id))
    await db.commit()


# AgentMessage CRUD
async def create_agent_message(db: AsyncSession, task_id: int, agent_name: str, content: str) -> AgentMessage:
    message = AgentMessage(task_id=task_id, agent_name=agent_name, content=content)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_task_messages(db: AsyncSession, task_id: int) -> List[AgentMessage]:
    result = await db.execute(
        select(AgentMessage)
        .where(AgentMessage.task_id == task_id)
        .order_by(AgentMessage.timestamp)
    )
    return result.scalars().all()


# TaskFile CRUD
async def create_task_file(
    db: AsyncSession, task_id: int, filename: str,
    file_path: str, file_type: str, size_bytes: int
) -> TaskFile:
    task_file = TaskFile(
        task_id=task_id, filename=filename,
        file_path=file_path, file_type=file_type,
        size_bytes=size_bytes
    )
    db.add(task_file)
    await db.commit()
    await db.refresh(task_file)
    return task_file


async def get_task_files(db: AsyncSession, task_id: int) -> List[TaskFile]:
    result = await db.execute(
        select(TaskFile)
        .where(TaskFile.task_id == task_id)
        .order_by(TaskFile.created_at)
    )
    return result.scalars().all()


# InteractionRequest CRUD
async def create_interaction_request(
    db: AsyncSession, task_id: int, interaction_type: InteractionType,
    tool_name: str, prompt_message: str,
    fields_json: Optional[str] = None, preview_json: Optional[str] = None
) -> InteractionRequest:
    interaction = InteractionRequest(
        task_id=task_id, interaction_type=interaction_type,
        tool_name=tool_name, prompt_message=prompt_message,
        fields_json=fields_json, preview_json=preview_json,
        status="pending"
    )
    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)
    return interaction


async def get_pending_interaction(db: AsyncSession, task_id: int) -> Optional[InteractionRequest]:
    result = await db.execute(
        select(InteractionRequest)
        .where(InteractionRequest.task_id == task_id, InteractionRequest.status == "pending")
        .order_by(InteractionRequest.created_at.desc())
    )
    return result.scalar_one_or_none()


async def respond_to_interaction(
    db: AsyncSession, request_id: int, response_json: str
) -> Optional[InteractionRequest]:
    result = await db.execute(
        select(InteractionRequest).where(InteractionRequest.id == request_id)
    )
    interaction = result.scalar_one_or_none()
    if interaction:
        interaction.response_json = response_json
        interaction.status = "responded"
        interaction.responded_at = datetime.utcnow()
        await db.commit()
        await db.refresh(interaction)
    return interaction
