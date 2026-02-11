from pathlib import Path


async def desktop_screenshot(task_id: str, filename: str = "desktop_screenshot.png") -> str:
    """Take a screenshot of the entire desktop.

    Args:
        task_id: The task ID for saving the file.
        filename: Name of the screenshot file (default: desktop_screenshot.png).
    """
    try:
        import pyautogui
        path = Path("workspace") / f"task_{task_id}" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        screenshot = pyautogui.screenshot()
        screenshot.save(str(path))
        return f"Desktop screenshot saved: {path}"
    except Exception as e:
        return f"Desktop screenshot failed: {str(e)}"


async def desktop_click(x: int, y: int, button: str = "left") -> str:
    """Click at screen coordinates.

    Args:
        x: X coordinate on screen.
        y: Y coordinate on screen.
        button: Mouse button to click - 'left', 'right', or 'middle' (default: left).
    """
    try:
        import pyautogui
        pyautogui.click(x, y, button=button)
        return f"Clicked at ({x}, {y}) with {button} button."
    except Exception as e:
        return f"Desktop click failed: {str(e)}"


async def desktop_double_click(x: int, y: int) -> str:
    """Double-click at screen coordinates.

    Args:
        x: X coordinate on screen.
        y: Y coordinate on screen.
    """
    try:
        import pyautogui
        pyautogui.doubleClick(x, y)
        return f"Double-clicked at ({x}, {y})."
    except Exception as e:
        return f"Desktop double-click failed: {str(e)}"


async def desktop_type_text(text: str, interval: float = 0.05) -> str:
    """Type text using the keyboard.

    Args:
        text: The text to type.
        interval: Time between keystrokes in seconds (default: 0.05).
    """
    try:
        import pyautogui
        pyautogui.typewrite(text, interval=interval)
        return f"Typed {len(text)} characters."
    except Exception as e:
        return f"Desktop type failed: {str(e)}"


async def desktop_hotkey(keys: str) -> str:
    """Press a keyboard shortcut.

    Args:
        keys: Keyboard shortcut as comma-separated keys (e.g., 'ctrl,c' or 'ctrl,shift,s').
    """
    try:
        import pyautogui
        key_list = [k.strip() for k in keys.split(",")]
        pyautogui.hotkey(*key_list)
        return f"Pressed hotkey: {'+'.join(key_list)}"
    except Exception as e:
        return f"Desktop hotkey failed: {str(e)}"


async def desktop_move_to(x: int, y: int) -> str:
    """Move mouse cursor to screen coordinates.

    Args:
        x: X coordinate on screen.
        y: Y coordinate on screen.
    """
    try:
        import pyautogui
        pyautogui.moveTo(x, y)
        return f"Mouse moved to ({x}, {y})."
    except Exception as e:
        return f"Desktop move failed: {str(e)}"
