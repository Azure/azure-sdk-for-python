# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Bounded Decision execution metadata and request-owned observations."""

import json
import logging
import math
import re
import time
from typing import Any, Dict, Optional

from azure.core.pipeline.policies import CustomHookPolicy

LOGGER = logging.getLogger(__name__)
_PREFIX = "azure.ai.evaluation.decision."


def _integer(value: Any, maximum: Optional[int] = None) -> bool:
    return (
        isinstance(value, int) and not isinstance(value, bool) and 0 <= value and (maximum is None or value <= maximum)
    )


def validated_execution(value: Any) -> Optional[Dict[str, Any]]:
    """Copy only a complete, strictly typed shared or independent execution summary.

    :param value: The untrusted summary carrier.
    :type value: Any
    :return: Known validated fields, or None for an invalid carrier.
    :rtype: Optional[Dict[str, Any]]
    """
    if not isinstance(value, dict):
        return None
    if "operation_id" in value:
        keys = {
            "operation_id",
            "attempt_count",
            "unknown_usage_attempt_count",
            "result_usage_scope",
            "usage_completeness",
        }
        if set(value) != keys or not all(
            (
                isinstance(value["operation_id"], str)
                and re.fullmatch("[0-9a-f]{32}", value["operation_id"]) is not None,
                _integer(value["attempt_count"]),
                _integer(value["unknown_usage_attempt_count"]),
                value["result_usage_scope"] == "final_response_only",
                value["usage_completeness"]
                in ("all_attempts_reported", "some_attempts_reported", "no_attempts_reported"),
            )
        ):
            return None
        return dict(value)
    keys = {"attempt_count", "retry_count", "elapsed_ms", "outcome", "last_http_status", "usage_state"}
    elapsed = value.get("elapsed_ms")
    status = value.get("last_http_status")
    if (
        not keys - {"last_http_status"} <= value.keys()
        or isinstance(elapsed, bool)
        or not isinstance(elapsed, (int, float))
    ):
        return None
    if not all(
        (
            _integer(value["attempt_count"], 21),
            _integer(value["retry_count"], 20),
            0 <= elapsed <= 86400000 and math.isfinite(elapsed),
            value["outcome"] in ("completed", "error", "deadline", "cancelled"),
            value["usage_state"] in ("known", "partial", "unknown"),
            status is None or (_integer(status, 599) and status >= 100),
        )
    ):
        return None
    return {key: value.get(key) for key in keys}


def _diagnostic(message: str) -> None:
    # Observer failures must not replace a model result, even if diagnostic logging is also broken.
    try:
        LOGGER.warning(message)
    except Exception:  # pylint: disable=broad-except
        pass


