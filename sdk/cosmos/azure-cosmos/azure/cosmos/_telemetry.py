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
from copy import deepcopy
from dataclasses import dataclass, field
from functools import wraps
import logging
import sys
from threading import Lock, get_ident
from time import perf_counter_ns
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, Optional, TypeVar

from typing_extensions import ParamSpec

from azure.core.settings import settings
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ._backend.constants import is_rust_backend
from ._backend.errors import BindingProtocolError
from ._backend.contracts import BackendResponse
from ._diagnostic_logging import DiagnosticLogging

if TYPE_CHECKING:
    from opentelemetry.trace import Span, SpanContext

_LOGGER = logging.getLogger(__name__)
_P = ParamSpec("_P")
_T = TypeVar("_T")
_Outcome = Literal["success", "error", "cancelled"]
_REPORTING_FAILURES = 0
_REPORT_LOCK = Lock()


@dataclass(frozen=True)
class BindingAlternatives:
    """Bounded sequences narrowed by each executed binding step, without phantom steps."""

    paths: tuple[tuple[str, ...], ...]

    def __post_init__(self) -> None:
        if not self.paths or any(not path for path in self.paths):
            raise ValueError("Binding alternatives require nonempty paths")
        if len(set(self.paths)) != len(self.paths):
            raise ValueError("Binding alternatives require distinct paths")


_BindingOperation = str | tuple[str, ...] | BindingAlternatives


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
class _Attempt:  # pylint: disable=too-many-instance-attributes
    start_ns: int
    end_ns: Optional[int]
    driver_status_code: int
    execution_context: str
    sub_status_code: Optional[int] = None
    failed: bool = False
    request_charge: float = 0.0
    region: Optional[str] = None
    server_address: Optional[str] = None
    activity_id: Optional[str] = None
    operation_name: Optional[str] = None


def _bounded(values: tuple[str, ...], limit: Optional[int]) -> tuple[str, ...]:
    if limit is None or len(values) <= limit:
        return values
    head = (limit + 1) // 2
    tail = limit - head
    return values[:head] + (values[-tail:] if tail else ())


@dataclass(frozen=True)
class _Summary:  # pylint: disable=too-many-instance-attributes
    """Operation-level driver facts, mirroring the Rust SDK's operation span."""

    status_code: Optional[int] = None
    sub_status_code: Optional[int] = None
    failed: bool = False
    request_charge: float = 0.0
    contacted_regions: tuple[str, ...] = ()
    machine_id: Optional[str] = None
    hedging_started: bool = False
    hedge_region: Optional[str] = None
    hedge_terminal_state: Optional[str] = None
    requested_regions: tuple[str, ...] = ()
    requested_regions_total: int = 0
    responded_regions: tuple[str, ...] = ()
    responded_regions_total: int = 0

    def merge(self, later: _Summary, limit: Optional[int] = None) -> _Summary:
        """Combine ordered contributions; the later step supplies the final status.

        :param later: The next contribution's summary.
        :type later: _Summary
        :param limit: Optional bound on region histories.
        :type limit: int or None
        :return: The combined summary.
        :rtype: _Summary
        """
        status = later if later.status_code is not None or later.failed else self
        hedge = later if later.hedge_terminal_state is not None else self
        return _Summary(
            status_code=status.status_code,
            sub_status_code=status.sub_status_code,
            failed=status.failed,
            request_charge=self.request_charge + later.request_charge,
            contacted_regions=tuple(dict.fromkeys(self.contacted_regions + later.contacted_regions)),
            machine_id=self.machine_id or later.machine_id,
            hedging_started=self.hedging_started or later.hedging_started,
            hedge_region=hedge.hedge_region,
            hedge_terminal_state=hedge.hedge_terminal_state,
            requested_regions=_bounded(self.requested_regions + later.requested_regions, limit),
            requested_regions_total=self.requested_regions_total + later.requested_regions_total,
            responded_regions=_bounded(self.responded_regions + later.responded_regions, limit),
            responded_regions_total=self.responded_regions_total + later.responded_regions_total,
        )


@dataclass(frozen=True)
class _Diagnostics:
    request_count: int
    attempts: tuple[_Attempt, ...]
    complete: bool
    incomplete_reasons: tuple[str, ...] = ()
    summary: Optional[_Summary] = None


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
    start: Optional[Callable[[], bool]] = None


