"""
Memory — RUMI's persistent storage.

Stores conversations and key facts in a SQLite database so RUMI
remembers things across sessions. Like a personal diary that
never forgets.

Two tables:
  • conversations — every message ever exchanged
  • facts — key-value pairs (user name, preferences, etc.)
"""

import sqlite3
from datetime import datetime
from pathlib import Path


class Memory:
    """Persistent memory backed by SQLite — survives restarts."""

    def __init__(self, db_path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(db_path))
        self._setup()

    def _setup(self):
        """Create tables on first run (safe to call repeatedly)."""
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                role      TEXT NOT NULL,
                content   TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS facts (
                key        TEXT PRIMARY KEY,
                value      TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_conv_time
                ON conversations(timestamp);
        """)
        self.db.commit()

    # ─── Conversations ───────────────────────────────────────

    def save(self, role: str, content: str):
        """Store a message (role = 'user' or 'assistant')."""
        self.db.execute(
            "INSERT INTO conversations (role, content) VALUES (?, ?)",
            (role, content),
        )
        self.db.commit()

    def get_recent(self, limit=20) -> list:
        """Get the most recent messages."""
        rows = self.db.execute(
            "SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def search(self, query: str, limit=10) -> list:
        """Search past conversations by keyword."""
        rows = self.db.execute(
            "SELECT role, content, timestamp FROM conversations "
            "WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        return [{"role": r[0], "content": r[1], "time": r[2]} for r in rows]

    # ─── Facts (key-value memory) ────────────────────────────

    def save_fact(self, key: str, value: str):
        """Store a persistent fact (preference, name, etc.)."""
        self.db.execute(
            "INSERT OR REPLACE INTO facts (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, datetime.now().isoformat()),
        )
        self.db.commit()

    def get_fact(self, key: str) -> str | None:
        """Retrieve a stored fact by key."""
        row = self.db.execute(
            "SELECT value FROM facts WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def get_facts(self) -> dict:
        """Get all stored facts as a dictionary."""
        rows = self.db.execute("SELECT key, value FROM facts").fetchall()
        return dict(rows)

    # ─── Cleanup ─────────────────────────────────────────────

    def close(self):
        """Close the database connection."""
        self.db.close()
