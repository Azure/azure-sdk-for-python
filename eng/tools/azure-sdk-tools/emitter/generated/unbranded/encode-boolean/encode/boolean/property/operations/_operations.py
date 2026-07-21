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
from ..._configuration import BooleanClientConfiguration
from ..._utils.model_base import SdkJSONEncoder, _deserialize
from ..._utils.serialization import Deserializer, Serializer

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_property_true_lower_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/boolean/property/true-lower"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_false_lower_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/boolean/property/false-lower"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_true_upper_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/boolean/property/true-upper"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_false_mixed_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/boolean/property/false-mixed"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


class PropertyOperations:  # pylint: disable=docstring-missing-param
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~encode.boolean.BooleanClient`'s
        :attr:`property` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: BooleanClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    def true_lower(
        self, value: _models1.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
    def true_lower(
        self, value: _types_models1.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
    def true_lower(
        self, value: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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

    def true_lower(
        self, value: Union[_models1.BoolAsStringProperty, _types_models1.BoolAsStringProperty, IO[bytes]], **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
        cls: ClsType[_models1.BoolAsStringProperty] = kwargs.pop("cls", None)

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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models1.BoolAsStringProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def false_lower(
        self, value: _models1.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
    def false_lower(
        self, value: _types_models1.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
    def false_lower(
        self, value: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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

    def false_lower(
        self, value: Union[_models1.BoolAsStringProperty, _types_models1.BoolAsStringProperty, IO[bytes]], **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
        cls: ClsType[_models1.BoolAsStringProperty] = kwargs.pop("cls", None)

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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models1.BoolAsStringProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def true_upper(
        self, value: _models1.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
    def true_upper(
        self, value: _types_models1.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
    def true_upper(
        self, value: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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

    def true_upper(
        self, value: Union[_models1.BoolAsStringProperty, _types_models1.BoolAsStringProperty, IO[bytes]], **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
        cls: ClsType[_models1.BoolAsStringProperty] = kwargs.pop("cls", None)

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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models1.BoolAsStringProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def false_mixed(
        self, value: _models1.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
    def false_mixed(
        self, value: _types_models1.BoolAsStringProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
    def false_mixed(
        self, value: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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

    def false_mixed(
        self, value: Union[_models1.BoolAsStringProperty, _types_models1.BoolAsStringProperty, IO[bytes]], **kwargs: Any
    ) -> _models1.BoolAsStringProperty:
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
        cls: ClsType[_models1.BoolAsStringProperty] = kwargs.pop("cls", None)

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

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models1.BoolAsStringProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
