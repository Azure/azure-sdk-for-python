# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
from collections.abc import MutableMapping
from typing import Any, Callable, Optional, TypeVar

from corehttp.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from corehttp.paging import ItemPaged
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.runtime import PipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from .... import models as _models3
from ...._configuration import PageableClientConfiguration
from ...._utils.model_base import _deserialize
from ...._utils.serialization import Deserializer, Serializer

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_server_driven_pagination_continuation_token_request_query_response_body_request(  # pylint: disable=name-too-long
    *, token: Optional[str] = None, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/payload/pageable/server-driven-pagination/continuationtoken/request-query-response-body"

    # Construct parameters
    if token is not None:
        _params["token"] = _SERIALIZER.query("token", token, "str")
    if bar is not None:
        _params["bar"] = _SERIALIZER.query("bar", bar, "str")

    # Construct headers
    if foo is not None:
        _headers["foo"] = _SERIALIZER.header("foo", foo, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)


def build_server_driven_pagination_continuation_token_request_header_response_body_request(  # pylint: disable=name-too-long
    *, token: Optional[str] = None, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/payload/pageable/server-driven-pagination/continuationtoken/request-header-response-body"

    # Construct parameters
    if bar is not None:
        _params["bar"] = _SERIALIZER.query("bar", bar, "str")

    # Construct headers
    if token is not None:
        _headers["token"] = _SERIALIZER.header("token", token, "str")
    if foo is not None:
        _headers["foo"] = _SERIALIZER.header("foo", foo, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)


def build_server_driven_pagination_continuation_token_request_query_response_header_request(  # pylint: disable=name-too-long
    *, token: Optional[str] = None, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/payload/pageable/server-driven-pagination/continuationtoken/request-query-response-header"

    # Construct parameters
    if token is not None:
        _params["token"] = _SERIALIZER.query("token", token, "str")
    if bar is not None:
        _params["bar"] = _SERIALIZER.query("bar", bar, "str")

    # Construct headers
    if foo is not None:
        _headers["foo"] = _SERIALIZER.header("foo", foo, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)


def build_server_driven_pagination_continuation_token_request_header_response_header_request(  # pylint: disable=name-too-long
    *, token: Optional[str] = None, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/payload/pageable/server-driven-pagination/continuationtoken/request-header-response-header"

    # Construct parameters
    if bar is not None:
        _params["bar"] = _SERIALIZER.query("bar", bar, "str")

    # Construct headers
    if token is not None:
        _headers["token"] = _SERIALIZER.header("token", token, "str")
    if foo is not None:
        _headers["foo"] = _SERIALIZER.header("foo", foo, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)


def build_server_driven_pagination_continuation_token_request_query_nested_response_body_request(  # pylint: disable=name-too-long
    *, token: Optional[str] = None, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/payload/pageable/server-driven-pagination/continuationtoken/request-query-nested-response-body"

    # Construct parameters
    if token is not None:
        _params["token"] = _SERIALIZER.query("token", token, "str")
    if bar is not None:
        _params["bar"] = _SERIALIZER.query("bar", bar, "str")

    # Construct headers
    if foo is not None:
        _headers["foo"] = _SERIALIZER.header("foo", foo, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)


def build_server_driven_pagination_continuation_token_request_header_nested_response_body_request(  # pylint: disable=name-too-long
    *, token: Optional[str] = None, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/payload/pageable/server-driven-pagination/continuationtoken/request-header-nested-response-body"

    # Construct parameters
    if bar is not None:
        _params["bar"] = _SERIALIZER.query("bar", bar, "str")

    # Construct headers
    if token is not None:
        _headers["token"] = _SERIALIZER.header("token", token, "str")
    if foo is not None:
        _headers["foo"] = _SERIALIZER.header("foo", foo, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)


class ServerDrivenPaginationContinuationTokenOperations:  # pylint: disable=name-too-long
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~payload.pageable.PageableClient`'s
        :attr:`continuation_token` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: PageableClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    def request_query_response_body(
        self, *, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
    ) -> ItemPaged["_models3.Pet"]:
        """request_query_response_body.

        :keyword foo: Default value is None.
        :paramtype foo: str
        :keyword bar: Default value is None.
        :paramtype bar: str
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[list[_models3.Pet]] = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(_continuation_token=None):

            _request = build_server_driven_pagination_continuation_token_request_query_response_body_request(
                token=_continuation_token,
                foo=foo,
                bar=bar,
                headers=_headers,
                params=_params,
            )
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            _request.url = self._client.format_url(_request.url, **path_format_arguments)
            return _request

        def extract_data(pipeline_response):
            deserialized = pipeline_response.http_response.json()
            list_of_elem = _deserialize(
                list[_models3.Pet],
                deserialized.get("pets", []),
            )
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            return deserialized.get("nextToken") or None, iter(list_of_elem)

        def get_next(_continuation_token=None):
            _request = prepare_request(_continuation_token)

            _stream = False
            pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            return pipeline_response

        return ItemPaged(get_next, extract_data)

    def request_header_response_body(
        self, *, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
    ) -> ItemPaged["_models3.Pet"]:
        """request_header_response_body.

        :keyword foo: Default value is None.
        :paramtype foo: str
        :keyword bar: Default value is None.
        :paramtype bar: str
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[list[_models3.Pet]] = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(_continuation_token=None):

            _request = build_server_driven_pagination_continuation_token_request_header_response_body_request(
                token=_continuation_token,
                foo=foo,
                bar=bar,
                headers=_headers,
                params=_params,
            )
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            _request.url = self._client.format_url(_request.url, **path_format_arguments)
            return _request

        def extract_data(pipeline_response):
            deserialized = pipeline_response.http_response.json()
            list_of_elem = _deserialize(
                list[_models3.Pet],
                deserialized.get("pets", []),
            )
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            return deserialized.get("nextToken") or None, iter(list_of_elem)

        def get_next(_continuation_token=None):
            _request = prepare_request(_continuation_token)

            _stream = False
            pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            return pipeline_response

        return ItemPaged(get_next, extract_data)

    def request_query_response_header(
        self, *, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
    ) -> ItemPaged["_models3.Pet"]:
        """request_query_response_header.

        :keyword foo: Default value is None.
        :paramtype foo: str
        :keyword bar: Default value is None.
        :paramtype bar: str
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[list[_models3.Pet]] = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(_continuation_token=None):

            _request = build_server_driven_pagination_continuation_token_request_query_response_header_request(
                token=_continuation_token,
                foo=foo,
                bar=bar,
                headers=_headers,
                params=_params,
            )
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            _request.url = self._client.format_url(_request.url, **path_format_arguments)
            return _request

        def extract_data(pipeline_response):
            deserialized = pipeline_response.http_response.json()
            list_of_elem = _deserialize(
                list[_models3.Pet],
                deserialized.get("pets", []),
            )
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            return pipeline_response.http_response.headers.get("next-token") or None, iter(list_of_elem)

        def get_next(_continuation_token=None):
            _request = prepare_request(_continuation_token)

            _stream = False
            pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            return pipeline_response

        return ItemPaged(get_next, extract_data)

    def request_header_response_header(
        self, *, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
    ) -> ItemPaged["_models3.Pet"]:
        """request_header_response_header.

        :keyword foo: Default value is None.
        :paramtype foo: str
        :keyword bar: Default value is None.
        :paramtype bar: str
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[list[_models3.Pet]] = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(_continuation_token=None):

            _request = build_server_driven_pagination_continuation_token_request_header_response_header_request(
                token=_continuation_token,
                foo=foo,
                bar=bar,
                headers=_headers,
                params=_params,
            )
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            _request.url = self._client.format_url(_request.url, **path_format_arguments)
            return _request

        def extract_data(pipeline_response):
            deserialized = pipeline_response.http_response.json()
            list_of_elem = _deserialize(
                list[_models3.Pet],
                deserialized.get("pets", []),
            )
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            return pipeline_response.http_response.headers.get("next-token") or None, iter(list_of_elem)

        def get_next(_continuation_token=None):
            _request = prepare_request(_continuation_token)

            _stream = False
            pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            return pipeline_response

        return ItemPaged(get_next, extract_data)

    def request_query_nested_response_body(
        self, *, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
    ) -> ItemPaged["_models3.Pet"]:
        """request_query_nested_response_body.

        :keyword foo: Default value is None.
        :paramtype foo: str
        :keyword bar: Default value is None.
        :paramtype bar: str
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[list[_models3.Pet]] = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(_continuation_token=None):

            _request = build_server_driven_pagination_continuation_token_request_query_nested_response_body_request(
                token=_continuation_token,
                foo=foo,
                bar=bar,
                headers=_headers,
                params=_params,
            )
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            _request.url = self._client.format_url(_request.url, **path_format_arguments)
            return _request

        def extract_data(pipeline_response):
            deserialized = pipeline_response.http_response.json()
            list_of_elem = _deserialize(
                list[_models3.Pet],
                deserialized.get("nestedItems", {}).get("pets", []),
            )
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            return deserialized.get("nestedNext", {}).get("nextToken") or None, iter(list_of_elem)

        def get_next(_continuation_token=None):
            _request = prepare_request(_continuation_token)

            _stream = False
            pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            return pipeline_response

        return ItemPaged(get_next, extract_data)

    def request_header_nested_response_body(
        self, *, foo: Optional[str] = None, bar: Optional[str] = None, **kwargs: Any
    ) -> ItemPaged["_models3.Pet"]:
        """request_header_nested_response_body.

        :keyword foo: Default value is None.
        :paramtype foo: str
        :keyword bar: Default value is None.
        :paramtype bar: str
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[list[_models3.Pet]] = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(_continuation_token=None):

            _request = build_server_driven_pagination_continuation_token_request_header_nested_response_body_request(
                token=_continuation_token,
                foo=foo,
                bar=bar,
                headers=_headers,
                params=_params,
            )
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            _request.url = self._client.format_url(_request.url, **path_format_arguments)
            return _request

        def extract_data(pipeline_response):
            deserialized = pipeline_response.http_response.json()
            list_of_elem = _deserialize(
                list[_models3.Pet],
                deserialized.get("nestedItems", {}).get("pets", []),
            )
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            return deserialized.get("nestedNext", {}).get("nextToken") or None, iter(list_of_elem)

        def get_next(_continuation_token=None):
            _request = prepare_request(_continuation_token)

            _stream = False
            pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            return pipeline_response

        return ItemPaged(get_next, extract_data)
