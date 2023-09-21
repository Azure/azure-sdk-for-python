# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable

from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities import Policy
from azure.core.tracing.decorator import distributed_trace
from azure.ai.ml._restclient.v2023_06_01_preview.models import ListComputePoliciesResponse

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class ComputePolicyOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient,
        **kwargs: Dict,
    ) -> None:
        super(ComputePolicyOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._operation = service_client.hub_policy
        self._workspace_operations = service_client.workspaces
        self._init_kwargs = kwargs

    @distributed_trace
    @monitor_with_activity(logger, "Policy.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, policy: Policy) -> Policy:
        policy_rest_obj = policy._to_rest_object()

        self._operation.create_or_update(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            policy_name=policy.name,
            body=policy_rest_obj,
        )
        return self.get(policy.name)

    @distributed_trace
    @monitor_with_activity(logger, "Policy.List", ActivityType.PUBLICAPI)
    def list(self) -> Iterable[Policy]:
        policies : ListComputePoliciesResponse = self._operation.list(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
        )

        return (Policy._from_rest_object(policy) for policy in policies.policies)

    @distributed_trace
    @monitor_with_activity(logger, "Policy.Get", ActivityType.PUBLICAPI)
    def get(self, name: str) -> Policy:
        rest_obj = self._operation.get(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            policy_name=name
        )

        return Policy._from_rest_object(rest_obj)

    @distributed_trace
    @monitor_with_activity(logger, "Policy.Delete", ActivityType.PUBLICAPI)
    def delete(self, name: str) -> None:
        return self._operation.delete(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            policy_name=name
        )