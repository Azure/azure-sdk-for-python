# coding=utf-8
from collections.abc import MutableMapping
from io import IOBase
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
from corehttp.rest import AsyncHttpResponse, HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from ... import types
from ..._operations._operations import (
    build_usage_input_and_output_request,
    build_usage_input_request,
    build_usage_output_request,
)
from ..._utils.utils import ClientMixinABC
from .._configuration import UsageClientConfiguration

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class _UsageClientOperationsMixin(
    ClientMixinABC[AsyncPipelineClient[HttpRequest, AsyncHttpResponse], UsageClientConfiguration]
):

    @overload
    async def input(self, input: types.InputRecord, *, content_type: str = "application/json", **kwargs: Any) -> None:
        """input.

        :param input: Required.
        :type input: ~typetest.model.usage.typeddictonly.types.InputRecord
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                input = {
                    "requiredProp": "str"
                }
        """

    @overload
    async def input(self, input: IO[bytes], *, content_type: str = "application/json", **kwargs: Any) -> None:
        """input.

        :param input: Required.
        :type input: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def input(self, input: Union[types.InputRecord, IO[bytes]], **kwargs: Any) -> None:
        """input.

        :param input: Is either a InputRecord type or a IO[bytes] type. Required.
        :type input: ~typetest.model.usage.typeddictonly.types.InputRecord or IO[bytes]
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                input = {
                    "requiredProp": "str"
                }
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
        cls: ClsType[None] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(input, (IOBase, bytes)):
            _content = input
        else:
            _json = input

        _request = build_usage_input_request(
            content_type=content_type,
            json=_json,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = await self._client.pipeline.run(  # type: ignore
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore

    async def output(self, **kwargs: Any) -> types.OutputRecord:
        """output.

        :return: OutputRecord
        :rtype: ~typetest.model.usage.typeddictonly.types.OutputRecord
        :raises ~corehttp.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "requiredProp": "str"
                }
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

        cls: ClsType[types.OutputRecord] = kwargs.pop("cls", None)

        _request = build_usage_output_request(
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _decompress = kwargs.pop("decompress", True)
        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client.pipeline.run(  # type: ignore
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                try:
                    await response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def input_and_output(
        self, body: types.InputOutputRecord, *, content_type: str = "application/json", **kwargs: Any
    ) -> types.InputOutputRecord:
        """input_and_output.

        :param body: Required.
        :type body: ~typetest.model.usage.typeddictonly.types.InputOutputRecord
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: InputOutputRecord
        :rtype: ~typetest.model.usage.typeddictonly.types.InputOutputRecord
        :raises ~corehttp.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "requiredProp": "str"
                }

                # response body for status code(s): 200
                response == {
                    "requiredProp": "str"
                }
        """

    @overload
    async def input_and_output(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> types.InputOutputRecord:
        """input_and_output.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: InputOutputRecord
        :rtype: ~typetest.model.usage.typeddictonly.types.InputOutputRecord
        :raises ~corehttp.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "requiredProp": "str"
                }
        """

    async def input_and_output(
        self, body: Union[types.InputOutputRecord, IO[bytes]], **kwargs: Any
    ) -> types.InputOutputRecord:
        """input_and_output.

        :param body: Is either a InputOutputRecord type or a IO[bytes] type. Required.
        :type body: ~typetest.model.usage.typeddictonly.types.InputOutputRecord or IO[bytes]
        :return: InputOutputRecord
        :rtype: ~typetest.model.usage.typeddictonly.types.InputOutputRecord
        :raises ~corehttp.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "requiredProp": "str"
                }

                # response body for status code(s): 200
                response == {
                    "requiredProp": "str"
                }
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
        cls: ClsType[types.InputOutputRecord] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _json = body

        _request = build_usage_input_and_output_request(
            content_type=content_type,
            json=_json,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _decompress = kwargs.pop("decompress", True)
        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client.pipeline.run(  # type: ignore
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                try:
                    await response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
