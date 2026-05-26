"""
RemoteOK public API scraper.
Fetches AI/API/Python-tagged remote jobs and scores by relevance keywords.
Source: https://remoteok.com/api
"""
import re
import sys
import requests
from datetime import datetime, timezone

from scrapers.scoring import score_text

REMOTEOK_TAGS = ["ai", "api", "python", "automation"]
BUDGET_RE = re.compile(
    r"\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s*/\s*(?:hr|hour|month|year))?",
    re.IGNORECASE,
)


def extract_budget(text: str) -> str:
    m = BUDGET_RE.search(text)
    return m.group(0) if m else ""


def fetch() -> tuple[list[dict], str | None]:
    now = datetime.now(timezone.utc).isoformat()
    leads = []
    seen_ids: set[str] = set()
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
                budget = salary or extract_budget(desc)

                leads.append({
                    "source": "remoteok",
                    "title": f"{title} @ {company}" if company else title,
                    "description": desc[:2000],
                    "url": job_url,
                    "poster": company or "Remote Company",
                    "posted_at": job.get("date", now),
                    "budget": budget,
                    "relevance_score": score_text(combined),
                    "fetched_at": now,
                })

        except Exception as e:
            errors.append(f"RemoteOK tag={tag}: {e}")
            print(f"[remoteok] error for tag={tag}: {e}", file=sys.stderr)

    error_msg = "; ".join(errors) if errors and not leads else None
    return leads, error_msg
