# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Opt-in legacy ``begin_*`` names over the real HTTP 200 request protocol.

These adapters do not implement an HTTP 202/Operation-Location protocol, start
heartbeats, or resubmit failed work. Generated methods remain the submission
authority. Continuation tokens and arbitrary polling strategies are deliberately
unsupported; neither requests nor credentials are serialized into a token.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from math import isfinite
from typing import Any, Optional

from azure.core.exceptions import HttpResponseError
from azure.core.polling import (
    AsyncLROPoller,
    AsyncNoPolling,
    AsyncPollingMethod,
    LROPoller,
    NoPolling,
    PollingMethod,
)
from azure.core.utils import case_insensitive_dict

from ._compat import _prepare_call
from ._exceptions import _classify_http_error, _classify_poll_failure
from ._utils.model_base import _deserialize
from .models import FoundryFeaturesOptInKeys, OperationResult

__all__ = ["install_legacy_pollers"]

_PREVIEW = FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW
_NO_CONTINUATION = "Legacy begin_* pollers do not support continuation tokens."
_BODY_NAMES = {
    "create_session": "session",
    "forward_backward": "request",
    "optim_step": "request",
    "save_checkpoint": "checkpoint",
    "save_sampler_weights": "checkpoint",
    "sample": "sample",
}


def _is_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _json_object(response: Any) -> dict[str, Any]:
    try:
        payload = response.json()
    except (ValueError, TypeError) as error:
        raise HttpResponseError(message="Expected a JSON object in the request response.", response=response) from error
    if not isinstance(payload, dict):
        raise HttpResponseError(message="Expected a JSON object in the request response.", response=response)
    return payload


def _http_failure(response: Any, session_id: Optional[str]) -> Optional[HttpResponseError]:
    try:
        body = response.json()
    except (ValueError, TypeError):
        body = None
    try:
        return _classify_http_error(
            response.status_code,
            body if isinstance(body, dict) else None,
            response=response,
            session_id=session_id,
        )
    except (ValueError, TypeError):
        # Malformed error metadata must not hide the HTTP failure.
        return None


def _accepted_ids(response: Any, session_id: Optional[str]) -> tuple[str, str]:
    if response.status_code != 200:
        raise _http_failure(response, session_id) or HttpResponseError(response=response)
    payload = _json_object(response)
    request_id = payload.get("request_id")
    # Only an omitted field may fall back to the submitted session identifier.
    # An array, null, or empty identifier is not an older handle to reinterpret.
    session_id = payload.get("session_id", session_id)
    for name, value in (("request_id", request_id), ("session_id", session_id)):
        if not _is_identifier(value):
            raise HttpResponseError(
                message=f"The submission response requires a non-empty string {name}.", response=response
            )
    return session_id, request_id


class _NoContinuation:
    def get_continuation_token(self) -> str:
        raise ValueError(_NO_CONTINUATION)

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs: Any) -> Any:
        raise ValueError(_NO_CONTINUATION)


class _LegacyNoPolling(_NoContinuation, NoPolling[Any]):
    """NoPolling without serialization of the submitted request or credentials."""


class _AsyncLegacyNoPolling(_NoContinuation, AsyncNoPolling[Any]):
    """AsyncNoPolling without continuation-token serialization."""


class _RequestPolling(_NoContinuation):
    """Shared synchronous state; async polling also has a synchronous resource()."""

    def __init__(
        self, endpoint: str, request_arguments: dict[str, Any], interval: float, options: dict[str, Any]
    ) -> None:
        self._endpoint = endpoint
        self._request_arguments = request_arguments
        self._interval = interval
        self._options = options
        self._status = "pending"
        self._error: Optional[Exception] = None

    def initialize(self, client: Any, initial_response: Any, deserialization_callback: Any) -> None:
        self._client = client
        self._response = initial_response
        self._deserialize = deserialization_callback

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._status in ("completed", "failed")

    def resource(self) -> Any:
        if self._error is not None:
            raise self._error
        return self._deserialize(self._response) if self._status == "completed" else None

    def _request(self) -> Any:
        # Lazy import avoids a cycle when operation patch hooks install aliases.
        # The generated builder owns the canonical route and ID/query encoding.
        from .operations._operations import build_operations_get_request

        request = build_operations_get_request(**self._request_arguments)
        request.url = self._client.format_url(request.url, endpoint=self._endpoint)
        return request

    def _update(self, pipeline_response: Any) -> None:
        response = pipeline_response.http_response
        session_id = self._request_arguments["session_id"]
        if response.status_code != 200:
            raise _http_failure(response, session_id) or HttpResponseError(response=response)
        payload = _json_object(response)
        status = payload.get("status")
        if status not in ("pending", "completed", "failed"):
            raise HttpResponseError(message="Expected request status pending, completed, or failed.", response=response)
        if status == "failed":
            try:
                error = _classify_poll_failure(payload, session_id=session_id)
            except (ValueError, TypeError):
                error = None
            raise error or HttpResponseError(message=str(payload.get("error") or "Operation failed."), response=response)
        if status == "completed" and payload.get("result") is not None and not isinstance(payload["result"], dict):
            raise HttpResponseError(message="Expected an object or null for the completed result.", response=response)
        self._response = pipeline_response
        self._status = status


