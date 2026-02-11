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
from app.agents.interaction_manager import InteractionManager

settings = get_settings()

# Thresholds for stuck detection
MAX_TOOL_DENIALS = 3          # User denied tool X times → ask for guidance
MAX_CONSECUTIVE_ERRORS = 3    # Tool errors in a row → ask for guidance
MAX_REVISION_ROUNDS = 3       # Reviewer sent back X times → ask user
MAX_EMPTY_MESSAGES = 5        # Agent producing empty/useless output → stuck

# Stuck signal keywords agents can emit
STUCK_SIGNALS = [
    "AGENT_STUCK", "CANNOT_PROCEED", "NEED_USER_HELP",
    "UNABLE_TO_COMPLETE", "BLOCKED"
]


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
    """Process a task through the multi-agent workflow with stuck detection."""
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

            # Stuck detection counters
            tool_denial_count = 0
            consecutive_error_count = 0
            revision_count = 0
            empty_message_count = 0
            user_cancelled = False

            async for message in team.run_stream(task=initial_message):
                if user_cancelled:
                    break

                # Extract message content based on type
                if hasattr(message, 'source') and hasattr(message, 'content'):
                    agent_name = message.source
                    content = message.content

                    # Save message to database
                    await create_agent_message(db, task_id, agent_name, content)

                    # Broadcast message to connected clients
                    await send_agent_message(task_id, agent_name, content)

                    # === STUCK DETECTION ===

                    # 1. Check for explicit stuck signals from agents
                    if any(signal in content for signal in STUCK_SIGNALS):
                        # Extract reason from agent message
                        reason = _extract_stuck_reason(content)
                        guidance = await InteractionManager.request_guidance(
                            task_id=task_id,
                            reason=f"Agent '{agent_name}' reported it cannot proceed",
                            context=reason,
                        )
                        if guidance and not guidance.get("cancelled"):
                            user_instruction = guidance.get("values", {}).get("guidance", "")
                            if user_instruction.lower() in ("cancel", "stop", "abort"):
                                user_cancelled = True
                                continue
                            # Inject user guidance as a system message
                            await create_agent_message(db, task_id, "User", f"User guidance: {user_instruction}")
                            await send_agent_message(task_id, "User", f"User guidance: {user_instruction}")
                        else:
                            user_cancelled = True
                            continue

                    # 2. Track tool denials
                    if "was denied by user" in content or "cancelled by user" in content:
                        tool_denial_count += 1
                        consecutive_error_count = 0  # Reset error count on denial (different issue)

                        if tool_denial_count >= MAX_TOOL_DENIALS:
                            guidance = await InteractionManager.request_guidance(
                                task_id=task_id,
                                reason=f"You have denied {tool_denial_count} tool actions",
                                context="The agent keeps trying actions you don't approve. Please tell the agent what approach to take instead.",
                            )
                            tool_denial_count = 0  # Reset after asking
                            if guidance and not guidance.get("cancelled"):
                                user_instruction = guidance.get("values", {}).get("guidance", "")
                                if user_instruction.lower() in ("cancel", "stop", "abort"):
                                    user_cancelled = True
                                    continue
                                await create_agent_message(db, task_id, "User", f"User guidance: {user_instruction}")
                                await send_agent_message(task_id, "User", f"User guidance: {user_instruction}")
                            else:
                                user_cancelled = True
                                continue

                    # 3. Track tool errors
                    if "Failed to" in content or "Error:" in content:
                        consecutive_error_count += 1
                        if consecutive_error_count >= MAX_CONSECUTIVE_ERRORS:
                            guidance = await InteractionManager.request_guidance(
                                task_id=task_id,
                                reason=f"Agent encountered {consecutive_error_count} consecutive errors",
                                context=content[:500],
                            )
                            consecutive_error_count = 0
                            if guidance and not guidance.get("cancelled"):
                                user_instruction = guidance.get("values", {}).get("guidance", "")
                                if user_instruction.lower() in ("cancel", "stop", "abort"):
                                    user_cancelled = True
                                    continue
                                await create_agent_message(db, task_id, "User", f"User guidance: {user_instruction}")
                                await send_agent_message(task_id, "User", f"User guidance: {user_instruction}")
                            else:
                                user_cancelled = True
                                continue
                    else:
                        consecutive_error_count = 0  # Reset on success

                    # 4. Track revision loops
                    if agent_name == "Reviewer" and "NEEDS_REVISION" in content:
                        revision_count += 1
                        if revision_count >= MAX_REVISION_ROUNDS:
                            guidance = await InteractionManager.request_guidance(
                                task_id=task_id,
                                reason=f"Task has been sent back for revision {revision_count} times",
                                context="The Reviewer keeps finding issues. The agent might be going in circles. You can provide specific instructions, simplify the task, or cancel it.",
                            )
                            revision_count = 0
                            if guidance and not guidance.get("cancelled"):
                                user_instruction = guidance.get("values", {}).get("guidance", "")
                                if user_instruction.lower() in ("cancel", "stop", "abort"):
                                    user_cancelled = True
                                    continue
                                await create_agent_message(db, task_id, "User", f"User guidance: {user_instruction}")
                                await send_agent_message(task_id, "User", f"User guidance: {user_instruction}")
                            else:
                                user_cancelled = True
                                continue

                    # 5. Track empty/very short messages (agent confused)
                    if len(content.strip()) < 20:
                        empty_message_count += 1
                        if empty_message_count >= MAX_EMPTY_MESSAGES:
                            guidance = await InteractionManager.request_guidance(
                                task_id=task_id,
                                reason="Agent appears to be confused or stuck in a loop",
                                context="The agent has produced several empty or very short responses. It may not understand the task.",
                            )
                            empty_message_count = 0
                            if guidance and not guidance.get("cancelled"):
                                user_instruction = guidance.get("values", {}).get("guidance", "")
                                if user_instruction.lower() in ("cancel", "stop", "abort"):
                                    user_cancelled = True
                                    continue
                                await create_agent_message(db, task_id, "User", f"User guidance: {user_instruction}")
                                await send_agent_message(task_id, "User", f"User guidance: {user_instruction}")
                            else:
                                user_cancelled = True
                                continue
                    else:
                        empty_message_count = 0

                    # === PHASE TRACKING (existing logic) ===
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

            # Scan workspace for files created by tools (skip temp screenshots for privacy)
            task_dir = Path("workspace") / f"task_{task_id}"
            if task_dir.exists():
                for file_path in task_dir.iterdir():
                    if file_path.is_file():
                        await create_task_file(
                            db, task_id, file_path.name,
                            str(file_path), file_path.suffix,
                            file_path.stat().st_size
                        )
                # Cleanup temp screenshots after task completes
                temp_dir = task_dir / "temp_screenshots"
                if temp_dir.exists():
                    for f in temp_dir.iterdir():
                        try:
                            f.unlink()
                        except Exception:
                            pass
                    try:
                        temp_dir.rmdir()
                    except Exception:
                        pass

            if user_cancelled:
                await update_task_status(db, task_id, TaskStatus.FAILED)
                await create_agent_message(db, task_id, "System", "Task stopped by user.")
                await send_status_update(task_id, "failed")
                await send_agent_message(task_id, "System", "Task stopped by user.")
            else:
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


def _extract_stuck_reason(content: str) -> str:
    """Extract the reason from an agent's stuck message."""
    for signal in STUCK_SIGNALS:
        if signal in content:
            # Get text after the signal keyword
            idx = content.index(signal) + len(signal)
            reason = content[idx:].strip().lstrip(":").lstrip("-").strip()
            if reason:
                return reason[:500]
    return content[:500]
