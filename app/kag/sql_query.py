import sqlite3
import re
from pathlib import Path
from typing import Dict, Any, Optional

class SQLRelationalQueryEngine:
    """
    KAG Engine berbasis SQL Relasional (PostgreSQL / MySQL / SQLite).
    Menggantikan Graph Traversal dengan SQL JOIN query berkecepatan tinggi.
    """
    def __init__(self, db_path: str = "./data/relational_sample.db"):
        self.db_path = db_path
        self._ensure_database_initialized()

    def _ensure_database_initialized(self):
        """Membaca data/schema_relational.sql dan membuat tabel jika belum ada."""
        schema_file = Path("data/schema_relational.sql")
        if not schema_file.exists():
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers';")
            if cursor.fetchone():
                return
            with open(schema_file, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

    def query_order_context(self, order_number: str) -> Dict[str, Any]:
        """
        Mengeksekusi SQL JOIN 5 tabel:
        orders -> customers -> order_items -> products -> issues -> agents
        """
        # Normalisasi nomor order (misal '#4521' atau '4521')
        clean_num = order_number.strip()
        if not clean_num.startswith("#"):
            clean_num = f"#{clean_num}"

        query = """
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
        WHERE o.order_number = ?;
        """

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (clean_num,))
            row = cursor.fetchone()

        if not row:
            return {
                "found": False,
                "order_number": order_number,
                "summary": f"Order {clean_num} was not found in the relational database records."
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

        if issue_type and agent_name:
            summary_parts.append(
                f"Reported Issue: {issue_type} (Status: '{issue_status}'). "
                f"Assigned Support Agent: {agent_name} ({agent_role}, Email: {agent_email}). "
                f"Notes: {issue_notes}."
            )
        elif issue_type:
            summary_parts.append(f"Reported Issue: {issue_type} (Status: '{issue_status}').")
        else:
            summary_parts.append("No active complaints or delivery issues recorded.")

        return {
            "found": True,
            "order_number": clean_num,
            "summary": " ".join(summary_parts)
        }
