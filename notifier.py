"""
Telegram Lead Notifier
Run this on a schedule (every 3 hours via Windows Task Scheduler).
Sends Telegram alerts for high-relevance leads not yet notified.
"""
import html
import os
import sys
import sqlite3
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

# fix Windows console Unicode issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# ensure project root on path
sys.path.insert(0, str(Path(__file__).parent))
import storage
from scrapers import reddit, hackernews
import scrapers.remoteok as remoteok

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MIN_SCORE = int(os.getenv("NOTIFY_MIN_SCORE", "5"))


def ensure_notified_column():
    """Add notified column if it doesn't exist yet."""
    with storage.get_conn() as conn:
        try:
            conn.execute("ALTER TABLE leads ADD COLUMN notified INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # column already exists


def get_unnotified_leads(min_score: int) -> list[dict]:
    with storage.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM leads
               WHERE notified = 0 AND relevance_score >= ?
               ORDER BY relevance_score DESC, posted_at DESC""",
            (min_score,)
        ).fetchall()
    return [dict(r) for r in rows]


def mark_notified(lead_id: int):
    with storage.get_conn() as conn:
        conn.execute("UPDATE leads SET notified = 1 WHERE id = ?", (lead_id,))


def send_telegram(message: str) -> bool:
    if not BOT_TOKEN or not CHAT_ID:
        print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env", file=sys.stderr)
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"Telegram send error: {e}", file=sys.stderr)
        return False


def format_message(lead: dict) -> str:
    score = lead.get("relevance_score", 0)
    emoji = "🔥" if score >= 10 else "⭐"
    source = lead.get("source", "").upper()
    # HTML-escape all user-generated fields — Reddit titles can contain <, >, &
    title = html.escape(lead.get("title", "")[:100])
    poster = html.escape(lead.get("poster", ""))
    posted = lead.get("posted_at", "")[:16]
    budget = html.escape(lead.get("budget", "") or "not listed")
    url = lead.get("url", "")
    desc = html.escape(lead.get("description", "").strip()[:200])

    msg = (
        f"{emoji} <b>New MCP Lead</b> [Score: {score}]\n"
        f"📌 Source: {source}\n"
        f"📝 <b>{title}</b>\n"
        f"👤 By: {poster} | {posted}\n"
        f"💰 Budget: {budget}\n"
    )
    if desc:
        msg += f"📄 {desc}...\n"
    msg += f"\n🔗 <a href='{url}'>Open Lead</a>"
    return msg


def run():
    storage.init_db()
    ensure_notified_column()

    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Telegram not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
        sys.exit(1)

    print(f"[{datetime.now().strftime('%H:%M')}] Scraping all sources...")

    # scrape fresh data
    total_new = 0
    for scraper, name in [(reddit, "Reddit"), (remoteok, "RemoteOK"), (hackernews, "HackerNews")]:
        leads, err = scraper.fetch()
        if err and not leads:
            print(f"  ⚠ {name}: {err}")
            continue
        new = sum(storage.upsert_lead(l) for l in leads)
        total_new += new
        print(f"  ✅ {name}: {new} new leads")

    print(f"  Total new: {total_new}")

    # get unnotified high-score leads
    leads_to_notify = get_unnotified_leads(MIN_SCORE)
    print(f"  Found {len(leads_to_notify)} leads to notify (score >= {MIN_SCORE})")

    if not leads_to_notify:
        print("  No new leads to notify.")
        return

    sent = 0
    failed = 0
    for lead in leads_to_notify:
        msg = format_message(lead)
        if send_telegram(msg):
            mark_notified(lead["id"])
            sent += 1
            print(f"  📤 Sent: {lead['title'][:60]}")
            time.sleep(0.05)  # stay under Telegram's 30 msg/sec limit
        else:
            failed += 1
            # log and continue — lead stays unnotified and retries next run
            print(f"  ⚠ Failed (will retry next run): {lead['title'][:60]}")

    print(f"\n✅ Done. {sent} sent, {failed} failed (will retry).")


if __name__ == "__main__":
    run()
