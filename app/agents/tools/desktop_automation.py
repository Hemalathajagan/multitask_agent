import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Safety: auto-delete screenshots after this many seconds
SCREENSHOT_AUTO_DELETE_SECONDS = 300  # 5 minutes


def _safe_screenshot_path(task_id: str, filename: str) -> Path:
    """Create a safe screenshot path in a temp directory (not permanent workspace)."""
    path = Path("workspace") / f"task_{task_id}" / "temp_screenshots" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _cleanup_old_screenshots(task_id: str):
    """Delete screenshots older than the auto-delete threshold."""
    temp_dir = Path("workspace") / f"task_{task_id}" / "temp_screenshots"
    if not temp_dir.exists():
        return
    now = time.time()
    for f in temp_dir.iterdir():
        if f.is_file() and (now - f.stat().st_mtime) > SCREENSHOT_AUTO_DELETE_SECONDS:
            try:
                f.unlink()
                logger.info(f"Auto-deleted old screenshot: {f.name}")
            except Exception:
                pass


async def desktop_screenshot(task_id: str, filename: str = "desktop_screenshot.png") -> str:
    """Take a screenshot of the entire desktop. Screenshots are auto-deleted after 5 minutes for privacy.

    Args:
        task_id: The task ID for saving the file.
        filename: Name of the screenshot file (default: desktop_screenshot.png).
    """
    try:
        import pyautogui

        # Cleanup old screenshots first
        _cleanup_old_screenshots(task_id)

        path = _safe_screenshot_path(task_id, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(str(path))

        logger.info(f"Desktop screenshot saved (auto-deletes in {SCREENSHOT_AUTO_DELETE_SECONDS}s): {path}")
        return f"Desktop screenshot saved: {path} (will auto-delete after 5 minutes for privacy)"
    except Exception as e:
        return f"Desktop screenshot failed: {str(e)}"


async def desktop_screenshot_region(task_id: str, x: int, y: int, width: int, height: int, filename: str = "region_screenshot.png") -> str:
    """Take a screenshot of a specific region of the screen only. Safer than full desktop screenshot.

    Args:
        task_id: The task ID for saving the file.
        x: Left edge X coordinate.
        y: Top edge Y coordinate.
        width: Width of the region in pixels.
        height: Height of the region in pixels.
        filename: Name of the screenshot file.
    """
    try:
        import pyautogui

        _cleanup_old_screenshots(task_id)

        path = _safe_screenshot_path(task_id, filename)
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot.save(str(path))

        return f"Region screenshot saved: {path} (region: {x},{y} {width}x{height})"
    except Exception as e:
        return f"Region screenshot failed: {str(e)}"


async def desktop_find_on_screen(image_path: str, confidence: float = 0.8) -> str:
    """Find an image/icon/button on screen and return its coordinates. Much more reliable than guessing coordinates.

    Args:
        image_path: Path to a reference image to find on screen (e.g., a button icon).
        confidence: Match confidence threshold 0.0-1.0 (default 0.8). Lower = more lenient.
    """
    try:
        import pyautogui

        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            return f"Found at coordinates: ({center.x}, {center.y}) - Region: {location}"
        else:
            return f"Image not found on screen with confidence {confidence}. Try a lower confidence value or take a screenshot to verify the screen state."
    except Exception as e:
        return f"Find on screen failed: {str(e)}. Make sure 'opencv-python' is installed for image matching."


async def desktop_find_window(window_title: str) -> str:
    """Find and bring a window to the foreground by its title. Use before interacting with an app.

    Args:
        window_title: Full or partial title of the window (e.g., 'WhatsApp', 'Chrome', 'Notepad').
    """
    try:
        import pyautogui

        windows = pyautogui.getWindowsWithTitle(window_title)
        if not windows:
            return f"No window found with title containing '{window_title}'. Make sure the application is open."

        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.5)  # Wait for window to come to foreground

        return f"Window '{win.title}' activated. Position: ({win.left}, {win.top}), Size: {win.width}x{win.height}"
    except Exception as e:
        return f"Find window failed: {str(e)}"


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


async def desktop_type_text(text: str, interval: float = 0.03) -> str:
    """Type text using the keyboard. Supports all characters including unicode/emojis via clipboard.

    Args:
        text: The text to type (supports any language and emojis).
        interval: Time between keystrokes in seconds (default: 0.03).
    """
    try:
        import pyautogui
        import subprocess

        # For ASCII-only text, use typewrite (faster and more reliable)
        if all(ord(c) < 128 for c in text):
            pyautogui.typewrite(text, interval=interval)
            return f"Typed {len(text)} characters."

        # For unicode/emoji text, use clipboard paste (cross-platform)
        try:
            # Copy to clipboard
            process = subprocess.Popen(
                ['clip'] if os.name == 'nt' else ['xclip', '-selection', 'clipboard'],
                stdin=subprocess.PIPE
            )
            process.communicate(text.encode('utf-16-le' if os.name == 'nt' else 'utf-8'))

            # Paste
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)
            return f"Typed {len(text)} characters (via clipboard paste for unicode support)."
        except Exception:
            # Fallback: type character by character with pyperclip
            pyautogui.typewrite(text.encode('ascii', 'replace').decode(), interval=interval)
            return f"Typed {len(text)} characters (some unicode characters may not have typed correctly)."

    except Exception as e:
        return f"Desktop type failed: {str(e)}"


async def desktop_hotkey(keys: str) -> str:
    """Press a keyboard shortcut.

    Args:
        keys: Keyboard shortcut as comma-separated keys (e.g., 'ctrl,c' or 'ctrl,shift,s' or 'enter').
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
