import json
import logging
import sys
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Optional, Dict, Any

from app.config import settings

# ContextVar to maintain trace_id across request lifecycle
current_trace_id: ContextVar[str] = ContextVar("current_trace_id", default="system")

def set_trace_id(trace_id: str):
    current_trace_id.set(trace_id)

def get_trace_id() -> str:
    return current_trace_id.get()

class StructuredJSONFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects conforming to PRD Section 6.1.
    """
    def format(self, record: logging.LogRecord) -> str:
        trace_id = getattr(record, "trace_id", None) or get_trace_id()
        layer = getattr(record, "layer", record.name)
        event = getattr(record, "event", "log_message")
        latency_ms = getattr(record, "latency_ms", None)
        status = getattr(record, "status", "success" if record.levelno < logging.WARNING else "warning" if record.levelno < logging.ERROR else "error")

        log_payload: Dict[str, Any] = {
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "layer": layer,
            "event": event,
            "message": record.getMessage(),
            "status": status
        }

        if latency_ms is not None:
            log_payload["latency_ms"] = latency_ms

        # Include any custom extra attributes
        if hasattr(record, "custom_fields") and isinstance(record.custom_fields, dict):
            log_payload.update(record.custom_fields)

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload)

def setup_structured_logging(level: Optional[str] = None):
    log_level = getattr(logging, (level or settings.log_level).upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJSONFormatter())
    root_logger.addHandler(handler)

def log_event(
    logger: logging.Logger,
    event: str,
    layer: str,
    message: str = "",
    latency_ms: Optional[float] = None,
    status: str = "success",
    level: int = logging.INFO,
    **custom_fields
):
    """
    Helper to emit structured lifecycle events matching PRD spec.
    """
    extra = {
        "event": event,
        "layer": layer,
        "latency_ms": latency_ms,
        "status": status,
        "custom_fields": custom_fields
    }
    logger.log(level, message or event, extra=extra)
