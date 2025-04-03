# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
from typing import Any, Callable, Dict, IO, List, Optional, TypeVar, Union

from azure.core import MatchConditions
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ... import models as _models

if sys.version_info >= (3, 8):
    from typing import Literal  # pylint: disable=no-name-in-module, ungrouped-imports
else:
    from typing_extensions import Literal  # type: ignore  # pylint: disable=ungrouped-imports
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]
from ._operations import TableOperations as TableOperationsGenerated
from ..operations._operations import (
    build_table_merge_entity_request,
    build_table_update_entity_request,
    build_table_insert_entity_request,
)


class TableOperations(TableOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.table.aio.AzureTable`'s
        :attr:`table` attribute.
    """

    @distributed_trace_async
    async def update_entity(  # pylint: disable=inconsistent-return-statements
        self,
        table: str,
        partition_key: str,
        row_key: str,
        table_entity_properties: Optional[Union[bytes, str]] = None,
        *,
        timeout: Optional[int] = None,
        format: Optional[Union[str, _models.OdataMetadataFormat]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> None:
        """Update entity in a table.

        :param table: The name of the table. Required.
        :type table: str
        :param partition_key: The partition key of the entity. Required.
        :type partition_key: str
        :param row_key: The row key of the entity. Required.
        :type row_key: str
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: bytes or str
        :keyword timeout: The timeout parameter is expressed in seconds. Default value is None.
        :paramtype timeout: int
        :keyword format: Specifies the media type for the response. Known values are:
         "application/json;odata=nometadata", "application/json;odata=minimalmetadata", and
         "application/json;odata=fullmetadata". Default value is None.
        :paramtype format: str or ~azure.table.models.OdataMetadataFormat
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword data_service_version: Specifies the data service version. Default value is "3.0". Note
         that overriding this default value may result in unsupported behavior.
        :paramtype data_service_version: str
        :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
         Default value is None.
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        elif match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        elif match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        data_service_version: Literal["3.0"] = kwargs.pop(
            "data_service_version", _headers.pop("DataServiceVersion", "3.0")
        )
        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[None] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        request = build_table_update_entity_request(
            table=table,
            partition_key=partition_key,
            row_key=row_key,
            timeout=timeout,
            format=format,
            etag=etag,
            match_condition=match_condition,
            data_service_version=data_service_version,
            content_type=content_type,
            version=self._config.version,
            content=table_entity_properties,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "url": self._serialize.url("self._config.url", self._config.url, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.TableServiceError, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        response_headers = {}
        response_headers["x-ms-client-request-id"] = self._deserialize(
            "str", response.headers.get("x-ms-client-request-id")
        )
        response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))
        response_headers["x-ms-version"] = self._deserialize("str", response.headers.get("x-ms-version"))
        response_headers["Date"] = self._deserialize("rfc-1123", response.headers.get("Date"))
        response_headers["ETag"] = self._deserialize("str", response.headers.get("ETag"))

        if cls:
            return cls(pipeline_response, None, response_headers)

    @distributed_trace_async
    async def merge_entity(  # pylint: disable=inconsistent-return-statements
        self,
        table: str,
        partition_key: str,
        row_key: str,
        table_entity_properties: Optional[Union[bytes, str]] = None,
        *,
        timeout: Optional[int] = None,
        format: Optional[Union[str, _models.OdataMetadataFormat]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> None:
        """Merge entity in a table.

        :param table: The name of the table. Required.
        :type table: str
        :param partition_key: The partition key of the entity. Required.
        :type partition_key: str
        :param row_key: The row key of the entity. Required.
        :type row_key: str
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: bytes or str
        :keyword timeout: The timeout parameter is expressed in seconds. Default value is None.
        :paramtype timeout: int
        :keyword format: Specifies the media type for the response. Known values are:
         "application/json;odata=nometadata", "application/json;odata=minimalmetadata", and
         "application/json;odata=fullmetadata". Default value is None.
        :paramtype format: str or ~azure.table.models.OdataMetadataFormat
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword data_service_version: Specifies the data service version. Default value is "3.0". Note
         that overriding this default value may result in unsupported behavior.
        :paramtype data_service_version: str
        :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
         Default value is None.
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        elif match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        elif match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        data_service_version: Literal["3.0"] = kwargs.pop(
            "data_service_version", _headers.pop("DataServiceVersion", "3.0")
        )
        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[None] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        request = build_table_merge_entity_request(
            table=table,
            partition_key=partition_key,
            row_key=row_key,
            timeout=timeout,
            format=format,
            etag=etag,
            match_condition=match_condition,
            data_service_version=data_service_version,
            content_type=content_type,
            version=self._config.version,
            content=table_entity_properties,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "url": self._serialize.url("self._config.url", self._config.url, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.TableServiceError, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        response_headers = {}
        response_headers["x-ms-client-request-id"] = self._deserialize(
            "str", response.headers.get("x-ms-client-request-id")
        )
        response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))
        response_headers["x-ms-version"] = self._deserialize("str", response.headers.get("x-ms-version"))
        response_headers["Date"] = self._deserialize("rfc-1123", response.headers.get("Date"))
        response_headers["ETag"] = self._deserialize("str", response.headers.get("ETag"))

        if cls:
            return cls(pipeline_response, None, response_headers)

    @distributed_trace_async
    async def insert_entity(
        self,
        table: str,
        table_entity_properties: Optional[Union[bytes, str]] = None,
        *,
        timeout: Optional[int] = None,
        format: Optional[Union[str, _models.OdataMetadataFormat]] = None,
        response_preference: Optional[Union[str, _models.ResponseFormat]] = None,
        **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        """Insert entity in a table.

        :param table: The name of the table. Required.
        :type table: str
        :param table_entity_properties: The properties for the table entity. Default value is None.
        :type table_entity_properties: bytes or str
        :keyword timeout: The timeout parameter is expressed in seconds. Default value is None.
        :paramtype timeout: int
        :keyword format: Specifies the media type for the response. Known values are:
         "application/json;odata=nometadata", "application/json;odata=minimalmetadata", and
         "application/json;odata=fullmetadata". Default value is None.
        :paramtype format: str or ~azure.table.models.OdataMetadataFormat
        :keyword response_preference: Specifies whether the response should include the inserted entity
         in the payload. Possible values are return-no-content and return-content. Known values are:
         "return-no-content" and "return-content". Default value is None.
        :paramtype response_preference: str or ~azure.table.models.ResponseFormat
        :keyword data_service_version: Specifies the data service version. Default value is "3.0". Note
         that overriding this default value may result in unsupported behavior.
        :paramtype data_service_version: str
        :return: dict mapping str to any or None
        :rtype: dict[str, any] or None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        data_service_version: Literal["3.0"] = kwargs.pop(
            "data_service_version", _headers.pop("DataServiceVersion", "3.0")
        )
        content_type: str = kwargs.pop(
            "content_type", _headers.pop("Content-Type", "application/json;odata=nometadata")
        )
        cls: ClsType[Optional[Dict[str, Any]]] = kwargs.pop("cls", None)

        request = build_table_insert_entity_request(
            table=table,
            timeout=timeout,
            format=format,
            response_preference=response_preference,
            data_service_version=data_service_version,
            content_type=content_type,
            version=self._config.version,
            content=table_entity_properties,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "url": self._serialize.url("self._config.url", self._config.url, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [201, 204]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.TableServiceError, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        deserialized = None
        response_headers = {}
        if response.status_code == 201:
            response_headers["x-ms-client-request-id"] = self._deserialize(
                "str", response.headers.get("x-ms-client-request-id")
            )
            response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))
            response_headers["x-ms-version"] = self._deserialize("str", response.headers.get("x-ms-version"))
            response_headers["Date"] = self._deserialize("rfc-1123", response.headers.get("Date"))
            response_headers["ETag"] = self._deserialize("str", response.headers.get("ETag"))
            response_headers["Preference-Applied"] = self._deserialize(
                "str", response.headers.get("Preference-Applied")
            )
            response_headers["Content-Type"] = self._deserialize("str", response.headers.get("Content-Type"))

            deserialized = self._deserialize("{object}", pipeline_response)

        if response.status_code == 204:
            response_headers["x-ms-client-request-id"] = self._deserialize(
                "str", response.headers.get("x-ms-client-request-id")
            )
            response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))
            response_headers["x-ms-version"] = self._deserialize("str", response.headers.get("x-ms-version"))
            response_headers["Date"] = self._deserialize("rfc-1123", response.headers.get("Date"))
            response_headers["ETag"] = self._deserialize("str", response.headers.get("ETag"))
            response_headers["Preference-Applied"] = self._deserialize(
                "str", response.headers.get("Preference-Applied")
            )
            response_headers["Content-Type"] = self._deserialize("str", response.headers.get("Content-Type"))

        if cls:
            return cls(pipeline_response, deserialized, response_headers)

        return deserialized


__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
