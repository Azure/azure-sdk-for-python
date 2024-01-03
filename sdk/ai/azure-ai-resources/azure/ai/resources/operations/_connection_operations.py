# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Iterable, Optional

from azure.core.tracing.decorator import distributed_trace

from azure.ai.resources.constants import OperationScope
from azure.ai.resources.entities import BaseConnection
from azure.ai.ml import MLClient

from azure.ai.resources._telemetry import ActivityType, monitor_with_activity, ActivityLogger

activity_logger = ActivityLogger(__name__)
logger, module_logger = activity_logger.package_logger, activity_logger.module_logger


class ConnectionOperations:
    """ConnectionOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(self, *, resource_ml_client: MLClient = None, project_ml_client: MLClient = None, **kwargs: Any):
        self._resource_ml_client = resource_ml_client
        self._project_ml_client = project_ml_client
        activity_logger.update_info(kwargs)

    @distributed_trace
    @monitor_with_activity(logger, "Connection.List", ActivityType.PUBLICAPI)
    def list(self, connection_type: Optional[str] = None, scope: str = OperationScope.AI_RESOURCE) -> Iterable[BaseConnection]:
        """List all connection assets in a project.

        :param connection_type: If set, return only connections of the specified type.
        :type connection_type: str

        :return: An iterator like instance of connection objects
        :rtype: Iterable[Connection]
        """
        client = self._resource_ml_client if scope == OperationScope.AI_RESOURCE else self._project_ml_client
        return [
            BaseConnection._from_v2_workspace_connection(conn)
            for conn in client._workspace_connections.list(connection_type=connection_type)
        ]

    @distributed_trace
    @monitor_with_activity(logger, "Connection.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, scope: str = OperationScope.AI_RESOURCE, **kwargs) -> BaseConnection:
        """Get a connection by name.

        :param name: Name of the connection.
        :type name: str

        :return: The connection with the provided name.
        :rtype: Connection
        """
        client = self._resource_ml_client if scope == OperationScope.AI_RESOURCE else self._project_ml_client
        workspace_connection = client._workspace_connections.get(name=name, **kwargs)
        connection = BaseConnection._from_v2_workspace_connection(workspace_connection)

        # It's by design that both API and V2 SDK don't include the secrets from API response, the following
        # code fills the gap when possible
        if not connection.credentials.key:
            list_secrets_response = client.connections._operation.list_secrets(
                connection_name=name,
                resource_group_name=client.resource_group_name,
                workspace_name=client.workspace_name,
            )
            if list_secrets_response.properties.credentials is not None:
                connection.credentials.key = list_secrets_response.properties.credentials.key
        return connection

    @distributed_trace
    @monitor_with_activity(logger, "Connection.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, connection: BaseConnection, scope: str = OperationScope.AI_RESOURCE, **kwargs) -> BaseConnection:
        """Create or update a connection.

        :param connection: Connection definition
            or object which can be translated to a connection.
        :type connection: Connection
        :param scope: The scope of the operation, which determines if the created connection is managed by
            an AI Resource or directly by a project. Defaults to AI resource-level scoping.
        :type scope: ~azure.ai.resources.constants.OperationScope
        :return: Created or updated connection.
        :rtype: Connection
        """
        client = self._resource_ml_client if scope == OperationScope.AI_RESOURCE else self._project_ml_client
        response = client._workspace_connections.create_or_update(
            workspace_connection=connection._workspace_connection, **kwargs
        )

        return BaseConnection._from_v2_workspace_connection(response)

    @distributed_trace
    @monitor_with_activity(logger, "Connection.Delete", ActivityType.PUBLICAPI)
    def delete(self, name: str, scope: str = OperationScope.AI_RESOURCE) -> None:
        """Delete the connection.

        :param name: Name of the connection to delete.
        :type name: str
        """
        client = self._resource_ml_client if scope == OperationScope.AI_RESOURCE else self._project_ml_client
        return client._workspace_connections.delete(name=name)
