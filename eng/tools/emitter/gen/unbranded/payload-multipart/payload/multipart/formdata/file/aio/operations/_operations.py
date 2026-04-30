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

from ... import models as _models2
from ....._utils.model_base import Model as _Model
from ....._utils.serialization import Deserializer, Serializer
from ....._utils.utils import prepare_multipart_form_data
from .....aio._configuration import MultiPartClientConfiguration
from ...operations._operations import (
    build_form_data_file_upload_file_array_request,
    build_form_data_file_upload_file_required_filename_request,
    build_form_data_file_upload_file_specific_content_type_request,
)

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


class FormDataFileOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~payload.multipart.aio.MultiPartClient`'s
        :attr:`file` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: MultiPartClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    async def upload_file_specific_content_type(
        self, body: _models2.UploadFileSpecificContentTypeRequest, **kwargs: Any
    ) -> None:
        """upload_file_specific_content_type.

        :param body: Required.
        :type body: ~payload.multipart.formdata.file.models.UploadFileSpecificContentTypeRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def upload_file_specific_content_type(self, body: JSON, **kwargs: Any) -> None:
        """upload_file_specific_content_type.

        :param body: Required.
        :type body: JSON
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def upload_file_specific_content_type(
        self, body: Union[_models2.UploadFileSpecificContentTypeRequest, JSON], **kwargs: Any
    ) -> None:
        """upload_file_specific_content_type.

        :param body: Is either a UploadFileSpecificContentTypeRequest type or a JSON type. Required.
        :type body: ~payload.multipart.formdata.file.models.UploadFileSpecificContentTypeRequest or
         JSON
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
        _file_fields: list[str] = ["file"]
        _data_fields: list[str] = []
        _files = prepare_multipart_form_data(_body, _file_fields, _data_fields)

        _request = build_form_data_file_upload_file_specific_content_type_request(
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
    async def upload_file_required_filename(
        self, body: _models2.UploadFileRequiredFilenameRequest, **kwargs: Any
    ) -> None:
        """upload_file_required_filename.

        :param body: Required.
        :type body: ~payload.multipart.formdata.file.models.UploadFileRequiredFilenameRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def upload_file_required_filename(self, body: JSON, **kwargs: Any) -> None:
        """upload_file_required_filename.

        :param body: Required.
        :type body: JSON
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def upload_file_required_filename(
        self, body: Union[_models2.UploadFileRequiredFilenameRequest, JSON], **kwargs: Any
    ) -> None:
        """upload_file_required_filename.

        :param body: Is either a UploadFileRequiredFilenameRequest type or a JSON type. Required.
        :type body: ~payload.multipart.formdata.file.models.UploadFileRequiredFilenameRequest or JSON
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
        _file_fields: list[str] = ["file"]
        _data_fields: list[str] = []
        _files = prepare_multipart_form_data(_body, _file_fields, _data_fields)

        _request = build_form_data_file_upload_file_required_filename_request(
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
    async def upload_file_array(self, body: _models2.UploadFileArrayRequest, **kwargs: Any) -> None:
        """upload_file_array.

        :param body: Required.
        :type body: ~payload.multipart.formdata.file.models.UploadFileArrayRequest
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    @overload
    async def upload_file_array(self, body: JSON, **kwargs: Any) -> None:
        """upload_file_array.

        :param body: Required.
        :type body: JSON
        :return: None
        :rtype: None
        :raises ~corehttp.exceptions.HttpResponseError:
        """

    async def upload_file_array(self, body: Union[_models2.UploadFileArrayRequest, JSON], **kwargs: Any) -> None:
        """upload_file_array.

        :param body: Is either a UploadFileArrayRequest type or a JSON type. Required.
        :type body: ~payload.multipart.formdata.file.models.UploadFileArrayRequest or JSON
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
        _file_fields: list[str] = ["files"]
        _data_fields: list[str] = []
        _files = prepare_multipart_form_data(_body, _file_fields, _data_fields)

        _request = build_form_data_file_upload_file_array_request(
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
