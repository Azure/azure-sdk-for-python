# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Raw-operation hooks using generated builders and request-ID polling.

The default raw pollers implement the service's HTTP-200 acceptance protocol,
not Azure's HTTP-202/Operation-Location protocol. Explicit polling strategies and
NoPolling remain caller-owned. Convenience training polling stays in root/aio
hooks; these raw pollers never resubmit a failed operation. The default strategy
disables pipeline retries on its POST and GET requests: HTTP errors are surfaced
instead of risking a duplicate mutation or an unbounded Retry-After sleep. A
continuation token retries only the existing request's GET.
"""

from __future__ import annotations

import base64
import binascii
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from io import IOBase
import json
import math
from typing import Any, Callable, NoReturn, Optional
from urllib.parse import urlsplit

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    StreamClosedError,
    StreamConsumedError,
    map_error,
)
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod, LROPoller, NoPolling, PollingMethod
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from . import models as _models
from ._exceptions import _classify_http_error, _classify_poll_failure
from ._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from ._utils.serialization import Serializer

_NO_BODY = object()
_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False
_MAX_POLL_DELAY = 60.0
_MAX_TOKEN_LENGTH = 65536
_PENDING_STATUSES = ("pending", "queued", "running")
_TOKEN_KIND = "azure.ai.finetuningsessions.request"
_ResultCallback = Callable[[Any], Any]
_RequestBuilder = Callable[..., HttpRequest]


def _build_sampling_request(session_id: str, *, foundry_features: str, api_version: str, **kwargs: Any) -> HttpRequest:
    """The legacy raw sampling call has no required checkpoint query argument.

    Modern REST sampling does. Keeping this one historical request shape in the
    compatibility hook avoids weakening the real required REST parameter.

    :param str session_id: Identifier of the fine-tuning session to sample from.
    :keyword str foundry_features: Value of the Foundry-Features preview opt-in header.
    :keyword str api_version: API version to include in the request query.
    :return: The HTTP POST request for the legacy sampling operation.
    :rtype: ~azure.core.rest.HttpRequest
    """
    headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    params = case_insensitive_dict(kwargs.pop("params", {}) or {})
    content_type = kwargs.pop("content_type", headers.pop("Content-Type", None))
    accept = headers.pop("Accept", "application/json")
    url = "/fine_tuning/sessions/{sessionId}/sample".format(sessionId=_SERIALIZER.url("session_id", session_id, "str"))
    params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")
    headers["Foundry-Features"] = _SERIALIZER.header("foundry_features", foundry_features, "str")
    if content_type is not None:
        headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    headers["Accept"] = _SERIALIZER.header("accept", accept, "str")
    return HttpRequest(method="POST", url=url, params=params, headers=headers, **kwargs)


def _error_map(options: dict[str, Any]) -> dict[int, Any]:
    """Extract the generated HTTP error mappings, retaining caller overrides.

    :param dict options: Mutable operation options from which error_map is removed.
    :return: Default status mappings updated with the caller's overrides.
    :rtype: dict[int, ~typing.Any]
    """
    errors = {
        401: ClientAuthenticationError,
        404: ResourceNotFoundError,
        409: ResourceExistsError,
        304: ResourceNotModifiedError,
    }
    errors.update(options.pop("error_map", {}) or {})
    return errors


def _request(
    operation: Any, builder: _RequestBuilder, arguments: dict[str, Any], body: Any, options: dict[str, Any]
) -> HttpRequest:
    """Build the unchanged preview request through generated serialization.

    :param ~typing.Any operation: Generated operation group providing serialization.
    :param callable builder: Generated HTTP request builder.
    :param dict arguments: Builder arguments, extended with serialized body fields.
    :param ~typing.Any body: Model, mapping, stream, bytes, or the no-body sentinel.
    :param dict options: Mutable header, query and content-type options.
    :return: Request resolved against the configured client endpoint.
    :rtype: ~azure.core.rest.HttpRequest
    """
    # The supported compatibility hook requires generated client, configuration, and serialization internals.
    # pylint: disable=protected-access
    headers = case_insensitive_dict(options.pop("headers", {}) or {})
    params = case_insensitive_dict(options.pop("params", {}) or {})
    # Preserve the preview query ordering after adopting the shared Foundry
    # operation template. The generated builder still serializes and replaces
    # this value; existing caller parameters keep their original positions.
    if "api_version" in arguments and "api-version" not in params:
        params["api-version"] = arguments["api_version"]
    if body is not _NO_BODY:
        content_type = options.pop("content_type", headers.pop("Content-Type", None))
        arguments["content_type"] = content_type or "application/json"
        arguments["content"] = (
            body if isinstance(body, (IOBase, bytes)) else json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)
        )
    request = builder(**arguments, headers=headers, params=params)
    path_arguments = {
        "endpoint": operation._serialize.url(
            "self._config.endpoint", operation._config.endpoint, "str", skip_quote=True
        )
    }
    request.url = operation._client.format_url(request.url, **path_arguments)
    return request


def _raise_error(response: Any, errors: dict[int, Any]) -> NoReturn:
    """Raise the generated HTTP error, applying the caller's status mapping.

    :param ~typing.Any response: Buffered HTTP response associated with the error.
    :param dict errors: HTTP status to exception mappings.
    :raises ~azure.core.exceptions.HttpResponseError: The mapped or generic error.
    """
    map_error(status_code=response.status_code, response=response, error_map=errors)
    error = _failsafe_deserialize(_models.ApiErrorResponse, response)
    raise HttpResponseError(response=response, model=error)


def _read(
    operation: Any,
    builder: _RequestBuilder,
    arguments: dict[str, Any],
    response_type: Any,
    options: dict[str, Any],
    body: Any = _NO_BODY,
) -> Any:
    """Execute a synchronous raw non-polling operation.

    :param ~typing.Any operation: Generated operation group owning the pipeline.
    :param callable builder: HTTP request builder.
    :param dict arguments: Builder arguments.
    :param ~typing.Any response_type: Model type, or None for a raw JSON response.
    :param dict options: Mutable request options, including cls and error_map.
    :param ~typing.Any body: Optional request body or the no-body sentinel.
    :return: Deserialized response, byte iterator, or the caller's cls result.
    :rtype: ~typing.Any
    """
    # The supported compatibility hook requires access to the generated client's internal pipeline.
    # pylint: disable=protected-access
    errors = _error_map(options)
    request = _request(operation, builder, arguments, body, options)
    cls = options.pop("cls", None)
    stream = options.pop("stream", False)
    decompress = options.pop("decompress", True) if response_type is not None else True
    result = operation._client._pipeline.run(request, stream=stream, **options)
    response = result.http_response
    if response.status_code != 200:
        if stream:
            try:
                response.read()
            except (StreamConsumedError, StreamClosedError):
                pass
        _raise_error(response, errors)
    if response_type is None:
        value = response.json()
    elif stream:
        value = response.iter_bytes() if decompress else response.iter_raw()
    else:
        value = _deserialize(response_type, response.json())
    return cls(result, value, {}) if cls else value


async def _read_async(
    operation: Any,
    builder: _RequestBuilder,
    arguments: dict[str, Any],
    response_type: Any,
    options: dict[str, Any],
    body: Any = _NO_BODY,
) -> Any:
    """Execute an asynchronous raw non-polling operation.

    :param ~typing.Any operation: Generated operation group owning the pipeline.
    :param callable builder: HTTP request builder.
    :param dict arguments: Builder arguments.
    :param ~typing.Any response_type: Model type, or None for a raw JSON response.
    :param dict options: Mutable request options, including cls and error_map.
    :param ~typing.Any body: Optional request body or the no-body sentinel.
    :return: Deserialized response, async byte iterator, or the caller's cls result.
    :rtype: ~typing.Any
    """
    # The supported compatibility hook requires access to the generated client's internal pipeline.
    # pylint: disable=protected-access
    errors = _error_map(options)
    request = _request(operation, builder, arguments, body, options)
    cls = options.pop("cls", None)
    stream = options.pop("stream", False)
    decompress = options.pop("decompress", True) if response_type is not None else True
    result = await operation._client._pipeline.run(request, stream=stream, **options)
    response = result.http_response
    if response.status_code != 200:
        if stream:
            try:
                await response.read()
            except (StreamConsumedError, StreamClosedError):
                pass
        _raise_error(response, errors)
    if response_type is None:
        value = response.json()
    elif stream:
        value = response.iter_bytes() if decompress else response.iter_raw()
    else:
        value = _deserialize(response_type, response.json())
    return cls(result, value, {}) if cls else value


def _identifier(value: Any, name: str) -> str:
    """Validate a locator before the generated builder encodes it as one segment.

    :param ~typing.Any value: Untrusted identity field from a response or token.
    :param str name: Field name used in validation errors.
    :return: Validated, unencoded identity field.
    :rtype: str
    """
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > 1024
        or value in (".", "..")
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise ValueError(f"{name} must be a nonempty string without control characters or dot segments")
    try:
        value.encode("utf-8")
    except UnicodeError as exc:
        raise ValueError(f"{name} must contain valid Unicode") from exc
    return value


def _polling_endpoint(endpoint: str) -> str:
    """Bind tokens to the configured origin and path, without credentials or query.

    :param str endpoint: Configured endpoint or token endpoint to validate.
    :return: Endpoint with trailing slashes removed, retaining its complete path.
    :rtype: str
    """
    parsed = urlsplit(endpoint)
    has_userinfo = parsed.username is not None or parsed.password is not None
    unsafe_characters = "\\" in endpoint or any(
        char.isspace() or ord(char) < 32 or ord(char) == 127 for char in endpoint
    )
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or has_userinfo
        or any((parsed.query, parsed.fragment))
        or unsafe_characters
    ):
        raise ValueError("Request polling requires an absolute HTTP(S) endpoint without credentials, query or fragment")
    # Accessing port also validates malformed/non-numeric/out-of-range ports.
    if parsed.port == 0:
        raise ValueError("Request polling requires a valid endpoint port")
    return endpoint.rstrip("/")


def _polling_interval(value: Any) -> float:
    """Reject invalid intervals before submitting; cap individual waits at 60 seconds.

    :param ~typing.Any value: Caller or client configured polling interval.
    :return: Finite non-negative interval, capped at 60 seconds.
    :rtype: float
    """
    try:
        interval = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("polling_interval must be a finite non-negative number") from exc
    if isinstance(value, bool) or not math.isfinite(interval) or interval < 0:
        raise ValueError("polling_interval must be a finite non-negative number")
    return min(interval, _MAX_POLL_DELAY)


def _retry_delay(response: Any, envelope: dict[str, Any], interval: float) -> float:
    """Use finite, bounded retry hints; malformed hints fall back to the interval.

    :param ~typing.Any response: Pending HTTP response carrying retry headers.
    :param dict envelope: Request envelope with an optional retry_after_sec hint.
    :param float interval: Validated default polling interval.
    :return: Delay between polls in seconds, never exceeding 60 seconds.
    :rtype: float
    """
    hints = (
        (response.headers.get("Retry-After"), 1.0, True),
        (response.headers.get("retry-after-ms"), 1000.0, False),
        (response.headers.get("x-ms-retry-after-ms"), 1000.0, False),
        (envelope.get("retry_after_sec"), 1.0, False),
    )
    for value, scale, http_date in hints:
        if value is None or isinstance(value, bool):
            continue
        try:
            delay = float(value) / scale
        except (TypeError, ValueError, OverflowError):
            if not http_date or not isinstance(value, str):
                continue
            try:
                date = parsedate_to_datetime(value)
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)
                delay = max(0.0, (date - datetime.now(timezone.utc)).total_seconds())
            except (TypeError, ValueError, OverflowError):
                continue
        if math.isfinite(delay) and delay >= 0:
            return min(delay, _MAX_POLL_DELAY)
    return interval


def _response_object(response: Any) -> dict[str, Any]:
    """Require an object, rather than silently treating invalid JSON as completion.

    :param ~typing.Any response: Buffered HTTP response to decode.
    :return: The JSON object returned by the service.
    :rtype: dict[str, ~typing.Any]
    """
    try:
        value = response.json()
    except (TypeError, ValueError) as exc:
        raise HttpResponseError(
            message="Invalid request polling response: expected a JSON object", response=response
        ) from exc
    if not isinstance(value, dict):
        raise HttpResponseError(message="Invalid request polling response: expected a JSON object", response=response)
    return value


def _raise_request_error(response: Any, custom_errors: dict[int, Any], session_id: Optional[str]) -> NoReturn:
    """Honor explicit error_map entries before the service's typed HTTP errors.

    :param ~typing.Any response: Buffered error response from POST or GET.
    :param dict custom_errors: Caller-supplied status overrides, without SDK defaults.
    :param session_id: Known session identity to include in engine errors.
    :type session_id: str or None
    :raises ~azure.core.exceptions.HttpResponseError: Caller, service or default error.
    """
    map_error(status_code=response.status_code, response=response, error_map=custom_errors)
    if response.status_code not in custom_errors:
        try:
            body = response.json()
        except (TypeError, ValueError):
            body = None
        typed = _classify_http_error(response.status_code, body, response=response, session_id=session_id)
        if typed is not None:
            raise typed
    _raise_error(response, _error_map({"error_map": custom_errors}))


def _request_token(token: str) -> dict[str, Any]:
    """Decode only a small, versioned JSON locator; never deserialize Python objects.

    :param str token: Untrusted opaque continuation token.
    :return: Validated locator; initialization still checks caller binding.
    :rtype: dict[str, ~typing.Any]
    """
    if not isinstance(token, str) or not token or len(token) > _MAX_TOKEN_LENGTH:
        raise ValueError("Invalid request polling continuation token")
    try:
        state = json.loads(base64.b64decode(token, altchars=b"-_", validate=True).decode("utf-8"))
    except (ValueError, TypeError, UnicodeError, binascii.Error, RecursionError) as exc:
        raise ValueError("Invalid request polling continuation token") from exc
    fields = {"kind", "version", "endpoint", "operation", "api_version", "session_id", "request_id"}
    if not isinstance(state, dict) or set(state) != fields or state["kind"] != _TOKEN_KIND:
        raise ValueError("Unsupported request polling continuation token")
    if not isinstance(state["version"], int) or isinstance(state["version"], bool) or state["version"] != 1:
        raise ValueError("Unsupported request polling continuation token")
    for name in ("session_id", "request_id", "operation", "api_version"):
        _identifier(state[name], name)
    if not isinstance(state["endpoint"], str) or _polling_endpoint(state["endpoint"]) != state["endpoint"]:
        raise ValueError("Invalid continuation token endpoint")
    return state


class _RequestPollingState:
    """Shared request-ID state machine; IO is supplied by the sync/async subclasses.

    Tokens contain only a bound request locator, not credentials, headers, results,
    arbitrary polling URLs or executable state. Resumption always queries the live
    request. Tokens are not authorization: service access checks still apply.

    :param operation: Generated operation group providing the configured pipeline.
    :type operation: ~typing.Any
    :param builder: Original submit builder, used to bind continuation tokens.
    :type builder: callable
    :param arguments: Explicit session, API version and feature header arguments.
    :type arguments: dict[str, ~typing.Any]
    :param initial_options: Caller headers and query parameters to retain on GETs.
    :type initial_options: dict[str, ~typing.Any]
    :param options: Caller pipeline options, including custom error mappings.
    :type options: dict[str, ~typing.Any]
    :param interval: Default delay between pending polls, capped at 60 seconds.
    :type interval: float
    """

    # Separate identity, pipeline configuration, terminal error and response state
    # keep token validation independent of transport and deserialization callbacks.
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        operation: Any,
        builder: _RequestBuilder,
        arguments: dict[str, Any],
        initial_options: dict[str, Any],
        options: dict[str, Any],
        interval: float,
    ) -> None:
        # The supported compatibility hook requires generated endpoint configuration.
        # pylint: disable=protected-access
        self._operation = operation
        self._arguments = dict(arguments)
        self._initial_options = initial_options
        self._options = dict(options)
        self._interval = _polling_interval(interval)
        session_id = arguments.get("session_id")
        self._identity: dict[str, Any] = {
            "kind": _TOKEN_KIND,
            "version": 1,
            "endpoint": _polling_endpoint(operation._config.endpoint),
            "operation": builder.__name__,
            "api_version": _identifier(arguments["api_version"], "api_version"),
            "session_id": _identifier(session_id, "session_id") if "session_id" in arguments else None,
        }
        self._client: Any = None
        self._response: Any = None
        self._deserialize: Optional[_ResultCallback] = None
        self._status = "InProgress"
        self._failure: Optional[HttpResponseError] = None
        self._next_delay: Optional[float] = None

    def initialize(self, client: Any, initial_response: Any, deserialization_callback: _ResultCallback) -> None:
        """Validate acceptance or a continuation locator without assuming completion.

        :param client: Azure Core pipeline client used to poll the request.
        :type client: ~typing.Any
        :param initial_response: Buffered acceptance response or decoded locator.
        :type initial_response: ~typing.Any
        :param deserialization_callback: Callback for the completed response only.
        :type deserialization_callback: callable
        """
        self._client = client
        self._deserialize = deserialization_callback
        if isinstance(initial_response, dict):
            for name, expected in self._identity.items():
                if expected is not None and initial_response[name] != expected:
                    raise ValueError(f"Continuation token {name} does not match this operation")
            self._identity = dict(initial_response)
            return
        response = initial_response.http_response
        data = _response_object(response)
        try:
            request_id = _identifier(data.get("request_id"), "request_id")
            session_id = _identifier(data.get("session_id", self._identity["session_id"]), "session_id")
            if self._identity["session_id"] is not None and session_id != self._identity["session_id"]:
                raise ValueError("Accepted response session_id does not match the requested session_id")
            # A create response describes the session ('created'/'queued'), not
            # the request. Even a POST marked 'completed' must be verified by GET.
            accepted: tuple[str, ...] = (*_PENDING_STATUSES, "completed", "failed")
            if "session_id" not in self._arguments:
                accepted = (*accepted, "created")
            if "status" in data and data["status"] not in accepted:
                raise ValueError(f"Unexpected acceptance status {data['status']!r}")
        except ValueError as exc:
            raise HttpResponseError(message=f"Invalid request acceptance: {exc}", response=response) from exc
        self._identity.update(session_id=session_id, request_id=request_id)

    def status(self) -> str:
        """Return Azure Core's InProgress, Succeeded or Failed status.

        :return: The status derived from a validated request envelope.
        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Report terminal envelope state, never merely successful HTTP acceptance.

        :return: Whether a terminal envelope or protocol failure was received.
        :rtype: bool
        """
        return self._status in ("Succeeded", "Failed")

    def resource(self) -> Any:
        """Deserialize only completion; a synchronous result timeout returns None.

        :return: Completed result, caller cls value, or None while still pending.
        :rtype: ~typing.Any
        """
        if self._failure is not None:
            raise self._failure
        if self._status != "Succeeded" or self._deserialize is None:
            return None
        return self._deserialize(self._response)

    def get_continuation_token(self) -> str:
        """Serialize a locator, excluding request bodies and authentication headers.

        :return: Opaque versioned JSON continuation token.
        :rtype: str
        """
        token = base64.urlsafe_b64encode(json.dumps(self._identity, separators=(",", ":")).encode("utf-8")).decode(
            "ascii"
        )
        if len(token) > _MAX_TOKEN_LENGTH:
            raise ValueError("Request polling continuation token is too large")
        return token

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs: Any) -> tuple[Any, Any, _ResultCallback]:
        """Restore a locator; initialize checks endpoint, session and operation binding.

        Azure Core supplies client and deserialization_callback through kwargs.

        :param str continuation_token: Token previously returned by this strategy.
        :return: Client, validated locator, and callback expected by Azure Core.
        :rtype: tuple[~typing.Any, ~typing.Any, callable]
        """
        if "client" not in kwargs or "deserialization_callback" not in kwargs:
            raise ValueError("Continuation requires client and deserialization_callback")
        return kwargs["client"], _request_token(continuation_token), kwargs["deserialization_callback"]

    def _poll_request(self) -> HttpRequest:
        """Use the existing encoded GET builder, never a server-supplied URL.

        :return: Encoded status GET targeting the configured endpoint only.
        :rtype: ~azure.core.rest.HttpRequest
        """
        # Import lazily: the generated operation patch itself imports these helpers.
        from .operations._operations import build_operations_get_request

        headers = case_insensitive_dict(self._initial_options["headers"])
        headers.pop("Content-Type", None)
        headers.pop("Content-Length", None)
        return _request(
            self._operation,
            build_operations_get_request,
            {
                "session_id": self._identity["session_id"],
                "request_id_parameter": self._identity["request_id"],
                "api_version": self._arguments["api_version"],
                "foundry_features": self._arguments["foundry_features"],
            },
            _NO_BODY,
            {"headers": headers, "params": self._initial_options["params"]},
        )

    def _poll_options(self) -> dict[str, Any]:
        """Retain options except redirects, streaming and unvalidated pipeline retries.

        :return: Poll pipeline options; result streaming is handled by this strategy.
        :rtype: dict[str, ~typing.Any]
        """
        options = dict(self._options)
        for name in ("error_map", "stream", "decompress"):
            options.pop(name, None)
        options["permit_redirects"] = False
        # Core retries can sleep on an unbounded/nonfinite Retry-After before our
        # state machine sees it. Surface HTTP errors; a token resumes this GET.
        options["retry_total"] = 0
        return options

    def _update(self, result: Any) -> None:
        """Validate identities, state and terminal payload before exposing a result.

        :param ~typing.Any result: Buffered status-GET pipeline response.
        """
        response = result.http_response
        errors = self._options.get("error_map", {}) or {}
        try:
            if response.status_code != 200:
                _raise_request_error(response, errors, self._identity["session_id"])
            envelope = _response_object(response)
            for name in ("request_id", "session_id"):
                if name in envelope and envelope[name] != self._identity[name]:
                    raise HttpResponseError(
                        message=f"Polling response {name} does not match the request", response=response
                    )
            status = envelope.get("status")
            if status == "failed":
                map_error(status_code=response.status_code, response=response, error_map=errors)
                if envelope.get("error") is not None and not isinstance(envelope["error"], str):
                    raise HttpResponseError(
                        message="Invalid failed request envelope: error must be a string", response=response
                    )
                typed = _classify_poll_failure(envelope, session_id=self._identity["session_id"])
                if typed is not None:
                    typed.response = response
                    typed.status_code = response.status_code
                    raise typed
                raise HttpResponseError(
                    message=(
                        f"Request {self._identity['request_id']} failed: {envelope.get('error') or 'Operation failed'}"
                    ),
                    response=response,
                )
            if status == "completed":
                if not isinstance(envelope.get("result"), dict):
                    raise HttpResponseError(
                        message="Invalid completed request envelope: result must be an object", response=response
                    )
                self._response = result
                self._status = "Succeeded"
            elif status in _PENDING_STATUSES:
                self._next_delay = _retry_delay(response, envelope, self._interval)
            else:
                raise HttpResponseError(message=f"Unexpected request envelope status {status!r}", response=response)
        except HttpResponseError as exc:
            self._failure = exc
            self._status = "Failed"
            raise


class _RequestPolling(_RequestPollingState, PollingMethod[Any]):
    """Synchronous request-ID polling without operation resubmission."""

    def run(self) -> None:
        """Poll GET until completion, surfacing terminal and HTTP errors.

        :return: None.
        :rtype: None
        """
        # The supported compatibility hook requires the generated pipeline and
        # its transport's sleep API, as Azure Core's default poller does.
        # pylint: disable=protected-access
        if self._failure is not None:
            raise self._failure
        while not self.finished():
            if self._next_delay is not None:
                self._client._pipeline._transport.sleep(self._next_delay)
            # Read explicitly so ContentDecodePolicy cannot mask an HTTP error_map
            # with its JSON DecodeError before the status code is classified.
            result = self._client._pipeline.run(self._poll_request(), stream=True, **self._poll_options())
            result.http_response.read()
            self._update(result)


class _AsyncRequestPolling(_RequestPollingState, AsyncPollingMethod[Any]):
    """Asynchronous request-ID polling with the same protocol and token validation."""

    async def run(self) -> None:
        """Poll GET using the async pipeline and transport sleep API.

        :return: None.
        :rtype: None
        """
        # The supported compatibility hook requires the generated pipeline and
        # its transport's async sleep API, without blocking the event loop.
        # pylint: disable=protected-access
        if self._failure is not None:
            raise self._failure
        while not self.finished():
            if self._next_delay is not None:
                await self._client._pipeline._transport.sleep(self._next_delay)
            # Mirror sync buffering before status classification or JSON validation.
            result = await self._client._pipeline.run(self._poll_request(), stream=True, **self._poll_options())
            await result.http_response.read()
            self._update(result)


def _poller_options(
    operation: Any, options: dict[str, Any], has_body: bool
) -> tuple[dict[str, Any], Any, Any, Optional[str], _ResultCallback]:
    """Separate initial request options and the existing result/cls callback.

    :param ~typing.Any operation: Generated operation group providing configuration.
    :param dict options: Mutable caller request and polling options.
    :param bool has_body: Whether the operation accepts a request body.
    :return: Initial options, strategy, delay, token and deserialization callback.
    :rtype: tuple[dict, ~typing.Any, ~typing.Any, str or None, callable]
    """
    # The supported compatibility hook requires generated polling configuration and deserialization internals.
    # pylint: disable=protected-access
    headers = case_insensitive_dict(options.pop("headers", {}) or {})
    params = options.pop("params", {}) or {}
    initial_options = {"headers": headers, "params": params}
    if has_body:
        initial_options["content_type"] = options.pop("content_type", headers.pop("Content-Type", None))
    cls = options.pop("cls", None)
    polling = options.pop("polling", True)
    delay = options.pop("polling_interval", operation._config.polling_interval)
    token = options.pop("continuation_token", None)

    def deserialize(result: Any) -> Any:
        response = result.http_response
        response_headers = {
            "Operation-Location": operation._deserialize("str", response.headers.get("Operation-Location"))
        }
        value = _deserialize(_models.OperationResult, response.json().get("result", {}))
        return cls(result, value, response_headers) if cls else value

    return initial_options, polling, delay, token, deserialize


def _initial(
    operation: Any,
    builder: _RequestBuilder,
    arguments: dict[str, Any],
    body: Any,
    options: dict[str, Any],
    *,
    request_polling: bool = False,
) -> Any:
    """Submit once through the existing pipeline, accepting the actual HTTP 200.

    The default request-ID strategy disables pipeline retries and redirects to
    prevent automatic mutation replay. Explicit strategies retain caller options.

    :param ~typing.Any operation: Generated operation group owning the pipeline.
    :param callable builder: Original submit request builder.
    :param dict arguments: Builder arguments.
    :param ~typing.Any body: Request body or the no-body sentinel.
    :param dict options: Mutable submit options, including caller error mappings.
    :keyword bool request_polling: Apply service HTTP classifiers for default polling.
    :return: Original HTTP-200 pipeline response, without synthetic LRO headers.
    :rtype: ~typing.Any
    """
    # The supported compatibility hook requires the generated pipeline and deserialization internals.
    # pylint: disable=protected-access
    custom_errors = options.get("error_map", {}) or {}
    errors = _error_map(options)
    request = _request(operation, builder, arguments, body, options)
    decompress = options.pop("decompress", True)
    if request_polling:
        # A retry or 307/308 replay can duplicate training mutations even before
        # an acceptance reaches the caller. Do not let the default path replay POST.
        options.update(retry_total=0, permit_redirects=False)
    result = operation._client._pipeline.run(request, stream=True, **options)
    response = result.http_response
    if response.status_code != 200:
        try:
            response.read()
        except (StreamConsumedError, StreamClosedError):
            pass
        if request_polling:
            _raise_request_error(response, custom_errors, arguments.get("session_id"))
        _raise_error(response, errors)
    # Match the initial generated helper even when its callback discards these.
    operation._deserialize("str", response.headers.get("Operation-Location"))
    if decompress:
        response.iter_bytes()
    else:
        response.iter_raw()
    return result


async def _initial_async(
    operation: Any,
    builder: _RequestBuilder,
    arguments: dict[str, Any],
    body: Any,
    options: dict[str, Any],
    *,
    request_polling: bool = False,
) -> Any:
    """Submit asynchronously, preserving the real HTTP 200 for custom pollers too.

    :param ~typing.Any operation: Generated operation group owning the pipeline.
    :param callable builder: Original submit request builder.
    :param dict arguments: Builder arguments.
    :param ~typing.Any body: Request body or the no-body sentinel.
    :param dict options: Mutable submit options, including caller error mappings.
    :keyword bool request_polling: Apply service HTTP classifiers for default polling.
    :return: Original HTTP-200 pipeline response, without synthetic LRO headers.
    :rtype: ~typing.Any
    """
    # The supported compatibility hook requires the generated pipeline and deserialization internals.
    # pylint: disable=protected-access
    custom_errors = options.get("error_map", {}) or {}
    errors = _error_map(options)
    request = _request(operation, builder, arguments, body, options)
    decompress = options.pop("decompress", True)
    if request_polling:
        # Match synchronous no-replay semantics; custom strategies keep their options.
        options.update(retry_total=0, permit_redirects=False)
    result = await operation._client._pipeline.run(request, stream=True, **options)
    response = result.http_response
    if response.status_code != 200:
        try:
            await response.read()
        except (StreamConsumedError, StreamClosedError):
            pass
        if request_polling:
            _raise_request_error(response, custom_errors, arguments.get("session_id"))
        _raise_error(response, errors)
    operation._deserialize("str", response.headers.get("Operation-Location"))
    if decompress:
        response.iter_bytes()
    else:
        response.iter_raw()
    return result


def _begin(
    operation: Any,
    builder: _RequestBuilder,
    arguments: dict[str, Any],
    options: dict[str, Any],
    body: Any = _NO_BODY,
) -> LROPoller[_models.OperationResult]:
    """Start raw request-ID polling unless the caller explicitly owns the strategy.

    :param ~typing.Any operation: Generated operation group owning the pipeline.
    :param callable builder: Original submit request builder.
    :param dict arguments: Required route, version and feature arguments.
    :param dict options: Mutable submit, polling and continuation options.
    :param ~typing.Any body: Request body, unused when resuming a continuation.
    :return: Azure Core poller with the caller's or default request-ID strategy.
    :rtype: ~azure.core.polling.LROPoller[~azure.ai.finetuningsessions.models.OperationResult]
    """
    # The supported compatibility hook requires generated client, configuration, and serialization internals.
    # pylint: disable=protected-access
    initial_options, polling, delay, token, deserialize = _poller_options(operation, options, body is not _NO_BODY)
    if token == "":
        raise ValueError("continuation_token must not be empty")
    request_polling = polling is True
    if request_polling:
        polling = _RequestPolling(operation, builder, arguments, initial_options, options, delay)
    elif polling is False:
        polling = NoPolling()
    result: Any = None
    if token is None:
        result = _initial(
            operation, builder, arguments, body, {**initial_options, **options}, request_polling=request_polling
        )
        result.http_response.read()
    if token is not None:
        return LROPoller[_models.OperationResult].from_continuation_token(
            polling_method=polling,
            continuation_token=token,
            client=operation._client,
            deserialization_callback=deserialize,
        )
    return LROPoller[_models.OperationResult](operation._client, result, deserialize, polling)


async def _begin_async(
    operation: Any,
    builder: _RequestBuilder,
    arguments: dict[str, Any],
    options: dict[str, Any],
    body: Any = _NO_BODY,
) -> AsyncLROPoller[_models.OperationResult]:
    """Start the equivalent asynchronous strategy without inventing HTTP 202.

    :param ~typing.Any operation: Generated operation group owning the pipeline.
    :param callable builder: Original submit request builder.
    :param dict arguments: Required route, version and feature arguments.
    :param dict options: Mutable submit, polling and continuation options.
    :param ~typing.Any body: Request body, unused when resuming a continuation.
    :return: Azure Core async poller with the caller's or default request-ID strategy.
    :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.finetuningsessions.models.OperationResult]
    """
    # The supported compatibility hook requires generated client, configuration, and serialization internals.
    # pylint: disable=protected-access
    initial_options, polling, delay, token, deserialize = _poller_options(operation, options, body is not _NO_BODY)
    if token == "":
        raise ValueError("continuation_token must not be empty")
    request_polling = polling is True
    if request_polling:
        polling = _AsyncRequestPolling(operation, builder, arguments, initial_options, options, delay)
    elif polling is False:
        polling = AsyncNoPolling()
    result: Any = None
    if token is None:
        result = await _initial_async(
            operation, builder, arguments, body, {**initial_options, **options}, request_polling=request_polling
        )
        await result.http_response.read()
    if token is not None:
        return AsyncLROPoller[_models.OperationResult].from_continuation_token(
            polling_method=polling,
            continuation_token=token,
            client=operation._client,
            deserialization_callback=deserialize,
        )
    return AsyncLROPoller[_models.OperationResult](operation._client, result, deserialize, polling)
