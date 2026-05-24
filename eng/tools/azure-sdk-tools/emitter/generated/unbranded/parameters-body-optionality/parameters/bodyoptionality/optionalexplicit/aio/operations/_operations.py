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
from corehttp.rest import AsyncHttpResponse, HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from .... import models as _models3
from ...._utils.model_base import SdkJSONEncoder
from ...._utils.serialization import Deserializer, Serializer
from ....aio._configuration import BodyOptionalityClientConfiguration
from ...operations._operations import build_optional_explicit_omit_request, build_optional_explicit_set_request

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class OptionalExplicitOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~parameters.bodyoptionality.aio.BodyOptionalityClient`'s
        :attr:`optional_explicit` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: BodyOptionalityClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    async def set(
        self, body: Optional[_models3.BodyModel] = None, *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """set.

        :param body: Default value is None.
        :type body: ~parameters.bodyoptionality.models.BodyModel
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def set(self, body: Optional[JSON] = None, *, content_type: str = "application/json", **kwargs: Any) -> None:
        """set.

        :param body: Default value is None.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def set(
        self, body: Optional[IO[bytes]] = None, *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """set.

        :param body: Default value is None.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def set(self, body: Optional[Union[_models3.BodyModel, JSON, IO[bytes]]] = None, **kwargs: Any) -> None:
        """set.

        :param body: Is one of the following types: BodyModel, JSON, IO[bytes] Default value is None.
        :type body: ~parameters.bodyoptionality.models.BodyModel or JSON or IO[bytes]
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
        content_type = content_type if body else None
        cls: ClsType[None] = kwargs.pop("cls", None)

        content_type = content_type or "application/json" if body else None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            if body is not None:
                _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore
            else:
                _content = None

        _request = build_optional_explicit_set_request(
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
        pipeline_response: PipelineResponse = await self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore

    @overload
    async def omit(
        self, body: Optional[_models3.BodyModel] = None, *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """omit.

        :param body: Default value is None.
        :type body: ~parameters.bodyoptionality.models.BodyModel
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def omit(self, body: Optional[JSON] = None, *, content_type: str = "application/json", **kwargs: Any) -> None:
        """omit.

        :param body: Default value is None.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def omit(
        self, body: Optional[IO[bytes]] = None, *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """omit.

        :param body: Default value is None.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def omit(self, body: Optional[Union[_models3.BodyModel, JSON, IO[bytes]]] = None, **kwargs: Any) -> None:
        """omit.

        :param body: Is one of the following types: BodyModel, JSON, IO[bytes] Default value is None.
        :type body: ~parameters.bodyoptionality.models.BodyModel or JSON or IO[bytes]
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
        content_type = content_type if body else None
        cls: ClsType[None] = kwargs.pop("cls", None)

        content_type = content_type or "application/json" if body else None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            if body is not None:
                _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore
            else:
                _content = None

        _request = build_optional_explicit_omit_request(
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
        pipeline_response: PipelineResponse = await self._client.pipeline.run(_request, stream=_stream, **kwargs)

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore
