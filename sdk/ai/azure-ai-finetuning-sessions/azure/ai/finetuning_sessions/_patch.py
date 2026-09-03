# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Handwritten convenience layer on top of the generated FineTuningSessionClient.

``FineTuningSession`` wraps a live session and exposes the hero-code API from
SPEC_FOUNDRY_AICLIENT.md:

    session = FineTuningSession(client, session_id="session_xxx")
    fb_result  = session.forward_backward(batch, loss_fn="cross_entropy")
    opt_result = session.optim_step(AdamParams(learning_rate=1e-4))
    ckpt_result    = session.save_weights("my_checkpoint")
    sampler_result = session.save_weights_for_sampler(seq_id=0)
    sample_result  = session.sample(prompt_tokens, sampling_params, num_samples=4)
    session.close()

Each mutating method follows loom's two-step protocol:
  1. POST to the action endpoint — loom returns **200** with
     ``{request_id, session_id, status: "pending"}``.
  2. GET ``/fine_tuning/sessions/{sessionId}/request/{requestId}`` — the server
     long-polls (up to 5 minutes) and returns the typed result when the GPU finishes.

Note: the generated ``begin_*`` methods on sub-clients use the Azure LRO (202 +
Operation-Location header) pattern and will **not** work against loom, which returns
200.  Always use ``FineTuningSession`` methods for training operations.
"""
from __future__ import annotations

import concurrent.futures as _futures
import json as _json
import logging as _logging
import os as _os
import threading as _threading
import time as _time
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Union

from azure.core import PipelineClient
from azure.core.exceptions import HttpResponseError as _HttpResponseError
from azure.core.exceptions import ServiceRequestError as _ServiceRequestError
from azure.core.exceptions import ServiceResponseError as _ServiceResponseError
from azure.core.pipeline import policies
from azure.core.rest import HttpRequest as _HttpRequest

from ._exceptions import (
    _classify_http_error,
    _classify_poll_failure,
)

from .models import (
    AdamParams,
    CreateSessionRequest,
    Datum,
    ForwardBackwardInput,
    ForwardBackwardOperationResult,
    ForwardBackwardRequest,
    FromCheckpoint,
    LoRAConfig,
    LossFn,
    LossFnConfig,
    ModelInput,
    ModelInputChunk,
    OperationResult,
    OperationType,
    OptimStepRequest,
    SampleRequest,
    SamplingParams,
    SaveCheckpointRequest,
    SaveSamplerWeightsRequest,
    TensorData,
    FoundryFeaturesOptInKeys,
)
from ._client import FineTuningSessionClient as FineTuningSessionClientGenerated
from ._utils.model_base import SdkJSONEncoder as _SdkJSONEncoder, _deserialize as _deserialize_model

# ── Loom wire-format → OperationResult discriminator map ─────────────────────
# Maps the last path segment of a Loom action URL to the SDK's "type" value.
# NOTE: "forward" maps to "forward_backward" because there is no dedicated
# ForwardOperationResult class yet. This means ForwardBackwardOperationResult
# must tolerate missing fields (total_loss, metrics) — do NOT add required
# fields to that class without also providing a separate ForwardOperationResult.
_LOOM_SUBPATH_TO_OP_TYPE: dict[str, str] = {
    "forward_backward": "forward_backward",
    "forward": "forward_backward",
    "optim_step": "optim_step",
    "checkpoint": "save_checkpoint",
    "checkpoint_sample": "save_sampler_weights",
    "sample": "sample",
}

# ---------------------------------------------------------------------------
# Chunked forward_backward helpers
# ---------------------------------------------------------------------------

#: Maximum number of datums in a single forward_backward HTTP request.
_MAX_CHUNK_LEN = 1024

#: Approximate maximum payload size (bytes) for a single request.
_MAX_CHUNK_BYTES = 5_000_000


def _estimate_bytes_count(datum: Datum) -> int:
    """Estimate the serialised size of a single Datum."""
    size = 0
    # Model input chunks — each token ID ≈ 10 bytes when JSON-serialised.
    for chunk in datum.model_input.chunks:
        size += len(chunk.tokens) * 10
    # Loss function inputs — each TensorData field's data list × 10.
    lfi = datum.loss_fn_inputs
    for field_name in ("target_tokens", "weights", "advantages", "logprobs"):
        td = getattr(lfi, field_name, None)
        if td is not None and hasattr(td, "data") and td.data is not None:
            size += len(td.data) * 10
    return size


def _chunk_data(data: List[Datum]) -> List[List[Datum]]:
    """Split Datum list into chunks respecting size limits."""
    chunks: List[List[Datum]] = []
    current: List[Datum] = []
    current_bytes = 0
    for datum in data:
        est = _estimate_bytes_count(datum)
        if (
            len(current) > 0
            and current_bytes + est > _MAX_CHUNK_BYTES
        ) or len(current) == _MAX_CHUNK_LEN:
            chunks.append(current)
            current = []
            current_bytes = 0
        current.append(datum)
        current_bytes += est
    if current:
        chunks.append(current)
    return chunks


# ── Metric reduction ──────────────────────────────────────────────────────


def _reduce_mean(xs: List[float], weights: Optional[List[int]] = None) -> float:
    if weights is None or sum(weights) == 0:
        return sum(xs) / len(xs) if xs else 0.0
    total = sum(x * w for x, w in zip(xs, weights))
    return total / sum(weights)


def _reduce_sum(xs: List[float]) -> float:
    return sum(xs)


def _reduce_min(xs: List[float]) -> float:
    return min(xs)


def _reduce_max(xs: List[float]) -> float:
    return max(xs)


def _reduce_slack(xs: List[float], weights: Optional[List[int]] = None) -> float:
    return max(xs) - _reduce_mean(xs, weights)


def _order_insensitive_hash(xs: list) -> int:
    """Order-insensitive hash for metric deduplication."""
    if xs and isinstance(xs[0], set):
        return hash(tuple(sorted([y for x in xs for y in x])))
    return hash(tuple(sorted(int(x) for x in xs)))


_REDUCE_MAP = {
    "mean": _reduce_mean,
    "sum": _reduce_sum,
    "min": _reduce_min,
    "max": _reduce_max,
    "slack": _reduce_slack,
    "hash_unordered": _order_insensitive_hash,
    "unique": lambda xs: xs,
}


def _metrics_reduction(
    results: List[ForwardBackwardOperationResult],
    chunk_sizes: List[int],
) -> dict:
    """Reduce metrics across chunked forward_backward results.

    Uses ``chunk_sizes`` (number of datums per chunk) as weights.
    """
    if not results:
        return {}
    # `forward` route returns a base ``OperationResult`` with no `metrics`
    # field; tolerate that by using getattr throughout.
    # TODO(forward-route): add a proper ``ForwardOperationResult`` subclass
    # to ``models/_models.py`` (per_datum_logprobs only, no total_loss /
    # metrics) and drop the ``"forward": "forward_backward"`` mapping in
    # ``_LOOM_SUBPATH_TO_OP_TYPE``. Then this defensive getattr can go away.
    first_metrics = getattr(results[0], "metrics", None) or {}
    keys = first_metrics.keys()
    res: dict = {}
    for key in keys:
        parts = key.split(":")
        if len(parts) != 2:
            continue
        name, reduction = parts
        if reduction not in _REDUCE_MAP:
            _logger.debug(
                "Invalid reduction=%s for metric name=%s. Expecting one of %s",
                reduction, name, list(_REDUCE_MAP.keys()),
            )
            continue
        if not all(key in (getattr(m, "metrics", None) or {}) for m in results):
            continue
        values = [(getattr(m, "metrics", None) or {})[key] for m in results]
        reduce_fn = _REDUCE_MAP[reduction]

        if reduction in ("mean", "slack"):
            res[key] = reduce_fn(values, chunk_sizes)
        elif reduction == "unique":
            res[key] = values[0]
            res.update({f"{key}_{i + 1}": v for i, v in enumerate(values[1:])})
        else:
            res[key] = reduce_fn(values)
    return res


def _combine_fwd_bwd_results(
    results: List[ForwardBackwardOperationResult],
    chunk_sizes: List[int],
) -> ForwardBackwardOperationResult:
    """Combine results from multiple forward_backward chunks."""
    if not results:
        return ForwardBackwardOperationResult(total_loss=0.0)

    combined_metrics = _metrics_reduction(results, chunk_sizes)
    combined_logprobs: List[TensorData] = []
    for r in results:
        if r.per_datum_logprobs:
            combined_logprobs.extend(r.per_datum_logprobs)
    # Combine loss_fn_outputs (extra JSON field carrying per-datum logprobs
    # from the Loom server).  The cookbook reads this field first, falling
    # back to per_datum_logprobs only when it is absent.
    combined_lfo: list = []
    for r in results:
        lfo = r.get("loss_fn_outputs") if hasattr(r, "get") else None
        if lfo:
            combined_lfo.extend(lfo)
    total_loss = sum(r.total_loss for r in results)
    combined: dict = {
        "total_loss": total_loss,
        "per_datum_logprobs": combined_logprobs or None,
        "metrics": combined_metrics or None,
    }
    if combined_lfo:
        combined["loss_fn_outputs"] = combined_lfo
    return ForwardBackwardOperationResult(combined)


def _normalize_loom_result(data: dict, op_type: str, request_id: str) -> dict:
    """Normalize the Loom poll-endpoint wire format into an OperationResult dict.

    The Loom server returns raw engine results (no ``"type"`` discriminator, metrics
    under namespaced keys like ``"total_loss:sum"``).  This function injects the
    discriminator and promotes metric fields so ``_deserialize(OperationResult, ...)``
    returns the correct typed subclass.
    """
    out = dict(data)
    out.setdefault("type", op_type)
    out.setdefault("operation_id", request_id)
    out.setdefault("status", "succeeded")

    metrics: dict = out.get("metrics") or {}

    if op_type == "forward_backward":
        if "total_loss" not in out:
            out["total_loss"] = float(metrics.get("total_loss:sum", 0.0))

    elif op_type == "optim_step":
        if "grad_norm" not in out:
            out["grad_norm"] = float(metrics.get("skyrl.ai/grad_norm", 0.0))
        if "step_count" not in out:
            out["step_count"] = int(metrics.get("step_count", 0))

    elif op_type == "save_sampler_weights":
        # Server may return "type": "save_weights_for_sampler" — normalise to SDK value.
        out["type"] = "save_sampler_weights"
        out.setdefault("checkpoint_id", out.get("checkpoint_id", ""))
        out.setdefault("sampling_session_id", out.get("sampling_session_id", ""))

    elif op_type == "save_checkpoint":
        out["type"] = "save_checkpoint"  # force, in case server returns a different value
        out.setdefault("checkpoint_id", out.get("checkpoint_id", ""))
        out.setdefault("path", out.get("path", ""))

    return out

_PREVIEW = FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW
_API_VERSION = "v1"
_logger = _logging.getLogger(__name__)

#: Per-call HTTP timeout for the (now short-poll) retrieve-status endpoint.
#: The server returns immediately, so this only needs to cover network RTT and
#: a one-shot DB read.
_RETRIEVE_TIMEOUT = 15.0

#: Adaptive poll backoff bounds (seconds) for the retrieve-status endpoint.
#: We start at MIN (catches fast operations cheaply) and double up to MAX
#: (bounds RPS for long-running operations).  Backoff resets on every new
#: poll loop (i.e. per-request), so each future starts polling at MIN.
_RETRIEVE_POLL_MIN = 1.0
_RETRIEVE_POLL_MAX = 30.0


def _operation_timeout_from_env() -> Optional[float]:
    env_name = "AZURE_AI_FINETUNING_SESSIONS_OPERATION_TIMEOUT_SEC"
    raw = _os.environ.get(env_name)
    if raw is None:
        _logger.debug("%s not set; using default 3600s operation timeout", env_name)
        return 3600.0  # not set -> default
    try:
        value = float(raw)
    except ValueError:
        _logger.warning("Invalid %s=%r; using default 3600s", env_name, raw)
        return 3600.0  # invalid -> default
    if value > 0:
        _logger.debug("%s=%s; operation timeout set to %.0fs", env_name, raw, value)
        return value
    _logger.warning("%s=%s; operation timeout DISABLED (retries can run unbounded)", env_name, raw)
    return None  # 0 (or negative) -> disabled


# Per-operation polling timeout for training/sample/checkpoint requests. This
# bounds retry loops on repeated 5xx/network failures while still allowing long
# operations; set env var to 0 (or negative) to disable.
_DEFAULT_OPERATION_TIMEOUT_SEC = _operation_timeout_from_env()


class _ErrorBudget:
    """Bounds a sustained error streak; healthy progress is unbounded.

    ``budget_sec=None`` disables the budget. ``on_exhausted(reason, budget_sec)``
    builds the exception to raise, where ``reason`` is the short error label
    (e.g. ``"HTTP 503"``) and ``budget_sec`` is the configured budget in seconds.
    """

    def __init__(
        self,
        budget_sec: Optional[float],
        *,
        on_exhausted: Callable[[str, float], BaseException],
    ) -> None:
        self._budget = budget_sec
        self._on_exhausted = on_exhausted
        self._deadline: Optional[float] = None

    @classmethod
    def for_polling(
        cls,
        budget_sec: Optional[float],
        *,
        op_type: str,
        request_id: str,
    ) -> "_ErrorBudget":
        """Build a poll-loop budget that raises ``TimeoutError`` when exhausted.

        Shared by the sync and async poll loops so the exhaustion message lives
        in one place.
        """
        return cls(
            budget_sec,
            on_exhausted=lambda reason, budget: TimeoutError(
                f"Timed out after {budget:.0f}s of sustained "
                f"errors ({reason}) waiting for {op_type or 'operation'} request {request_id}"
            ),
        )

    def clear(self) -> None:
        """Disarm; call on every healthy poll."""
        self._deadline = None

    def consume(self, reason: str) -> None:
        """Arm on the first error, raise once the streak outlasts the budget."""
        if self._budget is None:
            return
        now = _time.monotonic()
        if self._deadline is None:
            self._deadline = now + self._budget
        elif now > self._deadline:
            raise self._on_exhausted(reason, self._budget)


# Poll-progress state shared by sync and async clients.
_poll_log_last: dict[tuple[str, str], float] = {}
_request_active_since: dict[tuple[str, str], float] = {}
_POLL_LOG_DEDUP_SEC = 30.0


def _maybe_log_poll_progress(
    envelope: dict,
    session_id: str,
    request_id: str,
    op_type: str,
    elapsed: float,
) -> None:
    """Emit a throttled poll-progress log for a pending request."""
    now = _time.monotonic()
    is_queued = envelope.get("phase") == "resuming_session"
    req_key = (session_id, request_id)

    if is_queued:
        # Restart active timing if a request moves back to the queue.
        _request_active_since.pop(req_key, None)
        display_elapsed = elapsed
    else:
        active_since = _request_active_since.get(req_key)
        if active_since is None:
            _request_active_since[req_key] = now
            display_elapsed = 0.0
        else:
            display_elapsed = now - active_since

    if display_elapsed < _POLL_LOG_DEDUP_SEC:
        return
    dedup_key = (session_id, op_type)
    if now - _poll_log_last.get(dedup_key, 0.0) < _POLL_LOG_DEDUP_SEC:
        return
    _poll_log_last[dedup_key] = now
    if is_queued:
        _logger.info(
            "[poller] %s/%s (op=%s) queued waiting for capacity \u2014 %.0fs elapsed",
            session_id, request_id, op_type, display_elapsed,
        )
    else:
        _logger.info(
            "[poller] %s/%s (op=%s) in progress \u2014 %.0fs elapsed",
            session_id, request_id, op_type, display_elapsed,
        )


def _clear_poll_log_state(session_id: str, request_id: str, op_type: str) -> None:
    """Drop poll-progress state for a finished request."""
    _request_active_since.pop((session_id, request_id), None)
    _poll_log_last.pop((session_id, op_type), None)

# ---------------------------------------------------------------------------
# Verbose HTTP logging toggle
# ---------------------------------------------------------------------------
# Set to True (or set env var FINETUNING_VERBOSE_HTTP=1) to log every request
# URL + body and response status + body for all SDK API calls.
VERBOSE_HTTP: bool = _os.environ.get("FINETUNING_VERBOSE_HTTP", "").lower() in ("1", "true", "yes")


def _log_http(direction: str, method: str, url: str, status: Optional[int] = None, body: Any = None) -> None:
    """Log an HTTP request or response if VERBOSE_HTTP is enabled."""
    if not VERBOSE_HTTP:
        return
    body_str = ""
    if body is not None:
        try:
            body_str = _json.dumps(body, indent=2) if isinstance(body, (dict, list)) else str(body)
        except Exception:  # pragma: no cover
            body_str = repr(body)
        body_str = f"\n{body_str}"
    if direction == "request":
        _logger.info("[HTTP] --> %s %s%s", method, url, body_str)
    else:
        _logger.info("[HTTP] <-- %s %s  status=%d%s", method, url, status or 0, body_str)


def _base_headers(extra: Optional[dict] = None) -> dict:
    """Build the common headers for every Loom request.

    Reads ``X_COGNITIVE_SUBSCRIPTION_ID`` (or ``COGNITIVE_SUBSCRIPTION_ID`` /
    ``AZURE_SUBSCRIPTION_ID`` as fallbacks) from the environment and injects it
    as ``apim-subscription-id``.  The remote Loom endpoint (LOOM_SETUP_MODE=prod)
    requires this header on every request — same as
    ``clean_remote.sh`` which sets ``X_COGNITIVE_SUBSCRIPTION_ID=local-sub``.
    """
    headers: dict = {
        "Accept": "application/json",
        "Foundry-Features": _PREVIEW.value,
    }
    sub_id = (
        _os.environ.get("X_COGNITIVE_SUBSCRIPTION_ID")
        or _os.environ.get("COGNITIVE_SUBSCRIPTION_ID")
        or _os.environ.get("AZURE_SUBSCRIPTION_ID")
    )
    if sub_id:
        headers["apim-subscription-id"] = sub_id
    if extra:
        headers.update(extra)
    return headers


class FineTuningSessionClient(FineTuningSessionClientGenerated):  # pylint: disable=client-accepts-api-version-keyword
    """FineTuningSessionClient.

    :ivar sessions: SessionsOperations operations
    :vartype sessions: azure.ai.finetuning_sessions.operations.SessionsOperations
    :ivar training: TrainingOperations operations
    :vartype training: azure.ai.finetuning_sessions.operations.TrainingOperations
    :ivar checkpoints: CheckpointsOperations operations
    :vartype checkpoints: azure.ai.finetuning_sessions.operations.CheckpointsOperations
    :ivar sampling: SamplingOperations operations
    :vartype sampling: azure.ai.finetuning_sessions.operations.SamplingOperations
    :ivar operations: Operations operations
    :vartype operations: azure.ai.finetuning_sessions.operations.Operations
    :param endpoint: Foundry Project endpoint in the form
     "https://{ai-services-account-name}.services.ai.azure.com/api/projects/{project-name}". If you
     only have one Project in your Foundry Hub, or to target the default Project in your Hub, use
     the form "https://{ai-services-account-name}.services.ai.azure.com/api/projects/_project".
     Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """
    def __init__(self, endpoint: str, credential: "TokenCredential", *, allow_insecure_http: bool = False,
                 **kwargs: Any) -> None:
        provided_policies = kwargs.get("policies")
        original_kwargs = dict(kwargs)
        super().__init__(endpoint=endpoint, credential=credential, allow_insecure_http=allow_insecure_http, **original_kwargs)

        _policies = provided_policies
        if _policies is None:
            _policies = [
                policies.RequestIdPolicy(**original_kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**original_kwargs),
                self._config.redirect_policy,
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.custom_hook_policy,
                self._config.logging_policy,
                policies.DistributedTracingPolicy(**original_kwargs),
                policies.SensitiveHeaderCleanupPolicy(**original_kwargs) if self._config.redirect_policy else None,
                self._config.http_logging_policy,
            ]

        self._session_client = PipelineClient(base_url=endpoint, policies=_policies, **original_kwargs)
        self.sessions._client = self._session_client


class FineTuningSession:
    """Convenience wrapper around a single fine-tuning session.

    Mirrors the hero-code surface from SPEC_FOUNDRY_AICLIENT.md so callers
    can write training loops without constructing raw request bodies.

    :param client: The generated ``FineTuningSessionClient``.
    :param session_id: The session ID returned by the server after creating a session.
    """

    def __init__(self, client: "FineTuningSessionClient", session_id: str) -> None:
        self._client = client
        self.session_id = session_id
        # Derive the heartbeat session_id: heartbeat endpoint looks up by
        # "session_xxx" in the sessions table, not "model_xxx".
        raw_id = session_id.removeprefix("model_")
        self._heartbeat_session_id = f"session_{raw_id}"
        self._heartbeat_stop = _threading.Event()
        self._heartbeat_thread: Optional[_threading.Thread] = None
        self._start_heartbeat()

    # ── Background heartbeat ──────────────────────────────────────────────────

    def _start_heartbeat(self, interval_sec: float = 30.0) -> None:
        """Start a daemon thread that sends heartbeat every interval_sec."""
        def _heartbeat_loop() -> None:
            while not self._heartbeat_stop.wait(interval_sec):
                try:
                    self.heartbeat()
                except Exception as exc:
                    _logger.warning("[heartbeat] failed for %s: %s", self._heartbeat_session_id, exc)

        self._heartbeat_thread = _threading.Thread(
            target=_heartbeat_loop, name="fts-heartbeat", daemon=True
        )
        self._heartbeat_thread.start()
        _logger.info("[heartbeat] started (interval=%.0fs, session=%s)", interval_sec, self._heartbeat_session_id)

    def _stop_heartbeat(self) -> None:
        """Stop the background heartbeat thread."""
        self._heartbeat_stop.set()
        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join(timeout=5.0)
            self._heartbeat_thread = None

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        client: "FineTuningSessionClient",
        *,
        base_model: str,
        lora_config: Optional[LoRAConfig] = None,
        type: str = "training",
        from_checkpoint: Optional[FromCheckpoint] = None,
        timeout_sec: float = 600.0,
    ) -> "FineTuningSession":
        """Create a fine-tuning session and wait until the model is loaded.

        Combines ``POST /fine_tuning/sessions`` (which triggers an async model-load
        on the server) with polling of the returned ``request_id`` until the load
        completes, then returns a ready-to-use :class:`FineTuningSession`.

        :param client: The :class:`~azure.ai.finetuning_sessions.FineTuningSessionClient`.
        :param base_model: Name of the base model to load (e.g. ``"Llama-3.1-8B"``).
        :param lora_config: Optional LoRA adapter config. Server default is used if omitted.
        :param type: Session type string. Defaults to ``"training"``.
        :param from_checkpoint: Optional :class:`FromCheckpoint` specifying the
            source session and checkpoint to bootstrap from (continual fine-tuning
            / resume from checkpoint).
        :param timeout_sec: Maximum seconds to wait for the model to load. Defaults to ``600.0``.
        :note: Poll cadence is controlled by an internal adaptive backoff
            (``_RETRIEVE_POLL_MIN`` doubling up to ``_RETRIEVE_POLL_MAX``);
            it is not currently caller-configurable.
        :raises RuntimeError: If the server reports status ``"failed"`` or the timeout expires.
        :return: A :class:`FineTuningSession` instance ready for training operations.
        """
        create_request = CreateSessionRequest(
            type=type,
            base_model=base_model,
            lora_config=lora_config,
        )
        body = _json.loads(_json.dumps(
            create_request,
            cls=_SdkJSONEncoder,
            exclude_readonly=True,
        ))
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
        post_resp = client.send_request(post_req)
        _log_http("response", "POST", "/fine_tuning/sessions", status=post_resp.status_code, body=post_resp.json())
        if post_resp.status_code >= 400:
            try:
                resp_body = post_resp.json()
            except Exception:
                resp_body = None
            typed = _classify_http_error(
                post_resp.status_code, resp_body, response=post_resp
            )
            if typed is not None:
                raise typed
            post_resp.raise_for_status()
        data = post_resp.json()
        raw_session_id: str = data["session_id"]
        request_id: str = data["request_id"]
        _logger.info("[create] POST /fine_tuning/sessions response: raw_session_id=%s, request_id=%s, full_response=%s", raw_session_id, request_id, data)

        # The loom server stores the model record as f"model_{session_id}" (see
        # loom_create_model in the SQL/Cosmos providers).  Every route handler that
        # performs a training operation calls loom_require_model(provider, <url param>)
        # which does loom_get_model(<url param>).  Using the "model_" prefixed form as
        # our session_id means the URL path parameter matches the stored model_id, so
        # the lookup succeeds — no changes required on the server or engine side.
        session_id: str = f"model_{raw_session_id}"
        _logger.info("[create] session_id transformed: raw=%s -> resource_id=%s (used in all subsequent URL paths)", raw_session_id, session_id)

        # Wait for the model-load request to complete.
        # The retrieve-status endpoint (GET /fine_tuning/sessions/{id}/request/{rid})
        # is now non-blocking: each call returns a {status, result, error} envelope
        # immediately. We short-poll until status=="completed" (or "failed")
        # using adaptive backoff (MIN doubling up to MAX) to keep poll RPS bounded
        # for slow model loads while still reacting quickly when ready.
        deadline = _time.monotonic() + timeout_sec
        _create_conn_backoff = 1.0
        _create_poll_backoff = _RETRIEVE_POLL_MIN
        _create_poll_start = _time.monotonic()
        while True:
            try:
                poll_req = _HttpRequest(
                    "GET",
                    "{endpoint}" + f"/fine_tuning/sessions/{session_id}/request/{request_id}",
                    headers=_base_headers(),
                    params={"api-version": _API_VERSION},
                )
                poll_path = f"/fine_tuning/sessions/{session_id}/request/{request_id}"
                _log_http("request", "GET", poll_path)
                poll_resp = client.send_request(poll_req)
                # Parse JSON once — `azure.core.rest` responses do not guarantee
                # the body can be read more than once.
                envelope = poll_resp.json() if poll_resp.status_code == 200 else None
                _log_http("response", "GET", poll_path, status=poll_resp.status_code, body=envelope)

                if poll_resp.status_code == 200:
                    env_status = envelope.get("status")
                    if env_status == "completed":
                        _logger.info("[create] model load completed: %s", envelope)
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
                    # pending -> sleep with adaptive backoff and retry (subject to deadline).
                    if _time.monotonic() > deadline:
                        raise RuntimeError(
                            f"Timed out after {timeout_sec}s waiting for session_id={raw_session_id} to become ready"
                        )
                    elapsed = _time.monotonic() - _create_poll_start
                    _maybe_log_poll_progress(envelope, session_id, request_id, "create_session", elapsed)
                    _create_conn_backoff = 1.0  # reset on successful HTTP exchange
                    _time.sleep(_create_poll_backoff)
                    _create_poll_backoff = min(_create_poll_backoff * 2, _RETRIEVE_POLL_MAX)
                    continue

                # Retry on 5xx and on transient client-side conditions:
                #   408 Request Timeout  -- intermittent network/proxy timeout
                #   429 Too Many Requests -- server-side throttling
                # Both are safe to retry with the same adaptive backoff used
                # for pending polls.
                if (
                    500 <= poll_resp.status_code < 600
                    or poll_resp.status_code in (408, 429)
                ):
                    if _time.monotonic() > deadline:
                        raise RuntimeError(
                            f"Timed out after {timeout_sec}s waiting for session_id={raw_session_id} to become ready"
                        )
                    elapsed = _time.monotonic() - _create_poll_start
                    _logger.debug(
                        "[poller] retry on %s/%s after HTTP %d (%.0fs elapsed)",
                        session_id, request_id, poll_resp.status_code, elapsed,
                    )
                    _create_conn_backoff = 1.0
                    # Honor Retry-After header if present.
                    retry_after = poll_resp.headers.get("Retry-After")
                    if retry_after is not None:
                        try:
                            poll_wait = float(retry_after)
                        except (ValueError, TypeError):
                            poll_wait = _RETRIEVE_POLL_MIN
                    else:
                        poll_wait = _RETRIEVE_POLL_MIN
                    _time.sleep(poll_wait)
                    continue

                # Any other error — fail immediately
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
                # Transient network error — exponential backoff then retry.
                if _time.monotonic() > deadline:
                    raise RuntimeError(
                        f"Timed out after {timeout_sec}s waiting for session_id={raw_session_id} to become ready"
                    ) from exc
                elapsed = _time.monotonic() - _create_poll_start
                _logger.warning(
                    "[poller] retry on %s/%s after %s(%s) (%.0fs elapsed), backoff %.1fs",
                    session_id, request_id, type(exc).__name__, exc, elapsed, _create_conn_backoff,
                )
                _time.sleep(_create_conn_backoff)
                _create_conn_backoff = min(_create_conn_backoff * 2, 30.0)
                continue

        return cls(client, session_id=session_id)

    @classmethod
    def create_from_checkpoint(
        cls,
        client: "FineTuningSessionClient",
        *,
        checkpoint_path: str,
        base_model: str,
        lora_config: Optional[LoRAConfig] = None,
        type: str = "training",
        timeout_sec: float = 600.0,
    ) -> "FineTuningSession":
        """Create a session resumed from a previously saved training checkpoint.

        This is a convenience wrapper around :meth:`create` that parses a
        checkpoint path string and passes it as ``from_checkpoint``.

        The new session's LoRA weights, optimizer state, and scheduler step are
        all bootstrapped from the checkpoint — equivalent to calling ``create``
        with ``from_checkpoint=FromCheckpoint(source_session_id=..., checkpoint_id=...)``.

        :param client: The :class:`~azure.ai.finetuning_sessions.FineTuningSessionClient`.
        :param checkpoint_path: Reference to a saved training checkpoint.
            Accepted formats:
              - ``"<source_session_id>/<checkpoint_name>"``
              - ``"model_<session_id>/<checkpoint_name>"``
        :param base_model: Base model name. Must match the checkpoint's source.
        :param lora_config: Optional LoRA config override.
        :param type: Session type. Defaults to ``"training"``.
        :param timeout_sec: Maximum seconds to wait for model load.
        :raises ValueError: If ``checkpoint_path`` cannot be parsed.
        :return: A ready-to-use :class:`FineTuningSession`.
        """
        parts = checkpoint_path.split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(
                "checkpoint_path must be '<source_session_id>/<checkpoint_name>' with exactly one '/' separator, "
                f"got: {checkpoint_path!r}"
            )
        source_session_id, checkpoint_id = parts
        # Normalize: the API expects the model_ prefix on source_session_id
        if not source_session_id.startswith("model_"):
            source_session_id = f"model_{source_session_id}"
        return cls.create(
            client,
            base_model=base_model,
            lora_config=lora_config,
            type=type,
            from_checkpoint=FromCheckpoint(
                source_session_id=source_session_id,
                checkpoint_id=checkpoint_id,
            ),
            timeout_sec=timeout_sec,
        )

    # ── Low-level helper ──────────────────────────────────────────────────────

    def _post_and_poll(self, subpath: str, body_model: Any, extra_params: Optional[dict] = None, extra_result_fields: Optional[dict] = None) -> OperationResult:
        """POST to a loom action endpoint (returns 200 + request_id), then
        long-poll GET /request/{request_id} until the GPU finishes.

        Loom returns 200 (not 202) with ``{request_id, session_id, status}``
        from all mutating operations.  The poll endpoint blocks server-side
        (up to 5 minutes) and returns the typed result directly.

        Retries 408 / 5xx / transient network errors. The timeout is an ERROR
        budget, not a wall-clock budget — see below. Set
        AZURE_AI_FINETUNING_SESSIONS_OPERATION_TIMEOUT_SEC=0 to disable it.

        Timeout policy — IMPORTANT:
          The budget (``_DEFAULT_OPERATION_TIMEOUT_SEC``, default 3600s) bounds
          how long we tolerate a **sustained error streak**, NOT how long the
          operation may take. It is per operation, not per job.

          * Healthy progress is NOT bounded. While the server keeps returning a
            pending 200 — whether the request is queued waiting for GPU capacity
            or actively in progress — we keep polling indefinitely. A healthy
            poll CLEARS the error budget.
          * Errors ARE bounded. The first 5xx / 408 / 429 / transient network
            error after a healthy poll arms the error deadline
            (``_DEFAULT_OPERATION_TIMEOUT_SEC`` from that moment). Further errors
            do NOT extend it; the next healthy 200 disarms it. If errors persist
            past the budget we raise ``TimeoutError`` so a real backend outage
            fails fast instead of hanging.

          Net effect: a request can sit in the capacity queue for hours without
          being killed, but a stuck/erroring backend is surfaced within the
          budget. Note this means a server that returns healthy-pending forever
          (never completes, never errors) will poll forever — guard against that
          with server-side stall detection, not this client timeout.
        """
        body_json = _json.dumps(body_model, cls=_SdkJSONEncoder, exclude_readonly=True)
        post_params: dict = {"api-version": _API_VERSION}
        if extra_params:
            post_params.update(extra_params)
        post_req = _HttpRequest(
            "POST",
            "{endpoint}" + subpath,
            headers=_base_headers({"Content-Type": "application/json"}),
            params=post_params,
            content=body_json,
        )
        _log_http("request", "POST", subpath, body=_json.loads(body_json))
        post_resp = self._client.send_request(post_req)
        _log_http("response", "POST", subpath, status=post_resp.status_code, body=post_resp.json())
        if post_resp.status_code >= 400:
            try:
                resp_body = post_resp.json()
            except Exception:
                resp_body = None
            typed = _classify_http_error(
                post_resp.status_code, resp_body, response=post_resp, session_id=self.session_id
            )
            if typed is not None:
                raise typed
            post_resp.raise_for_status()
        data = post_resp.json()
        request_id = data["request_id"]
        session_id = data.get("session_id", self.session_id)

        # Long-poll the result directly so we can normalize the Loom wire format
        # before deserializing.  The generated operations.get() passes the raw JSON
        # straight to _deserialize(OperationResult, ...) which expects a "type"
        # discriminator field — but the Loom server returns its own engine format
        # (no "type", metrics under namespaced keys).  We do the GET ourselves,
        # normalize, then deserialize.
        op_type = _LOOM_SUBPATH_TO_OP_TYPE.get(subpath.rsplit("/", 1)[-1], "")
        poll_req = _HttpRequest(
            "GET",
            "{endpoint}" + f"/fine_tuning/sessions/{session_id}/request/{request_id}",
            headers=_base_headers(),
            params={"api-version": _API_VERSION},
        )
        poll_path = f"/fine_tuning/sessions/{session_id}/request/{request_id}"

        # Short-poll the {status, result, error} envelope. The server returns
        # immediately on every call; we sleep with adaptive backoff (MIN doubling
        # up to MAX) between pending polls.
        #
        # Timeout policy: the budget is an ERROR budget, not a wall-clock budget.
        #   * A healthy pending 200 (queued waiting for capacity, or in progress)
        #     does NOT consume the budget — it CLEARS it. So a request can sit in
        #     the capacity queue indefinitely as long as the server keeps
        #     reporting healthy progress.
        #   * The first 5xx / 408 / 429 / transient network error after a healthy
        #     poll ARMS the error deadline (`_DEFAULT_OPERATION_TIMEOUT_SEC` from
        #     now). Subsequent errors do NOT extend it; the next healthy 200
        #     disarms it. If the error streak outlasts the budget we raise
        #     TimeoutError (fail fast on a real outage).
        # Set the env var <= 0 to disable the error budget (retry forever).
        error_budget = _ErrorBudget.for_polling(
            _DEFAULT_OPERATION_TIMEOUT_SEC, op_type=op_type, request_id=request_id
        )

        connection_error_backoff = 1.0
        poll_backoff = _RETRIEVE_POLL_MIN
        result_data: Any = None
        poll_start = _time.monotonic()
        while True:
            try:
                _log_http("request", "GET", poll_path)
                poll_resp = self._client.send_request(poll_req)

                if poll_resp.status_code == 200:
                    envelope = poll_resp.json()
                    _log_http("response", "GET", poll_path, status=200, body=envelope)
                    env_status = envelope.get("status")
                    if env_status == "completed":
                        result_data = envelope.get("result") or {}
                        _clear_poll_log_state(session_id, request_id, op_type)
                        break
                    if env_status == "failed":
                        _clear_poll_log_state(session_id, request_id, op_type)
                        typed = _classify_poll_failure(envelope, session_id=session_id)
                        if typed is not None:
                            raise typed
                        raise RuntimeError(
                            f"Request failed "
                            f"[{envelope.get('error_code') or envelope.get('code') or 'unknown'}]: "
                            f"{envelope.get('error') or 'no error message'} "
                            f"(debug_ref={envelope.get('debug_ref') or 'n/a'})"
                        )
                    # pending -> healthy progress: clear the error budget (queued
                    # / in-progress time is unbounded), then sleep with backoff.
                    elapsed = _time.monotonic() - poll_start
                    _maybe_log_poll_progress(envelope, session_id, request_id, op_type, elapsed)
                    error_budget.clear()
                    connection_error_backoff = 1.0
                    _time.sleep(poll_backoff)
                    poll_backoff = min(poll_backoff * 2, _RETRIEVE_POLL_MAX)
                    continue

                # Retry on 5xx and on transient 408/429 (timeout / throttling).
                if (
                    500 <= poll_resp.status_code < 600
                    or poll_resp.status_code in (408, 429)
                ):
                    elapsed = _time.monotonic() - poll_start
                    _logger.debug(
                        "[poller] retry on %s/%s after HTTP %d (%.0fs elapsed)",
                        session_id, request_id, poll_resp.status_code, elapsed,
                    )
                    error_budget.consume(f"HTTP {poll_resp.status_code}")
                    connection_error_backoff = 1.0
                    # Honor Retry-After header if present.
                    retry_after = poll_resp.headers.get("Retry-After")
                    if retry_after is not None:
                        try:
                            poll_wait = float(retry_after)
                        except (ValueError, TypeError):
                            poll_wait = _RETRIEVE_POLL_MIN
                    else:
                        poll_wait = _RETRIEVE_POLL_MIN
                    _time.sleep(poll_wait)
                    continue

                # Non-retryable HTTP error (4xx other than 408/429).
                _log_http("response", "GET", poll_path, status=poll_resp.status_code, body=None)
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
                # Transient network error — exponential backoff then retry.
                elapsed = _time.monotonic() - poll_start
                _logger.warning(
                    "[poller] retry on %s/%s after %s(%s) (%.0fs elapsed), backoff %.1fs",
                    session_id, request_id, type(exc).__name__, exc, elapsed, connection_error_backoff,
                )
                error_budget.consume(type(exc).__name__)
                _time.sleep(connection_error_backoff)
                connection_error_backoff = min(connection_error_backoff * 2, 30.0)
                continue

        normalized = _normalize_loom_result(result_data, op_type, request_id)
        # Merge caller-supplied fallback fields BEFORE deserialization so that
        # generated model classes receive them (post-deserialization attr
        # assignment doesn't work on SDK objects with __slots__).
        if extra_result_fields:
            for k, v in extra_result_fields.items():
                if not normalized.get(k):  # server value takes precedence
                    normalized[k] = v
        return _deserialize_model(OperationResult, normalized)

    # ── Training ──────────────────────────────────────────────────────────────

    def forward_backward(
        self,
        batch: List[Datum],
        *,
        loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY,
        loss_fn_config: Optional[LossFnConfig] = None,
        **kwargs: Any,
    ) -> OperationResult:
        """Submit a mini-batch for a forward + backward pass.

        If the batch exceeds ``_MAX_CHUNK_LEN`` datums or ``_MAX_CHUNK_BYTES``
        estimated payload size, the batch is automatically split into chunks.
        Chunks are submitted in parallel and results are combined.

        Spec: ``fb_result = session.forward_backward(batch, loss_fn="cross_entropy")``

        :param batch: List of :class:`~azure.ai.finetuning_sessions.models.Datum`.
        :param loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
        :param loss_fn_config: Optional per-loss hyper-parameters.
        :return: :class:`~azure.ai.finetuning_sessions.models.OperationResult`.
        """
        chunks = _chunk_data(batch)
        if len(chunks) <= 1:
            # Single chunk — no combining needed.
            return self._post_and_poll(
                f"/fine_tuning/sessions/{self.session_id}/forward_backward",
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
            len(batch), len(chunks), [len(c) for c in chunks],
        )

        def _submit_chunk(idx_chunk: tuple) -> ForwardBackwardOperationResult:
            i, chunk = idx_chunk
            _logger.info("[forward_backward] sending chunk %d/%d (%d datums)", i + 1, len(chunks), len(chunk))
            result = self._post_and_poll(
                f"/fine_tuning/sessions/{self.session_id}/forward_backward",
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
        # Wall-clock time ≈ max(chunk times) instead of sum.
        with _futures.ThreadPoolExecutor(max_workers=len(chunks)) as pool:
            chunk_results = list(pool.map(_submit_chunk, enumerate(chunks)))

        chunk_sizes = [len(c) for c in chunks]
        return _combine_fwd_bwd_results(chunk_results, chunk_sizes)

    def optim_step(
        self,
        adam_params: AdamParams,
        **kwargs: Any,
    ) -> OperationResult:
        """Apply accumulated gradients with Adam.

        Blocks until the GPU applies the weight update.

        Spec: ``opt_result = session.optim_step(AdamParams(learning_rate=1e-4))``
        """
        return self._post_and_poll(
            f"/fine_tuning/sessions/{self.session_id}/optim_step",
            OptimStepRequest(adam_params=adam_params),
        )

    def forward(
        self,
        batch: List[Datum],
        *,
        loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY,
        loss_fn_config: Optional[LossFnConfig] = None,
        **kwargs: Any,
    ) -> OperationResult:
        """Submit a mini-batch for a forward-only pass (no gradient accumulation).

        Returns the same result shape as ``forward_backward`` but does not
        accumulate gradients on the worker, making it safe for evaluation.

        If the batch exceeds ``_MAX_CHUNK_LEN`` datums or ``_MAX_CHUNK_BYTES``
        estimated payload size, the batch is automatically split into chunks.
        Chunks are submitted in parallel and results are combined.

        :param batch: List of :class:`~azure.ai.finetuning_sessions.models.Datum`.
        :param loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
        :param loss_fn_config: Optional per-loss hyper-parameters.
        :return: :class:`~azure.ai.finetuning_sessions.models.OperationResult`.
        """
        # Server expects a ForwardRequest with `forward_input` wrapping the
        # shared ForwardBackwardInput payload.
        subpath = f"/fine_tuning/sessions/{self.session_id}/forward"

        def _build_body(chunk: List[Datum]) -> dict:
            return {
                "forward_input": ForwardBackwardInput(
                    data=chunk,
                    loss_fn=loss_fn,
                    loss_fn_config=loss_fn_config,
                )
            }

        chunks = _chunk_data(batch)
        if len(chunks) <= 1:
            return self._post_and_poll(subpath, _build_body(batch))

        _logger.info(
            "[forward] batch of %d datums split into %d chunks: %s",
            len(batch), len(chunks), [len(c) for c in chunks],
        )

        def _submit_chunk(idx_chunk: tuple) -> ForwardBackwardOperationResult:
            i, chunk = idx_chunk
            _logger.info("[forward] sending chunk %d/%d (%d datums)", i + 1, len(chunks), len(chunk))
            result = self._post_and_poll(subpath, _build_body(chunk))
            if isinstance(result, ForwardBackwardOperationResult):
                return result
            return ForwardBackwardOperationResult(
                total_loss=getattr(result, "total_loss", 0.0),
                per_datum_logprobs=getattr(result, "per_datum_logprobs", None),
                metrics=getattr(result, "metrics", None),
            )

        with _futures.ThreadPoolExecutor(max_workers=len(chunks)) as pool:
            chunk_results = list(pool.map(_submit_chunk, enumerate(chunks)))

        chunk_sizes = [len(c) for c in chunks]
        return _combine_fwd_bwd_results(chunk_results, chunk_sizes)

    # ── Checkpoints ───────────────────────────────────────────────────────────

    def save_weights(
        self,
        path: str,
        **kwargs: Any,
    ) -> OperationResult:
        """Save a training checkpoint (LoRA weights + optimizer state).

        Blocks until the checkpoint is written to storage.

        Spec: ``ckpt_result = session.save_weights("sft_piglatin_v1")``
        """
        return self._post_and_poll(
            f"/fine_tuning/sessions/{self.session_id}/checkpoint",
            SaveCheckpointRequest(path=path),
        )

    def save_weights_for_sampler(
        self,
        seq_id: int,
        *,
        sampling_session_seq_id: Optional[int] = None,
        path: Optional[str] = None,
        **kwargs: Any,
    ) -> OperationResult:
        """Push current LoRA weights to the sampler (required before calling ``sample``).

        Blocks until the sampler weights are ready.

        Spec: ``sampler_result = session.save_weights_for_sampler(seq_id=step)``

        :param seq_id: Training step index -- must match the ``seq_id`` passed to ``sample``.
        :param sampling_session_seq_id: Ordinal of this sampling session in the run.
        :param path: Optional explicit checkpoint identifier.
        """
        # Compute the checkpoint_id using the same formula the server uses
        # (loom_sampling.py line 270).  The server doesn't echo it back in the
        # poll response, so we inject it before deserialization.
        computed_checkpoint_id = path or f"ss{sampling_session_seq_id}_seq{seq_id}"
        return self._post_and_poll(
            f"/fine_tuning/sessions/{self.session_id}/checkpoint_sample",
            SaveSamplerWeightsRequest(
                seq_id=seq_id,
                sampling_session_seq_id=sampling_session_seq_id,
                path=path,
            ),
            extra_result_fields={"checkpoint_id": computed_checkpoint_id},
        )

    # ── Sampling ──────────────────────────────────────────────────────────────

    def sample(
        self,
        prompt_tokens: List[int],
        sampling_params: SamplingParams,
        *,
        checkpoint_id: str,
        num_samples: int = 1,
        sampling_session_id: Optional[str] = None,
        seq_id: Optional[int] = None,
        prompt_logprobs: bool = False,
        prompt_token_ids: bool = False,
        topk_prompt_logprobs: int = 0,
        **kwargs: Any,
    ) -> OperationResult:
        """Generate completions using current LoRA weights.

        Blocks until the GPU finishes sampling.

        Spec: ``sample_result = session.sample(prompt_tokens, sampling_params, checkpoint_id=..., num_samples=4, ...)``

        :param prompt_tokens: Tokenised input prompt as a list of integer IDs.
        :param sampling_params: Generation parameters (max_tokens, temperature, etc.).
        :param checkpoint_id: Sampler checkpoint ID returned by ``save_weights_for_sampler``.
        :param num_samples: Number of independent completions to generate. Default 1.
        :param sampling_session_id: ID returned by a prior ``save_weights_for_sampler`` call.
        :param seq_id: Training step index; must match the one used in ``save_weights_for_sampler``.
        :param prompt_logprobs: If True, return per-token log-probabilities for the prompt.
        :param prompt_token_ids: If True, return the exact prompt token IDs with the sample result.
        :param topk_prompt_logprobs: Top-k log-probabilities per prompt token. 0 = none.
        """
        return self._post_and_poll(
            f"/fine_tuning/sessions/{self.session_id}/sample",
            SampleRequest(
                num_samples=num_samples,
                prompt=ModelInput(chunks=[ModelInputChunk(tokens=prompt_tokens)]),
                sampling_params=sampling_params,
                topk_prompt_logprobs=topk_prompt_logprobs,
                prompt_token_ids=prompt_token_ids,
                sampling_session_id=sampling_session_id,
                seq_id=seq_id,
                prompt_logprobs=prompt_logprobs,
            ),
            extra_params={"checkpoint_id": checkpoint_id},
        )

    # ── Session lifecycle ─────────────────────────────────────────────────────

    def heartbeat(self, **kwargs: Any) -> Any:
        """Refresh an active session to prevent idle expiry."""
        return self._client.sessions.heartbeat(
            session_id=self._heartbeat_session_id,
            foundry_features=_PREVIEW,
            api_version=_API_VERSION,
            **kwargs,
        )

    def close(self, **kwargs: Any) -> None:
        """Unload the session from the GPU engine.

        Stops the background heartbeat, then issues the complete request.

        Spec: ``session.close()``
        """
        self._stop_heartbeat()
        close_req = _HttpRequest(
            "POST",
            "{endpoint}" + f"/fine_tuning/sessions/{self.session_id}/complete",
            headers=_base_headers(),
            params={"api-version": _API_VERSION},
        )
        resp = self._client.send_request(close_req)
        resp.raise_for_status()


__all__: list[str] = ["FineTuningSession", "FineTuningSessionClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
