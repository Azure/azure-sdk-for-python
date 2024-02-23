# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Iterable

from azure.ai.ml._restclient.v2024_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient202401Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.core.polling import LROPoller
from azure.ai.ml._utils._experimental import experimental


class ServerlessEndpointOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient202401Preview,
    ):
        super().__init__(operation_scope, operation_config)
        self._service_client = service_client.serverless_endpoints

    @experimental
    def begin_create_or_update(self, endpoint: "ServerlessEndpoint") -> LROPoller["ServerlessEndpoint"]:
        return self._service_client.begin_create_or_update(
            self._resource_group_name,
            self._workspace_name,
            endpoint.name,
            endpoint,
        )

    @experimental
    def get(self, name: str) -> "ServerlessEndpoint":
        return self._service_client.get(
            self._resource_group_name,
            self._workspace_name,
            name,
        )

    @experimental
    def list(self) -> Iterable["ServerlessEndpoint"]:
        return self._service_client.list(self._resource_group_name, self._workspace_name)

    @experimental
    def begin_delete(self) -> LROPoller[None]:
        return self._service_client.begin_delete(self._resource_group_name, self._workspace_name)

    @experimental
    def get_keys(self, name: str) -> "ServerlessEndpointKeys":
        return self._service_client.list_keys(
            self._resource_group_name,
            self._workspace_name,
            name,
        )

    @experimental
    def begin_regenerate_keys(self, name: str) -> LROPoller[None]:
        return self._service_client.begin_regenerate_keys(
            self._resource_group_name,
            self._workspace_name,
            name,
        )
