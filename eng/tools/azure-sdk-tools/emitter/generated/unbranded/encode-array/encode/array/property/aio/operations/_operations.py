# pylint: disable=too-many-lines
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
from corehttp.rest import AsyncHttpResponse, HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from .... import models as _models3
from ...._utils.model_base import SdkJSONEncoder, _deserialize
from ...._utils.serialization import Deserializer, Serializer
from ....aio._configuration import ArrayClientConfiguration
from ...operations._operations import (
    build_property_comma_delimited_request,
    build_property_enum_comma_delimited_request,
    build_property_enum_newline_delimited_request,
    build_property_enum_pipe_delimited_request,
    build_property_enum_space_delimited_request,
    build_property_extensible_enum_comma_delimited_request,
    build_property_extensible_enum_newline_delimited_request,
    build_property_extensible_enum_pipe_delimited_request,
    build_property_extensible_enum_space_delimited_request,
    build_property_newline_delimited_request,
    build_property_pipe_delimited_request,
    build_property_space_delimited_request,
)

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class PropertyOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~encode.array.aio.ArrayClient`'s
        :attr:`property` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: ArrayClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    async def comma_delimited(
        self, body: _models3.CommaDelimitedArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.CommaDelimitedArrayProperty:
        """comma_delimited.

        :param body: Required.
        :type body: ~encode.array.models.CommaDelimitedArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CommaDelimitedArrayProperty. The CommaDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def comma_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.CommaDelimitedArrayProperty:
        """comma_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CommaDelimitedArrayProperty. The CommaDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def comma_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.CommaDelimitedArrayProperty:
        """comma_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CommaDelimitedArrayProperty. The CommaDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def comma_delimited(
        self, body: Union[_models3.CommaDelimitedArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.CommaDelimitedArrayProperty:
        """comma_delimited.

        :param body: Is one of the following types: CommaDelimitedArrayProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.array.models.CommaDelimitedArrayProperty or JSON or IO[bytes]
        :return: CommaDelimitedArrayProperty. The CommaDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedArrayProperty
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
        cls: ClsType[_models3.CommaDelimitedArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_comma_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.CommaDelimitedArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def space_delimited(
        self, body: _models3.SpaceDelimitedArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.SpaceDelimitedArrayProperty:
        """space_delimited.

        :param body: Required.
        :type body: ~encode.array.models.SpaceDelimitedArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SpaceDelimitedArrayProperty. The SpaceDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def space_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.SpaceDelimitedArrayProperty:
        """space_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SpaceDelimitedArrayProperty. The SpaceDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def space_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.SpaceDelimitedArrayProperty:
        """space_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SpaceDelimitedArrayProperty. The SpaceDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def space_delimited(
        self, body: Union[_models3.SpaceDelimitedArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.SpaceDelimitedArrayProperty:
        """space_delimited.

        :param body: Is one of the following types: SpaceDelimitedArrayProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.array.models.SpaceDelimitedArrayProperty or JSON or IO[bytes]
        :return: SpaceDelimitedArrayProperty. The SpaceDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedArrayProperty
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
        cls: ClsType[_models3.SpaceDelimitedArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_space_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.SpaceDelimitedArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def pipe_delimited(
        self, body: _models3.PipeDelimitedArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.PipeDelimitedArrayProperty:
        """pipe_delimited.

        :param body: Required.
        :type body: ~encode.array.models.PipeDelimitedArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: PipeDelimitedArrayProperty. The PipeDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def pipe_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.PipeDelimitedArrayProperty:
        """pipe_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: PipeDelimitedArrayProperty. The PipeDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def pipe_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.PipeDelimitedArrayProperty:
        """pipe_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: PipeDelimitedArrayProperty. The PipeDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def pipe_delimited(
        self, body: Union[_models3.PipeDelimitedArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.PipeDelimitedArrayProperty:
        """pipe_delimited.

        :param body: Is one of the following types: PipeDelimitedArrayProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.array.models.PipeDelimitedArrayProperty or JSON or IO[bytes]
        :return: PipeDelimitedArrayProperty. The PipeDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedArrayProperty
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
        cls: ClsType[_models3.PipeDelimitedArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_pipe_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.PipeDelimitedArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def newline_delimited(
        self, body: _models3.NewlineDelimitedArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.NewlineDelimitedArrayProperty:
        """newline_delimited.

        :param body: Required.
        :type body: ~encode.array.models.NewlineDelimitedArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: NewlineDelimitedArrayProperty. The NewlineDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def newline_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.NewlineDelimitedArrayProperty:
        """newline_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: NewlineDelimitedArrayProperty. The NewlineDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def newline_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.NewlineDelimitedArrayProperty:
        """newline_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: NewlineDelimitedArrayProperty. The NewlineDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def newline_delimited(
        self, body: Union[_models3.NewlineDelimitedArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.NewlineDelimitedArrayProperty:
        """newline_delimited.

        :param body: Is one of the following types: NewlineDelimitedArrayProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.array.models.NewlineDelimitedArrayProperty or JSON or IO[bytes]
        :return: NewlineDelimitedArrayProperty. The NewlineDelimitedArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedArrayProperty
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
        cls: ClsType[_models3.NewlineDelimitedArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_newline_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.NewlineDelimitedArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def enum_comma_delimited(
        self, body: _models3.CommaDelimitedEnumArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.CommaDelimitedEnumArrayProperty:
        """enum_comma_delimited.

        :param body: Required.
        :type body: ~encode.array.models.CommaDelimitedEnumArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CommaDelimitedEnumArrayProperty. The CommaDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def enum_comma_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.CommaDelimitedEnumArrayProperty:
        """enum_comma_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CommaDelimitedEnumArrayProperty. The CommaDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def enum_comma_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.CommaDelimitedEnumArrayProperty:
        """enum_comma_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CommaDelimitedEnumArrayProperty. The CommaDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def enum_comma_delimited(
        self, body: Union[_models3.CommaDelimitedEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.CommaDelimitedEnumArrayProperty:
        """enum_comma_delimited.

        :param body: Is one of the following types: CommaDelimitedEnumArrayProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.array.models.CommaDelimitedEnumArrayProperty or JSON or IO[bytes]
        :return: CommaDelimitedEnumArrayProperty. The CommaDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedEnumArrayProperty
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
        cls: ClsType[_models3.CommaDelimitedEnumArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_enum_comma_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.CommaDelimitedEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def enum_space_delimited(
        self, body: _models3.SpaceDelimitedEnumArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.SpaceDelimitedEnumArrayProperty:
        """enum_space_delimited.

        :param body: Required.
        :type body: ~encode.array.models.SpaceDelimitedEnumArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SpaceDelimitedEnumArrayProperty. The SpaceDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def enum_space_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.SpaceDelimitedEnumArrayProperty:
        """enum_space_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SpaceDelimitedEnumArrayProperty. The SpaceDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def enum_space_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.SpaceDelimitedEnumArrayProperty:
        """enum_space_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SpaceDelimitedEnumArrayProperty. The SpaceDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def enum_space_delimited(
        self, body: Union[_models3.SpaceDelimitedEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.SpaceDelimitedEnumArrayProperty:
        """enum_space_delimited.

        :param body: Is one of the following types: SpaceDelimitedEnumArrayProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.array.models.SpaceDelimitedEnumArrayProperty or JSON or IO[bytes]
        :return: SpaceDelimitedEnumArrayProperty. The SpaceDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedEnumArrayProperty
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
        cls: ClsType[_models3.SpaceDelimitedEnumArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_enum_space_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.SpaceDelimitedEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def enum_pipe_delimited(
        self, body: _models3.PipeDelimitedEnumArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.PipeDelimitedEnumArrayProperty:
        """enum_pipe_delimited.

        :param body: Required.
        :type body: ~encode.array.models.PipeDelimitedEnumArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: PipeDelimitedEnumArrayProperty. The PipeDelimitedEnumArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def enum_pipe_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.PipeDelimitedEnumArrayProperty:
        """enum_pipe_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: PipeDelimitedEnumArrayProperty. The PipeDelimitedEnumArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def enum_pipe_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.PipeDelimitedEnumArrayProperty:
        """enum_pipe_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: PipeDelimitedEnumArrayProperty. The PipeDelimitedEnumArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def enum_pipe_delimited(
        self, body: Union[_models3.PipeDelimitedEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.PipeDelimitedEnumArrayProperty:
        """enum_pipe_delimited.

        :param body: Is one of the following types: PipeDelimitedEnumArrayProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.array.models.PipeDelimitedEnumArrayProperty or JSON or IO[bytes]
        :return: PipeDelimitedEnumArrayProperty. The PipeDelimitedEnumArrayProperty is compatible with
         MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedEnumArrayProperty
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
        cls: ClsType[_models3.PipeDelimitedEnumArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_enum_pipe_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.PipeDelimitedEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def enum_newline_delimited(
        self, body: _models3.NewlineDelimitedEnumArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.NewlineDelimitedEnumArrayProperty:
        """enum_newline_delimited.

        :param body: Required.
        :type body: ~encode.array.models.NewlineDelimitedEnumArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: NewlineDelimitedEnumArrayProperty. The NewlineDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def enum_newline_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.NewlineDelimitedEnumArrayProperty:
        """enum_newline_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: NewlineDelimitedEnumArrayProperty. The NewlineDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def enum_newline_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.NewlineDelimitedEnumArrayProperty:
        """enum_newline_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: NewlineDelimitedEnumArrayProperty. The NewlineDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def enum_newline_delimited(
        self, body: Union[_models3.NewlineDelimitedEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.NewlineDelimitedEnumArrayProperty:
        """enum_newline_delimited.

        :param body: Is one of the following types: NewlineDelimitedEnumArrayProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.array.models.NewlineDelimitedEnumArrayProperty or JSON or IO[bytes]
        :return: NewlineDelimitedEnumArrayProperty. The NewlineDelimitedEnumArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedEnumArrayProperty
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
        cls: ClsType[_models3.NewlineDelimitedEnumArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_enum_newline_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.NewlineDelimitedEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def extensible_enum_comma_delimited(
        self,
        body: _models3.CommaDelimitedExtensibleEnumArrayProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models3.CommaDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_comma_delimited.

        :param body: Required.
        :type body: ~encode.array.models.CommaDelimitedExtensibleEnumArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CommaDelimitedExtensibleEnumArrayProperty. The
         CommaDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def extensible_enum_comma_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.CommaDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_comma_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CommaDelimitedExtensibleEnumArrayProperty. The
         CommaDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def extensible_enum_comma_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.CommaDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_comma_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CommaDelimitedExtensibleEnumArrayProperty. The
         CommaDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def extensible_enum_comma_delimited(
        self, body: Union[_models3.CommaDelimitedExtensibleEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.CommaDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_comma_delimited.

        :param body: Is one of the following types: CommaDelimitedExtensibleEnumArrayProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.array.models.CommaDelimitedExtensibleEnumArrayProperty or JSON or IO[bytes]
        :return: CommaDelimitedExtensibleEnumArrayProperty. The
         CommaDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.CommaDelimitedExtensibleEnumArrayProperty
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
        cls: ClsType[_models3.CommaDelimitedExtensibleEnumArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_extensible_enum_comma_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.CommaDelimitedExtensibleEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def extensible_enum_space_delimited(
        self,
        body: _models3.SpaceDelimitedExtensibleEnumArrayProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models3.SpaceDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_space_delimited.

        :param body: Required.
        :type body: ~encode.array.models.SpaceDelimitedExtensibleEnumArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SpaceDelimitedExtensibleEnumArrayProperty. The
         SpaceDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def extensible_enum_space_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.SpaceDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_space_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SpaceDelimitedExtensibleEnumArrayProperty. The
         SpaceDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def extensible_enum_space_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.SpaceDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_space_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SpaceDelimitedExtensibleEnumArrayProperty. The
         SpaceDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def extensible_enum_space_delimited(
        self, body: Union[_models3.SpaceDelimitedExtensibleEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.SpaceDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_space_delimited.

        :param body: Is one of the following types: SpaceDelimitedExtensibleEnumArrayProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.array.models.SpaceDelimitedExtensibleEnumArrayProperty or JSON or IO[bytes]
        :return: SpaceDelimitedExtensibleEnumArrayProperty. The
         SpaceDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.SpaceDelimitedExtensibleEnumArrayProperty
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
        cls: ClsType[_models3.SpaceDelimitedExtensibleEnumArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_extensible_enum_space_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.SpaceDelimitedExtensibleEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def extensible_enum_pipe_delimited(
        self,
        body: _models3.PipeDelimitedExtensibleEnumArrayProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models3.PipeDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_pipe_delimited.

        :param body: Required.
        :type body: ~encode.array.models.PipeDelimitedExtensibleEnumArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: PipeDelimitedExtensibleEnumArrayProperty. The PipeDelimitedExtensibleEnumArrayProperty
         is compatible with MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def extensible_enum_pipe_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.PipeDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_pipe_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: PipeDelimitedExtensibleEnumArrayProperty. The PipeDelimitedExtensibleEnumArrayProperty
         is compatible with MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def extensible_enum_pipe_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.PipeDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_pipe_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: PipeDelimitedExtensibleEnumArrayProperty. The PipeDelimitedExtensibleEnumArrayProperty
         is compatible with MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def extensible_enum_pipe_delimited(
        self, body: Union[_models3.PipeDelimitedExtensibleEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.PipeDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_pipe_delimited.

        :param body: Is one of the following types: PipeDelimitedExtensibleEnumArrayProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.array.models.PipeDelimitedExtensibleEnumArrayProperty or JSON or IO[bytes]
        :return: PipeDelimitedExtensibleEnumArrayProperty. The PipeDelimitedExtensibleEnumArrayProperty
         is compatible with MutableMapping
        :rtype: ~encode.array.models.PipeDelimitedExtensibleEnumArrayProperty
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
        cls: ClsType[_models3.PipeDelimitedExtensibleEnumArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_extensible_enum_pipe_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.PipeDelimitedExtensibleEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def extensible_enum_newline_delimited(
        self,
        body: _models3.NewlineDelimitedExtensibleEnumArrayProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models3.NewlineDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_newline_delimited.

        :param body: Required.
        :type body: ~encode.array.models.NewlineDelimitedExtensibleEnumArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: NewlineDelimitedExtensibleEnumArrayProperty. The
         NewlineDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def extensible_enum_newline_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.NewlineDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_newline_delimited.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: NewlineDelimitedExtensibleEnumArrayProperty. The
         NewlineDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def extensible_enum_newline_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models3.NewlineDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_newline_delimited.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: NewlineDelimitedExtensibleEnumArrayProperty. The
         NewlineDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedExtensibleEnumArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def extensible_enum_newline_delimited(
        self, body: Union[_models3.NewlineDelimitedExtensibleEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models3.NewlineDelimitedExtensibleEnumArrayProperty:
        """extensible_enum_newline_delimited.

        :param body: Is one of the following types: NewlineDelimitedExtensibleEnumArrayProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.array.models.NewlineDelimitedExtensibleEnumArrayProperty or JSON or
         IO[bytes]
        :return: NewlineDelimitedExtensibleEnumArrayProperty. The
         NewlineDelimitedExtensibleEnumArrayProperty is compatible with MutableMapping
        :rtype: ~encode.array.models.NewlineDelimitedExtensibleEnumArrayProperty
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
        cls: ClsType[_models3.NewlineDelimitedExtensibleEnumArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_extensible_enum_newline_delimited_request(
            content_type=content_type,
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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models3.NewlineDelimitedExtensibleEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
