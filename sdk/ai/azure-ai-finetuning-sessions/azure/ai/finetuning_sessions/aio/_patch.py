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

    from azure.ai.finetuning_sessions.aio import FineTuningSessionClient

    async with FineTuningSessionClient(endpoint, credential) as client:
        session_id = await client.create_session(base_model="Llama-3.1-8B")
        fb = await client.forward_backward(session_id, batch, loss_fn="cross_entropy")
        opt = await client.optim_step(session_id, AdamParams(learning_rate=1e-4))
        await client.close_session(session_id)
"""
from __future__ import annotations

import asyncio
import json as _json
import logging as _logging
import random as _random
import time as _time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from azure.core.exceptions import ServiceRequestError as _ServiceRequestError
from azure.core.exceptions import ServiceResponseError as _ServiceResponseError
from azure.core.rest import HttpRequest as _HttpRequest

from .._exceptions import (
    _classify_http_error,
    _classify_poll_failure,
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
)

if TYPE_CHECKING:
    from ._client import FineTuningSessionClient

_PREVIEW = FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW
_logger = _logging.getLogger(__name__)

_POLL_LOG_DEDUP_SEC = 30.0

#: Default maximum concurrent POST requests.
_DEFAULT_POST_CONCURRENCY = 64


# -- Internal state initializer -----------------------------------------------

def _ensure_async_state(self: "FineTuningSessionClient") -> None:
    """Lazily initialize async state on the client instance."""
    if not hasattr(self, "_heartbeat_tasks"):
        self._heartbeat_tasks: dict[str, asyncio.Task] = {}
    if not hasattr(self, "_post_semaphore"):
        self._post_semaphore = asyncio.Semaphore(_DEFAULT_POST_CONCURRENCY)
    if not hasattr(self, "_sampling_session_seq"):
        self._sampling_session_seq: dict[str, int] = {}


# -- Background heartbeat -----------------------------------------------------

def _start_heartbeat(
    self: "FineTuningSessionClient",
    session_id: str,
    interval_sec: float = 30.0,
) -> None:
    """Start an asyncio task that sends heartbeat every interval_sec."""
    _ensure_async_state(self)
    raw_id = session_id.removeprefix("model_")
    heartbeat_session_id = f"session_{raw_id}"

    async def _heartbeat_loop() -> None:
        while True:
            await asyncio.sleep(interval_sec)
            try:
                hb_req = _HttpRequest(
                    "POST",
                    "{endpoint}"
                    + f"/fine_tuning/sessions/{heartbeat_session_id}/heartbeat",
                    headers=_base_headers(),
                    params={"api-version": _API_VERSION},
                )
                resp = await self.send_request(hb_req)
                if resp.status_code != 200:
                    _logger.warning(
                        "[heartbeat] status=%d for %s",
                        resp.status_code,
                        heartbeat_session_id,
                    )
            except asyncio.CancelledError:
                return
            except Exception as exc:
                _logger.warning(
                    "[heartbeat] failed for %s: %s",
                    heartbeat_session_id,
                    exc,
                )

    task = asyncio.create_task(
        _heartbeat_loop(), name=f"fts-heartbeat-{session_id}"
    )
    self._heartbeat_tasks[session_id] = task
    _logger.info(
        "[heartbeat] started (interval=%.0fs, session=%s)",
        interval_sec,
        heartbeat_session_id,
    )


def _stop_heartbeat(self: "FineTuningSessionClient", session_id: str) -> None:
    """Cancel the background heartbeat task for a session."""
    _ensure_async_state(self)
    task = self._heartbeat_tasks.pop(session_id, None)
    if task is not None:
        task.cancel()


# -- Low-level helpers ---------------------------------------------------------

async def _post(
    self: "FineTuningSessionClient",
    subpath: str,
    body_model: Any,
    extra_params: Optional[dict] = None,
) -> tuple[str, str]:
    """POST to enqueue a job.  Returns ``(request_id, op_type)``.

    Gated by ``_post_semaphore`` to prevent connection storms.
    Retries on 408/409/429/5xx with exponential backoff (max 5 retries).
    """
    _ensure_async_state(self)
    body_json = _json.dumps(
        body_model, cls=_SdkJSONEncoder, exclude_readonly=True
    )
    post_params: dict = {"api-version": _API_VERSION}
    if extra_params:
        post_params.update(extra_params)
    op_type = _LOOM_SUBPATH_TO_OP_TYPE.get(subpath.rsplit("/", 1)[-1], "")
    _log_http("request", "POST", subpath, body=_json.loads(body_json))

    max_retries = 2
    _BASE_TIMEOUT_SEC = 100  # per-request timeout; escalated on each retry
    _TIMEOUT_MULTIPLIER = 1.5
    # Non-retryable status codes: deterministic rejections that will
    # never succeed on retry. Surface a typed exception immediately.
    _NON_RETRYABLE = frozenset({400, 413, 422})

    async with self._post_semaphore:
        last_status: Optional[int] = None
        consecutive_same_status = 0

        for attempt in range(max_retries + 1):
            # Escalate per-request timeout on retries so later attempts
            # aren't doomed to the same cutoff when the server is slow.
            request_timeout = _BASE_TIMEOUT_SEC * (_TIMEOUT_MULTIPLIER ** attempt)
            try:
                post_req = _HttpRequest(
                    "POST",
                    "{endpoint}" + subpath,
                    headers=_base_headers({"Content-Type": "application/json"}),
                    params=post_params,
                    content=body_json,
                )
                resp = await self.send_request(
                    post_req, connection_timeout=request_timeout
                )
                sc = resp.status_code

                # --- Non-retryable: classify and raise immediately ---
                if sc in _NON_RETRYABLE:
                    try:
                        resp_body = resp.json()
                    except Exception:
                        resp_body = None
                    typed = _classify_http_error(sc, resp_body, response=resp)
                    if typed is not None:
                        raise typed
                    resp.raise_for_status()

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
                        try:
                            resp_body = resp.json()
                        except Exception:
                            resp_body = None
                        typed = _classify_http_error(sc, resp_body, response=resp)
                        if typed is not None:
                            raise typed

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
                    try:
                        resp_body = resp.json()
                    except Exception:
                        resp_body = None
                    typed = _classify_http_error(sc, resp_body, response=resp)
                    if typed is not None:
                        raise typed

                _log_http(
                    "response",
                    "POST",
                    subpath,
                    status=sc,
                    body=resp.json() if sc < 400 else None,
                )
                resp.raise_for_status()
                data = resp.json()
                return (
                    data["request_id"],
                    op_type,
                )

            except (_ServiceRequestError, _ServiceResponseError) as exc:
                if attempt < max_retries:
                    # Back off longer for network errors (timeout/connection
                    # failures). The actual request timeout is escalated via
                    # connection_timeout above.
                    wait = min(1.0 * (2**attempt), 10.0) * (
                        1 - 0.25 * _random.random()
                    )
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

    # Should not be reached.
    raise RuntimeError(f"POST {subpath} failed after {max_retries} retries")


async def _poll(
    self: "FineTuningSessionClient",
    session_id: str,
    request_id: str,
    op_type: str,
    extra_result_fields: Optional[dict] = None,
    error_budget_sec: Optional[float] = None,
) -> OperationResult:
    """Short-poll the envelope endpoint until the request resolves.

    Adaptive backoff: starts at ``_RETRIEVE_POLL_MIN``, doubles up to
    ``_RETRIEVE_POLL_MAX``. Retries 5xx and transient network errors.

    ``error_budget_sec`` is an ERROR budget, not a wall-clock budget (matching
    the sync ``_post_and_poll``): healthy pending progress is unbounded and
    CLEARS the budget, while a sustained streak of 5xx / 408 / 429 / transient
    network errors longer than the budget raises ``TimeoutError``. Pass ``None``
    to disable it (retry forever).
    """
    poll_path = f"/fine_tuning/sessions/{session_id}/request/{request_id}"
    conn_backoff = 1.0
    poll_backoff = _RETRIEVE_POLL_MIN
    error_budget = _ErrorBudget.for_polling(
        error_budget_sec, op_type=op_type, request_id=request_id
    )
    poll_start = _time.monotonic()

    while True:
        try:
            poll_req = _HttpRequest(
                "GET",
                "{endpoint}"
                + f"/fine_tuning/sessions/{session_id}/request/{request_id}",
                headers=_base_headers(),
                params={"api-version": _API_VERSION},
            )
            _log_http("request", "GET", poll_path)
            resp = await self.send_request(poll_req)

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
                    poll_backoff = min(poll_backoff * 2, _RETRIEVE_POLL_MAX)
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
                        f"Unexpected envelope status {status!r} for "
                        f"{op_type} request {request_id}: {envelope}"
                    )

                # completed -- normalize and deserialize.
                _clear_poll_log_state(session_id, request_id, op_type)
                raw = envelope.get("result") or {}
                normalized = _normalize_loom_result(raw, op_type, request_id)
                if extra_result_fields:
                    for k, v in extra_result_fields.items():
                        if not normalized.get(k):
                            normalized[k] = v
                return _deserialize_model(OperationResult, normalized)

            # Retryable HTTP status.
            if (
                500 <= resp.status_code < 600
                or resp.status_code in (408, 429)
            ):
                body: Optional[Any] = None
                try:
                    body = resp.json()
                except Exception:
                    body = None
                _log_http(
                    "response", "GET", poll_path,
                    status=resp.status_code, body=body,
                )
                elapsed = _time.monotonic() - poll_start
                _logger.debug(
                    "[poller] retry on %s/%s after HTTP %d (%.0fs elapsed)",
                    session_id, request_id, resp.status_code, elapsed,
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
                await asyncio.sleep(poll_wait)
                continue

            # Non-retryable HTTP error.
            _log_http(
                "response", "GET", poll_path,
                status=resp.status_code, body=None,
            )
            try:
                poll_body = resp.json()
            except Exception:
                poll_body = None
            typed = _classify_http_error(
                resp.status_code, poll_body, response=resp, session_id=session_id
            )
            if typed is not None:
                raise typed
            resp.raise_for_status()

        except (_ServiceRequestError, _ServiceResponseError) as exc:
            elapsed = _time.monotonic() - poll_start
            _logger.warning(
                "[poller] retry on %s/%s after %s(%s) (%.0fs elapsed), backoff %.1fs",
                session_id, request_id, type(exc).__name__, exc, elapsed, conn_backoff,
            )
            error_budget.consume(type(exc).__name__)
            await asyncio.sleep(conn_backoff)
            conn_backoff = min(conn_backoff * 2, 30.0)
            continue


async def _post_and_poll(
    self: "FineTuningSessionClient",
    session_id: str,
    subpath: str,
    body_model: Any,
    extra_params: Optional[dict] = None,
    extra_result_fields: Optional[dict] = None,
) -> OperationResult:
    """POST to enqueue a job, then poll until it completes."""
    request_id, op_type = await _post(
        self, subpath, body_model, extra_params
    )
    return await _poll(
        self,
        session_id,
        request_id,
        op_type,
        extra_result_fields,
        error_budget_sec=_DEFAULT_OPERATION_TIMEOUT_SEC,
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
) -> str:
    """Create a fine-tuning session and wait until the model is loaded.

    :param base_model: Name of the base model to load.
    :param lora_config: Optional LoRA adapter config.
    :param type: Session type string. Defaults to ``"training"``.
    :param from_checkpoint: Optional checkpoint to resume from.
    :param timeout_sec: Maximum seconds to wait for model load.
    :return: The ``session_id`` string (e.g. ``"model_abc123"``).
    """
    _ensure_async_state(self)

    body = _json.loads(
        _json.dumps(
            CreateSessionRequest(
                type=type, base_model=base_model, lora_config=lora_config,
            ),
            cls=_SdkJSONEncoder,
            exclude_readonly=True,
        )
    )
    if from_checkpoint is not None:
        body["from_checkpoint"] = _json.loads(
            _json.dumps(from_checkpoint, cls=_SdkJSONEncoder, exclude_readonly=True)
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

    session_id: str = f"model_{raw_session_id}"
    _logger.info(
        "[create_session] session_id transformed: raw=%s -> resource_id=%s",
        raw_session_id,
        session_id,
    )

    # Poll until model load completes.
    deadline = _time.monotonic() + timeout_sec
    conn_backoff = 1.0
    poll_backoff = _RETRIEVE_POLL_MIN
    _create_poll_start = _time.monotonic()
    while True:
        try:
            poll_req = _HttpRequest(
                "GET",
                "{endpoint}"
                + f"/fine_tuning/sessions/{session_id}/request/{request_id}",
                headers=_base_headers(),
                params={"api-version": _API_VERSION},
            )
            poll_path = (
                f"/fine_tuning/sessions/{session_id}/request/{request_id}"
            )
            _log_http("request", "GET", poll_path)
            poll_resp = await self.send_request(poll_req)
            envelope = (
                poll_resp.json() if poll_resp.status_code == 200 else None
            )
            _log_http(
                "response", "GET", poll_path,
                status=poll_resp.status_code, body=envelope,
            )

            if poll_resp.status_code == 200:
                env_status = envelope.get("status")
                if env_status == "completed":
                    _logger.info("[create_session] model load completed: %s", envelope)
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
                # pending -> adaptive backoff
                if _time.monotonic() > deadline:
                    raise RuntimeError(
                        f"Timed out after {timeout_sec}s waiting for "
                        f"session_id={raw_session_id} to become ready"
                    )
                elapsed = _time.monotonic() - _create_poll_start
                _maybe_log_poll_progress(envelope, session_id, request_id, "create_session", elapsed)
                conn_backoff = 1.0
                await asyncio.sleep(poll_backoff)
                poll_backoff = min(poll_backoff * 2, _RETRIEVE_POLL_MAX)
                continue

            # Retryable HTTP status codes.
            if (
                500 <= poll_resp.status_code < 600
                or poll_resp.status_code in (408, 429)
            ):
                if _time.monotonic() > deadline:
                    raise RuntimeError(
                        f"Timed out after {timeout_sec}s waiting for "
                        f"session_id={raw_session_id} to become ready"
                    )
                elapsed = _time.monotonic() - _create_poll_start
                _logger.debug(
                    "[poller] retry on %s/%s after HTTP %d (%.0fs elapsed)",
                    session_id, request_id, poll_resp.status_code, elapsed,
                )
                conn_backoff = 1.0
                await asyncio.sleep(_RETRIEVE_POLL_MIN)
                continue

            # Non-retryable error.
            try:
                poll_body = poll_resp.json()
            except Exception:
                poll_body = None
            typed = _classify_http_error(
                poll_resp.status_code, poll_body, response=poll_resp, session_id=session_id
            )
            if typed is not None:
                raise typed
            poll_resp.raise_for_status()

        except (_ServiceRequestError, _ServiceResponseError) as exc:
            if _time.monotonic() > deadline:
                raise RuntimeError(
                    f"Timed out after {timeout_sec}s waiting for "
                    f"session_id={raw_session_id} to become ready"
                ) from exc
            elapsed = _time.monotonic() - _create_poll_start
            _logger.warning(
                "[poller] retry on %s/%s after %s(%s) (%.0fs elapsed), backoff %.1fs",
                session_id, request_id, type(exc).__name__, exc, elapsed, conn_backoff,
            )
            await asyncio.sleep(conn_backoff)
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

    :param checkpoint_path: Format: ``"<source_session_id>/<checkpoint_name>"``.
    :param base_model: Base model name.
    :param lora_config: Optional LoRA config override.
    :param type: Session type. Defaults to ``"training"``.
    :param timeout_sec: Maximum seconds to wait for model load.
    :return: The ``session_id`` string.
    """
    parts = checkpoint_path.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(
            "checkpoint_path must be '<source_session_id>/<checkpoint_name>' "
            f"with exactly one '/' separator, got: {checkpoint_path!r}"
        )
    source_session_id, checkpoint_id = parts
    if not source_session_id.startswith("model_"):
        source_session_id = f"model_{source_session_id}"
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
    :param batch: List of Datum.
    :param loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
    :param loss_fn_config: Optional per-loss hyper-parameters.
    :return: OperationResult.
    """
    chunks = _chunk_data(batch)
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

    async def _submit_chunk(
        i: int, chunk: List[Datum]
    ) -> ForwardBackwardOperationResult:
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
            total_loss=getattr(result, "total_loss", 0.0),
            per_datum_logprobs=getattr(result, "per_datum_logprobs", None),
            metrics=getattr(result, "metrics", None),
        )

    # Fire all chunks in parallel.
    chunk_results = await asyncio.gather(
        *(_submit_chunk(i, chunk) for i, chunk in enumerate(chunks))
    )
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
    :param batch: List of Datum.
    :param loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
    :param loss_fn_config: Optional per-loss hyper-parameters.
    :return: OperationResult.
    """
    chunks = _chunk_data(batch)
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

    async def _submit_chunk(
        i: int, chunk: List[Datum]
    ) -> ForwardBackwardOperationResult:
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
            total_loss=getattr(result, "total_loss", 0.0),
            per_datum_logprobs=getattr(result, "per_datum_logprobs", None),
            metrics=getattr(result, "metrics", None),
        )

    # Fire all chunks in parallel.
    chunk_results = await asyncio.gather(
        *(_submit_chunk(i, chunk) for i, chunk in enumerate(chunks))
    )
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
    :param batch: List of Datum.
    :param loss_fn: Loss function name.
    :param loss_fn_config: Optional per-loss hyper-parameters.
    :return: PendingRequests handle.
    """
    subpath = f"/fine_tuning/sessions/{session_id}/forward"
    chunks = _chunk_data(batch)

    if len(chunks) > 1:
        _logger.info(
            "[forward_post] batch of %d datums split into %d chunks: %s",
            len(batch),
            len(chunks),
            [len(c) for c in chunks],
        )

    posted: List[tuple] = []
    for chunk in chunks:
        request_id, op_type = await _post(
            self,
            subpath,
            ForwardRequest(
                forward_input=ForwardInput(
                    data=chunk,
                    loss_fn=loss_fn,
                    loss_fn_config=loss_fn_config,
                )
            ),
        )
        posted.append((request_id, op_type))

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
    :param batch: List of Datum.
    :param loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
    :param loss_fn_config: Optional per-loss hyper-parameters.
    :return: An asyncio.Task whose result is an OperationResult.
    """
    pending = await forward_post(
        self, session_id, batch, loss_fn=loss_fn, loss_fn_config=loss_fn_config
    )

    if len(pending._posted) > 1:
        _logger.info(
            "[forward_async] multi-chunk (%d): awaiting all chunk results before returning",
            len(pending._posted),
        )
        result = await pending.poll_result()
        done: asyncio.Future[OperationResult] = asyncio.get_running_loop().create_future()
        done.set_result(result)
        return done  # type: ignore[return-value]

    return asyncio.create_task(pending.poll_result(), name="fwd_poll")


