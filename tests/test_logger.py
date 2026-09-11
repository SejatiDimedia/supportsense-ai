import json
import logging
from io import StringIO
from app.observability.logger import (
    StructuredJSONFormatter,
    set_trace_id,
    get_trace_id,
    log_event
)

def test_json_formatter_structure():
    set_trace_id("test_trace_123")
    assert get_trace_id() == "test_trace_123"

    formatter = StructuredJSONFormatter()
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    log_event(
        logger=logger,
        event="retrieval_completed",
        layer="rag.retriever",
        message="Retrieved 5 chunks successfully",
        latency_ms=142.5,
        status="success",
        chunks_retrieved=5
    )

    output = stream.getvalue().strip()
    data = json.loads(output)

    assert data["trace_id"] == "test_trace_123"
    assert data["layer"] == "rag.retriever"
    assert data["event"] == "retrieval_completed"
    assert data["latency_ms"] == 142.5
    assert data["status"] == "success"
    assert data["chunks_retrieved"] == 5
    assert "timestamp" in data
