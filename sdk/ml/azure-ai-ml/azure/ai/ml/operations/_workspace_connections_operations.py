# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable, Optional

from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062023Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils.utils import _snake_to_camel
from azure.ai.ml.entities._workspace.connections.workspace_connection import WorkspaceConnection
from azure.core.credentials import TokenCredential

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class WorkspaceConnectionsOperations(_ScopeDependentOperations):
    """WorkspaceConnectionsOperations.

    You should not instantiate this class directly. Instead, you should create
    an MLClient instance that instantiates it for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient062023Preview,
        all_operations: OperationsContainer,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        super(WorkspaceConnectionsOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._all_operations = all_operations
        self._operation = service_client.workspace_connections
        self._credentials = credentials
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "WorkspaceConnections.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, **kwargs: Dict) -> WorkspaceConnection:
        """Get a workspace connection by name.

        :param name: Name of the workspace connection.
        :type name: str
        :return: The workspace connection with the provided name.
        :rtype: ~azure.ai.ml.entities.WorkspaceConnection

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START get_connection]
                :end-before: [END get_connection]
                :language: python
                :dedent: 8
                :caption: Get a workspace connection by name.
        """

        obj = self._operation.get(
            workspace_name=self._workspace_name,
            connection_name=name,
            **self._scope_kwargs,
            **kwargs,
        )

        return WorkspaceConnection._from_rest_object(rest_obj=obj)

    @monitor_with_activity(logger, "WorkspaceConnections.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, workspace_connection, **kwargs) -> WorkspaceConnection:
        """Create or update a workspace connection.

        :param workspace_connection: Workspace Connection definition
            or object which can be translated to a workspace connection.
        :type workspace_connection: ~azure.ai.ml.entities.WorkspaceConnection
        :return: Created or update workspace connection.
        :rtype: ~azure.ai.ml.entities.WorkspaceConnection

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START create_or_update_connection]
                :end-before: [END create_or_update_connection]
                :language: python
                :dedent: 8
                :caption: Create or update a workspace connection, this example shows snowflake.
        """
        rest_workspace_connection = workspace_connection._to_rest_object()
        response = self._operation.create(
            workspace_name=self._workspace_name,
            connection_name=workspace_connection.name,
            body=rest_workspace_connection,
            **self._scope_kwargs,
            **kwargs,
        )

        return WorkspaceConnection._from_rest_object(rest_obj=response)

    @monitor_with_activity(logger, "WorkspaceConnections.Delete", ActivityType.PUBLICAPI)
    def delete(self, name) -> None:
        """Delete the workspace connection.

        :param name: Name of the workspace connection.
        :type name: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START delete_connection]
                :end-before: [END delete_connection]
                :language: python
                :dedent: 8
                :caption: Delete a workspace connection.
        """

        self._operation.delete(
            connection_name=name,
            workspace_name=self._workspace_name,
            **self._scope_kwargs,
        )

    @monitor_with_activity(logger, "WorkspaceConnections.List", ActivityType.PUBLICAPI)
    def list(
        self,
        connection_type: Optional[str] = None,
    ) -> Iterable[WorkspaceConnection]:
        """List all workspace connections for a workspace.

        :param connection_type: Type of workspace connection to list.
        :type connection_type: Optional[str]
        :return: An iterator like instance of workspace connection objects
        :rtype: Iterable[~azure.ai.ml.entities.WorkspaceConnection]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START list_connection]
                :end-before: [END list_connection]
                :language: python
                :dedent: 8
                :caption: Lists all connections for a workspace for a certain type, in this case "git".
        """
        return self._operation.list(
            workspace_name=self._workspace_name,
            cls=lambda objs: [WorkspaceConnection._from_rest_object(obj) for obj in objs],
            category=_snake_to_camel(connection_type) if connection_type else connection_type,
            **self._scope_kwargs,
        )
