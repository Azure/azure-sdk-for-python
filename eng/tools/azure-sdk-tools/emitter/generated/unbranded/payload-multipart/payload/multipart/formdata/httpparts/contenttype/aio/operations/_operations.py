# coding=utf-8
from collections.abc import MutableMapping
from typing import Any, Callable, Optional, TypeVar, Union, overload

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

from ...... import models as _models5, types as _types_models5
from ......_utils.model_base import Model as _Model
from ......_utils.serialization import Deserializer, Serializer
from ......_utils.utils import prepare_multipart_form_data
from ......aio._configuration import MultiPartClientConfiguration
from ...operations._operations import (
    build_form_data_http_parts_content_type_image_jpeg_content_type_request,
    build_form_data_http_parts_content_type_optional_content_type_request,
    build_form_data_http_parts_content_type_required_content_type_request,
)

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class FormDataHttpPartsContentTypeOperations:  # pylint: disable=docstring-missing-param
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~payload.multipart.aio.MultiPartClient`'s
        :attr:`content_type` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: MultiPartClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    async def image_jpeg_content_type(
        self, body: _models5.FileWithHttpPartSpecificContentTypeRequest, **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data.

        :param body: Required.
        :type body: ~payload.multipart.models.FileWithHttpPartSpecificContentTypeRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def image_jpeg_content_type(
        self, body: _types_models5.FileWithHttpPartSpecificContentTypeRequest, **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data.

        :param body: Required.
        :type body: ~payload.multipart.types.FileWithHttpPartSpecificContentTypeRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def image_jpeg_content_type(
        self,
        body: Union[
            _models5.FileWithHttpPartSpecificContentTypeRequest,
            _types_models5.FileWithHttpPartSpecificContentTypeRequest,
        ],
        **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data.

        :param body: Is one of the following types: FileWithHttpPartSpecificContentTypeRequest
         Required.
        :type body: ~payload.multipart.models.FileWithHttpPartSpecificContentTypeRequest or
         ~payload.multipart.types.FileWithHttpPartSpecificContentTypeRequest
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

        _body = body.as_dict() if isinstance(body, _Model) else body
        _file_fields: list[str] = ["profileImage"]
        _data_fields: list[str] = []
        _files = prepare_multipart_form_data(_body, _file_fields, _data_fields)

        _request = build_form_data_http_parts_content_type_image_jpeg_content_type_request(
            files=_files,
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
    async def required_content_type(
        self, body: _models5.FileWithHttpPartRequiredContentTypeRequest, **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data.

        :param body: Required.
        :type body: ~payload.multipart.models.FileWithHttpPartRequiredContentTypeRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def required_content_type(
        self, body: _types_models5.FileWithHttpPartRequiredContentTypeRequest, **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data.

        :param body: Required.
        :type body: ~payload.multipart.types.FileWithHttpPartRequiredContentTypeRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def required_content_type(
        self,
        body: Union[
            _models5.FileWithHttpPartRequiredContentTypeRequest,
            _types_models5.FileWithHttpPartRequiredContentTypeRequest,
        ],
        **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data.

        :param body: Is one of the following types: FileWithHttpPartRequiredContentTypeRequest
         Required.
        :type body: ~payload.multipart.models.FileWithHttpPartRequiredContentTypeRequest or
         ~payload.multipart.types.FileWithHttpPartRequiredContentTypeRequest
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

        _body = body.as_dict() if isinstance(body, _Model) else body
        _file_fields: list[str] = ["profileImage"]
        _data_fields: list[str] = []
        _files = prepare_multipart_form_data(_body, _file_fields, _data_fields)

        _request = build_form_data_http_parts_content_type_required_content_type_request(
            files=_files,
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
    async def optional_content_type(
        self, body: _models5.FileWithHttpPartOptionalContentTypeRequest, **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data for optional content type.

        :param body: Required.
        :type body: ~payload.multipart.models.FileWithHttpPartOptionalContentTypeRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def optional_content_type(
        self, body: _types_models5.FileWithHttpPartOptionalContentTypeRequest, **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data for optional content type.

        :param body: Required.
        :type body: ~payload.multipart.types.FileWithHttpPartOptionalContentTypeRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def optional_content_type(
        self,
        body: Union[
            _models5.FileWithHttpPartOptionalContentTypeRequest,
            _types_models5.FileWithHttpPartOptionalContentTypeRequest,
        ],
        **kwargs: Any
    ) -> None:
        """Test content-type: multipart/form-data for optional content type.

        :param body: Is one of the following types: FileWithHttpPartOptionalContentTypeRequest
         Required.
        :type body: ~payload.multipart.models.FileWithHttpPartOptionalContentTypeRequest or
         ~payload.multipart.types.FileWithHttpPartOptionalContentTypeRequest
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

        _body = body.as_dict() if isinstance(body, _Model) else body
        _file_fields: list[str] = ["profileImage"]
        _data_fields: list[str] = []
        _files = prepare_multipart_form_data(_body, _file_fields, _data_fields)

        _request = build_form_data_http_parts_content_type_optional_content_type_request(
            files=_files,
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
