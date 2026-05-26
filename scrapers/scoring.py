"""
Shared relevance scoring for all scrapers.
Single source of truth — do not duplicate KEYWORDS in individual scrapers.
"""

KEYWORDS: dict[str, int] = {
    "mcp": 10,
    "model context protocol": 10,
    "claude": 5,
    "ai agent": 3,
    "llm": 3,
    "langchain": 3,
    "automation": 2,
    "api integration": 2,
    "n8n": 2,
    "zapier": 2,
    "python": 1,
}


def score_text(text: str) -> int:
    """Return relevance score by summing points for each matched keyword."""
    low = text.lower()
    return sum(pts for kw, pts in KEYWORDS.items() if kw in low)
