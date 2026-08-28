# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
from collections.abc import MutableMapping
import json
from typing import Any, Callable, Optional, TypeVar

from corehttp.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    StreamClosedError,
    StreamConsumedError,
    map_error,
)
from corehttp.rest import AsyncHttpResponse, HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime.pipeline import PipelineResponse

from ... import models as _models2
from ...._utils.model_base import _deserialize
from ...._utils.serialization import Deserializer, Serializer
from ...._utils.streaming_base import AsyncStream
from ....aio._configuration import SseClientConfiguration
from ...operations._operations import build_unnamed_receive_request

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class UnnamedOperations:  # pylint: disable=docstring-missing-param
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~streaming.sse.aio.SseClient`'s
        :attr:`unnamed` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: SseClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    async def receive(self, **kwargs: Any) -> AsyncStream[_models2.Info]:
        """receive.

        :return: An instance of AsyncStream that iterates over Info
        :rtype: ~streaming.sse.AsyncStream[~streaming.sse.unnamed.models.Info]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[AsyncStream[_models2.Info]] = kwargs.pop("cls", None)

        _last_event_id = kwargs.pop("last_event_id", None)

        _request = build_unnamed_receive_request(
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        if _last_event_id is not None:
            _request.headers["Last-Event-ID"] = _last_event_id

        _decompress = kwargs.pop("decompress", True)
        _stream = kwargs.pop("stream", True)
        pipeline_response: PipelineResponse = await self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                try:
                    await response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        def _callback(_http_response, _event):
            if _event.event == "message":
                _event_json = json.loads(_event.data)
                deserialized = _deserialize(_models2.Info, _event_json)
            else:
                raise ValueError(f"Unknown SSE event type: {_event.event!r}")
            return deserialized

        deserialized: AsyncStream[_models2.Info] = AsyncStream(response=response, deserialization_callback=_callback)  # type: ignore
        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore
        return deserialized
