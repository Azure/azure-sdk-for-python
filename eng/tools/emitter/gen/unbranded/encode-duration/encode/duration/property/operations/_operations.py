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
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.runtime import PipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from .. import models as _models1
from ..._configuration import DurationClientConfiguration
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
    _url = "/encode/duration/property/default"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_iso8601_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/iso8601"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_int32_seconds_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/int32-seconds"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_float_seconds_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/float-seconds"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_float64_seconds_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/float64-seconds"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_int32_milliseconds_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/int32-milliseconds"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_float_milliseconds_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/float-milliseconds"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_float64_milliseconds_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/float64-milliseconds"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_float_seconds_array_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/float-seconds-array"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_float_milliseconds_array_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/float-milliseconds-array"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_int32_seconds_larger_unit_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/int32-seconds-larger-unit"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_float_seconds_larger_unit_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/float-seconds-larger-unit"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_int32_milliseconds_larger_unit_request(  # pylint: disable=name-too-long
    **kwargs: Any,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/int32-milliseconds-larger-unit"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_float_milliseconds_larger_unit_request(  # pylint: disable=name-too-long
    **kwargs: Any,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/duration/property/float-milliseconds-larger-unit"

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
        :class:`~encode.duration.DurationClient`'s
        :attr:`property` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: DurationClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    def default(
        self, body: _models1.DefaultDurationProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.DefaultDurationProperty:
        """default.

        :param body: Required.
        :type body: ~encode.duration.property.models.DefaultDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: DefaultDurationProperty. The DefaultDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.DefaultDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def default(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.DefaultDurationProperty:
        """default.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: DefaultDurationProperty. The DefaultDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.DefaultDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def default(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.DefaultDurationProperty:
        """default.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: DefaultDurationProperty. The DefaultDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.DefaultDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def default(
        self, body: Union[_models1.DefaultDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.DefaultDurationProperty:
        """default.

        :param body: Is one of the following types: DefaultDurationProperty, JSON, IO[bytes] Required.
        :type body: ~encode.duration.property.models.DefaultDurationProperty or JSON or IO[bytes]
        :return: DefaultDurationProperty. The DefaultDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.DefaultDurationProperty
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
        cls: ClsType[_models1.DefaultDurationProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models1.DefaultDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def iso8601(
        self, body: _models1.ISO8601DurationProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.ISO8601DurationProperty:
        """iso8601.

        :param body: Required.
        :type body: ~encode.duration.property.models.ISO8601DurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ISO8601DurationProperty. The ISO8601DurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.ISO8601DurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def iso8601(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.ISO8601DurationProperty:
        """iso8601.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ISO8601DurationProperty. The ISO8601DurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.ISO8601DurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def iso8601(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.ISO8601DurationProperty:
        """iso8601.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ISO8601DurationProperty. The ISO8601DurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.ISO8601DurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def iso8601(
        self, body: Union[_models1.ISO8601DurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.ISO8601DurationProperty:
        """iso8601.

        :param body: Is one of the following types: ISO8601DurationProperty, JSON, IO[bytes] Required.
        :type body: ~encode.duration.property.models.ISO8601DurationProperty or JSON or IO[bytes]
        :return: ISO8601DurationProperty. The ISO8601DurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.ISO8601DurationProperty
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
        cls: ClsType[_models1.ISO8601DurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_iso8601_request(
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
            deserialized = _deserialize(_models1.ISO8601DurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def int32_seconds(
        self, body: _models1.Int32SecondsDurationProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32SecondsDurationProperty:
        """int32_seconds.

        :param body: Required.
        :type body: ~encode.duration.property.models.Int32SecondsDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32SecondsDurationProperty. The Int32SecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.Int32SecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def int32_seconds(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32SecondsDurationProperty:
        """int32_seconds.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32SecondsDurationProperty. The Int32SecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.Int32SecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def int32_seconds(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32SecondsDurationProperty:
        """int32_seconds.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32SecondsDurationProperty. The Int32SecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.Int32SecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def int32_seconds(
        self, body: Union[_models1.Int32SecondsDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.Int32SecondsDurationProperty:
        """int32_seconds.

        :param body: Is one of the following types: Int32SecondsDurationProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.duration.property.models.Int32SecondsDurationProperty or JSON or IO[bytes]
        :return: Int32SecondsDurationProperty. The Int32SecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.Int32SecondsDurationProperty
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
        cls: ClsType[_models1.Int32SecondsDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_int32_seconds_request(
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
            deserialized = _deserialize(_models1.Int32SecondsDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def float_seconds(
        self, body: _models1.FloatSecondsDurationProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatSecondsDurationProperty:
        """float_seconds.

        :param body: Required.
        :type body: ~encode.duration.property.models.FloatSecondsDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatSecondsDurationProperty. The FloatSecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_seconds(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatSecondsDurationProperty:
        """float_seconds.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatSecondsDurationProperty. The FloatSecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_seconds(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatSecondsDurationProperty:
        """float_seconds.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatSecondsDurationProperty. The FloatSecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def float_seconds(
        self, body: Union[_models1.FloatSecondsDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.FloatSecondsDurationProperty:
        """float_seconds.

        :param body: Is one of the following types: FloatSecondsDurationProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.duration.property.models.FloatSecondsDurationProperty or JSON or IO[bytes]
        :return: FloatSecondsDurationProperty. The FloatSecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsDurationProperty
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
        cls: ClsType[_models1.FloatSecondsDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_float_seconds_request(
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
            deserialized = _deserialize(_models1.FloatSecondsDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def float64_seconds(
        self, body: _models1.Float64SecondsDurationProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Float64SecondsDurationProperty:
        """float64_seconds.

        :param body: Required.
        :type body: ~encode.duration.property.models.Float64SecondsDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Float64SecondsDurationProperty. The Float64SecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.Float64SecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float64_seconds(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Float64SecondsDurationProperty:
        """float64_seconds.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Float64SecondsDurationProperty. The Float64SecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.Float64SecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float64_seconds(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Float64SecondsDurationProperty:
        """float64_seconds.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Float64SecondsDurationProperty. The Float64SecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.Float64SecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def float64_seconds(
        self, body: Union[_models1.Float64SecondsDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.Float64SecondsDurationProperty:
        """float64_seconds.

        :param body: Is one of the following types: Float64SecondsDurationProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.duration.property.models.Float64SecondsDurationProperty or JSON or
         IO[bytes]
        :return: Float64SecondsDurationProperty. The Float64SecondsDurationProperty is compatible with
         MutableMapping
        :rtype: ~encode.duration.property.models.Float64SecondsDurationProperty
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
        cls: ClsType[_models1.Float64SecondsDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_float64_seconds_request(
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
            deserialized = _deserialize(_models1.Float64SecondsDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def int32_milliseconds(
        self, body: _models1.Int32MillisecondsDurationProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32MillisecondsDurationProperty:
        """int32_milliseconds.

        :param body: Required.
        :type body: ~encode.duration.property.models.Int32MillisecondsDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32MillisecondsDurationProperty. The Int32MillisecondsDurationProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.Int32MillisecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def int32_milliseconds(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32MillisecondsDurationProperty:
        """int32_milliseconds.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32MillisecondsDurationProperty. The Int32MillisecondsDurationProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.Int32MillisecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def int32_milliseconds(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32MillisecondsDurationProperty:
        """int32_milliseconds.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32MillisecondsDurationProperty. The Int32MillisecondsDurationProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.Int32MillisecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def int32_milliseconds(
        self, body: Union[_models1.Int32MillisecondsDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.Int32MillisecondsDurationProperty:
        """int32_milliseconds.

        :param body: Is one of the following types: Int32MillisecondsDurationProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.duration.property.models.Int32MillisecondsDurationProperty or JSON or
         IO[bytes]
        :return: Int32MillisecondsDurationProperty. The Int32MillisecondsDurationProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.Int32MillisecondsDurationProperty
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
        cls: ClsType[_models1.Int32MillisecondsDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_int32_milliseconds_request(
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
            deserialized = _deserialize(_models1.Int32MillisecondsDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def float_milliseconds(
        self, body: _models1.FloatMillisecondsDurationProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatMillisecondsDurationProperty:
        """float_milliseconds.

        :param body: Required.
        :type body: ~encode.duration.property.models.FloatMillisecondsDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatMillisecondsDurationProperty. The FloatMillisecondsDurationProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_milliseconds(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatMillisecondsDurationProperty:
        """float_milliseconds.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatMillisecondsDurationProperty. The FloatMillisecondsDurationProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_milliseconds(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatMillisecondsDurationProperty:
        """float_milliseconds.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatMillisecondsDurationProperty. The FloatMillisecondsDurationProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def float_milliseconds(
        self, body: Union[_models1.FloatMillisecondsDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.FloatMillisecondsDurationProperty:
        """float_milliseconds.

        :param body: Is one of the following types: FloatMillisecondsDurationProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.duration.property.models.FloatMillisecondsDurationProperty or JSON or
         IO[bytes]
        :return: FloatMillisecondsDurationProperty. The FloatMillisecondsDurationProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsDurationProperty
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
        cls: ClsType[_models1.FloatMillisecondsDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_float_milliseconds_request(
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
            deserialized = _deserialize(_models1.FloatMillisecondsDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def float64_milliseconds(
        self,
        body: _models1.Float64MillisecondsDurationProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models1.Float64MillisecondsDurationProperty:
        """float64_milliseconds.

        :param body: Required.
        :type body: ~encode.duration.property.models.Float64MillisecondsDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Float64MillisecondsDurationProperty. The Float64MillisecondsDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Float64MillisecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float64_milliseconds(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Float64MillisecondsDurationProperty:
        """float64_milliseconds.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Float64MillisecondsDurationProperty. The Float64MillisecondsDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Float64MillisecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float64_milliseconds(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Float64MillisecondsDurationProperty:
        """float64_milliseconds.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Float64MillisecondsDurationProperty. The Float64MillisecondsDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Float64MillisecondsDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def float64_milliseconds(
        self, body: Union[_models1.Float64MillisecondsDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.Float64MillisecondsDurationProperty:
        """float64_milliseconds.

        :param body: Is one of the following types: Float64MillisecondsDurationProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.duration.property.models.Float64MillisecondsDurationProperty or JSON or
         IO[bytes]
        :return: Float64MillisecondsDurationProperty. The Float64MillisecondsDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Float64MillisecondsDurationProperty
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
        cls: ClsType[_models1.Float64MillisecondsDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_float64_milliseconds_request(
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
            deserialized = _deserialize(_models1.Float64MillisecondsDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def float_seconds_array(
        self, body: _models1.FloatSecondsDurationArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatSecondsDurationArrayProperty:
        """float_seconds_array.

        :param body: Required.
        :type body: ~encode.duration.property.models.FloatSecondsDurationArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatSecondsDurationArrayProperty. The FloatSecondsDurationArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsDurationArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_seconds_array(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatSecondsDurationArrayProperty:
        """float_seconds_array.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatSecondsDurationArrayProperty. The FloatSecondsDurationArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsDurationArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_seconds_array(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatSecondsDurationArrayProperty:
        """float_seconds_array.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatSecondsDurationArrayProperty. The FloatSecondsDurationArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsDurationArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def float_seconds_array(
        self, body: Union[_models1.FloatSecondsDurationArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.FloatSecondsDurationArrayProperty:
        """float_seconds_array.

        :param body: Is one of the following types: FloatSecondsDurationArrayProperty, JSON, IO[bytes]
         Required.
        :type body: ~encode.duration.property.models.FloatSecondsDurationArrayProperty or JSON or
         IO[bytes]
        :return: FloatSecondsDurationArrayProperty. The FloatSecondsDurationArrayProperty is compatible
         with MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsDurationArrayProperty
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
        cls: ClsType[_models1.FloatSecondsDurationArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_float_seconds_array_request(
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
            deserialized = _deserialize(_models1.FloatSecondsDurationArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def float_milliseconds_array(
        self,
        body: _models1.FloatMillisecondsDurationArrayProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models1.FloatMillisecondsDurationArrayProperty:
        """float_milliseconds_array.

        :param body: Required.
        :type body: ~encode.duration.property.models.FloatMillisecondsDurationArrayProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatMillisecondsDurationArrayProperty. The FloatMillisecondsDurationArrayProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsDurationArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_milliseconds_array(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatMillisecondsDurationArrayProperty:
        """float_milliseconds_array.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatMillisecondsDurationArrayProperty. The FloatMillisecondsDurationArrayProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsDurationArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_milliseconds_array(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatMillisecondsDurationArrayProperty:
        """float_milliseconds_array.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatMillisecondsDurationArrayProperty. The FloatMillisecondsDurationArrayProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsDurationArrayProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def float_milliseconds_array(
        self, body: Union[_models1.FloatMillisecondsDurationArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.FloatMillisecondsDurationArrayProperty:
        """float_milliseconds_array.

        :param body: Is one of the following types: FloatMillisecondsDurationArrayProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.duration.property.models.FloatMillisecondsDurationArrayProperty or JSON or
         IO[bytes]
        :return: FloatMillisecondsDurationArrayProperty. The FloatMillisecondsDurationArrayProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsDurationArrayProperty
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
        cls: ClsType[_models1.FloatMillisecondsDurationArrayProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_float_milliseconds_array_request(
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
            deserialized = _deserialize(_models1.FloatMillisecondsDurationArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def int32_seconds_larger_unit(
        self,
        body: _models1.Int32SecondsLargerUnitDurationProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models1.Int32SecondsLargerUnitDurationProperty:
        """int32_seconds_larger_unit.

        :param body: Required.
        :type body: ~encode.duration.property.models.Int32SecondsLargerUnitDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32SecondsLargerUnitDurationProperty. The Int32SecondsLargerUnitDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Int32SecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def int32_seconds_larger_unit(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32SecondsLargerUnitDurationProperty:
        """int32_seconds_larger_unit.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32SecondsLargerUnitDurationProperty. The Int32SecondsLargerUnitDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Int32SecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def int32_seconds_larger_unit(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32SecondsLargerUnitDurationProperty:
        """int32_seconds_larger_unit.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32SecondsLargerUnitDurationProperty. The Int32SecondsLargerUnitDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Int32SecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def int32_seconds_larger_unit(
        self, body: Union[_models1.Int32SecondsLargerUnitDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.Int32SecondsLargerUnitDurationProperty:
        """int32_seconds_larger_unit.

        :param body: Is one of the following types: Int32SecondsLargerUnitDurationProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.duration.property.models.Int32SecondsLargerUnitDurationProperty or JSON or
         IO[bytes]
        :return: Int32SecondsLargerUnitDurationProperty. The Int32SecondsLargerUnitDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Int32SecondsLargerUnitDurationProperty
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
        cls: ClsType[_models1.Int32SecondsLargerUnitDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_int32_seconds_larger_unit_request(
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
            deserialized = _deserialize(_models1.Int32SecondsLargerUnitDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def float_seconds_larger_unit(
        self,
        body: _models1.FloatSecondsLargerUnitDurationProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models1.FloatSecondsLargerUnitDurationProperty:
        """float_seconds_larger_unit.

        :param body: Required.
        :type body: ~encode.duration.property.models.FloatSecondsLargerUnitDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatSecondsLargerUnitDurationProperty. The FloatSecondsLargerUnitDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_seconds_larger_unit(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatSecondsLargerUnitDurationProperty:
        """float_seconds_larger_unit.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatSecondsLargerUnitDurationProperty. The FloatSecondsLargerUnitDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_seconds_larger_unit(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatSecondsLargerUnitDurationProperty:
        """float_seconds_larger_unit.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatSecondsLargerUnitDurationProperty. The FloatSecondsLargerUnitDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def float_seconds_larger_unit(
        self, body: Union[_models1.FloatSecondsLargerUnitDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.FloatSecondsLargerUnitDurationProperty:
        """float_seconds_larger_unit.

        :param body: Is one of the following types: FloatSecondsLargerUnitDurationProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.duration.property.models.FloatSecondsLargerUnitDurationProperty or JSON or
         IO[bytes]
        :return: FloatSecondsLargerUnitDurationProperty. The FloatSecondsLargerUnitDurationProperty is
         compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatSecondsLargerUnitDurationProperty
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
        cls: ClsType[_models1.FloatSecondsLargerUnitDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_float_seconds_larger_unit_request(
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
            deserialized = _deserialize(_models1.FloatSecondsLargerUnitDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def int32_milliseconds_larger_unit(
        self,
        body: _models1.Int32MillisecondsLargerUnitDurationProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models1.Int32MillisecondsLargerUnitDurationProperty:
        """int32_milliseconds_larger_unit.

        :param body: Required.
        :type body: ~encode.duration.property.models.Int32MillisecondsLargerUnitDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32MillisecondsLargerUnitDurationProperty. The
         Int32MillisecondsLargerUnitDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Int32MillisecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def int32_milliseconds_larger_unit(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32MillisecondsLargerUnitDurationProperty:
        """int32_milliseconds_larger_unit.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32MillisecondsLargerUnitDurationProperty. The
         Int32MillisecondsLargerUnitDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Int32MillisecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def int32_milliseconds_larger_unit(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.Int32MillisecondsLargerUnitDurationProperty:
        """int32_milliseconds_larger_unit.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Int32MillisecondsLargerUnitDurationProperty. The
         Int32MillisecondsLargerUnitDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Int32MillisecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def int32_milliseconds_larger_unit(
        self, body: Union[_models1.Int32MillisecondsLargerUnitDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.Int32MillisecondsLargerUnitDurationProperty:
        """int32_milliseconds_larger_unit.

        :param body: Is one of the following types: Int32MillisecondsLargerUnitDurationProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.duration.property.models.Int32MillisecondsLargerUnitDurationProperty or
         JSON or IO[bytes]
        :return: Int32MillisecondsLargerUnitDurationProperty. The
         Int32MillisecondsLargerUnitDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.Int32MillisecondsLargerUnitDurationProperty
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
        cls: ClsType[_models1.Int32MillisecondsLargerUnitDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_int32_milliseconds_larger_unit_request(
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
            deserialized = _deserialize(_models1.Int32MillisecondsLargerUnitDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def float_milliseconds_larger_unit(
        self,
        body: _models1.FloatMillisecondsLargerUnitDurationProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models1.FloatMillisecondsLargerUnitDurationProperty:
        """float_milliseconds_larger_unit.

        :param body: Required.
        :type body: ~encode.duration.property.models.FloatMillisecondsLargerUnitDurationProperty
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatMillisecondsLargerUnitDurationProperty. The
         FloatMillisecondsLargerUnitDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_milliseconds_larger_unit(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatMillisecondsLargerUnitDurationProperty:
        """float_milliseconds_larger_unit.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatMillisecondsLargerUnitDurationProperty. The
         FloatMillisecondsLargerUnitDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def float_milliseconds_larger_unit(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models1.FloatMillisecondsLargerUnitDurationProperty:
        """float_milliseconds_larger_unit.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: FloatMillisecondsLargerUnitDurationProperty. The
         FloatMillisecondsLargerUnitDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsLargerUnitDurationProperty
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def float_milliseconds_larger_unit(
        self, body: Union[_models1.FloatMillisecondsLargerUnitDurationProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models1.FloatMillisecondsLargerUnitDurationProperty:
        """float_milliseconds_larger_unit.

        :param body: Is one of the following types: FloatMillisecondsLargerUnitDurationProperty, JSON,
         IO[bytes] Required.
        :type body: ~encode.duration.property.models.FloatMillisecondsLargerUnitDurationProperty or
         JSON or IO[bytes]
        :return: FloatMillisecondsLargerUnitDurationProperty. The
         FloatMillisecondsLargerUnitDurationProperty is compatible with MutableMapping
        :rtype: ~encode.duration.property.models.FloatMillisecondsLargerUnitDurationProperty
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
        cls: ClsType[_models1.FloatMillisecondsLargerUnitDurationProperty] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_property_float_milliseconds_larger_unit_request(
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
            deserialized = _deserialize(_models1.FloatMillisecondsLargerUnitDurationProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
