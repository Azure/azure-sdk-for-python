# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict, Iterable, Optional, cast

from azure.ai.ml._restclient.v2023_08_01_preview import AzureMachineLearningWorkspaces as ServiceClient022023Preview
from azure.ai.ml._restclient.v2024_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042024Preview
from azure.ai.ml._restclient.v2024_04_01_preview.models import SsoSetting
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.constants._common import COMPUTE_UPDATE_ERROR
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.entities import AmlComputeNodeInfo, Compute, Usage, VmSize
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class ComputeOperations(_ScopeDependentOperations):
    """ComputeOperations.

    This class should not be instantiated directly. Instead, use the `compute` attribute of an MLClient object.

    :param operation_scope: Scope variables for the operations classes of an MLClient object.
    :type operation_scope: ~azure.ai.ml._scope_dependent_operations.OperationScope
    :param operation_config: Common configuration for operations classes of an MLClient object.
    :type operation_config: ~azure.ai.ml._scope_dependent_operations.OperationConfig
    :param service_client: Service client to allow end users to operate on Azure Machine Learning
        Workspace resources.
    :type service_client: ~azure.ai.ml._restclient.v2023_02_01_preview.AzureMachineLearningWorkspaces
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient022023Preview,
        service_client_2024: ServiceClient042024Preview,
        **kwargs: Dict,
    ) -> None:
        super(ComputeOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._operation = service_client.compute
        self._operation2024 = service_client_2024.compute
        self._workspace_operations = service_client.workspaces
        self._vmsize_operations = service_client.virtual_machine_sizes
        self._usage_operations = service_client.usages
        self._init_kwargs = kwargs

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.List", ActivityType.PUBLICAPI)
    def list(self, *, compute_type: Optional[str] = None) -> Iterable[Compute]:
        """List computes of the workspace.

        :keyword compute_type: The type of the compute to be listed, case-insensitive. Defaults to AMLCompute.
        :paramtype compute_type: Optional[str]
        :return: An iterator like instance of Compute objects.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.Compute]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_list]
                :end-before: [END compute_operations_list]
                :language: python
                :dedent: 8
                :caption: Retrieving a list of the AzureML Kubernetes compute resources in a workspace.
        """

        return cast(
            Iterable[Compute],
            self._operation.list(
                self._operation_scope.resource_group_name,
                self._workspace_name,
                cls=lambda objs: [
                    Compute._from_rest_object(obj)
                    for obj in objs
                    if compute_type is None or str(Compute._from_rest_object(obj).type).lower() == compute_type.lower()
                ],
            ),
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.Get", ActivityType.PUBLICAPI)
    def get(self, name: str) -> Compute:
        """Get a compute resource.

        :param name: Name of the compute resource.
        :type name: str
        :return: A Compute object.
        :rtype: ~azure.ai.ml.entities.Compute

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_get]
                :end-before: [END compute_operations_get]
                :language: python
                :dedent: 8
                :caption: Retrieving a compute resource from a workspace.
        """

        rest_obj = self._operation.get(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
        )
        return Compute._from_rest_object(rest_obj)

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.ListNodes", ActivityType.PUBLICAPI)
    def list_nodes(self, name: str) -> Iterable[AmlComputeNodeInfo]:
        """Retrieve a list of a compute resource's nodes.

        :param name: Name of the compute resource.
        :type name: str
        :return: An iterator-like instance of AmlComputeNodeInfo objects.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.AmlComputeNodeInfo]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_list_nodes]
                :end-before: [END compute_operations_list_nodes]
                :language: python
                :dedent: 8
                :caption: Retrieving a list of nodes from a compute resource.
        """
        return cast(
            Iterable[AmlComputeNodeInfo],
            self._operation.list_nodes(
                self._operation_scope.resource_group_name,
                self._workspace_name,
                name,
                cls=lambda objs: [AmlComputeNodeInfo._from_rest_object(obj) for obj in objs],
            ),
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, compute: Compute) -> LROPoller[Compute]:
        """Create and register a compute resource.

        :param compute: The compute resource definition.
        :type compute: ~azure.ai.ml.entities.Compute
        :return: An instance of LROPoller that returns a Compute object once the
            long-running operation is complete.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Compute]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_create_update]
                :end-before: [END compute_operations_create_update]
                :language: python
                :dedent: 8
                :caption: Creating and registering a compute resource.
        """
        if compute.type != ComputeType.AMLCOMPUTE:
            if compute.location:
                module_logger.warning(
                    "Warning: 'Location' is not supported for compute type %s and will not be used.",
                    compute.type,
                )
            compute.location = self._get_workspace_location()

        if not compute.location:
            compute.location = self._get_workspace_location()

        compute._set_full_subnet_name(
            self._operation_scope.subscription_id,
            self._operation_scope.resource_group_name,
        )

        compute_rest_obj = compute._to_rest_object()

        poller = self._operation.begin_create_or_update(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            compute_name=compute.name,
            parameters=compute_rest_obj,
            polling=True,
            cls=lambda response, deserialized, headers: Compute._from_rest_object(deserialized),
        )

        return poller

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.Attach", ActivityType.PUBLICAPI)
    def begin_attach(self, compute: Compute, **kwargs: Any) -> LROPoller[Compute]:
        """Attach a compute resource to the workspace.

        :param compute: The compute resource definition.
        :type compute: ~azure.ai.ml.entities.Compute
        :return: An instance of LROPoller that returns a Compute object once the
            long-running operation is complete.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Compute]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_attach]
                :end-before: [END compute_operations_attach]
                :language: python
                :dedent: 8
                :caption: Attaching a compute resource to the workspace.
        """
        return self.begin_create_or_update(compute=compute, **kwargs)

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.BeginUpdate", ActivityType.PUBLICAPI)
    def begin_update(self, compute: Compute) -> LROPoller[Compute]:
        """Update a compute resource. Currently only valid for AmlCompute resource types.

        :param compute: The compute resource definition.
        :type compute: ~azure.ai.ml.entities.Compute
        :return: An instance of LROPoller that returns a Compute object once the
            long-running operation is complete.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Compute]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_update]
                :end-before: [END compute_operations_update]
                :language: python
                :dedent: 8
                :caption: Updating an AmlCompute resource.
        """
        if not compute.type == ComputeType.AMLCOMPUTE:
            COMPUTE_UPDATE_ERROR.format(compute.name, compute.type)

        compute_rest_obj = compute._to_rest_object()

        poller = self._operation.begin_create_or_update(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            compute_name=compute.name,
            parameters=compute_rest_obj,
            polling=True,
            cls=lambda response, deserialized, headers: Compute._from_rest_object(deserialized),
        )

        return poller

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, *, action: str = "Delete") -> LROPoller[None]:
        """Delete or detach a compute resource.

        :param name: The name of the compute resource.
        :type name: str
        :keyword action: Action to perform. Possible values: ["Delete", "Detach"]. Defaults to "Delete".
        :type action: str
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_delete]
                :end-before: [END compute_operations_delete]
                :language: python
                :dedent: 8
                :caption: Delete compute example.
        """
        return self._operation.begin_delete(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            compute_name=name,
            underlying_resource_action=action,
            **self._init_kwargs,
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.BeginStart", ActivityType.PUBLICAPI)
    def begin_start(self, name: str) -> LROPoller[None]:
        """Start a compute instance.

        :param name: The name of the compute instance.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: azure.core.polling.LROPoller[None]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_start]
                :end-before: [END compute_operations_start]
                :language: python
                :dedent: 8
                :caption: Starting a compute instance.
        """

        return self._operation.begin_start(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.BeginStop", ActivityType.PUBLICAPI)
    def begin_stop(self, name: str) -> LROPoller[None]:
        """Stop a compute instance.

        :param name: The name of the compute instance.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: azure.core.polling.LROPoller[None]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_stop]
                :end-before: [END compute_operations_stop]
                :language: python
                :dedent: 8
                :caption: Stopping a compute instance.
        """
        return self._operation.begin_stop(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.BeginRestart", ActivityType.PUBLICAPI)
    def begin_restart(self, name: str) -> LROPoller[None]:
        """Restart a compute instance.

        :param name: The name of the compute instance.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: azure.core.polling.LROPoller[None]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_restart]
                :end-before: [END compute_operations_restart]
                :language: python
                :dedent: 8
                :caption: Restarting a stopped compute instance.
        """
        return self._operation.begin_restart(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.ListUsage", ActivityType.PUBLICAPI)
    def list_usage(self, *, location: Optional[str] = None) -> Iterable[Usage]:
        """List the current usage information as well as AzureML resource limits for the
        given subscription and location.

        :keyword location: The location for which resource usage is queried.
            Defaults to workspace location.
        :paramtype location: Optional[str]
        :return: An iterator over current usage info objects.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.Usage]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_list_usage]
                :end-before: [END compute_operations_list_usage]
                :language: python
                :dedent: 8
                :caption: Listing resource usage for the workspace location.
        """
        if not location:
            location = self._get_workspace_location()
        return cast(
            Iterable[Usage],
            self._usage_operations.list(
                location=location,
                cls=lambda objs: [Usage._from_rest_object(obj) for obj in objs],
            ),
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.ListSizes", ActivityType.PUBLICAPI)
    def list_sizes(self, *, location: Optional[str] = None, compute_type: Optional[str] = None) -> Iterable[VmSize]:
        """List the supported VM sizes in a location.

        :keyword location: The location upon which virtual-machine-sizes is queried.
            Defaults to workspace location.
        :paramtype location: str
        :keyword compute_type: The type of the compute to be listed, case-insensitive. Defaults to AMLCompute.
        :paramtype compute_type: Optional[str]
        :return: An iterator over virtual machine size objects.
        :rtype: Iterable[~azure.ai.ml.entities.VmSize]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_compute.py
                :start-after: [START compute_operations_list_sizes]
                :end-before: [END compute_operations_list_sizes]
                :language: python
                :dedent: 8
                :caption: Listing the supported VM sizes in the workspace location.
        """
        if not location:
            location = self._get_workspace_location()
        size_list = self._vmsize_operations.list(location=location)
        if not size_list:
            return []
        if compute_type:
            return [
                VmSize._from_rest_object(item)
                for item in size_list.value
                if compute_type.lower() in (supported_type.lower() for supported_type in item.supported_compute_types)
            ]
        return [VmSize._from_rest_object(item) for item in size_list.value]

    @distributed_trace
    @monitor_with_activity(ops_logger, "Compute.enablesso", ActivityType.PUBLICAPI)
    @experimental
    def enable_sso(self, *, name: str, enable_sso: bool = True) -> None:
        """enable sso for a compute instance.

        :keyword name: Name of the compute instance.
        :paramtype name: str
        :keyword enable_sso: enable sso bool flag
            Default to True
        :paramtype enable_sso: bool
        """

        self._operation2024.update_sso_settings(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
            parameters=SsoSetting(enable_sso=enable_sso),
        )

    def _get_workspace_location(self) -> str:
        workspace = self._workspace_operations.get(self._resource_group_name, self._workspace_name)
        return str(workspace.location)
