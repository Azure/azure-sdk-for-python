# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Associate Rust request diagnostics with their public SDK operation."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from _thread import LockType
from collections.abc import Awaitable, Callable, Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps
import logging
import sys
from threading import Lock, get_ident
from time import perf_counter_ns
from typing import TYPE_CHECKING, Any, Literal, Optional, TypeVar

from typing_extensions import ParamSpec

from azure.core.settings import settings
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ._backend.constants import is_rust_backend
from ._backend.errors import BindingProtocolError

if TYPE_CHECKING:
    from opentelemetry.trace import Span, SpanContext

_LOGGER = logging.getLogger(__name__)
_P = ParamSpec("_P")
_T = TypeVar("_T")
_Outcome = Literal["success", "error", "cancelled"]
_REPORTING_FAILURES = 0
_REPORT_LOCK = Lock()


def _report(message: str, level: int = logging.WARNING) -> None:
    global _REPORTING_FAILURES  # pylint: disable=global-statement
    try:
        _LOGGER.log(level, message)
    except Exception:  # pylint: disable=broad-except
        with _REPORT_LOCK:
            _REPORTING_FAILURES += 1
        try:
            if sys.__stderr__ is not None:
                sys.__stderr__.write(f"Rust telemetry reporting failed: {message}\n")
        except Exception:  # pylint: disable=broad-except
            # The counter remains observable even when both reporting channels fail.
            pass


@dataclass(frozen=True)
class _Attempt:
    start_ns: int
    end_ns: Optional[int]
    driver_status_code: int
    execution_context: str


@dataclass(frozen=True)
class _Diagnostics:
    request_count: int
    attempts: tuple[_Attempt, ...]
    complete: bool = True


@dataclass(frozen=True)
class OperationCompletion:
    """Internal completion data, independent of any tracing provider."""

    operation: str
    outcome: _Outcome
    execution_duration_ns: int
    diagnostics: Optional[_Diagnostics]


@dataclass(frozen=True)
class CompletionHandler:
    """Internal recording registration; not a customer configuration surface."""

    record: Callable[[OperationCompletion], None]
    collect_attempts: bool = False


@dataclass
class _DiagnosticCollector:
    retained_limit: Optional[int] = None
    closed: bool = False
    diagnostics: Optional[_Diagnostics] = None
    contributions: int = 0
    received: int = 0
    _lock: LockType = field(default_factory=Lock, repr=False)

    def __post_init__(self) -> None:
        if self.retained_limit is not None:
            _integer(self.retained_limit)

    def reserve(self) -> Optional[_Contribution]:
        """Reserve one independent binding result; repeated delivery is rejected.

        :return: A single-use contribution, or None when collection is rejected.
        :rtype: _Contribution or None
        """
        with self._lock:
            allowed = not self.closed and (self.contributions == 0 or self.retained_limit is not None)
            if not self.closed:
                self.contributions += 1
            if allowed:
                return _Contribution(self)
        _report("Rust telemetry rejected a closed or unbounded additional contribution")
        return None

    def accept(self, contribution: _Contribution, diagnostics: Optional[_Diagnostics]) -> None:
        with self._lock:
            if self.closed or contribution.owner is not self or contribution.consumed:
                rejected = True
            else:
                rejected = False
                contribution.consumed = True
                if diagnostics is not None:
                    self.received += 1
                    previous = self.diagnostics
                    attempts = (previous.attempts if previous else ()) + diagnostics.attempts
                    if self.retained_limit is not None and len(attempts) > self.retained_limit:
                        attempts = tuple(sorted(attempts, key=lambda attempt: attempt.start_ns))
                        head = (self.retained_limit + 1) // 2
                        tail = self.retained_limit - head
                        attempts = attempts[:head] + (attempts[-tail:] if tail else ())
                    self.diagnostics = _Diagnostics(
                        (previous.request_count if previous else 0) + diagnostics.request_count, attempts
                    )
        if rejected:
            _report("Rust telemetry rejected a duplicate or late diagnostic contribution, or a different owner")

    def close(self) -> tuple[bool, Optional[_Diagnostics]]:
        with self._lock:
            if self.closed:
                return False, None
            self.closed = True
            diagnostics = self.diagnostics
            if diagnostics is not None and self.received != self.contributions:
                diagnostics = _Diagnostics(diagnostics.request_count, diagnostics.attempts, complete=False)
            self.diagnostics = None
            return True, diagnostics


