import httpx
from bs4 import BeautifulSoup


async def read_webpage(url: str, max_length: int = 5000) -> str:
    """Fetch a webpage and extract its main text content.

    Args:
        url: The full URL to fetch (must start with http:// or https://).
        max_length: Maximum characters of content to return (default 5000).
    """
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; TaskAgent/1.0)"
            })
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        if len(text) > max_length:
            text = text[:max_length] + "\n\n[Content truncated...]"

        return f"Content from {url}:\n\n{text}"
    except Exception as e:
        return f"Failed to read webpage: {str(e)}"
