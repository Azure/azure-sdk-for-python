# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable, Optional

from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062023Preview
from azure.ai.ml._restclient.v2023_06_01_preview.models import ManagedNetworkProvisionOptions
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.constants._common import Scope
from azure.ai.ml.entities import (
    DiagnoseRequestProperties,
    DiagnoseResponseResult,
    DiagnoseResponseResultValue,
    DiagnoseWorkspaceParameters,
    Workspace,
    WorkspaceKeys,
    ManagedNetworkProvisionStatus,
)
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from ._workspace_operations_base import WorkspaceOperationsBase

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class WorkspaceOperations(WorkspaceOperationsBase):
    """WorkspaceOperations.

    You should not instantiate this class directly. Instead, you should create
    an MLClient instance that instantiates it for you and attaches it as an attribute.
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
        self._provision_network_operation = service_client.managed_network_provisions
        super().__init__(
            operation_scope=operation_scope,
            service_client=service_client,
            all_operations=all_operations,
            credentials=credentials,
            **kwargs,
        )

    @monitor_with_activity(logger, "Workspace.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP) -> Iterable[Workspace]:
        """List all Workspaces that the user has access to in the current resource group or subscription.

        :keyword scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :paramtype scope: str
        :return: An iterator like instance of Workspace objects
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.Workspace]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_list]
                :end-before: [END workspace_list]
                :language: python
                :dedent: 8
                :caption: List the workspaces by resource group or subscription.
        """

        if scope == Scope.SUBSCRIPTION:
            return self._operation.list_by_subscription(
                cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs]
            )
        return self._operation.list_by_resource_group(
            self._resource_group_name,
            cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs],
        )

    @monitor_with_activity(logger, "Workspace.Get", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def get(self, name: Optional[str] = None, **kwargs: Dict) -> Workspace:
        """Get a Workspace by name.

        :param name: Name of the workspace.
        :type name: str
        :return: The workspace with the provided name.
        :rtype: ~azure.ai.ml.entities.Workspace

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_get]
                :end-before: [END workspace_get]
                :language: python
                :dedent: 8
                :caption: Get the workspace with the given name.
        """

        return super().get(workspace_name=name, **kwargs)

    @monitor_with_activity(logger, "Workspace.Get_Keys", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-differ
    def get_keys(self, name: Optional[str] = None) -> WorkspaceKeys:
        """Get WorkspaceKeys by workspace name.

        :param name: Name of the workspace.
        :type name: str
        :return: Keys of workspace dependent resources.
        :rtype: ~azure.ai.ml.entities.WorkspaceKeys

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_get_keys]
                :end-before: [END workspace_get_keys]
                :language: python
                :dedent: 8
                :caption: Get the workspace keys for the workspace with the given name.
        """
        workspace_name = self._check_workspace_name(name)
        obj = self._operation.list_keys(self._resource_group_name, workspace_name)
        return WorkspaceKeys._from_rest_object(obj)

    @monitor_with_activity(logger, "Workspace.BeginSyncKeys", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_sync_keys(self, name: Optional[str] = None) -> LROPoller[None]:
        """Triggers the workspace to immediately synchronize keys. If keys for any resource in the workspace are
        changed, it can take around an hour for them to automatically be updated. This function enables keys to be
        updated upon request. An example scenario is needing immediate access to storage after regenerating storage
        keys.

        :param name: Name of the workspace.
        :type name: str
        :return: An instance of LROPoller that returns either None or the sync keys result.
        :rtype: ~azure.core.polling.LROPoller[None]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_sync_keys]
                :end-before: [END workspace_sync_keys]
                :language: python
                :dedent: 8
                :caption: Begin sync keys for the workspace with the given name.
        """
        workspace_name = self._check_workspace_name(name)
        return self._operation.begin_resync_keys(self._resource_group_name, workspace_name)

    @monitor_with_activity(logger, "Workspace.BeginProvisionNetwork", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_provision_network(
        self,
        *,
        workspace_name: Optional[str] = None,
        include_spark: bool = False,
        **kwargs,
    ) -> LROPoller[ManagedNetworkProvisionStatus]:
        """Triggers the workspace to provision the managed network. Specifying spark enabled
        as true prepares the workspace managed network for supporting Spark.

        :keyword workspace_name: Name of the workspace.
        :paramtype workspace_name: str
        :keyword include_spark: Whether the workspace managed network should prepare to support Spark.
        :paramtype include_space: bool
        :return: An instance of LROPoller.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.ManagedNetworkProvisionStatus]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_provision_network]
                :end-before: [END workspace_provision_network]
                :language: python
                :dedent: 8
                :caption: Begin provision network for a workspace with managed network.
        """
        workspace_name = self._check_workspace_name(workspace_name)

        poller = self._provision_network_operation.begin_provision_managed_network(
            self._resource_group_name,
            workspace_name,
            ManagedNetworkProvisionOptions(include_spark=include_spark),
            polling=True,
            cls=lambda response, deserialized, headers: ManagedNetworkProvisionStatus._from_rest_object(deserialized),
            **kwargs,
        )
        module_logger.info("Provision network request initiated for workspace: %s\n", workspace_name)
        return poller

    @monitor_with_activity(logger, "Workspace.BeginCreate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-differ
    def begin_create(
        self,
        workspace: Workspace,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[Workspace]:
        """Create a new Azure Machine Learning Workspace.

        Returns the workspace if already exists.

        :param workspace: Workspace definition.
        :type workspace: ~azure.ai.ml.entities.Workspace
        :param update_dependent_resources: Whether to update dependent resources, defaults to False.
        :type update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a Workspace.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Workspace]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_begin_create]
                :end-before: [END workspace_begin_create]
                :language: python
                :dedent: 8
                :caption: Begin create for a workspace.
        """
        return super().begin_create(workspace, update_dependent_resources=update_dependent_resources, **kwargs)

    @monitor_with_activity(logger, "Workspace.BeginUpdate", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_update(
        self,
        workspace: Workspace,
        *,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[Workspace]:
        """Updates a Azure Machine Learning Workspace.

        :param workspace: Workspace definition.
        :type workspace: ~azure.ai.ml.entities.Workspace
        :keyword update_dependent_resources: Whether to update dependent resources, defaults to False.
        :paramtype update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a Workspace.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Workspace]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_begin_update]
                :end-before: [END workspace_begin_update]
                :language: python
                :dedent: 8
                :caption: Begin update for a workspace.
        """
        return super().begin_update(workspace, update_dependent_resources=update_dependent_resources, **kwargs)

    @monitor_with_activity(logger, "Workspace.BeginDelete", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_delete(
        self, name: str, *, delete_dependent_resources: bool, permanently_delete: bool = False, **kwargs: Dict
    ) -> LROPoller[None]:
        """Delete a workspace.

        :param name: Name of the workspace
        :type name: str
        :keyword delete_dependent_resources: Whether to delete resources associated with the workspace,
            i.e., container registry, storage account, key vault, application insights, log analytics.
            The default is False. Set to True to delete these resources.
        :paramtype delete_dependent_resources: bool
        :keyword permanently_delete: Workspaces are soft-deleted by default to allow recovery of workspace data.
            Set this flag to true to override the soft-delete behavior and permanently delete your workspace.
        :paramtype permanently_delete: bool
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_begin_delete]
                :end-before: [END workspace_begin_delete]
                :language: python
                :dedent: 8
                :caption: Begin permanent (force) deletion for a workspace and delete dependent resources.
        """
        return super().begin_delete(
            name, delete_dependent_resources=delete_dependent_resources, permanently_delete=permanently_delete, **kwargs
        )

    @distributed_trace
    @monitor_with_activity(logger, "Workspace.BeginDiagnose", ActivityType.PUBLICAPI)
    def begin_diagnose(self, name: str, **kwargs: Dict) -> LROPoller[DiagnoseResponseResultValue]:
        """Diagnose workspace setup problems.

        If your workspace is not working as expected, you can run this diagnosis to
        check if the workspace has been broken.
        For private endpoint workspace, it will also help check if the network
        setup to this workspace and its dependent resource has problems or not.

        :param name: Name of the workspace
        :type name: str
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.DiagnoseResponseResultValue]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START workspace_begin_diagnose]
                :end-before: [END workspace_begin_diagnose]
                :language: python
                :dedent: 8
                :caption: Begin diagnose operation for a workspace.
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        parameters = DiagnoseWorkspaceParameters(value=DiagnoseRequestProperties())._to_rest_object()

        # pylint: disable=unused-argument, docstring-missing-param
        def callback(_, deserialized, args):
            """Callback to be called after completion

            :return: DiagnoseResponseResult deserialized.
            :rtype: ~azure.ai.ml.entities.DiagnoseResponseResult
            """
            diagnose_response_result = DiagnoseResponseResult._from_rest_object(deserialized)
            res = None
            if diagnose_response_result:
                res = diagnose_response_result.value
            return res

        poller = self._operation.begin_diagnose(resource_group, name, parameters, polling=True, cls=callback)
        module_logger.info("Diagnose request initiated for workspace: %s\n", name)
        return poller
