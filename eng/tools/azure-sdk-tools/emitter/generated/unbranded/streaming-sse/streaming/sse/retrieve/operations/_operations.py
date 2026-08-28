# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
from collections.abc import MutableMapping
from io import IOBase
import json
from typing import Any, Callable, IO, Optional, TypeVar, Union, overload

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
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.runtime import PipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from .. import models as _models1, types as _types_models1
from ..._configuration import SseClientConfiguration
from ..._utils.model_base import SdkJSONEncoder, _deserialize
from ..._utils.serialization import Deserializer, Serializer
from ..._utils.streaming_base import Stream

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_retrieve_stream_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "text/event-stream")

    # Construct URL
    _url = "/streaming/sse/retrieve/stream"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


class RetrieveOperations:  # pylint: disable=docstring-missing-param
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~streaming.sse.SseClient`'s
        :attr:`retrieve` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: SseClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    def stream(
        self, request: _models1.RetrievalRequest, *, content_type: str = "application/json", **kwargs: Any
    ) -> Stream[Union[_models1.PartialResult, _models1.FinalResult]]:
        """stream.

        :param request: Required.
        :type request: ~streaming.sse.retrieve.models.RetrievalRequest
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of Stream that iterates over PartialResult or FinalResult
        :rtype: ~streaming.sse.Stream[~streaming.sse.retrieve.models.PartialResult or
         ~streaming.sse.retrieve.models.FinalResult]
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def stream(
        self, request: _types_models1.RetrievalRequest, *, content_type: str = "application/json", **kwargs: Any
    ) -> Stream[Union[_models1.PartialResult, _models1.FinalResult]]:
        """stream.

        :param request: Required.
        :type request: ~streaming.sse.retrieve.types.RetrievalRequest
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of Stream that iterates over PartialResult or FinalResult
        :rtype: ~streaming.sse.Stream[~streaming.sse.retrieve.models.PartialResult or
         ~streaming.sse.retrieve.models.FinalResult]
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def stream(
        self, request: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> Stream[Union[_models1.PartialResult, _models1.FinalResult]]:
        """stream.

        :param request: Required.
        :type request: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of Stream that iterates over PartialResult or FinalResult
        :rtype: ~streaming.sse.Stream[~streaming.sse.retrieve.models.PartialResult or
         ~streaming.sse.retrieve.models.FinalResult]
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def stream(
        self, request: Union[_models1.RetrievalRequest, _types_models1.RetrievalRequest, IO[bytes]], **kwargs: Any
    ) -> Stream[Union[_models1.PartialResult, _models1.FinalResult]]:
        """stream.

        :param request: Is either a RetrievalRequest type or a IO[bytes] type. Required.
        :type request: ~streaming.sse.retrieve.models.RetrievalRequest or
         ~streaming.sse.retrieve.types.RetrievalRequest or IO[bytes]
        :return: An instance of Stream that iterates over PartialResult or FinalResult
        :rtype: ~streaming.sse.Stream[~streaming.sse.retrieve.models.PartialResult or
         ~streaming.sse.retrieve.models.FinalResult]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[Stream[Union[_models1.PartialResult, _models1.FinalResult]]] = kwargs.pop("cls", None)

        _last_event_id = kwargs.pop("last_event_id", None)
        content_type = content_type or "application/json"
        _content = None
        if isinstance(request, (IOBase, bytes)):
            _content = request
        else:
            _content = json.dumps(request, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_retrieve_stream_request(
            content_type=content_type,
            content=_content,
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
        pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                try:
                    response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        def _callback(_http_response, _event):
            if _event.event == "partialResult":
                _event_json = json.loads(_event.data)
                deserialized = _deserialize(_models1.PartialResult, _event_json)
            elif _event.event == "finalResult":
                _event_json = json.loads(_event.data)
                deserialized = _deserialize(_models1.FinalResult, _event_json)
            else:
                raise ValueError(f"Unknown SSE event type: {_event.event!r}")
            return deserialized

        deserialized: Stream[Union[_models1.PartialResult, _models1.FinalResult]] = Stream(response=response, deserialization_callback=_callback, terminal_event="[DONE]")  # type: ignore
        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore
        return deserialized
