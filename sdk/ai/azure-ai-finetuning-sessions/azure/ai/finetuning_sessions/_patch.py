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

import json as _json
import logging as _logging
import os as _os
import threading as _threading
import time as _time
from typing import TYPE_CHECKING, Any, List, Optional, Union

from azure.core.rest import HttpRequest as _HttpRequest

from .models import (
    AdamParams,
    CreateSessionRequest,
    Datum,
    ForwardBackwardInput,
    ForwardBackwardRequest,
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
from ._utils.model_base import SdkJSONEncoder as _SdkJSONEncoder, _deserialize as _deserialize_model

# ── Loom wire-format → OperationResult discriminator map ─────────────────────
# Maps the last path segment of a Loom action URL to the SDK's "type" value.
_LOOM_SUBPATH_TO_OP_TYPE: dict[str, str] = {
    "forward_backward": "forward_backward",
    "optim_step": "optim_step",
    "checkpoint": "save_checkpoint",
    "checkpoint_sample": "save_sampler_weights",
    "sample": "sample",
}


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
        out.setdefault("checkpoint_id", out.get("checkpoint_id", ""))
        out.setdefault("path", out.get("path", ""))

    return out

if TYPE_CHECKING:
    from ._client import FineTuningSessionClient

_PREVIEW = FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW
_API_VERSION = "v1"
_logger = _logging.getLogger(__name__)

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
    requires this header on every request — same as ``loom_client`` and
    ``clean_remote.sh`` which set ``X_COGNITIVE_SUBSCRIPTION_ID=local-sub``.
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
                    hb_req = _HttpRequest(
                        "POST",
                        "{endpoint}" + f"/fine_tuning/sessions/{self._heartbeat_session_id}/heartbeat",
                        headers=_base_headers(),
                        params={"api-version": _API_VERSION},
                    )
                    resp = self._client.send_request(hb_req)
                    if resp.status_code != 200:
                        _logger.warning("[heartbeat] status=%d for %s", resp.status_code, self._heartbeat_session_id)
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
        poll_interval_sec: float = 5.0,
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
        :param poll_interval_sec: Seconds between poll attempts. Defaults to ``5.0``.
        :param timeout_sec: Maximum seconds to wait for the model to load. Defaults to ``600.0``.
        :raises RuntimeError: If the server reports status ``"failed"`` or the timeout expires.
        :return: A :class:`FineTuningSession` instance ready for training operations.
        """
        body_json = _json.dumps(
            CreateSessionRequest(type=type, base_model=base_model, lora_config=lora_config),
            cls=_SdkJSONEncoder,
            exclude_readonly=True,
        )
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
        # The retrieve-future endpoint (GET /fine_tuning/sessions/{id}/request/{rid})
        # long-polls server-side for up to 5 minutes.  A 200 response means the
        # request completed successfully — the server only returns 200 when the
        # engine has finished loading the model.  If the model is still loading
        # after the server's internal timeout, it returns 408 which raises an
        # HttpResponseError here.  We retry on 408 until our own deadline.
        deadline = _time.monotonic() + timeout_sec
        while True:
            poll_req = _HttpRequest(
                "GET",
                "{endpoint}" + f"/fine_tuning/sessions/{session_id}/request/{request_id}",
                headers=_base_headers(),
                params={"api-version": _API_VERSION},
            )
            poll_path = f"/fine_tuning/sessions/{session_id}/request/{request_id}"
            _log_http("request", "GET", poll_path)
            poll_resp = client.send_request(poll_req)
            _log_http("response", "GET", poll_path, status=poll_resp.status_code, body=poll_resp.json() if poll_resp.status_code == 200 else None)

            if poll_resp.status_code == 200:
                _logger.info("[create] model load completed: %s", poll_resp.json())
                break

            if poll_resp.status_code == 408:
                # Server timed out waiting (model still loading) — retry if within deadline
                if _time.monotonic() > deadline:
                    raise RuntimeError(
                        f"Timed out after {timeout_sec}s waiting for session_id={raw_session_id} to become ready"
                    )
                _logger.info("[create] server returned 408 (still loading), retrying...")
                continue

            # Any other error — fail immediately
            poll_resp.raise_for_status()

        return cls(client, session_id=session_id)

    # ── Low-level helper ──────────────────────────────────────────────────────

    def _post_and_poll(self, subpath: str, body_model: Any, extra_params: Optional[dict] = None, extra_result_fields: Optional[dict] = None) -> OperationResult:
        """POST to a loom action endpoint (returns 200 + request_id), then
        long-poll GET /request/{request_id} until the GPU finishes.

        Loom returns 200 (not 202) with ``{request_id, session_id, status}``
        from all mutating operations.  The poll endpoint blocks server-side
        (up to 5 minutes) and returns the typed result directly.
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

        # Retry up to 3 times on 408 (server long-polls ~5 min per attempt,
        # so 3 retries = ~15 min max wait before giving up).
        max_retries = 3
        for attempt in range(max_retries + 1):
            _log_http("request", "GET", poll_path)
            poll_resp = self._client.send_request(poll_req)
            if poll_resp.status_code == 200:
                _log_http("response", "GET", poll_path, status=200, body=poll_resp.json())
                break
            if poll_resp.status_code == 408 and attempt < max_retries:
                _logger.info("[_post_and_poll] server returned 408 (GPU still processing), retry %d/%d", attempt + 1, max_retries)
                continue
            _log_http("response", "GET", poll_path, status=poll_resp.status_code, body=None)
            poll_resp.raise_for_status()

        raw = poll_resp.json()
        normalized = _normalize_loom_result(raw, op_type, request_id)
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

        Blocks until the GPU finishes the backward pass.

        Spec: ``fb_result = session.forward_backward(batch, loss_fn="cross_entropy")``

        :param batch: List of :class:`~azure.ai.finetuning_sessions.models.Datum`.
        :param loss_fn: Loss function name. Defaults to ``"cross_entropy"``.
        :param loss_fn_config: Optional per-loss hyper-parameters.
        :return: :class:`~azure.ai.finetuning_sessions.models.OperationResult`.
        """
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
        :param topk_prompt_logprobs: Top-k log-probabilities per prompt token. 0 = none.
        """
        return self._post_and_poll(
            f"/fine_tuning/sessions/{self.session_id}/sample",
            SampleRequest(
                num_samples=num_samples,
                prompt=ModelInput(chunks=[ModelInputChunk(tokens=prompt_tokens)]),
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
            session_id=self.session_id,
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


__all__: list[str] = ["FineTuningSession"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
