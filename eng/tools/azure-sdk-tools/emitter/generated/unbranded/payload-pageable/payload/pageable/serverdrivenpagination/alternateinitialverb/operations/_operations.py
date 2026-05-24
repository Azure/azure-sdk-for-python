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
from corehttp.paging import ItemPaged
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.runtime import PipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from .. import models as _models1
from .... import models as _models3
from ...._configuration import PageableClientConfiguration
from ...._utils.model_base import SdkJSONEncoder, _deserialize
from ...._utils.serialization import Deserializer, Serializer

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_server_driven_pagination_alternate_initial_verb_post_request(  # pylint: disable=name-too-long
    **kwargs: Any,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/payload/pageable/server-driven-pagination/link/initial-post"

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_headers, **kwargs)


class ServerDrivenPaginationAlternateInitialVerbOperations:  # pylint: disable=name-too-long
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~payload.pageable.PageableClient`'s
        :attr:`alternate_initial_verb` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: PageableClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    def post(
        self, body: _models1.Filter, *, content_type: str = "application/json", **kwargs: Any
    ) -> ItemPaged["_models3.Pet"]:
        """post.

        :param body: Required.
        :type body: ~payload.pageable.serverdrivenpagination.alternateinitialverb.models.Filter
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def post(self, body: JSON, *, content_type: str = "application/json", **kwargs: Any) -> ItemPaged["_models3.Pet"]:
        """post.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    def post(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> ItemPaged["_models3.Pet"]:
        """post.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    def post(self, body: Union[_models1.Filter, JSON, IO[bytes]], **kwargs: Any) -> ItemPaged["_models3.Pet"]:
        """post.

        :param body: Is one of the following types: Filter, JSON, IO[bytes] Required.
        :type body: ~payload.pageable.serverdrivenpagination.alternateinitialverb.models.Filter or JSON
         or IO[bytes]
        :return: An iterator like instance of Pet
        :rtype: ~corehttp.paging.ItemPaged[~payload.pageable.models.Pet]
        :raises ~corehttp.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[list[_models3.Pet]] = kwargs.pop("cls", None)

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        def prepare_request(next_link=None):
            if not next_link:

                _request = build_server_driven_pagination_alternate_initial_verb_post_request(
                    content_type=content_type,
                    content=_content,
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
            deserialized = pipeline_response.http_response.json()
            list_of_elem = _deserialize(
                list[_models3.Pet],
                deserialized.get("pets", []),
            )
            if cls:
                list_of_elem = cls(list_of_elem)  # type: ignore
            return deserialized.get("next") or None, iter(list_of_elem)

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
