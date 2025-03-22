# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, IO, Any, TYPE_CHECKING, Optional
from azure.core.tracing.decorator_async import distributed_trace_async

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.utils import case_insensitive_dict
from ..._operations._patch import (
    build_schema_registry_get_schema_properties_by_content_request,
    build_schema_registry_register_schema_request,
)
from ._operations import (
    ClsType,
    SchemaRegistryClientOperationsMixin as GeneratedClientOperationsMixin,
)

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineResponse


class SchemaRegistryClientOperationsMixin(GeneratedClientOperationsMixin):
    """
    Generated client to add custom methods.
    """

    @distributed_trace_async
    async def _get_schema_properties_by_content(  # type: ignore[override]
        self,
        group_name: str,
        schema_name: str,
        schema_content: IO,
        *,
        content_type: Optional[str] = None,
        stream: bool = False,
        **kwargs: Any
    ) -> None:
        """Get properties for existing schema.

        Gets the properties referencing an existing schema within the specified schema group, as matched by
        schema content comparison.

        :param group_name: Name of schema group. Required.
        :type group_name: str
        :param schema_name: Name of schema. Required.
        :type schema_name: str
        :param schema_content: String representation (UTF-8) of the registered schema. Required.
        :type schema_content: IO
        :keyword content_type: The content type for given schema. If None, value will be "text/plain;
         charset=utf-8".
        :paramtype content_type: str or None
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
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
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        _content_type: str = content_type or _headers.pop("Content-Type", "text/plain; charset=utf-8")
        cls: ClsType[None] = kwargs.pop("cls", None)

        _content = schema_content

        request = build_schema_registry_get_schema_properties_by_content_request(
            group_name=group_name,
            schema_name=schema_name,
            content_type=_content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "fullyQualifiedNamespace": self._serialize.url(
                "self._config.fully_qualified_namespace",
                self._config.fully_qualified_namespace,
                "str",
                skip_quote=True,
            ),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        _stream = stream
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        response_headers = {}
        response_headers["Location"] = self._deserialize("str", response.headers.get("Location"))
        response_headers["Schema-Id"] = self._deserialize("str", response.headers.get("Schema-Id"))
        response_headers["Schema-Id-Location"] = self._deserialize("str", response.headers.get("Schema-Id-Location"))
        response_headers["Schema-Group-Name"] = self._deserialize("str", response.headers.get("Schema-Group-Name"))
        response_headers["Schema-Name"] = self._deserialize("str", response.headers.get("Schema-Name"))
        response_headers["Schema-Version"] = self._deserialize("int", response.headers.get("Schema-Version"))

        if cls:
            return cls(pipeline_response, None, response_headers)

    @distributed_trace_async
    async def _register_schema(  # type: ignore[override]
        self,
        group_name: str,
        schema_name: str,
        schema_content: IO,
        *,
        content_type: Optional[str] = None,
        stream: bool = False,
        **kwargs: Any
    ) -> None:
        """Register new schema.

        Register new schema. If schema of specified name does not exist in specified group, schema is
        created at version 1. If schema of specified name exists already in specified group, schema is
        created at latest version + 1.

        :param group_name: Name of schema group. Required.
        :type group_name: str
        :param schema_name: Name of schema. Required.
        :type schema_name: str
        :param schema_content: String representation (UTF-8) of the schema. Required.
        :type schema_content: IO
        :keyword content_type: The content type for given schema. If None, value will be "text/plain;
         charset=utf-8".
        :paramtype content_type: str or None
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
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
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        _content_type: str = content_type or _headers.pop("Content-Type", "text/plain; charset=utf-8")
        cls: ClsType[None] = kwargs.pop("cls", None)

        _content = schema_content

        request = build_schema_registry_register_schema_request(
            group_name=group_name,
            schema_name=schema_name,
            content_type=_content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "fullyQualifiedNamespace": self._serialize.url(
                "self._config.fully_qualified_namespace",
                self._config.fully_qualified_namespace,
                "str",
                skip_quote=True,
            ),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        _stream = stream
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        response_headers = {}
        response_headers["Location"] = self._deserialize("str", response.headers.get("Location"))
        response_headers["Schema-Id"] = self._deserialize("str", response.headers.get("Schema-Id"))
        response_headers["Schema-Id-Location"] = self._deserialize("str", response.headers.get("Schema-Id-Location"))
        response_headers["Schema-Group-Name"] = self._deserialize("str", response.headers.get("Schema-Group-Name"))
        response_headers["Schema-Name"] = self._deserialize("str", response.headers.get("Schema-Name"))
        response_headers["Schema-Version"] = self._deserialize("int", response.headers.get("Schema-Version"))

        if cls:
            return cls(pipeline_response, None, response_headers)


__all__: List[str] = [
    "SchemaRegistryClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
