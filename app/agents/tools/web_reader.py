import httpx
from bs4 import BeautifulSoup


async def read_webpage(url: str, max_length: int = 8000) -> str:
    """Fetch a webpage and extract its main text content cleanly.

    Args:
        url: The full URL to fetch (must start with http:// or https://).
        max_length: Maximum characters of content to return (default 8000).
    """
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                         "form", "iframe", "noscript", "svg", "img", "button"]):
            tag.decompose()

        # Try to find the main content area first
        main_content = None
        for selector in ["article", "main", "[role='main']", ".article-body",
                         ".post-content", ".entry-content", "#content", ".content"]:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        # Clean up: remove excessive blank lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        text = "\n".join(lines)

        if len(text) > max_length:
            text = text[:max_length] + "\n\n[Content truncated...]"

        if len(text) < 50:
            return f"Could not extract meaningful content from {url}. The page may require JavaScript."

        return f"Content from {url}:\n\n{text}"
    except httpx.HTTPStatusError as e:
        return f"HTTP error fetching {url}: {e.response.status_code}"
    except Exception as e:
        return f"Failed to read webpage: {str(e)}"
