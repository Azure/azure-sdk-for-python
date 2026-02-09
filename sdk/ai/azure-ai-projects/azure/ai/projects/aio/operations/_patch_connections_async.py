# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, Union
from azure.core.tracing.decorator_async import distributed_trace_async

from ._operations import ConnectionsOperations as ConnectionsOperationsGenerated
from ...models._models import Connection
from ...models._enums import ConnectionType


class ConnectionsOperations(ConnectionsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`connections` attribute.
    """

    @distributed_trace_async
    async def get(self, name: str, *, include_credentials: Optional[bool] = False, **kwargs: Any) -> Connection:
        """Get a connection by name.

        :param name: The name of the resource. Required.
        :type name: str
        :keyword include_credentials: Whether to include credentials in the response. Default is False.
        :paramtype include_credentials: bool
        :return: Connection. The Connection is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Connection
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if include_credentials:
            connection = await super()._get_with_credentials(name, **kwargs)
            if connection.type == ConnectionType.CUSTOM:
                # Why do we do this? See comment in the sync version of this code (file _patch_connections.py).
                setattr(
                    connection.credentials,
                    "credential_keys",
                    {k: v for k, v in connection.credentials.as_dict().items() if k != "type"},
                )

            return connection

        return await super()._get(name, **kwargs)

    @distributed_trace_async
    async def list_api_center_apis(
        self,
        connection_name: str,
        *,
        api_type: Optional[str] = None,
        **kwargs: Any
    ) -> list:
        """List APIs from an Azure API Center connection.

        :param connection_name: The name of the API Center connection. Required.
        :type connection_name: str
        :keyword api_type: Filter APIs by type (e.g., "mcp", "rest", "graphql"). Optional.
        :paramtype api_type: Optional[str]
        :return: List of APIs from the API Center.
        :rtype: list[~azure.ai.projects.models.ApiCenterApi]
        :raises ValueError: If the connection is not found or is not an API Center connection.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        from ...models._patch import ApiCenterApi
        
        # Get the connection to validate it exists and get its target URL
        connection = await self.get(connection_name, **kwargs)
        
        if not connection.target:
            raise ValueError(f"Connection '{connection_name}' does not have a target URL.")
        
        # Construct API Center REST API endpoint
        api_center_url = connection.target.rstrip("/")
        url = f"{api_center_url}/apis"
        
        # Make request to list APIs
        from azure.core.rest import HttpRequest
        request = HttpRequest(
            method="GET",
            url=url,
            params={"api-version": "2024-03-01"}
        )
        
        pipeline_response = await self._client._pipeline.run(request, **kwargs)  # pylint: disable=protected-access
        response = pipeline_response.http_response
        
        if response.status_code != 200:
            from azure.core.exceptions import HttpResponseError
            raise HttpResponseError(response=response)
        
        # Parse response
        data = response.json()
        apis = []
        
        for api_data in data.get("value", []):
            api_kind = api_data.get("properties", {}).get("kind", "")
            
            # Filter by type if specified
            if api_type and api_kind.lower() != api_type.lower():
                continue
            
            api = ApiCenterApi(
                id=api_data.get("id", ""),
                name=api_data.get("name", ""),
                type=api_kind,
                title=api_data.get("properties", {}).get("title"),
                description=api_data.get("properties", {}).get("description"),
                kind=api_kind,
                metadata=api_data.get("properties", {})
            )
            apis.append(api)
        
        return apis

    @distributed_trace_async
    async def list_api_center_mcp_servers(
        self,
        connection_name: str,
        **kwargs: Any
    ) -> list:
        """List MCP servers from an Azure API Center connection.

        :param connection_name: The name of the API Center connection. Required.
        :type connection_name: str
        :return: List of MCP servers from the API Center.
        :rtype: list[~azure.ai.projects.models.ApiCenterMcpServer]
        :raises ValueError: If the connection is not found or is not an API Center connection.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        from ...models._patch import ApiCenterMcpServer
        
        # Get all APIs and filter for MCP type
        all_apis = await self.list_api_center_apis(connection_name, api_type="mcp", **kwargs)
        
        # Convert to MCP server objects
        mcp_servers = []
        for api in all_apis:
            server_url = api.metadata.get("serverUrl") or api.metadata.get("server_url")
            connector_id = api.metadata.get("connectorId") or api.metadata.get("connector_id")
            
            mcp_server = ApiCenterMcpServer(
                id=api.id,
                name=api.name,
                server_url=server_url,
                title=api.title,
                description=api.description,
                connector_id=connector_id,
                metadata=api.metadata
            )
            mcp_servers.append(mcp_server)
        
        return mcp_servers

    @distributed_trace_async
    async def get_api_center_api(
        self,
        connection_name: str,
        api_name: str,
        **kwargs: Any
    ) -> Any:
        """Get a specific API from an Azure API Center connection.

        :param connection_name: The name of the API Center connection. Required.
        :type connection_name: str
        :param api_name: The name of the API to retrieve. Required.
        :type api_name: str
        :return: The API from the API Center.
        :rtype: ~azure.ai.projects.models.ApiCenterApi
        :raises ValueError: If the connection or API is not found.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        from ...models._patch import ApiCenterApi
        
        # Get the connection to validate it exists and get its target URL
        connection = await self.get(connection_name, **kwargs)
        
        if not connection.target:
            raise ValueError(f"Connection '{connection_name}' does not have a target URL.")
        
        # Construct API Center REST API endpoint for specific API
        api_center_url = connection.target.rstrip("/")
        url = f"{api_center_url}/apis/{api_name}"
        
        # Make request to get API
        from azure.core.rest import HttpRequest
        request = HttpRequest(
            method="GET",
            url=url,
            params={"api-version": "2024-03-01"}
        )
        
        pipeline_response = await self._client._pipeline.run(request, **kwargs)  # pylint: disable=protected-access
        response = pipeline_response.http_response
        
        if response.status_code != 200:
            from azure.core.exceptions import HttpResponseError
            raise HttpResponseError(response=response)
        
        # Parse response
        api_data = response.json()
        api_kind = api_data.get("properties", {}).get("kind", "")
        
        api = ApiCenterApi(
            id=api_data.get("id", ""),
            name=api_data.get("name", ""),
            type=api_kind,
            title=api_data.get("properties", {}).get("title"),
            description=api_data.get("properties", {}).get("description"),
            kind=api_kind,
            metadata=api_data.get("properties", {})
        )
        
        return api

    @distributed_trace_async
    async def get_default(
        self, connection_type: Union[str, ConnectionType], *, include_credentials: Optional[bool] = False, **kwargs: Any
    ) -> Connection:
        """Get the default connection for a given connection type.

        :param connection_type: The type of the connection. Required.
        :type connection_type: str or ~azure.ai.projects.models.ConnectionType
        :keyword include_credentials: Whether to include credentials in the response. Default is False.
        :paramtype include_credentials: bool
        :return: Connection. The Connection is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Connection
        :raises ValueError: If no default connection is found for the given type.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        connections = super().list(connection_type=connection_type, default_connection=True, **kwargs)
        async for connection in connections:
            return await self.get(connection.name, include_credentials=include_credentials, **kwargs)
        raise ValueError(f"No default connection found for type: {connection_type}.")
