import asyncio
from pathlib import Path
from typing import Optional
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

from app.config import get_settings
from app.agents.planner import create_planner_agent
from app.agents.executor import create_executor_agent
from app.agents.reviewer import create_reviewer_agent
from app.db.database import AsyncSessionLocal
from app.db.crud import (
    update_task_status, update_task_plan, update_task_execution,
    update_task_review, create_agent_message, get_task, create_task_file
)
from app.db.models import TaskStatus
from app.agents.tools._context import set_current_task_id

settings = get_settings()


SELECTOR_PROMPT = """You are the orchestrator for a multi-agent task completion system.
Based on the conversation history, select the most appropriate agent to speak next.

Available agents:
- Planner: Creates detailed task plans. Should go first to analyze and break down the objective.
- Executor: Executes the plan. Should work after the Planner has created a plan.
- Reviewer: Reviews completed work. Should review after the Executor has completed execution.

Workflow:
1. Planner creates the plan first
2. Executor executes each subtask
3. Reviewer validates the work
4. If Reviewer finds issues, Executor fixes them
5. Process ends when Reviewer approves with "TASK_COMPLETE"

Select the agent whose turn it is based on the conversation state."""


async def process_task(task_id: int):
    """Process a task through the multi-agent workflow."""
    async with AsyncSessionLocal() as db:
        # Get the task
        task = await get_task(db, task_id)
        if not task:
            return

        try:
            # Set task ID context for tool confirmation flow
            set_current_task_id(task_id)

            # Update status to planning
            await update_task_status(db, task_id, TaskStatus.PLANNING)

            # Broadcast status update
            from app.api.websocket import send_status_update, send_agent_message
            await send_status_update(task_id, "planning")

            # Create model client
            model_client = OpenAIChatCompletionClient(
                model="gpt-4o-mini",
                api_key=settings.openai_api_key,
            )

            # Create agents
            planner = create_planner_agent(model_client)
            executor = create_executor_agent(model_client)
            reviewer = create_reviewer_agent(model_client)

            # Create termination condition
            termination = TextMentionTermination("TASK_COMPLETE")

            # Create the selector group chat
            team = SelectorGroupChat(
                participants=[planner, executor, reviewer],
                model_client=model_client,
                termination_condition=termination,
                selector_prompt=SELECTOR_PROMPT,
            )

            # Initial message with the task objective and task ID for tool usage
            initial_message = f"""## Task Objective

Task ID: {task_id}

{task.objective}

Please begin by creating a detailed plan to accomplish this objective."""

            # Run the team and collect messages
            plan_content = []
            execution_content = []
            review_content = []
            current_phase = "planning"

            async for message in team.run_stream(task=initial_message):
                # Extract message content based on type
                if hasattr(message, 'source') and hasattr(message, 'content'):
                    agent_name = message.source
                    content = message.content

                    # Save message to database
                    await create_agent_message(db, task_id, agent_name, content)

                    # Broadcast message to connected clients
                    await send_agent_message(task_id, agent_name, content)

                    # Track content by phase
                    if agent_name == "Planner":
                        plan_content.append(content)
                        if "PLAN_COMPLETE" in content and current_phase == "planning":
                            current_phase = "executing"
                            await update_task_status(db, task_id, TaskStatus.EXECUTING)
                            await send_status_update(task_id, "executing")
                    elif agent_name == "Executor":
                        execution_content.append(content)
                        if "EXECUTION_COMPLETE" in content and current_phase == "executing":
                            current_phase = "reviewing"
                            await update_task_status(db, task_id, TaskStatus.REVIEWING)
                            await send_status_update(task_id, "reviewing")
                    elif agent_name == "Reviewer":
                        review_content.append(content)

            # Update task with results
            if plan_content:
                await update_task_plan(db, task_id, "\n\n".join(plan_content))
            if execution_content:
                await update_task_execution(db, task_id, "\n\n".join(execution_content))
            if review_content:
                await update_task_review(db, task_id, "\n\n".join(review_content))

            # Scan workspace for files created by tools
            task_dir = Path("workspace") / f"task_{task_id}"
            if task_dir.exists():
                for file_path in task_dir.iterdir():
                    if file_path.is_file():
                        await create_task_file(
                            db, task_id, file_path.name,
                            str(file_path), file_path.suffix,
                            file_path.stat().st_size
                        )

            # Mark task as completed
            await update_task_status(db, task_id, TaskStatus.COMPLETED)
            await send_status_update(task_id, "completed")

        except Exception as e:
            # Mark task as failed
            await update_task_status(db, task_id, TaskStatus.FAILED)
            await create_agent_message(db, task_id, "System", f"Error: {str(e)}")

            from app.api.websocket import send_status_update, send_agent_message
            await send_status_update(task_id, "failed")
            await send_agent_message(task_id, "System", f"Error: {str(e)}")
