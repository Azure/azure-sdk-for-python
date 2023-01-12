# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Iterable, Tuple

from azure.ai.ml._arm_deployments import ArmDeploymentExecutor
from azure.ai.ml._arm_deployments.arm_helper import get_template
from azure.ai.ml._restclient.v2022_10_01_preview import AzureMachineLearningWorkspaces as ServiceClient102022Preview
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
from azure.ai.ml.entities._workspace.networking import ManagedNetwork
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller, PollingMethod
from azure.core.tracing.decorator import distributed_trace

class WorkspaceOutboundRuleOperations:
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient102022Preview,
        all_operations: OperationsContainer,
        credentials: TokenCredential = None,
        **kwargs: Dict,
    ):
        self._subscription_id = operation_scope.subscription_id
        self._resource_group_name = operation_scope.resource_group_name
        self._default_workspace_name = operation_scope.workspace_name
        self._all_operations = all_operations
        # operations for workspaces from ServiceClient102022Preview, need managednetwork api instead
        self._operation = service_client.workspaces
        self._credentials = credentials
        self._init_kwargs = kwargs

    def show(
        self,
        name: str,
        outbound_rule_name: str,
        **kwargs) -> ManagedNetwork:

        print("SDK show method called")
        return ManagedNetwork()
        """obj = self._operation.get(
            workspace_name=self._workspace_name,
            outbound_rule_name=outbound_rule_name,
            **self._scope_kwargs,
            **kwargs,
        )
        return ManagedNetwork._from_rest_object(rest_obj=obj)"""


    def list(
        self,
        name: str,
        **kwargs) -> ManagedNetwork:
        
        print("SDK list method called")
        return ManagedNetwork()

    def set(
        self,
        name: str,
        outbound_rule_name: str,
        **kwargs) -> ManagedNetwork:
        
        print("SDK set method called")
        return ManagedNetwork()

    def remove(
        self,
        name: str,
        outbound_rule_name: str,
        **kwargs) -> ManagedNetwork:
        
        print("SDK remove method called")
        return ManagedNetwork()
