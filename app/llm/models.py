from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

class CircuitState(str, Enum):
    CLOSED = "CLOSED"       # Normal: Requests pass through to LLM
    OPEN = "OPEN"           # Tripped: Requests fail immediately / fallback
    HALF_OPEN = "HALF_OPEN" # Testing: Allows trial request to check recovery

@dataclass
class LLMResponse:
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    latency_ms: float = 0.0
    is_fallback: bool = False
    error: Optional[str] = None