@dataclass(frozen=True)
class RecordingOptions:
    """Snapshot recording configuration, never execution context or logger objects."""

    kwargs: Mapping[str, Any]

    @classmethod
    def snapshot(cls, kwargs: Mapping[str, Any]) -> RecordingOptions:
        return cls(
            MappingProxyType(
                {
                    key: (deepcopy(kwargs[key]) if key in ("tracing_options", "tracing_attributes") else kwargs[key])
                    for key in (
                        "tracing_options",
                        "tracing_attributes",
                        "logger",
                        "logging_enable",
                    )
                    if key in kwargs
                }
            )
        )

    @classmethod
    def take(cls, kwargs: dict[str, Any]) -> RecordingOptions:
        snapshot = cls.snapshot(kwargs)
        for key in snapshot.kwargs:
            kwargs.pop(key)
        return snapshot

    def attributes(self, defaults: Mapping[str, Any]) -> Mapping[str, Any]:
        selected = self.kwargs["tracing_attributes"] if "tracing_attributes" in self.kwargs else deepcopy(defaults)
        return {
            **selected,
            **self.kwargs.get("tracing_options", {}).get("attributes", {}),
        }


@dataclass
class _AttemptSpanRecorder:
    """Provider-specific activation and emission; the collector only sees callbacks."""

    caller: SpanContext
    attributes: Mapping[str, Any]
    parent: Optional[Span] = None
    namespace: Optional[str] = None
    collection: Optional[str] = None

    def start(self) -> bool:
        try:
            from opentelemetry import trace  # pylint: disable=import-outside-toplevel

            parent = trace.get_current_span()
            if parent.is_recording() and parent.get_span_context() != self.caller:
                self.parent = parent
                return True
        except Exception:  # pylint: disable=broad-except
            _report("Rust telemetry could not capture the operation span; attempt recording is skipped")
        return False

    def record(self, completion: OperationCompletion) -> None:
        parent, self.parent = self.parent, None
        if parent is not None:
            emit_attempts(
                parent,
                completion.diagnostics,
                self.attributes,
                operation=completion.operation,
                namespace=self.namespace,
                collection=self.collection,
            )
            summary = completion.diagnostics.summary if completion.diagnostics is not None else None
            if completion.outcome == "error" and summary is not None and summary.failed:
                _pin_error_type(parent, "_OTHER" if summary.status_code is None else str(summary.status_code))


@dataclass
class _DiagnosticCollector:
    retained_limit: Optional[int] = None
    contribution_limit: Optional[int] = None
    closed: bool = False
    diagnostics: Optional[_Diagnostics] = None
    contributions: int = 0
    received: int = 0
    incomplete_reasons: set[str] = field(default_factory=set)
    _lock: LockType = field(default_factory=Lock, repr=False)

    def __post_init__(self) -> None:
        if self.retained_limit is not None:
            _integer(self.retained_limit)
        if self.contribution_limit is not None:
            _integer(self.contribution_limit)

    def reserve(self) -> Optional[_Contribution]:
        """Reserve one independent binding result; repeated delivery is rejected.

        :return: A single-use contribution, or None when collection is rejected.
        :rtype: _Contribution or None
        """
        with self._lock:
            allowed = not self.closed and (
                self.contributions < self.contribution_limit
                if self.contribution_limit is not None
                else self.contributions == 0 or self.retained_limit is not None
            )
            if not self.closed:
                self.contributions += 1
            if allowed:
                return _Contribution(self)
        _report("Rust telemetry rejected a closed, excess, or unbounded additional contribution")
        return None

    def mark_incomplete(self, reason: str) -> None:
        with self._lock:
            if not self.closed:
                self.incomplete_reasons.add(reason)

    def accept(
        self,
        contribution: _Contribution,
        diagnostics: Optional[_Diagnostics],
        *,
        incomplete_reason: Optional[str] = None,
    ) -> None:
        with self._lock:
            if self.closed or contribution.owner is not self or contribution.consumed:
                rejected = True
            else:
                rejected = False
                contribution.consumed = True
                if incomplete_reason is not None:
                    self.incomplete_reasons.add(incomplete_reason)
                if diagnostics is not None:
                    self.received += 1
                    previous = self.diagnostics
                    attempts = (previous.attempts if previous else ()) + diagnostics.attempts
                    if self.retained_limit is not None and len(attempts) > self.retained_limit:
                        attempts = tuple(sorted(attempts, key=lambda attempt: attempt.start_ns))
                        head = (self.retained_limit + 1) // 2
                        tail = self.retained_limit - head
                        attempts = attempts[:head] + (attempts[-tail:] if tail else ())
                    if previous is not None and previous.summary is not None and diagnostics.summary is not None:
                        summary = previous.summary.merge(diagnostics.summary, self.retained_limit)
                    else:
                        summary = diagnostics.summary or (previous.summary if previous else None)
                    self.diagnostics = _Diagnostics(
                        (previous.request_count if previous else 0) + diagnostics.request_count,
                        attempts,
                        complete=diagnostics.complete and (previous is None or previous.complete),
                        incomplete_reasons=tuple(
                            sorted(
                                set(diagnostics.incomplete_reasons)
                                | (set(previous.incomplete_reasons) if previous else set())
                            )
                        ),
                        summary=summary,
                    )
        if rejected:
            _report("Rust telemetry rejected a duplicate or late diagnostic contribution, or a different owner")

    def close(self) -> tuple[bool, Optional[_Diagnostics]]:
        with self._lock:
            if self.closed:
                return False, None
            self.closed = True
            diagnostics = self.diagnostics
            if self.received != self.contributions:
                self.incomplete_reasons.add("missing_contribution")
            if diagnostics is not None and self.incomplete_reasons:
                diagnostics = _Diagnostics(
                    diagnostics.request_count,
                    diagnostics.attempts,
                    complete=False,
                    incomplete_reasons=tuple(sorted(set(diagnostics.incomplete_reasons) | self.incomplete_reasons)),
                    summary=diagnostics.summary,
                )
            self.diagnostics = None
            return True, diagnostics


