# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Optional, List

from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope, _ScopeDependentOperations, OperationConfig
from azure.ai.ml._restclient.v2024_10_01_preview import AzureMachineLearningWorkspaces as ServiceClient102024Preview
from azure.ai.ml.entities._workspace.workspace import Workspace
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._workspace._ai_workspaces.capability_host import CapabilityHost
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml.constants._common import WorkspaceKind
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml.constants._workspace import CapabilityHostKind
from marshmallow.exceptions import ValidationError as SchemaValidationError
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class CapabilityHostsOperations(_ScopeDependentOperations):
    """CapabilityHostsOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client_10_2024: ServiceClient102024Preview,
        all_operations: OperationsContainer,
        credentials: TokenCredential,
        **kwargs: Any,
    ):
        super(CapabilityHostsOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._all_operations = all_operations
        self._capability_hosts_operations = service_client_10_2024.capability_hosts
        self._workspace_operations = service_client_10_2024.workspaces
        self._credentials = credentials
        self._init_kwargs = kwargs

    @monitor_with_activity(ops_logger, "CapabilityHost.Get", ActivityType.PUBLICAPI)
    @distributed_trace
    def get(self, name: str, **kwargs: Any) -> CapabilityHost:
        """Retrieve a capability host resource from the specified Azure Machine Learning workspace.

        :param name: The name of the capability host to retrieve.
        :type name: str
        :param workspace_name: The name of hub or project workspace.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: Any
        :return: A CapabilityHost object representing the retrieved capability host resource.
        :rtype: ~azure.ai.ml.entities.CapabilityHost
        """

        self.__validate_workspace_name()

        self.__validate_capability_host_name(name)

        rest_obj=self._capability_hosts_operations.get(
                resource_group_name = self._resource_group_name, 
                workspace_name = self._workspace_name, 
                name = name,  
                **kwargs)
        
        capability_host = CapabilityHost._from_rest_object(rest_obj)
        
        return capability_host

    @monitor_with_activity(ops_logger, "CapabilityHost.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    @distributed_trace
    def create_or_update(
            self,
            capability_host: CapabilityHost
    ) -> LROPoller[CapabilityHost]:
        """Begin the creation or update of a capability host in a Hub or Project workspace.

        :param capability_host: The CapabilityHost object containing the details of the capability host to create or update.
        :type capability_host: ~azure.ai.ml.entities.CapabilityHost
        :return: An LROPoller object that can be used to track the long-running operation that is creation of capability host.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.CapabilityHost]
        """

        self.__validate_workspace_name()
        
        workspace = self.__get_workspace()

        self._init_kwargs.pop('cloud', None)
        self._init_kwargs.pop('credential_scopes', None)

        if workspace is None:
            msg = f"Workspace '{self._workspace_name}' does not exist."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.CAPABILITY_HOST,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        
        workspace_kind = WorkspaceKind.PROJECT
        if workspace._hub_id is None: 
            workspace_kind = WorkspaceKind.HUB

        self.__validate_properties(capability_host, workspace_kind)
        
        if workspace_kind == WorkspaceKind.HUB:
            capability_host.ai_services_connections = []
            capability_host.storage_connections = []
            capability_host.vector_store_connections = []
        elif workspace_kind == WorkspaceKind.PROJECT:
            if capability_host.storage_connections is None or len(capability_host.storage_connections) == 0:
                capability_host.storage_connections = self.__get_default_storage_connections()
        
        try:

            capability_host_resource = capability_host._to_rest_object()
            poller = self._capability_hosts_operations.begin_create_or_update(
                resource_group_name = self._resource_group_name,
                workspace_name = self._workspace_name,
                name = capability_host.name,
                body = capability_host_resource,
                polling=True,
                **self._init_kwargs,
                cls=lambda response, deserialized, headers: CapabilityHost._from_rest_object(deserialized)
            )
            return poller
    
        except Exception as ex:
            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            raise ex
        
    def __validate_capability_host_name(self, capability_host_name: Optional[str]) -> None:
        """Validates that a capability host name exists.

        :param capability_host_name: Name for a capability host resource.
        :type capability_host_name: str
        """
        if not capability_host_name:
            msg = "Please provide capability host name"
            raise ValidationException(
                message = msg,
                target = ErrorTarget.CAPABILITY_HOST,
                no_personal_data_message = msg,
                error_category = ErrorCategory.USER_ERROR,
            )
    
    def __get_default_storage_connections(self) -> List[str]:
        """Retrieve the default storage connections for a capability host.

        :return: A list of default storage connections.
        :rtype: List[str]
        """
        return [f"{self._workspace_name}/workspaceblobstore"]
        
    def __validate_properties(self, capability_host: CapabilityHost, workspace_kind: str) -> None:
        """Validate the properties of the capability host based on the workspace kind.

        :param capability_host: The capability host to validate.
        :type capability_host: CapabilityHost
        :param kind: The kind of the workspace, either hub or project only.
        :type kind: str
        """
        
        if not self.__is_valid_kind(workspace_kind):
            msg = f"Invalid workspace kind: {workspace_kind}. Workspace kind should be either 'Hub' or 'Project'."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.CAPABILITY_HOST,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        if workspace_kind == WorkspaceKind.PROJECT:
            if capability_host.ai_services_connections is None or capability_host.vector_store_connections is None:
                msg = (
                    "For Project workspace kind, AI services connections and vector store connections are required."
                )
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.CAPABILITY_HOST,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                )
            
    def __is_valid_kind(self, kind: str):
        """Validate if the provided kind is a valid WorkspaceKind.

        :param kind: The kind of workspace to validate, eiher hub or project only.
        :type kind: str
        :return: True if the kind is valid, False otherwise.
        :rtype: bool
        """
        
        return kind in {WorkspaceKind.HUB, WorkspaceKind.PROJECT}
    
    def __get_workspace(self) -> Optional[Workspace]:
        """Retrieve the workspace object.

        :return: The current workspace if it exists, otherwise None.
        :rtype: Optional[~azure.ai.ml.entities._workspace.workspace.Workspace]
        """
        rest_workspace = self._workspace_operations.get(self._resource_group_name, self._workspace_name)
        workspace = Workspace._from_rest_object(rest_workspace)
        return workspace
    
    def __validate_workspace_name(self) -> None:
        """Validates that a workspace name set in MLClient.

        :param name: Name for a workspace resource.
        :type name: str
        :return: No Return.
        :rtype: None
        :raises ~azure.ai.ml.ValidationException: Raised if MLClient does not have workspace name set.
        """
        workspace_name = self._workspace_name
        if not workspace_name:
            msg = "Please set workspace name in MLClient."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.CAPABILITY_HOST,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