@dataclass
class _Operation:
    operation: str
    backend: object
    caller: Optional[SpanContext]
    task: object
    thread: int
    binding_operation: str
    parent: Optional[Span] = None
    handlers: tuple[CompletionHandler, ...] = ()
    started_ns: int = field(default_factory=perf_counter_ns)
    collector: _DiagnosticCollector = field(default_factory=_DiagnosticCollector)

    @property
    def closed(self) -> bool:
        return self.collector.closed

    def begin_contribution(self) -> Optional[_Contribution]:
        """Reserve one independently completed binding result.

        :return: A single-use contribution, or None when collection is rejected.
        :rtype: _Contribution or None
        """
        return self.collector.reserve()

    def finish(self, outcome: _Outcome = "success") -> None:
        """Freeze completion once, before invoking independently isolated handlers.

        :param outcome: Public method outcome, including response hook failures.
        :type outcome: str
        """
        ended_ns = perf_counter_ns()
        first_completion, diagnostics = self.collector.close()
        if not first_completion:
            return
        completion = OperationCompletion(self.operation, outcome, max(0, ended_ns - self.started_ns), diagnostics)
        parent, handlers = self.parent, self.handlers
        self.parent = None
        self.handlers = ()
        if parent is not None:
            try:
                emit_attempts(parent, diagnostics)
            except Exception:  # pylint: disable=broad-except
                _report("Rust telemetry could not emit attempt spans; operation result is unchanged")
        for handler in handlers:
            try:
                handler.record(completion)
            except Exception:  # pylint: disable=broad-except
                _report("Rust telemetry completion handler failed; operation result is unchanged")


@dataclass
class _Contribution:
    owner: _DiagnosticCollector
    consumed: bool = False

    def _complete(self, payload: object) -> None:
        diagnostics = None
        if payload is not None:
            try:
                total, _, attempts = _decode_payload(payload)
                diagnostics = _Diagnostics(total, tuple(attempts))
            except Exception:  # pylint: disable=broad-except
                _report("Rust telemetry rejected an invalid diagnostics payload; operation result is unchanged")
        self.owner.accept(self, diagnostics)

    def response(self, result: object) -> tuple[Any, ...]:
        """Keep normal response conversion separate from optional diagnostics.

        :param result: Binding response with optional request diagnostics.
        :type result: object
        :return: The unchanged response tuple.
        :rtype: tuple
        """
        if isinstance(result, tuple) and result and isinstance(result[0], tuple):
            response = result[0]
            if len(result) == 2:
                self._complete(result[1])
            else:
                self._complete(None)
                _report("Rust attempt envelope has invalid detail; response is preserved")
            return response
        if isinstance(result, tuple) and len(result) in (4, 5):
            self._complete(None)
            _report("Rust attempt envelope is missing; response is preserved")
            return result
        raise BindingProtocolError("The binding returned an invalid attempt envelope")

    def error(self, error: BaseException) -> None:
        """Retain available diagnostics without replacing the original error.

        :param error: The original binding exception.
        :type error: BaseException
        """
        try:
            payload = getattr(error, "_cosmos_attempt_payload", None)
        except Exception:  # pylint: disable=broad-except
            payload = None
            _report("Rust telemetry could not read error diagnostics; operation error is unchanged")
        self._complete(payload)


_OPERATION: ContextVar[Optional[_Operation]] = ContextVar("cosmos_operation_telemetry", default=None)


def _current_task() -> object:
    try:
        return asyncio.current_task()
    except RuntimeError:
        return None


def _new_operation(
    owner: object, operation: str, kwargs: Mapping[str, Any], binding_operation: Optional[str] = None
) -> Optional[_Operation]:
    context = getattr(owner, "_item_context", None)
    handlers = getattr(context, "telemetry_handlers", ())
    options = kwargs.get("tracing_options", {})
    enabled = options.get("enabled") if isinstance(options, Mapping) else False
    tracing = enabled is not False and (enabled is not None or settings.tracing_enabled())
    if not tracing and not handlers:
        return None
    backend = getattr(context, "adapter", None)
    if backend is None or not is_rust_backend(backend):
        return None
    state = None
    if handlers:
        state = _Operation(
            operation, backend, None, _current_task(), get_ident(), binding_operation or operation, handlers=handlers
        )
    if not tracing:
        # Azure Core retains validation of its own tracing options.
        return state
    try:
        from opentelemetry import trace  # pylint: disable=import-outside-toplevel
    except ImportError:
        _report("OpenTelemetry is unavailable; Rust attempt recording is disabled", logging.DEBUG)
        return state
    try:
        caller = trace.get_current_span().get_span_context()
        if state is None:
            state = _Operation(operation, backend, caller, _current_task(), get_ident(), binding_operation or operation)
        else:
            state.caller = caller
        return state
    except Exception:  # pylint: disable=broad-except
        _report("Rust telemetry could not capture the caller span; attempt recording is skipped")
        return state


@contextmanager
def _operation_scope(
    owner: object, operation: str, kwargs: Mapping[str, Any], binding_operation: Optional[str] = None
) -> Iterator[None]:
    # Even a disabled call masks inherited state from an outer SDK operation.
    token = _OPERATION.set(_new_operation(owner, operation, kwargs, binding_operation))
    try:
        yield
    finally:
        _OPERATION.reset(token)