class DecisionExecution(CustomHookPolicy):
    """One operation's per-attempt pipeline policy; never shared between concurrent calls."""

    def __init__(self, logger: Any, max_response_bytes: Optional[int]) -> None:
        super().__init__()
        self.logger = logger
        self.max_response_bytes = max_response_bytes
        self.started = time.monotonic()
        self.attempt_started: Optional[float] = None
        self.attempt_count = 0
        self.known_usage_attempts = 0
        self.partial_usage_attempts = 0
        self.last_http_status: Optional[int] = None
        self.outcome = "error"
        self.instruments: Optional[Dict[str, Any]] = None

    def on_request(self, request: Any) -> None:
        self.attempt_count += 1
        self.attempt_started = time.monotonic()
        super().on_request(request)

    def on_response(self, request: Any, response: Any) -> None:
        raw = response.http_response
        status = raw.status_code
        self.last_http_status = status if _integer(status, 599) and status >= 100 else None
        known = False
        partial = False
        try:
            body = raw.body()
            if self.max_response_bytes is None or len(body) <= self.max_response_bytes:
                payload = json.loads(body)
                usage = payload.get("usage") if isinstance(payload, dict) else None
                if isinstance(usage, dict):
                    tokens = [_integer(usage.get(key)) for key in ("input_tokens", "output_tokens")]
                    known, partial = all(tokens), any(tokens)
        except (ValueError, TypeError):
            pass
        self.known_usage_attempts += int(known)
        self.partial_usage_attempts += int(partial and not known)
        self.finish_attempt(
            "completed" if status == 200 else "error",
            "known" if known else "partial" if partial else "unknown",
            self.last_http_status,
        )
        super().on_response(request, response)

    def on_exception(self, request: Any) -> None:
        self.finish_attempt("error")

    def summary(self, outcome: str) -> Dict[str, Any]:
        return {
            "attempt_count": self.attempt_count,
            "retry_count": max(0, self.attempt_count - 1),
            "elapsed_ms": (time.monotonic() - self.started) * 1000,
            "outcome": outcome,
            "last_http_status": self.last_http_status,
            "usage_state": (
                "known"
                if self.attempt_count and self.known_usage_attempts == self.attempt_count
                else "partial" if self.known_usage_attempts or self.partial_usage_attempts else "unknown"
            ),
        }

    def finish_attempt(self, outcome: str, usage: str = "unknown", status: Optional[int] = None) -> None:
        if self.attempt_started is None:
            return
        elapsed = (time.monotonic() - self.attempt_started) * 1000
        self.attempt_started = None
        self.emit("attempt", outcome, self.summary(outcome), elapsed, usage, status)

    def finish(self, outcome: str) -> Optional[Dict[str, Any]]:
        self.finish_attempt(outcome)
        summary = self.summary(outcome)
        self.emit("execution", outcome, summary, summary["elapsed_ms"], summary["usage_state"])
        accepted = validated_execution(summary)
        if accepted is None:
            _diagnostic("Decision execution summary exceeds the hosted metadata bounds; summary omitted.")
        return accepted

    def emit(
        self,
        phase: str,
        outcome: str,
        summary: Dict[str, Any],
        elapsed: float,
        usage: str,
        status: Optional[int] = None,
    ) -> None:
        status = self.last_http_status if phase == "execution" else status
        dimensions = {
            "backend": "decision",
            "route": "shared_sdk",
            "phase": phase,
            "outcome": outcome,
            "usage_state": usage,
            "http_status_class": f"{status // 100}xx" if status is not None else "unknown",
            "throttled": str(status == 429).lower(),
        }
        try:
            logger = self.logger
            if logger is not None and logger.isEnabledFor(logging.INFO):
                fields = {
                    "decision_dimensions": json.dumps(dimensions),
                    "decision_execution": json.dumps(summary),
                }
                while isinstance(logger, logging.LoggerAdapter):
                    # Python 3.10 LoggerAdapter.process replaces, rather than merges, per-call extra fields.
                    _, kwargs = logger.process("DECISION_EXECUTION_OBSERVATION", {"extra": dict(fields)})
                    fields = {**kwargs.get("extra", {}), **fields}
                    logger = logger.logger
                logger.info("DECISION_EXECUTION_OBSERVATION", extra=fields)
        except Exception:  # pylint: disable=broad-except
            _diagnostic("Decision execution log sink failed; evaluation and metrics continue.")
        try:
            self.emit_metrics(phase, elapsed, dimensions)
        except Exception:  # pylint: disable=broad-except
            _diagnostic("Decision execution metric sink failed; evaluation and logs continue.")

    def emit_metrics(self, phase: str, elapsed: float, dimensions: Dict[str, str]) -> None:
        if self.instruments is None:
            try:
                from opentelemetry.metrics import get_meter  # pylint: disable=import-outside-toplevel
            except ImportError:
                self.instruments = {}
                LOGGER.debug("Decision metrics require the optional opentelemetry extra.")
                return
            meter = get_meter("azure.ai.evaluation.decision")
            self.instruments = {
                key: meter.create_counter(_PREFIX + key)
                for key in ("provider.attempts", "provider.retries", "operations")
            }
            self.instruments["provider.duration"] = meter.create_histogram(_PREFIX + "provider.duration", unit="ms")
        if not self.instruments:
            return
        if phase == "attempt":
            self.instruments["provider.attempts"].add(1, attributes=dimensions)
            self.instruments["provider.duration"].record(elapsed, attributes=dimensions)
            if self.attempt_count > 1:
                self.instruments["provider.retries"].add(1, attributes=dimensions)
        else:
            self.instruments["operations"].add(1, attributes=dimensions)
