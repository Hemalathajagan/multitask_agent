from autogen_core.tools import FunctionTool

from app.agents.tools.web_search import web_search, web_search_news
from app.agents.tools.web_reader import read_webpage
from app.agents.tools.email_sender import send_email
from app.agents.tools.file_manager import create_file
from app.agents.tools.code_executor import execute_python_code
from app.agents.tools.http_client import make_api_call
from app.agents.tools.csv_handler import read_csv_file, analyze_csv_data, edit_csv_file
from app.agents.tools.excel_handler import edit_excel_file
from app.agents.tools.social_media import post_to_instagram, post_to_twitter, post_to_linkedin, post_to_facebook
from app.agents.tools.browser_automation import (
    browser_navigate, browser_fill_form, browser_click,
    browser_screenshot, browser_get_text, browser_close
)
from app.agents.tools.desktop_automation import (
    desktop_screenshot, desktop_screenshot_region, desktop_find_on_screen,
    desktop_find_window, desktop_click, desktop_double_click,
    desktop_type_text, desktop_hotkey, desktop_move_to
)
from app.agents.tools.confirmed_tool import make_confirmed_tool


def get_executor_tools() -> list:
    """Return the list of FunctionTool objects for the Executor agent, all wrapped with user confirmation."""
    return [
        # Existing tools (with confirmation)
        FunctionTool(make_confirmed_tool(web_search, "web_search"), description="Search the internet using DuckDuckGo. Returns titles, URLs, and snippets."),
        FunctionTool(make_confirmed_tool(web_search_news, "web_search_news"), description="Search for recent news articles. Use this for current events, latest updates, and real-time information."),
        FunctionTool(make_confirmed_tool(read_webpage, "read_webpage"), description="Fetch and extract text content from a URL. Intelligently extracts main article content."),
        FunctionTool(make_confirmed_tool(send_email, "send_email"), description="Send an email via SMTP to a specified address. Will ask the user for email details."),
        FunctionTool(make_confirmed_tool(create_file, "create_file"), description="Create a file (txt, md, csv, json, html) in the task workspace."),
        FunctionTool(make_confirmed_tool(execute_python_code, "execute_python_code"), description="Execute Python code in a sandboxed subprocess and return output."),
        FunctionTool(make_confirmed_tool(make_api_call, "make_api_call"), description="Make an HTTP request to an external REST API."),
        FunctionTool(make_confirmed_tool(read_csv_file, "read_csv_file"), description="Read and display contents of a CSV file from the task workspace."),
        FunctionTool(make_confirmed_tool(analyze_csv_data, "analyze_csv_data"), description="Perform basic analysis on a CSV file."),
        # Browser automation tools (with confirmation)
        FunctionTool(make_confirmed_tool(browser_navigate, "browser_navigate"), description="Open a URL in a headless browser and return the page title."),
        FunctionTool(make_confirmed_tool(browser_fill_form, "browser_fill_form"), description="Fill a form field on the current browser page using CSS selector."),
        FunctionTool(make_confirmed_tool(browser_click, "browser_click"), description="Click an element on the browser page using CSS selector."),
        FunctionTool(make_confirmed_tool(browser_screenshot, "browser_screenshot"), description="Take a screenshot of the current browser page."),
        FunctionTool(make_confirmed_tool(browser_get_text, "browser_get_text"), description="Extract text content from an element on the browser page."),
        FunctionTool(make_confirmed_tool(browser_close, "browser_close"), description="Close the browser session."),
        # Desktop automation tools (with confirmation)
        FunctionTool(make_confirmed_tool(desktop_screenshot, "desktop_screenshot"), description="Take a screenshot of the entire desktop (auto-deletes after 5 min for privacy)."),
        FunctionTool(make_confirmed_tool(desktop_screenshot_region, "desktop_screenshot_region"), description="Take a screenshot of a specific screen region only. Safer than full desktop."),
        FunctionTool(make_confirmed_tool(desktop_find_on_screen, "desktop_find_on_screen"), description="Find an image/icon/button on screen and return its coordinates. More reliable than guessing."),
        FunctionTool(make_confirmed_tool(desktop_find_window, "desktop_find_window"), description="Find and activate a window by title (e.g., 'WhatsApp', 'Chrome'). Use before interacting with any app."),
        FunctionTool(make_confirmed_tool(desktop_click, "desktop_click"), description="Click at screen coordinates (x, y)."),
        FunctionTool(make_confirmed_tool(desktop_double_click, "desktop_double_click"), description="Double-click at screen coordinates."),
        FunctionTool(make_confirmed_tool(desktop_type_text, "desktop_type_text"), description="Type text using the keyboard."),
        FunctionTool(make_confirmed_tool(desktop_hotkey, "desktop_hotkey"), description="Press a keyboard shortcut (e.g., 'ctrl,c')."),
        FunctionTool(make_confirmed_tool(desktop_move_to, "desktop_move_to"), description="Move mouse cursor to screen coordinates."),
        # Excel/CSV editing tools
        FunctionTool(make_confirmed_tool(edit_excel_file, "edit_excel_file"), description="Edit specific cells in a local Excel file (.xlsx). No file records stored in DB."),
        FunctionTool(make_confirmed_tool(edit_csv_file, "edit_csv_file"), description="Edit specific cells in a local CSV file. No file records stored in DB."),
        # Social media tools
        FunctionTool(make_confirmed_tool(post_to_instagram, "post_to_instagram"), description="Post an image to Instagram via Meta Graph API."),
        FunctionTool(make_confirmed_tool(post_to_twitter, "post_to_twitter"), description="Post a tweet to Twitter/X via API v2."),
        FunctionTool(make_confirmed_tool(post_to_linkedin, "post_to_linkedin"), description="Post a text update to LinkedIn via UGC API."),
        FunctionTool(make_confirmed_tool(post_to_facebook, "post_to_facebook"), description="Post a message to a Facebook Page via Graph API."),
    ]
