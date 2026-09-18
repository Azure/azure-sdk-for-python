# pylint: disable=line-too-long,useless-suppression,too-many-lines
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

Training submissions follow loom's two-step protocol:
  1. POST to the action endpoint — loom returns **200** with
     ``{request_id, session_id, status: "pending"}``.
  2. GET ``/fine_tuning_sessions/{sessionId}/request/{requestId}`` — the server
      returns a ``pending``, ``completed``, or ``failed`` request-status envelope.

Generated operations expose these HTTP 200 accepted-request handles and raw
request-status envelopes. This handwritten layer manually polls request status,
applies retries, and normalizes completed results into SDK convenience models.
"""
from __future__ import annotations

import concurrent.futures as _futures
import json as _json
import logging as _logging
import os as _os
import random as _random
import re as _re
import threading as _threading
import time as _time
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Union
from urllib.request import parse_http_list as _parse_http_list

from azure.core import PipelineClient
from azure.core.exceptions import HttpResponseError as _HttpResponseError
from azure.core.exceptions import ServiceRequestError as _ServiceRequestError
from azure.core.exceptions import ServiceResponseError as _ServiceResponseError
from azure.core.pipeline import policies
from azure.core.rest import HttpRequest as _HttpRequest

from ._client_options import prepare_client_options
from ._exceptions import (
    _classify_http_error,
    _classify_poll_failure,
    RequestRetryableError as _RequestRetryableError,
    BatchTooLargeError,
    ContentionError,
    EngineDeadError,
    FineTuningSessionsError,
    MalformedDatumError,
    NoCapacityError,
    OperationResultUnavailableError,
    RateLimitedError,
    RequestRetryableError,
    RequestValidationError,
    TrainingEngineError,
)
from ._logging_setup import install_default_logging as _install_default_logging

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

if TYPE_CHECKING:
    from azure.core.rest import AsyncHttpResponse, HttpResponse

# ── Loom wire-format → OperationResult discriminator map ─────────────────────
# Maps the last path segment of a Loom action URL to the SDK's "type" value.
# Forward and forward_backward share the same output shape. Forward-only
# responses omit the aggregate training loss.
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
    # Token IDs average about 10 bytes in JSON; image bytes are base64 encoded.
    for chunk in datum.model_input.chunks:
        if hasattr(chunk, "tokens"):
            size += len(chunk.tokens) * 10
        elif hasattr(chunk, "data"):
            size += 4 * ((len(chunk.data) + 2) // 3)
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
        if (len(current) > 0 and current_bytes + est > _MAX_CHUNK_BYTES) or len(current) == _MAX_CHUNK_LEN:
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
                reduction,
                name,
                list(_REDUCE_MAP.keys()),
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
    for prefix in ("prefill", "sample", "training"):
        tokens_key = f"{prefix}_tokens"
        duration_key = f"{prefix}_duration_s"
        throughput_key = f"{prefix}_tokens_per_sec"
        if all(
            tokens_key in (getattr(result, "metrics", None) or {})
            and duration_key in (getattr(result, "metrics", None) or {})
            for result in results
        ):
            tokens = sum((getattr(result, "metrics", None) or {})[tokens_key] for result in results)
            duration = sum((getattr(result, "metrics", None) or {})[duration_key] for result in results)
            res[tokens_key] = tokens
            res[duration_key] = duration
            res[throughput_key] = tokens / duration if duration > 0 and tokens > 0 else None

    cache_key = "prefill_cache_hit_tokens"
    cache_values = [(getattr(result, "metrics", None) or {}).get(cache_key) for result in results]
    if cache_values and all(value is not None for value in cache_values):
        res[cache_key] = sum(cache_values)
    elif any(cache_key in (getattr(result, "metrics", None) or {}) for result in results):
        res[cache_key] = None

    return res


def _combine_fwd_bwd_results(
    results: List[ForwardBackwardOperationResult],
    chunk_sizes: List[int],
) -> ForwardBackwardOperationResult:
    """Combine results from multiple forward_backward chunks."""
    if not results:
        return ForwardBackwardOperationResult(
            total_loss=None,
            loss_fn_output_type=None,
            loss_fn_outputs=[],
        )

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
        lfo = r.loss_fn_outputs
        if lfo:
            combined_lfo.extend(lfo)
    losses = [r.total_loss for r in results]
    total_loss = sum(losses) if all(loss is not None for loss in losses) else None
    combined: dict = {
        "total_loss": total_loss,
        "loss_fn_output_type": next(
            (r.loss_fn_output_type for r in results if r.loss_fn_output_type is not None),
            None,
        ),
        "loss_fn_outputs": combined_lfo or None,
        "per_datum_logprobs": combined_logprobs or None,
        "metrics": combined_metrics or None,
    }
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
        if "total_loss" not in out and "total_loss:sum" in metrics:
            out["total_loss"] = float(metrics["total_loss:sum"])

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


def _canonical_session_id(session_id: str) -> str:
    if session_id.startswith("session_"):
        return session_id
    return f"session_{session_id.removeprefix('model_')}"


def _parse_checkpoint_path(checkpoint_path: str) -> tuple[str, str]:
    if checkpoint_path.startswith("loom://"):
        parts = checkpoint_path.removeprefix("loom://").split("/")
        if len(parts) == 3 and parts[1] == "weights" and parts[0] and parts[2]:
            return _canonical_session_id(parts[0]), parts[2]
    else:
        parts = checkpoint_path.split("/")
        if len(parts) == 2 and parts[0] and parts[1]:
            return _canonical_session_id(parts[0]), parts[1]
    raise ValueError(
        "checkpoint_path must be '<source_session_id>/<checkpoint_name>' or "
        "'loom://<source_session_id>/weights/<checkpoint_name>', "
        f"got: {checkpoint_path!r}"
    )


def _resource_session_id(session_id: str) -> str:
    if session_id.startswith(("session_", "model_")):
        return session_id
    return f"model_{session_id}"


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

#: Maximum automatic resubmits of a request that failed with a retryable
#: (``should_retry``) envelope. Each resubmit uses a NEW request id. Kept small
#: to bound extra load; retries are a safety net for transient, server-signalled
#: failures (pod restarts, read timeouts, ...), not a substitute for capacity.
_MAX_REQUEST_RETRIES = 2

#: Fallback wait before a retryable resubmit when the server did not supply a
#: ``retry_after_sec`` hint.
_DEFAULT_RESUBMIT_WAIT_SEC = 15.0

_PROXY_JWT_RETRY_TIMEOUT_SEC = 120.0


class _BoundedRetryState:
    """Track exponential retry delays within a wall-clock limit."""

    def __init__(
        self,
        *,
        limit_sec: float,
        base_delay_sec: float,
        max_delay_sec: float,
    ) -> None:
        self._started_at = _time.monotonic()
        self.limit_sec = limit_sec
        self.base_delay_sec = base_delay_sec
        self.max_delay_sec = max_delay_sec
        self.attempts = 0
        self.elapsed = 0.0

    def next_delay(self) -> Optional[float]:
        """Return the next delay, or None when the limit is exhausted."""
        self.elapsed = _time.monotonic() - self._started_at
        if self.elapsed >= self.limit_sec:
            return None
        self.attempts += 1
        return min(
            self.base_delay_sec * (2 ** (self.attempts - 1)),
            self.max_delay_sec,
            self.limit_sec - self.elapsed,
        )


def _is_proxy_jwt_rejection(response: Union["HttpResponse", "AsyncHttpResponse"]) -> bool:
    """Match Envoy's local JWT rejection, not an application's auth failure."""
    if response.status_code != 401:
        return False
    headers = {name.lower(): value for name, value in response.headers.items()}
    if headers.get("server", "").lower() != "istio-envoy":
        return False
    challenge = headers.get("www-authenticate", "")
    if not _re.fullmatch(r'(?:[^"\\\r\n]|"(?:[^"\\\r\n]|\\[^\r\n])*")*', challenge):
        return False
    if not any(
        _re.fullmatch(
            r'(?:Bearer[ \t]+)?error[ \t]*=[ \t]*"invalid_token"',
            parameter,
            _re.IGNORECASE,
        )
        for parameter in _parse_http_list(challenge)
    ):
        return False
    try:
        body = response.json()
    except ValueError:
        return response.text().strip() == "Jwt verification fails"
    if not isinstance(body, dict):
        return False
    error = body.get("error", body)
    return isinstance(error, dict) and error.get("message") == "Jwt verification fails"


class _ProxyJwtRetryState:
    """Track the deadline and backoff for proxy JWT rejections."""

    def __init__(self) -> None:
        self._deadline: Optional[float] = None
        self._delay = 1.0

    def update_and_get_delay(
        self,
        response: Union["HttpResponse", "AsyncHttpResponse"],
        *,
        method: str,
        path: str,
    ) -> Optional[float]:
        """Update JWT retry state; return seconds to wait, or None for normal handling."""
        if response.status_code == 200:
            self._deadline = None
            self._delay = 1.0
            return None
        if not _is_proxy_jwt_rejection(response):
            return None

        now = _time.monotonic()
        if self._deadline is None:
            self._deadline = now + _PROXY_JWT_RETRY_TIMEOUT_SEC
        remaining = self._deadline - now
        apim_request_id = response.headers.get("apim-request-id", "n/a")
        if remaining <= 0:
            _logger.warning(
                "[proxy-jwt] %s %s retry window exhausted (apim_request_id=%s)",
                method,
                path,
                apim_request_id,
            )
            return None

        wait = min(self._delay * (1 + 0.25 * _random.random()), remaining)
        _logger.warning(
            "[proxy-jwt] %s %s rejected before application; retry in %.1fs " "(apim_request_id=%s)",
            method,
            path,
            wait,
            apim_request_id,
        )
        self._delay = min(self._delay * 2, 10.0)
        return wait


def _retryable_resubmit_wait(retry_after_sec: Optional[float]) -> float:
    """Wait (seconds) before resubmitting a ``should_retry`` failure.

    Honors the server's ``retry_after_sec`` hint (falling back to a default),
    then adds up to 25% jitter so a fleet of simultaneously-failed
    requests doesn't stampede the rate limiter on the same tick.
    """
    base = retry_after_sec if retry_after_sec and retry_after_sec > 0 else _DEFAULT_RESUBMIT_WAIT_SEC
    return base * (1 + 0.25 * _random.random())


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


#: Lifecycle-scoped sampling concurrency limit. Unlike ``_post_semaphore`` (which
#: only bounds the in-flight POST), this permit is held across the FULL sample
#: submit+poll lifecycle so a throttled or slow-generating sample does not
#: release capacity to a burst queued behind it.
_MAX_CONCURRENT_SAMPLES = 400

#: Wall-clock cap on the sample admission (429) phase. A throttled sample submit
#: is retried in place — honoring ``Retry-After`` + jitter — until this deadline,
#: then a typed ``RateLimitedError`` is raised.
_SAMPLE_THROTTLE_TIMEOUT_SEC = 3 * 60 * 60  # 3 hours


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


def _resolve_poll_warn_sec() -> float:
    """Seconds a single request may stay pending before INFO poll logs escalate
    to WARNING. A long-pending request is usually a healthy-but-slow op (e.g. a
    cold inference fleet warming a large base model), but it is also the first
    visible symptom of a wedged run -- a WARNING makes it stand out instead of
    being buried in INFO. Override via LOOM_POLL_WARN_SEC; <= 0 disables
    escalation. Default 600s (10 min)."""
    raw = _os.environ.get("LOOM_POLL_WARN_SEC")
    if raw is None:
        return 600.0
    try:
        return float(raw)
    except ValueError:
        _logger.warning("Invalid LOOM_POLL_WARN_SEC=%r; using default 600s", raw)
        return 600.0


_POLL_WARN_SEC = _resolve_poll_warn_sec()
# Warnings re-fire at most once per this interval per (session, op, request) so a
# single genuinely-stuck request does not spam the log every poll cycle. Keying
# on request_id (not just op) means a short request of the same op completing
# cannot reset a long-pending request's dedup window, and every distinct stuck
# request stays individually visible.
_POLL_WARN_DEDUP_SEC = 300.0
_poll_warn_last: dict[tuple[str, str, str], float] = {}


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

    dedup_key = (session_id, op_type)
    warn_key = (session_id, op_type, request_id)

    # Escalate to WARNING once a request has been pending past the warn
    # threshold. Tracked per-request on a separate, slower dedup so it surfaces
    # even when the INFO line was recently emitted, without spamming, and so a
    # sibling request of the same op completing cannot reset this window.
    if (
        not is_queued
        and _POLL_WARN_SEC > 0
        and display_elapsed >= _POLL_WARN_SEC
        and now - _poll_warn_last.get(warn_key, 0.0) >= _POLL_WARN_DEDUP_SEC
    ):
        _poll_warn_last[warn_key] = now
        _poll_log_last[dedup_key] = now
        _logger.warning(
            "[poller] %s/%s (op=%s) still pending after %.0fs (%.1f min) \u2014 likely a "
            "slow/cold inference fleet; if it never clears the run may be wedged.",
            session_id,
            request_id,
            op_type,
            display_elapsed,
            display_elapsed / 60.0,
        )
        return

    if display_elapsed < _POLL_LOG_DEDUP_SEC:
        return
    if now - _poll_log_last.get(dedup_key, 0.0) < _POLL_LOG_DEDUP_SEC:
        return
    _poll_log_last[dedup_key] = now
    if is_queued:
        _logger.info(
            "[poller] %s/%s (op=%s) queued waiting for capacity \u2014 %.0fs elapsed",
            session_id,
            request_id,
            op_type,
            display_elapsed,
        )
    else:
        _logger.info(
            "[poller] %s/%s (op=%s) in progress \u2014 %.0fs elapsed",
            session_id,
            request_id,
            op_type,
            display_elapsed,
        )


def _clear_poll_log_state(session_id: str, request_id: str, op_type: str) -> None:
    """Drop poll-progress state for a finished request."""
    _request_active_since.pop((session_id, request_id), None)
    _poll_log_last.pop((session_id, op_type), None)
    _poll_warn_last.pop((session_id, op_type, request_id), None)


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


#: Headers Loom reads off every request, and the env var each is sourced from on
#: the direct (non-APIM) path. Derived mechanically from what ``loom_api`` reads:
#:   grep -rhno "headers\.get([^)]*)" --include=*.py loom_api/src/
#: Keep this list in sync with docs/command-job-direct-loom-api-design.md.
_DIRECT_PATH_HEADER_ENV: tuple[tuple[str, str], ...] = (
    # Parsed by loom_api's worker_affinity as a Cognitive Services ARM path.
    # Absent -> affinity silently resolves to the GENERAL worker pool.
    ("azure-resource-id", "LOOM_AZURE_RESOURCE_ID"),
    # Populates TenantContext.tenant_id, which drives ECS allow-list gating.
    # Absent -> tenant-gated features silently evaluate as ungated.
    ("azure-resource-tenant-id", "LOOM_AZURE_RESOURCE_TENANT_ID"),
    # Region. HARD 400 on create-session once checkpoint_cmk_storage_enabled is
    # on; also feeds training-SKU / datazone validation.
    ("azure-resource-location", "LOOM_AZURE_RESOURCE_LOCATION"),
    # Workspace metadata used for checkpoint registration.
    ("X-Workspace-Resource-Id", "LOOM_WORKSPACE_RESOURCE_ID"),
)


def _base_headers(extra: Optional[dict] = None) -> dict:
    """Build the common headers for every Loom request.

    Loom derives the caller's identity entirely from headers -- it performs no
    token validation on these values. On the APIM path APIM injects them. On the
    direct path (command job -> regional ``loom_api``, used when the customer's
    Foundry resource sits in their VNet) there is no APIM in between, so the
    caller must supply the same set itself.

    Every header is read from the environment and sent only when present, which
    keeps the APIM path byte-for-byte unchanged.

    ``apim-subscription-id`` is the identity: ``ApiAccessControlMiddleware``
    resolves it to the caller's API-ring scopes and model allowlist, and
    ``LOOM_SETUP_MODE=prod`` returns ``401`` when it is absent. Read from
    ``X_COGNITIVE_SUBSCRIPTION_ID`` (or ``COGNITIVE_SUBSCRIPTION_ID`` /
    ``AZURE_SUBSCRIPTION_ID`` as fallbacks) -- same as ``clean_remote.sh``,
    which sets ``X_COGNITIVE_SUBSCRIPTION_ID=local-sub``.

    The rest are listed in :data:`_DIRECT_PATH_HEADER_ENV`. Only
    ``azure-resource-location`` fails loudly; the others degrade silently, which
    is why they are plumbed explicitly rather than left to chance.
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

    for header_name, env_var in _DIRECT_PATH_HEADER_ENV:
        value = _os.environ.get(env_var)
        if value:
            headers[header_name] = value

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

    def __init__(
        self, endpoint: str, credential: "TokenCredential", *, allow_insecure_http: bool = False, **kwargs: Any
    ) -> None:
        kwargs = prepare_client_options(endpoint, credential, allow_insecure_http=allow_insecure_http, **kwargs)
        provided_policies = kwargs.get("policies")
        original_kwargs = dict(kwargs)
        super().__init__(endpoint=endpoint, credential=credential, **original_kwargs)
        self._config.allow_insecure_http = allow_insecure_http

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
        # Lifecycle-scoped semaphore bounding concurrent sample() calls across
        # their full submit+poll lifecycle (shared by all sessions on this client).
        self._sample_semaphore = _threading.BoundedSemaphore(_MAX_CONCURRENT_SAMPLES)


