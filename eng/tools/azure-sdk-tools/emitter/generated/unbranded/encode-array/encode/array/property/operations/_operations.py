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

from ... import models as _models2
from ..._configuration import ArrayClientConfiguration
from ..._utils.model_base import SdkJSONEncoder, _deserialize
from ..._utils.serialization import Deserializer, Serializer

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_property_comma_delimited_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/comma-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_space_delimited_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/space-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_pipe_delimited_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/pipe-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_newline_delimited_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/newline-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_enum_comma_delimited_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/enum/comma-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_enum_space_delimited_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/enum/space-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_enum_pipe_delimited_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/enum/pipe-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_enum_newline_delimited_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/enum/newline-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_extensible_enum_comma_delimited_request(  # pylint: disable=name-too-long
    **kwargs: Any,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/extensible-enum/comma-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_extensible_enum_space_delimited_request(  # pylint: disable=name-too-long
    **kwargs: Any,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/extensible-enum/space-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_extensible_enum_pipe_delimited_request(  # pylint: disable=name-too-long
    **kwargs: Any,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/extensible-enum/pipe-delimited"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_property_extensible_enum_newline_delimited_request(  # pylint: disable=name-too-long
    **kwargs: Any,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/encode/array/property/extensible-enum/newline-delimited"

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
        :class:`~encode.array.ArrayClient`'s
        :attr:`property` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: ArrayClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    def comma_delimited(
        self, body: _models2.CommaDelimitedArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.CommaDelimitedArrayProperty:
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
    def comma_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.CommaDelimitedArrayProperty:
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
    def comma_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.CommaDelimitedArrayProperty:
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

    def comma_delimited(
        self, body: Union[_models2.CommaDelimitedArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.CommaDelimitedArrayProperty:
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
        cls: ClsType[_models2.CommaDelimitedArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.CommaDelimitedArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def space_delimited(
        self, body: _models2.SpaceDelimitedArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.SpaceDelimitedArrayProperty:
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
    def space_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.SpaceDelimitedArrayProperty:
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
    def space_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.SpaceDelimitedArrayProperty:
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

    def space_delimited(
        self, body: Union[_models2.SpaceDelimitedArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.SpaceDelimitedArrayProperty:
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
        cls: ClsType[_models2.SpaceDelimitedArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.SpaceDelimitedArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def pipe_delimited(
        self, body: _models2.PipeDelimitedArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.PipeDelimitedArrayProperty:
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
    def pipe_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.PipeDelimitedArrayProperty:
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
    def pipe_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.PipeDelimitedArrayProperty:
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

    def pipe_delimited(
        self, body: Union[_models2.PipeDelimitedArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.PipeDelimitedArrayProperty:
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
        cls: ClsType[_models2.PipeDelimitedArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.PipeDelimitedArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def newline_delimited(
        self, body: _models2.NewlineDelimitedArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.NewlineDelimitedArrayProperty:
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
    def newline_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.NewlineDelimitedArrayProperty:
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
    def newline_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.NewlineDelimitedArrayProperty:
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

    def newline_delimited(
        self, body: Union[_models2.NewlineDelimitedArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.NewlineDelimitedArrayProperty:
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
        cls: ClsType[_models2.NewlineDelimitedArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.NewlineDelimitedArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def enum_comma_delimited(
        self, body: _models2.CommaDelimitedEnumArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.CommaDelimitedEnumArrayProperty:
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
    def enum_comma_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.CommaDelimitedEnumArrayProperty:
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
    def enum_comma_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.CommaDelimitedEnumArrayProperty:
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

    def enum_comma_delimited(
        self, body: Union[_models2.CommaDelimitedEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.CommaDelimitedEnumArrayProperty:
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
        cls: ClsType[_models2.CommaDelimitedEnumArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.CommaDelimitedEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def enum_space_delimited(
        self, body: _models2.SpaceDelimitedEnumArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.SpaceDelimitedEnumArrayProperty:
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
    def enum_space_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.SpaceDelimitedEnumArrayProperty:
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
    def enum_space_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.SpaceDelimitedEnumArrayProperty:
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

    def enum_space_delimited(
        self, body: Union[_models2.SpaceDelimitedEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.SpaceDelimitedEnumArrayProperty:
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
        cls: ClsType[_models2.SpaceDelimitedEnumArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.SpaceDelimitedEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def enum_pipe_delimited(
        self, body: _models2.PipeDelimitedEnumArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.PipeDelimitedEnumArrayProperty:
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
    def enum_pipe_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.PipeDelimitedEnumArrayProperty:
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
    def enum_pipe_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.PipeDelimitedEnumArrayProperty:
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

    def enum_pipe_delimited(
        self, body: Union[_models2.PipeDelimitedEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.PipeDelimitedEnumArrayProperty:
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
        cls: ClsType[_models2.PipeDelimitedEnumArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.PipeDelimitedEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def enum_newline_delimited(
        self, body: _models2.NewlineDelimitedEnumArrayProperty, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.NewlineDelimitedEnumArrayProperty:
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
    def enum_newline_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.NewlineDelimitedEnumArrayProperty:
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
    def enum_newline_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.NewlineDelimitedEnumArrayProperty:
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

    def enum_newline_delimited(
        self, body: Union[_models2.NewlineDelimitedEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.NewlineDelimitedEnumArrayProperty:
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
        cls: ClsType[_models2.NewlineDelimitedEnumArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.NewlineDelimitedEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def extensible_enum_comma_delimited(
        self,
        body: _models2.CommaDelimitedExtensibleEnumArrayProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models2.CommaDelimitedExtensibleEnumArrayProperty:
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
    def extensible_enum_comma_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.CommaDelimitedExtensibleEnumArrayProperty:
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
    def extensible_enum_comma_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.CommaDelimitedExtensibleEnumArrayProperty:
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

    def extensible_enum_comma_delimited(
        self, body: Union[_models2.CommaDelimitedExtensibleEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.CommaDelimitedExtensibleEnumArrayProperty:
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
        cls: ClsType[_models2.CommaDelimitedExtensibleEnumArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.CommaDelimitedExtensibleEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def extensible_enum_space_delimited(
        self,
        body: _models2.SpaceDelimitedExtensibleEnumArrayProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models2.SpaceDelimitedExtensibleEnumArrayProperty:
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
    def extensible_enum_space_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.SpaceDelimitedExtensibleEnumArrayProperty:
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
    def extensible_enum_space_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.SpaceDelimitedExtensibleEnumArrayProperty:
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

    def extensible_enum_space_delimited(
        self, body: Union[_models2.SpaceDelimitedExtensibleEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.SpaceDelimitedExtensibleEnumArrayProperty:
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
        cls: ClsType[_models2.SpaceDelimitedExtensibleEnumArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.SpaceDelimitedExtensibleEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def extensible_enum_pipe_delimited(
        self,
        body: _models2.PipeDelimitedExtensibleEnumArrayProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models2.PipeDelimitedExtensibleEnumArrayProperty:
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
    def extensible_enum_pipe_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.PipeDelimitedExtensibleEnumArrayProperty:
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
    def extensible_enum_pipe_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.PipeDelimitedExtensibleEnumArrayProperty:
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

    def extensible_enum_pipe_delimited(
        self, body: Union[_models2.PipeDelimitedExtensibleEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.PipeDelimitedExtensibleEnumArrayProperty:
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
        cls: ClsType[_models2.PipeDelimitedExtensibleEnumArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.PipeDelimitedExtensibleEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def extensible_enum_newline_delimited(
        self,
        body: _models2.NewlineDelimitedExtensibleEnumArrayProperty,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models2.NewlineDelimitedExtensibleEnumArrayProperty:
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
    def extensible_enum_newline_delimited(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.NewlineDelimitedExtensibleEnumArrayProperty:
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
    def extensible_enum_newline_delimited(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models2.NewlineDelimitedExtensibleEnumArrayProperty:
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

    def extensible_enum_newline_delimited(
        self, body: Union[_models2.NewlineDelimitedExtensibleEnumArrayProperty, JSON, IO[bytes]], **kwargs: Any
    ) -> _models2.NewlineDelimitedExtensibleEnumArrayProperty:
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
        cls: ClsType[_models2.NewlineDelimitedExtensibleEnumArrayProperty] = kwargs.pop("cls", None)

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
            deserialized = _deserialize(_models2.NewlineDelimitedExtensibleEnumArrayProperty, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
