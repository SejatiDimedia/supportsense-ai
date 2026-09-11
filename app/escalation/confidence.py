from typing import List, Optional

ESCALATION_CONFIDENCE_THRESHOLD = 0.60

def should_escalate(confidence_score: float, route_taken: str, is_security_trigger: bool = False) -> bool:
    """
    Determines if human handoff is warranted according to PRD Section 10 & 16.1:
    Triggered when confidence_score < 0.60 OR route_taken == 'escalated' OR security trigger.
    """
    if is_security_trigger:
        return True
    if route_taken == "escalated":
        return True
    if confidence_score < ESCALATION_CONFIDENCE_THRESHOLD:
        return True
    return False

def calculate_confidence_score(
    route_taken: str,
    has_rag_context: bool,
    order_found: Optional[bool] = None,
    is_malicious: bool = False
) -> float:
    """
    Returns normalized confidence score [0.0 - 1.0].
    """
    if is_malicious:
        return 0.20
    if order_found is False:
        return 0.40
    if route_taken == "hybrid":
        return 0.95
    if route_taken == "kag":
        return 0.92
    if route_taken == "rag":
        return 0.89
    if route_taken == "direct":
        return 1.00
    return 0.50
