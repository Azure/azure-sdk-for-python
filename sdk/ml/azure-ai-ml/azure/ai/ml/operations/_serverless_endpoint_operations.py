# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Iterable

from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml._restclient.v2024_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient202401Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.core.polling import LROPoller
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    MarketplaceSubscription,
    MarketplaceSubscriptionProperties,
)
from azure.ai.ml.entities._endpoint.serverless_endpoint import ServerlessEndpoint
from azure.core.exceptions import HttpResponseError


class ServerlessEndpointOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient202401Preview,
        all_operations: OperationsContainer
    ):
        super().__init__(operation_scope, operation_config)
        self._service_client = service_client.serverless_endpoints
        self._marketplace_subscriptions = service_client.marketplace_subscriptions
        self._all_operations = all_operations

    def _get_workspace_location(self) -> str:
        return str(
            self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location
        )

    @experimental
    def begin_create_or_update(self, endpoint: ServerlessEndpoint) -> LROPoller[ServerlessEndpoint]:
        if not endpoint.location:
            endpoint.location = self._get_workspace_location()
        rest_serverless_endpoint = endpoint._to_rest_object()
        try:
            return self._service_client.begin_create_or_update(
                self._resource_group_name,
                self._workspace_name,
                endpoint.name,
                rest_serverless_endpoint,
                cls=lambda response, deserialized, headers: ServerlessEndpoint._from_rest_object(deserialized)
            )
        except HttpResponseError as e:
            if "The requested model requires an active Azure Marketplace subscription for publisher" in e.message:
                marketplace_subscription = MarketplaceSubscription(
                    properties=MarketplaceSubscriptionProperties(
                        model_id=endpoint.properties.model_settings.model_id,
                    )
                )
                self._marketplace_subscriptions.begin_create_or_update(
                    self._resource_group_name,
                    self._workspace_name,
                    endpoint.name,
                    marketplace_subscription
                ).wait()
                return self._service_client.begin_create_or_update(
                    self._resource_group_name,
                    self._workspace_name,
                    endpoint.name,
                    rest_serverless_endpoint,
                    cls=lambda response, deserialized, headers: ServerlessEndpoint._from_rest_object(deserialized),
                )
            else:
                raise e

    @experimental
    def get(self, name: str) -> ServerlessEndpoint:
        return self._service_client.get(
            self._resource_group_name,
            self._workspace_name,
            name,
            cls=lambda response, deserialized, headers: ServerlessEndpoint._from_rest_object(deserialized)
        )

    @experimental
    def list(self) -> Iterable[ServerlessEndpoint]:
        return self._service_client.list(
            self._resource_group_name,
            self._workspace_name,
            cls=lambda objs: [ServerlessEndpoint._from_rest_object(obj) for obj in objs]
        )

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
