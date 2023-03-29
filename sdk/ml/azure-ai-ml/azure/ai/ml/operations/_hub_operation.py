# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable, Optional

from marshmallow import ValidationError

from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._hub.hub import Hub

from azure.ai.ml.constants._common import Scope
from azure.ai.ml.entities._hub._constants import HUB_KIND
from ._workspace_operations_base import WorkspaceOperationsBase

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class HubOperations(WorkspaceOperationsBase):
    """_HubOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient042023Preview,
        all_operations: OperationsContainer,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        ops_logger.update_info(kwargs)
        super().__init__(
            operation_scope=operation_scope,
            service_client=service_client,
            all_operations=all_operations,
            credentials=credentials,
            **kwargs,
        )

    # @monitor_with_activity(logger, "Hub.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP) -> Iterable[Hub]:
        """List all hub workspaces that the user has access to in the current
        resource group or subscription.

        :param scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :type scope: str, optional
        :return: An iterator like instance of Hub objects
        :rtype: ~azure.core.paging.ItemPaged[Hub]
        """

        if scope == Scope.SUBSCRIPTION:
            return self._operation.list_by_subscription(
                cls=lambda objs: [
                    Hub._from_rest_object(filterObj)
                    for filterObj in filter(lambda ws: ws.kind.lower() == HUB_KIND, objs)
                ]
            )
        return self._operation.list_by_resource_group(
            self._resource_group_name,
            cls=lambda objs: [
                Hub._from_rest_object(filterObj)
                for filterObj in filter(lambda ws: ws.kind.lower() == HUB_KIND, objs)
            ],
        )

    # @monitor_with_activity(logger, "Hub.Get", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def get(self, name: str, **kwargs: Dict) -> Hub:
        """Get a hub workspace by name.

        :param name: Name of the hub.
        :type name: str
        :return: The hub with the provided name.
        :rtype: Hub
        """

        hub_workspace = None
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name)
        if rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == HUB_KIND:
            hub_workspace = Hub._from_rest_object(rest_workspace_obj)

        return hub_workspace

    # @monitor_with_activity(logger, "Hub.BeginCreate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-differ
    def begin_create(
        self,
        hub: Hub,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[Hub]:
        """Create a new Hub.

        Returns the hub workspace if already exists.

        :param hub: Hub definition.
        :type hub: Hub
        :type update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a Hub.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Hub]
        """

        def get_callback():
            return self.get(hub.name)

        return super().begin_create(
            workspace=hub,
            update_dependent_resources=update_dependent_resources,
            get_callback=get_callback,
            **kwargs,
        )

    # @monitor_with_activity(logger, "Hub.BeginUpdate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def begin_update(
        self,
        hub: Hub,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[Hub]:
        """Update friendly name, description, tags, or PNA, manageNetworkSettings, encryption of a Hub.

        :param hub: Hub resource.
        :type hub: Hub
        :return: An instance of LROPoller that returns a Hub.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Hub]
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, hub.name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == HUB_KIND
        ):
            raise ValidationError("{0} is not a hub workspace".format(hub.name))

        def deserialize_callback(rest_obj):
            return HubWorkspace._from_rest_object(rest_obj=rest_obj)

        return super().begin_update(
            workspace=hub,
            update_dependent_resources=update_dependent_resources,
            deserialize_callback=deserialize_callback,
            **kwargs,
        )

    # @monitor_with_activity(logger, "Hub.BeginDelete", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_delete(self, name: str, *, delete_dependent_resources: bool, **kwargs: Dict) -> LROPoller:
        """Delete a Hub.

        :param name: Name of the Hub
        :type name: str
        :param delete_dependent_resources: Whether to delete resources associated with the Hub,
            i.e., container registry, storage account, key vault.
            The default is False. Set to True to delete these resources.
        :type delete_dependent_resources: bool
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == HUB_KIND
        ):
            raise ValidationError("{0} is not a hub".format(name))

        return super().begin_delete(name=name, delete_dependent_resources=delete_dependent_resources, **kwargs)
