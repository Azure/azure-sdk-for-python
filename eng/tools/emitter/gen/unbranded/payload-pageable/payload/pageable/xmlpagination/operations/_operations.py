# coding=utf-8
from collections.abc import MutableMapping
from typing import Any, Callable, Optional, TypeVar
from xml.etree import ElementTree as ET

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

from ... import models as _models2
from ..._configuration import PageableClientConfiguration
from ..._utils.model_base import _deserialize
from ..._utils.serialization import Deserializer, Serializer

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_xml_pagination_list_with_continuation_request(  # pylint: disable=name-too-long
    *, marker: Optional[str] = None, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    accept = _headers.pop("Accept", "application/xml")

    # Construct URL
    _url = "/payload/pageable/xml/list-with-continuation"

    # Construct parameters
    if marker is not None:
        _params["marker"] = _SERIALIZER.query("marker", marker, "str")

    # Construct headers
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)


def build_xml_pagination_list_with_next_link_request(**kwargs: Any) -> HttpRequest:  # pylint: disable=name-too-long
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    accept = _headers.pop("Accept", "application/xml")

    # Construct URL
    _url = "/payload/pageable/xml/list-with-next-link"

    # Construct headers
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="GET", url=_url, headers=_headers, **kwargs)


class XmlPaginationOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~payload.pageable.PageableClient`'s
        :attr:`xml_pagination` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: PageableClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    def list_with_continuation(self, **kwargs: Any) -> ItemPaged["_models2.XmlPet"]:
        """list_with_continuation.

        :return: An iterator like instance of XmlPet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.XmlPet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[list[_models2.XmlPet]] = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(_continuation_token=None):

            _request = build_xml_pagination_list_with_continuation_request(
                marker=_continuation_token,
                headers=_headers,
                params=_params,
            )
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            _request.url = self._client.format_url(_request.url, **path_format_arguments)
            return _request

        def extract_data(pipeline_response):
            deserialized = ET.fromstring(pipeline_response.http_response.text())
            list_of_elem = _deserialize(
                list[_models2.XmlPet],
                deserialized.find("Pets"),
            )
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            _cont_token_elem = deserialized.find("NextMarker")
            return _cont_token_elem.text if _cont_token_elem is not None else None, iter(list_of_elem)

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

    def list_with_next_link(self, **kwargs: Any) -> ItemPaged["_models2.XmlPet"]:
        """list_with_next_link.

        :return: An iterator like instance of XmlPet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.XmlPet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[list[_models2.XmlPet]] = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        def prepare_request(next_link=None):
            if not next_link:

                _request = build_xml_pagination_list_with_next_link_request(
                    headers=_headers,
                    params=_params,
                )
                path_format_arguments = {
                    "endpoint": self._serialize.url(
                        "self._config.endpoint", self._config.endpoint, "str", skip_quote=True
                    ),
                }
                _request.url = self._client.format_url(_request.url, **path_format_arguments)

            else:
                _request = HttpRequest("GET", next_link, headers=_headers)
                path_format_arguments = {
                    "endpoint": self._serialize.url(
                        "self._config.endpoint", self._config.endpoint, "str", skip_quote=True
                    ),
                }
                _request.url = self._client.format_url(_request.url, **path_format_arguments)

            return _request

        def extract_data(pipeline_response):
            deserialized = ET.fromstring(pipeline_response.http_response.text())
            list_of_elem = _deserialize(
                list[_models2.XmlPet],
                deserialized.find("Pets"),
            )
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            _cont_token_elem = deserialized.find("NextLink")
            return _cont_token_elem.text if _cont_token_elem is not None else None, iter(list_of_elem)

        def get_next(next_link=None):
            _request = prepare_request(next_link)

            _stream = False
            pipeline_response: PipelineResponse = self._client.pipeline.run(_request, stream=_stream, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            return pipeline_response

        return ItemPaged(get_next, extract_data)