class _SyncRequestPolling(_RequestPolling, PollingMethod[Any]):
    def run(self) -> None:
        if self._error is not None:
            raise self._error
        try:
            while not self.finished():
                self._update(self._client._pipeline.run(self._request(), stream=False, **self._options))
                if not self.finished() and self._interval:
                    self._client._pipeline._transport.sleep(self._interval)
        except Exception as error:
            self._error, self._status = error, "failed"
            raise


class _AsyncRequestPolling(_RequestPolling, AsyncPollingMethod[Any]):
    async def run(self) -> None:
        if self._error is not None:
            raise self._error
        try:
            while not self.finished():
                self._update(await self._client._pipeline.run(self._request(), stream=False, **self._options))
                if not self.finished() and self._interval:
                    await self._client._pipeline._transport.sleep(self._interval)
        except Exception as error:
            self._error, self._status = error, "failed"
            raise


def _capture_response(response: Any, deserialized: Any, headers: Any) -> tuple[Any, Any]:
    return response, deserialized


class _LegacyCall:
    """Snapshot one submission's options without changing a shared operation group."""

    def __init__(
        self, operation: Any, new_name: str, result_type: str, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        if kwargs.pop("continuation_token", None) is not None:
            raise ValueError(_NO_CONTINUATION)
        self._polling = kwargs.pop("polling", True)
        if self._polling is not True and self._polling is not False:
            raise ValueError("Legacy begin_* supports only polling=True or polling=False, not custom strategies.")
        if kwargs.pop("stream", False):
            raise ValueError("Legacy begin_* requires buffered responses; stream=True is unsupported.")
        try:
            self._interval = float(kwargs.pop("polling_interval", operation._config.polling_interval))
        except (TypeError, ValueError) as error:
            raise ValueError("polling_interval must be a finite non-negative number.") from error
        if not isfinite(self._interval) or self._interval < 0:
            raise ValueError("polling_interval must be a finite non-negative number.")
        self._cls = kwargs.pop("cls", None)
        self._result_type = result_type
        body_name = _BODY_NAMES.get(result_type)
        operation = _prepare_call(operation, {"body": body_name} if body_name else {}, kwargs)
        self._client = operation._client
        self._endpoint = operation._config.endpoint
        self.method = getattr(operation, new_name)
        self.session_id = None
        if result_type != "create_session":
            if not args and "session_id" not in kwargs:
                raise TypeError("session_id is required.")
            self.session_id = args[0] if args else kwargs["session_id"]
            if not _is_identifier(self.session_id):
                raise ValueError("session_id must be a non-empty string.")
        if result_type == "sample":
            if "checkpoint_id" not in kwargs:
                raise TypeError("checkpoint_id is required for sampling.")
            if not _is_identifier(kwargs["checkpoint_id"]):
                raise ValueError("checkpoint_id must be a non-empty string.")

        self._extra_result_fields = {}
        if result_type in ("save_checkpoint", "save_sampler_weights"):
            body = args[1] if len(args) > 1 else kwargs.get(body_name)
            if isinstance(body, Mapping) and _is_identifier(body.get("path")):
                self._extra_result_fields["checkpoint_id"] = body["path"]

        headers = case_insensitive_dict(kwargs.get("headers") or {})
        for name in ("Content-Type", "Content-Length", "Transfer-Encoding"):
            headers.pop(name, None)
        self._request_arguments = {
            "foundry_features": kwargs.setdefault("foundry_features", _PREVIEW),
            "api_version": operation._config.api_version,
            "headers": headers,
            "params": deepcopy(kwargs.get("params") or {}),
        }
        submission_only = {
            body_name,
            "session_id",
            "checkpoint_id",
            "foundry_features",
            "headers",
            "params",
            "content_type",
            "decompress",
            "error_map",
        }
        self._poll_options = {name: value for name, value in kwargs.items() if name not in submission_only}
        self._poll_options["permit_redirects"] = False
        # Even azure-core's default RetryPolicy retries some POST failures.
        # Disable submission retries/redirects per call, not on the shared client.
        # GETs retain the existing pipeline's (or caller's) bounded retry policy.
        kwargs.update(cls=_capture_response, retry_total=0, permit_redirects=False)
        self.kwargs = kwargs

    def poller(self, submission: tuple[Any, Any], asynchronous: bool) -> Any:
        initial_response, handle = submission
        session_id, request_id = _accepted_ids(initial_response.http_response, self.session_id)

        def deserialize(response: Any) -> Any:
            if response is initial_response:
                # NoPolling returns the submitted handle, not a fictitious success.
                result = handle
            else:
                # _patch imports operation groups; importing it at module load
                # would create a cycle with their installation hooks.
                from ._patch import _normalize_loom_result

                data = _json_object(response.http_response).get("result") or {}
                normalized = _normalize_loom_result(data, self._result_type, request_id)
                if self._result_type in ("create_session", "unload_session"):
                    normalized.setdefault("session_id", session_id)
                for name, value in self._extra_result_fields.items():
                    if not normalized.get(name):
                        normalized[name] = value
                result = _deserialize(OperationResult, normalized)
            return self._cls(response, result, {}) if self._cls else result

        if self._polling is False:
            strategy = _AsyncLegacyNoPolling() if asynchronous else _LegacyNoPolling()
        else:
            request_arguments = dict(self._request_arguments, session_id=session_id, request_id_parameter=request_id)
            polling_type = _AsyncRequestPolling if asynchronous else _SyncRequestPolling
            strategy = polling_type(self._endpoint, request_arguments, self._interval, self._poll_options)
        poller_type = AsyncLROPoller if asynchronous else LROPoller
        return poller_type(self._client, initial_response, deserialize, strategy)


def _make_begin(new_name: str, result_type: str, asynchronous: bool) -> Any:
    def begin(self: Any, *args: Any, **kwargs: Any) -> LROPoller[Any]:
        call = _LegacyCall(self, new_name, result_type, args, kwargs)
        try:
            submission = call.method(*args, **call.kwargs)
        except HttpResponseError as error:
            if error.response is not None:
                typed = _http_failure(error.response, call.session_id)
                if typed is not None:
                    raise typed from error
            raise
        return call.poller(submission, False)

    async def begin_async(self: Any, *args: Any, **kwargs: Any) -> AsyncLROPoller[Any]:
        call = _LegacyCall(self, new_name, result_type, args, kwargs)
        try:
            submission = await call.method(*args, **call.kwargs)
        except HttpResponseError as error:
            if error.response is not None:
                typed = _http_failure(error.response, call.session_id)
                if typed is not None:
                    raise typed from error
            raise
        return call.poller(submission, True)

    return begin_async if asynchronous else begin


def install_legacy_pollers(
    operation_type: type, mapping: Mapping[str, tuple[str, str]], asynchronous: bool = False
) -> None:
    """Install missing legacy names on a generated operation class, idempotently.

    ``mapping`` maps each old name to ``(generated_method_name, operation_type)``.
    Set ``asynchronous=True`` for async groups: their begin methods must be
    awaited to obtain an :class:`~azure.core.polling.AsyncLROPoller`.

    Aliases accept positional/generated body arguments, the older ``body``
    keyword, and per-call ``api_version`` without mutating group configuration.
    All but create require a session ID; sampling also requires checkpoint_id.
    ``polling_interval`` defaults to client configuration. ``cls`` receives the
    final PipelineResponse, normalized OperationResult, and an empty header map.
    With ``polling=False`` it instead receives the raw submitted handle through
    NoPolling/AsyncNoPolling, and no GET is issued. Explicit checkpoint body paths
    fill missing checkpoint_id results; binary/stream bodies are not inspected.

    Continuation tokens, custom polling strategies, and streamed responses are
    unsupported and rejected before submission. Only the normal sync LROPoller
    worker polls; this adapter adds no heartbeat or application-level retries.
    Submission retries and redirects are disabled per call; GET retries remain
    governed by the existing pipeline. Poller status uses the service's raw
    pending/completed/failed states (NoPolling retains azure-core's own status).
    """
    for old_name, (new_name, result_type) in mapping.items():
        if hasattr(operation_type, old_name):
            continue
        getattr(operation_type, new_name)  # Fail installation early for a stale mapping.
        method = _make_begin(new_name, result_type, asynchronous)
        method.__name__ = old_name
        method.__qualname__ = f"{operation_type.__qualname__}.{old_name}"
        method.__doc__ = f"Submit once through {new_name} and poll request status. See install_legacy_pollers for limits."
        setattr(operation_type, old_name, method)