@dataclass
class _Operation:  # pylint: disable=too-many-instance-attributes
    operation: str
    backend: object
    task: object
    thread: int
    binding_operation: _BindingOperation
    handlers: tuple[CompletionHandler, ...] = ()
    diagnostic_logging: DiagnosticLogging = field(default_factory=DiagnosticLogging)
    started_ns: int = field(default_factory=perf_counter_ns)
    collector: _DiagnosticCollector = field(default_factory=_DiagnosticCollector)
    delegated_tasks: set[object] = field(default_factory=set, repr=False)

    def __post_init__(self) -> None:
        if isinstance(self.binding_operation, BindingAlternatives):
            self.collector.contribution_limit = max(len(path) for path in self.binding_operation.paths)
        elif isinstance(self.binding_operation, tuple):
            # A composed call retains each step's native-bounded detail, at most once per step.
            self.collector.contribution_limit = len(self.binding_operation)

    @property
    def closed(self) -> bool:
        return self.collector.closed

    def owns_execution(self) -> bool:
        task = _current_task()
        return self.thread == get_ident() and (self.task is task or task in self.delegated_tasks)

    def begin_contribution(self) -> Optional[_Contribution]:
        """Reserve one independently completed binding result.

        :return: A single-use contribution, or None when collection is rejected.
        :rtype: _Contribution or None
        """
        return self.collector.reserve()

    def start(self) -> None:
        active = []
        for handler in self.handlers:
            try:
                if handler.start is None or handler.start():
                    active.append(handler)
            except Exception:  # pylint: disable=broad-except
                _report("Rust telemetry completion handler could not start; operation result is unchanged")
        self.handlers = tuple(active)
        self.started_ns = perf_counter_ns()

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
        handlers = self.handlers
        self.handlers = ()
        self.delegated_tasks.clear()
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
        incomplete_reason = None
        if payload is not None:
            try:
                total, _, attempts = _decode_payload(payload)
                complete = payload["complete"]
                reasons = payload["incomplete_reasons"]
                if (
                    not isinstance(complete, bool)
                    or not isinstance(reasons, list)
                    or any(not isinstance(reason, str) or not reason for reason in reasons)
                    or complete == bool(reasons)
                ):
                    raise ValueError("Invalid diagnostic completeness")
                diagnostics = _Diagnostics(
                    total,
                    tuple(attempts),
                    complete=complete,
                    incomplete_reasons=tuple(sorted(set(reasons))),
                    summary=_decode_summary(payload),
                )
            except Exception:  # pylint: disable=broad-except
                incomplete_reason = "invalid_diagnostics"
                _report("Rust telemetry rejected an invalid diagnostics payload; operation result is unchanged")
        else:
            incomplete_reason = "diagnostics_unavailable"
        self.owner.accept(self, diagnostics, incomplete_reason=incomplete_reason)

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


@dataclass
class _DelegatedCall:
    state: _Operation
    owner: object
    operation: str
    task: object
    consumed: bool = False


