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
from corehttp.rest import AsyncHttpResponse, HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime.pipeline import PipelineResponse
from corehttp.utils import case_insensitive_dict

from ... import models as _models
from ..._operations._operations import build_removed_model_v3_request, build_removed_v2_request
from ..._utils.model_base import SdkJSONEncoder, _deserialize
from ..._utils.utils import ClientMixinABC
from .._configuration import RemovedClientConfiguration

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class _RemovedClientOperationsMixin(
    ClientMixinABC[AsyncPipelineClient[HttpRequest, AsyncHttpResponse], RemovedClientConfiguration]
):

    @overload
    async def v2(
        self, body: _models.ModelV2, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ModelV2:
        """v2.

        :param body: Required.
        :type body: ~versioning.removed.models.ModelV2
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ModelV2. The ModelV2 is compatible with MutableMapping
        :rtype: ~versioning.removed.models.ModelV2
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def v2(self, body: JSON, *, content_type: str = "application/json", **kwargs: Any) -> _models.ModelV2:
        """v2.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ModelV2. The ModelV2 is compatible with MutableMapping
        :rtype: ~versioning.removed.models.ModelV2
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def v2(self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any) -> _models.ModelV2:
        """v2.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ModelV2. The ModelV2 is compatible with MutableMapping
        :rtype: ~versioning.removed.models.ModelV2
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def v2(self, body: Union[_models.ModelV2, JSON, IO[bytes]], **kwargs: Any) -> _models.ModelV2:
        """v2.

        :param body: Is one of the following types: ModelV2, JSON, IO[bytes] Required.
        :type body: ~versioning.removed.models.ModelV2 or JSON or IO[bytes]
        :return: ModelV2. The ModelV2 is compatible with MutableMapping
        :rtype: ~versioning.removed.models.ModelV2
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
        cls: ClsType[_models.ModelV2] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_removed_v2_request(
            content_type=content_type,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            "version": self._serialize.url("self._config.version", self._config.version, "str"),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _decompress = kwargs.pop("decompress", True)
        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client.pipeline.run(  # type: ignore
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                try:
                    await response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models.ModelV2, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def model_v3(
        self, body: _models.ModelV3, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ModelV3:
        """This operation will pass different paths and different request bodies based on different
        versions.

        :param body: Required.
        :type body: ~versioning.removed.models.ModelV3
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ModelV3. The ModelV3 is compatible with MutableMapping
        :rtype: ~versioning.removed.models.ModelV3
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def model_v3(self, body: JSON, *, content_type: str = "application/json", **kwargs: Any) -> _models.ModelV3:
        """This operation will pass different paths and different request bodies based on different
        versions.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ModelV3. The ModelV3 is compatible with MutableMapping
        :rtype: ~versioning.removed.models.ModelV3
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def model_v3(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ModelV3:
        """This operation will pass different paths and different request bodies based on different
        versions.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ModelV3. The ModelV3 is compatible with MutableMapping
        :rtype: ~versioning.removed.models.ModelV3
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def model_v3(self, body: Union[_models.ModelV3, JSON, IO[bytes]], **kwargs: Any) -> _models.ModelV3:
        """This operation will pass different paths and different request bodies based on different
        versions.

        :param body: Is one of the following types: ModelV3, JSON, IO[bytes] Required.
        :type body: ~versioning.removed.models.ModelV3 or JSON or IO[bytes]
        :return: ModelV3. The ModelV3 is compatible with MutableMapping
        :rtype: ~versioning.removed.models.ModelV3
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
        cls: ClsType[_models.ModelV3] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_removed_model_v3_request(
            content_type=content_type,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            "version": self._serialize.url("self._config.version", self._config.version, "str"),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _decompress = kwargs.pop("decompress", True)
        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client.pipeline.run(  # type: ignore
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                try:
                    await response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes() if _decompress else response.iter_raw()
        else:
            deserialized = _deserialize(_models.ModelV3, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
