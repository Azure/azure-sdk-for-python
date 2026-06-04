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
    map_error,
)
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.runtime import PipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from .. import models as _models1
from ..._configuration import SpreadClientConfiguration
from ..._utils.model_base import SdkJSONEncoder
from ..._utils.serialization import Deserializer, Serializer

JSON = MutableMapping[str, Any]
_Unset: Any = object()
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_model_spread_as_request_body_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    # Construct URL
    _url = "/parameters/spread/model/request-body"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="PUT", url=_url, headers=_headers, **kwargs)


def build_model_spread_composite_request_only_with_body_request(  # pylint: disable=name-too-long
    **kwargs: Any,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    # Construct URL
    _url = "/parameters/spread/model/composite-request-only-with-body"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="PUT", url=_url, headers=_headers, **kwargs)


def build_model_spread_composite_request_without_body_request(  # pylint: disable=name-too-long
    name: str, *, test_header: str, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    # Construct URL
    _url = "/parameters/spread/model/composite-request-without-body/{name}"
    path_format_arguments = {
        "name": _SERIALIZER.url("name", name, "str"),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct headers
    _headers["test-header"] = _SERIALIZER.header("test_header", test_header, "str")

    return HttpRequest(method="PUT", url=_url, headers=_headers, **kwargs)


def build_model_spread_composite_request_request(  # pylint: disable=name-too-long
    name: str, *, test_header: str, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    # Construct URL
    _url = "/parameters/spread/model/composite-request/{name}"
    path_format_arguments = {
        "name": _SERIALIZER.url("name", name, "str"),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct headers
    _headers["test-header"] = _SERIALIZER.header("test_header", test_header, "str")
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="PUT", url=_url, headers=_headers, **kwargs)


def build_model_spread_composite_request_mix_request(  # pylint: disable=name-too-long
    name: str, *, test_header: str, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    # Construct URL
    _url = "/parameters/spread/model/composite-request-mix/{name}"
    path_format_arguments = {
        "name": _SERIALIZER.url("name", name, "str"),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct headers
    _headers["test-header"] = _SERIALIZER.header("test_header", test_header, "str")
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="PUT", url=_url, headers=_headers, **kwargs)


class ModelOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~parameters.spread.SpreadClient`'s
        :attr:`model` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: SpreadClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    def spread_as_request_body(self, *, name: str, content_type: str = "application/json", **kwargs: Any) -> None:
        """spread_as_request_body.

        :keyword name: Required.
        :paramtype name: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def spread_as_request_body(self, body: JSON, *, content_type: str = "application/json", **kwargs: Any) -> None:
        """spread_as_request_body.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def spread_as_request_body(self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any) -> None:
        """spread_as_request_body.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def spread_as_request_body(  # pylint: disable=inconsistent-return-statements
        self, body: Union[JSON, IO[bytes]] = _Unset, *, name: str = _Unset, **kwargs: Any
    ) -> None:
        """spread_as_request_body.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword name: Required.
        :paramtype name: str
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[None] = kwargs.pop("cls", None)

        if body is _Unset:
            if name is _Unset:
                raise TypeError("missing required argument: name")
            body = {"name": name}
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_model_spread_as_request_body_request(
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

    @overload
    def spread_composite_request_only_with_body(
        self, body: _models1.BodyParameter, *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """spread_composite_request_only_with_body.

        :param body: Required.
        :type body: ~parameters.spread.model.models.BodyParameter
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def spread_composite_request_only_with_body(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """spread_composite_request_only_with_body.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def spread_composite_request_only_with_body(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """spread_composite_request_only_with_body.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def spread_composite_request_only_with_body(  # pylint: disable=inconsistent-return-statements
        self, body: Union[_models1.BodyParameter, JSON, IO[bytes]], **kwargs: Any
    ) -> None:
        """spread_composite_request_only_with_body.

        :param body: Is one of the following types: BodyParameter, JSON, IO[bytes] Required.
        :type body: ~parameters.spread.model.models.BodyParameter or JSON or IO[bytes]
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[None] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_model_spread_composite_request_only_with_body_request(
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

    def spread_composite_request_without_body(  # pylint: disable=inconsistent-return-statements
        self, name: str, *, test_header: str, **kwargs: Any
    ) -> None:
        """spread_composite_request_without_body.

        :param name: Required.
        :type name: str
        :keyword test_header: Required.
        :paramtype test_header: str
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[None] = kwargs.pop("cls", None)

        _request = build_model_spread_composite_request_without_body_request(
            name=name,
            test_header=test_header,
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

    @overload
    def spread_composite_request(
        self,
        name: str,
        body: _models1.BodyParameter,
        *,
        test_header: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> None:
        """spread_composite_request.

        :param name: Required.
        :type name: str
        :param body: Required.
        :type body: ~parameters.spread.model.models.BodyParameter
        :keyword test_header: Required.
        :paramtype test_header: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def spread_composite_request(
        self, name: str, body: JSON, *, test_header: str, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """spread_composite_request.

        :param name: Required.
        :type name: str
        :param body: Required.
        :type body: JSON
        :keyword test_header: Required.
        :paramtype test_header: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def spread_composite_request(
        self, name: str, body: IO[bytes], *, test_header: str, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """spread_composite_request.

        :param name: Required.
        :type name: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword test_header: Required.
        :paramtype test_header: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def spread_composite_request(  # pylint: disable=inconsistent-return-statements
        self, name: str, body: Union[_models1.BodyParameter, JSON, IO[bytes]], *, test_header: str, **kwargs: Any
    ) -> None:
        """spread_composite_request.

        :param name: Required.
        :type name: str
        :param body: Is one of the following types: BodyParameter, JSON, IO[bytes] Required.
        :type body: ~parameters.spread.model.models.BodyParameter or JSON or IO[bytes]
        :keyword test_header: Required.
        :paramtype test_header: str
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[None] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_model_spread_composite_request_request(
            name=name,
            test_header=test_header,
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

    @overload
    def spread_composite_request_mix(
        self, name: str, *, test_header: str, prop: str, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """spread_composite_request_mix.

        :param name: Required.
        :type name: str
        :keyword test_header: Required.
        :paramtype test_header: str
        :keyword prop: Required.
        :paramtype prop: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def spread_composite_request_mix(
        self, name: str, body: JSON, *, test_header: str, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """spread_composite_request_mix.

        :param name: Required.
        :type name: str
        :param body: Required.
        :type body: JSON
        :keyword test_header: Required.
        :paramtype test_header: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def spread_composite_request_mix(
        self, name: str, body: IO[bytes], *, test_header: str, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """spread_composite_request_mix.

        :param name: Required.
        :type name: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword test_header: Required.
        :paramtype test_header: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def spread_composite_request_mix(  # pylint: disable=inconsistent-return-statements
        self, name: str, body: Union[JSON, IO[bytes]] = _Unset, *, test_header: str, prop: str = _Unset, **kwargs: Any
    ) -> None:
        """spread_composite_request_mix.

        :param name: Required.
        :type name: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword test_header: Required.
        :paramtype test_header: str
        :keyword prop: Required.
        :paramtype prop: str
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[None] = kwargs.pop("cls", None)

        if body is _Unset:
            if prop is _Unset:
                raise TypeError("missing required argument: prop")
            body = {"prop": prop}
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_model_spread_composite_request_mix_request(
            name=name,
            test_header=test_header,
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