_DELEGATED_CALL: ContextVar[Optional[_DelegatedCall]] = ContextVar("cosmos_delegated_call", default=None)


@contextmanager
def delegate_operation(owner: object, operation: str) -> Iterator[None]:
    """Authorize one internal public-method call to complete with its outer operation.

    Ordinary nested public calls still own independent state. This single-use
    authorization is scoped to the specified owner, method and executing task.

    :param owner: The proxy making the internal call.
    :type owner: object
    :param operation: The public method invoked internally.
    :type operation: str
    :return: A scope for the authorized call.
    :rtype: Iterator[None]
    """
    state = _OPERATION.get()
    call = None
    if (
        state is not None
        and not state.closed
        and state.owns_execution()
        and isinstance(state.binding_operation, (tuple, BindingAlternatives))
        and state.backend is getattr(getattr(owner, "_item_context", None), "adapter", None)
    ):
        call = _DelegatedCall(state, owner, operation, _current_task())
    token = _DELEGATED_CALL.set(call)
    try:
        yield
    finally:
        _DELEGATED_CALL.reset(token)


def _consume_delegated_call(owner: object, operation: str) -> bool:
    call = _DELEGATED_CALL.get()
    if call is None or call.consumed or call.owner is not owner or call.operation != operation:
        return False
    if (
        call.task is not _current_task()
        or call.state is not _OPERATION.get()
        or call.state.closed
        or not call.state.owns_execution()
        or call.state.backend is not getattr(getattr(owner, "_item_context", None), "adapter", None)
    ):
        return False
    call.consumed = True
    return True


def _current_task() -> object:
    try:
        return asyncio.current_task()
    except RuntimeError:
        return None


def bind_operation_task(
    operation: Callable[[], Awaitable[_T]],
) -> Callable[[], Awaitable[_T]]:
    """Authorize one SDK-owned worker, captured before creating its task.

    Ordinary context inheritance does not authorize child tasks. Only this
    worker joins the current operation, until its execution unwinds. This also
    works when a task factory starts the worker eagerly.

    :param operation: Work that the SDK will execute in its deadline task.
    :type operation: callable
    :return: A single-use worker with scoped diagnostic ownership.
    :rtype: callable
    """
    state = _OPERATION.get()
    if state is None or state.closed or not state.owns_execution():
        return operation
    used = False

    async def run() -> _T:
        nonlocal used
        task = _current_task()
        authorized = (
            not used
            and task is not None
            and not state.closed
            and state.thread == get_ident()
            and _OPERATION.get() is state
        )
        used = True
        if authorized:
            state.delegated_tasks.add(task)
        try:
            return await operation()
        finally:
            if authorized:
                state.delegated_tasks.discard(task)

    return run


def _new_operation(
    owner: object,
    operation: str,
    kwargs: Mapping[str, Any],
    binding_operation: Optional[_BindingOperation] = None,
    args: tuple[Any, ...] = (),
) -> Optional[_Operation]:
    context = getattr(owner, "_item_context", None)
    handlers = getattr(context, "telemetry_handlers", ())
    logging_defaults = getattr(context, "diagnostic_logging", None) or DiagnosticLogging()
    diagnostic_logging = logging_defaults.for_operation(kwargs)
    options = kwargs.get("tracing_options", {})
    enabled = options.get("enabled") if isinstance(options, Mapping) else False
    tracing = enabled is not False and (enabled is not None or settings.tracing_enabled())
    if (
        not tracing
        and not handlers
        and diagnostic_logging.level is None
        and not isinstance(binding_operation, (tuple, BindingAlternatives))
    ):
        return None
    backend = getattr(context, "adapter", None)
    if backend is None or not is_rust_backend(backend):
        return None
    binding_operation = operation if binding_operation is None else binding_operation
    state = None
    if handlers or diagnostic_logging.level is not None or not tracing:
        state = _Operation(
            operation,
            backend,
            _current_task(),
            get_ident(),
            binding_operation,
            handlers=handlers,
            diagnostic_logging=diagnostic_logging,
        )
    if not tracing:
        # Azure Core retains validation of its own tracing options.
        return state
    try:
        from opentelemetry import trace  # pylint: disable=import-outside-toplevel
    except ImportError:
        _report(
            "OpenTelemetry is unavailable; Rust attempt recording is disabled",
            logging.DEBUG,
        )
        return state
    try:
        attributes = RecordingOptions.snapshot(kwargs).attributes(getattr(context, "tracing_attributes", {}))
    except Exception:  # pylint: disable=broad-except
        _report("Rust telemetry could not snapshot tracing attributes; attempt recording is skipped")
        return state
    try:
        recorder = _AttemptSpanRecorder(trace.get_current_span().get_span_context(), attributes)
        recorder.namespace, recorder.collection = _resource_names(owner, operation, args, kwargs)
        if state is None:
            state = _Operation(operation, backend, _current_task(), get_ident(), binding_operation)
        state.handlers += (CompletionHandler(recorder.record, collect_attempts=True, start=recorder.start),)
        return state
    except Exception:  # pylint: disable=broad-except
        _report("Rust telemetry could not capture the caller span; attempt recording is skipped")
        return state


