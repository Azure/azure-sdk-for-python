# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable, Optional

from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062023Preview
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._workspace_utils import delete_resource_by_arm_id
from azure.ai.ml.constants._common import Scope, ArmConstants
from azure.ai.ml.entities._workspace_hub._constants import WORKSPACE_HUB_KIND
from azure.ai.ml.entities._workspace_hub.workspace_hub import WorkspaceHub
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._workspace_operations_base import WorkspaceOperationsBase

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class WorkspaceHubOperations(WorkspaceOperationsBase):
    """WorkspaceHubOperations.

    You should not instantiate this class directly. Instead, you should create an
    MLClient instance that instantiates it for you and attaches it as an attribute.
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

    @monitor_with_activity(logger, "WorkspaceHub.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP) -> Iterable[WorkspaceHub]:
        """List all WorkspaceHubs that the user has access to in the current resource group or subscription.

        :keyword scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :paramtype scope: str
        :return: An iterator like instance of WorkspaceHub objects
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.WorkspaceHub]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START hub_list]
                :end-before: [END hub_list]
                :language: python
                :dedent: 8
                :caption: List the workspace hubs by resource group or subscription.
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

    @distributed_trace
    @monitor_with_activity(logger, "WorkspaceHub.Get", ActivityType.PUBLICAPI)
    # pylint: disable=arguments-renamed, arguments-differ
    def get(self, name: str, **kwargs: Dict) -> WorkspaceHub:
        """Get a Workspace WorkspaceHub by name.

        :param name: Name of the WorkspaceHub.
        :type name: str
        :return: The WorkspaceHub with the provided name.
        :rtype: ~azure.ai.ml.entities.WorkspaceHub

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START hub_get]
                :end-before: [END hub_get]
                :language: python
                :dedent: 8
                :caption: Get the workspace hub by name.
        """

        workspace_hub = None
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name)
        if rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == WORKSPACE_HUB_KIND:
            workspace_hub = WorkspaceHub._from_rest_object(rest_workspace_obj)

        return workspace_hub

    @distributed_trace
    @monitor_with_activity(logger, "WorkspaceHub.BeginCreate", ActivityType.PUBLICAPI)
    # pylint: disable=arguments-differ
    def begin_create(
        self,
        *,
        workspace_hub: WorkspaceHub,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[WorkspaceHub]:
        """Create a new WorkspaceHub.

        Returns the WorkspaceHub if already exists.

        :keyword workspace_hub: WorkspaceHub definition.
        :paramtype workspace_hub: ~azure.ai.ml.entities.WorkspaceHub
        :keyword update_dependent_resources: Whether to update dependent resources. Defaults to False.
        :paramtype update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a WorkspaceHub.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.WorkspaceHub]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START hub_begin_create]
                :end-before: [END hub_begin_create]
                :language: python
                :dedent: 8
                :caption: Create the workspace hub.
        """

        def get_callback():
            """Callback to be called after completion"""
            return self.get(name=workspace_hub.name)

        return super().begin_create(
            workspace=workspace_hub,
            update_dependent_resources=update_dependent_resources,
            get_callback=get_callback,
            **kwargs,
        )

    @distributed_trace
    @monitor_with_activity(logger, "WorkspaceHub.BeginUpdate", ActivityType.PUBLICAPI)
    # pylint: disable=arguments-renamed
    def begin_update(
        self,
        workspace_hub: WorkspaceHub,
        *,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[WorkspaceHub]:
        """Update Friendly Name, Description, Tags, PNA, Managed Network Settings, or Encryption of a WorkspaceHub.

        :param workspace_hub: WorkspaceHub resource.
        :type workspace_hub: ~azure.ai.ml.entities.WorkspaceHub
        :return: An instance of LROPoller that returns a WorkspaceHub.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.WorkspaceHub]
        :raises ~azure.ai.ml.ValidationException: Raised if workspace_hub is not a WorkspaceHub.

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START hub_begin_update]
                :end-before: [END hub_begin_update]
                :language: python
                :dedent: 8
                :caption: Update the workspace hub.
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, workspace_hub.name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == WORKSPACE_HUB_KIND
        ):
            raise ValidationException(
                message="{0} is not a WorkspaceHub.".format(workspace_hub.name),
                no_personal_data_message="The workspace_hub specified is not a WorkspaceHub.",
                target=ErrorTarget.GENERAL,
                error_category=ErrorCategory.USER_ERROR,
            )

        def deserialize_callback(rest_obj):
            """Callback to be called after completion

            :param rest_obj: A rest representation of the Workspace.
            :type: Any
            :return: WorkspaceHub deserialized.
            :rtype: ~azure.ai.ml.entities.WorkspaceHub
            """
            return WorkspaceHub._from_rest_object(rest_obj=rest_obj)

        return super().begin_update(
            workspace=workspace_hub,
            update_dependent_resources=update_dependent_resources,
            deserialize_callback=deserialize_callback,
            **kwargs,
        )

    @distributed_trace
    @monitor_with_activity(logger, "WorkspaceHub.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(
        self, name: str, *, delete_dependent_resources: bool, permanently_delete: bool = False, **kwargs: Dict
    ) -> LROPoller[None]:
        """Delete a WorkspaceHub.

        :param name: Name of the WorkspaceHub
        :type name: str
        :keyword delete_dependent_resources: Whether to delete resources associated with the WorkspaceHub,
            i.e., container registry, storage account, key vault, application insights, log analytics.
            The default is False. Set to True to delete these resources.
        :paramtype delete_dependent_resources: bool
        :keyword permanently_delete: Workspaces are soft-deleted by default to allow recovery of workspace data.
            Set this flag to true to override the soft-delete behavior and permanently delete your workspace.
        :paramtype permanently_delete: bool
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.ai.ml.ValidationException: Raised if workspace with name is not a WorkspaceHub.

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START hub_begin_delete]
                :end-before: [END hub_begin_delete]
                :language: python
                :dedent: 8
                :caption: Delete the workspace hub.
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == WORKSPACE_HUB_KIND
        ):
            raise ValidationException(
                message="{0} is not a WorkspaceHub.".format(name),
                no_personal_data_message="The name of workspace specified is not a WorkspaceHub.",
                target=ErrorTarget.GENERAL,
                error_category=ErrorCategory.USER_ERROR,
            )
        if (
            hasattr(rest_workspace_obj, "workspace_hub_config")
            and hasattr(rest_workspace_obj.workspace_hub_config, "additional_workspace_storage_accounts")
            and rest_workspace_obj.workspace_hub_config.additional_workspace_storage_accounts
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