class FineTuningSession:
    """Convenience wrapper around a single fine-tuning session.

    Mirrors the hero-code surface from SPEC_FOUNDRY_AICLIENT.md so callers
    can write training loops without constructing raw request bodies.

    :param client: The generated ``FineTuningSessionClient``.
    :param session_id: The session ID returned by the server after creating a session.
    """

    def __init__(
        self,
        client: "FineTuningSessionClient",
        session_id: str,
    ) -> None:
        self._client = client
        self.session_id = _canonical_session_id(session_id)
        self._resource_session_id = _resource_session_id(session_id)
        self._heartbeat_session_id = self.session_id
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

        self._heartbeat_thread = _threading.Thread(target=_heartbeat_loop, name="fts-heartbeat", daemon=True)
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
        user_metadata: Optional[dict[str, Any]] = None,
        training_type: Optional[str] = None,
    ) -> "FineTuningSession":
        """Create a fine-tuning session and wait until the model is loaded.

        Combines ``POST /fine_tuning_sessions`` (which triggers an async model-load
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
        :param training_type: Training SKU type: ``"GlobalStandard"`` (default),
            ``"DatazoneStandard"``, or ``"DeveloperTier"``.
        :note: Poll cadence is controlled by an internal adaptive backoff
            (``_RETRIEVE_POLL_MIN`` doubling up to ``_RETRIEVE_POLL_MAX``);
            it is not currently caller-configurable.
        :raises RuntimeError: If the server reports status ``"failed"`` or the timeout expires.
        :return: A :class:`FineTuningSession` instance ready for training operations.
        """
        create_request = CreateSessionRequest(
            type=type,
            base_model=base_model,
            lora_config=lora_config if lora_config is not None else LoRAConfig(),
            user_metadata=user_metadata,
            training_type=training_type,
        )
        body = _json.loads(
            _json.dumps(
                create_request,
                cls=_SdkJSONEncoder,
                exclude_readonly=True,
            )
        )
        if from_checkpoint is not None:
            body["from_checkpoint"] = _json.loads(
                _json.dumps(from_checkpoint, cls=_SdkJSONEncoder, exclude_readonly=True)
            )
            body["from_checkpoint"]["source_session_id"] = _canonical_session_id(
                body["from_checkpoint"]["source_session_id"]
            )
        body_json = _json.dumps(body)
        post_req = _HttpRequest(
            "POST",
            "{endpoint}/fine_tuning_sessions",
            headers=_base_headers({"Content-Type": "application/json"}),
            params={"api-version": _API_VERSION},
            content=body_json,
        )
        _log_http("request", "POST", "/fine_tuning_sessions", body=_json.loads(body_json))
        post_resp = client.send_request(post_req)
        _log_http("response", "POST", "/fine_tuning_sessions", status=post_resp.status_code, body=post_resp.json())
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
            "[create] POST /fine_tuning_sessions response: raw_session_id=%s, request_id=%s, full_response=%s",
            raw_session_id,
            request_id,
            data,
        )

        session_id = _canonical_session_id(raw_session_id)
        resource_session_id = _resource_session_id(raw_session_id)
        _logger.info(
            "[create] session_id normalized: raw=%s -> session_id=%s, resource_session_id=%s",
            raw_session_id,
            session_id,
            resource_session_id,
        )

        # Wait for the model-load request to complete.
        # The retrieve-status endpoint (GET /fine_tuning_sessions/{id}/request/{rid})
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
                    "{endpoint}" + f"/fine_tuning_sessions/{resource_session_id}/request/{request_id}",
                    headers=_base_headers(),
                    params={"api-version": _API_VERSION},
                )
                poll_path = f"/fine_tuning_sessions/{resource_session_id}/request/{request_id}"
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
                if 500 <= poll_resp.status_code < 600 or poll_resp.status_code in (408, 429):
                    if _time.monotonic() > deadline:
                        raise RuntimeError(
                            f"Timed out after {timeout_sec}s waiting for session_id={raw_session_id} to become ready"
                        )
                    elapsed = _time.monotonic() - _create_poll_start
                    _logger.debug(
                        "[poller] retry on %s/%s after HTTP %d (%.0fs elapsed)",
                        session_id,
                        request_id,
                        poll_resp.status_code,
                        elapsed,
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
                    session_id,
                    request_id,
                    type(exc).__name__,
                    exc,
                    elapsed,
                    _create_conn_backoff,
                )
                _time.sleep(_create_conn_backoff)
                _create_conn_backoff = min(_create_conn_backoff * 2, 30.0)
                continue

        return cls(
            client,
            session_id=resource_session_id,
        )

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
                            - ``"loom://<source_session_id>/weights/<checkpoint_name>"``
        :param base_model: Base model name. Must match the checkpoint's source.
        :param lora_config: Optional LoRA config override.
        :param type: Session type. Defaults to ``"training"``.
        :param timeout_sec: Maximum seconds to wait for model load.
        :raises ValueError: If ``checkpoint_path`` cannot be parsed.
        :return: A ready-to-use :class:`FineTuningSession`.
        """
        source_session_id, checkpoint_id = _parse_checkpoint_path(checkpoint_path)
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

    def _submit(self, post_req: "_HttpRequest", subpath: str):
        """Issue the submit POST and return the raw response.

        For a ``/sample`` request a ``429`` is healthy backpressure, not a fault:
        retry the submit in place (honoring ``Retry-After`` + jitter, clamped to
        the remaining budget) until ``_SAMPLE_THROTTLE_TIMEOUT_SEC``, then return
        the final 429 so the caller classifies it as ``RateLimitedError``.
        Sample submissions also retry the known pre-application Envoy JWT
        rejection within a separate bounded window. Other requests are a single send.
        """
        if not subpath.endswith("/sample"):
            return self._client.send_request(post_req)
        start = _time.monotonic()
        jwt_retry_state = _ProxyJwtRetryState()
        while True:
            resp = self._client.send_request(post_req)
            retry_wait = jwt_retry_state.update_and_get_delay(resp, method="POST", path=subpath)
            if retry_wait is not None:
                _time.sleep(retry_wait)
                continue
            if resp.status_code != 429:
                return resp
            elapsed = _time.monotonic() - start
            if elapsed >= _SAMPLE_THROTTLE_TIMEOUT_SEC:
                _logger.warning(
                    "POST %s throttled (429) for %.0fs >= cap %.0fs; giving up",
                    subpath,
                    elapsed,
                    _SAMPLE_THROTTLE_TIMEOUT_SEC,
                )
                return resp
            retry_after = resp.headers.get("Retry-After")
            try:
                wait = float(retry_after) if retry_after is not None else _RETRIEVE_POLL_MIN
            except (ValueError, TypeError):
                wait = _RETRIEVE_POLL_MIN
            wait *= 1 - 0.25 * _random.random()  # jitter
            # Clamp to the remaining budget so a large Retry-After can never push
            # the wall-clock cap out; the next iteration then crosses the deadline.
            # Guaranteed > 0 (elapsed < cap here).
            wait = min(wait, _SAMPLE_THROTTLE_TIMEOUT_SEC - elapsed)
            _logger.warning(
                "POST %s throttled (429), retry in %.1fs (%.0fs/%.0fs)",
                subpath,
                wait,
                elapsed,
                _SAMPLE_THROTTLE_TIMEOUT_SEC,
            )
            _time.sleep(wait)

    def _post_and_poll(
        self,
        subpath: str,
        body_model: Any,
        extra_params: Optional[dict] = None,
        extra_result_fields: Optional[dict] = None,
    ) -> OperationResult:
        """POST-then-poll with bounded resubmit on retryable failures.

        Wraps :meth:`_post_and_poll_once`. When the server marks a failed
        request retryable (``should_retry`` → ``RequestRetryableError`` — e.g. a
        drained/restarted pod, an orphan-sweep reclaim, or an upstream read
        timeout), resubmit with a **fresh request id**, up to
        ``_MAX_REQUEST_RETRIES`` times, honoring the server's ``retry_after_sec``
        hint with jitter. Retry is driven purely by the server's ``should_retry``
        signal — the SDK does not gate on operation type or error code — so the
        server is responsible for only setting the flag on recoverable failures.
        """
        attempt = 0
        timeline: dict[str, Optional[float]] = {
            "operation_started_at": _time.monotonic(),
            "poll_started_at": None,
        }
        while True:
            try:
                return self._post_and_poll_once(
                    subpath,
                    body_model,
                    extra_params,
                    extra_result_fields,
                    timeline,
                )
            except _RequestRetryableError as exc:
                if attempt >= _MAX_REQUEST_RETRIES:
                    raise
                attempt += 1
                wait = _retryable_resubmit_wait(exc.retry_after_sec)
                _logger.warning(
                    "[resubmit] %s failed retryably [%s]; resubmit %d/%d in %.1fs",
                    subpath,
                    exc.error_code or "unknown",
                    attempt,
                    _MAX_REQUEST_RETRIES,
                    wait,
                )
                _time.sleep(wait)

    def _post_and_poll_once(
        self,
        subpath: str,
        body_model: Any,
        extra_params: Optional[dict] = None,
        extra_result_fields: Optional[dict] = None,
        timeline: Optional[dict[str, Optional[float]]] = None,
    ) -> OperationResult:
        """POST to a loom action endpoint (returns 200 + request_id), then
        poll GET /request/{request_id} until the GPU finishes.

        Loom returns HTTP 200 with an accepted-request handle containing
        ``{request_id, session_id, status}``. The poll endpoint returns a
        request-status envelope; completed results are normalized below.

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
        resource_session_id = getattr(
            self,
            "_resource_session_id",
            self.session_id,
        )
        subpath = subpath.replace(
            f"/fine_tuning_sessions/{self.session_id}",
            f"/fine_tuning_sessions/{resource_session_id}",
            1,
        )
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
        op_type = _LOOM_SUBPATH_TO_OP_TYPE.get(subpath.rsplit("/", 1)[-1], "")
        submit_started = _time.monotonic()
        _logger.info(
            "[operation_timeline] submit_started session_id=%s op=%s path=%s",
            self.session_id,
            op_type,
            subpath,
        )
        _log_http("request", "POST", subpath, body=_json.loads(body_json))
        post_resp = self._submit(post_req, subpath)
        if post_resp.status_code >= 400:
            try:
                resp_body = post_resp.json()
            except Exception:
                resp_body = None
            _log_http("response", "POST", subpath, status=post_resp.status_code, body=resp_body)
            typed = _classify_http_error(
                post_resp.status_code, resp_body, response=post_resp, session_id=self.session_id
            )
            if typed is not None:
                raise typed
            post_resp.raise_for_status()
        data = post_resp.json()
        _log_http("response", "POST", subpath, status=post_resp.status_code, body=data)
        request_id = data["request_id"]
        session_id = _resource_session_id(data.get("session_id", resource_session_id))
        _logger.info(
            "[operation_timeline] submit_completed session_id=%s request_id=%s " "op=%s elapsed_ms=%.1f",
            session_id,
            request_id,
            op_type,
            (_time.monotonic() - submit_started) * 1000.0,
        )

        # Poll the raw request-status envelope directly so we can apply retries
        # and normalize the completed result's Loom wire format into the
        # discriminated SDK OperationResult convenience model.
        poll_req = _HttpRequest(
            "GET",
            "{endpoint}" + f"/fine_tuning_sessions/{session_id}/request/{request_id}",
            headers=_base_headers(),
            params={"api-version": _API_VERSION},
        )
        poll_path = f"/fine_tuning_sessions/{session_id}/request/{request_id}"

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
        error_budget = _ErrorBudget.for_polling(_DEFAULT_OPERATION_TIMEOUT_SEC, op_type=op_type, request_id=request_id)

        connection_error_backoff = 1.0
        poll_backoff = _RETRIEVE_POLL_MIN
        result_data: Any = None
        if timeline is None:
            timeline = {
                "operation_started_at": submit_started,
                "poll_started_at": None,
            }
        if timeline["poll_started_at"] is None:
            timeline["poll_started_at"] = _time.monotonic()
        poll_start = timeline["poll_started_at"]
        assert poll_start is not None
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
                _log_http("request", "GET", poll_path)
                poll_resp = self._client.send_request(poll_req)
                retry_wait = jwt_retry_state.update_and_get_delay(
                    poll_resp,
                    method="GET",
                    path=poll_path,
                )
                if retry_wait is not None:
                    _time.sleep(retry_wait)
                    continue

                if poll_resp.status_code == 200:
                    envelope = poll_resp.json()
                    _log_http("response", "GET", poll_path, status=200, body=envelope)
                    env_status = envelope.get("status")
                    if env_status == "completed":
                        result_data = envelope.get("result") or {}
                        _clear_poll_log_state(session_id, request_id, op_type)
                        consumed_at = _time.monotonic()
                        operation_started_at = timeline["operation_started_at"]
                        operation_elapsed_ms = (
                            (consumed_at - operation_started_at) * 1000.0
                            if operation_started_at is not None
                            else (consumed_at - poll_start) * 1000.0
                        )
                        _logger.info(
                            "[operation_timeline] result_consumed session_id=%s request_id=%s "
                            "op=%s poll_attempts=%d elapsed_ms=%.1f poll_elapsed_ms=%.1f",
                            session_id,
                            request_id,
                            op_type,
                            poll_attempts,
                            operation_elapsed_ms,
                            (consumed_at - poll_start) * 1000.0,
                        )
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

                if poll_resp.status_code == 404:
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
                        _time.sleep(wait)
                        continue

                # Retry on 5xx and on transient 408/429 (timeout / throttling).
                if 500 <= poll_resp.status_code < 600 or poll_resp.status_code in (408, 429):
                    elapsed = _time.monotonic() - poll_start
                    _logger.debug(
                        "[poller] retry on %s/%s after HTTP %d (%.0fs elapsed)",
                        session_id,
                        request_id,
                        poll_resp.status_code,
                        elapsed,
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
                    session_id,
                    request_id,
                    type(exc).__name__,
                    exc,
                    elapsed,
                    connection_error_backoff,
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
                f"/fine_tuning_sessions/{self.session_id}/forward_backward",
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

        def _submit_chunk(idx_chunk: tuple) -> ForwardBackwardOperationResult:
            i, chunk = idx_chunk
            _logger.info("[forward_backward] sending chunk %d/%d (%d datums)", i + 1, len(chunks), len(chunk))
            result = self._post_and_poll(
                f"/fine_tuning_sessions/{self.session_id}/forward_backward",
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
            f"/fine_tuning_sessions/{self.session_id}/optim_step",
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

        Returns per-datum loss-function outputs without accumulating gradients.
        ``total_loss`` is a training-only field and is None on this result.

        If the batch exceeds ``_MAX_CHUNK_LEN`` datums or ``_MAX_CHUNK_BYTES``
        estimated payload size, the batch is automatically split into chunks.
        Chunks are submitted in parallel and results are combined.

        :param batch: List of :class:`~azure.ai.finetuning_sessions.models.Datum`.
        :param loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
        :param loss_fn_config: Optional per-loss hyper-parameters.
        :return: :class:`~azure.ai.finetuning_sessions.models.ForwardBackwardOperationResult`.
        """
        # Server expects a ForwardRequest with `forward_input` wrapping the
        # shared ForwardBackwardInput payload.
        subpath = f"/fine_tuning_sessions/{self.session_id}/forward"

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
            len(batch),
            len(chunks),
            [len(c) for c in chunks],
        )

        def _submit_chunk(idx_chunk: tuple) -> ForwardBackwardOperationResult:
            i, chunk = idx_chunk
            _logger.info("[forward] sending chunk %d/%d (%d datums)", i + 1, len(chunks), len(chunk))
            result = self._post_and_poll(subpath, _build_body(chunk))
            if isinstance(result, ForwardBackwardOperationResult):
                return result
            return ForwardBackwardOperationResult(
                total_loss=getattr(result, "total_loss", None),
                loss_fn_output_type=getattr(result, "loss_fn_output_type", None),
                loss_fn_outputs=getattr(result, "loss_fn_outputs", None),
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
            f"/fine_tuning_sessions/{self.session_id}/checkpoint",
            SaveCheckpointRequest(path=path),
            extra_result_fields={"checkpoint_id": path},
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
            f"/fine_tuning_sessions/{self.session_id}/checkpoint_sample",
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
        prompt_tokens: List[int] | ModelInput,
        sampling_params: SamplingParams,
        *,
        checkpoint_id: str,
        num_samples: int = 1,
        sampling_session_id: Optional[str] = None,
        seq_id: Optional[int] = None,
        prompt_logprobs: bool = False,
        topk_prompt_logprobs: int = 0,
        **kwargs: Any,
    ) -> OperationResult:
        """Generate completions using current LoRA weights.

        Blocks until the GPU finishes sampling.

        Spec: ``sample_result = session.sample(prompt_tokens, sampling_params, checkpoint_id=..., num_samples=4, ...)``

        :param prompt_tokens: Tokenised input prompt as a list of integer IDs, or a
            structured ``ModelInput`` for multimodal prompts.
        :param sampling_params: Generation parameters (max_tokens, temperature, etc.).
        :param checkpoint_id: Sampler checkpoint ID returned by ``save_weights_for_sampler``.
        :param num_samples: Number of independent completions to generate. Default 1.
        :param sampling_session_id: ID returned by a prior ``save_weights_for_sampler`` call.
        :param seq_id: Training step index; must match the one used in ``save_weights_for_sampler``.
        :param prompt_logprobs: If True, return per-token log-probabilities for the prompt.
        :param topk_prompt_logprobs: Top-k log-probabilities per prompt token. 0 = none. Must be between 0 and 20 (default 20).

        Concurrency is bounded by a lifecycle-scoped semaphore (size
        ``_MAX_CONCURRENT_SAMPLES``). The permit is held for the FULL submit+poll
        lifecycle so a throttled or slow-generating sample does not release
        capacity to a burst queued behind it. A 429 on submit is treated as
        healthy backpressure and retried in place — honoring ``Retry-After`` +
        jitter — until ``_SAMPLE_THROTTLE_TIMEOUT_SEC``, then a typed
        ``RateLimitedError`` is raised.
        """
        with self._client._sample_semaphore:
            return self._post_and_poll(
                f"/fine_tuning_sessions/{self.session_id}/sample",
                SampleRequest(
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
                ),
                extra_params={"checkpoint_id": checkpoint_id},
            )

    # ── Session lifecycle ─────────────────────────────────────────────────────

    def heartbeat(self, **kwargs: Any) -> Any:
        """Refresh an active session to prevent idle expiry."""
        return self._client.sessions.heartbeat(
            session_id=self._resource_session_id,
            foundry_features=_PREVIEW,
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
            "{endpoint}" + f"/fine_tuning_sessions/{self._resource_session_id}/complete",
            headers=_base_headers(),
            params={"api-version": _API_VERSION},
        )
        resp = self._client.send_request(close_req)
        resp.raise_for_status()

    def delete(self, **kwargs: Any) -> None:
        """Delete the session and cascade-delete its models, checkpoints, and sampling sessions.

        Stops the background heartbeat, then issues an HTTP DELETE against
        the session resource; the cascade is performed server-side.

        Idempotent — a 404 (session already gone) is swallowed.  Any other
        non-2xx surfaces via the standard SDK error path.

        Spec: ``session.delete()``
        """
        self._stop_heartbeat()
        del_req = _HttpRequest(
            "DELETE",
            "{endpoint}" + f"/fine_tuning_sessions/{self._resource_session_id}",
            headers=_base_headers(),
            params={"api-version": _API_VERSION},
        )
        resp = self._client.send_request(del_req)
        if resp.status_code == 404:
            # Already gone — treat as success.
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


__all__: list[str] = [
    "FineTuningSession",
    "FineTuningSessionClient",
    "FineTuningSessionsError",
    "BatchTooLargeError",
    "ContentionError",
    "EngineDeadError",
    "MalformedDatumError",
    "NoCapacityError",
    "OperationResultUnavailableError",
    "RateLimitedError",
    "RequestRetryableError",
    "RequestValidationError",
    "TrainingEngineError",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    _install_default_logging()
