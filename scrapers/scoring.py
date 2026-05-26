"""
Shared relevance scoring for all scrapers.
Single source of truth — do not duplicate in individual scrapers.

Score design:
  - JOB_SIGNALS:    someone is actually hiring/looking (+points)
  - TECH_KEYWORDS:  technology relevance (+points)
  - NOISE_KEYWORDS: news, tutorials, announcements (-points)

A genuine lead needs job signals + tech keywords.
A blog post has tech keywords but noise keywords cancel them out.
Score is floored at 0 (never goes negative).
"""

# Someone is actively hiring or looking for a developer
JOB_SIGNALS: dict[str, int] = {
    "for hire":           8,
    "[for hire]":         8,
    "hiring":             7,
    "looking for":        6,
    "need developer":     7,
    "need someone":       6,
    "developer needed":   7,
    "developer wanted":   7,
    "seeking developer":  7,
    "freelance":          6,
    "freelancer":         6,
    "contract work":      6,
    "contract role":      6,
    "paid project":       6,
    "paid work":          6,
    "budget":             5,
    "hourly rate":        5,
    "fixed price":        4,
    "upwork":             4,
    "fiverr":             4,
    "project":            2,
    "opportunity":        2,
    "commission":         4,
    "rate negotiable":    5,
}

# Technology relevance — what we actually build
TECH_KEYWORDS: dict[str, int] = {
    "mcp":                    10,
    "model context protocol": 10,
    "claude":                  5,
    "ai agent":                3,
    "llm":                     3,
    "langchain":               3,
    "automation":              2,
    "api integration":         2,
    "n8n":                     2,
    "zapier":                  2,
    "python":                  1,
}

# Noise — articles, tutorials, news, product launches
NOISE_KEYWORDS: dict[str, int] = {
    "tutorial":           -5,
    "how to":             -3,
    "getting started":    -4,
    "step by step":       -4,
    "beginners guide":    -5,
    "guide":              -3,
    "released":           -4,
    "release notes":      -5,
    "announcing":         -5,
    "announcement":       -5,
    "we built":           -4,
    "i built":            -4,
    "blog post":          -4,
    "research paper":     -5,
    "benchmark":          -4,
    "deep dive":          -3,
    "comparison":         -3,
    "launched":           -4,
    "new feature":        -3,
    "documentation":      -4,
    "open sourced":       -4,
    "just released":      -5,
    "introducing":        -4,
}


def score_text(text: str) -> int:
    """
    Return relevance score for a lead.
    Combines job signals, tech keywords, and noise penalties.
    Floored at 0 — never returns negative.
    """
    low = text.lower()
    pts = 0
    pts += sum(v for kw, v in JOB_SIGNALS.items() if kw in low)
    pts += sum(v for kw, v in TECH_KEYWORDS.items() if kw in low)
    pts += sum(v for kw, v in NOISE_KEYWORDS.items() if kw in low)
    return max(0, pts)
