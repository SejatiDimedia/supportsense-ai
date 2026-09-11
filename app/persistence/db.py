import os
import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from app.config import settings

logger = logging.getLogger(__name__)

def get_db_path() -> Path:
    raw_url = settings.database_url
    if raw_url.startswith("sqlite:///"):
        clean_path = raw_url.replace("sqlite:///", "")
    else:
        clean_path = "./data/support_assistant.db"
    
    path = Path(clean_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

@contextmanager
def get_db_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction rolled back: {e}", exc_info=True)
        raise
    finally:
        conn.close()

def init_db():
    """
    Initializes database tables conforming to PRD Section 8.3.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Conversations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT,
            session_id TEXT,
            role TEXT,
            message TEXT,
            route_taken TEXT,
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Escalations / Pending Webhook Queue table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT,
            reason TEXT,
            payload TEXT,
            webhook_status TEXT DEFAULT 'pending',
            retry_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        logger.info(f"Database initialized successfully at {get_db_path()}")
