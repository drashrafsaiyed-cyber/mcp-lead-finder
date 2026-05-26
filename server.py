import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv(Path(__file__).parent / ".env")

import storage
import scrapers.reddit as reddit_scraper
import scrapers.upwork as upwork_scraper
import scrapers.hackernews as hn_scraper

storage.init_db()

mcp = FastMCP("lead-finder")


def _fmt_lead(lead: dict) -> str:
    lines = [
        f"[ID: {lead['id']}] [{lead['source'].upper()}] {lead['title']}",
        f"  Score: {lead['relevance_score']} | Posted: {lead['posted_at'][:10]} | By: {lead['poster']}",
    ]
    if lead.get("budget"):
        lines.append(f"  Budget: {lead['budget']}")
    if lead.get("notes"):
        lines.append(f"  Notes: {lead['notes']}")
    lines.append(f"  URL: {lead['url']}")
    return "\n".join(lines)


@mcp.tool()
def get_fresh_leads(hours_back: int = 24) -> str:
    """
    Return leads fetched in the last N hours, sorted by relevance score.
    Triggers a fresh scrape first, then shows results.
    Use this for your daily morning check.
    """
    _do_scrape()
    leads = storage.get_fresh_leads(hours_back)
    if not leads:
        return f"No leads found in the last {hours_back} hours. Try increasing hours_back or run refresh_leads()."
    lines = [f"Found {len(leads)} leads from last {hours_back} hours:\n"]
    lines += [_fmt_lead(l) for l in leads]
    return "\n\n".join(lines)


@mcp.tool()
def search_leads(query: str, source: str = "all", limit: int = 20) -> str:
    """
    Search stored leads by keyword in title or description.
    source can be: 'all', 'reddit', 'upwork', 'hackernews'
    Example: search_leads('MCP python') or search_leads('Claude', source='upwork')
    """
    leads = storage.search_leads(query, source, limit)
    if not leads:
        return f"No leads found matching '{query}' in source '{source}'."
    lines = [f"Found {len(leads)} leads matching '{query}':\n"]
    lines += [_fmt_lead(l) for l in leads]
    return "\n\n".join(lines)


@mcp.tool()
def get_lead_details(lead_id: int) -> str:
    """
    Get full details of a specific lead including the complete description text.
    Use the ID shown in square brackets from search or fresh leads results.
    """
    lead = storage.get_lead_by_id(lead_id)
    if not lead:
        return f"No lead found with ID {lead_id}."

    lines = [
        f"=== Lead #{lead['id']} ===",
        f"Source:  {lead['source'].upper()}",
        f"Title:   {lead['title']}",
        f"Poster:  {lead['poster']}",
        f"Posted:  {lead['posted_at']}",
        f"Score:   {lead['relevance_score']}",
        f"Budget:  {lead['budget'] or 'Not mentioned'}",
        f"Saved:   {'Yes' if lead['saved'] else 'No'}",
        f"Notes:   {lead['notes'] or 'None'}",
        f"URL:     {lead['url']}",
        "",
        "--- Description ---",
        lead["description"] or "(no description)",
    ]
    return "\n".join(lines)


@mcp.tool()
def save_lead(lead_id: int, notes: str = "") -> str:
    """
    Bookmark a lead so you can track it. Add optional notes like 'replied', 'high budget', etc.
    Example: save_lead(42, notes='Strong match, replied via DM')
    """
    ok = storage.save_lead(lead_id, notes)
    if not ok:
        return f"Lead ID {lead_id} not found."
    return f"Lead #{lead_id} saved. Notes: '{notes}'" if notes else f"Lead #{lead_id} saved."


@mcp.tool()
def unsave_lead(lead_id: int) -> str:
    """Remove bookmark from a saved lead."""
    ok = storage.unsave_lead(lead_id)
    return f"Lead #{lead_id} unsaved." if ok else f"Lead ID {lead_id} not found."


@mcp.tool()
def list_saved_leads() -> str:
    """Show all your bookmarked leads with notes. Use this to track your pipeline."""
    leads = storage.list_saved_leads()
    if not leads:
        return "No saved leads yet. Use save_lead(id) to bookmark promising ones."
    lines = [f"=== Your Saved Leads ({len(leads)}) ===\n"]
    lines += [_fmt_lead(l) for l in leads]
    return "\n\n".join(lines)


@mcp.tool()
def get_subreddit_posts(subreddit: str, limit: int = 25, keyword: str = "") -> str:
    """
    Browse new posts from any subreddit, with optional keyword filter.
    Example: get_subreddit_posts('forhire', keyword='automation')
    Does NOT save to DB — use refresh_leads() to save.
    """
    posts, err = reddit_scraper.fetch_subreddit(subreddit, limit, keyword)
    if err:
        return f"Error: {err}"
    if not posts:
        kw_msg = f" matching '{keyword}'" if keyword else ""
        return f"No posts found in r/{subreddit}{kw_msg}."

    lines = [f"Latest {len(posts)} posts from r/{subreddit}:\n"]
    for p in posts:
        lines.append(
            f"• {p['title']}\n"
            f"  By: {p['poster']} | {p['posted_at'][:10]} | Score: {p['relevance_score']}\n"
            f"  {p['url']}"
        )
    return "\n\n".join(lines)


@mcp.tool()
def refresh_leads() -> str:
    """
    Scrape all sources right now (Reddit + Upwork + HackerNews) and save new leads to DB.
    Returns count of new leads found. Run this to get the freshest data.
    """
    count, notes = _do_scrape()
    msg = f"Refresh complete. {count} new leads added to database."
    if notes:
        msg += "\n\nNotes:\n" + "\n".join(f"  - {n}" for n in notes)
    return msg


def _do_scrape() -> tuple[int, list[str]]:
    notes = []
    total_new = 0

    reddit_leads, reddit_err = reddit_scraper.fetch()
    if reddit_err:
        notes.append(f"Reddit: {reddit_err}")
    for lead in reddit_leads:
        if storage.upsert_lead(lead):
            total_new += 1

    upwork_leads, upwork_err = upwork_scraper.fetch()
    if upwork_err:
        notes.append(f"Upwork: {upwork_err}")
    for lead in upwork_leads:
        if storage.upsert_lead(lead):
            total_new += 1

    hn_leads, hn_err = hn_scraper.fetch()
    if hn_err:
        notes.append(f"HackerNews: {hn_err}")
    for lead in hn_leads:
        if storage.upsert_lead(lead):
            total_new += 1

    return total_new, notes


if __name__ == "__main__":
    mcp.run()