async def optim_step(
    self: "FineTuningSessionClient",
    session_id: str,
    adam_params: AdamParams,
) -> OperationResult:
    """Apply accumulated gradients with Adam.

    :param session_id: The session ID.
    :param adam_params: Optimizer hyper-parameters.
    :return: OperationResult.
    """
    return await _post_and_poll(
        self,
        session_id,
        f"/fine_tuning/sessions/{session_id}/optim_step",
        OptimStepRequest(adam_params=adam_params),
    )


# -- POST-only variants (for pipelined training) -------------------------------


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
        posted: List[tuple],
        chunks: Optional[List[List[Datum]]] = None,
        extra_result_fields: Optional[dict] = None,
    ):
        self._client = client
        self._session_id = session_id
        self._posted = posted  # list of (request_id, op_type)
        self._chunks = chunks  # only set for chunked forward_backward
        self._extra_result_fields = extra_result_fields

    async def poll_result(self) -> OperationResult:
        """Poll until all POSTed requests complete and return the combined result."""
        if len(self._posted) == 1:
            rid, ot = self._posted[0]
            return await _poll(
                self._client, self._session_id, rid, ot,
                extra_result_fields=self._extra_result_fields,
                error_budget_sec=_DEFAULT_OPERATION_TIMEOUT_SEC,
            )

        # Multiple chunks — poll in parallel and combine.
        async def _poll_one(rid: str, ot: str) -> ForwardBackwardOperationResult:
            result = await _poll(
                self._client, self._session_id, rid, ot,
                extra_result_fields=self._extra_result_fields,
                error_budget_sec=_DEFAULT_OPERATION_TIMEOUT_SEC,
            )
            if isinstance(result, ForwardBackwardOperationResult):
                return result
            return ForwardBackwardOperationResult(
                total_loss=getattr(result, "total_loss", 0.0),
                per_datum_logprobs=getattr(result, "per_datum_logprobs", None),
                metrics=getattr(result, "metrics", None),
            )

        chunk_results = await asyncio.gather(
            *(_poll_one(rid, ot) for rid, ot in self._posted)
        )
        chunk_sizes = [len(c) for c in self._chunks] if self._chunks else [1] * len(self._posted)
        return _combine_fwd_bwd_results(list(chunk_results), chunk_sizes)


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
    :param batch: List of Datum.
    :param loss_fn: Loss function name.
    :param loss_fn_config: Optional per-loss hyper-parameters.
    :return: PendingRequests handle.
    """
    subpath = f"/fine_tuning/sessions/{session_id}/forward_backward"
    chunks = _chunk_data(batch)

    if len(chunks) > 1:
        _logger.info(
            "[forward_backward_post] batch of %d datums split into %d chunks: %s",
            len(batch),
            len(chunks),
            [len(c) for c in chunks],
        )

    posted: List[tuple] = []
    for chunk in chunks:
        request_id, op_type = await _post(
            self,
            subpath,
            ForwardBackwardRequest(
                forward_backward_input=ForwardBackwardInput(
                    data=chunk,
                    loss_fn=loss_fn,
                    loss_fn_config=loss_fn_config,
                )
            ),
        )
        posted.append((request_id, op_type))

    return PendingRequests(self, session_id, posted, chunks)


async def forward_backward_async(
    self: "FineTuningSessionClient",
    session_id: str,
    batch: List[Datum],
    *,
    loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY,
    loss_fn_config: Optional[LossFnConfig] = None,
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

    :param session_id: The session ID.
    :param batch: List of Datum.
    :param loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
    :param loss_fn_config: Optional per-loss hyper-parameters.
    :return: An asyncio.Task whose result is an OperationResult.
    """
    pending = await forward_backward_post(
        self, session_id, batch, loss_fn=loss_fn, loss_fn_config=loss_fn_config
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
        result = await pending.poll_result()
        done: asyncio.Future[OperationResult] = asyncio.get_running_loop().create_future()
        done.set_result(result)
        return done  # type: ignore[return-value]  # Future is awaitable like Task

    return asyncio.create_task(pending.poll_result(), name="fwd_bwd_poll")


async def optim_step_post(
    self: "FineTuningSessionClient",
    session_id: str,
    adam_params: AdamParams,
) -> PendingRequests:
    """POST an optim_step without polling for completion.

    Returns a :class:`PendingRequests` handle whose ``poll_result()``
    can be awaited later.

    :param session_id: The session ID.
    :param adam_params: Optimizer hyper-parameters.
    :return: PendingRequests handle.
    """
    subpath = f"/fine_tuning/sessions/{session_id}/optim_step"
    request_id, op_type = await _post(
        self,
        subpath,
        OptimStepRequest(adam_params=adam_params),
    )
    return PendingRequests(self, session_id, [(request_id, op_type)])


async def optim_step_async(
    self: "FineTuningSessionClient",
    session_id: str,
    adam_params: AdamParams,
) -> "asyncio.Task[OperationResult]":
    """Submit an optim_step, return an asyncio Task for the result.

    Awaits the POST so the server assigns a UUID v7 *after* all preceding
    forward_backward_async calls.  Only the poll runs in the background.

    :param session_id: The session ID.
    :param adam_params: Optimizer hyper-parameters.
    :return: An asyncio.Task whose result is an OperationResult.
    """
    pending = await optim_step_post(self, session_id, adam_params)
    return asyncio.create_task(pending.poll_result(), name="optim_poll")


# -- Checkpoints ---------------------------------------------------------------

async def save_weights(
    self: "FineTuningSessionClient",
    session_id: str,
    path: str,
) -> OperationResult:
    """Save a training checkpoint (LoRA weights + optimizer state).

    :param session_id: The session ID.
    :param path: Checkpoint name/path.
    :return: OperationResult.
    """
    return await _post_and_poll(
        self,
        session_id,
        f"/fine_tuning/sessions/{session_id}/checkpoint",
        SaveCheckpointRequest(path=path),
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
    :param path: Checkpoint name/path.
    :param step_number: Training step number for this checkpoint.
    :param metrics: Evaluation metrics at checkpoint time.
    :return: PendingRequests handle.
    """
    subpath = f"/fine_tuning/sessions/{session_id}/checkpoint"
    request_id, op_type = await _post(
        self,
        subpath,
        SaveCheckpointRequest(path=path, step_number=step_number, metrics=metrics),
    )
    return PendingRequests(self, session_id, [(request_id, op_type)])


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
    :param path: Checkpoint name/path.
    :param step_number: Training step number for this checkpoint.
    :param metrics: Evaluation metrics at checkpoint time.
    :return: An asyncio.Task whose result is an OperationResult.
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
    request_id, op_type = await _post(
        self,
        subpath,
        SaveSamplerWeightsRequest(
            seq_id=0,
            sampling_session_seq_id=sampling_session_seq_id,
            path=path,
        ),
    )
    return PendingRequests(
        self, session_id, [(request_id, op_type)],
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
    :param name: Checkpoint name/identifier.
    :return: An asyncio.Task whose result is an OperationResult with
        ``checkpoint_id`` set to *name*.
    """
    _ensure_async_state(self)
    pending = await _save_weights_for_sampler_post(
        self, session_id, path=name,
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
    :param name: Checkpoint name/identifier (e.g. ``"step5"``).
    :return: An asyncio.Task whose result is an OperationResult with
        ``checkpoint_id`` set to *name*.
    """
    _ensure_async_state(self)
    seq = self._sampling_session_seq.get(session_id, 0) + 1
    self._sampling_session_seq[session_id] = seq
    pending = await _save_weights_for_sampler_post(
        self, session_id,
        sampling_session_seq_id=seq, path=name,
    )
    return asyncio.create_task(pending.poll_result(), name=f"sync_sampler_{name}")


# -- Sampling ------------------------------------------------------------------

async def sample(
    self: "FineTuningSessionClient",
    session_id: str,
    prompt_tokens: List[int],
    sampling_params: SamplingParams,
    *,
    checkpoint_id: str,
    num_samples: int = 1,
    sampling_session_id: Optional[str] = None,
    seq_id: Optional[int] = None,
    prompt_logprobs: bool = False,
    return_prompt_token_ids: bool = False,
    topk_prompt_logprobs: int = 0,
) -> OperationResult:
    """Generate completions using current LoRA weights.

    :param session_id: The session ID.
    :param prompt_tokens: Tokenised prompt as a list of integer IDs.
    :param sampling_params: Generation parameters.
    :param checkpoint_id: Sampler checkpoint ID from ``save_weights_for_sampler``.
    :param num_samples: Number of completions. Default 1.
    :param return_prompt_token_ids: If True, return the exact prompt token IDs with the sample result.
    :return: OperationResult.
    """
    return await _post_and_poll(
        self,
        session_id,
        f"/fine_tuning/sessions/{session_id}/sample",
        SampleRequest(
            num_samples=num_samples,
            prompt=ModelInput(chunks=[ModelInputChunk(tokens=prompt_tokens)]),
            sampling_params=sampling_params,
            topk_prompt_logprobs=topk_prompt_logprobs,
            return_prompt_token_ids=return_prompt_token_ids,
            sampling_session_id=sampling_session_id,
            seq_id=seq_id,
            prompt_logprobs=prompt_logprobs,
        ),
        extra_params={"checkpoint_id": checkpoint_id},
    )


# -- Session lifecycle ---------------------------------------------------------

async def close_session(
    self: "FineTuningSessionClient",
    session_id: str,
) -> None:
    """Unload the session from the GPU engine.

    Stops the background heartbeat, then issues the complete request.

    :param session_id: The session ID to close.
    """
    _stop_heartbeat(self, session_id)
    close_req = _HttpRequest(
        "POST",
        "{endpoint}" + f"/fine_tuning/sessions/{session_id}/complete",
        headers=_base_headers(),
        params={"api-version": _API_VERSION},
    )
    resp = await self.send_request(close_req)
    resp.raise_for_status()


# -- Patch the generated client ------------------------------------------------

__all__: list[str] = []


def patch_sdk():
    """Patch async convenience methods onto FineTuningSessionClient."""
    from ._client import FineTuningSessionClient

    FineTuningSessionClient.create_session = create_session
    FineTuningSessionClient.create_session_from_checkpoint = create_session_from_checkpoint
    FineTuningSessionClient.forward_backward = forward_backward
    FineTuningSessionClient.forward_backward_post = forward_backward_post
    FineTuningSessionClient.forward_backward_async = forward_backward_async
    FineTuningSessionClient.forward = forward
    FineTuningSessionClient.forward_post = forward_post
    FineTuningSessionClient.forward_async = forward_async
    FineTuningSessionClient.optim_step = optim_step
    FineTuningSessionClient.optim_step_post = optim_step_post
    FineTuningSessionClient.optim_step_async = optim_step_async
    FineTuningSessionClient.save_weights = save_weights
    FineTuningSessionClient.save_weights_post = save_weights_post
    FineTuningSessionClient.save_weights_async = save_weights_async
    FineTuningSessionClient.save_weights_for_sampler_async = save_weights_for_sampler_async
    FineTuningSessionClient.save_weights_and_get_sampling_client_async = save_weights_and_get_sampling_client_async
    FineTuningSessionClient.sample = sample
    FineTuningSessionClient.close_session = close_session
