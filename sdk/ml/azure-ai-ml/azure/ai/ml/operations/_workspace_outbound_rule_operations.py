# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# for now disable all warnings
# pylint: disable-all

from typing import Dict, Iterable, Tuple

from azure.ai.ml._arm_deployments import ArmDeploymentExecutor
from azure.ai.ml._arm_deployments.arm_helper import get_template
from azure.ai.ml._restclient.v2022_12_01_preview import AzureMachineLearningWorkspaces as ServiceClient122022Preview
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    EncryptionKeyVaultUpdateProperties,
    EncryptionUpdateProperties,
    WorkspaceUpdateParameters,
)
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._workspace_utils import (
    delete_resource_by_arm_id,
    get_deployment_name,
    get_name_for_dependent_resource,
    get_resource_and_group_name,
    get_resource_group_location,
)
from azure.ai.ml._utils.utils import from_iso_duration_format_min_sec
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._version import VERSION
from azure.ai.ml.constants import ManagedServiceIdentityType
from azure.ai.ml.constants._common import ArmConstants, LROConfigurations, WorkspaceResourceConstants, Scope
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._workspace.networking import ManagedNetwork, OutboundRule
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller, PollingMethod
from azure.core.tracing.decorator import distributed_trace


class WorkspaceOutboundRuleOperations:
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient122022Preview,
        all_operations: OperationsContainer,
        credentials: TokenCredential = None,
        **kwargs: Dict,
    ):
        self._subscription_id = operation_scope.subscription_id
        self._resource_group_name = operation_scope.resource_group_name
        self._default_workspace_name = operation_scope.workspace_name
        self._all_operations = all_operations
        self._operation = service_client.managed_network_settings_rule
        self._credentials = credentials
        self._init_kwargs = kwargs

    def show(self, name: str, outbound_rule_name: str, **kwargs) -> OutboundRule:
        print("SDK outbound rule show method called")

        workspace_name = self._check_workspace_name(name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        obj = self._operation.get(resource_group, workspace_name, outbound_rule_name)
        return OutboundRule._from_rest_object(obj)

        # obj = self._operation.get(resource_group, workspace_name)
        # return Workspace._from_rest_object(obj)
        """def get(
        self,
        resource_group_name,  # type: str
        workspace_name,  # type: str
        **kwargs  # type: Any):"""

        raise NotImplementedError("workspace outbound rule operations show")

    def list(self, name: str, **kwargs) -> OutboundRule:

        print("SDK outbound rule list method called")
        raise NotImplementedError("workspace outbound rule operations list")
        # return OutboundRule()

    def set(self, name: str, outbound_rule_name: str, **kwargs) -> OutboundRule:

        print("SDK outbound rule set method called")
        raise NotImplementedError("workspace outbound rule operations set")
        # return OutboundRule()

    def remove(self, name: str, outbound_rule_name: str, **kwargs) -> OutboundRule:

        print("SDK outbound rule remove method called")
        raise NotImplementedError("workspace outbound rule operations remove")
        # return OutboundRule()

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
