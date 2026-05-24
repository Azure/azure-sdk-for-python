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
    map_error,
)
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.runtime import PipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from ..._configuration import BytesClientConfiguration
from ..._utils.model_base import SdkJSONEncoder
from ..._utils.serialization import Deserializer, Serializer

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_request_body_default_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: str = kwargs.pop("content_type")
    # Construct URL
    _url = "/encode/bytes/body/request/default"

    # Construct headers
    _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_request_body_octet_stream_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: str = kwargs.pop("content_type")
    # Construct URL
    _url = "/encode/bytes/body/request/octet-stream"

    # Construct headers
    _headers["content-type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_request_body_custom_content_type_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: str = kwargs.pop("content_type")
    # Construct URL
    _url = "/encode/bytes/body/request/custom-content-type"

    # Construct headers
    _headers["content-type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_request_body_base64_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: str = kwargs.pop("content_type")
    # Construct URL
    _url = "/encode/bytes/body/request/base64"

    # Construct headers
    _headers["content-type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


def build_request_body_base64_url_request(**kwargs: Any) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: str = kwargs.pop("content_type")
    # Construct URL
    _url = "/encode/bytes/body/request/base64url"

    # Construct headers
    _headers["content-type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


class RequestBodyOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~encode.bytes.BytesClient`'s
        :attr:`request_body` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: BytesClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    def default(self, value: bytes, **kwargs: Any) -> None:  # pylint: disable=inconsistent-return-statements
        """default.

        :param value: Required.
        :type value: bytes
        :return: None
        :rtype: None
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

        content_type: str = kwargs.pop("content_type", _headers.pop("Content-Type", "application/octet-stream"))
        cls: ClsType[None] = kwargs.pop("cls", None)

        _content = value

        _request = build_request_body_default_request(
            content_type=content_type,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore

    def octet_stream(self, value: bytes, **kwargs: Any) -> None:  # pylint: disable=inconsistent-return-statements
        """octet_stream.

        :param value: Required.
        :type value: bytes
        :return: None
        :rtype: None
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

        content_type: str = kwargs.pop("content_type", _headers.pop("content-type", "application/octet-stream"))
        cls: ClsType[None] = kwargs.pop("cls", None)

        _content = value

        _request = build_request_body_octet_stream_request(
            content_type=content_type,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore

    def custom_content_type(  # pylint: disable=inconsistent-return-statements
        self, value: bytes, **kwargs: Any
    ) -> None:
        """custom_content_type.

        :param value: Required.
        :type value: bytes
        :return: None
        :rtype: None
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

        content_type: str = kwargs.pop("content_type", _headers.pop("content-type", "image/png"))
        cls: ClsType[None] = kwargs.pop("cls", None)

        _content = value

        _request = build_request_body_custom_content_type_request(
            content_type=content_type,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore

    def base64(self, value: bytes, **kwargs: Any) -> None:  # pylint: disable=inconsistent-return-statements
        """base64.

        :param value: Required.
        :type value: bytes
        :return: None
        :rtype: None
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

        content_type: str = kwargs.pop("content_type", _headers.pop("content-type", "application/json"))
        cls: ClsType[None] = kwargs.pop("cls", None)

        _content = json.dumps(value, cls=SdkJSONEncoder, exclude_readonly=True, format="base64")  # type: ignore

        _request = build_request_body_base64_request(
            content_type=content_type,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore

    def base64_url(self, value: bytes, **kwargs: Any) -> None:  # pylint: disable=inconsistent-return-statements
        """base64_url.

        :param value: Required.
        :type value: bytes
        :return: None
        :rtype: None
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

        content_type: str = kwargs.pop("content_type", _headers.pop("content-type", "application/json"))
        cls: ClsType[None] = kwargs.pop("cls", None)

        _content = json.dumps(value, cls=SdkJSONEncoder, exclude_readonly=True, format="base64url")  # type: ignore

        _request = build_request_body_base64_url_request(
            content_type=content_type,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore
