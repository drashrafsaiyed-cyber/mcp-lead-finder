# 🔍 MCP Lead Finder

> An MCP server that finds freelancing leads for MCP builders, Claude integrators, and AI automation developers — and sends Telegram alerts when high-value leads appear.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastMCP](https://img.shields.io/badge/FastMCP-3.x-green)

---

## What it does

- Scrapes **Reddit**, **RemoteOK**, and **HackerNews** for MCP/AI integration freelancing opportunities
- Scores every lead by keyword relevance (MCP, Claude, LLM, automation...)
- **Sends Telegram alerts** every 3 hours when high-score leads are found
- Exposes **8 MCP tools** so you can query leads conversationally inside Claude Desktop

**No API keys needed** — Reddit uses public JSON endpoints, HackerNews uses the free Algolia API, RemoteOK has a free public API.

---

## What it won't do

- Won't reply to leads for you — it finds and drafts, you send
- Won't run without your machine on — it's a local tool, not a hosted service
- Won't guarantee paid work — lead quality depends on what's posted that day
- Won't scrape LinkedIn — their ToS prohibits it and getting banned kills your profile

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

Telegram alert on your phone:
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
| **Reddit** | r/forhire, r/freelance_forhire, r/ClaudeAI, r/LocalLLaMA, r/LangChain, r/entrepreneur, r/SaaS, r/MachineLearning — no API key needed |
| **RemoteOK** | Remote jobs tagged: ai, api, python, automation — free public API |
| **HackerNews** | Hiring posts mentioning MCP / Claude / Model Context Protocol — via Algolia API |

---

## Relevance Scoring

| Keyword | Points |
|---------|--------|
| MCP / Model Context Protocol | +10 |
| Claude | +5 |
| AI agent / LLM | +3 |
| automation / API integration / n8n / zapier | +2 |
| python | +1 |

Leads scoring **5+** trigger Telegram alerts by default. Adjust `NOTIFY_MIN_SCORE` in `.env`.

---

## Requirements

- Python 3.10+
- A Telegram account (free) — for alerts
- Claude Desktop — to use the MCP tools conversationally
- Windows / macOS / Linux

---

## Setup (5 minutes)

### 1. Clone & install

```bash
git clone https://github.com/drashrafsaiyed-cyber/mcp-lead-finder.git
cd mcp-lead-finder
pip install -r requirements.txt
```

### 2. Set up Telegram bot (for alerts)

1. Open Telegram → search **@BotFather** → send `/newbot`
2. Follow the steps to create your bot and get your **token**
3. Run the setup helper — it creates `.env` automatically, fetches your Chat ID, and sends a test message:

```bash
python setup_telegram.py
```

Check your Telegram — a test message will arrive confirming it works.

> **Note:** `setup_telegram.py` creates `.env` from `.env.example` automatically if it doesn't exist yet. No manual `cp` needed.

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

### 5. Schedule auto-alerts

**Windows** — run once in Command Prompt:
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
| `search_leads(query, source, limit)` | Search stored leads by keyword — source: all/reddit/remoteok/hackernews |
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
│   ├── remoteok.py     # RemoteOK public API scraper
│   ├── scoring.py      # Shared keyword scoring (single source of truth)
│   └── hackernews.py   # HackerNews via Algolia API
├── .env.example        # Environment variable template
├── requirements.txt
└── leads.db            # Local SQLite database (gitignored)
```

---

## Contributing

Contributions welcome. Particularly useful additions:

- Additional job sources (Contra, Toptal RSS, HN monthly hiring threads)
- Better relevance scoring for non-English posts
- LinkedIn integration if/when their API opens up
- Web UI dashboard for leads (Flask/Streamlit)

Open an issue first for significant changes.

---

## Related

- [Model Context Protocol spec](https://modelcontextprotocol.io)
- [FastMCP Python SDK](https://github.com/jlowin/fastmcp)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Claude Desktop](https://claude.ai/download)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

Built by **Dr. Ashraf Saiyed** ([VR AI Automations](https://github.com/drashrafsaiyed-cyber)).
Not affiliated with or endorsed by Anthropic.
