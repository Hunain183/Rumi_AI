"""
Web Tools — Search the internet and fetch web pages.

Uses DuckDuckGo for search (no API key needed) and
BeautifulSoup for extracting clean text from web pages.
"""

import requests
from bs4 import BeautifulSoup


DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the internet using DuckDuckGo. Returns top results "
                "with titles, URLs, and snippets. No API key needed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results (default: 5)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "Fetch a webpage and extract its main text content",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch",
                    }
                },
                "required": ["url"],
            },
        },
    },
]


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo (free, no API key)."""
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "No results found."

        output = []
        for i, r in enumerate(results, 1):
            output.append(
                f"{i}. **{r['title']}**\n   {r['href']}\n   {r['body']}"
            )
        return "\n\n".join(output)

    except ImportError:
        return "Install duckduckgo-search: pip install duckduckgo-search"
    except Exception as e:
        return f"Search failed: {e}"


def fetch_webpage(url: str) -> str:
    """Fetch a webpage and extract clean text (no scripts/styles)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (RUMI AI Assistant)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Strip out non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # Truncate very long pages
        if len(text) > 5000:
            text = text[:5000] + "\n\n[... content truncated ...]"

        return text

    except Exception as e:
        return f"Failed to fetch {url}: {e}"
