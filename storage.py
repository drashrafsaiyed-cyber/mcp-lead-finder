import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "leads.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    title TEXT,
    description TEXT,
    url TEXT UNIQUE,
    poster TEXT,
    posted_at TEXT,
    budget TEXT,
    relevance_score INTEGER DEFAULT 0,
    saved INTEGER DEFAULT 0,
    notes TEXT DEFAULT '',
    fetched_at TEXT
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def upsert_lead(lead: dict) -> bool:
    """Insert lead, skip if URL already exists. Returns True if new."""
    sql = """
    INSERT OR IGNORE INTO leads
        (source, title, description, url, poster, posted_at, budget, relevance_score, fetched_at)
    VALUES
        (:source, :title, :description, :url, :poster, :posted_at, :budget, :relevance_score, :fetched_at)
    """
    with get_conn() as conn:
        cur = conn.execute(sql, lead)
        return cur.rowcount > 0


def get_fresh_leads(hours_back: int = 24) -> list[dict]:
    sql = """
    SELECT * FROM leads
    WHERE fetched_at >= datetime('now', ? || ' hours')
    ORDER BY relevance_score DESC, posted_at DESC
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (f"-{hours_back}",)).fetchall()
    return [dict(r) for r in rows]


def search_leads(query: str, source: str = "all", limit: int = 20) -> list[dict]:
    terms = [f"%{t}%" for t in query.split()]
    conditions = " OR ".join(
        ["(LOWER(title) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?))" for _ in terms]
    )
    params = [v for t in terms for v in (t, t)]

    if source != "all":
        conditions = f"({conditions}) AND source = ?"
        params.append(source)

    sql = f"SELECT * FROM leads WHERE {conditions} ORDER BY relevance_score DESC, posted_at DESC LIMIT ?"
    params.append(limit)

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def get_lead_by_id(lead_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    return dict(row) if row else None


def save_lead(lead_id: int, notes: str = "") -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE leads SET saved = 1, notes = ? WHERE id = ?", (notes, lead_id)
        )
        return cur.rowcount > 0


def unsave_lead(lead_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE leads SET saved = 0, notes = '' WHERE id = ?", (lead_id,)
        )
        return cur.rowcount > 0


def list_saved_leads() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM leads WHERE saved = 1 ORDER BY relevance_score DESC"
        ).fetchall()
    return [dict(r) for r in rows]
