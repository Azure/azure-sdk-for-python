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

from ... import models as _models2
from ..._configuration import DatetimeClientConfiguration
from ..._utils.model_base import SdkJSONEncoder, _deserialize
from ..._utils.serialization import Deserializer, Serializer

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_property_default_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/datetime/property/default"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_rfc3339_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/datetime/property/rfc3339"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_rfc7231_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/datetime/property/rfc7231"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_unix_timestamp_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/datetime/property/unix-timestamp"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_unix_timestamp_array_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/datetime/property/unix-timestamp-array"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


class PropertyOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~encode.datetime.DatetimeClient`'s
        :attr:`property` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: DatetimeClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    def default(
        self, body: _models2.DefaultDatetimeProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.DefaultDatetimeProperty:
        """default.

        :param body: Required.
        :type body: ~encode.datetime.models.DefaultDatetimeProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: DefaultDatetimeProperty. The DefaultDatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.DefaultDatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def default(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.DefaultDatetimeProperty:
        """default.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: DefaultDatetimeProperty. The DefaultDatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.DefaultDatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def default(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.DefaultDatetimeProperty:
        """default.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: DefaultDatetimeProperty. The DefaultDatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.DefaultDatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def default(
        self, body: Union[_models2.DefaultDatetimeProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.DefaultDatetimeProperty:
        """default.

        :param body: Is one of the following types: DefaultDatetimeProperty, JSON, IO[bytes] Required.
        :type body: ~encode.datetime.models.DefaultDatetimeProperty or JSON or IO[bytes]
        :return: DefaultDatetimeProperty. The DefaultDatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.DefaultDatetimeProperty
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
        cls: ClsType[_models2.DefaultDatetimeProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_default_request(
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
            deserialized = _deserialize(_models2.DefaultDatetimeProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def rfc3339(
        self, body: _models2.Rfc3339DatetimeProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.Rfc3339DatetimeProperty:
        """rfc3339.

        :param body: Required.
        :type body: ~encode.datetime.models.Rfc3339DatetimeProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Rfc3339DatetimeProperty. The Rfc3339DatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.Rfc3339DatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def rfc3339(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.Rfc3339DatetimeProperty:
        """rfc3339.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Rfc3339DatetimeProperty. The Rfc3339DatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.Rfc3339DatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def rfc3339(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.Rfc3339DatetimeProperty:
        """rfc3339.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Rfc3339DatetimeProperty. The Rfc3339DatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.Rfc3339DatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def rfc3339(
        self, body: Union[_models2.Rfc3339DatetimeProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.Rfc3339DatetimeProperty:
        """rfc3339.

        :param body: Is one of the following types: Rfc3339DatetimeProperty, JSON, IO[bytes] Required.
        :type body: ~encode.datetime.models.Rfc3339DatetimeProperty or JSON or IO[bytes]
        :return: Rfc3339DatetimeProperty. The Rfc3339DatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.Rfc3339DatetimeProperty
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
        cls: ClsType[_models2.Rfc3339DatetimeProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_rfc3339_request(
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
            deserialized = _deserialize(_models2.Rfc3339DatetimeProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def rfc7231(
        self, body: _models2.Rfc7231DatetimeProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.Rfc7231DatetimeProperty:
        """rfc7231.

        :param body: Required.
        :type body: ~encode.datetime.models.Rfc7231DatetimeProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Rfc7231DatetimeProperty. The Rfc7231DatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.Rfc7231DatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def rfc7231(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.Rfc7231DatetimeProperty:
        """rfc7231.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Rfc7231DatetimeProperty. The Rfc7231DatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.Rfc7231DatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def rfc7231(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.Rfc7231DatetimeProperty:
        """rfc7231.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Rfc7231DatetimeProperty. The Rfc7231DatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.Rfc7231DatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def rfc7231(
        self, body: Union[_models2.Rfc7231DatetimeProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.Rfc7231DatetimeProperty:
        """rfc7231.

        :param body: Is one of the following types: Rfc7231DatetimeProperty, JSON, IO[bytes] Required.
        :type body: ~encode.datetime.models.Rfc7231DatetimeProperty or JSON or IO[bytes]
        :return: Rfc7231DatetimeProperty. The Rfc7231DatetimeProperty is compatible with MutableMapping
        :rtype: ~encode.datetime.models.Rfc7231DatetimeProperty
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
        cls: ClsType[_models2.Rfc7231DatetimeProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_rfc7231_request(
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
            deserialized = _deserialize(_models2.Rfc7231DatetimeProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def unix_timestamp(
        self, body: _models2.UnixTimestampDatetimeProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.UnixTimestampDatetimeProperty:
        """unix_timestamp.

        :param body: Required.
        :type body: ~encode.datetime.models.UnixTimestampDatetimeProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: UnixTimestampDatetimeProperty. The UnixTimestampDatetimeProperty is compatible with
         MutableMapping
        :rtype: ~encode.datetime.models.UnixTimestampDatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def unix_timestamp(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.UnixTimestampDatetimeProperty:
        """unix_timestamp.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: UnixTimestampDatetimeProperty. The UnixTimestampDatetimeProperty is compatible with
         MutableMapping
        :rtype: ~encode.datetime.models.UnixTimestampDatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def unix_timestamp(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.UnixTimestampDatetimeProperty:
        """unix_timestamp.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: UnixTimestampDatetimeProperty. The UnixTimestampDatetimeProperty is compatible with
         MutableMapping
        :rtype: ~encode.datetime.models.UnixTimestampDatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def unix_timestamp(
        self, body: Union[_models2.UnixTimestampDatetimeProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.UnixTimestampDatetimeProperty:
        """unix_timestamp.

        :param body: Is one of the following types: UnixTimestampDatetimeProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.datetime.models.UnixTimestampDatetimeProperty or JSON or IO[bytes]
        :return: UnixTimestampDatetimeProperty. The UnixTimestampDatetimeProperty is compatible with
         MutableMapping
        :rtype: ~encode.datetime.models.UnixTimestampDatetimeProperty
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
        cls: ClsType[_models2.UnixTimestampDatetimeProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_unix_timestamp_request(
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
            deserialized = _deserialize(_models2.UnixTimestampDatetimeProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def unix_timestamp_array(
        self,
        body: _models2.UnixTimestampArrayDatetimeProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models2.UnixTimestampArrayDatetimeProperty:
        """unix_timestamp_array.

        :param body: Required.
        :type body: ~encode.datetime.models.UnixTimestampArrayDatetimeProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: UnixTimestampArrayDatetimeProperty. The UnixTimestampArrayDatetimeProperty is
         compatible with MutableMapping
        :rtype: ~encode.datetime.models.UnixTimestampArrayDatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def unix_timestamp_array(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.UnixTimestampArrayDatetimeProperty:
        """unix_timestamp_array.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: UnixTimestampArrayDatetimeProperty. The UnixTimestampArrayDatetimeProperty is
         compatible with MutableMapping
        :rtype: ~encode.datetime.models.UnixTimestampArrayDatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def unix_timestamp_array(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.UnixTimestampArrayDatetimeProperty:
        """unix_timestamp_array.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: UnixTimestampArrayDatetimeProperty. The UnixTimestampArrayDatetimeProperty is
         compatible with MutableMapping
        :rtype: ~encode.datetime.models.UnixTimestampArrayDatetimeProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def unix_timestamp_array(
        self, body: Union[_models2.UnixTimestampArrayDatetimeProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.UnixTimestampArrayDatetimeProperty:
        """unix_timestamp_array.

        :param body: Is one of the following types: UnixTimestampArrayDatetimeProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.datetime.models.UnixTimestampArrayDatetimeProperty or JSON or IO[bytes]
        :return: UnixTimestampArrayDatetimeProperty. The UnixTimestampArrayDatetimeProperty is
         compatible with MutableMapping
        :rtype: ~encode.datetime.models.UnixTimestampArrayDatetimeProperty
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
        cls: ClsType[_models2.UnixTimestampArrayDatetimeProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_unix_timestamp_array_request(
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
            deserialized = _deserialize(_models2.UnixTimestampArrayDatetimeProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