@contextmanager
def _record_operation() -> Iterator[None]:
    operation = _OPERATION.get()
    if operation is not None and operation.caller is not None:
        try:
            from opentelemetry import trace  # pylint: disable=import-outside-toplevel

            parent = trace.get_current_span()
            if parent.is_recording() and parent.get_span_context() != operation.caller:
                operation.parent = parent
        except Exception:  # pylint: disable=broad-except
            _report("Rust telemetry could not capture the operation span; attempt recording is skipped")
    if operation is not None:
        operation.started_ns = perf_counter_ns()
    outcome: _Outcome = "success"
    try:
        yield
    except BaseException as error:
        outcome = "cancelled" if isinstance(error, asyncio.CancelledError) else "error"
        raise
    finally:
        if operation is not None:
            operation.finish(outcome)


def trace_operation(*, binding_operation: str) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    """Reuse Azure Core's span while owning diagnostics until public completion.

    :keyword binding_operation: Explicit binding operation owned by this public method.
    :paramtype binding_operation: str
    :return: A decorator with operation-scoped diagnostic collection.
    :rtype: callable
    """

    def decorate(func: Callable[_P, _T]) -> Callable[_P, _T]:
        @wraps(func)
        def record(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            with _record_operation():
                return func(*args, **kwargs)

        traced = distributed_trace(record)

        @wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            with _operation_scope(args[0] if args else kwargs.get("self"), func.__name__, kwargs, binding_operation):
                return traced(*args, **kwargs)

        return wrapper

    return decorate


def trace_operation_async(
    *, binding_operation: str
) -> Callable[[Callable[_P, Awaitable[_T]]], Callable[_P, Awaitable[_T]]]:
    """Async execution with the same ownership and recording rules as sync.

    :keyword binding_operation: Explicit binding operation owned by this public method.
    :paramtype binding_operation: str
    :return: A decorator with operation-scoped diagnostic collection.
    :rtype: callable
    """

    def decorate(func: Callable[_P, Awaitable[_T]]) -> Callable[_P, Awaitable[_T]]:
        @wraps(func)
        async def record(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            with _record_operation():
                return await func(*args, **kwargs)

        traced = distributed_trace_async(record)

        @wraps(func)
        async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            with _operation_scope(args[0] if args else kwargs.get("self"), func.__name__, kwargs, binding_operation):
                return await traced(*args, **kwargs)

        return wrapper

    return decorate


def get_operation(backend: object, operation: str) -> Optional[_Operation]:
    """Return only the recording state owned by this execution.

    :param backend: Python backend executing the operation.
    :type backend: object
    :param operation: Prepared operation name.
    :type operation: str
    :return: Matching active state, or None when recording is not requested.
    :rtype: _Operation or None
    """
    state = _OPERATION.get()
    if state is None or state.closed:
        return None
    if state.parent is None and not any(handler.collect_attempts for handler in state.handlers):
        return None
    if (
        state.backend is not backend
        or state.binding_operation != operation
        or state.thread != get_ident()
        or state.task is not _current_task()
    ):
        return None
    return state


def _integer(value: object) -> int:
    if type(value) is not int or not 0 <= value <= (1 << 64) - 1:  # pylint: disable=unidiomatic-typecheck
        raise ValueError("Expected an unsigned 64-bit integer")
    return value


def _decode_payload(payload: object) -> tuple[int, int, list[_Attempt]]:
    if not isinstance(payload, dict):
        raise ValueError("Missing attempt schema version")
    if _integer(payload.get("schema_version")) != 1 or payload.get("error") is not None:
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
        if (end is not None and end < start) or status > 65535 or not isinstance(reason, str) or not reason:
            raise ValueError("Invalid attempt timing or execution context")
        attempts.append(_Attempt(start, end, status, reason))
    return total, retained, attempts


def emit_attempts(parent: Span, payload: Optional[_Diagnostics]) -> None:
    """Create sibling spans from the finalized, validated diagnostics.

    :param parent: Owned public operation span.
    :type parent: ~opentelemetry.trace.Span
    :param payload: Aggregated diagnostics, or None when unavailable.
    :type payload: _Diagnostics or None
    """
    if payload is None:
        _report("Rust telemetry has no request diagnostics for this result", logging.DEBUG)
        return

    try:
        from opentelemetry import trace  # pylint: disable=import-outside-toplevel

        if payload.complete:
            parent.set_attribute("cosmos.poc.request_count", payload.request_count)
            parent.set_attribute("cosmos.poc.retained_request_count", len(payload.attempts))
        else:
            _report("Rust telemetry has incomplete contributions; operation totals are unavailable")
        tracer = trace.get_tracer("azure.cosmos.rust")
        parent_context = trace.set_span_in_context(parent)
        for attempt in payload.attempts:
            if attempt.end_ns is None:
                _report("Rust telemetry skipped a retained attempt without a completion time")
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
        _report("Rust telemetry could not emit all attempt spans; operation result is unchanged")