@contextmanager
def _operation_scope(
    owner: object,
    operation: str,
    kwargs: Mapping[str, Any],
    binding_operation: Optional[_BindingOperation] = None,
    args: tuple[Any, ...] = (),
) -> Iterator[None]:
    # Even a disabled call masks inherited state from an outer SDK operation.
    token = _OPERATION.set(_new_operation(owner, operation, kwargs, binding_operation, args))
    try:
        yield
    finally:
        _OPERATION.reset(token)


@contextmanager
def _record_operation() -> Iterator[None]:
    operation = _OPERATION.get()
    if operation is not None:
        operation.start()
    outcome: _Outcome = "success"
    try:
        yield
    except BaseException as error:
        outcome = "cancelled" if isinstance(error, asyncio.CancelledError) else "error"
        raise
    finally:
        if operation is not None:
            operation.finish(outcome)


class _LocalOperationError(Exception):
    """A tracing-only error; the original exception is restored outside the SDK span."""

    def __init__(self, error: Exception) -> None:
        super().__init__(f"Local SDK operation failed ({type(error).__name__})")
        self.original = error


def trace_operation(
    *,
    binding_operation: _BindingOperation,
    operation_name: Optional[str] = None,
    name_of_span: Optional[str] = None,
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    """Reuse Azure Core's span through method or deferred-callback completion.

    :keyword binding_operation: One binding operation, or the ordered steps of a bounded
        composed call. A tuple allows a prefix of that sequence, not arbitrary repeated calls.
        BindingAlternatives narrows permitted paths with each actual binding call.
        An empty tuple records local execution without accepting binding contributions.
    :paramtype binding_operation: str or tuple[str, ...] or BindingAlternatives
    :keyword str operation_name: Completion identity for a deferred callback; defaults to the method name.
    :keyword str name_of_span: Explicit span name for deferred execution; defaults to the qualified method name.
    :return: A decorator with operation-scoped diagnostic collection.
    :rtype: callable
    """

    def decorate(func: Callable[_P, _T]) -> Callable[_P, _T]:
        @wraps(func)
        def record(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            try:
                with _record_operation():
                    return func(*args, **kwargs)
            except Exception as error:
                if binding_operation == ():
                    raise _LocalOperationError(error) from None
                raise

        traced = distributed_trace(name_of_span=name_of_span)(record)

        @wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            owner = args[0] if args else kwargs.get("self")
            if _consume_delegated_call(owner, func.__name__):
                return func(*args, **kwargs)
            with _operation_scope(owner, operation_name or func.__name__, kwargs, binding_operation, args[1:]):
                try:
                    return traced(*args, **kwargs)
                except _LocalOperationError as error:
                    if binding_operation != ():
                        raise
                    original = error.original
                raise original.with_traceback(original.__traceback__)

        return wrapper

    return decorate


def trace_operation_async(
    *,
    binding_operation: _BindingOperation,
    operation_name: Optional[str] = None,
    name_of_span: Optional[str] = None,
) -> Callable[[Callable[_P, Awaitable[_T]]], Callable[_P, Awaitable[_T]]]:
    """Async execution with the same ownership and recording rules as sync.

    :keyword binding_operation: One binding operation, or the ordered steps of a bounded
        composed call. A tuple allows a prefix of that sequence, not arbitrary repeated calls.
        BindingAlternatives narrows permitted paths with each actual binding call.
        An empty tuple records local execution without accepting binding contributions.
    :paramtype binding_operation: str or tuple[str, ...] or BindingAlternatives
    :keyword str operation_name: Completion identity for a deferred callback; defaults to the method name.
    :keyword str name_of_span: Explicit span name for deferred execution; defaults to the qualified method name.
    :return: A decorator with operation-scoped diagnostic collection.
    :rtype: callable
    """

    def decorate(func: Callable[_P, Awaitable[_T]]) -> Callable[_P, Awaitable[_T]]:
        @wraps(func)
        async def record(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            try:
                with _record_operation():
                    return await func(*args, **kwargs)
            except Exception as error:
                if binding_operation == ():
                    raise _LocalOperationError(error) from None
                raise

        traced = distributed_trace_async(name_of_span=name_of_span)(record)

        @wraps(func)
        async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            owner = args[0] if args else kwargs.get("self")
            if _consume_delegated_call(owner, func.__name__):
                return await func(*args, **kwargs)
            with _operation_scope(owner, operation_name or func.__name__, kwargs, binding_operation, args[1:]):
                try:
                    return await traced(*args, **kwargs)
                except _LocalOperationError as error:
                    if binding_operation != ():
                        raise
                    original = error.original
                raise original.with_traceback(original.__traceback__)

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
    if (
        state.backend is not backend
        or not state.owns_execution()
        or not any(handler.collect_attempts for handler in state.handlers)
    ):
        return None
    expected = state.binding_operation
    if isinstance(expected, BindingAlternatives):
        index = state.collector.contributions
        selected = tuple(path for path in expected.paths if index < len(path) and path[index] == operation)
        matched = bool(selected)
        if selected:
            state.binding_operation = selected[0] if len(selected) == 1 else BindingAlternatives(selected)
            state.collector.contribution_limit = max(len(path) for path in selected)
    elif isinstance(expected, tuple):
        index = state.collector.contributions
        matched = index < len(expected) and expected[index] == operation
    else:
        matched = expected == operation
    if not matched:
        state.collector.mark_incomplete("unexpected_binding_operation")
        _report("Rust telemetry encountered unexpected owned binding work; operation totals are unavailable")
        return None
    return state


def log_response_diagnostics(backend: object, operation: str, response: BackendResponse) -> None:
    """Log only a supplied summary belonging to the active native call or page."""
    state = _OPERATION.get()
    if state is None or state.closed or state.backend is not backend or not state.owns_execution():
        return
    try:
        state.diagnostic_logging.record(operation, response)
    except Exception:  # pylint: disable=broad-except
        _report("Rust diagnostic logging failed; operation result is unchanged")


def _integer(value: object) -> int:
    if type(value) is not int or not 0 <= value <= (1 << 64) - 1:  # pylint: disable=unidiomatic-typecheck
        raise ValueError("Expected an unsigned 64-bit integer")
    return value


def _optional_integer(value: object, maximum: int) -> Optional[int]:
    if value is None:
        return None
    if _integer(value) > maximum:
        raise ValueError("Integer is out of range")
    return value  # type: ignore[return-value]


def _charge(value: object) -> float:
    if type(value) not in (int, float) or not 0 <= value < float("inf"):  # pylint: disable=unidiomatic-typecheck
        raise ValueError("Invalid request charge")
    return float(value)  # type: ignore[arg-type]


def _optional_text(value: object) -> Optional[str]:
    if value is not None and (not isinstance(value, str) or not value):
        raise ValueError("Expected a nonempty string")
    return value


def _texts(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError("Expected a list of nonempty strings")
    return tuple(value)


def _flag(value: object) -> bool:
    if not isinstance(value, bool):
        raise ValueError("Expected a boolean")
    return value


def _decode_payload(payload: object) -> tuple[int, int, list[_Attempt]]:
    if not isinstance(payload, dict):
        raise ValueError("Missing attempt schema version")
    if _integer(payload.get("schema_version")) != 2 or payload.get("error") is not None:
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
        attempts.append(
            _Attempt(
                start,
                end,
                status,
                reason,
                sub_status_code=_optional_integer(row["sub_status_code"], 65535),
                failed=_flag(row["failed"]),
                request_charge=_charge(row["request_charge"]),
                region=_optional_text(row["region"]),
                server_address=_optional_text(row["server_address"]),
                activity_id=_optional_text(row["activity_id"]),
                operation_name=_optional_text(row["operation_name"]),
            )
        )
    return total, retained, attempts


def _decode_summary(payload: Mapping[str, Any]) -> _Summary:
    requested = _texts(payload["requested_regions"])
    responded = _texts(payload["responded_regions"])
    requested_total = _integer(payload["requested_regions_total"])
    responded_total = _integer(payload["responded_regions_total"])
    if requested_total < len(requested) or responded_total < len(responded):
        raise ValueError("Inconsistent region totals")
    return _Summary(
        status_code=_optional_integer(payload["status_code"], 65535),
        sub_status_code=_optional_integer(payload["sub_status_code"], 65535),
        failed=_flag(payload["failed"]),
        request_charge=_charge(payload["request_charge"]),
        contacted_regions=_texts(payload["contacted_regions"]),
        machine_id=_optional_text(payload["machine_id"]),
        hedging_started=_flag(payload["hedging_started"]),
        hedge_region=_optional_text(payload["hedge_region"]),
        hedge_terminal_state=_optional_text(payload["hedge_terminal_state"]),
        requested_regions=requested,
        requested_regions_total=requested_total,
        responded_regions=responded,
        responded_regions_total=responded_total,
    )


# Methods whose target resource is an argument rather than the owner: keyword name and level.
_RESOURCE_ARGUMENTS = {
    "create_database": ("id", "namespace"),
    "create_database_if_not_exists": ("id", "namespace"),
    "delete_database": ("database", "namespace"),
    "create_container": ("id", "collection"),
    "create_container_if_not_exists": ("id", "collection"),
    "replace_container": ("container", "collection"),
    "delete_container": ("container", "collection"),
}


def _resource_id(value: object) -> Optional[str]:
    if isinstance(value, str):
        resource: object = value
    elif isinstance(value, Mapping):
        resource = value.get("id")
    else:
        resource = getattr(value, "id", None)
    return resource if isinstance(resource, str) and resource else None


def _resource_names(
    owner: object,
    operation: Optional[str] = None,
    args: tuple[Any, ...] = (),
    kwargs: Optional[Mapping[str, Any]] = None,
) -> tuple[Optional[str], Optional[str]]:
    """Return the database and container ids that an operation targets.

    :param owner: The proxy, or a page configuration holding it as ``proxy``.
    :type owner: object
    :param operation: Public SDK method name.
    :type operation: str or None
    :param args: Positional arguments after ``self``.
    :type args: tuple
    :param kwargs: Keyword arguments of the call.
    :type kwargs: Mapping[str, Any] or None
    :return: Database id and container id, each None when not applicable.
    :rtype: tuple[str or None, str or None]
    """
    namespace = collection = None
    for candidate in (owner, getattr(owner, "proxy", None)):
        link = getattr(candidate, "container_link", None)
        if not isinstance(link, str):
            link = getattr(candidate, "database_link", None)
        if isinstance(link, str):
            parts = link.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "dbs" and parts[1]:
                namespace = parts[1]
                collection = parts[3] if len(parts) >= 4 and parts[2] == "colls" and parts[3] else None
                break
    target = _RESOURCE_ARGUMENTS.get(operation or "")
    if target is not None:
        keyword, level = target
        resource = _resource_id(args[0] if args else (kwargs or {}).get(keyword))
        if resource is not None:
            if level == "namespace":
                namespace = resource
            else:
                collection = resource
    return namespace, collection


_DB_SYSTEM = {"db.system.name": "azure.cosmosdb"}


def _set_summary(parent: Span, summary: _Summary, attempts: tuple[_Attempt, ...]) -> None:
    if summary.status_code is not None:
        parent.set_attribute("db.response.status_code", str(summary.status_code))
        if summary.sub_status_code is not None:
            parent.set_attribute("azure.cosmosdb.response.sub_status_code", summary.sub_status_code)
    parent.set_attribute("azure.cosmosdb.operation.request_charge", summary.request_charge)
    if summary.contacted_regions:
        parent.set_attribute("azure.cosmosdb.operation.contacted_regions", summary.contacted_regions)
    if summary.hedging_started:
        parent.set_attribute("azure.cosmosdb.operation.hedging_started", True)
        if summary.hedge_terminal_state is not None:
            if summary.hedge_region is not None:
                parent.set_attribute("azure.cosmosdb.operation.hedge_region", summary.hedge_region)
            parent.set_attribute("azure.cosmosdb.operation.hedge_terminal_state", summary.hedge_terminal_state)
        for name, regions, total in (
            ("requested_regions", summary.requested_regions, summary.requested_regions_total),
            ("responded_regions", summary.responded_regions, summary.responded_regions_total),
        ):
            if regions:
                parent.set_attribute(f"azure.cosmosdb.operation.{name}", regions)
                if total > len(regions):
                    parent.set_attribute(f"azure.cosmosdb.operation.{name}_total", total)
    server = next((attempt.server_address for attempt in reversed(attempts) if attempt.server_address), None)
    if server is not None:
        parent.set_attribute("server.address", server)
    if summary.machine_id is not None:
        parent.set_attribute("azure.cosmosdb.machine_id", summary.machine_id)


def _pin_error_type(span: Span, value: str) -> None:
    """Record the Rust SDK's status-based ``error.type`` on the operation span.

    Azure Core writes the exception class to ``error.type`` after this callback and
    before it ends the span; this span instance keeps the driver status instead.

    :param span: Owned public operation span.
    :type span: ~opentelemetry.trace.Span
    :param str value: The failing status code, or ``_OTHER`` when none was reported.
    """
    try:
        span.set_attribute("error.type", value)
        original = span.set_attribute

        def set_attribute(key: str, attribute: Any) -> None:
            if key != "error.type":
                original(key, attribute)

        span.set_attribute = set_attribute  # type: ignore[method-assign]
    except Exception:  # pylint: disable=broad-except
        _report("Rust telemetry could not record the operation error type; operation result is unchanged")


def _attempt_attributes(attempt: _Attempt, operation: Optional[str]) -> dict[str, Any]:
    status = str(attempt.driver_status_code)
    values: dict[str, Any] = {
        **_DB_SYSTEM,
        "db.response.status_code": status,
        "azure.cosmosdb.operation.request_charge": attempt.request_charge,
        "azure.cosmosdb.request.execution_context": attempt.execution_context,
    }
    name = attempt.operation_name or operation
    if name:
        values["db.operation.name"] = name
    if attempt.sub_status_code is not None:
        values["azure.cosmosdb.response.sub_status_code"] = attempt.sub_status_code
    if attempt.region is not None:
        values["azure.cosmosdb.operation.contacted_regions"] = (attempt.region,)
    if attempt.execution_context == "hedging":
        values["azure.cosmosdb.request.hedge"] = True
    if attempt.server_address is not None:
        values["server.address"] = attempt.server_address
    if attempt.activity_id is not None:
        values["azure.cosmosdb.request.activity_id"] = attempt.activity_id
    if attempt.failed:
        values["error.type"] = status
    return values


def emit_attempts(
    parent: Span,
    payload: Optional[_Diagnostics],
    attributes: Optional[Mapping[str, Any]] = None,
    *,
    operation: Optional[str] = None,
    namespace: Optional[str] = None,
    collection: Optional[str] = None,
) -> None:
    """Add Rust SDK attribute names to the operation span and create attempt spans.

    :param parent: Owned public operation span.
    :type parent: ~opentelemetry.trace.Span
    :param payload: Aggregated diagnostics, or None when unavailable.
    :type payload: _Diagnostics or None
    :param attributes: Resolved customer attributes; recorded driver facts take precedence.
    :type attributes: Mapping[str, Any] or None
    :keyword str operation: Public SDK method name, used for ``db.operation.name``.
    :keyword str namespace: Database id, used for ``db.namespace``.
    :keyword str collection: Container id, used for ``db.collection.name``.
    """
    try:
        for key, value in (
            *_DB_SYSTEM.items(),
            ("db.operation.name", operation),
            ("db.namespace", namespace),
            ("db.collection.name", collection),
        ):
            if value:
                parent.set_attribute(key, value)
    except Exception:  # pylint: disable=broad-except
        _report("Rust telemetry could not label the operation span; operation result is unchanged")
    if payload is None:
        _report("Rust telemetry has no request diagnostics for this result", logging.DEBUG)
        return

    try:
        from opentelemetry import trace  # pylint: disable=import-outside-toplevel

        if payload.complete:
            parent.set_attribute("azure.cosmosdb.operation.request_count", payload.request_count)
            parent.set_attribute("azure.cosmosdb.operation.retained_request_count", len(payload.attempts))
        parent.set_attribute("azure.cosmosdb.operation.diagnostics_complete", payload.complete)
        if not payload.complete:
            parent.set_attribute(
                "azure.cosmosdb.operation.diagnostics_incomplete_reasons", payload.incomplete_reasons
            )
        if payload.summary is not None:
            _set_summary(parent, payload.summary, payload.attempts)
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
                attributes={**(attributes or {}), **_attempt_attributes(attempt, operation)},
            )
            if attempt.failed:
                span.set_status(trace.Status(trace.StatusCode.ERROR, "request failed"))
            span.end(end_time=attempt.end_ns)
    except Exception:  # pylint: disable=broad-except
        # Only instrumentation is inside this boundary, never the database call.
        _report("Rust telemetry could not emit all attempt spans; operation result is unchanged")