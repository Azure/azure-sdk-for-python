# pylint: disable=line-too-long,useless-suppression,too-many-lines
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async convenience methods patched onto FineTuningSessionClient.

All async training operations (create_session, forward_backward, optim_step,
save_weights, save_weights_for_sampler, sample, close_session) are added
directly to the generated ``FineTuningSessionClient`` class via ``patch_sdk()``.

Concurrency:
  - Heartbeat uses an ``asyncio.Task`` per session.
  - Chunked ``forward_backward`` uses ``asyncio.gather``.
  - A configurable ``asyncio.Semaphore`` gates concurrent POSTs to prevent
    connection storms (default: 64).

Usage::

    from azure.ai.finetuningsessions.aio import FineTuningSessionClient

    async with FineTuningSessionClient(endpoint, credential) as client:
        session_id = await client.create_session(base_model="Llama-3.1-8B")
        fb = await client.forward_backward(session_id, batch, loss_fn="cross_entropy")
        opt = await client.optim_step(session_id, AdamParams(learning_rate=1e-4))
        await client.close_session(session_id)
"""
from __future__ import annotations

import asyncio
import contextvars as _contextvars
import json as _json
import logging as _logging
import random as _random
import time as _time
from typing import Awaitable, Callable, Any, Dict, List, NamedTuple, Optional, Union, cast

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import HttpResponseError as _HttpResponseError
from azure.core.exceptions import ServiceRequestError as _ServiceRequestError
from azure.core.exceptions import ServiceResponseError as _ServiceResponseError
from azure.core.rest import HttpRequest as _HttpRequest

from ._client import FineTuningSessionClient as _GeneratedClient
from .._client_options import _prepare_client_options
from .._exceptions import (
    _classify_http_error,
    _classify_poll_failure,
    RequestRetryableError as _RequestRetryableError,
)

from ..models import (
    AdamParams,
    CreateSessionRequest,
    Datum,
    ForwardBackwardInput,
    ForwardBackwardOperationResult,
    ForwardBackwardRequest,
    ForwardInput,
    ForwardRequest,
    FromCheckpoint,
    LoRAConfig,
    LossFn,
    LossFnConfig,
    ModelInput,
    ModelInputChunk,
    OperationResult,
    OptimStepRequest,
    SampleRequest,
    SamplingParams,
    SaveCheckpointRequest,
    SaveSamplerWeightsRequest,
    FoundryFeaturesOptInKeys,
)
from .._utils.model_base import SdkJSONEncoder as _SdkJSONEncoder, _deserialize as _deserialize_model
from .._patch import (
    _chunk_data,
    _combine_fwd_bwd_results,
    _normalize_loom_result,
    _parse_checkpoint_path,
    _base_headers,
    _log_http,
    _LOOM_SUBPATH_TO_OP_TYPE,
    _API_VERSION,
    _DEFAULT_OPERATION_TIMEOUT_SEC,
    _ErrorBudget,
    _RETRIEVE_POLL_MIN,
    _RETRIEVE_POLL_MAX,
    _maybe_log_poll_progress,
    _clear_poll_log_state,
    _MAX_REQUEST_RETRIES,
    _retryable_resubmit_wait,
    _MAX_CONCURRENT_SAMPLES,
    _SAMPLE_THROTTLE_TIMEOUT_SEC,
    _BoundedRetryState,
    _ProxyJwtRetryState,
    _creation_wait,
)


class _ClientBase(_GeneratedClient):
    """The generated async client with the tested preview authentication policies."""

    _heartbeat_tasks: dict[str, asyncio.Task]
    _heartbeat_shutdowns: dict[str, asyncio.Task]
    _post_semaphore: asyncio.Semaphore
    _sample_semaphore: asyncio.Semaphore
    _sampling_session_seq: dict[str, int]
    _session_resource_ids: dict[str, str]

    def __init__(
        self, endpoint: str, credential: Union[AsyncTokenCredential, AzureKeyCredential], **kwargs: Any
    ) -> None:
        options = dict(kwargs)
        allow_insecure_http = options.pop("allow_insecure_http", False)
        options = _prepare_client_options(
            endpoint,
            credential,
            options,
            allow_insecure_http=allow_insecure_http,
            asynchronous=True,
        )
        super().__init__(endpoint=endpoint, credential=cast(AsyncTokenCredential, credential), **options)
        cast(Any, self._config).allow_insecure_http = allow_insecure_http

    async def close(self) -> None:
        """Drain all heartbeat tasks before closing the HTTP pipeline."""
        _ensure_async_state(cast("FineTuningSessionClient", self))
        for session_id in tuple(self._heartbeat_tasks):
            await _stop_heartbeat(cast("FineTuningSessionClient", self), session_id)
        await super().close()

    async def __aexit__(self, *args: Any) -> None:
        """Close the client and its background heartbeats on context exit."""
        await self.close()


_PREVIEW = FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW
_logger = _logging.getLogger(__name__)


def _canonical_session_id(session_id: str) -> str:
    if session_id.startswith("session_"):
        return session_id
    return f"session_{session_id.removeprefix('model_')}"


def _resource_session_id(session_id: str) -> str:
    if session_id.startswith(("session_", "model_")):
        return session_id
    return f"model_{session_id}"


_POLL_LOG_DEDUP_SEC = 30.0

# Caller-supplied correlation label copied into background tasks at creation.
operation_label_var: _contextvars.ContextVar[str] = _contextvars.ContextVar("loom_operation_label", default="")


def set_operation_label(label: str) -> "_contextvars.Token[str]":
    """Set the operation timeline label for the current context."""
    return operation_label_var.set(label)


def reset_operation_label(token: "_contextvars.Token[str]") -> None:
    """Restore the operation timeline label to its previous value."""
    operation_label_var.reset(token)


def _label_suffix() -> str:
    label = operation_label_var.get()
    return f" label={label}" if label else ""


async def _to_thread_and_drain_on_cancel(
    function: Callable[..., Any],
    /,
    *args: Any,
    task_name: str,
    **kwargs: Any,
) -> Any:
    """Run work off-loop without orphaning its thread when the caller is cancelled."""
    worker = asyncio.create_task(
        asyncio.to_thread(function, *args, **kwargs),
        name=task_name,
    )
    try:
        return await asyncio.shield(worker)
    except asyncio.CancelledError:
        try:
            await worker
        except Exception:
            _logger.exception("[%s] worker failed while draining after cancellation", task_name)
        raise


async def _chunk_data_async(batch: List[Datum]) -> List[List[Datum]]:
    """Build chunks off-loop and drain work on cancellation."""
    return await _to_thread_and_drain_on_cancel(
        _chunk_data,
        batch,
        task_name="chunk_data",
    )


async def _completed_result_task(result: OperationResult, name: str) -> "asyncio.Task[OperationResult]":
    """Return the promised Task interface for an already-completed wave."""

    async def completed() -> OperationResult:
        return result

    task = asyncio.create_task(completed(), name=name)
    await task
    return task


#: Default maximum concurrent POST requests.
_DEFAULT_POST_CONCURRENCY = 64


# -- Internal state initializer -----------------------------------------------


def _ensure_async_state(self: "FineTuningSessionClient") -> None:
    """Lazily initialize async state on the client instance."""
    if not hasattr(self, "_heartbeat_tasks"):
        self._heartbeat_tasks = {}
    if not hasattr(self, "_heartbeat_shutdowns"):
        self._heartbeat_shutdowns = {}
    if not hasattr(self, "_post_semaphore"):
        self._post_semaphore = asyncio.Semaphore(_DEFAULT_POST_CONCURRENCY)
    if not hasattr(self, "_sampling_session_seq"):
        self._sampling_session_seq = {}
    if not hasattr(self, "_sample_semaphore"):
        # Lifecycle-scoped semaphore bounding concurrent sample() calls across
        # their full submit+poll lifecycle.
        self._sample_semaphore = asyncio.Semaphore(_MAX_CONCURRENT_SAMPLES)
    if not hasattr(self, "_session_resource_ids"):
        self._session_resource_ids = {}


def _client_resource_session_id(
    self: "FineTuningSessionClient",
    session_id: str,
) -> str:
    _ensure_async_state(self)
    canonical_session_id = _canonical_session_id(session_id)
    return self._session_resource_ids.get(
        canonical_session_id,
        _resource_session_id(session_id),
    )


def _client_resource_subpath(
    self: "FineTuningSessionClient",
    subpath: str,
) -> str:
    prefix = "/fine_tuning/sessions/"
    if not subpath.startswith(prefix):
        return subpath
    session_id, separator, suffix = subpath[len(prefix) :].partition("/")
    resource_session_id = _client_resource_session_id(self, session_id)
    return f"{prefix}{resource_session_id}{separator}{suffix}"


# -- Background heartbeat -----------------------------------------------------


def _start_heartbeat(
    self: "FineTuningSessionClient",
    session_id: str,
    interval_sec: float = 30.0,
) -> None:
    """Start an asyncio task that sends heartbeat every interval_sec."""
    _ensure_async_state(self)
    session_id = _canonical_session_id(session_id)
    resource_session_id = _client_resource_session_id(self, session_id)

    async def _heartbeat_loop() -> None:
        while True:
            await asyncio.sleep(interval_sec)
            try:
                hb_req = _HttpRequest(
                    "POST",
                    "{endpoint}" + f"/fine_tuning/sessions/{resource_session_id}/heartbeat",
                    headers=_base_headers(),
                    params={"api-version": _API_VERSION},
                )
                resp = await self.send_request(hb_req)
                if resp.status_code != 200:
                    _logger.warning(
                        "[heartbeat] status=%d for %s",
                        resp.status_code,
                        session_id,
                    )
            except asyncio.CancelledError:
                return
            except Exception as exc:
                _logger.warning(
                    "[heartbeat] failed for %s: %s",
                    session_id,
                    exc,
                )

    task = asyncio.create_task(_heartbeat_loop(), name=f"fts-heartbeat-{session_id}")
    self._heartbeat_tasks[session_id] = task
    _logger.info(
        "[heartbeat] started (interval=%.0fs, session=%s)",
        interval_sec,
        session_id,
    )


async def _stop_heartbeat(self: "FineTuningSessionClient", session_id: str) -> None:
    """Cancel once and drain heartbeat cleanup before lifecycle requests.

    Concurrent callers share a shielded shutdown task, so cancelling one waiter
    cannot interrupt transport cleanup or let another waiter send early.
    """
    _ensure_async_state(self)
    session_id = _canonical_session_id(session_id)
    shutdown = self._heartbeat_shutdowns.get(session_id)
    if shutdown is None:
        task = self._heartbeat_tasks.get(session_id)
        if task is None:
            return
        if not task.done():
            task.cancel()

        async def drain() -> None:
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                _logger.exception("[heartbeat] failed during shutdown for %s", session_id)
            finally:
                if self._heartbeat_tasks.get(session_id) is task:
                    self._heartbeat_tasks.pop(session_id, None)
                self._heartbeat_shutdowns.pop(session_id, None)

        shutdown = asyncio.create_task(drain(), name=f"fts-heartbeat-shutdown-{session_id}")
        if not shutdown.done():
            self._heartbeat_shutdowns[session_id] = shutdown
    await asyncio.shield(shutdown)


# -- Low-level helpers ---------------------------------------------------------


def _classify_and_raise(resp: Any, sc: int) -> None:
    """Raise a typed exception for an error response, if one applies.

    Reads the response body (tolerating a non-JSON body) and delegates to
    ``_classify_http_error``. Raises the typed exception when the status is
    specifically classifiable; otherwise returns so the caller can fall
    through to its own ``resp.raise_for_status()``.
    """
    try:
        resp_body = resp.json()
    except Exception:
        resp_body = None
    typed = _classify_http_error(sc, resp_body, response=resp)
    if typed is not None:
        raise typed


async def _post(
    self: "FineTuningSessionClient",
    subpath: str,
    body_model: Any,
    extra_params: Optional[dict] = None,
) -> tuple[str, str]:
    """POST to enqueue a job.  Returns ``(request_id, op_type)``.

    Gated by ``_post_semaphore`` to prevent connection storms.
    Retries on 408/429/5xx (and unclassified 409s) with exponential backoff.
    A 409 that classifies to a terminal typed error (e.g. engine_dead) is
    non-retryable and raised on the first response.
    """
    _ensure_async_state(self)
    subpath = _client_resource_subpath(self, subpath)
    body_json = _json.dumps(body_model, cls=_SdkJSONEncoder, exclude_readonly=True)
    post_params: dict = {"api-version": _API_VERSION}
    if extra_params:
        post_params.update(extra_params)
    op_type = _LOOM_SUBPATH_TO_OP_TYPE.get(subpath.rsplit("/", 1)[-1], "")
    timeline_session_id = subpath.split("/sessions/", 1)[1].split("/", 1)[0] if "/sessions/" in subpath else ""
    submit_queued = _time.monotonic()
    _logger.info(
        "[operation_timeline] submit_queued session_id=%s op=%s path=%s%s",
        timeline_session_id,
        op_type,
        subpath,
        _label_suffix(),
    )
    _log_http("request", "POST", subpath, body=_json.loads(body_json))

    max_retries = 2
    _BASE_TIMEOUT_SEC = 100  # per-request timeout; escalated on each retry
    _TIMEOUT_MULTIPLIER = 1.5
    # Non-retryable status codes: deterministic rejections that will
    # never succeed on retry. Surface a typed exception immediately.
    _NON_RETRYABLE = frozenset({400, 413, 422})

    async with self._post_semaphore:
        submit_started = _time.monotonic()
        _logger.info(
            "[operation_timeline] submit_started session_id=%s op=%s path=%s " "queue_wait_ms=%.1f%s",
            timeline_session_id,
            op_type,
            subpath,
            (submit_started - submit_queued) * 1000.0,
            _label_suffix(),
        )
        last_status: Optional[int] = None
        consecutive_same_status = 0

        for attempt in range(max_retries + 1):
            # Escalate per-request timeout on retries so later attempts
            # aren't doomed to the same cutoff when the server is slow.
            request_timeout = _BASE_TIMEOUT_SEC * (_TIMEOUT_MULTIPLIER**attempt)
            try:
                post_req = _HttpRequest(
                    "POST",
                    "{endpoint}" + subpath,
                    headers=_base_headers({"Content-Type": "application/json"}),
                    params=post_params,
                    content=body_json,
                )
                resp = await self.send_request(post_req, connection_timeout=request_timeout)
                sc = resp.status_code

                # --- Non-retryable: classify and raise immediately ---
                if sc in _NON_RETRYABLE:
                    _classify_and_raise(resp, sc)
                    resp.raise_for_status()

                # --- Terminal 409 (engine dead): non-retryable ---
                # A 409 that classifies to a typed terminal error (e.g.
                # engine_dead) can never succeed on retry, so raise it now
                # instead of consuming the retry budget with duplicate backend
                # calls. An unclassified 409 returns from _classify_and_raise
                # and falls through to the retry tracking below, preserving its
                # existing behavior.
                if sc == 409:
                    _classify_and_raise(resp, sc)

                # --- Track repeated same-status for pattern detection ---
                if sc in (408, 409, 429) or (500 <= sc < 600):
                    if sc == last_status:
                        consecutive_same_status += 1
                    else:
                        consecutive_same_status = 1
                        last_status = sc

                    # After 2 consecutive identical failures, it's likely
                    # persistent — classify and raise typed if possible.
                    if consecutive_same_status >= 2:
                        _classify_and_raise(resp, sc)

                    if attempt < max_retries:
                        # Honor Retry-After header from server (seconds).
                        retry_after = resp.headers.get("Retry-After")
                        if retry_after is not None:
                            try:
                                wait = float(retry_after)
                            except (ValueError, TypeError):
                                wait = min(0.5 * (2**attempt), 10.0)
                        else:
                            wait = min(0.5 * (2**attempt), 10.0)
                        # Add jitter to prevent thundering herd.
                        wait *= 1 - 0.25 * _random.random()
                        _logger.warning(
                            "POST %s returned %d, retry %d/%d in %.1fs",
                            subpath,
                            sc,
                            attempt + 1,
                            max_retries,
                            wait,
                        )
                        await asyncio.sleep(wait)
                        continue

                    # Exhausted retries — classify before raising generic error.
                    _classify_and_raise(resp, sc)

                _log_http(
                    "response",
                    "POST",
                    subpath,
                    status=sc,
                    body=resp.json() if sc < 400 else None,
                )
                resp.raise_for_status()
                data = resp.json()
                _logger.info(
                    "[operation_timeline] submit_completed session_id=%s request_id=%s " "op=%s elapsed_ms=%.1f%s",
                    data.get("session_id", timeline_session_id),
                    data["request_id"],
                    op_type,
                    (_time.monotonic() - submit_started) * 1000.0,
                    _label_suffix(),
                )
                return (
                    data["request_id"],
                    op_type,
                )

            except (_ServiceRequestError, _ServiceResponseError) as exc:
                if attempt < max_retries:
                    # Back off longer for network errors (timeout/connection
                    # failures). The actual request timeout is escalated via
                    # connection_timeout above.
                    wait = min(1.0 * (2**attempt), 10.0) * (1 - 0.25 * _random.random())
                    _logger.warning(
                        "POST %s %s(%s), retry %d/%d in %.1fs",
                        subpath,
                        type(exc).__name__,
                        exc,
                        attempt + 1,
                        max_retries,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue
                raise

        raise RuntimeError("Submission retry loop ended without a response")


async def _post_sample(
    self: "FineTuningSessionClient",
    subpath: str,
    body_model: Any,
    extra_params: Optional[dict] = None,
) -> tuple[str, str]:
    """Submit a ``sample()`` job, holding 429 backpressure in place.

    Behaves like ``_post`` for genuine transient faults — 408/5xx (and
    unclassified 409s) and
    ``ServiceRequestError``/``ServiceResponseError`` get the same bounded
    (``max_retries``) retry with escalating per-request timeout. A 409 that
    classifies to a terminal typed error (e.g. engine_dead) is non-retryable
    and raised on the first response. It also treats a
    ``429`` as healthy throttling rather than a fault: the submit is retried in
    place (honoring ``Retry-After`` + jitter, clamped to the remaining budget)
    until the ``_SAMPLE_THROTTLE_TIMEOUT_SEC`` wall-clock deadline, then
    classified as a typed ``RateLimitedError``.

    The caller (``sample()``) already holds the lifecycle-scoped
    ``_sample_semaphore``; ``_post_semaphore`` is taken only around each
    individual send — never across a throttle sleep or fault backoff — so a
    throttled/backing-off sample never head-of-line-blocks other POSTs.
    """
    _ensure_async_state(self)
    subpath = _client_resource_subpath(self, subpath)
    body_json = _json.dumps(body_model, cls=_SdkJSONEncoder, exclude_readonly=True)
    post_params: dict = {"api-version": _API_VERSION}
    if extra_params:
        post_params.update(extra_params)
    op_type = _LOOM_SUBPATH_TO_OP_TYPE.get(subpath.rsplit("/", 1)[-1], "")
    _log_http("request", "POST", subpath, body=_json.loads(body_json))

    max_retries = 2
    _BASE_TIMEOUT_SEC = 100  # per-request timeout; escalated on each fault retry
    _TIMEOUT_MULTIPLIER = 1.5
    # Non-retryable status codes: deterministic rejections that will never
    # succeed on retry. Surface a typed exception immediately.
    _NON_RETRYABLE = frozenset({400, 413, 422})

    fault_attempt = 0  # bounds genuine faults (408/409/5xx + network); NOT 429
    throttle_start = _time.monotonic()
    jwt_retry_state = _ProxyJwtRetryState()

    while True:
        # Escalate per-request timeout on fault retries so later attempts aren't
        # doomed to the same cutoff when the server is slow.
        request_timeout = _BASE_TIMEOUT_SEC * (_TIMEOUT_MULTIPLIER ** min(fault_attempt, max_retries))
        post_req = _HttpRequest(
            "POST",
            "{endpoint}" + subpath,
            headers=_base_headers({"Content-Type": "application/json"}),
            params=post_params,
            content=body_json,
        )
        try:
            # Hold _post_semaphore only around the send, never across a sleep.
            async with self._post_semaphore:
                resp = await self.send_request(post_req, connection_timeout=request_timeout)
        except (_ServiceRequestError, _ServiceResponseError) as exc:
            if fault_attempt < max_retries:
                # Back off (outside the semaphore) for network errors.
                wait = min(1.0 * (2**fault_attempt), 10.0) * (1 - 0.25 * _random.random())
                _logger.warning(
                    "POST %s %s(%s), retry %d/%d in %.1fs",
                    subpath,
                    type(exc).__name__,
                    exc,
                    fault_attempt + 1,
                    max_retries,
                    wait,
                )
                fault_attempt += 1
                await asyncio.sleep(wait)
                continue
            raise
        sc = resp.status_code
        retry_wait = jwt_retry_state.update_and_get_delay(resp, method="POST", path=subpath)
        if retry_wait is not None:
            await asyncio.sleep(retry_wait)
            continue

        # --- Non-retryable: classify and raise immediately ---
        if sc in _NON_RETRYABLE:
            _classify_and_raise(resp, sc)
            resp.raise_for_status()

        # --- Terminal 409 (engine dead): non-retryable ---
        # A 409 that classifies to a typed terminal error (e.g. engine_dead)
        # can never succeed on retry, so raise it now instead of spending the
        # fault budget on duplicate backend calls. An unclassified 409 returns
        # and falls through to the fault-retry branch below unchanged.
        if sc == 409:
            _classify_and_raise(resp, sc)

        # --- Sample throttle: 429 held in-place, wall-clock bounded ---
        # Healthy backpressure, not a fault: retry until the throttle deadline,
        # sleeping OUTSIDE _post_semaphore. Does NOT consume the fault budget.
        if sc == 429:
            elapsed = _time.monotonic() - throttle_start
            if elapsed < _SAMPLE_THROTTLE_TIMEOUT_SEC:
                retry_after = resp.headers.get("Retry-After")
                try:
                    wait = float(retry_after) if retry_after is not None else _RETRIEVE_POLL_MIN
                except (ValueError, TypeError):
                    wait = _RETRIEVE_POLL_MIN
                wait *= 1 - 0.25 * _random.random()  # jitter
                # Clamp to the remaining budget so a large Retry-After can never
                # push the wall-clock cap out; the next iteration then crosses the
                # deadline. Guaranteed > 0 (elapsed < cap here).
                wait = min(wait, _SAMPLE_THROTTLE_TIMEOUT_SEC - elapsed)
                _logger.warning(
                    "POST %s throttled (429), retry in %.1fs (%.0fs/%.0fs)",
                    subpath,
                    wait,
                    elapsed,
                    _SAMPLE_THROTTLE_TIMEOUT_SEC,
                )
                await asyncio.sleep(wait)
                continue
            _logger.warning(
                "POST %s throttled (429) for %.0fs >= cap %.0fs; giving up",
                subpath,
                elapsed,
                _SAMPLE_THROTTLE_TIMEOUT_SEC,
            )
            _classify_and_raise(resp, sc)
            resp.raise_for_status()

        # --- Faults: 408/409/5xx, bounded retry (sleep OUTSIDE the semaphore) ---
        if sc in (408, 409) or (500 <= sc < 600):
            if fault_attempt < max_retries:
                # Honor Retry-After header from server (seconds).
                retry_after = resp.headers.get("Retry-After")
                if retry_after is not None:
                    try:
                        wait = float(retry_after)
                    except (ValueError, TypeError):
                        wait = min(0.5 * (2**fault_attempt), 10.0)
                else:
                    wait = min(0.5 * (2**fault_attempt), 10.0)
                wait *= 1 - 0.25 * _random.random()  # jitter
                _logger.warning(
                    "POST %s returned %d, retry %d/%d in %.1fs",
                    subpath,
                    sc,
                    fault_attempt + 1,
                    max_retries,
                    wait,
                )
                fault_attempt += 1
                await asyncio.sleep(wait)
                continue

            # Exhausted retries — classify before raising generic error.
            _classify_and_raise(resp, sc)

        _log_http("response", "POST", subpath, status=sc, body=resp.json() if sc < 400 else None)
        resp.raise_for_status()
        data = resp.json()
        return data["request_id"], op_type


async def _poll(
    self: "FineTuningSessionClient",
    session_id: str,
    request_id: str,
    op_type: str,
    extra_result_fields: Optional[dict] = None,
    error_budget_sec: Optional[float] = None,
    operation_started_at: Optional[float] = None,
    poll_started_at: Optional[float] = None,
    poll_min_sec: Optional[float] = None,
    poll_max_sec: Optional[float] = None,
) -> OperationResult:
    """Short-poll the envelope endpoint until the request resolves.

    Adaptive backoff defaults to ``_RETRIEVE_POLL_MIN`` through
    ``_RETRIEVE_POLL_MAX``. Callers may override those bounds, including setting
    them equal for a fixed cadence. Retries 5xx and transient network errors.

    ``error_budget_sec`` is an ERROR budget, not a wall-clock budget (matching
    the sync ``_post_and_poll``): healthy pending progress is unbounded and
    CLEARS the budget, while a sustained streak of 5xx / 408 / 429 / transient
    network errors longer than the budget raises ``TimeoutError``. Pass ``None``
    to disable it (retry forever).
    """
    effective_poll_min = _RETRIEVE_POLL_MIN if poll_min_sec is None else poll_min_sec
    effective_poll_max = _RETRIEVE_POLL_MAX if poll_max_sec is None else poll_max_sec
    if effective_poll_min <= 0:
        raise ValueError("poll_min_sec must be greater than zero")
    if effective_poll_max < effective_poll_min:
        raise ValueError("poll_max_sec must be greater than or equal to poll_min_sec")

    resource_session_id = _client_resource_session_id(self, session_id)
    poll_path = f"/fine_tuning/sessions/{resource_session_id}/request/{request_id}"
    conn_backoff = 1.0
    poll_backoff = effective_poll_min
    error_budget = _ErrorBudget.for_polling(error_budget_sec, op_type=op_type, request_id=request_id)
    poll_start = poll_started_at if poll_started_at is not None else _time.monotonic()
    request_not_found_retry = _BoundedRetryState(
        limit_sec=120.0,
        base_delay_sec=1.0,
        max_delay_sec=10.0,
    )
    jwt_retry_state = _ProxyJwtRetryState()
    poll_attempts = 0

    while True:
        try:
            poll_attempts += 1
            poll_req = _HttpRequest(
                "GET",
                "{endpoint}" + f"/fine_tuning/sessions/{resource_session_id}/request/{request_id}",
                headers=_base_headers(),
                params={"api-version": _API_VERSION},
            )
            _log_http("request", "GET", poll_path)
            resp = await self.send_request(poll_req)
            retry_wait = jwt_retry_state.update_and_get_delay(resp, method="GET", path=poll_path)
            if retry_wait is not None:
                await asyncio.sleep(retry_wait)
                continue

            if resp.status_code == 200:
                envelope = resp.json()
                _log_http("response", "GET", poll_path, status=200, body=envelope)
                conn_backoff = 1.0

                status = envelope.get("status")
                if status == "pending":
                    elapsed = _time.monotonic() - poll_start
                    _maybe_log_poll_progress(envelope, session_id, request_id, op_type, elapsed)
                    error_budget.clear()
                    await asyncio.sleep(poll_backoff)
                    poll_backoff = min(poll_backoff * 2, effective_poll_max)
                    continue
                if status == "failed":
                    _clear_poll_log_state(session_id, request_id, op_type)
                    typed = _classify_poll_failure(envelope, session_id=session_id)
                    if typed is not None:
                        raise typed
                    raise RuntimeError(
                        f"{op_type} request {request_id} failed "
                        f"[{envelope.get('error_code') or envelope.get('code') or 'unknown'}]: "
                        f"{envelope.get('error')} "
                        f"(debug_ref={envelope.get('debug_ref') or 'n/a'})"
                    )
                if status != "completed":
                    _clear_poll_log_state(session_id, request_id, op_type)
                    raise RuntimeError(
                        f"Unexpected envelope status {status!r} for " f"{op_type} request {request_id}: {envelope}"
                    )

                # completed -- normalize and deserialize.
                _clear_poll_log_state(session_id, request_id, op_type)
                consumed_at = _time.monotonic()
                poll_elapsed_ms = (consumed_at - poll_start) * 1000.0
                operation_elapsed_ms = (
                    (consumed_at - operation_started_at) * 1000.0
                    if operation_started_at is not None
                    else poll_elapsed_ms
                )
                _logger.info(
                    "[operation_timeline] result_consumed session_id=%s request_id=%s "
                    "op=%s poll_attempts=%d elapsed_ms=%.1f poll_elapsed_ms=%.1f%s",
                    session_id,
                    request_id,
                    op_type,
                    poll_attempts,
                    operation_elapsed_ms,
                    poll_elapsed_ms,
                    _label_suffix(),
                )
                raw = envelope.get("result") or {}
                normalized = _normalize_loom_result(raw, op_type, request_id)
                if extra_result_fields:
                    for k, v in extra_result_fields.items():
                        if not normalized.get(k):
                            normalized[k] = v
                return _deserialize_model(OperationResult, normalized)

            if resp.status_code == 404:
                wait = request_not_found_retry.next_delay()
                if wait is not None:
                    log = _logger.warning if request_not_found_retry.attempts == 1 else _logger.debug
                    log(
                        "[poller] transient request-store 404 for %s/%s "
                        "(op=%s, %.1fs/%.1fs grace); retrying in %.1fs",
                        session_id,
                        request_id,
                        op_type,
                        request_not_found_retry.elapsed,
                        request_not_found_retry.limit_sec,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue

            # Retryable HTTP status.
            if 500 <= resp.status_code < 600 or resp.status_code in (408, 429):
                body: Optional[Any] = None
                try:
                    body = resp.json()
                except Exception:
                    body = None
                _log_http(
                    "response",
                    "GET",
                    poll_path,
                    status=resp.status_code,
                    body=body,
                )
                elapsed = _time.monotonic() - poll_start
                _logger.debug(
                    "[poller] retry on %s/%s after HTTP %d (%.0fs elapsed)",
                    session_id,
                    request_id,
                    resp.status_code,
                    elapsed,
                )
                error_budget.consume(f"HTTP {resp.status_code}")
                conn_backoff = 1.0
                # Honor Retry-After header if present.
                retry_after = resp.headers.get("Retry-After")
                if retry_after is not None:
                    try:
                        poll_wait = float(retry_after)
                    except (ValueError, TypeError):
                        poll_wait = _RETRIEVE_POLL_MIN
                else:
                    poll_wait = _RETRIEVE_POLL_MIN
                await asyncio.sleep(error_budget.clamp_delay(poll_wait))
                continue

            # Non-retryable HTTP error.
            _log_http(
                "response",
                "GET",
                poll_path,
                status=resp.status_code,
                body=None,
            )
            try:
                poll_body = resp.json()
            except Exception:
                poll_body = None
            typed = _classify_http_error(resp.status_code, poll_body, response=resp, session_id=session_id)
            if typed is not None:
                raise typed
            resp.raise_for_status()

        except (_ServiceRequestError, _ServiceResponseError) as exc:
            elapsed = _time.monotonic() - poll_start
            _logger.warning(
                "[poller] retry on %s/%s after %s(%s) (%.0fs elapsed), backoff %.1fs",
                session_id,
                request_id,
                type(exc).__name__,
                exc,
                elapsed,
                conn_backoff,
            )
            error_budget.consume(type(exc).__name__)
            await asyncio.sleep(error_budget.clamp_delay(conn_backoff))
            conn_backoff = min(conn_backoff * 2, 30.0)
            continue


async def _poll_with_resubmit(
    self: "FineTuningSessionClient",
    session_id: str,
    request_id: str,
    op_type: str,
    subpath: str,
    body_model: Any,
    extra_params: Optional[dict] = None,
    extra_result_fields: Optional[dict] = None,
    post_fn: Optional[Callable[..., Awaitable[tuple[str, str]]]] = None,
    operation_started_at: Optional[float] = None,
    poll_min_sec: Optional[float] = None,
    poll_max_sec: Optional[float] = None,
) -> OperationResult:
    """Poll an already-POSTed request, resubmitting on retryable failures.

    Shared by :func:`_post_and_poll` and :meth:`PendingRequests.poll_result`
    so every public surface (direct calls AND the pipelined ``*_post`` /
    ``*_async`` handles) honors the server's ``should_retry`` signal
    identically. On :class:`RequestRetryableError` (the server flagged the
    failure safe to retry — e.g. a drained pod, an orphan-sweep reclaim, or an
    upstream read timeout) we POST a **fresh request id** and poll again, up to
    ``_MAX_REQUEST_RETRIES`` times, honoring ``retry_after_sec`` with jitter.
    ``post_fn`` preserves specialized submit behavior, such as sample 429
    throttling, on every resubmit.

    Retry is driven purely by the flag; the SDK never resubmits an operation
    the server has not marked retryable, so ordering-sensitive training ops
    (which the server never flags) are unaffected.
    """
    attempt = 0
    poll_started_at = _time.monotonic()
    while True:
        try:
            poll_kwargs: dict[str, Any] = {
                "error_budget_sec": _DEFAULT_OPERATION_TIMEOUT_SEC,
                "operation_started_at": operation_started_at,
                "poll_started_at": poll_started_at,
            }
            if poll_min_sec is not None:
                poll_kwargs["poll_min_sec"] = poll_min_sec
            if poll_max_sec is not None:
                poll_kwargs["poll_max_sec"] = poll_max_sec
            return await _poll(
                self,
                session_id,
                request_id,
                op_type,
                extra_result_fields,
                **poll_kwargs,
            )
        except _RequestRetryableError as exc:
            if attempt >= _MAX_REQUEST_RETRIES:
                # Exhausted resubmits — surface the typed terminal error.
                raise
            attempt += 1
            wait = _retryable_resubmit_wait(exc.retry_after_sec)
            _logger.warning(
                "[resubmit] %s/%s failed retryably [%s]; resubmit %d/%d in %.1fs",
                session_id,
                request_id,
                exc.error_code or "unknown",
                attempt,
                _MAX_REQUEST_RETRIES,
                wait,
            )
            await asyncio.sleep(wait)
            submit = post_fn or _post
            request_id, op_type = await submit(self, subpath, body_model, extra_params)


async def _post_and_poll(
    self: "FineTuningSessionClient",
    session_id: str,
    subpath: str,
    body_model: Any,
    extra_params: Optional[dict] = None,
    extra_result_fields: Optional[dict] = None,
) -> OperationResult:
    """POST to enqueue a job, then poll until it completes.

    Retryable-by-design failures (``RequestRetryableError`` — the server set
    ``should_retry`` on a failed request, e.g. a drained pod, an orphan-sweep
    reclaim, or an upstream read timeout) are resubmitted with a **fresh
    request id**, up to ``_MAX_REQUEST_RETRIES`` times, honoring the server's
    ``retry_after_sec`` hint with jitter. Retry is driven purely by the
    server's ``should_retry`` signal — the SDK does not gate on operation type
    or error code — so the server only sets the flag on recoverable failures.
    """
    operation_started_at = _time.monotonic()
    request_id, op_type = await _post(self, subpath, body_model, extra_params)
    return await _poll_with_resubmit(
        self,
        session_id,
        request_id,
        op_type,
        subpath,
        body_model,
        extra_params,
        extra_result_fields,
        operation_started_at=operation_started_at,
    )


# -- Public methods patched onto FineTuningSessionClient -----------------------


async def create_session(
    self: "FineTuningSessionClient",
    *,
    base_model: str,
    lora_config: Optional[LoRAConfig] = None,
    type: str = "training",
    from_checkpoint: Optional[FromCheckpoint] = None,
    timeout_sec: float = 600.0,
    user_metadata: Optional[dict[str, Any]] = None,
    training_type: Optional[str] = None,
) -> str:
    """Create a fine-tuning session and wait until the model is loaded.

    :keyword base_model: Name of the base model to load.
    :paramtype base_model: str
    :keyword lora_config: Optional LoRA adapter config.
    :paramtype lora_config: ~azure.ai.finetuningsessions.models.LoRAConfig or None
    :keyword type: Session type string. Defaults to ``"training"``.
    :paramtype type: str
    :keyword from_checkpoint: Optional checkpoint to resume from.
    :paramtype from_checkpoint: ~azure.ai.finetuningsessions.models.FromCheckpoint or None
    :keyword timeout_sec: Maximum seconds to wait for model load.
    :paramtype timeout_sec: float
    :keyword user_metadata: Optional key/value metadata stored on the session
        record.
    :paramtype user_metadata: dict[str, ~typing.Any] or None
    :keyword training_type: Training SKU type: ``"GlobalStandard"`` (default),
        ``"DatazoneStandard"``, or ``"DeveloperTier"``. Global jobs can run on
        any worker; datazone jobs require a worker in the same datazone as the
        API's region; Developer Tier jobs use eligible development capacity.
    :paramtype training_type: str or None
    :return: The ``session_id`` string (e.g. ``"session_abc12345"``).
    :rtype: str
    """
    _ensure_async_state(self)

    body = _json.loads(
        _json.dumps(
            CreateSessionRequest(
                type=type,
                base_model=base_model,
                lora_config=lora_config,
                user_metadata=user_metadata,
                training_type=training_type,
            ),
            cls=_SdkJSONEncoder,
            exclude_readonly=True,
        )
    )
    if from_checkpoint is not None:
        body["from_checkpoint"] = _json.loads(_json.dumps(from_checkpoint, cls=_SdkJSONEncoder, exclude_readonly=True))
        body["from_checkpoint"]["source_session_id"] = _canonical_session_id(
            body["from_checkpoint"]["source_session_id"]
        )

    body_json = _json.dumps(body)
    post_req = _HttpRequest(
        "POST",
        "{endpoint}/fine_tuning/sessions",
        headers=_base_headers({"Content-Type": "application/json"}),
        params={"api-version": _API_VERSION},
        content=body_json,
    )
    _log_http("request", "POST", "/fine_tuning/sessions", body=_json.loads(body_json))
    post_resp = await self.send_request(post_req)
    _log_http(
        "response",
        "POST",
        "/fine_tuning/sessions",
        status=post_resp.status_code,
        body=post_resp.json() if post_resp.status_code < 400 else None,
    )
    if post_resp.status_code >= 400:
        try:
            resp_body = post_resp.json()
        except Exception:
            resp_body = None
        typed = _classify_http_error(post_resp.status_code, resp_body, response=post_resp)
        if typed is not None:
            raise typed
        post_resp.raise_for_status()
    data = post_resp.json()
    raw_session_id: str = data["session_id"]
    request_id: str = data["request_id"]
    _logger.info(
        "[create_session] POST response: raw_session_id=%s, request_id=%s",
        raw_session_id,
        request_id,
    )

    session_id = _canonical_session_id(raw_session_id)
    resource_session_id = _resource_session_id(raw_session_id)
    self._session_resource_ids[session_id] = resource_session_id
    _logger.info(
        "[create_session] session_id transformed: raw=%s -> session_id=%s, resource_session_id=%s",
        raw_session_id,
        session_id,
        resource_session_id,
    )

    # Poll until model load completes.
    deadline = _time.monotonic() + timeout_sec
    conn_backoff = 1.0
    poll_backoff = _RETRIEVE_POLL_MIN
    _create_poll_start = _time.monotonic()
    not_found_retry = _BoundedRetryState(limit_sec=120.0, base_delay_sec=1.0, max_delay_sec=10.0)
    while True:
        _creation_wait(deadline, 0, timeout_sec, raw_session_id)
        try:
            poll_req = _HttpRequest(
                "GET",
                "{endpoint}" + f"/fine_tuning/sessions/{resource_session_id}/request/{request_id}",
                headers=_base_headers(),
                params={"api-version": _API_VERSION},
            )
            poll_path = f"/fine_tuning/sessions/{resource_session_id}/request/{request_id}"
            _log_http("request", "GET", poll_path)
            poll_resp = await self.send_request(poll_req)
            envelope = poll_resp.json() if poll_resp.status_code == 200 else None
            _log_http(
                "response",
                "GET",
                poll_path,
                status=poll_resp.status_code,
                body=envelope,
            )

            if poll_resp.status_code == 200:
                if not isinstance(envelope, dict):
                    raise RuntimeError(f"Unexpected response envelope for create request {request_id}")
                env_status = envelope.get("status")
                if env_status == "completed":
                    _logger.info(
                        "[create_session] model load completed: session_id=%s request_id=%s", session_id, request_id
                    )
                    _clear_poll_log_state(session_id, request_id, "create_session")
                    break
                if env_status == "failed":
                    _clear_poll_log_state(session_id, request_id, "create_session")
                    typed = _classify_poll_failure(envelope, session_id=session_id)
                    if typed is not None:
                        raise typed
                    raise RuntimeError(
                        f"Model load failed for session_id={raw_session_id} "
                        f"[{envelope.get('error_code') or envelope.get('code') or 'unknown'}]: "
                        f"{envelope.get('error') or 'unknown error'} "
                        f"(debug_ref={envelope.get('debug_ref') or 'n/a'})"
                    )
                if env_status != "pending":
                    raise RuntimeError(f"Unexpected envelope status {env_status!r} for create request {request_id}")
                # pending -> adaptive backoff
                if _time.monotonic() > deadline:
                    raise RuntimeError(
                        f"Timed out after {timeout_sec}s waiting for " f"session_id={raw_session_id} to become ready"
                    )
                elapsed = _time.monotonic() - _create_poll_start
                _maybe_log_poll_progress(envelope, session_id, request_id, "create_session", elapsed)
                conn_backoff = 1.0
                await asyncio.sleep(_creation_wait(deadline, poll_backoff, timeout_sec, raw_session_id))
                poll_backoff = min(poll_backoff * 2, _RETRIEVE_POLL_MAX)
                continue

            if poll_resp.status_code == 404:
                wait = not_found_retry.next_delay()
                if wait is not None:
                    await asyncio.sleep(_creation_wait(deadline, wait, timeout_sec, raw_session_id))
                    continue

            # Retryable HTTP status codes.
            if 500 <= poll_resp.status_code < 600 or poll_resp.status_code in (408, 429):
                if _time.monotonic() > deadline:
                    raise RuntimeError(
                        f"Timed out after {timeout_sec}s waiting for " f"session_id={raw_session_id} to become ready"
                    )
                elapsed = _time.monotonic() - _create_poll_start
                _logger.debug(
                    "[poller] retry on %s/%s after HTTP %d (%.0fs elapsed)",
                    session_id,
                    request_id,
                    poll_resp.status_code,
                    elapsed,
                )
                conn_backoff = 1.0
                retry_after = poll_resp.headers.get("Retry-After")
                try:
                    wait = float(retry_after) if retry_after is not None else _RETRIEVE_POLL_MIN
                except (TypeError, ValueError):
                    wait = _RETRIEVE_POLL_MIN
                await asyncio.sleep(_creation_wait(deadline, wait, timeout_sec, raw_session_id))
                continue

            # Non-retryable error.
            try:
                poll_body = poll_resp.json()
            except Exception:
                poll_body = None
            typed = _classify_http_error(poll_resp.status_code, poll_body, response=poll_resp, session_id=session_id)
            if typed is not None:
                raise typed
            poll_resp.raise_for_status()

        except (_ServiceRequestError, _ServiceResponseError) as exc:
            if _time.monotonic() > deadline:
                raise RuntimeError(
                    f"Timed out after {timeout_sec}s waiting for " f"session_id={raw_session_id} to become ready"
                ) from exc
            elapsed = _time.monotonic() - _create_poll_start
            _logger.warning(
                "[poller] retry on %s/%s after %s(%s) (%.0fs elapsed), backoff %.1fs",
                session_id,
                request_id,
                exc.__class__.__name__,
                exc,
                elapsed,
                conn_backoff,
            )
            await asyncio.sleep(_creation_wait(deadline, conn_backoff, timeout_sec, raw_session_id))
            conn_backoff = min(conn_backoff * 2, 30.0)
            continue

    _start_heartbeat(self, session_id)
    return session_id


async def create_session_from_checkpoint(
    self: "FineTuningSessionClient",
    *,
    checkpoint_path: str,
    base_model: str,
    lora_config: Optional[LoRAConfig] = None,
    type: str = "training",
    timeout_sec: float = 600.0,
) -> str:
    """Create a session resumed from a previously saved training checkpoint.

    :keyword checkpoint_path: Format: ``"<source_session_id>/<checkpoint_name>"``
        or ``"loom://<source_session_id>/weights/<checkpoint_name>"``.
    :paramtype checkpoint_path: str
    :keyword base_model: Base model name.
    :paramtype base_model: str
    :keyword lora_config: Optional LoRA config override.
    :paramtype lora_config: ~azure.ai.finetuningsessions.models.LoRAConfig or None
    :keyword type: Session type. Defaults to ``"training"``.
    :paramtype type: str
    :keyword timeout_sec: Maximum seconds to wait for model load.
    :paramtype timeout_sec: float
    :return: The ``session_id`` string.
    :rtype: str
    """
    source_session_id, checkpoint_id = _parse_checkpoint_path(checkpoint_path)
    return await create_session(
        self,
        base_model=base_model,
        lora_config=lora_config,
        type=type,
        from_checkpoint=FromCheckpoint(
            source_session_id=source_session_id,
            checkpoint_id=checkpoint_id,
        ),
        timeout_sec=timeout_sec,
    )


# -- Training ------------------------------------------------------------------


async def forward_backward(
    self: "FineTuningSessionClient",
    session_id: str,
    batch: List[Datum],
    *,
    loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY,
    loss_fn_config: Optional[LossFnConfig] = None,
) -> OperationResult:
    """Submit a mini-batch for a forward + backward pass.

    Automatically chunks large batches and submits chunks in parallel
    using ``asyncio.gather``.

    :param session_id: The session ID returned by ``create_session``.
    :type session_id: str
    :param batch: List of Datum.
    :type batch: list[~azure.ai.finetuningsessions.models.Datum]
    :keyword loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
    :paramtype loss_fn: str or ~azure.ai.finetuningsessions.models.LossFn
    :keyword loss_fn_config: Optional per-loss hyper-parameters.
    :paramtype loss_fn_config: ~azure.ai.finetuningsessions.models.LossFnConfig or None
    :return: OperationResult.
    :rtype: ~azure.ai.finetuningsessions.models.OperationResult
    """
    chunks = await _chunk_data_async(batch)
    if len(chunks) <= 1:
        return await _post_and_poll(
            self,
            session_id,
            f"/fine_tuning/sessions/{session_id}/forward_backward",
            ForwardBackwardRequest(
                forward_backward_input=ForwardBackwardInput(
                    data=batch,
                    loss_fn=loss_fn,
                    loss_fn_config=loss_fn_config,
                )
            ),
        )

    _logger.info(
        "[forward_backward] batch of %d datums split into %d chunks: %s",
        len(batch),
        len(chunks),
        [len(c) for c in chunks],
    )

    async def _submit_chunk(i: int, chunk: List[Datum]) -> ForwardBackwardOperationResult:
        _logger.info(
            "[forward_backward] sending chunk %d/%d (%d datums)",
            i + 1,
            len(chunks),
            len(chunk),
        )
        result = await _post_and_poll(
            self,
            session_id,
            f"/fine_tuning/sessions/{session_id}/forward_backward",
            ForwardBackwardRequest(
                forward_backward_input=ForwardBackwardInput(
                    data=chunk,
                    loss_fn=loss_fn,
                    loss_fn_config=loss_fn_config,
                )
            ),
        )
        if isinstance(result, ForwardBackwardOperationResult):
            return result
        return ForwardBackwardOperationResult(
            total_loss=getattr(result, "total_loss", None),
            per_datum_logprobs=getattr(result, "per_datum_logprobs", None),
            metrics=getattr(result, "metrics", None),
        )

    # Fire all chunks in parallel.
    chunk_results = await asyncio.gather(*(_submit_chunk(i, chunk) for i, chunk in enumerate(chunks)))
    chunk_sizes = [len(c) for c in chunks]
    return _combine_fwd_bwd_results(list(chunk_results), chunk_sizes)


async def forward(
    self: "FineTuningSessionClient",
    session_id: str,
    batch: List[Datum],
    *,
    loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY,
    loss_fn_config: Optional[LossFnConfig] = None,
) -> OperationResult:
    """Submit a mini-batch for a forward-only pass (no gradients).

    Automatically chunks large batches and submits chunks in parallel
    using ``asyncio.gather``.

    :param session_id: The session ID returned by ``create_session``.
    :type session_id: str
    :param batch: List of Datum.
    :type batch: list[~azure.ai.finetuningsessions.models.Datum]
    :keyword loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
    :paramtype loss_fn: str or ~azure.ai.finetuningsessions.models.LossFn
    :keyword loss_fn_config: Optional per-loss hyper-parameters.
    :paramtype loss_fn_config: ~azure.ai.finetuningsessions.models.LossFnConfig or None
    :return: ForwardBackwardOperationResult with per-datum loss outputs.
        ``total_loss`` is None for forward-only operations.
    :rtype: ~azure.ai.finetuningsessions.models.OperationResult
    """
    chunks = await _chunk_data_async(batch)
    if len(chunks) <= 1:
        return await _post_and_poll(
            self,
            session_id,
            f"/fine_tuning/sessions/{session_id}/forward",
            ForwardRequest(
                forward_input=ForwardInput(
                    data=batch,
                    loss_fn=loss_fn,
                    loss_fn_config=loss_fn_config,
                )
            ),
        )

    _logger.info(
        "[forward] batch of %d datums split into %d chunks: %s",
        len(batch),
        len(chunks),
        [len(c) for c in chunks],
    )

    async def _submit_chunk(i: int, chunk: List[Datum]) -> ForwardBackwardOperationResult:
        _logger.info(
            "[forward] sending chunk %d/%d (%d datums)",
            i + 1,
            len(chunks),
            len(chunk),
        )
        result = await _post_and_poll(
            self,
            session_id,
            f"/fine_tuning/sessions/{session_id}/forward",
            ForwardRequest(
                forward_input=ForwardInput(
                    data=chunk,
                    loss_fn=loss_fn,
                    loss_fn_config=loss_fn_config,
                )
            ),
        )
        if isinstance(result, ForwardBackwardOperationResult):
            return result
        return ForwardBackwardOperationResult(
            total_loss=getattr(result, "total_loss", None),
            loss_fn_output_type=getattr(result, "loss_fn_output_type", None),
            loss_fn_outputs=getattr(result, "loss_fn_outputs", None),
            per_datum_logprobs=getattr(result, "per_datum_logprobs", None),
            metrics=getattr(result, "metrics", None),
        )

    # Fire all chunks in parallel.
    chunk_results = await asyncio.gather(*(_submit_chunk(i, chunk) for i, chunk in enumerate(chunks)))
    chunk_sizes = [len(c) for c in chunks]
    return _combine_fwd_bwd_results(list(chunk_results), chunk_sizes)


async def forward_post(
    self: "FineTuningSessionClient",
    session_id: str,
    batch: List[Datum],
    *,
    loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY,
    loss_fn_config: Optional[LossFnConfig] = None,
) -> "PendingRequests":
    """POST a forward-only pass without polling for completion.

    Automatically chunks large batches.  Each chunk's POST is awaited
    sequentially so the server assigns monotonically increasing UUID v7
    request IDs.  Returns a :class:`PendingRequests` handle whose
    ``poll_result()`` can be awaited later.

    :param session_id: The session ID.
    :type session_id: str
    :param batch: List of Datum.
    :type batch: list[~azure.ai.finetuningsessions.models.Datum]
    :keyword loss_fn: Loss function name.
    :paramtype loss_fn: str or ~azure.ai.finetuningsessions.models.LossFn
    :keyword loss_fn_config: Optional per-loss hyper-parameters.
    :paramtype loss_fn_config: ~azure.ai.finetuningsessions.models.LossFnConfig or None
    :return: PendingRequests handle.
    :rtype: ~azure.ai.finetuningsessions.aio._patch.PendingRequests
    """
    subpath = f"/fine_tuning/sessions/{session_id}/forward"
    chunks = await _chunk_data_async(batch)

    if len(chunks) > 1:
        _logger.info(
            "[forward_post] batch of %d datums split into %d chunks: %s",
            len(batch),
            len(chunks),
            [len(c) for c in chunks],
        )

    posted: List[_PostSpec] = []
    for chunk in chunks:
        body = ForwardRequest(
            forward_input=ForwardInput(
                data=chunk,
                loss_fn=loss_fn,
                loss_fn_config=loss_fn_config,
            )
        )
        operation_started_at = _time.monotonic()
        request_id, op_type = await _post(self, subpath, body)
        posted.append(
            _PostSpec(
                request_id,
                op_type,
                subpath,
                body,
                operation_started_at=operation_started_at,
            )
        )

    return PendingRequests(self, session_id, posted, chunks)


async def forward_async(
    self: "FineTuningSessionClient",
    session_id: str,
    batch: List[Datum],
    *,
    loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY,
    loss_fn_config: Optional[LossFnConfig] = None,
) -> "asyncio.Task[OperationResult]":
    """Submit a forward-only pass, return an asyncio Task for the result.

    Awaits all POSTs (with chunking) so that the server assigns UUID v7
    request IDs *before* this method returns.

    **Multi-chunk correctness:** When the batch is split into multiple HTTP
    chunks, this method awaits GPU completion of *all* chunks before
    returning, matching the forward_backward_async behavior.

    :param session_id: The session ID.
    :type session_id: str
    :param batch: List of Datum.
    :type batch: list[~azure.ai.finetuningsessions.models.Datum]
    :keyword loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
    :paramtype loss_fn: str or ~azure.ai.finetuningsessions.models.LossFn
    :keyword loss_fn_config: Optional per-loss hyper-parameters.
    :paramtype loss_fn_config: ~azure.ai.finetuningsessions.models.LossFnConfig or None
    :return: An asyncio.Task whose result is an OperationResult.
    :rtype: ~asyncio.Task[~azure.ai.finetuningsessions.models.OperationResult] or
        ~asyncio.Future[~azure.ai.finetuningsessions.models.OperationResult]
    """
    pending = await forward_post(self, session_id, batch, loss_fn=loss_fn, loss_fn_config=loss_fn_config)

    if len(pending._posted) > 1:
        _logger.info(
            "[forward_async] multi-chunk (%d): awaiting all chunk results before returning",
            len(pending._posted),
        )
        result = await pending.poll_result()
        return await _completed_result_task(result, "fwd_poll_completed")

    return asyncio.create_task(pending.poll_result(), name="fwd_poll")


async def optim_step(
    self: "FineTuningSessionClient",
    session_id: str,
    adam_params: AdamParams,
) -> OperationResult:
    """Apply accumulated gradients with Adam.

    :param session_id: The session ID.
    :type session_id: str
    :param adam_params: Optimizer hyper-parameters.
    :type adam_params: ~azure.ai.finetuningsessions.models.AdamParams
    :return: OperationResult.
    :rtype: ~azure.ai.finetuningsessions.models.OperationResult
    """
    return await _post_and_poll(
        self,
        session_id,
        f"/fine_tuning/sessions/{session_id}/optim_step",
        OptimStepRequest(adam_params=adam_params),
    )


# -- POST-only variants (for pipelined training) -------------------------------


class _PostSpec(NamedTuple):
    """Everything needed to poll a POSTed request AND resubmit it if the server
    marks the failure retryable (``should_retry``).

    ``subpath`` / ``body_model`` / ``extra_params`` capture the original POST so
    :func:`_poll_with_resubmit` can re-issue it with a fresh request id.
    """

    request_id: str
    op_type: str
    subpath: str
    body_model: Any
    extra_params: Optional[dict] = None
    operation_started_at: Optional[float] = None


class PendingRequests:
    """Opaque handle returned by ``*_post`` methods.

    Holds the request IDs assigned by the server so that
    ``poll_result`` can wait for completion later.  This lets callers
    guarantee POST ordering (UUID v7) while backgrounding the poll.
    """

    def __init__(
        self,
        client: "FineTuningSessionClient",
        session_id: str,
        posted: List[_PostSpec],
        chunks: Optional[List[List[Datum]]] = None,
        extra_result_fields: Optional[dict] = None,
    ):
        self._client = client
        self._session_id = session_id
        self._posted = posted  # list of _PostSpec
        self._chunks = chunks  # only set for chunked forward_backward
        self._extra_result_fields = extra_result_fields

    async def poll_result(
        self,
        *,
        poll_min_sec: Optional[float] = None,
        poll_max_sec: Optional[float] = None,
    ) -> OperationResult:
        """Poll until all POSTed requests complete and return the combined result.

        Uses :func:`_poll_with_resubmit` so retryable (``should_retry``) failures
        are resubmitted here too — the pipelined ``*_post`` / ``*_async`` public
        surfaces get the same recovery as the direct ``_post_and_poll`` path.
        ``poll_min_sec`` and ``poll_max_sec`` override the default pending-result
        backoff bounds.

        :keyword poll_min_sec: Minimum pending-result poll interval in seconds.
            ``None`` uses the default minimum interval.
        :paramtype poll_min_sec: float or None
        :keyword poll_max_sec: Maximum pending-result poll interval in seconds.
            ``None`` uses the default maximum interval.
        :paramtype poll_max_sec: float or None
        :return: The operation result, combined across chunks when needed.
        :rtype: ~azure.ai.finetuningsessions.models.OperationResult
        """
        poll_kwargs: dict[str, float] = {}
        if poll_min_sec is not None:
            poll_kwargs["poll_min_sec"] = poll_min_sec
        if poll_max_sec is not None:
            poll_kwargs["poll_max_sec"] = poll_max_sec
        chunk_results = await self._poll_chunk_results(**poll_kwargs)
        if len(chunk_results) == 1:
            return chunk_results[0]

        chunk_sizes = [len(c) for c in self._chunks] if self._chunks else [1] * len(self._posted)
        return _combine_fwd_bwd_results(cast(List[ForwardBackwardOperationResult], chunk_results), chunk_sizes)

    async def _poll_chunk_results(
        self,
        *,
        poll_min_sec: Optional[float] = None,
        poll_max_sec: Optional[float] = None,
    ) -> List[OperationResult]:
        """Poll all requests and return their uncombined results in POST order."""
        poll_kwargs: dict[str, float] = {}
        if poll_min_sec is not None:
            poll_kwargs["poll_min_sec"] = poll_min_sec
        if poll_max_sec is not None:
            poll_kwargs["poll_max_sec"] = poll_max_sec

        if len(self._posted) == 1:
            spec = self._posted[0]
            result = await _poll_with_resubmit(
                self._client,
                self._session_id,
                spec.request_id,
                spec.op_type,
                spec.subpath,
                spec.body_model,
                spec.extra_params,
                extra_result_fields=self._extra_result_fields,
                operation_started_at=spec.operation_started_at,
                poll_min_sec=poll_min_sec,
                poll_max_sec=poll_max_sec,
            )
            return [result]  # type: ignore[list-item]

        # Multiple chunks — poll in parallel, retaining POST order.
        async def _poll_one(spec: _PostSpec) -> OperationResult:
            result = await _poll_with_resubmit(
                self._client,
                self._session_id,
                spec.request_id,
                spec.op_type,
                spec.subpath,
                spec.body_model,
                spec.extra_params,
                extra_result_fields=self._extra_result_fields,
                operation_started_at=spec.operation_started_at,
                poll_min_sec=poll_min_sec,
                poll_max_sec=poll_max_sec,
            )
            if isinstance(result, ForwardBackwardOperationResult):
                return result
            return ForwardBackwardOperationResult(
                total_loss=getattr(result, "total_loss", None),
                loss_fn_output_type=getattr(result, "loss_fn_output_type", None),
                loss_fn_outputs=getattr(result, "loss_fn_outputs", None),
                per_datum_logprobs=getattr(result, "per_datum_logprobs", None),
                metrics=getattr(result, "metrics", None),
            )

        return list(await asyncio.gather(*(_poll_one(spec) for spec in self._posted)))


async def forward_backward_post(
    self: "FineTuningSessionClient",
    session_id: str,
    batch: List[Datum],
    *,
    loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY,
    loss_fn_config: Optional[LossFnConfig] = None,
) -> PendingRequests:
    """POST a forward+backward pass without polling for completion.

    Automatically chunks large batches.  Each chunk's POST is awaited
    sequentially so the server assigns monotonically increasing UUID v7
    request IDs.  Returns a :class:`PendingRequests` handle whose
    ``poll_result()`` can be awaited later.

    Use this instead of :meth:`forward_backward` when you need to
    guarantee that all forward_backward requests are registered on the
    server *before* a subsequent ``optim_step_post``.

    :param session_id: The session ID.
    :type session_id: str
    :param batch: List of Datum.
    :type batch: list[~azure.ai.finetuningsessions.models.Datum]
    :keyword loss_fn: Loss function name.
    :paramtype loss_fn: str or ~azure.ai.finetuningsessions.models.LossFn
    :keyword loss_fn_config: Optional per-loss hyper-parameters.
    :paramtype loss_fn_config: ~azure.ai.finetuningsessions.models.LossFnConfig or None
    :return: PendingRequests handle.
    :rtype: ~azure.ai.finetuningsessions.aio._patch.PendingRequests
    """
    chunks = await _chunk_data_async(batch)
    if len(chunks) > 1:
        _logger.info(
            "[forward_backward_post] batch of %d datums split into %d chunks: %s",
            len(batch),
            len(chunks),
            [len(c) for c in chunks],
        )

    return await _forward_backward_chunks_post(
        self,
        session_id,
        chunks,
        loss_fn=loss_fn,
        loss_fn_config=loss_fn_config,
    )


async def _forward_backward_chunks_post(
    self: "FineTuningSessionClient",
    session_id: str,
    chunks: List[List[Datum]],
    *,
    loss_fn: Union[str, LossFn],
    loss_fn_config: Optional[LossFnConfig],
) -> PendingRequests:
    """POST precomputed forward/backward chunks sequentially."""
    if not chunks or any(not chunk for chunk in chunks):
        raise ValueError("Training batch must not be empty")
    subpath = f"/fine_tuning/sessions/{session_id}/forward_backward"

    posted: List[_PostSpec] = []
    for chunk in chunks:
        body = ForwardBackwardRequest(
            forward_backward_input=ForwardBackwardInput(
                data=chunk,
                loss_fn=loss_fn,
                loss_fn_config=loss_fn_config,
            )
        )
        operation_started_at = _time.monotonic()
        request_id, op_type = await _post(self, subpath, body)
        posted.append(
            _PostSpec(
                request_id,
                op_type,
                subpath,
                body,
                operation_started_at=operation_started_at,
            )
        )

    return PendingRequests(self, session_id, posted, chunks)


async def forward_backward_async(
    self: "FineTuningSessionClient",
    session_id: str,
    batch: List[Datum],
    *,
    loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY,
    loss_fn_config: Optional[LossFnConfig] = None,
    poll_min_sec: Optional[float] = None,
    poll_max_sec: Optional[float] = None,
    max_chunks_per_wave: Optional[int] = None,
) -> "asyncio.Task[OperationResult]":
    """Submit a forward+backward pass, return an asyncio Task for the result.

    Awaits all POSTs (with chunking) so that the server assigns UUID v7
    request IDs *before* this method returns.

    **Multi-chunk correctness:** When the batch is split into multiple HTTP
    chunks, this method awaits GPU completion of *all* chunks before
    returning.  This ensures that a subsequent ``optim_step_async`` POST
    cannot reach the engine until every chunk's gradients have been
    accumulated.  The returned task resolves immediately with the combined
    result.

    For single-chunk batches (the common case), only the poll phase runs
    in the background — fully pipelined, no extra latency.

    When ``max_chunks_per_wave`` is set, at most that many HTTP chunks are
    registered at once. Each wave completes before the next is posted. This
    bounds the worker's pre-optimizer batch while preserving one logical
    forward/backward operation and one subsequent optimizer step.

    :param session_id: The session ID.
    :type session_id: str
    :param batch: List of Datum.
    :type batch: list[~azure.ai.finetuningsessions.models.Datum]
    :keyword loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
    :paramtype loss_fn: str or ~azure.ai.finetuningsessions.models.LossFn
    :keyword loss_fn_config: Optional per-loss hyper-parameters.
    :paramtype loss_fn_config: ~azure.ai.finetuningsessions.models.LossFnConfig or None
    :keyword poll_min_sec: Optional minimum pending-result poll interval.
    :paramtype poll_min_sec: float or None
    :keyword poll_max_sec: Optional maximum pending-result poll interval.
    :paramtype poll_max_sec: float or None
    :keyword max_chunks_per_wave: Maximum number of chunks to post before waiting
        for their completion. ``None`` preserves the existing all-at-once behavior.
    :paramtype max_chunks_per_wave: int or None
    :return: An asyncio.Task whose result is an OperationResult.
    :rtype: ~asyncio.Task[~azure.ai.finetuningsessions.models.OperationResult] or
        ~asyncio.Future[~azure.ai.finetuningsessions.models.OperationResult]
    """
    if max_chunks_per_wave is not None and max_chunks_per_wave <= 0:
        raise ValueError("max_chunks_per_wave must be positive when set")

    poll_kwargs: dict[str, float] = {}
    if poll_min_sec is not None:
        poll_kwargs["poll_min_sec"] = poll_min_sec
    if poll_max_sec is not None:
        poll_kwargs["poll_max_sec"] = poll_max_sec

    chunks = await _chunk_data_async(batch)
    if max_chunks_per_wave is not None and len(chunks) > max_chunks_per_wave:
        _logger.info(
            "[forward_backward_async] processing %d chunks in waves of at most %d",
            len(chunks),
            max_chunks_per_wave,
        )
        chunk_results: List[ForwardBackwardOperationResult] = []
        chunk_sizes: List[int] = []
        for start in range(0, len(chunks), max_chunks_per_wave):
            wave = chunks[start : start + max_chunks_per_wave]
            pending = await _forward_backward_chunks_post(
                self,
                session_id,
                wave,
                loss_fn=loss_fn,
                loss_fn_config=loss_fn_config,
            )
            chunk_results.extend(
                cast(List[ForwardBackwardOperationResult], await pending._poll_chunk_results(**poll_kwargs))
            )
            chunk_sizes.extend(len(chunk) for chunk in wave)

        wave_result = _combine_fwd_bwd_results(chunk_results, chunk_sizes)
        return await _completed_result_task(wave_result, "fwd_bwd_wave_completed")

    pending = await _forward_backward_chunks_post(
        self,
        session_id,
        chunks,
        loss_fn=loss_fn,
        loss_fn_config=loss_fn_config,
    )

    if len(pending._posted) > 1:
        # Multiple chunks: await GPU completion of all chunks NOW so that
        # the caller can safely post optim_step after this returns.
        #
        # Why: the engine polls the DB on a 0.5-2s cadence.  If we fire
        # chunk1-POST, chunk2-POST, optim-POST in ~600ms, the engine can
        # poll between chunk1 and chunk2, see chunk1 with no barrier, and
        # process chunk1 + optim_step before chunk2 lands — applying
        # gradients from only half the batch.
        #
        # Waiting for GPU completion of all chunks before posting
        # optim_step eliminates the race at the cost of one extra engine
        # poll cycle (~0.5-2s) of latency.
        _logger.info(
            "[forward_backward_async] multi-chunk (%d): awaiting all chunk results before returning",
            len(pending._posted),
        )
        result = await pending.poll_result(**poll_kwargs)
        return await _completed_result_task(result, "fwd_bwd_poll_completed")

    return asyncio.create_task(
        pending.poll_result(**poll_kwargs),
        name="fwd_bwd_poll",
    )


async def optim_step_post(
    self: "FineTuningSessionClient",
    session_id: str,
    adam_params: AdamParams,
) -> PendingRequests:
    """POST an optim_step without polling for completion.

    Returns a :class:`PendingRequests` handle whose ``poll_result()``
    can be awaited later.

    :param session_id: The session ID.
    :type session_id: str
    :param adam_params: Optimizer hyper-parameters.
    :type adam_params: ~azure.ai.finetuningsessions.models.AdamParams
    :return: PendingRequests handle.
    :rtype: ~azure.ai.finetuningsessions.aio._patch.PendingRequests
    """
    subpath = f"/fine_tuning/sessions/{session_id}/optim_step"
    body = OptimStepRequest(adam_params=adam_params)
    operation_started_at = _time.monotonic()
    request_id, op_type = await _post(self, subpath, body)
    return PendingRequests(
        self,
        session_id,
        [
            _PostSpec(
                request_id,
                op_type,
                subpath,
                body,
                operation_started_at=operation_started_at,
            )
        ],
    )


async def optim_step_async(
    self: "FineTuningSessionClient",
    session_id: str,
    adam_params: AdamParams,
    *,
    poll_min_sec: Optional[float] = None,
    poll_max_sec: Optional[float] = None,
) -> "asyncio.Task[OperationResult]":
    """Submit an optim_step, return an asyncio Task for the result.

    Awaits the POST so the server assigns a UUID v7 *after* all preceding
    forward_backward_async calls.  Only the poll runs in the background.

    :param session_id: The session ID.
    :type session_id: str
    :param adam_params: Optimizer hyper-parameters.
    :type adam_params: ~azure.ai.finetuningsessions.models.AdamParams
    :keyword poll_min_sec: Optional minimum pending-result poll interval.
    :paramtype poll_min_sec: float or None
    :keyword poll_max_sec: Optional maximum pending-result poll interval.
    :paramtype poll_max_sec: float or None
    :return: An asyncio.Task whose result is an OperationResult.
    :rtype: ~asyncio.Task[~azure.ai.finetuningsessions.models.OperationResult]
    """
    pending = await optim_step_post(self, session_id, adam_params)
    poll_kwargs: dict[str, float] = {}
    if poll_min_sec is not None:
        poll_kwargs["poll_min_sec"] = poll_min_sec
    if poll_max_sec is not None:
        poll_kwargs["poll_max_sec"] = poll_max_sec
    return asyncio.create_task(
        pending.poll_result(**poll_kwargs),
        name="optim_poll",
    )


# -- Checkpoints ---------------------------------------------------------------


async def save_weights(
    self: "FineTuningSessionClient",
    session_id: str,
    path: str,
) -> OperationResult:
    """Save a training checkpoint (LoRA weights + optimizer state).

    :param session_id: The session ID.
    :type session_id: str
    :param path: Checkpoint name/path.
    :type path: str
    :return: OperationResult.
    :rtype: ~azure.ai.finetuningsessions.models.OperationResult
    """
    return await _post_and_poll(
        self,
        session_id,
        f"/fine_tuning/sessions/{session_id}/checkpoint",
        SaveCheckpointRequest(path=path),
        extra_result_fields={"checkpoint_id": path},
    )


async def save_weights_post(
    self: "FineTuningSessionClient",
    session_id: str,
    path: str,
    *,
    step_number: Optional[int] = None,
    metrics: Optional[Dict[str, Any]] = None,
) -> "PendingRequests":
    """POST a save-weights request without polling for completion.

    :param session_id: The session ID.
    :type session_id: str
    :param path: Checkpoint name/path.
    :type path: str
    :keyword step_number: Training step number for this checkpoint.
    :paramtype step_number: int or None
    :keyword metrics: Evaluation metrics at checkpoint time.
    :paramtype metrics: dict[str, ~typing.Any] or None
    :return: PendingRequests handle.
    :rtype: ~azure.ai.finetuningsessions.aio._patch.PendingRequests
    """
    subpath = f"/fine_tuning/sessions/{session_id}/checkpoint"
    body = SaveCheckpointRequest(path=path, step_number=step_number, metrics=metrics)
    operation_started_at = _time.monotonic()
    request_id, op_type = await _post(self, subpath, body)
    return PendingRequests(
        self,
        session_id,
        [
            _PostSpec(
                request_id,
                op_type,
                subpath,
                body,
                operation_started_at=operation_started_at,
            )
        ],
        extra_result_fields={"checkpoint_id": path},
    )


async def save_weights_async(
    self: "FineTuningSessionClient",
    session_id: str,
    path: str,
    *,
    step_number: Optional[int] = None,
    metrics: Optional[Dict[str, Any]] = None,
) -> "asyncio.Task[OperationResult]":
    """Submit a save-weights request, return an asyncio Task for the result.

    Awaits the POST so the server assigns a UUID v7 *after* all preceding
    requests.  Only the poll runs in the background.

    :param session_id: The session ID.
    :type session_id: str
    :param path: Checkpoint name/path.
    :type path: str
    :keyword step_number: Training step number for this checkpoint.
    :paramtype step_number: int or None
    :keyword metrics: Evaluation metrics at checkpoint time.
    :paramtype metrics: dict[str, ~typing.Any] or None
    :return: An asyncio.Task whose result is an OperationResult.
    :rtype: ~asyncio.Task[~azure.ai.finetuningsessions.models.OperationResult]
    """
    pending = await save_weights_post(self, session_id, path, step_number=step_number, metrics=metrics)
    return asyncio.create_task(pending.poll_result(), name=f"save_{path}")


async def _save_weights_for_sampler_post(
    self: "FineTuningSessionClient",
    session_id: str,
    *,
    sampling_session_seq_id: Optional[int] = None,
    path: Optional[str] = None,
) -> "PendingRequests":
    """Internal: POST a save-weights-for-sampler request without polling."""
    subpath = f"/fine_tuning/sessions/{session_id}/checkpoint_sample"
    body = SaveSamplerWeightsRequest(
        seq_id=0,
        sampling_session_seq_id=sampling_session_seq_id,
        path=path,
    )
    operation_started_at = _time.monotonic()
    request_id, op_type = await _post(self, subpath, body)
    return PendingRequests(
        self,
        session_id,
        [
            _PostSpec(
                request_id,
                op_type,
                subpath,
                body,
                operation_started_at=operation_started_at,
            )
        ],
        extra_result_fields={"checkpoint_id": path or ""},
    )


async def save_weights_for_sampler_async(
    self: "FineTuningSessionClient",
    session_id: str,
    name: str,
) -> "asyncio.Task[OperationResult]":
    """Save sampler weights and persist them to blob storage.

    The engine persists the checkpoint because ``sampling_session_seq_id``
    is not set.

    :param session_id: The session ID.
    :type session_id: str
    :param name: Checkpoint name/identifier.
    :type name: str
    :return: An asyncio.Task whose result is an OperationResult with
        ``checkpoint_id`` set to *name*.
    :rtype: ~asyncio.Task[~azure.ai.finetuningsessions.models.OperationResult]
    """
    _ensure_async_state(self)
    pending = await _save_weights_for_sampler_post(
        self,
        session_id,
        path=name,
    )
    return asyncio.create_task(pending.poll_result(), name=f"sampler_{name}")


async def save_weights_and_get_sampling_client_async(
    self: "FineTuningSessionClient",
    session_id: str,
    name: str,
) -> "asyncio.Task[OperationResult]":
    """Sync current LoRA weights to the sampler (ephemeral — not persisted).

    Used every training step to push weights for rollout sampling.
    The engine skips blob persistence because ``sampling_session_seq_id``
    is set. The SDK maintains an internal per-session counter — the user
    never sees it.

    :param session_id: The session ID.
    :type session_id: str
    :param name: Checkpoint name/identifier (e.g. ``"step5"``).
    :type name: str
    :return: An asyncio.Task whose result is an OperationResult with
        ``checkpoint_id`` set to *name*.
    :rtype: ~asyncio.Task[~azure.ai.finetuningsessions.models.OperationResult]
    """
    _ensure_async_state(self)
    seq = self._sampling_session_seq.get(session_id, 0) + 1
    self._sampling_session_seq[session_id] = seq
    pending = await _save_weights_for_sampler_post(
        self,
        session_id,
        sampling_session_seq_id=seq,
        path=name,
    )
    return asyncio.create_task(pending.poll_result(), name=f"sync_sampler_{name}")


# -- Sampling ------------------------------------------------------------------


async def sample(
    self: "FineTuningSessionClient",
    session_id: str,
    prompt_tokens: List[int] | ModelInput,
    sampling_params: SamplingParams,
    *,
    checkpoint_id: str,
    num_samples: int = 1,
    sampling_session_id: Optional[str] = None,
    seq_id: Optional[int] = None,
    prompt_logprobs: bool = False,
    topk_prompt_logprobs: int = 0,
) -> OperationResult:
    """Generate completions using current LoRA weights.

    :param session_id: The session ID.
    :type session_id: str
    :param prompt_tokens: Tokenised prompt as a list of integer IDs, or a
        structured ``ModelInput`` for multimodal prompts.
    :type prompt_tokens: list[int] or ~azure.ai.finetuningsessions.models.ModelInput
    :param sampling_params: Generation parameters.
    :type sampling_params: ~azure.ai.finetuningsessions.models.SamplingParams
    :keyword checkpoint_id: Sampler checkpoint ID from ``save_weights_for_sampler``.
    :paramtype checkpoint_id: str
    :keyword num_samples: Number of completions. Default 1.
    :paramtype num_samples: int
    :keyword sampling_session_id: Optional sampling session ID sent with the request.
    :paramtype sampling_session_id: str or None
    :keyword seq_id: Optional sequence ID sent with the sampling request.
    :paramtype seq_id: int or None
    :keyword prompt_logprobs: If True, return per-token log-probabilities for the prompt.
    :paramtype prompt_logprobs: bool
    :keyword topk_prompt_logprobs: Top-k log-probabilities per prompt token. 0 = none. Must be between 0 and 20 (default 0).
    :paramtype topk_prompt_logprobs: int
    :return: OperationResult.
    :rtype: ~azure.ai.finetuningsessions.models.OperationResult

    Concurrency is bounded by a lifecycle-scoped semaphore (size
    ``_MAX_CONCURRENT_SAMPLES``). The permit is held for the FULL submit+poll
    lifecycle so a throttled or slow-generating sample does not release capacity
    to a burst queued behind it. A 429 on submit is treated as healthy
    backpressure and retried in place — honoring ``Retry-After`` + jitter — until
    ``_SAMPLE_THROTTLE_TIMEOUT_SEC``, then a typed ``RateLimitedError`` is raised.
    """
    _ensure_async_state(self)
    body = SampleRequest(
        num_samples=num_samples,
        prompt=(
            prompt_tokens
            if isinstance(prompt_tokens, ModelInput)
            else ModelInput(chunks=[ModelInputChunk(tokens=prompt_tokens)])
        ),
        sampling_params=sampling_params,
        topk_prompt_logprobs=topk_prompt_logprobs,
        sampling_session_id=sampling_session_id,
        seq_id=seq_id,
        prompt_logprobs=prompt_logprobs,
    )
    subpath = f"/fine_tuning/sessions/{session_id}/sample"
    operation_started_at = _time.monotonic()
    # Hold the lifecycle-scoped permit across BOTH submit and poll: releasing it
    # after submit would let a queued burst starve slow/throttled in-flight
    # samples. Permit is released only when this sample fully resolves (success,
    # throttle-cap, or error) — samples are independent, so there is no
    # hold-and-wait cycle and thus no deadlock.
    async with self._sample_semaphore:
        request_id, op_type = await _post_sample(
            self,
            subpath,
            body,
            extra_params={"checkpoint_id": checkpoint_id},
        )
        return await _poll_with_resubmit(
            self,
            session_id,
            request_id,
            op_type,
            subpath,
            body,
            extra_params={"checkpoint_id": checkpoint_id},
            post_fn=_post_sample,
            operation_started_at=operation_started_at,
        )


# -- Session lifecycle ---------------------------------------------------------


async def close_session(
    self: "FineTuningSessionClient",
    session_id: str,
) -> None:
    """Unload the session from the GPU engine.

    Stops the background heartbeat, then issues the complete request.

    :param session_id: The session ID to close.
    :type session_id: str
    :return: None.
    :rtype: None
    """
    resource_session_id = _client_resource_session_id(self, session_id)
    await _stop_heartbeat(self, session_id)
    close_req = _HttpRequest(
        "POST",
        "{endpoint}" + f"/fine_tuning/sessions/{resource_session_id}/complete",
        headers=_base_headers(),
        params={"api-version": _API_VERSION},
    )
    resp = await self.send_request(close_req)
    resp.raise_for_status()


async def delete_session(
    self: "FineTuningSessionClient",
    session_id: str,
) -> None:
    """Delete a session and cascade-delete its models, checkpoints, and sampling sessions.

    Stops the background heartbeat, then issues an HTTP DELETE against the
    session resource; the cascade is performed server-side.

    Idempotent — a 404 (session already gone) is swallowed.  Any other
    non-2xx surfaces via the standard SDK error path.

    :param session_id: The session ID to delete.
    :type session_id: str
    :return: None.
    :rtype: None
    """
    session_id = _canonical_session_id(session_id)
    resource_session_id = _client_resource_session_id(self, session_id)
    await _stop_heartbeat(self, session_id)
    del_req = _HttpRequest(
        "DELETE",
        "{endpoint}" + f"/fine_tuning/sessions/{resource_session_id}",
        headers=_base_headers(),
        params={"api-version": _API_VERSION},
    )
    resp = await self.send_request(del_req)
    if resp.status_code == 404:
        self._session_resource_ids.pop(session_id, None)
        return
    if resp.status_code >= 400:
        try:
            resp_body = resp.json()
        except Exception:
            resp_body = None
        typed = _classify_http_error(resp.status_code, resp_body, response=resp)
        if typed is not None:
            raise typed
        resp.raise_for_status()
    if not 200 <= resp.status_code < 300:
        raise _HttpResponseError(response=resp)
    self._session_resource_ids.pop(session_id, None)


# -- Statically visible supported public client -------------------------------


class FineTuningSessionClient(_ClientBase):
    """Async fine-tuning client with token/key authentication and training APIs.

    :param endpoint: Foundry project endpoint.
    :type endpoint: str
    :param credential: Token credential or API key for the endpoint.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential or ~azure.core.credentials.AzureKeyCredential
    """

    create_session = create_session
    create_session_from_checkpoint = create_session_from_checkpoint
    forward_backward = forward_backward
    forward_backward_post = forward_backward_post
    forward_backward_async = forward_backward_async
    forward = forward
    forward_post = forward_post
    forward_async = forward_async
    optim_step = optim_step
    optim_step_post = optim_step_post
    optim_step_async = optim_step_async
    save_weights = save_weights
    save_weights_post = save_weights_post
    save_weights_async = save_weights_async
    save_weights_for_sampler_async = save_weights_for_sampler_async
    save_weights_and_get_sampling_client_async = save_weights_and_get_sampling_client_async
    sample = sample
    close_session = close_session
    delete_session = delete_session


# -- Patch private compatibility imports ---------------------------------------

__all__: list[str] = ["FineTuningSessionClient"]


def patch_sdk():
    """Patch async convenience methods onto FineTuningSessionClient."""
    from . import _configuration
    from .._client_options import _patch_configuration

    _patch_configuration(_configuration, asynchronous=True)

    # Preserve the original private import path used by the upstream tests and
    # existing callers, while public construction uses the supported subclass.
    for name in (
        "create_session",
        "create_session_from_checkpoint",
        "forward_backward",
        "forward_backward_post",
        "forward_backward_async",
        "forward",
        "forward_post",
        "forward_async",
        "optim_step",
        "optim_step_post",
        "optim_step_async",
        "save_weights",
        "save_weights_post",
        "save_weights_async",
        "save_weights_for_sampler_async",
        "save_weights_and_get_sampling_client_async",
        "sample",
        "close_session",
        "delete_session",
    ):
        setattr(_GeneratedClient, name, getattr(FineTuningSessionClient, name))
