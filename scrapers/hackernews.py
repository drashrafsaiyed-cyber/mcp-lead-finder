"""
HackerNews scraper using the free Algolia HN Search API.
No API key needed. Filters out Show HN / Ask HN noise posts.
"""
import sys
import urllib.parse
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    requests = None

from scrapers.scoring import score_text

QUERIES = [
    "MCP developer hire freelance",
    "Model Context Protocol developer needed",
    "Claude API integration hire",
    "AI agent developer freelance budget",
]

# Title prefixes that are product launches or discussions — NOT job leads.
# NOTE: "who is hiring" is intentionally NOT here — those threads are leads.
NOISE_PREFIXES = (
    "show hn:",
    "show hn :",
    "tell hn:",
    "launch hn:",
    "poll:",
)


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
                s = score_text(combined)

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
