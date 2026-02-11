from duckduckgo_search import DDGS


async def web_search(query: str, max_results: int = 5) -> str:
    """Search the internet using DuckDuckGo and return results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5, max 10).
    """
    try:
        max_results = min(max_results, 10)
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "No results found for the query."

        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"{i}. **{r['title']}**\n"
                f"   URL: {r['href']}\n"
                f"   {r['body']}"
            )
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Search failed: {str(e)}"
