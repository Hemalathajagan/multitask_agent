from pathlib import Path

_browser = None
_page = None


async def _get_page():
    global _browser, _page
    if _page is None:
        from playwright.async_api import async_playwright
        pw = await async_playwright().start()
        _browser = await pw.chromium.launch(headless=True)
        _page = await _browser.new_page()
    return _page


async def browser_navigate(url: str) -> str:
    """Navigate browser to a URL and return page title.

    Args:
        url: The full URL to navigate to (e.g., https://google.com).
    """
    try:
        page = await _get_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        title = await page.title()
        return f"Navigated to: {title} ({url})"
    except Exception as e:
        return f"Navigation failed: {str(e)}"


async def browser_fill_form(selector: str, value: str) -> str:
    """Fill a form field identified by CSS selector.

    Args:
        selector: CSS selector for the form field (e.g., 'input[name=email]').
        value: The value to fill in the field.
    """
    try:
        page = await _get_page()
        await page.fill(selector, value)
        return f"Filled '{selector}' with value."
    except Exception as e:
        return f"Fill form failed: {str(e)}"


async def browser_click(selector: str) -> str:
    """Click an element identified by CSS selector.

    Args:
        selector: CSS selector for the element to click (e.g., 'button[type=submit]').
    """
    try:
        page = await _get_page()
        await page.click(selector)
        return f"Clicked element: {selector}"
    except Exception as e:
        return f"Click failed: {str(e)}"


async def browser_screenshot(task_id: str, filename: str = "screenshot.png") -> str:
    """Take a screenshot of the current browser page.

    Args:
        task_id: The task ID for saving the file.
        filename: Name of the screenshot file (default: screenshot.png).
    """
    try:
        page = await _get_page()
        path = Path("workspace") / f"task_{task_id}" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(path), full_page=True)
        return f"Screenshot saved: {path}"
    except Exception as e:
        return f"Screenshot failed: {str(e)}"


async def browser_get_text(selector: str = "body") -> str:
    """Extract text content from an element on the page.

    Args:
        selector: CSS selector for the element (default: 'body' for full page text).
    """
    try:
        page = await _get_page()
        text = await page.inner_text(selector)
        if len(text) > 5000:
            text = text[:5000] + "\n\n[Content truncated...]"
        return text
    except Exception as e:
        return f"Get text failed: {str(e)}"


async def browser_close() -> str:
    """Close the browser session."""
    global _browser, _page
    try:
        if _browser:
            await _browser.close()
            _browser = None
            _page = None
        return "Browser closed."
    except Exception as e:
        return f"Close failed: {str(e)}"
