# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Iterable
from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient122022Preview
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope

from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._workspace.networking import OutboundRule
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class WorkspaceOutboundRuleOperations:
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient122022Preview,
        all_operations: OperationsContainer,
        credentials: TokenCredential = None,
        **kwargs: Dict,
    ):
        ops_logger.update_info(kwargs)
        self._subscription_id = operation_scope.subscription_id
        self._resource_group_name = operation_scope.resource_group_name
        self._default_workspace_name = operation_scope.workspace_name
        self._all_operations = all_operations
        self._rule_operation = service_client.managed_network_settings_rule
        self._credentials = credentials
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "WorkspaceOutboundRule.Get", ActivityType.PUBLICAPI)
    def get(self, resource_group: str, ws_name: str, outbound_rule_name: str, **kwargs) -> OutboundRule:
        workspace_name = self._check_workspace_name(ws_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        obj = self._rule_operation.get(resource_group, workspace_name, outbound_rule_name)
        return OutboundRule._from_rest_object(obj.properties, name=obj.name)  # pylint: disable=protected-access

    @monitor_with_activity(logger, "WorkspaceOutboundRule.List", ActivityType.PUBLICAPI)
    def list(self, resource_group: str, ws_name: str, **kwargs) -> Iterable[OutboundRule]:
        workspace_name = self._check_workspace_name(ws_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        rest_rules = self._rule_operation.list(resource_group, workspace_name)

        result = [
            OutboundRule._from_rest_object(rest_obj=obj.properties, name=obj.name)  # pylint: disable=protected-access
            for obj in rest_rules
        ]
        return result

    @monitor_with_activity(logger, "WorkspaceOutboundRule.Remove", ActivityType.PUBLICAPI)
    def begin_remove(self, resource_group: str, ws_name: str, outbound_rule_name: str, **kwargs) -> LROPoller[None]:
        workspace_name = self._check_workspace_name(ws_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        poller = self._rule_operation.begin_delete(
            resource_group_name=resource_group,
            workspace_name=workspace_name,
            rule_name=outbound_rule_name,
        )
        module_logger.info("Delete request initiated for outbound rule: %s\n", outbound_rule_name)
        return poller

    def _check_workspace_name(self, name) -> str:
        workspace_name = name or self._default_workspace_name
        if not workspace_name:
            msg = "Please provide a workspace name or use a MLClient with a workspace name set."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.WORKSPACE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return workspace_name
