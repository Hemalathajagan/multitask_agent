import httpx
import json


async def make_api_call(
    url: str,
    method: str = "GET",
    headers_json: str = "{}",
    body_json: str = ""
) -> str:
    """Make an HTTP API call to an external REST endpoint.

    Args:
        url: The full API endpoint URL.
        method: HTTP method - GET, POST, PUT, PATCH, or DELETE.
        headers_json: JSON string of request headers (e.g., '{"Authorization": "Bearer xxx"}').
        body_json: JSON string of request body (for POST/PUT/PATCH). Empty string for no body.
    """
    method = method.upper()
    if method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
        return f"Error: Invalid method '{method}'. Use GET, POST, PUT, PATCH, or DELETE."

    try:
        headers = json.loads(headers_json) if headers_json else {}
        body = json.loads(body_json) if body_json else None
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in headers or body: {str(e)}"

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.request(
                method, url, headers=headers, json=body
            )

        content = response.text[:5000]
        if len(response.text) > 5000:
            content += "\n\n[Response truncated...]"

        return (
            f"Status: {response.status_code}\n\n"
            f"Body:\n{content}"
        )
    except Exception as e:
        return f"API call failed: {str(e)}"
