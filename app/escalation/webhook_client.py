import logging
from typing import Dict, Any, Optional
import httpx

from app.config import settings
from app.persistence.repository import repo, ConversationRepository

logger = logging.getLogger(__name__)

class N8nWebhookClient:
    """
    Dispatches incident tickets to n8n escalation workflow.
    Guarantees zero-loss delivery: if n8n is unreachable, stores
    in SQLite local pending queue for background retries.
    """
    def __init__(
        self,
        webhook_url: str = settings.n8n_webhook_url,
        repository: Optional[ConversationRepository] = None,
        timeout: float = 4.0
    ):
        self.webhook_url = webhook_url
        self.repo = repository or repo
        self.timeout = timeout

    def send_escalation_webhook(
        self,
        trace_id: str,
        reason: str,
        user_message: str,
        session_id: str,
        route_taken: str = "escalated",
        confidence_score: float = 0.30
    ) -> Dict[str, Any]:
        payload = {
            "trace_id": trace_id,
            "session_id": session_id,
            "reason": reason,
            "user_message": user_message,
            "route_taken": route_taken,
            "confidence_score": confidence_score
        }

        # 1. Attempt sending to n8n webhook
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.webhook_url, json=payload)
                if resp.status_code in (200, 201):
                    logger.info(f"[{trace_id}] Successfully dispatched escalation to n8n webhook.")
                    esc_id = self.repo.save_escalation(trace_id, reason, payload, webhook_status="sent")
                    return {"status": "sent", "escalation_id": esc_id, "response": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text}
                else:
                    logger.warning(f"[{trace_id}] n8n returned status {resp.status_code}. Enqueuing locally.")
        except Exception as e:
            logger.warning(f"[{trace_id}] Could not reach n8n webhook ({e}). Enqueuing locally to SQLite.")

        # 2. Resilience Fallback: Store locally in SQLite pending queue
        esc_id = self.repo.save_escalation(trace_id, reason, payload, webhook_status="pending")
        return {"status": "pending", "escalation_id": esc_id, "queued_locally": True}

    def process_pending_retries(self, max_items: int = 10) -> int:
        """
        Background worker method to retry pending webhook deliveries.
        """
        pending_items = self.repo.get_pending_escalations(limit=max_items)
        if not pending_items:
            return 0

        successfully_sent = 0
        for item in pending_items:
            item_id = item["id"]
            trace_id = item["trace_id"]
            payload = item.get("payload", {})
            retries = item.get("retry_count", 0)

            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(self.webhook_url, json=payload)
                    if resp.status_code in (200, 201):
                        self.repo.update_escalation_status(item_id, status="sent")
                        successfully_sent += 1
                        logger.info(f"[{trace_id}] Successfully retried pending escalation #{item_id}.")
                        continue
            except Exception as e:
                logger.debug(f"[{trace_id}] Retry failed for escalation #{item_id}: {e}")

            # Update failure & increment retry
            next_status = "failed" if retries >= 5 else "pending"
            self.repo.update_escalation_status(item_id, status=next_status, increment_retry=True)

        return successfully_sent

# Global singleton
webhook_client = N8nWebhookClient()
