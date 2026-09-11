import json
import logging
from typing import List, Dict, Any, Optional
from app.persistence.db import get_db_connection

logger = logging.getLogger(__name__)

class ConversationRepository:
    """
    Data Access Layer for conversations and escalation records.
    """
    def save_message(
        self,
        trace_id: str,
        session_id: str,
        role: str,
        message: str,
        route_taken: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversations (trace_id, session_id, role, message, route_taken, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (trace_id, session_id, role, message, route_taken, confidence_score)
            )
            return cursor.lastrowid

    def get_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, trace_id, session_id, role, message, route_taken, confidence_score, created_at
                FROM conversations
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?;
                """,
                (session_id, limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def save_escalation(
        self,
        trace_id: str,
        reason: str,
        payload: Dict[str, Any],
        webhook_status: str = "pending"
    ) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO escalations (trace_id, reason, payload, webhook_status, retry_count)
                VALUES (?, ?, ?, ?, 0);
                """,
                (trace_id, reason, json.dumps(payload), webhook_status)
            )
            esc_id = cursor.lastrowid
            logger.info(f"[{trace_id}] Saved escalation #{esc_id} with status '{webhook_status}'")
            return esc_id

    def get_pending_escalations(self, limit: int = 10) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, trace_id, reason, payload, webhook_status, retry_count, created_at
                FROM escalations
                WHERE webhook_status = 'pending'
                ORDER BY id ASC
                LIMIT ?;
                """,
                (limit,)
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                if item.get("payload"):
                    try:
                        item["payload"] = json.loads(item["payload"])
                    except Exception:
                        pass
                results.append(item)
            return results

    def update_escalation_status(
        self,
        escalation_id: int,
        status: str,
        increment_retry: bool = False
    ):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if increment_retry:
                cursor.execute(
                    """
                    UPDATE escalations
                    SET webhook_status = ?, retry_count = retry_count + 1
                    WHERE id = ?;
                    """,
                    (status, escalation_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE escalations
                    SET webhook_status = ?
                    WHERE id = ?;
                    """,
                    (status, escalation_id)
                )

    def get_escalations_by_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, trace_id, reason, payload, webhook_status, retry_count, created_at
                FROM escalations
                WHERE trace_id = ?
                ORDER BY id ASC;
                """,
                (trace_id,)
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                if item.get("payload"):
                    try:
                        item["payload"] = json.loads(item["payload"])
                    except Exception:
                        pass
                results.append(item)
            return results

    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return self.get_history(session_id, limit)

# Global repository singleton
repo = ConversationRepository()
