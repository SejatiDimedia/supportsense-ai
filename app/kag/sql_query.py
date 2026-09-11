import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

class SQLRelationalQueryEngine:
    """
    KAG Engine for Relational Databases (PostgreSQL Docker container on port 5433,
    with automatic local SQLite fallback).
    Executes multi-table relational JOIN queries for real-time customer context.
    """
    def __init__(
        self,
        pg_url: Optional[str] = None,
        sqlite_path: str = "./data/relational_sample.db"
    ):
        try:
            from app.config import settings
            default_pg = getattr(settings, "postgres_url", "postgresql://postgres:postgres@localhost:5433/supportsense")
        except Exception:
            default_pg = "postgresql://postgres:postgres@localhost:5433/supportsense"

        self.pg_url = pg_url or os.getenv("POSTGRES_URL", default_pg)
        self.sqlite_path = sqlite_path
        self.use_postgres = self._init_postgres()
        if not self.use_postgres:
            self._init_sqlite()

    def _init_postgres(self) -> bool:
        if not HAS_PSYCOPG2:
            return False
        try:
            with psycopg2.connect(self.pg_url, connect_timeout=2) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM orders;")
                    count = cur.fetchone()[0]
                    logger.info(f"Connected to live PostgreSQL (supportsense_postgres). Orders count: {count}")
                    return True
        except Exception as e:
            logger.debug(f"PostgreSQL not reachable ({e}), using SQLite fallback.")
            return False

    def _init_sqlite(self):
        """Membaca data/schema_relational.sql dan membuat tabel SQLite jika belum ada."""
        schema_file = Path("data/schema_relational.sql")
        if not schema_file.exists():
            return

        with sqlite3.connect(self.sqlite_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers';")
            if cursor.fetchone():
                return
            with open(schema_file, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

    def query_order_context(self, order_number: str) -> Dict[str, Any]:
        """
        Mengeksekusi SQL JOIN 5 tabel di PostgreSQL atau SQLite:
        orders -> customers -> order_items -> products -> issues -> agents
        """
        clean_num = order_number.strip()
        if not clean_num.startswith("#"):
            clean_num = f"#{clean_num}"

        placeholder = "%s" if self.use_postgres else "?"
        query = f"""
        SELECT 
            o.order_number,
            o.status AS order_status,
            o.carrier,
            o.tracking_number,
            c.name AS customer_name,
            c.email AS customer_email,
            p.name AS product_name,
            i.issue_type,
            i.issue_status,
            i.notes AS issue_notes,
            a.name AS agent_name,
            a.role AS agent_role,
            a.email AS agent_email
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        LEFT JOIN order_items oi ON oi.order_id = o.id
        LEFT JOIN products p ON oi.product_id = p.id
        LEFT JOIN issues i ON i.order_id = o.id
        LEFT JOIN agents a ON i.assigned_agent_id = a.id
        WHERE o.order_number = {placeholder};
        """

        row = None
        if self.use_postgres:
            try:
                with psycopg2.connect(self.pg_url, connect_timeout=3) as conn:
                    with conn.cursor() as cur:
                        cur.execute(query, (clean_num,))
                        row = cur.fetchone()
            except Exception as e:
                logger.warning(f"PostgreSQL query failed ({e}), attempting SQLite fallback.")
                self.use_postgres = False

        if not self.use_postgres:
            self._init_sqlite()
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query.replace("%s", "?"), (clean_num,))
                row = cursor.fetchone()

        if not row:
            return {
                "found": False,
                "order_number": order_number,
                "engine": "postgresql" if self.use_postgres else "sqlite",
                "summary": f"Order {clean_num} was not found in relational database records."
            }

        (
            ord_num, ord_status, carrier, tracking,
            cust_name, cust_email, prod_name,
            issue_type, issue_status, issue_notes,
            agent_name, agent_role, agent_email
        ) = row

        # Rangkum fakta relasional menjadi kalimat natural untuk LLM
        summary_parts = [
            f"Order {ord_num} placed by Customer {cust_name} ({cust_email}).",
            f"Contains Product: {prod_name}.",
            f"Current Shipping Status: '{ord_status}' via {carrier} (Tracking: {tracking})."
        ]

        notes_clean = issue_notes.strip() if issue_notes else ""
        if notes_clean and not notes_clean.endswith("."):
            notes_clean += "."

        if issue_type and agent_name:
            summary_parts.append(
                f"Reported Issue: {issue_type} (Status: '{issue_status}'). "
                f"Assigned Support Agent: {agent_name} ({agent_role}, Email: {agent_email})."
            )
            if notes_clean:
                summary_parts.append(f"Notes: {notes_clean}")
        elif issue_type:
            summary_parts.append(f"Reported Issue: {issue_type} (Status: '{issue_status}').")
        else:
            summary_parts.append("No active complaints or delivery issues recorded.")

        return {
            "found": True,
            "order_number": clean_num,
            "engine": "postgresql" if self.use_postgres else "sqlite",
            "summary": " ".join(summary_parts),
            "data": {
                "order": {
                    "order_number": ord_num,
                    "status": ord_status,
                    "carrier": carrier,
                    "tracking_number": tracking
                },
                "customer": {
                    "name": cust_name,
                    "email": cust_email
                },
                "products": [{"name": prod_name}] if prod_name else [],
                "issues": [
                    {
                        "issue_type": issue_type,
                        "status": issue_status,
                        "notes": issue_notes,
                        "assigned_agent": {
                            "name": agent_name,
                            "role": agent_role,
                            "email": agent_email
                        } if agent_name else None
                    }
                ] if issue_type else []
            }
        }
