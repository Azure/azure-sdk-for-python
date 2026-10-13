# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Transport-only execution settings for hosted decision evaluators."""

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, Literal, Optional, Tuple

from ..._exceptions import EvaluationException


@dataclass(frozen=True)
class DecisionRequestObservation:
    """A sanitized per-attempt receipt. Unknown usage and model values remain ``None``."""

    attempt: int
    outcome: Literal["response", "error", "timeout", "cancelled", "request_rejected"]
    http_status: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    model: Optional[str] = None


@dataclass(frozen=True)
class DecisionExecutionPolicy:
    """Internal hosted execution policy, separate from the model configuration.

    ``timeout_seconds`` bounds each transport connect/read; ``deadline_seconds`` caps the entire
    operation, including authentication and azure-core retries. Request budgets measure compact UTF-8 JSON,
    not estimated tokens. ``max_state_question_bytes`` bounds the largest ``{"state", "question"}`` pair.
    ``max_response_bytes`` limits the body accepted for JSON parsing, not transport buffering or allocation.
    Cancellation is polled every 50 ms, including during authentication and retry backoff.
    Cancellation and deadlines stop awaiting authentication, but cannot forcibly interrupt a synchronous
    credential call already running in a worker thread or bound that thread's shutdown time.
    The synchronous observer receives transport receipts only; callback failures are explicit errors.
    """

    timeout_seconds: Optional[float] = None
    deadline_seconds: Optional[float] = None
    max_retries: int = 3
    max_request_bytes: Optional[int] = None
    max_state_question_bytes: Optional[int] = None
    max_response_bytes: Optional[int] = None
    cancellation_requested: Optional[Callable[[], bool]] = None
    observer: Optional[Callable[[DecisionRequestObservation], None]] = None

    def __post_init__(self) -> None:
        for name in ("timeout_seconds", "deadline_seconds"):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0
            ):
                raise ValueError(f"{name} must be a positive finite number.")
        for name in ("max_request_bytes", "max_state_question_bytes", "max_response_bytes"):
            value = getattr(self, name)
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value <= 0):
                raise ValueError(f"{name} must be a positive integer.")
        if isinstance(self.max_retries, bool) or not isinstance(self.max_retries, int) or self.max_retries < 0:
            raise ValueError("max_retries must be a nonnegative integer.")
        for name in ("cancellation_requested", "observer"):
            value = getattr(self, name)
            if value is not None and not callable(value):
                raise ValueError(f"{name} must be callable.")


class DecisionEvaluationException(EvaluationException):
    """An execution or interpretation error retaining only known, sanitized decision metadata."""

    def __init__(
        self,
        message: str,
        *,
        observations: Tuple[DecisionRequestObservation, ...] = (),
        properties: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.observations = tuple(observations)
        self.properties = properties
        super().__init__(message, **kwargs)
