# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable, Optional

from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
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

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient052022,
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
        :rtype: WorkspaceConnection
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
        :type workspace_connection: WorkspaceConnection
        :return: Created or update workspace connection.
        :rtype: WorkspaceConnection
        """
        rest_workspace_connection = workspace_connection._to_rest_object()
        response = self._operation.create(
            workspace_name=self._workspace_name,
            connection_name=workspace_connection.name,
            parameters=rest_workspace_connection,
            **self._scope_kwargs,
            **kwargs,
        )

        return WorkspaceConnection._from_rest_object(rest_obj=response)

    @monitor_with_activity(logger, "WorkspaceConnections.Delete", ActivityType.PUBLICAPI)
    def delete(self, name) -> None:
        """Delete the workspace connection.

        :param name: Name of the workspace connection.
        :type name: str
        """

        return self._operation.delete(
            connection_name=name,
            workspace_name=self._workspace_name,
            **self._scope_kwargs,
        )

    @monitor_with_activity(logger, "WorkspaceConnections.List", ActivityType.PUBLICAPI)
    def list(
        self,
        connection_type=None,
    ) -> Iterable[WorkspaceConnection]:
        """List all environment assets in workspace.

        :param connection_type: Type of workspace connection to list.
        :type connection_type: str
        :return: An iterator like instance of workspace connection objects
        :rtype: Iterable[WorkspaceConnection]
        """
        return self._operation.list(
            workspace_name=self._workspace_name,
            cls=lambda objs: [WorkspaceConnection._from_rest_object(obj) for obj in objs],
            category=_snake_to_camel(connection_type) if connection_type else connection_type,
            **self._scope_kwargs,
        )
