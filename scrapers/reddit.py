"""
Reddit scraper using public JSON endpoints — no API key or registration needed.
Uses reddit.com/r/subreddit/new.json which is publicly accessible.
"""
import sys
import time
import requests
from datetime import datetime, timezone

from scrapers.scoring import score_text

SUBREDDITS = [
    "forhire",
    "freelance_forhire",
    "ClaudeAI",
    "LocalLLaMA",
    "LangChain",
    "entrepreneur",
    "SaaS",
    "MachineLearning",
]

HEADERS = {"User-Agent": "mcp-lead-finder/1.0 (personal use)"}


def fetch(limit_per_sub: int = 25) -> tuple[list[dict], str | None]:
    now = datetime.now(timezone.utc).isoformat()
    leads = []
    errors = []

    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit={limit_per_sub}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            posts = resp.json().get("data", {}).get("children", [])

            for item in posts:
                post = item.get("data", {})
                title = post.get("title", "")
                body = post.get("selftext", "")
                combined = f"{title} {body}"
                s = score_text(combined)

                posted_ts = post.get("created_utc", 0)
                posted = datetime.fromtimestamp(posted_ts, tz=timezone.utc).isoformat()

                leads.append({
                    "source": "reddit",
                    "title": title,
                    "description": body[:2000],
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "poster": post.get("author", "[deleted]"),
                    "posted_at": posted,
                    "budget": "",
                    "relevance_score": s,
                    "fetched_at": now,
                })

            time.sleep(1)  # be polite to Reddit servers

        except Exception as e:
            errors.append(f"r/{sub}: {e}")
            print(f"[reddit] error on r/{sub}: {e}", file=sys.stderr)

    error_msg = "; ".join(errors) if errors and not leads else None
    return leads, error_msg


def fetch_subreddit(subreddit: str, limit: int = 25, keyword: str = "") -> tuple[list[dict], str | None]:
    now = datetime.now(timezone.utc).isoformat()
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit * 2 if keyword else limit}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        posts = resp.json().get("data", {}).get("children", [])

        results = []
        for item in posts:
            post = item.get("data", {})
            title = post.get("title", "")
            body = post.get("selftext", "")
            combined = f"{title} {body}"

            if keyword and keyword.lower() not in combined.lower():
                continue

            posted_ts = post.get("created_utc", 0)
            posted = datetime.fromtimestamp(posted_ts, tz=timezone.utc).isoformat()

            results.append({
                "source": "reddit",
                "title": title,
                "description": body[:1000],
                "url": f"https://reddit.com{post.get('permalink', '')}",
                "poster": post.get("author", "[deleted]"),
                "posted_at": posted,
                "budget": "",
                "relevance_score": score(combined),
                "fetched_at": now,
            })

            if len(results) >= limit:
                break

        return results, None

    except Exception as e:
        return [], f"Reddit error: {e}"
