from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List

from app.db.models import User, Task, AgentMessage, TaskStatus


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
        .options(selectinload(Task.messages))
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
