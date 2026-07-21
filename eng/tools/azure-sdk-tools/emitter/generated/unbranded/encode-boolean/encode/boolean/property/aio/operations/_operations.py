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

from ... import models as _models2, types as _types_models2
from ...._utils.model_base import SdkJSONEncoder, _deserialize
from ...._utils.serialization import Deserializer, Serializer
from ....aio._configuration import BooleanClientConfiguration
from ...operations._operations import (
    build_property_false_lower_request,
    build_property_false_mixed_request,
    build_property_true_lower_request,
    build_property_true_upper_request,
)

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class PropertyOperations:  # pylint: disable=docstring-missing-param
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~encode.boolean.aio.BooleanClient`'s
        :attr:`property` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: BooleanClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    async def true_lower(
        self, value: _models2.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """true_lower.

        :param value: Required.
        :type value: ~encode.boolean.property.models.BoolAsStringProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def true_lower(
        self, value: _types_models2.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """true_lower.

        :param value: Required.
        :type value: ~encode.boolean.property.types.BoolAsStringProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def true_lower(
        self, value: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """true_lower.

        :param value: Required.
        :type value: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def true_lower(
        self, value: Union[_models2.BoolAsStringProperty, _types_models2.BoolAsStringProperty, IO[bytes]], **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """true_lower.

        :param value: Is either a BoolAsStringProperty type or a IO[bytes] type. Required.
        :type value: ~encode.boolean.property.models.BoolAsStringProperty or
         ~encode.boolean.property.types.BoolAsStringProperty or IO[bytes]
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
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
        cls: ClsType[_models2.BoolAsStringProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(value, (IOBase, bytes)):
            _content = value
        else:
            _content = json.dumps(value, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_true_lower_request(
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
            deserialized = _deserialize(_models2.BoolAsStringProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def false_lower(
        self, value: _models2.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """false_lower.

        :param value: Required.
        :type value: ~encode.boolean.property.models.BoolAsStringProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def false_lower(
        self, value: _types_models2.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """false_lower.

        :param value: Required.
        :type value: ~encode.boolean.property.types.BoolAsStringProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def false_lower(
        self, value: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """false_lower.

        :param value: Required.
        :type value: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def false_lower(
        self, value: Union[_models2.BoolAsStringProperty, _types_models2.BoolAsStringProperty, IO[bytes]], **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """false_lower.

        :param value: Is either a BoolAsStringProperty type or a IO[bytes] type. Required.
        :type value: ~encode.boolean.property.models.BoolAsStringProperty or
         ~encode.boolean.property.types.BoolAsStringProperty or IO[bytes]
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
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
        cls: ClsType[_models2.BoolAsStringProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(value, (IOBase, bytes)):
            _content = value
        else:
            _content = json.dumps(value, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_false_lower_request(
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
            deserialized = _deserialize(_models2.BoolAsStringProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def true_upper(
        self, value: _models2.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """true_upper.

        :param value: Required.
        :type value: ~encode.boolean.property.models.BoolAsStringProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def true_upper(
        self, value: _types_models2.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """true_upper.

        :param value: Required.
        :type value: ~encode.boolean.property.types.BoolAsStringProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def true_upper(
        self, value: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """true_upper.

        :param value: Required.
        :type value: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def true_upper(
        self, value: Union[_models2.BoolAsStringProperty, _types_models2.BoolAsStringProperty, IO[bytes]], **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """true_upper.

        :param value: Is either a BoolAsStringProperty type or a IO[bytes] type. Required.
        :type value: ~encode.boolean.property.models.BoolAsStringProperty or
         ~encode.boolean.property.types.BoolAsStringProperty or IO[bytes]
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
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
        cls: ClsType[_models2.BoolAsStringProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(value, (IOBase, bytes)):
            _content = value
        else:
            _content = json.dumps(value, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_true_upper_request(
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
            deserialized = _deserialize(_models2.BoolAsStringProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def false_mixed(
        self, value: _models2.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """false_mixed.

        :param value: Required.
        :type value: ~encode.boolean.property.models.BoolAsStringProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def false_mixed(
        self, value: _types_models2.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """false_mixed.

        :param value: Required.
        :type value: ~encode.boolean.property.types.BoolAsStringProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def false_mixed(
        self, value: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """false_mixed.

        :param value: Required.
        :type value: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def false_mixed(
        self, value: Union[_models2.BoolAsStringProperty, _types_models2.BoolAsStringProperty, IO[bytes]], **kwargs: Any
    ) -> _models2.BoolAsStringProperty:
        """false_mixed.

        :param value: Is either a BoolAsStringProperty type or a IO[bytes] type. Required.
        :type value: ~encode.boolean.property.models.BoolAsStringProperty or
         ~encode.boolean.property.types.BoolAsStringProperty or IO[bytes]
        :return: BoolAsStringProperty. The BoolAsStringProperty is compatible with MutableMapping
        :rtype: ~encode.boolean.property.models.BoolAsStringProperty
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
        cls: ClsType[_models2.BoolAsStringProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(value, (IOBase, bytes)):
            _content = value
        else:
            _content = json.dumps(value, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_false_mixed_request(
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
            deserialized = _deserialize(_models2.BoolAsStringProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
