from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Optional

from src.config import settings
from src.exceptions import AliasConflictException, URLNotFoundException


class SQLiteRepository:
    def __init__(self, db_path: str = "urls.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=20.0, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS urls (
                    short_code TEXT PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    clicks INTEGER DEFAULT 0
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT
                )
                """
            )
            conn.commit()

    def check_health(self) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            return cursor.fetchone() is not None

    def get_next_sequence_id(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sequence DEFAULT VALUES;")
            conn.commit()
            return cursor.lastrowid

    def save(self, short_code: str, original_url: str) -> dict:
        created_at = datetime.now(timezone.utc).isoformat()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO urls (short_code, original_url, created_at, clicks)
                    VALUES (?, ?, ?, 0)
                    """,
                    (short_code, original_url, created_at),
                )
                conn.commit()
        except sqlite3.IntegrityError as exc:
            raise AliasConflictException(f"Alias '{short_code}' already exists.") from exc

        return {
            "short_code": short_code,
            "original_url": original_url,
            "created_at": created_at,
            "clicks": 0,
        }

    def get_by_code(self, short_code: str) -> Optional[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT short_code, original_url, created_at, clicks "
                "FROM urls WHERE short_code = ?",
                (short_code,),
            )
            row = cursor.fetchone()
            if row:
                return {
                    "short_code": row[0],
                    "original_url": row[1],
                    "created_at": row[2],
                    "clicks": row[3],
                }
        return None

    def increment_clicks(self, short_code: str) -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
                (short_code,),
            )
            if cursor.rowcount == 0:
                raise URLNotFoundException(f"URL code '{short_code}' not found.")
            conn.commit()
            cursor.execute(
                "SELECT original_url FROM urls WHERE short_code = ?",
                (short_code,),
            )
            row = cursor.fetchone()
            if row is None:
                raise URLNotFoundException(f"URL code '{short_code}' not found.")
            return row[0]

    def get_analytics(self, short_code: str) -> dict:
        record = self.get_by_code(short_code)
        if record is None:
            raise URLNotFoundException(f"URL code '{short_code}' not found.")
        return record


class PostgresRepository:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("SQLAlchemy is required for PostgresRepository") from exc

        self.engine = create_engine(self.database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._init_db()

    def _init_db(self):
        from sqlalchemy import text

        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS urls (
                        short_code TEXT PRIMARY KEY,
                        original_url TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        clicks INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS sequence (
                        id SERIAL PRIMARY KEY
                    )
                    """
                )
            )

    def check_health(self) -> bool:
        from sqlalchemy import text

        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return True

    def get_next_sequence_id(self) -> int:
        from sqlalchemy import text

        with self.engine.begin() as conn:
            result = conn.execute(text("INSERT INTO sequence DEFAULT VALUES RETURNING id"))
            row = result.fetchone()
            return int(row[0])

    def save(self, short_code: str, original_url: str) -> dict:
        from sqlalchemy import text

        created_at = datetime.now(timezone.utc).isoformat()
        try:
            with self.engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        INSERT INTO urls (short_code, original_url, created_at, clicks)
                        VALUES (:short_code, :original_url, :created_at, 0)
                        """
                    ),
                    {
                        "short_code": short_code,
                        "original_url": original_url,
                        "created_at": created_at,
                    },
                )
        except Exception as exc:
            raise AliasConflictException(f"Alias '{short_code}' already exists.") from exc

        return {
            "short_code": short_code,
            "original_url": original_url,
            "created_at": created_at,
            "clicks": 0,
        }

    def get_by_code(self, short_code: str) -> Optional[dict]:
        from sqlalchemy import text

        with self.engine.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT short_code, original_url, created_at, clicks "
                    "FROM urls WHERE short_code = :short_code"
                ),
                {"short_code": short_code},
            ).fetchone()
        if row:
            return {
                "short_code": row[0],
                "original_url": row[1],
                "created_at": row[2],
                "clicks": row[3],
            }
        return None

    def increment_clicks(self, short_code: str) -> str:
        from sqlalchemy import text

        with self.engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    UPDATE urls
                    SET clicks = clicks + 1
                    WHERE short_code = :short_code
                    RETURNING original_url
                    """
                ),
                {"short_code": short_code},
            )
            row = result.fetchone()
            if row is None:
                raise URLNotFoundException(f"URL code '{short_code}' not found.")
            return row[0]

    def get_analytics(self, short_code: str) -> dict:
        record = self.get_by_code(short_code)
        if record is None:
            raise URLNotFoundException(f"URL code '{short_code}' not found.")
        return record


def get_repository(database_url: str | None = None):
    url = database_url or settings.database_url
    if url.startswith("postgresql"):
        try:
            return PostgresRepository(url)
        except Exception:
            return SQLiteRepository(db_path="urls.db")
    return SQLiteRepository(db_path="urls.db")
