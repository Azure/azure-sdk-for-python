# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict, Iterable, List, Optional, Union, cast

from marshmallow import ValidationError

from azure.ai.ml._restclient.v2024_07_01_preview import AzureMachineLearningWorkspaces as ServiceClient072024Preview
from azure.ai.ml._restclient.v2024_07_01_preview.models import ManagedNetworkProvisionOptions
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils.utils import (
    _get_workspace_base_url,
    get_resource_and_group_name_from_resource_id,
    get_resource_group_name_from_resource_group_id,
    modified_operation_client,
)
from azure.ai.ml.constants._common import AzureMLResourceType, Scope, WorkspaceKind
from azure.ai.ml.entities import (
    DiagnoseRequestProperties,
    DiagnoseResponseResult,
    DiagnoseResponseResultValue,
    DiagnoseWorkspaceParameters,
    ManagedNetworkProvisionStatus,
    Workspace,
    WorkspaceKeys,
)
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._workspace_operations_base import WorkspaceOperationsBase

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class WorkspaceOperations(WorkspaceOperationsBase):
    """Handles workspaces and its subclasses, hubs and projects.

    You should not instantiate this class directly. Instead, you should create
    an MLClient instance that instantiates it for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient072024Preview,
        all_operations: OperationsContainer,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Any,
    ):
        self.dataplane_workspace_operations = (
            kwargs.pop("dataplane_client").workspaces if kwargs.get("dataplane_client") else None
        )
        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline", None)
        ops_logger.update_info(kwargs)
        self._provision_network_operation = service_client.managed_network_provisions
        super().__init__(
            operation_scope=operation_scope,
            service_client=service_client,
            all_operations=all_operations,
            credentials=credentials,
            **kwargs,
        )

    @monitor_with_activity(ops_logger, "Workspace.List", ActivityType.PUBLICAPI)
    def list(
        self, *, scope: str = Scope.RESOURCE_GROUP, filtered_kinds: Optional[Union[str, List[str]]] = None
    ) -> Iterable[Workspace]:
        """List all Workspaces that the user has access to in the current resource group or subscription.

        :keyword scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :paramtype scope: str
        :keyword filtered_kinds: The kinds of workspaces to list. If not provided, all workspaces varieties will
            be listed. Accepts either a single kind, or a list of them.
            Valid kind options include: "default", "project", and "hub".
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

        # Kind should be converted to a comma-separating string if multiple values are supplied.
        formatted_kinds = filtered_kinds
        if filtered_kinds and not isinstance(filtered_kinds, str):
            formatted_kinds = ",".join(filtered_kinds)  # type: ignore[arg-type]

        if scope == Scope.SUBSCRIPTION:
            return cast(
                Iterable[Workspace],
                self._operation.list_by_subscription(
                    cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs],
                    kind=formatted_kinds,
                ),
            )
        return cast(
            Iterable[Workspace],
            self._operation.list_by_resource_group(
                self._resource_group_name,
                cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs],
                kind=formatted_kinds,
            ),
        )

    @monitor_with_activity(ops_logger, "Workspace.Get", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def get(self, name: Optional[str] = None, **kwargs: Dict) -> Optional[Workspace]:
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

    @monitor_with_activity(ops_logger, "Workspace.Get_Keys", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-differ
    def get_keys(self, name: Optional[str] = None) -> Optional[WorkspaceKeys]:
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

    @monitor_with_activity(ops_logger, "Workspace.BeginSyncKeys", ActivityType.PUBLICAPI)
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

    @monitor_with_activity(ops_logger, "Workspace.BeginProvisionNetwork", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_provision_network(
        self,
        *,
        workspace_name: Optional[str] = None,
        include_spark: bool = False,
        **kwargs: Any,
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

    @monitor_with_activity(ops_logger, "Workspace.BeginCreate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-differ
    def begin_create(
        self,
        workspace: Workspace,
        update_dependent_resources: bool = False,
        **kwargs: Any,
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
        # Add hub values to project if possible
        if workspace._kind == WorkspaceKind.PROJECT:
            try:
                parent_name = workspace._hub_id.split("/")[-1] if workspace._hub_id else ""
                parent = self.get(parent_name)
                if parent:
                    # Project location can not differ from hub, so try to force match them if possible.
                    workspace.location = parent.location
                    # Project's technically don't save their PNA, since it implicitly matches their parent's.
                    # However, some PNA-dependent code is run server-side before that alignment is made, so make sure
                    # they're aligned before the request hits the server.
                    workspace.public_network_access = parent.public_network_access
            except HttpResponseError:
                module_logger.warning("Failed to get parent hub for project, some values won't be transferred:")
        try:
            return super().begin_create(workspace, update_dependent_resources=update_dependent_resources, **kwargs)
        except HttpResponseError as error:
            if error.status_code == 403 and workspace._kind == WorkspaceKind.PROJECT:
                resource_group = kwargs.get("resource_group") or self._resource_group_name
                hub_name, _ = get_resource_and_group_name_from_resource_id(workspace._hub_id)
                rest_workspace_obj = self._operation.get(resource_group, hub_name)
                hub_default_project_resource_group = get_resource_group_name_from_resource_group_id(
                    rest_workspace_obj.workspace_hub_config.default_workspace_resource_group
                )
                # we only want to try joining the workspaceHub when the default workspace resource group
                # is same with the user provided resource group.
                if hub_default_project_resource_group == resource_group:
                    log_msg = (
                        "User lacked permission to create project workspace,"
                        + "trying to join the workspaceHub default resource group."
                    )
                    module_logger.info(log_msg)
                    return self._begin_join(workspace, **kwargs)
            raise error

    @monitor_with_activity(ops_logger, "Workspace.BeginUpdate", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_update(
        self,
        workspace: Workspace,
        *,
        update_dependent_resources: bool = False,
        **kwargs: Any,
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

    @monitor_with_activity(ops_logger, "Workspace.BeginDelete", ActivityType.PUBLICAPI)
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
    @monitor_with_activity(ops_logger, "Workspace.BeginDiagnose", ActivityType.PUBLICAPI)
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
        def callback(_: Any, deserialized: Any, args: Any) -> Optional[DiagnoseResponseResultValue]:
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

    @distributed_trace
    def _begin_join(self, workspace: Workspace, **kwargs: Dict) -> LROPoller[Workspace]:
        """Join a WorkspaceHub by creating a project workspace under workspaceHub's default resource group.

        :param workspace: Project workspace definition to create
        :type workspace: Workspace
        :return: An instance of LROPoller that returns a project Workspace.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Workspace]
        """
        if not workspace._hub_id:
            raise ValidationError(
                "{0} is not a Project workspace, join operation can only perform with workspaceHub provided".format(
                    workspace.name
                )
            )

        resource_group = kwargs.get("resource_group") or self._resource_group_name
        hub_name, _ = get_resource_and_group_name_from_resource_id(workspace._hub_id)
        rest_workspace_obj = self._operation.get(resource_group, hub_name)

        # override the location to the same as the workspaceHub
        workspace.location = rest_workspace_obj.location
        # set this to system assigned so ARM will create MSI
        if not hasattr(workspace, "identity") or not workspace.identity:
            workspace.identity = IdentityConfiguration(type="system_assigned")

        workspace_operations = self._all_operations.all_operations[AzureMLResourceType.WORKSPACE]
        workspace_base_uri = _get_workspace_base_url(workspace_operations, hub_name, self._requests_pipeline)

        # pylint:disable=unused-argument
        def callback(_: Any, deserialized: Any, args: Any) -> Optional[Workspace]:
            return Workspace._from_rest_object(deserialized)

        with modified_operation_client(self.dataplane_workspace_operations, workspace_base_uri):
            result = self.dataplane_workspace_operations.begin_hub_join(
                resource_group_name=resource_group,
                workspace_name=hub_name,
                project_workspace_name=workspace.name,
                body=workspace._to_rest_object(),
                cls=callback,
                **self._init_kwargs,
            )
            return result
