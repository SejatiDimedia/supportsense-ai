import time
import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings
from app.llm.models import CircuitState, LLMResponse

logger = logging.getLogger(__name__)

FALLBACK_ANSWER = (
    "I apologize, but our automated assistant is currently experiencing high load or connectivity issues. "
    "Your inquiry has been logged and our support team will follow up with you shortly."
)

class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern:
    - CLOSED: Normal operation. Success resets failure counter.
    - OPEN: Tripped after `failure_threshold` consecutive failures. Requests immediately fallback.
    - HALF_OPEN: After `recovery_timeout`, allows a single trial request to test if the service has recovered.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def record_success(self):
        if self.state in (CircuitState.HALF_OPEN, CircuitState.OPEN):
            logger.info("Circuit Breaker recovered: Transitioning to CLOSED.")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def record_failure(self):
        self.failure_count += 1
        self.last_state_change = time.time()
        logger.warning(f"Circuit Breaker recorded failure ({self.failure_count}/{self.failure_threshold}).")

        if self.failure_count >= self.failure_threshold and self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit Breaker TRIPPED to OPEN! Blocking outbound calls for {self.recovery_timeout}s.")

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if (now - self.last_state_change) >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                logger.info("Circuit Breaker entering HALF_OPEN trial state.")
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            # Allow single trial
            return True

        return True


class ResilientOllamaClient:
    """
    Centralized, resilient Ollama client with timeout, exponential backoff retries,
    and circuit breaker protection.
    """
    def __init__(
        self,
        base_url: str = settings.ollama_base_url,
        model: str = settings.llm_model,
        timeout: float = 15.0,
        max_retries: int = 2,
        backoff_factor: float = 1.0,
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.circuit_breaker = circuit_breaker or CircuitBreaker()

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
        stream: bool = False
    ) -> LLMResponse:
        t0 = time.time()

        # 1. Circuit Breaker Check
        if not self.circuit_breaker.can_execute():
            elapsed = round((time.time() - t0) * 1000, 2)
            logger.warning("Circuit breaker is OPEN. Returning immediate fallback response.")
            return LLMResponse(
                content=FALLBACK_ANSWER,
                tool_calls=[],
                latency_ms=elapsed,
                is_fallback=True,
                error="Circuit breaker is OPEN: Ollama service temporarily unreachable."
            )

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": temperature}
        }
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/api/chat"

        # 2. Retry loop with exponential backoff
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()

                # Success
                self.circuit_breaker.record_success()
                elapsed = round((time.time() - t0) * 1000, 2)
                msg = data.get("message", {})

                return LLMResponse(
                    content=msg.get("content", "").strip(),
                    tool_calls=msg.get("tool_calls", []),
                    latency_ms=elapsed,
                    is_fallback=False
                )

            except Exception as e:
                self.circuit_breaker.record_failure()
                is_last_attempt = (attempt == self.max_retries)
                logger.warning(
                    f"Ollama call failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}."
                )

                if not is_last_attempt:
                    sleep_time = self.backoff_factor * (2 ** attempt)
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    elapsed = round((time.time() - t0) * 1000, 2)
                    logger.error(f"All {self.max_retries + 1} attempts to Ollama failed. Returning graceful fallback.")
                    return LLMResponse(
                        content=FALLBACK_ANSWER,
                        tool_calls=[],
                        latency_ms=elapsed,
                        is_fallback=True,
                        error=str(e)
                    )

        # Fallback return in case loop completes unexpectedly
        elapsed = round((time.time() - t0) * 1000, 2)
        return LLMResponse(
            content=FALLBACK_ANSWER,
            tool_calls=[],
            latency_ms=elapsed,
            is_fallback=True,
            error="Unexpected execution flow."
        )
