"""
Jobs source: RemoteOK public API (replaces Upwork RSS which was discontinued).
Fetches AI/API/Python-tagged remote jobs and filters by relevance keywords.
"""
import re
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    requests = None

REMOTEOK_TAGS = ["ai", "api", "python", "automation"]
BUDGET_RE = re.compile(r"\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s*/\s*(?:hr|hour|month|year))?", re.IGNORECASE)

KEYWORDS = {
    "mcp": 10, "model context protocol": 10,
    "claude": 5,
    "ai agent": 3, "llm": 3, "langchain": 3,
    "automation": 2, "api integration": 2, "n8n": 2, "zapier": 2,
    "python": 1,
}


def score(text: str) -> int:
    low = text.lower()
    return sum(pts for kw, pts in KEYWORDS.items() if kw in low)


def extract_budget(text: str) -> str:
    m = BUDGET_RE.search(text)
    return m.group(0) if m else ""


def fetch() -> tuple[list[dict], str | None]:
    if requests is None:
        return [], "requests not installed — run: pip install requests"

    now = datetime.now(timezone.utc).isoformat()
    leads = []
    seen_ids = set()
    errors = []

    for tag in REMOTEOK_TAGS:
        url = f"https://remoteok.com/api?tag={tag}"
        try:
            resp = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": "mcp-lead-finder/1.0"},
            )
            resp.raise_for_status()
            jobs = [j for j in resp.json() if isinstance(j, dict) and j.get("position")]

            for job in jobs:
                job_id = str(job.get("id", ""))
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                title = job.get("position", "")
                company = job.get("company", "")
                desc = re.sub(r"<[^>]+>", " ", job.get("description", "")).strip()
                job_url = f"https://remoteok.com/remote-jobs/{job_id}" if job_id else ""
                salary = job.get("salary", "")
                tags_list = job.get("tags", [])

                combined = f"{title} {desc} {' '.join(tags_list)}"
                s = score(combined)

                budget = salary or extract_budget(desc)
                date_str = job.get("date", now)

                leads.append({
                    "source": "upwork",  # labelled 'upwork' to keep source label consistent for users
                    "title": f"{title} @ {company}" if company else title,
                    "description": desc[:2000],
                    "url": job_url,
                    "poster": company or "Remote Company",
                    "posted_at": date_str,
                    "budget": budget,
                    "relevance_score": s,
                    "fetched_at": now,
                })

        except Exception as e:
            errors.append(f"RemoteOK tag={tag}: {e}")
            print(f"[remoteok] error for tag={tag}: {e}", file=sys.stderr)

    error_msg = "; ".join(errors) if errors and not leads else None
    return leads, error_msg
