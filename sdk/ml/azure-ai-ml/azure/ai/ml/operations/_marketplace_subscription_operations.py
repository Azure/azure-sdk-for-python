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
    """MarketplaceSubscriptionOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

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
        """Create or update a Marketplace Subscription.

        :param marketplace_subscription: The marketplace subscription entity.
        :type marketplace_subscription: ~azure.ai.ml.entities.MarketplaceSubscription
        :return: A poller to track the operation status
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.MarketplaceSubscription]
        """
        return self._service_client.begin_create_or_update(
            self._resource_group_name,
            self._workspace_name,
            marketplace_subscription.name,
            marketplace_subscription._to_rest_object(),  # type: ignore
            cls=lambda response, deserialized, headers: MarketplaceSubscription._from_rest_object(deserialized),  # type: ignore # pylint: disable=line-too-long
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "MarketplaceSubscription.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, **kwargs) -> MarketplaceSubscription:
        """Get a Marketplace Subscription resource.

        :param name: Name of the marketplace subscription.
        :type name: str
        :return: Marketplace subscription object retrieved from the service.
        :rtype: ~azure.ai.ml.entities.MarketplaceSubscription
        """
        return self._service_client.get(
            self._resource_group_name,
            self._workspace_name,
            name,
            cls=lambda response, deserialized, headers: MarketplaceSubscription._from_rest_object(deserialized),  # type: ignore # pylint: disable=line-too-long
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "MarketplaceSubscription.List", ActivityType.PUBLICAPI)
    def list(self, **kwargs) -> Iterable[MarketplaceSubscription]:
        """List marketplace subscriptions of the workspace.

        :return: A list of marketplace subscriptions
        :rtype: ~typing.Iterable[~azure.ai.ml.entities.MarketplaceSubscription]
        """
        return self._service_client.list(
            self._resource_group_name,
            self._workspace_name,
            cls=lambda objs: [MarketplaceSubscription._from_rest_object(obj) for obj in objs],  # type: ignore
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "MarketplaceSubscription.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, **kwargs) -> LROPoller[None]:
        """Delete a Marketplace Subscription.

        :param name: Name of the marketplace subscription.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        return self._service_client.begin_delete(
            self._resource_group_name,
            self._workspace_name,
            name=name,
            **kwargs,
        )
