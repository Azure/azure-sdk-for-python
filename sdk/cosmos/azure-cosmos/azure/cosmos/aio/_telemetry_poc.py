# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Private, success-only Rust attempt tracing proof for async create_item."""

from __future__ import annotations

import asyncio
import logging
from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from opentelemetry.trace import Span, SpanContext
    from ._container import ContainerProxy
    from .._cosmos_responses import CosmosDict

_LOGGER = logging.getLogger(__name__)


@dataclass
class _Capture:
    caller: SpanContext
    backend: object
    task: object
    consumed: bool = False


_CAPTURE: ContextVar[Optional[_Capture]] = ContextVar("cosmos_attempt_poc", default=None)


async def create_item_with_attempt_tracing(
    container: ContainerProxy, body: dict[str, Any], **kwargs: Any
) -> CosmosDict:
    """Opt in for one Rust-backed async create; retain the public operation span.

    The customer app must configure OpenTelemetry and enable Azure Core tracing.
    This private helper neither installs an exporter nor enables tracing globally.
    """
    from opentelemetry import trace  # pylint: disable=import-outside-toplevel
    from ._backend.rust_backend import AsyncRustBackend  # pylint: disable=import-outside-toplevel

    backend = getattr(container._get_item_helper(), "_backend", None)  # pylint: disable=protected-access
    if not isinstance(backend, AsyncRustBackend):
        raise ValueError("Attempt tracing POC requires the async Rust backend")
    token = _CAPTURE.set(
        _Capture(trace.get_current_span().get_span_context(), backend, asyncio.current_task())
    )
    try:
        return await container.create_item(body, **kwargs)
    finally:
        _CAPTURE.reset(token)


def take_operation_parent(backend: object) -> Optional[Span]:
    """Consume the opt-in only in the originating task and selected backend."""
    capture = _CAPTURE.get()
    if capture is None or capture.consumed or capture.backend is not backend:
        return None
    if capture.task is not asyncio.current_task():
        return None
    capture.consumed = True
    from opentelemetry import trace  # pylint: disable=import-outside-toplevel

    try:
        parent = trace.get_current_span()
        if not parent.is_recording() or parent.get_span_context() == capture.caller:
            _LOGGER.debug("Rust attempt POC skipped: no new recording operation span")
            return None
    except Exception:  # pylint: disable=broad-except
        # Customer-supplied tracing code must not prevent the database call.
        _LOGGER.warning("Rust attempt POC could not capture the operation span; tracing this call is skipped")
        return None
    return parent


@dataclass(frozen=True)
class _Attempt:
    start_ns: int
    end_ns: Optional[int]
    driver_status_code: int
    execution_context: str


def _integer(value: object) -> int:
    if type(value) is not int or not 0 <= value <= (1 << 64) - 1:
        raise ValueError("Expected an unsigned 64-bit integer")
    return value


def _decode_payload(payload: object) -> tuple[int, int, list[_Attempt]]:
    if not isinstance(payload, dict) or type(payload.get("schema_version")) is not int:
        raise ValueError("Missing attempt schema version")
    if payload["schema_version"] != 1 or payload.get("error") is not None:
        raise ValueError("Unsupported schema or binding timing failure")
    total = _integer(payload["request_count"])
    retained = _integer(payload["retained_request_count"])
    rows = payload["attempts"]
    if not isinstance(rows, list) or retained != len(rows) or total < retained:
        raise ValueError("Inconsistent attempt counts")
    attempts = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid attempt record")
        start = _integer(row["start_ns"])
        end = None if row["end_ns"] is None else _integer(row["end_ns"])
        status = _integer(row["driver_status_code"])
        reason = row["execution_context"]
        if (
            (end is not None and end < start)
            or status > 65535
            or not isinstance(reason, str)
            or not reason
        ):
            raise ValueError("Invalid attempt timing or execution context")
        attempts.append(_Attempt(start, end, status, reason))
    return total, retained, attempts


def emit_attempts(parent: Span, payload: object) -> None:
    """Validate the whole payload before emitting backdated sibling spans."""
    if payload is None:
        _LOGGER.debug("Rust attempt POC has no attempt payload for this result")
        return
    try:
        total, retained, attempts = _decode_payload(payload)
    except (KeyError, TypeError, ValueError):
        # Do not log the payload: an incompatible binding may include private data.
        _LOGGER.warning("Rust attempt POC rejected an invalid diagnostics payload; write result is unchanged")
        return

    try:
        from opentelemetry import trace  # pylint: disable=import-outside-toplevel

        parent.set_attribute("cosmos.poc.request_count", total)
        parent.set_attribute("cosmos.poc.retained_request_count", retained)
        tracer = trace.get_tracer("azure.cosmos.rust_attempt_poc")
        parent_context = trace.set_span_in_context(parent)
        for attempt in attempts:
            if attempt.end_ns is None:
                _LOGGER.warning("Rust attempt POC skipped a retained attempt without a completion time")
                continue
            span = tracer.start_span(
                "cosmosdb.request",
                context=parent_context,
                kind=trace.SpanKind.CLIENT,
                start_time=attempt.start_ns,
                attributes={
                    "cosmos.poc.driver_status_code": attempt.driver_status_code,
                    "cosmos.poc.execution_context": attempt.execution_context,
                },
            )
            span.end(end_time=attempt.end_ns)
    except Exception:  # pylint: disable=broad-except
        # Only instrumentation is inside this boundary, never the database call.
        _LOGGER.warning("Rust attempt POC could not emit all attempt spans; write result is unchanged")
