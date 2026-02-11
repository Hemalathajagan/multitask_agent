import asyncio
import json
from typing import Dict, Optional

from app.db.database import AsyncSessionLocal
from app.db.crud import (
    create_interaction_request, get_pending_interaction,
    update_task_status, get_task
)
from app.db.models import TaskStatus, InteractionType


class InteractionManager:
    """Manages pause/resume of tool execution for user interactions."""

    _events: Dict[int, asyncio.Event] = {}
    _responses: Dict[int, dict] = {}
    _task_status_before: Dict[int, str] = {}

    @classmethod
    async def request_input(
        cls,
        task_id: int,
        tool_name: str,
        prompt_message: str,
        fields: list,
        timeout: float = 300.0
    ) -> Optional[dict]:
        """Pause tool execution and request input from user."""
        async with AsyncSessionLocal() as db:
            task = await get_task(db, task_id)
            if task and task_id not in cls._task_status_before:
                cls._task_status_before[task_id] = task.status.value if task.status != TaskStatus.AWAITING_INPUT else "executing"

            interaction = await create_interaction_request(
                db, task_id,
                InteractionType.INPUT_NEEDED,
                tool_name, prompt_message,
                json.dumps(fields), None
            )
            await update_task_status(db, task_id, TaskStatus.AWAITING_INPUT)

        from app.api.websocket import send_status_update, send_input_request
        await send_status_update(task_id, "awaiting_input")
        await send_input_request(task_id, interaction.id, tool_name, prompt_message, fields)

        event = asyncio.Event()
        cls._events[interaction.id] = event

        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            response = cls._responses.pop(interaction.id, None)
        except asyncio.TimeoutError:
            response = None
        finally:
            cls._events.pop(interaction.id, None)

        # Restore previous task status
        async with AsyncSessionLocal() as db:
            prev = cls._task_status_before.pop(task_id, "executing")
            await update_task_status(db, task_id, TaskStatus(prev))
        await send_status_update(task_id, prev)

        return response

    @classmethod
    async def request_confirmation(
        cls,
        task_id: int,
        tool_name: str,
        action_description: str,
        parameters: dict,
        timeout: float = 300.0
    ) -> bool:
        """Pause tool execution and request confirmation from user."""
        async with AsyncSessionLocal() as db:
            task = await get_task(db, task_id)
            if task and task_id not in cls._task_status_before:
                cls._task_status_before[task_id] = task.status.value if task.status != TaskStatus.AWAITING_INPUT else "executing"

            preview = {
                "tool": tool_name,
                "description": action_description,
                "parameters": parameters
            }
            interaction = await create_interaction_request(
                db, task_id,
                InteractionType.CONFIRMATION,
                tool_name, action_description,
                None, json.dumps(preview)
            )
            await update_task_status(db, task_id, TaskStatus.AWAITING_INPUT)

        from app.api.websocket import send_status_update, send_confirmation_request
        await send_status_update(task_id, "awaiting_input")
        await send_confirmation_request(task_id, interaction.id, tool_name, action_description, parameters)

        event = asyncio.Event()
        cls._events[interaction.id] = event

        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            response = cls._responses.pop(interaction.id, {})
            confirmed = response.get("confirmed", False)
        except asyncio.TimeoutError:
            confirmed = False
        finally:
            cls._events.pop(interaction.id, None)

        async with AsyncSessionLocal() as db:
            prev = cls._task_status_before.pop(task_id, "executing")
            await update_task_status(db, task_id, TaskStatus(prev))
        await send_status_update(task_id, prev)

        return confirmed

    @classmethod
    async def request_guidance(
        cls,
        task_id: int,
        reason: str,
        context: str,
        options: list = None,
        timeout: float = 600.0
    ) -> Optional[dict]:
        """Pause the entire workflow and ask the user for guidance when agent is stuck."""
        async with AsyncSessionLocal() as db:
            task = await get_task(db, task_id)
            if task and task_id not in cls._task_status_before:
                cls._task_status_before[task_id] = task.status.value if task.status != TaskStatus.AWAITING_INPUT else "executing"

            fields = [
                {"name": "guidance", "label": "What should the agent do?", "type": "textarea", "required": True}
            ]
            prompt = f"**Agent needs help**\n\n**Reason:** {reason}\n\n**Context:** {context}"

            interaction = await create_interaction_request(
                db, task_id,
                InteractionType.AGENT_STUCK,
                "system", prompt,
                json.dumps(fields), json.dumps({"reason": reason, "context": context, "options": options or []})
            )
            await update_task_status(db, task_id, TaskStatus.AWAITING_INPUT)

        from app.api.websocket import send_status_update
        await send_status_update(task_id, "awaiting_input")

        event = asyncio.Event()
        cls._events[interaction.id] = event

        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            response = cls._responses.pop(interaction.id, None)
        except asyncio.TimeoutError:
            response = {"values": {"guidance": "cancel"}}
        finally:
            cls._events.pop(interaction.id, None)

        async with AsyncSessionLocal() as db:
            prev = cls._task_status_before.pop(task_id, "executing")
            await update_task_status(db, task_id, TaskStatus(prev))
        from app.api.websocket import send_status_update as send_update
        await send_update(task_id, prev)

        return response

    @classmethod
    def resolve(cls, request_id: int, response_data: dict):
        """Called by API endpoint when user responds. Unblocks the waiting tool."""
        cls._responses[request_id] = response_data
        event = cls._events.get(request_id)
        if event:
            event.set()
