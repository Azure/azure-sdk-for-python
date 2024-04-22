# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Iterable

from azure.ai.ml._restclient.v2024_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient202401Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.core.polling import LROPoller
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._autogen_entities.models import MarketplaceSubscription


class MarketplaceSubscriptionOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient202401Preview,
    ):
        super().__init__(operation_scope, operation_config)
        self._service_client = service_client.marketplace_subscriptions

    @experimental
    def begin_create_or_update(
        self, marketplace_subscription: MarketplaceSubscription
    ) -> LROPoller[MarketplaceSubscription]:
        return self._service_client.begin_create_or_update(
            self._resource_group_name,
            self._workspace_name,
            marketplace_subscription.name,
            marketplace_subscription._to_rest_object(),
        )

    @experimental
    def get(self, name: str) -> MarketplaceSubscription:
        return self._service_client.get(
            self._resource_group_name,
            self._workspace_name,
            name,
            cls=lambda response, deserialized, headers: MarketplaceSubscription._from_rest_object(deserialized),
        )

    @experimental
    def list(self) -> Iterable[MarketplaceSubscription]:
        return self._service_client.list(
            self._resource_group_name,
            self._workspace_name,
            cls=lambda objs: [MarketplaceSubscription._from_rest_object(obj) for obj in objs],
        )

    @experimental
    def begin_delete(self, name: str) -> LROPoller[None]:
        return self._service_client.begin_delete(
            self._resource_group_name,
            self._workspace_name,
            name=name,
        )
