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
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._autogen_entities.models import MarketplaceSubscription


ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


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
    @monitor_with_activity(ops_logger, "MarketplaceSubscription.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(
        self, marketplace_subscription: MarketplaceSubscription, **kwargs
    ) -> LROPoller[MarketplaceSubscription]:
        return self._service_client.begin_create_or_update(
            self._resource_group_name,
            self._workspace_name,
            marketplace_subscription.name,
            marketplace_subscription._to_rest_object(),
            cls=lambda response, deserialized, headers: MarketplaceSubscription._from_rest_object(deserialized),
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "MarketplaceSubscription.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, **kwargs) -> MarketplaceSubscription:
        return self._service_client.get(
            self._resource_group_name,
            self._workspace_name,
            name,
            cls=lambda response, deserialized, headers: MarketplaceSubscription._from_rest_object(deserialized),
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "MarketplaceSubscription.List", ActivityType.PUBLICAPI)
    def list(self, **kwargs) -> Iterable[MarketplaceSubscription]:
        return self._service_client.list(
            self._resource_group_name,
            self._workspace_name,
            cls=lambda objs: [MarketplaceSubscription._from_rest_object(obj) for obj in objs],
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "MarketplaceSubscription.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, **kwargs) -> LROPoller[None]:
        return self._service_client.begin_delete(
            self._resource_group_name,
            self._workspace_name,
            name=name,
            **kwargs,
        )
