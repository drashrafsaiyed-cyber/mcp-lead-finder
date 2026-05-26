# Changelog

All notable changes to MCP Lead Finder will be documented here.

---

## [0.1.0] - 2026-05-27

### Added
- Reddit scraper using public JSON endpoints (no API key required)
- RemoteOK scraper via public API (ai, api, python, automation tags)
- HackerNews scraper via Algolia API — filters out Show HN / Ask HN noise
- Relevance scoring system (MCP=10, Claude=5, LLM=3, automation=2, python=1)
- SQLite local storage with URL-based deduplication
- 8 MCP tools: `refresh_leads`, `get_fresh_leads`, `search_leads`, `get_lead_details`, `save_lead`, `unsave_lead`, `list_saved_leads`, `get_subreddit_posts`
- Telegram alert notifier with configurable score threshold
- `setup_telegram.py` — one-command bot setup with auto Chat ID detection
- Windows Task Scheduler support (every 3 hours)
- macOS/Linux crontab support
