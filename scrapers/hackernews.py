import sys
import urllib.parse
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    requests = None

QUERIES = [
    "MCP freelance hire build",
    "Model Context Protocol developer hire",
    "Claude API integration developer",
]

# These title prefixes are product launches / news — NOT job leads
NOISE_PREFIXES = (
    "show hn:", "ask hn:", "tell hn:", "launch hn:",
    "show hn :", "poll:", "who is hiring",
)


def score(text: str) -> int:
    low = text.lower()
    pts = 0
    if "mcp" in low or "model context protocol" in low:
        pts += 10
    if "claude" in low:
        pts += 5
    if "ai agent" in low or "llm" in low:
        pts += 3
    if "automation" in low or "api integration" in low:
        pts += 2
    return pts


def fetch() -> tuple[list[dict], str | None]:
    if requests is None:
        return [], "requests not installed — run: pip install requests"

    now = datetime.now(timezone.utc).isoformat()
    leads = []
    seen_urls = set()

    for query in QUERIES:
        encoded = urllib.parse.quote(query)
        url = f"https://hn.algolia.com/api/v1/search?query={encoded}&tags=story&hitsPerPage=30"
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            data = resp.json()

            for hit in data.get("hits", []):
                title = hit.get("title") or hit.get("comment_text", "")[:100] or ""
                desc = hit.get("story_text") or hit.get("comment_text") or ""
                hn_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"

                if hn_url in seen_urls:
                    continue

                # skip product launches and non-job posts
                if title.lower().startswith(NOISE_PREFIXES):
                    continue

                seen_urls.add(hn_url)

                poster = hit.get("author", "unknown")
                ts = hit.get("created_at", now)
                combined = f"{title} {desc}"
                s = score(combined)

                leads.append({
                    "source": "hackernews",
                    "title": title[:300],
                    "description": desc[:2000],
                    "url": hn_url,
                    "poster": poster,
                    "posted_at": ts,
                    "budget": "",
                    "relevance_score": s,
                    "fetched_at": now,
                })

        except Exception as e:
            print(f"[hackernews] error for query '{query}': {e}", file=sys.stderr)

    return leads, None
