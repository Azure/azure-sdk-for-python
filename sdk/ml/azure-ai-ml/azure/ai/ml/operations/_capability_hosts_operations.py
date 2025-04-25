# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

from typing import Any, List

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2024_10_01_preview import AzureMachineLearningWorkspaces as ServiceClient102024Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.constants._common import DEFAULT_STORAGE_CONNECTION_NAME, WorkspaceKind
from azure.ai.ml.entities._workspace._ai_workspaces.capability_host import CapabilityHost
from azure.ai.ml.entities._workspace.workspace import Workspace
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class CapabilityHostsOperations(_ScopeDependentOperations):
    """CapabilityHostsOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.

    :param operation_scope: Scope variables for the operations classes of an MLClient object.
    :type operation_scope: ~azure.ai.ml._scope_dependent_operations.OperationScope
    :param operation_config: Common configuration for operations classes of an MLClient object.
    :type operation_config: ~azure.ai.ml._scope_dependent_operations.OperationConfig
    :param service_client_10_2024: Service client to allow end users to operate on Azure Machine Learning Workspace
        resources (ServiceClient102024Preview).
    :type service_client_10_2024: ~azure.ai.ml._restclient.v2024_10_01_preview._azure_machine_learning_workspaces.AzureMachineLearningWorkspaces    # pylint: disable=line-too-long
    :param all_operations: All operations classes of an MLClient object.
    :type all_operations: ~azure.ai.ml._scope_dependent_operations.OperationsContainer
    :param credentials: Credential to use for authentication.
    :type credentials: ~azure.core.credentials.TokenCredential
    :param kwargs: Additional keyword arguments.
    :type kwargs: Any
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
        """Constructor of CapabilityHostsOperations class.

        :param operation_scope: Scope variables for the operations classes of an MLClient object.
        :type operation_scope: ~azure.ai.ml._scope_dependent_operations.OperationScope
        :param operation_config: Common configuration for operations classes of an MLClient object.
        :type operation_config: ~azure.ai.ml._scope_dependent_operations.OperationConfig
        :param service_client_10_2024: Service client to allow end users to operate on Azure Machine Learning Workspace
            resources (ServiceClient102024Preview).
        :type service_client_10_2024: ~azure.ai.ml._restclient.v2024_10_01_preview._azure_machine_learning_workspaces.AzureMachineLearningWorkspaces    # pylint: disable=line-too-long
        :param all_operations: All operations classes of an MLClient object.
        :type all_operations: ~azure.ai.ml._scope_dependent_operations.OperationsContainer
        :param credentials: Credential to use for authentication.
        :type credentials: ~azure.core.credentials.TokenCredential
        :param kwargs: Additional keyword arguments.
        :type kwargs: Any
        """

        super(CapabilityHostsOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_filter()
        self._all_operations = all_operations
        self._capability_hosts_operations = service_client_10_2024.capability_hosts
        self._workspace_operations = service_client_10_2024.workspaces
        self._credentials = credentials
        self._init_kwargs = kwargs

    @experimental
    @monitor_with_activity(ops_logger, "CapabilityHost.Get", ActivityType.PUBLICAPI)
    @distributed_trace
    def get(self, name: str, **kwargs: Any) -> CapabilityHost:
        """Retrieve a capability host resource.

        :param name: The name of the capability host to retrieve.
        :type name: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if project name or hub name
            not provided while creation of MLClient object in workspacename param.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Capabilityhost name is not provided.
            Details will be provided in the error message.
        :return: CapabilityHost object.
        :rtype: ~azure.ai.ml.entities._workspace._ai_workspaces.capability_host.CapabilityHost

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_capability_host.py
                :start-after: [START capability_host_get_operation]
                :end-before: [END capability_host_get_operation]
                :language: python
                :dedent: 8
                :caption: Get example.
        """

        self._validate_workspace_name()

        rest_obj = self._capability_hosts_operations.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            **kwargs,
        )

        capability_host = CapabilityHost._from_rest_object(rest_obj)

        return capability_host

    @experimental
    @monitor_with_activity(ops_logger, "CapabilityHost.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_create_or_update(self, capability_host: CapabilityHost, **kwargs: Any) -> LROPoller[CapabilityHost]:
        """Begin the creation of a capability host in a Hub or Project workspace.
        Note that currently this method can only accept the `create` operation request
        and not `update` operation request.

        :param capability_host: The CapabilityHost object containing the details of the capability host to create.
        :type capability_host: ~azure.ai.ml.entities.CapabilityHost
        :return: An LROPoller object that can be used to track the long-running
            operation that is creation of capability host.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities._workspace._ai_workspaces.capability_host.CapabilityHost]    # pylint: disable=line-too-long

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_capability_host.py
                :start-after: [START capability_host_begin_create_or_update_operation]
                :end-before: [END capability_host_begin_create_or_update_operation]
                :language: python
                :dedent: 8
                :caption: Create example.
        """
        try:
            self._validate_workspace_name()

            workspace = self._get_workspace()

            self._validate_workspace_kind(workspace._kind)

            self._validate_properties(capability_host, workspace._kind)

            if workspace._kind == WorkspaceKind.PROJECT:
                if capability_host.storage_connections is None or len(capability_host.storage_connections) == 0:
                    capability_host.storage_connections = self._get_default_storage_connections()

            capability_host_resource = capability_host._to_rest_object()

            poller = self._capability_hosts_operations.begin_create_or_update(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=capability_host.name,
                body=capability_host_resource,
                polling=True,
                **kwargs,
                cls=lambda response, deserialized, headers: CapabilityHost._from_rest_object(deserialized),
            )
            return poller

        except Exception as ex:
            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            raise ex

    @experimental
    @distributed_trace
    @monitor_with_activity(ops_logger, "CapabilityHost.Delete", ActivityType.PUBLICAPI)
    def begin_delete(
        self,
        name: str,
        **kwargs: Any,
    ) -> LROPoller[None]:
        """Delete capability host.

        :param name: capability host name.
        :type name: str
        :return: A poller for deletion status
        :rtype: ~azure.core.polling.LROPoller[None]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_capability_host.py
                :start-after: [START capability_host_delete_operation]
                :end-before: [END capability_host_delete_operation]
                :language: python
                :dedent: 8
                :caption: Delete example.
        """
        poller = self._capability_hosts_operations.begin_delete(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            polling=True,
            **kwargs,
        )
        return poller

    def _get_default_storage_connections(self) -> List[str]:
        """Retrieve the default storage connections for a capability host.

        :return: A list of default storage connections.
        :rtype: List[str]
        """
        return [f"{self._workspace_name}/{DEFAULT_STORAGE_CONNECTION_NAME}"]

    def _validate_workspace_kind(self, workspace_kind: str) -> None:
        """Validate the workspace kind, it should be either hub or project only.

        :param workspace_kind: The kind of the workspace, either hub or project only.
        :type workspace_kind: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if workspace kind is not Hub or Project.
            Details will be provided in the error message.
        :return: None, or the result of cls(response)
        :rtype: None
        """

        valid_kind = workspace_kind in {WorkspaceKind.HUB, WorkspaceKind.PROJECT}
        if not valid_kind:
            msg = f"Invalid workspace kind: {workspace_kind}. Workspace kind should be either 'Hub' or 'Project'."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.CAPABILITY_HOST,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

    def _validate_properties(self, capability_host: CapabilityHost, workspace_kind: str) -> None:
        """Validate the properties of the capability host for project workspace.

        :param capability_host: The capability host to validate.
        :type capability_host: CapabilityHost
        :param workspace_kind: The kind of the workspace, Project only.
        :type workspace_kind: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the
            OpenAI service connection is empty for a Project workspace kind.
            Details will be provided in the error message.
        :return: None, or the result of cls(response)
        :rtype: None
        """

        if workspace_kind == WorkspaceKind.PROJECT:
            if capability_host.ai_services_connections is None:
                msg = "For Project workspace kind, OpenAI service connections are required."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.CAPABILITY_HOST,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                )

    def _get_workspace(self) -> Workspace:
        """Retrieve the workspace object.

        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if specified Hub or Project do not exist.
            Details will be provided in the error message.
        :return: Hub or Project object if it exists
        :rtype: ~azure.ai.ml.entities._workspace.workspace.Workspace
        """
        rest_workspace = self._workspace_operations.get(self._resource_group_name, self._workspace_name)
        workspace = Workspace._from_rest_object(rest_workspace)
        if workspace is None:
            msg = f"Workspace with name {self._workspace_name} does not exist."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.CAPABILITY_HOST,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return workspace

    def _validate_workspace_name(self) -> None:
        """Validates that a hub name or project name is set in the MLClient's workspace name parameter.

        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if project name or hub name
            not provided while creation of
            MLClient object in workspacename param. Details will be provided in the error message.
        :return: None, or the result of cls(response)
        :rtype: None
        """
        workspace_name = self._workspace_name
        if not workspace_name:
            msg = "Please pass either a hub name or project name to the workspace_name parameter when initializing an MLClient object."  # pylint: disable=line-too-long
            raise ValidationException(
                message=msg,
                target=ErrorTarget.CAPABILITY_HOST,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
