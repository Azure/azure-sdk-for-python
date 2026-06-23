# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Typed exceptions for actionable failure modes.

Customers should branch on exception type rather than grepping message strings:

    from azure.ai.finetuning_sessions import (
        BatchTooLargeError,
        NoCapacityError,
        TrainingEngineError,
        ContentionError,
        RequestValidationError,
    )

    try:
        result = session.forward_backward(batch, loss_fn="cross_entropy")
    except BatchTooLargeError as e:
        # Split batch and retry
        ...
    except NoCapacityError as e:
        # Wait e.retry_after_sec, or switch project
        ...
    except TrainingEngineError as e:
        # Stop the run — model weights are lost
        ...

Each exception carries structured metadata extracted from the server's response
body so callers can make decisions without string parsing.
"""
from __future__ import annotations

from typing import Any, Optional

from azure.core.exceptions import HttpResponseError


class FineTuningSessionsError(HttpResponseError):
    """Base class for all typed SDK exceptions.

    Inherits from ``azure.core.exceptions.HttpResponseError`` so existing
    ``except HttpResponseError`` handlers still catch these.
    """

    def __init__(self, message: str, *, response: Any = None, **kwargs: Any) -> None:
        super().__init__(message=message, response=response, **kwargs)


class BatchTooLargeError(FineTuningSessionsError):
    """The batch exceeded the server's size limit.

    Action: split the batch into smaller chunks and retry.

    Attributes:
        max_batch_size: The maximum batch size the server accepts (if reported).
        actual_batch_size: The batch size that was rejected (if reported).
    """

    def __init__(
        self,
        message: str,
        *,
        max_batch_size: Optional[int] = None,
        actual_batch_size: Optional[int] = None,
        response: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, response=response, **kwargs)
        self.max_batch_size = max_batch_size
        self.actual_batch_size = actual_batch_size


class NoCapacityError(FineTuningSessionsError):
    """No engine capacity is currently available.

    Action: wait ``retry_after_sec`` seconds and retry, or switch to a
    different project/endpoint.

    Attributes:
        retry_after_sec: Suggested wait time in seconds before retrying.
        reason: Server-reported reason string (e.g. ``"engine_busy"``).
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after_sec: Optional[float] = None,
        reason: Optional[str] = None,
        response: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, response=response, **kwargs)
        self.retry_after_sec = retry_after_sec
        self.reason = reason


class TrainingEngineError(FineTuningSessionsError):
    """The engine serving this session has died.

    Action: stop the training run, alert on-call. LoRA weights in VRAM are
    lost. Do NOT retry on the same session — create a new one (optionally
    from the last checkpoint).

    Attributes:
        session_id: The session that was being served.
        error_code: Server error code (e.g. ``"worker_crashed"``).
        debug_ref: Opaque reference for support tickets.
    """

    def __init__(
        self,
        message: str,
        *,
        session_id: Optional[str] = None,
        error_code: Optional[str] = None,
        debug_ref: Optional[str] = None,
        response: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, response=response, **kwargs)
        self.session_id = session_id
        self.error_code = error_code
        self.debug_ref = debug_ref


