import json
import inspect
from typing import Callable
from app.agents.interaction_manager import InteractionManager
from app.agents.tools._context import get_current_task_id


TOOL_INPUT_SPECS = {
    "send_email": {
        "needs_input": True,
        "fields": [
            {"name": "to_address", "label": "Recipient Email", "type": "email", "required": True},
            {"name": "subject", "label": "Subject", "type": "text", "required": True},
            {"name": "body", "label": "Email Body", "type": "textarea", "required": True},
        ]
    },
    "web_search": {"needs_input": False, "confirm_only": True},
    "read_webpage": {"needs_input": False, "confirm_only": True},
    "create_file": {"needs_input": False, "confirm_only": True},
    "execute_python_code": {"needs_input": False, "confirm_only": True},
    "make_api_call": {"needs_input": False, "confirm_only": True},
    "read_csv_file": {"needs_input": False, "confirm_only": True},
    "analyze_csv_data": {"needs_input": False, "confirm_only": True},
    "browser_navigate": {"needs_input": False, "confirm_only": True},
    "browser_fill_form": {
        "needs_input": True,
        "fields": [
            {"name": "selector", "label": "CSS Selector", "type": "text", "required": True},
            {"name": "value", "label": "Value to Fill", "type": "text", "required": True},
        ]
    },
    "browser_click": {"needs_input": False, "confirm_only": True},
    "browser_screenshot": {"needs_input": False, "confirm_only": True},
    "browser_get_text": {"needs_input": False, "confirm_only": True},
    "browser_close": {"needs_input": False, "confirm_only": True},
    "desktop_screenshot": {"needs_input": False, "confirm_only": True},
    "desktop_click": {"needs_input": False, "confirm_only": True},
    "desktop_double_click": {"needs_input": False, "confirm_only": True},
    "desktop_type_text": {"needs_input": False, "confirm_only": True},
    "desktop_hotkey": {"needs_input": False, "confirm_only": True},
    "desktop_move_to": {"needs_input": False, "confirm_only": True},
}


def make_confirmed_tool(original_func: Callable, tool_name: str) -> Callable:
    """Wrap a tool function with user input collection and confirmation."""

    # Get the original signature for preserving metadata
    orig_sig = inspect.signature(original_func)

    async def confirmed_wrapper(**kwargs):
        task_id = get_current_task_id()

        if task_id is None:
            return await original_func(**kwargs)

        spec = TOOL_INPUT_SPECS.get(tool_name, {"confirm_only": True})

        # Step 1: If tool needs user input, request it
        if spec.get("needs_input"):
            missing_fields = []
            for field in spec.get("fields", []):
                param_name = field["name"]
                if param_name in kwargs and kwargs[param_name]:
                    continue
                missing_fields.append(field)

            if missing_fields:
                user_input = await InteractionManager.request_input(
                    task_id=task_id,
                    tool_name=tool_name,
                    prompt_message=f"The agent wants to use **{tool_name}**. Please provide the required information:",
                    fields=missing_fields,
                )
                if user_input is None:
                    return f"Tool {tool_name} cancelled: user did not respond in time."
                if user_input.get("cancelled"):
                    return f"Tool {tool_name} cancelled by user."
                for key, value in user_input.get("values", {}).items():
                    kwargs[key] = value

        # Step 2: Confirmation
        param_summary = {k: str(v)[:200] for k, v in kwargs.items() if k != "task_id"}
        action_desc = f"Execute **{tool_name}**"

        confirmed = await InteractionManager.request_confirmation(
            task_id=task_id,
            tool_name=tool_name,
            action_description=action_desc,
            parameters=param_summary,
        )

        if not confirmed:
            return f"Tool {tool_name} was denied by user. Please adjust your approach or try a different tool."

        # Step 3: Execute the actual tool
        return await original_func(**kwargs)

    # Preserve function metadata for AutoGen's FunctionTool
    confirmed_wrapper.__name__ = original_func.__name__
    confirmed_wrapper.__doc__ = original_func.__doc__
    confirmed_wrapper.__annotations__ = original_func.__annotations__
    confirmed_wrapper.__signature__ = orig_sig

    return confirmed_wrapper
