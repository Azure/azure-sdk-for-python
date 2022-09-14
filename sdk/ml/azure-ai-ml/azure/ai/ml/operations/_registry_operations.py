# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict

# TODO - what is this service_client and is this the right type?
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._restclient.v2022_10_01_preview.models import Registry as RestRegistry
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities import Registry
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.logger, ops_logger.module_logger


# Largely placeholder to allow for mocks until implemented in successor tasks
class RegistryOperations:
    """RegistryOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient052022,
        all_operations: OperationsContainer,
        credentials: TokenCredential = None,
        **kwargs: Dict,
    ):
        ops_logger.update_info(kwargs)
        # TODO check needed variables - these are initially copied from workspace operations.
        self._subscription_id = operation_scope.subscription_id
        self._resource_group_name = operation_scope.resource_group_name
        self._default_workspace_name = operation_scope.workspace_name
        self._all_operations = all_operations
        self._operation = service_client.workspaces
        self._credentials = credentials
        self._init_kwargs = kwargs
        self.containerRegistry = "none"

    @monitor_with_activity(logger, "Registry.BeginCreate", ActivityType.PUBLICAPI)
    def begin_create_or_update(
        self,
        registry: Registry,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[RestRegistry]:
        raise NotImplementedError("Placeholder until implemented in subsequent task.")
