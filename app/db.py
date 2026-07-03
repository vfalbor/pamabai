"""SQLite layer: schema, connection helper, FTS5 sync.

One writer (single uvicorn worker) + WAL keeps this safe without a pool.
"""
import os

import aiosqlite

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS papers (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    authors     TEXT NOT NULL,
    abstract    TEXT NOT NULL DEFAULT '',
    keywords    TEXT NOT NULL DEFAULT '',
    ai_models   TEXT NOT NULL,
    human_role  TEXT NOT NULL DEFAULT '',
    artifact_url TEXT NOT NULL DEFAULT '',
    license     TEXT NOT NULL DEFAULT 'CC BY 4.0',
    kind        TEXT NOT NULL CHECK(kind IN ('pdf','latex')),
    filename    TEXT NOT NULL,
    size_bytes  INTEGER NOT NULL,
    status      TEXT NOT NULL DEFAULT 'preprint'
                CHECK(status IN ('preprint','published','hidden')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts USING fts5(
    id UNINDEXED, title, authors, abstract, keywords
);
CREATE TABLE IF NOT EXISTS issues (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    volume      INTEGER NOT NULL,
    number      INTEGER NOT NULL,
    title       TEXT NOT NULL,
    editorial   TEXT NOT NULL DEFAULT '',
    published_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(volume, number)
);
CREATE TABLE IF NOT EXISTS articles (
    issue_id    INTEGER NOT NULL REFERENCES issues(id),
    paper_id    TEXT NOT NULL REFERENCES papers(id),
    position    INTEGER NOT NULL,
    pages       TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (issue_id, paper_id)
);
CREATE INDEX IF NOT EXISTS idx_papers_status_created
    ON papers(status, created_at DESC);
"""


def data_dir() -> str:
    d = os.environ.get("PAMABAI_DATA", os.path.join(os.getcwd(), "data"))
    os.makedirs(os.path.join(d, "uploads"), exist_ok=True)
    return d


def db_path() -> str:
    return os.path.join(data_dir(), "pamabai.db")


async def connect() -> aiosqlite.Connection:
    conn = await aiosqlite.connect(db_path())
    conn.row_factory = aiosqlite.Row
    await conn.executescript(SCHEMA)
    await conn.commit()
    return conn


async def fts_index(conn: aiosqlite.Connection, paper: dict) -> None:
    await conn.execute("DELETE FROM papers_fts WHERE id = ?", (paper["id"],))
    await conn.execute(
        "INSERT INTO papers_fts (id, title, authors, abstract, keywords) "
        "VALUES (?,?,?,?,?)",
        (paper["id"], paper["title"], paper["authors"],
         paper["abstract"], paper["keywords"]),
    )


def fts_query(q: str) -> str:
    """User text -> safe FTS5 query: quoted terms ANDed together."""
    terms = [t.replace('"', "") for t in q.split() if t.replace('"', "")]
    return " ".join(f'"{t}"' for t in terms) or '""'
