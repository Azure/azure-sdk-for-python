# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict, Iterable, Optional, cast

from azure.ai.ml._restclient.v2024_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient082023Preview
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
from azure.core.tracing.decorator import distributed_trace
from azure.ai.ml.entities._credentials import (
    ApiKeyConfiguration,
)

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class WorkspaceConnectionsOperations(_ScopeDependentOperations):
    """WorkspaceConnectionsOperations.

    You should not instantiate this class directly. Instead, you should create
    an MLClient instance that instantiates it for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient082023Preview,
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

    def _try_fill_api_key(self, connection: WorkspaceConnection) -> None:
        """Try to fill in a connection's credentials with it's actual values.
        Connection data retrievals normally return an empty credential object that merely includes the
        connection's credential type, but not the actual secrets of that credential.
        However, it's extremely common for users to want to know the contents of their connection's credentials.
        This method tries to fill in the user's credentials with the actual values by making
        a secondary API call to the service. It requires that the user have the necessary permissions to do so,
        and it only works on api key-based credentials.

        :param connection: The connection to try to fill in the credentials for.
        :type connection: ~azure.ai.ml.entities.WorkspaceConnection
        """
        if hasattr(connection, "credentials") and isinstance(connection.credentials, ApiKeyConfiguration):
            list_secrets_response = self._operation.list_secrets(
                connection_name=connection.name,
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._operation_scope.workspace_name,
            )
            if list_secrets_response.properties.credentials is not None:
                connection.credentials.key = list_secrets_response.properties.credentials.key

    @distributed_trace
    @monitor_with_activity(ops_logger, "WorkspaceConnections.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, *, populate_secrets: bool = False, **kwargs: Dict) -> WorkspaceConnection:
        """Get a connection by name.

        :param name: Name of the connection.
        :type name: str
        :keyword populate_secrets: If true, make a secondary API call to try filling in the workspace
            connections credentials. Currently only works for api key-based credentials. Defaults to False.
        :paramtype populate_secrets: bool
        :raises ~azure.core.exceptions.HttpResponseError: Raised if the corresponding name and version cannot be
            retrieved from the service.
        :return: The connection with the provided name.
        :rtype: ~azure.ai.ml.entities.WorkspaceConnection
        """

        connection = WorkspaceConnection._from_rest_object(
            rest_obj=self._operation.get(
                workspace_name=self._workspace_name,
                connection_name=name,
                **self._scope_kwargs,
                **kwargs,
            )
        )

        if populate_secrets and connection is not None:
            self._try_fill_api_key(connection)
        return connection  # type: ignore[return-value]

    @distributed_trace
    @monitor_with_activity(ops_logger, "WorkspaceConnections.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(
        self, workspace_connection: WorkspaceConnection, *, populate_secrets: bool = False, **kwargs: Any
    ) -> WorkspaceConnection:
        """Create or update a connection.

        :param workspace_connection: Definition of a Workspace Connection or one of its subclasses
            or object which can be translated to a connection.
        :type workspace_connection: ~azure.ai.ml.entities.WorkspaceConnection
        :keyword populate_secrets: If true, make a secondary API call to try filling in the workspace
            connections credentials. Currently only works for api key-based credentials. Defaults to False.
        :paramtype populate_secrets: bool
        :return: Created or update connection.
        :rtype: ~azure.ai.ml.entities.WorkspaceConnection
        """
        rest_workspace_connection = workspace_connection._to_rest_object()
        response = self._operation.create(
            workspace_name=self._workspace_name,
            connection_name=workspace_connection.name,
            body=rest_workspace_connection,
            **self._scope_kwargs,
            **kwargs,
        )
        conn = WorkspaceConnection._from_rest_object(rest_obj=response)
        if populate_secrets and conn is not None:
            self._try_fill_api_key(conn)
        return conn

    @distributed_trace
    @monitor_with_activity(ops_logger, "WorkspaceConnections.Delete", ActivityType.PUBLICAPI)
    def delete(self, name: str, **kwargs: Any) -> None:
        """Delete the connection.

        :param name: Name of the connection.
        :type name: str
        """

        self._operation.delete(
            connection_name=name,
            workspace_name=self._workspace_name,
            **self._scope_kwargs,
            **kwargs,
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "WorkspaceConnections.List", ActivityType.PUBLICAPI)
    def list(
        self,
        connection_type: Optional[str] = None,
        *,
        populate_secrets: bool = False,
        include_data_connections: bool = False,
        **kwargs: Any,
    ) -> Iterable[WorkspaceConnection]:
        """List all connections for a workspace.

        :param connection_type: Type of connection to list.
        :type connection_type: Optional[str]
        :keyword populate_secrets: If true, make a secondary API call to try filling in the workspace
            connections credentials. Currently only works for api key-based credentials. Defaults to False.
        :paramtype populate_secrets: bool
        :keyword include_data_connections: If true, also return data connections. Defaults to False.
        :paramtype include_data_connections: bool
        :return: An iterator like instance of connection objects
        :rtype: Iterable[~azure.ai.ml.entities.WorkspaceConnection]
        """

        if include_data_connections:
            if "params" in kwargs:
                kwargs["params"]["includeAll"] = "true"
            else:
                kwargs["params"] = {"includeAll": "true"}

        def post_process_conn(rest_obj):
            result = WorkspaceConnection._from_rest_object(rest_obj)
            if populate_secrets and result is not None:
                self._try_fill_api_key(result)
            return result

        result = self._operation.list(
            workspace_name=self._workspace_name,
            cls=lambda objs: [post_process_conn(obj) for obj in objs],
            category=_snake_to_camel(connection_type) if connection_type else connection_type,
            **self._scope_kwargs,
            **kwargs,
        )

        return cast(Iterable[WorkspaceConnection], result)
