# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Iterable

from azure.ai.ml._restclient.v2024_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient2020404Preview
from azure.ai.ml._restclient.v2024_04_01_preview.models import EndpointDeploymentResourcePropertiesBasicResource
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations, OperationsContainer
from azure.ai.ml.entities._autogen_entities.models import AzureOpenAIDeployment

module_logger = logging.getLogger(__name__)


class AzureOpenAIDeploymentOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient2020404Preview,
    ):
        super().__init__(operation_scope, operation_config)
        self._service_client = service_client.connection

    def list(self, connection_name: str, **kwargs) -> Iterable[AzureOpenAIDeployment]:
        return self._service_client.list_deployments(
            self._resource_group_name,
            self._workspace_name,
            connection_name,
            cls=lambda objs: [AzureOpenAIDeployment._from_rest_object(obj) for obj in objs],
            **kwargs,
        )
