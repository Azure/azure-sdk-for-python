# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Iterable

from azure.ai.ml._restclient.v2024_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient2020404Preview
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml.entities._autogen_entities.models import AzureOpenAIDeployment

from ._workspace_connections_operations import WorkspaceConnectionsOperations

module_logger = logging.getLogger(__name__)


class AzureOpenAIDeploymentOperations(_ScopeDependentOperations):
    """AzureOpenAIDeploymentOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient2020404Preview,
        connections_operations: WorkspaceConnectionsOperations,
    ):
        super().__init__(operation_scope, operation_config)
        self._service_client = service_client.connection
        self._workspace_connections_operations = connections_operations

    def list(self, connection_name: str, **kwargs) -> Iterable[AzureOpenAIDeployment]:
        """List Azure OpenAI deployments of the workspace.

        :param connection_name: Name of the connection from which to list deployments
        :type connection_name: str
        :return: A list of Azure OpenAI deployments
        :rtype: ~typing.Iterable[~azure.ai.ml.entities.AzureOpenAIDeployment]
        """
        connection = self._workspace_connections_operations.get(connection_name)

        def _from_rest_add_connection_name(obj):
            from_rest_deployment = AzureOpenAIDeployment._from_rest_object(obj)
            from_rest_deployment.connection_name = connection_name
            from_rest_deployment.target_url = connection.target
            return from_rest_deployment

        return self._service_client.list_deployments(
            self._resource_group_name,
            self._workspace_name,
            connection_name,
            cls=lambda objs: [_from_rest_add_connection_name(obj) for obj in objs],
            **kwargs,
        )
