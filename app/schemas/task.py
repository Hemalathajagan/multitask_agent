from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.db.models import TaskStatus


class TaskCreate(BaseModel):
    objective: str = Field(..., min_length=10, max_length=2000)


class TaskUpdate(BaseModel):
    objective: str = Field(..., min_length=10, max_length=2000)


class TaskCreateResponse(BaseModel):
    """Response for task creation - without messages to avoid async issues."""
    id: int
    objective: str
    status: TaskStatus
    plan: Optional[str] = None
    execution_result: Optional[str] = None
    review_result: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentMessageResponse(BaseModel):
    id: int
    agent_name: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: int
    objective: str
    status: TaskStatus
    plan: Optional[str] = None
    execution_result: Optional[str] = None
    review_result: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[AgentMessageResponse] = []

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    id: int
    objective: str
    status: TaskStatus
    created_at: datetime

    class Config:
        from_attributes = True
