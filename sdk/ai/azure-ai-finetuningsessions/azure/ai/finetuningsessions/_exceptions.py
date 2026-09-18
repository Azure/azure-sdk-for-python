# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Typed exceptions for actionable failure modes.

Customers should branch on exception type rather than grepping message strings:

    from azure.ai.finetuningsessions import (
        BatchTooLargeError,
        NoCapacityError,
        TrainingEngineError,
        OperationResultUnavailableError,
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


class RateLimitedError(NoCapacityError):
    """The request was throttled with HTTP 429 (rate limit / budget exhausted).

    A subclass of :class:`NoCapacityError` so existing ``except NoCapacityError``
    handlers still catch it. Raised by the SDK when a sample submission stays
    throttled past the client throttle timeout.

    Action: wait ``retry_after_sec`` seconds and retry, or reduce concurrency.
    """


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


class OperationResultUnavailableError(FineTuningSessionsError):
    """A terminal operation's result payload can no longer be returned.

    This error is always non-retryable. When ``operation_completed`` is true,
    the operation's side effects may already have been applied, so submitting
    it again could duplicate a training update. When it is false, the operation
    failed but its original error details are no longer available.

    Attributes:
        operation_completed: Whether the server durably recorded the operation
            as completed before its result payload became unavailable.
        error_code: Server error code identifying the payload-loss outcome.
        debug_ref: Opaque reference for support tickets.
    """

    def __init__(
        self,
        message: str,
        *,
        operation_completed: bool,
        error_code: Optional[str] = None,
        debug_ref: Optional[str] = None,
        response: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, response=response, **kwargs)
        self.operation_completed = operation_completed
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


class RequestRetryableError(FineTuningSessionsError):
    """A request failed transiently and the server marked it safe to retry.

    Generic, operation-agnostic retry signal: whenever a failed request
    envelope carries ``should_retry: true``, the server is telling the client
    that this failure is not the caller's fault and a fresh attempt (a NEW
    request id) can succeed. Current producers include sampling failures such
    as a drained/restarted serving pod, an orphan-sweep reclaim, or an upstream
    read timeout — but any operation may opt in to this contract by setting the
    flag; the SDK does not gate on specific error codes.

    The SDK's ``_post_and_poll`` catches this and resubmits automatically
    (bounded retries). It is only surfaced to the caller once retries are
    exhausted.

    Attributes:
        error_code: Server error code, if provided (e.g. ``"request_orphaned"``,
            ``"request_timeout"``). Informational only — retry is driven by
            ``should_retry``, not the code.
        retry_after_sec: Suggested wait before resubmitting, if provided.
        debug_ref: Opaque reference for support tickets.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        retry_after_sec: Optional[float] = None,
        debug_ref: Optional[str] = None,
        response: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, response=response, **kwargs)
        self.error_code = error_code
        self.retry_after_sec = retry_after_sec
        self.debug_ref = debug_ref


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
        detail = body.get("detail") if isinstance(body.get("detail"), dict) else None
        effective = detail or body
        msg = effective.get("message") or body.get("detail") or "Batch too large"
        field = effective.get("field")
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
        return BatchTooLargeError(msg, max_batch_size=max_size, actual_batch_size=actual_size, response=response)

    # --- HTTP 503: No capacity / contention ---
    if status_code == 503:
        reason = body.get("reason", "")
        msg = body.get("message") or body.get("detail") or "No available engine capacity"
        retry_after: Optional[float] = None
        if body.get("retry_after_sec") is not None:
            retry_after = float(body["retry_after_sec"])

        # If the body is a plain string (legacy format), extract from detail
        if isinstance(msg, str) and ("capacity" in msg.lower() or "no engine" in msg.lower()):
            return NoCapacityError(msg, retry_after_sec=retry_after, reason=reason or "engine_busy", response=response)
        if reason == "engine_busy":
            return NoCapacityError(msg, retry_after_sec=retry_after, reason=reason, response=response)
        # Generic 503 — treat as contention
        return ContentionError(msg, retry_after_sec=retry_after, reason=reason or None, response=response)

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
        if isinstance(msg, str) and any(kw in msg.lower() for kw in ("engine", "dead", "crashed", "died")):
            return TrainingEngineError(
                msg,
                session_id=session_id,
                error_code=error_code,
                debug_ref=debug_ref,
                response=response,
            )
        return None  # Unknown 500 — don't classify

    # --- HTTP 409: Terminal engine-dead conflict (non-retryable) ---
    # The server returns 409 (not 500) for a permanently engine-dead model so
    # the azure-core transport RetryPolicy does NOT retry it (409 is not in the
    # default retry-status set). The body mirrors the structured shape used
    # elsewhere: {reason, message, error_code, ...}, possibly nested under
    # "detail". We still surface it as the terminal TrainingEngineError so
    # callers branch on type exactly as they did for the legacy 500.
    if status_code == 409:
        detail = body.get("detail") if isinstance(body.get("detail"), dict) else None
        effective = detail or body
        reason = effective.get("reason", "")
        msg = (
            effective.get("message")
            or (body.get("detail") if isinstance(body.get("detail"), str) else None)
            or effective.get("error")
            or "The model's engine has died"
        )
        error_code = effective.get("error_code") or effective.get("code")
        debug_ref = effective.get("debug_ref")
        if (
            reason == "engine_dead"
            or error_code == "engine_dead"
            or (isinstance(msg, str) and any(kw in msg.lower() for kw in ("engine", "dead", "died", "crashed")))
        ):
            return TrainingEngineError(
                msg,
                session_id=session_id,
                error_code=error_code or "engine_dead",
                debug_ref=debug_ref,
                response=response,
            )
        return None  # Unknown 409 — don't classify

    # --- HTTP 429: Rate limited / budget exhausted ---
    if status_code == 429:
        reason = body.get("reason") or "rate_limited"
        msg = body.get("message") or body.get("detail") or "Rate limited"
        retry_after: Optional[float] = None
        if body.get("retry_after_sec") is not None:
            try:
                retry_after = float(body["retry_after_sec"])
            except (ValueError, TypeError):
                retry_after = None
        if retry_after is None and response is not None:
            raw = None
            try:
                raw = response.headers.get("Retry-After")
            except Exception:
                raw = None
            if raw is not None:
                try:
                    retry_after = float(raw)
                except (ValueError, TypeError):
                    retry_after = None
        return RateLimitedError(msg, retry_after_sec=retry_after, reason=reason, response=response)

    # --- HTTP 400/422: Malformed datum / invalid request ---
    if status_code in (400, 422):
        detail = body.get("detail") if isinstance(body.get("detail"), dict) else None
        effective = detail or body
        error_type = effective.get("type", "")
        msg = effective.get("message") or body.get("detail") or "Invalid request"
        field = effective.get("field")
        error_code = effective.get("error_code") or effective.get("code")
        debug_ref = effective.get("debug_ref")

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

    # Payload-loss outcomes are terminal even if a malformed response also
    # carries should_retry=true. In particular, resubmitting a completed
    # forward_backward request could apply its gradients twice.
    if error_code in (
        "operation_completed_result_unavailable",
        "operation_failed_result_unavailable",
    ):
        return OperationResultUnavailableError(
            error_msg,
            operation_completed=(error_code == "operation_completed_result_unavailable"),
            error_code=error_code,
            debug_ref=debug_ref,
        )

    # Retryable-by-design failures. A generic, code-agnostic mechanism: when
    # the server sets ``should_retry: true`` on a failed request it is telling
    # the client this failure is safe to recover from by resubmitting a fresh
    # request. We deliberately do NOT gate on specific error codes — any
    # operation may opt in to this contract by setting the flag. ``_post_and_poll``
    # catches the resulting exception and resubmits (bounded).
    if envelope.get("should_retry") is True:
        retry_after = envelope.get("retry_after_sec")
        try:
            retry_after = float(retry_after) if retry_after is not None else None
        except (TypeError, ValueError):
            retry_after = None
        return RequestRetryableError(
            error_msg,
            error_code=error_code,
            retry_after_sec=retry_after,
            debug_ref=debug_ref,
        )

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
    "RateLimitedError",
    "TrainingEngineError",
    "EngineDeadError",
    "OperationResultUnavailableError",
    "ContentionError",
    "RequestValidationError",
    "MalformedDatumError",
]
