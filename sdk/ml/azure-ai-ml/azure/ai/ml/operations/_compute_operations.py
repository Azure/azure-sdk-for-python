# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict, Iterable, Optional

from azure.ai.ml._restclient.v2023_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022023Preview
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations

from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.constants._common import COMPUTE_UPDATE_ERROR
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.entities import AmlComputeNodeInfo, Compute, Usage, VmSize
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class ComputeOperations(_ScopeDependentOperations):
    """ComputeOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient022023Preview,
        **kwargs: Dict,
    ):
        super(ComputeOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._operation = service_client.compute
        self._workspace_operations = service_client.workspaces
        self._vmsize_operations = service_client.virtual_machine_sizes
        self._usage_operations = service_client.usages
        self._init_kwargs = kwargs

    @distributed_trace
    @monitor_with_activity(logger, "Compute.List", ActivityType.PUBLICAPI)
    def list(self, *, compute_type: Optional[str] = None) -> Iterable[Compute]:
        """List computes of the workspace.

        :param compute_type: the type of the compute to be listed, defaults to amlcompute
        :type compute_type: str
        :return: An iterator like instance of Compute objects
        :rtype: ~azure.core.paging.ItemPaged[Compute]
        """

        return self._operation.list(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            cls=lambda objs: [
                Compute._from_rest_object(obj)
                for obj in objs
                if compute_type is None or Compute._from_rest_object(obj).type.lower() == compute_type.lower()
            ],
        )

    @distributed_trace
    @monitor_with_activity(logger, "Compute.Get", ActivityType.PUBLICAPI)
    def get(self, name: str) -> Compute:
        """Get a compute resource.

        :param name: Name of the compute
        :type name: str
        :return: Compute object
        :rtype: Compute
        """

        rest_obj = self._operation.get(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
        )
        return Compute._from_rest_object(rest_obj)

    @distributed_trace
    @monitor_with_activity(logger, "Compute.ListNodes", ActivityType.PUBLICAPI)
    def list_nodes(self, name: str) -> Iterable[AmlComputeNodeInfo]:
        """Get a compute resource nodes.

        :param name: Name of the compute
        :type name: str
        :return: An iterator over aml compute node information objects
        :rtype: ~azure.core.paging.ItemPaged[AmlComputeNodeInfo]
        """
        return self._operation.list_nodes(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
            cls=lambda objs: [AmlComputeNodeInfo._from_rest_object(obj) for obj in objs],
        )

    @distributed_trace
    @monitor_with_activity(logger, "Compute.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, compute: Compute) -> LROPoller[Compute]:
        """Create a compute.

        :param compute: Compute definition.
        :type compute: Compute
        :return: An instance of LROPoller that returns a Compute.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Compute]
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
    @monitor_with_activity(logger, "Compute.Attach", ActivityType.PUBLICAPI)
    def begin_attach(self, compute: Compute, **kwargs: Any) -> LROPoller[Compute]:
        """Attaches a compute to the workspace.

        :param compute: Compute definition.
        :type compute: Compute
        :return: An instance of LROPoller that returns Compute.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Compute]
        """
        return self.begin_create_or_update(compute=compute, **kwargs)

    @distributed_trace
    @monitor_with_activity(logger, "Compute.BeginUpdate", ActivityType.PUBLICAPI)
    def begin_update(self, compute: Compute) -> LROPoller[Compute]:
        """Update a compute. Currently only valid for AmlCompute.

        :param compute: Compute resource.
        :type compute: Compute
        :return: An instance of LROPoller that returns Compute.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Compute]
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
    @monitor_with_activity(logger, "Compute.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, *, action: str = "Delete") -> LROPoller[None]:
        """Delete a compute.

        :param name: The name of the compute.
        :type name: str
        :param action: Action to perform. Possible values: ["Delete", "Detach"]. Defaults to "Delete".
        :type action: Optional[str]
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        return self._operation.begin_delete(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            compute_name=name,
            underlying_resource_action=action,
            **self._init_kwargs,
        )

    @distributed_trace
    @monitor_with_activity(logger, "Compute.BeginStart", ActivityType.PUBLICAPI)
    def begin_start(self, name: str) -> LROPoller[None]:
        """Start a compute.

        :param name: The name of the compute.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: azure.core.polling.LROPoller[None]
        """

        return self._operation.begin_start(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
        )

    @distributed_trace
    @monitor_with_activity(logger, "Compute.BeginStop", ActivityType.PUBLICAPI)
    def begin_stop(self, name: str) -> LROPoller[None]:
        """Stop a compute.

        :param name: The name of the compute.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: azure.core.polling.LROPoller[None]
        """
        return self._operation.begin_stop(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
        )

    @distributed_trace
    @monitor_with_activity(logger, "Compute.BeginRestart", ActivityType.PUBLICAPI)
    def begin_restart(self, name: str) -> LROPoller[None]:
        """Restart a compute.

        :param name: The name of the compute.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: azure.core.polling.LROPoller[None]
        """
        return self._operation.begin_restart(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            name,
        )

    @distributed_trace
    @monitor_with_activity(logger, "Compute.ListUsage", ActivityType.PUBLICAPI)
    def list_usage(self, *, location: Optional[str] = None) -> Iterable[Usage]:
        """Gets the current usage information as well as limits for AML resources for given subscription and location.

        :param location: The location for which resource usage is queried.
            If location not provided , defaults to workspace location
        :type location: str
        :return: An iterator over current usage info
        :rtype: ~azure.core.paging.ItemPaged[Usage]
        """
        if not location:
            location = self._get_workspace_location()
        return self._usage_operations.list(
            location=location,
            cls=lambda objs: [Usage._from_rest_object(obj) for obj in objs],
        )

    @distributed_trace
    @monitor_with_activity(logger, "Compute.ListSizes", ActivityType.PUBLICAPI)
    def list_sizes(self, *, location: Optional[str] = None, compute_type: Optional[str] = None) -> Iterable[VmSize]:
        """Returns supported VM Sizes in a location.

        :param location: The location upon which virtual-machine-sizes is queried.
            If location not provided, defaults to workspace location.
        :type location: str

        :return: An iterator over virtual machine sizes.
        :rtype: Iterable[VmSize]
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

    def _get_workspace_location(self) -> str:
        workspace = self._workspace_operations.get(self._resource_group_name, self._workspace_name)
        return workspace.location
