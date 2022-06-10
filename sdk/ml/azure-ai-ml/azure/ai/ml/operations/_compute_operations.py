# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import time
from typing import Any, Dict, Iterable

from azure.core.exceptions import HttpResponseError
from azure.core.polling import LROPoller
from azure.ai.ml._restclient.v2021_10_01 import AzureMachineLearningWorkspaces as ServiceClient102021
from azure.ai.ml._scope_dependent_operations import OperationScope, _ScopeDependentOperations
from azure.ai.ml.constants import ComputeType, LROConfigurations, COMPUTE_UPDATE_ERROR
from azure.ai.ml.entities import Compute, Usage, VmSize, AmlComputeNodeInfo
from azure.ai.ml._utils._azureml_polling import AzureMLPolling, polling_wait
from azure.ai.ml._utils.utils import get_http_response_and_deserialized_from_pipeline_response
from azure.ai.ml._restclient.v2021_10_01.models import (
    AmlComputeNodeInformation,
)

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class ComputeOperations(_ScopeDependentOperations):
    """
    ComputeOperations

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient102021,
        **kwargs: Dict,
    ):
        super(ComputeOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._operation = service_client.compute
        self._workspace_operations = service_client.workspaces
        self._vmsize_operations = service_client.virtual_machine_sizes
        self._usage_operations = service_client.usages
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "Compute.List", ActivityType.PUBLICAPI)
    def list(self, compute_type: str = None) -> Iterable[Compute]:
        """List computes of the workspace

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

    @monitor_with_activity(logger, "Compute.Get", ActivityType.PUBLICAPI)
    def get(self, name: str) -> Compute:
        """Get a compute resource

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

    @monitor_with_activity(logger, "Compute.ListNodes", ActivityType.PUBLICAPI)
    def list_nodes(self, name: str) -> Iterable[AmlComputeNodeInfo]:
        """Get a compute resource nodes

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

    @monitor_with_activity(logger, "Compute.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, compute: Compute, **kwargs: Any) -> LROPoller:
        """Create a compute

        :param compute: Compute definition.
        :type compute: Compute
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        compute.location = self._get_workspace_location()
        compute._set_full_subnet_name(self._operation_scope.subscription_id, self._operation_scope.resource_group_name)

        compute_rest_obj = compute._to_rest_object()

        no_wait = kwargs.get("no_wait", False)
        poller = self._operation.begin_create_or_update(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            compute_name=compute.name,
            parameters=compute_rest_obj,
            polling=True,
        )

        if no_wait:
            return poller
        else:
            return Compute._from_rest_object(poller.result())

    @monitor_with_activity(logger, "Compute.Attach", ActivityType.PUBLICAPI)
    def attach(self, compute: Compute, **kwargs: Any) -> LROPoller:
        """Attaches a compute to the workspace.

        :param compute: Compute definition.
        :type compute: Compute
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        return self.begin_create(compute=compute, **kwargs)

    @monitor_with_activity(logger, "Compute.BeginUpdate", ActivityType.PUBLICAPI)
    def begin_update(self, compute: Compute, **kwargs: Any) -> LROPoller:
        """Update a compute. Currently only valid for AmlCompute.

        :param compute: Compute resource.
        :type compute: Compute
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        if not compute.type == ComputeType.AMLCOMPUTE:
            COMPUTE_UPDATE_ERROR.format(compute.name, compute.type)

        compute_rest_obj = compute._to_rest_object()

        try:
            no_wait = kwargs.get("no_wait", False)
            poller = self._operation.begin_create_or_update(
                self._operation_scope.resource_group_name,
                self._workspace_name,
                compute_name=compute.name,
                parameters=compute_rest_obj,
                polling=True,
            )

            if no_wait:
                return poller
            else:
                return Compute._from_rest_object(poller.result())
        # This is a temporary fix until the swagger with MLC if fixed for update not to throw exception on 202
        except HttpResponseError as e:
            if e.status_code == 202:
                time.sleep(5)
                return self.get(name=compute.name)
            raise e

    @monitor_with_activity(logger, "Compute.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, *, action: str = "Delete", **kwargs: Any) -> LROPoller:
        """Delete a compute

        :param name: The name of the compute.
        :type name: str
        :param action: Action to perform. Possible values: ["Delete", "Detach"]. Defaults to "Delete".
        :type action: Optional[str]
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        start_time = time.time()
        path_format_arguments = {
            "computeName": name,
            "resourceGroupName": self._operation_scope.resource_group_name,
            "workspaceName": self._workspace_name,
        }
        no_wait = kwargs.get("no_wait", False)

        delete_poller = self._operation.begin_delete(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            compute_name=name,
            underlying_resource_action=action,
            polling=AzureMLPolling(
                LROConfigurations.POLL_INTERVAL,
                path_format_arguments=path_format_arguments,
                **self._init_kwargs,
            )
            if not no_wait
            else False,
            polling_interval=LROConfigurations.POLL_INTERVAL,
            **self._init_kwargs,
        )

        if no_wait:
            module_logger.info(f"Delete request initiated for workspace: {name}`\n")
            return delete_poller
        else:
            message = f"Deleting compute {name} "
            polling_wait(poller=delete_poller, start_time=start_time, message=message)

    @monitor_with_activity(logger, "Compute.BeginStart", ActivityType.PUBLICAPI)
    def begin_start(self, name: str, **kwargs: Any) -> LROPoller:
        """Start a compute

        :param name: The name of the compute.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        no_wait = kwargs.get("no_wait", False)
        return self._operation.begin_start(
            self._operation_scope.resource_group_name, self._workspace_name, name, polling=(not no_wait)
        )

    @monitor_with_activity(logger, "Compute.BeginStop", ActivityType.PUBLICAPI)
    def begin_stop(self, name: str, **kwargs: Any) -> LROPoller:
        """Stop a compute.

        :param name: The name of the compute.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        no_wait = kwargs.get("no_wait", False)
        return self._operation.begin_stop(
            self._operation_scope.resource_group_name, self._workspace_name, name, polling=(not no_wait)
        )

    @monitor_with_activity(logger, "Compute.BeginRestart", ActivityType.PUBLICAPI)
    def begin_restart(self, name: str, **kwargs: Any) -> LROPoller:
        """Restart a compute

        :param name: The name of the compute.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        no_wait = kwargs.get("no_wait", False)
        return self._operation.begin_restart(
            self._operation_scope.resource_group_name, self._workspace_name, name, polling=(not no_wait)
        )

    @monitor_with_activity(logger, "Compute.ListUsage", ActivityType.PUBLICAPI)
    def list_usage(self, *, location: str = None) -> Iterable[Usage]:
        """Gets the current usage information as well as limits for AML resources for given subscription
        and location.
        :param location: The location for which resource usage is queried. If location not provided , defaults to workspace location
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

    @monitor_with_activity(logger, "Compute.ListSizes", ActivityType.PUBLICAPI)
    def list_sizes(self, *, location: str = None, compute_type: str = None) -> Iterable[VmSize]:
        """Returns supported VM Sizes in a location.

        :param location: The location upon which virtual-machine-sizes is queried. If location not provided, defaults to workspace location.
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
        else:
            return [VmSize._from_rest_object(item) for item in size_list.value]

    def _get_workspace_location(self) -> str:
        workspace = self._workspace_operations.get(self._resource_group_name, self._workspace_name)
        return workspace.location
