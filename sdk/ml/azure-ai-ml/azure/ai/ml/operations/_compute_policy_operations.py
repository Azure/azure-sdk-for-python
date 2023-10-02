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
        scope = policy.scope
        subscription_id, resource_group_name, workspace_name = self.__get_scope_values(scope)

        policy_rest_obj = policy._to_rest_object()

        self._operation.create_or_update(
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            policy_name=policy.name,
            body=policy_rest_obj,
        )
        return self.get(policy.name, scope=scope)

    @distributed_trace
    @monitor_with_activity(logger, "Policy.List", ActivityType.PUBLICAPI)
    def list(self, workspace_name=None, scope=None) -> Iterable[Policy]:
        if scope is not None:
            subscription_id, resource_group_name, workspace_name = self.__get_scope_values(scope)
        else:
            subscription_id = self._operation_scope.subscription_id
            resource_group_name = self._operation_scope.resource_group_name
            workspace_name = workspace_name or self._workspace_name

        if subscription_id is None or resource_group_name is None or workspace_name is None:
            raise ValueError("Please provide a valid scope or workspace_name or use a MLClient with a workspace set")

        policies: ListComputePoliciesResponse = self._operation.list(
            subscription_id=subscription_id, resource_group_name=resource_group_name, workspace_name=workspace_name
        )

        return (Policy._from_rest_object(policy) for policy in policies.policies)

    @distributed_trace
    @monitor_with_activity(logger, "Policy.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, workspace_name=None, scope=None) -> Policy:
        if scope is not None:
            subscription_id, resource_group_name, workspace_name = self.__get_scope_values(scope)
        else:
            subscription_id = self._operation_scope.subscription_id
            resource_group_name = self._operation_scope.resource_group_name
            workspace_name = workspace_name or self._workspace_name

        if subscription_id is None or resource_group_name is None or workspace_name is None:
            raise ValueError("Please provide a valid scope or workspace_name or use a MLClient with a workspace set")

        rest_obj = self._operation.get(
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            policy_name=name,
        )

        return Policy._from_rest_object(rest_obj)

    @distributed_trace
    @monitor_with_activity(logger, "Policy.Delete", ActivityType.PUBLICAPI)
    def delete(self, name: str, workspace_name=None, scope=None) -> None:
        if scope is not None:
            subscription_id, resource_group_name, workspace_name = self.__get_scope_values(scope)
        else:
            subscription_id = self._operation_scope.subscription_id
            resource_group_name = self._operation_scope.resource_group_name
            workspace_name = workspace_name or self._workspace_name

        if subscription_id is None or resource_group_name is None or workspace_name is None:
            raise ValueError("Please provide a valid scope or workspace_name or use a MLClient with a workspace set")

        return self._operation.delete(
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            policy_name=name,
        )

    def __get_scope_values(self, scope: str):
        scope = scope.split("/")
        subscription_id = scope[2] if len(scope) > 2 else None
        resource_group_name = scope[4] if len(scope) > 4 else None
        workspace_name = scope[8] if len(scope) > 8 else None
        return subscription_id, resource_group_name, workspace_name
