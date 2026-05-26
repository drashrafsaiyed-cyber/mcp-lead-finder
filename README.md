# 🔍 MCP Lead Finder

> An MCP server that finds freelancing leads for MCP builders, Claude integrators, and AI automation developers — and sends Telegram alerts when high-value leads appear.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastMCP](https://img.shields.io/badge/FastMCP-3.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What it does

- Scrapes **Reddit**, **RemoteOK**, and **HackerNews** for MCP/AI integration freelancing opportunities
- Scores every lead by keyword relevance (MCP, Claude, LLM, automation...)
- **Sends Telegram alerts** every 3 hours when high-score leads are found
- Exposes **MCP tools** so you can query leads conversationally inside Claude Desktop

**No API keys needed** — Reddit uses public JSON endpoints, HackerNews uses the free Algolia API, RemoteOK has a free public API.

---

## Demo

Ask Claude naturally:
```
"Show me fresh MCP leads from the last 24 hours"
"Search for Claude integration jobs on Reddit"
"Get full details for lead #12"
"Save lead #7 with note: replied via DM"
"Draft a reply for lead #5 — I build FastMCP servers in Python"
```

Telegram alert example:
```
🔥 New MCP Lead [Score: 15]
📌 Source: REDDIT
📝 Need MCP server built for Slack + Notion integration
👤 By: u/startup_founder | 2 hrs ago
💰 Budget: $500-1000
🔗 https://reddit.com/r/forhire/...
```

---

## Sources

| Source | What it finds |
|--------|--------------|
| **Reddit** | r/forhire, r/freelance_forhire, r/ClaudeAI, r/LocalLLaMA, r/LangChain, r/entrepreneur, r/SaaS, r/MachineLearning |
| **RemoteOK** | Remote jobs tagged: ai, api, python, automation |
| **HackerNews** | Hiring posts mentioning MCP / Claude / Model Context Protocol |

---

## Relevance Scoring

| Keyword | Points |
|---------|--------|
| MCP / Model Context Protocol | +10 |
| Claude | +5 |
| AI agent / LLM | +3 |
| automation / API integration / n8n / zapier | +2 |
| python | +1 |

Leads scoring **10+** trigger Telegram alerts. Adjust `NOTIFY_MIN_SCORE` in `.env`.

---

## Setup (5 minutes)

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/mcp-lead-finder.git
cd mcp-lead-finder
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

### 3. Set up Telegram bot (for alerts)

1. Open Telegram → search **@BotFather** → send `/newbot`
2. Follow the steps to create your bot and get your **token**
3. Run the setup helper — it fetches your Chat ID and saves everything automatically:

```bash
python setup_telegram.py
```

Check your Telegram — a test message will arrive confirming it works.

### 4. Connect to Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "lead-finder": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-lead-finder/server.py"]
    }
  }
}
```

Fully quit Claude Desktop and reopen it.

### 5. Schedule auto-alerts (Windows)

Run once in Command Prompt — scrapes + notifies every 3 hours:

```
schtasks /create /tn "MCP Lead Finder" /tr "python C:\path\to\mcp-lead-finder\notifier.py" /sc hourly /mo 3 /st 08:00 /f
```

**macOS/Linux** — add to crontab:
```bash
crontab -e
# Add this line:
0 */3 * * * python /path/to/mcp-lead-finder/notifier.py
```

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `refresh_leads()` | Scrape all sources now, save new leads to DB |
| `get_fresh_leads(hours_back=24)` | Show leads from last N hours, sorted by score |
| `search_leads(query, source, limit)` | Search stored leads by keyword |
| `get_lead_details(lead_id)` | Full details + description for a specific lead |
| `save_lead(lead_id, notes)` | Bookmark a lead with optional notes |
| `list_saved_leads()` | View all bookmarked leads |
| `unsave_lead(lead_id)` | Remove bookmark |
| `get_subreddit_posts(subreddit, limit, keyword)` | Browse any subreddit directly |

---

## Project Structure

```
mcp-lead-finder/
├── server.py           # FastMCP server — all MCP tools
├── notifier.py         # Telegram alert script (run on schedule)
├── setup_telegram.py   # One-time Telegram setup helper
├── storage.py          # SQLite operations
├── scrapers/
│   ├── reddit.py       # Reddit public JSON scraper (no auth needed)
│   ├── upwork.py       # RemoteOK API scraper
│   └── hackernews.py   # HackerNews via Algolia API
├── .env.example        # Environment variable template
├── requirements.txt
└── leads.db            # Local SQLite database (gitignored)
```

---

## License

MIT — free to use, modify, and distribute.

---

Built with [FastMCP](https://github.com/jlowin/fastmcp) • Inspired by the need to find real MCP freelancing work 🚀
