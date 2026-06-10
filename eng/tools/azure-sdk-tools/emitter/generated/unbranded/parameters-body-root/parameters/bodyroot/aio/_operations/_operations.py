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

from ... import models as _models
from ..._operations._operations import build_body_root_nested_request
from ..._utils.model_base import SdkJSONEncoder
from ..._utils.utils import ClientMixinABC
from .._configuration import BodyRootClientConfiguration

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class _BodyRootClientOperationsMixin(
    ClientMixinABC[AsyncPipelineClient[HttpRequest, AsyncHttpResponse], BodyRootClientConfiguration]
):

    @overload
    async def nested(
        self, body_root_parameters: _models.BodyRootModel, *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """nested.

        :param body_root_parameters: Required.
        :type body_root_parameters: ~parameters.bodyroot.models.BodyRootModel
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def nested(
        self, body_root_parameters: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """nested.

        :param body_root_parameters: Required.
        :type body_root_parameters: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def nested(
        self, body_root_parameters: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> None:
        """nested.

        :param body_root_parameters: Required.
        :type body_root_parameters: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def nested(self, body_root_parameters: Union[_models.BodyRootModel, JSON, IO[bytes]], **kwargs: Any) -> None:
        """nested.

        :param body_root_parameters: Is one of the following types: BodyRootModel, JSON, IO[bytes]
         Required.
        :type body_root_parameters: ~parameters.bodyroot.models.BodyRootModel or JSON or IO[bytes]
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
        if isinstance(body_root_parameters, (IOBase, bytes)):
            _content = body_root_parameters
        else:
            _content = json.dumps(body_root_parameters, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_body_root_nested_request(
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
        pipeline_response: PipelineResponse = await self._client.pipeline.run(  # type: ignore
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if cls:
            return cls(pipeline_response, None, {})  # type: ignore
