# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Iterable, Optional

from azure.ai.resources._project_scope import OperationScope
from azure.ai.resources.constants._common import DEFAULT_OPEN_AI_CONNECTION_NAME
from azure.ai.resources.entities.connection import Connection
from azure.ai.ml import MLClient


class ConnectionOperations:
    """ConnectionOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(self, ml_client: MLClient, **kwargs: Any):
        self._ml_client = ml_client

    def list(self, connection_type: Optional[str] = None) -> Iterable[Connection]:
        """List all connection assets in a project.

        :param connection_type: If set, return only connections of the specified type.
        :type connection_type: str

        :return: An iterator like instance of connection objects
        :rtype: Iterable[Connection]
        """
        return [
            Connection._from_v2_workspace_connection(conn)
            for conn in self._ml_client._workspace_connections.list(connection_type=connection_type)
        ]

    def get(self, name: str, **kwargs) -> Connection:
        """Get a connection by name.

        :param name: Name of the connection.
        :type name: str

        :return: The connection with the provided name.
        :rtype: Connection
        """
        workspace_connection = self._ml_client._workspace_connections.get(name=name, **kwargs)
        connection = Connection._from_v2_workspace_connection(workspace_connection)

        # It's by design that both API and V2 SDK don't include the secrets from API response, the following
        # code fills the gap
        if not connection.credentials.key:
            list_secrets_response = self._ml_client.connections._operation.list_secrets(
                connection_name=name,
                resource_group_name=self._ml_client.resource_group_name,
                workspace_name=self._ml_client.workspace_name,
            )
            connection.credentials.key = list_secrets_response.properties.credentials.key

        return connection

    def create_or_update(self, connection: Connection, **kwargs) -> Connection:
        """Create or update a connection.

        :param connection: Connection definition
            or object which can be translated to a connection.
        :type connection: Connection
        :return: Created or updated connection.
        :rtype: Connection
        """
        response = self._ml_client._workspace_connections.create_or_update(
            workspace_connection=connection._workspace_connection, **kwargs
        )

        return Connection._from_v2_workspace_connection(response)

    def delete(self, name: str) -> None:
        """Delete the connection.

        :param name: Name of the connection to delete.
        :type name: str
        """
        return self._ml_client._workspace_connections.delete(name=name)
