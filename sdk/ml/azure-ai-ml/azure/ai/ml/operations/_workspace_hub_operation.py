# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable, Optional

from marshmallow import ValidationError

from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062023Preview
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._workspace_hub.workspace_hub import WorkspaceHub
from azure.ai.ml._utils._workspace_utils import delete_resource_by_arm_id

from azure.ai.ml.constants._common import Scope, ArmConstants
from azure.ai.ml.entities._workspace_hub._constants import WORKSPACE_HUB_KIND
from ._workspace_operations_base import WorkspaceOperationsBase

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class WorkspaceHubOperations(WorkspaceOperationsBase):
    """_HubOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient062023Preview,
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

    # @monitor_with_activity(logger, "WorkspaceHub.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP) -> Iterable[WorkspaceHub]:
        """List all WorkspaceHubs that the user has access to in the current
        resource group or subscription.

        :keyword scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :type scope: str, optional
        :return: An iterator like instance of WorkspaceHub objects
        :rtype: ~azure.core.paging.ItemPaged[WorkspaceHub]
        """

        if scope == Scope.SUBSCRIPTION:
            return self._operation.list_by_subscription(
                cls=lambda objs: [
                    WorkspaceHub._from_rest_object(filterObj)
                    for filterObj in filter(lambda ws: ws.kind.lower() == WORKSPACE_HUB_KIND, objs)
                ]
            )
        return self._operation.list_by_resource_group(
            self._resource_group_name,
            cls=lambda objs: [
                WorkspaceHub._from_rest_object(filterObj)
                for filterObj in filter(lambda ws: ws.kind.lower() == WORKSPACE_HUB_KIND, objs)
            ],
        )

    # @monitor_with_activity(logger, "Hub.Get", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def get(self, name: str, **kwargs: Dict) -> WorkspaceHub:
        """Get a Workspace WorkspaceHub by name.

        :param name: Name of the WorkspaceHub.
        :type name: str
        :return: The WorkspaceHub with the provided name.
        :rtype: WorkspaceHub
        """

        workspace_hub = None
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name)
        if rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == WORKSPACE_HUB_KIND:
            workspace_hub = WorkspaceHub._from_rest_object(rest_workspace_obj)

        return workspace_hub

    # @monitor_with_activity(logger, "Hub.BeginCreate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-differ
    def begin_create(
        self,
        workspace_hub: WorkspaceHub,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[WorkspaceHub]:
        """Create a new WorkspaceHub.

        Returns the WorkspaceHub if already exists.

        :param workspace_hub: WorkspaceHub definition.
        :type workspace_hub: WorkspaceHub
        :param update_dependent_resources: Whether to update dependent resources. Defaults to False.
        :type update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a WorkspaceHub.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.WorkspaceHub]
        """

        def get_callback():
            return self.get(workspace_hub.name)

        return super().begin_create(
            workspace=workspace_hub,
            update_dependent_resources=update_dependent_resources,
            get_callback=get_callback,
            **kwargs,
        )

    # @monitor_with_activity(logger, "Hub.BeginUpdate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def begin_update(
        self,
        workspace_hub: WorkspaceHub,
        *,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[WorkspaceHub]:
        """Update friendly name, description, tags, or PNA, manageNetworkSettings, encryption of a WorkspaceHub.

        :param workspace_hub: WorkspaceHub resource.
        :type workspace_hub: WorkspaceHub
        :return: An instance of LROPoller that returns a WorkspaceHub.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.WorkspaceHub]
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, workspace_hub.name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == WORKSPACE_HUB_KIND
        ):
            raise ValidationError("{0} is not a WorkspaceHub".format(workspace_hub.name))

        def deserialize_callback(rest_obj):
            return WorkspaceHub._from_rest_object(rest_obj=rest_obj)

        return super().begin_update(
            workspace=workspace_hub,
            update_dependent_resources=update_dependent_resources,
            deserialize_callback=deserialize_callback,
            **kwargs,
        )

    # @monitor_with_activity(logger, "Hub.BeginDelete", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_delete(
        self, name: str, *, delete_dependent_resources: bool, permanently_delete: bool = False, **kwargs: Dict
    ) -> LROPoller:
        """Delete a WorkspaceHub.

        :param name: Name of the WorkspaceHub
        :type name: str
        :keyword delete_dependent_resources: Whether to delete resources associated with the WorkspaceHub,
            i.e., container registry, storage account, key vault.
            The default is False. Set to True to delete these resources.
        :type delete_dependent_resources: bool
        :keyword permanently_delete: Workspaces are soft-deleted by default to allow recovery of workspace data.
            Set this flag to true to override the soft-delete behavior and permanently delete your workspace.
        :type permanently_delete: bool
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == WORKSPACE_HUB_KIND
        ):
            raise ValidationError("{0} is not a WorkspaceHub".format(name))
        if hasattr(rest_workspace_obj, "workspace_hub_config") and hasattr(
            rest_workspace_obj.workspace_hub_config, "additional_workspace_storage_accounts"
        ):
            for storageaccount in rest_workspace_obj.workspace_hub_config.additional_workspace_storage_accounts:
                delete_resource_by_arm_id(
                    self._credentials,
                    self._subscription_id,
                    storageaccount,
                    ArmConstants.AZURE_MGMT_STORAGE_API_VERSION,
                )

        return super().begin_delete(
            name=name,
            delete_dependent_resources=delete_dependent_resources,
            permanently_delete=permanently_delete,
            **kwargs,
        )