class ContentionError(FineTuningSessionsError):
    """The engine is temporarily contended (busy with other tenants).

    Action: back off with exponential delay. Do NOT retry immediately.

    Attributes:
        retry_after_sec: Suggested wait time before retrying.
        reason: Server-reported reason string.
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after_sec: Optional[float] = None,
        reason: Optional[str] = None,
        response: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, response=response, **kwargs)
        self.retry_after_sec = retry_after_sec
        self.reason = reason


class RequestValidationError(FineTuningSessionsError):
    """One or more datums in the batch were rejected as invalid.

    Action: this is terminal for the affected datums — fix the data.

    Attributes:
        field: The field that failed validation (e.g. ``"forward_backward_input.data"``).
        error_code: Server error code (e.g. ``"invalid_request"``).
        debug_ref: Opaque reference for support tickets.
    """

    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
        error_code: Optional[str] = None,
        debug_ref: Optional[str] = None,
        response: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, response=response, **kwargs)
        self.field = field
        self.error_code = error_code
        self.debug_ref = debug_ref


def _classify_http_error(
    status_code: int,
    body: Optional[dict],
    *,
    response: Any = None,
    session_id: Optional[str] = None,
) -> Optional[FineTuningSessionsError]:
    """Attempt to classify an HTTP error response into a typed exception.

    Returns ``None`` if the error doesn't match any known pattern (caller
    should fall through to generic error handling).
    """
    if body is None:
        body = {}

    # --- HTTP 413: Batch too large ---
    if status_code == 413:
        msg = body.get("message") or body.get("detail") or "Batch too large"
        field = body.get("field")
        # Try to extract numbers from the message
        max_size = None
        actual_size = None
        if isinstance(msg, str):
            import re
            # "Batch size (N) exceeds the maximum allowed (M)"
            m = re.search(r"Batch size \((\d+)\) exceeds the maximum allowed \((\d+)\)", msg)
            if m:
                actual_size = int(m.group(1))
                max_size = int(m.group(2))
        if field and "data" in field:
            return BatchTooLargeError(
                msg,
                max_batch_size=max_size,
                actual_batch_size=actual_size,
                response=response,
            )
        # 413 for metadata is not a batch error — return None to let generic handling take over
        return BatchTooLargeError(
            msg, max_batch_size=max_size, actual_batch_size=actual_size, response=response
        )

    # --- HTTP 503: No capacity / contention ---
    if status_code == 503:
        reason = body.get("reason", "")
        msg = body.get("message") or body.get("detail") or "No available engine capacity"
        retry_after: Optional[float] = None
        if body.get("retry_after_sec") is not None:
            retry_after = float(body["retry_after_sec"])

        # If the body is a plain string (legacy format), extract from detail
        if isinstance(msg, str) and ("capacity" in msg.lower() or "no engine" in msg.lower()):
            return NoCapacityError(
                msg, retry_after_sec=retry_after, reason=reason or "engine_busy", response=response
            )
        if reason == "engine_busy":
            return NoCapacityError(
                msg, retry_after_sec=retry_after, reason=reason, response=response
            )
        # Generic 503 — treat as contention
        return ContentionError(
            msg, retry_after_sec=retry_after, reason=reason or None, response=response
        )

    # --- HTTP 500: Engine dead / worker crashed / capacity exhaustion ---
    if status_code == 500:
        # The body may be a flat dict or nested under "detail".
        detail = body.get("detail") if isinstance(body.get("detail"), dict) else None
        effective = detail or body
        msg = (
            effective.get("error_message")
            or effective.get("message")
            or body.get("detail")
            or body.get("error")
            or "Internal server error"
        )
        error_type = effective.get("type", "")
        error_code = effective.get("error_code") or effective.get("code")
        debug_ref = effective.get("debug_ref")

        # Capacity exhaustion: server returns type="internal_model_error" with
        # a message mentioning capacity. Should really be a 503,
        # but older servers return 500.
        if isinstance(msg, str) and ("capacity" in msg.lower() or "no engine" in msg.lower()):
            return NoCapacityError(
                msg,
                retry_after_sec=None,
                reason=error_type or "no_capacity",
                response=response,
            )

        if error_code in ("worker_crashed", "engine_oom", "engine_timeout"):
            return TrainingEngineError(
                msg,
                session_id=session_id,
                error_code=error_code,
                debug_ref=debug_ref,
                response=response,
            )
        # Check message heuristics for legacy plain-string responses
        if isinstance(msg, str) and any(
            kw in msg.lower() for kw in ("engine", "dead", "crashed", "died")
        ):
            return TrainingEngineError(
                msg,
                session_id=session_id,
                error_code=error_code,
                debug_ref=debug_ref,
                response=response,
            )
        return None  # Unknown 500 — don't classify

    # --- HTTP 400/422: Malformed datum / invalid request ---
    if status_code in (400, 422):
        error_type = body.get("type", "")
        msg = body.get("message") or body.get("detail") or "Invalid request"
        field = body.get("field")
        error_code = body.get("error_code") or body.get("code")
        debug_ref = body.get("debug_ref")

        if error_type == "validation_error" or error_code == "invalid_request":
            return RequestValidationError(
                msg,
                field=field,
                error_code=error_code or "invalid_request",
                debug_ref=debug_ref,
                response=response,
            )
        return None

    return None


def _classify_poll_failure(
    envelope: dict,
    *,
    session_id: Optional[str] = None,
) -> Optional[FineTuningSessionsError]:
    """Classify a failed poll-endpoint envelope into a typed exception.

    The poll endpoint returns ``{"status": "failed", "error": "...", "error_code": "...", ...}``
    when a GPU operation fails. This function translates known error codes into typed exceptions.

    Returns ``None`` if the failure doesn't match any known pattern.
    """
    error_code = envelope.get("error_code") or envelope.get("code")
    error_msg = envelope.get("error") or "Operation failed"
    debug_ref = envelope.get("debug_ref")

    if error_code == "engine_oom":
        return BatchTooLargeError(
            error_msg + " (Try a smaller batch or shorter sequences.)",
            response=None,
        )

    if error_code in ("worker_crashed", "engine_timeout"):
        return TrainingEngineError(
            error_msg,
            session_id=session_id,
            error_code=error_code,
            debug_ref=debug_ref,
        )

    if error_code == "invalid_request":
        return RequestValidationError(
            error_msg,
            error_code=error_code,
            debug_ref=debug_ref,
        )

    if error_code == "model_not_found":
        return TrainingEngineError(
            error_msg,
            session_id=session_id,
            error_code=error_code,
            debug_ref=debug_ref,
        )

    return None


# Backward-compat aliases.
EngineDeadError = TrainingEngineError
MalformedDatumError = RequestValidationError

__all__ = [
    "FineTuningSessionsError",
    "BatchTooLargeError",
    "NoCapacityError",
    "TrainingEngineError",
    "EngineDeadError",
    "ContentionError",
    "RequestValidationError",
    "MalformedDatumError",
]
