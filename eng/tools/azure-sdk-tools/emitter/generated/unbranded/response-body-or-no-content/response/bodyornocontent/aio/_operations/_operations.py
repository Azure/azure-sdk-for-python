# coding=utf-8
from collections.abc import MutableMapping
from typing import Any, Callable, Optional, TypeVar

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
from corehttp.rest import AsyncHttpResponse, HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime.pipeline import PipelineResponse

from ... import models as _models
from ..._operations._operations import (
    build_body_or_no_content_get_body_request,
    build_body_or_no_content_get_no_content_request,
)
from ..._utils.model_base import _deserialize
from ..._utils.utils import ClientMixinABC
from .._configuration import BodyOrNoContentClientConfiguration

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class _BodyOrNoContentClientOperationsMixin(
    ClientMixinABC[AsyncPipelineClient[HttpRequest, AsyncHttpResponse], BodyOrNoContentClientConfiguration]
):

    async def get_body(self, **kwargs: Any) -> Optional[_models.BlobLayout]:
        """get_body.

        :return: BlobLayout or None. The BlobLayout is compatible with MutableMapping
        :rtype: ~response.bodyornocontent.models.BlobLayout or None
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

        cls: ClsType[Optional[_models.BlobLayout]] = kwargs.pop("cls", None)

        _request = build_body_or_no_content_get_body_request(
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _decompress = kwargs.pop("decompress", True)
        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client.pipeline.run(  # type: ignore
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 204]:
            if _stream:
                try:
                    await response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = None
        response_headers = {}
        if response.status_code == 200:
            response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))

            if _stream:
                deserialized = response.iter_bytes() if _decompress else response.iter_raw()
            else:
                deserialized = _deserialize(_models.BlobLayout, response.json())

        if response.status_code == 204:
            response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))

        if cls:
            return cls(pipeline_response, deserialized, response_headers)  # type: ignore

        return deserialized  # type: ignore

    async def get_no_content(self, **kwargs: Any) -> Optional[_models.BlobLayout]:
        """get_no_content.

        :return: BlobLayout or None. The BlobLayout is compatible with MutableMapping
        :rtype: ~response.bodyornocontent.models.BlobLayout or None
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

        cls: ClsType[Optional[_models.BlobLayout]] = kwargs.pop("cls", None)

        _request = build_body_or_no_content_get_no_content_request(
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _decompress = kwargs.pop("decompress", True)
        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client.pipeline.run(  # type: ignore
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 204]:
            if _stream:
                try:
                    await response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = None
        response_headers = {}
        if response.status_code == 200:
            response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))

            if _stream:
                deserialized = response.iter_bytes() if _decompress else response.iter_raw()
            else:
                deserialized = _deserialize(_models.BlobLayout, response.json())

        if response.status_code == 204:
            response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))

        if cls:
            return cls(pipeline_response, deserialized, response_headers)  # type: ignore

        return deserialized  # type: ignore
