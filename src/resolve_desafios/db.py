import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple

from .config import get_settings


def _dict_factory(cursor: sqlite3.Cursor, row: Tuple[Any, ...]) -> Dict[str, Any]:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@contextmanager
def connect() -> Generator[sqlite3.Connection, None, None]:
    settings = get_settings()
    conn = sqlite3.connect(str(settings.db_path))
    conn.row_factory = _dict_factory
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS challenges (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              description TEXT NOT NULL,
              objectives TEXT,
              constraints TEXT,
              language TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              challenge_id INTEGER NOT NULL,
              difficulty TEXT NOT NULL,
              categories TEXT NOT NULL,
              summary TEXT NOT NULL,
              recommended_approach TEXT NOT NULL,
              approaches TEXT NOT NULL,
              complexity_time TEXT NOT NULL,
              complexity_space TEXT NOT NULL,
              assumptions TEXT,
              references TEXT,
              model TEXT NOT NULL,
              raw JSON,
              created_at TEXT NOT NULL,
              FOREIGN KEY(challenge_id) REFERENCES challenges(id)
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            """
        )
        conn.commit()


def insert_challenge(
    *, title: str, description: str, objectives: Optional[str], constraints: Optional[str], language: str
) -> int:
    now = datetime.utcnow().isoformat()
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO challenges (title, description, objectives, constraints, language, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, description, objectives, constraints, language, now),
        )
        conn.commit()
        return int(cur.lastrowid)


def insert_analysis(
    *,
    challenge_id: int,
    difficulty: str,
    categories: List[str],
    summary: str,
    recommended_approach: str,
    approaches: List[Dict[str, Any]],
    complexity_time: str,
    complexity_space: str,
    assumptions: Optional[str],
    references: Optional[str],
    model: str,
    raw: Dict[str, Any],
) -> int:
    now = datetime.utcnow().isoformat()
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO analyses (
              challenge_id, difficulty, categories, summary, recommended_approach, approaches,
              complexity_time, complexity_space, assumptions, references, model, raw, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                challenge_id,
                difficulty,
                json.dumps(categories, ensure_ascii=False),
                summary,
                recommended_approach,
                json.dumps(approaches, ensure_ascii=False),
                complexity_time,
                complexity_space,
                assumptions,
                references,
                model,
                json.dumps(raw, ensure_ascii=False),
                now,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_analyses(limit: int = 20) -> List[Dict[str, Any]]:
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.id as analysis_id, c.id as challenge_id, c.title, a.difficulty, a.categories, a.created_at
            FROM analyses a
            JOIN challenges c ON c.id = a.challenge_id
            ORDER BY a.id DESC
            LIMIT ?
            """,
            (int(limit),),
        )
        rows = cur.fetchall()
        for r in rows:
            try:
                r["categories"] = json.loads(r["categories"]) if r.get("categories") else []
            except Exception:
                pass
        return rows


def get_analysis(analysis_id: int) -> Optional[Dict[str, Any]]:
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.*, c.title, c.description, c.objectives, c.constraints, c.language
            FROM analyses a
            JOIN challenges c ON c.id = a.challenge_id
            WHERE a.id = ?
            """,
            (int(analysis_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        try:
            row["categories"] = json.loads(row["categories"]) if row.get("categories") else []
        except Exception:
            pass
        try:
            row["approaches"] = json.loads(row["approaches"]) if row.get("approaches") else []
        except Exception:
            pass
        try:
            row["raw"] = json.loads(row["raw"]) if row.get("raw") else {}
        except Exception:
            pass
        return row


def upsert_metadata(key: str, value: Dict[str, Any]) -> None:
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT key FROM metadata WHERE key = ?", (key,))
        exists = cur.fetchone() is not None
        if exists:
            cur.execute("UPDATE metadata SET value = ? WHERE key = ?", (json.dumps(value, ensure_ascii=False), key))
        else:
            cur.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", (key, json.dumps(value, ensure_ascii=False)))
        conn.commit()


def get_metadata(key: str) -> Optional[Dict[str, Any]]:
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        row = cur.fetchone()
        if not row:
            return None
        try:
            return json.loads(row["value"]) if row.get("value") else None
        except Exception:
            return None


