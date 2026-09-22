# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""The tested preview's raw-operation behavior, using generated request builders.

This is not the training polling implementation. Training remains in the original
root/aio hooks. These helpers preserve the older raw Azure poller API, including
custom polling and continuation tokens, without misrepresenting the REST service
as HTTP 202 or rewriting emitted source.
"""

from io import IOBase
import json
from typing import Any

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
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, LROPoller, NoPolling
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.polling.base_polling import LROBasePolling
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from . import models as _models
from ._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from ._utils.serialization import Serializer

_NO_BODY = object()
_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def _build_sampling_request(session_id, *, foundry_features, api_version, **kwargs):
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


def _error_map(options):
    errors = {
        401: ClientAuthenticationError,
        404: ResourceNotFoundError,
        409: ResourceExistsError,
        304: ResourceNotModifiedError,
    }
    errors.update(options.pop("error_map", {}) or {})
    return errors


def _request(operation, builder, arguments, body, options):
    # The supported compatibility hook requires generated client, configuration, and serialization internals.
    # pylint: disable=protected-access
    headers = case_insensitive_dict(options.pop("headers", {}) or {})
    params = options.pop("params", {}) or {}
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


def _raise_error(response, errors):
    map_error(status_code=response.status_code, response=response, error_map=errors)
    error = _failsafe_deserialize(_models.ApiErrorResponse, response)
    raise HttpResponseError(response=response, model=error)


def _read(operation, builder, arguments, response_type, options, body=_NO_BODY):
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


async def _read_async(operation, builder, arguments, response_type, options, body=_NO_BODY):
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


def _poller_options(operation, options, has_body):
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

    def deserialize(result):
        response = result.http_response
        response_headers = {
            "Operation-Location": operation._deserialize("str", response.headers.get("Operation-Location"))
        }
        value = _deserialize(_models.OperationResult, response.json().get("result", {}))
        return cls(result, value, response_headers) if cls else value

    return initial_options, polling, delay, token, deserialize


def _initial(operation, builder, arguments, body, options):
    # The supported compatibility hook requires the generated pipeline and deserialization internals.
    # pylint: disable=protected-access
    errors = _error_map(options)
    request = _request(operation, builder, arguments, body, options)
    decompress = options.pop("decompress", True)
    result = operation._client._pipeline.run(request, stream=True, **options)
    response = result.http_response
    if response.status_code != 200:
        try:
            response.read()
        except (StreamConsumedError, StreamClosedError):
            pass
        _raise_error(response, errors)
    # Match the initial generated helper even when its callback discards these.
    operation._deserialize("str", response.headers.get("Operation-Location"))
    if decompress:
        response.iter_bytes()
    else:
        response.iter_raw()
    return result


async def _initial_async(operation, builder, arguments, body, options):
    # The supported compatibility hook requires the generated pipeline and deserialization internals.
    # pylint: disable=protected-access
    errors = _error_map(options)
    request = _request(operation, builder, arguments, body, options)
    decompress = options.pop("decompress", True)
    result = await operation._client._pipeline.run(request, stream=True, **options)
    response = result.http_response
    # The frozen async raw begin_* helpers retained 202, unlike their sync
    # counterparts. Preserve this inconsistency; convenience training uses 200
    # and request-ID polling independently, as does the actual REST contract.
    if response.status_code != 202:
        try:
            await response.read()
        except (StreamConsumedError, StreamClosedError):
            pass
        _raise_error(response, errors)
    operation._deserialize("str", response.headers.get("Operation-Location"))
    if decompress:
        response.iter_bytes()
    else:
        response.iter_raw()
    return result


def _begin(operation, builder, arguments, options, body=_NO_BODY):
    # The supported compatibility hook requires generated client, configuration, and serialization internals.
    # pylint: disable=protected-access
    initial_options, polling, delay, token, deserialize = _poller_options(operation, options, body is not _NO_BODY)
    if token == "":
        raise ValueError("continuation_token must not be empty")
    result: Any = None
    if token is None:
        result = _initial(operation, builder, arguments, body, {**initial_options, **options})
        result.http_response.read()
    options.pop("error_map", None)
    path_arguments = {
        "endpoint": operation._serialize.url(
            "self._config.endpoint", operation._config.endpoint, "str", skip_quote=True
        )
    }
    if polling is True:
        polling = LROBasePolling(delay, path_format_arguments=path_arguments, **options)
    elif polling is False:
        polling = NoPolling()
    if token:
        return LROPoller[_models.OperationResult].from_continuation_token(
            polling_method=polling,
            continuation_token=token,
            client=operation._client,
            deserialization_callback=deserialize,
        )
    return LROPoller[_models.OperationResult](operation._client, result, deserialize, polling)


async def _begin_async(operation, builder, arguments, options, body=_NO_BODY):
    # The supported compatibility hook requires generated client, configuration, and serialization internals.
    # pylint: disable=protected-access
    initial_options, polling, delay, token, deserialize = _poller_options(operation, options, body is not _NO_BODY)
    if token == "":
        raise ValueError("continuation_token must not be empty")
    result: Any = None
    if token is None:
        result = await _initial_async(operation, builder, arguments, body, {**initial_options, **options})
        await result.http_response.read()
    options.pop("error_map", None)
    path_arguments = {
        "endpoint": operation._serialize.url(
            "self._config.endpoint", operation._config.endpoint, "str", skip_quote=True
        )
    }
    if polling is True:
        polling = AsyncLROBasePolling(delay, path_format_arguments=path_arguments, **options)
    elif polling is False:
        polling = AsyncNoPolling()
    if token:
        return AsyncLROPoller[_models.OperationResult].from_continuation_token(
            polling_method=polling,
            continuation_token=token,
            client=operation._client,
            deserialization_callback=deserialize,
        )
    return AsyncLROPoller[_models.OperationResult](operation._client, result, deserialize, polling)
