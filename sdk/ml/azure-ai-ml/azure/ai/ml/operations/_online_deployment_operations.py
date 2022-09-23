# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-self-use

import random
from typing import Dict, Optional

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._local_endpoints import LocalEndpointMode
from azure.ai.ml._local_endpoints.errors import InvalidVSCodeRequestError
from azure.ai.ml._restclient.v2022_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022022Preview
from azure.ai.ml._restclient.v2022_02_01_preview.models import DeploymentLogsRequest
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._azureml_polling import AzureMLPolling
from azure.ai.ml._utils._endpoint_utils import upload_dependencies
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.constants._common import AzureMLResourceType, LROConfigurations
from azure.ai.ml.constants._deployment import EndpointDeploymentLogContainerType
from azure.ai.ml.entities import OnlineDeployment
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._local_deployment_helper import _LocalDeploymentHelper
from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.logger, ops_logger.module_logger


class OnlineDeploymentOperations(_ScopeDependentOperations):
    """OnlineDeploymentOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client_02_2022_preview: ServiceClient022022Preview,
        all_operations: OperationsContainer,
        local_deployment_helper: _LocalDeploymentHelper,
        credentials: TokenCredential = None,
        **kwargs: Dict,
    ):
        super(OnlineDeploymentOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._local_deployment_helper = local_deployment_helper
        self._online_deployment = service_client_02_2022_preview.online_deployments
        self._online_endpoint_operations = service_client_02_2022_preview.online_endpoints
        self._all_operations = all_operations
        self._credentials = credentials
        self._init_kwargs = kwargs

    @distributed_trace
    @monitor_with_activity(logger, "OnlineDeployment.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(
        self,
        deployment: OnlineDeployment,
        *,
        local: bool = False,
        vscode_debug: bool = False,
    ) -> LROPoller[OnlineDeployment]:
        """Create or update a deployment.

        :param deployment: the deployment entity
        :type deployment: ~azure.ai.ml.entities.OnlineDeployment
        :param local: Whether deployment should be created locally, defaults to False
        :type local: bool, optional
        :param vscode_debug: Whether to open VSCode instance to debug local deployment, defaults to False
        :type vscode_debug: bool, optional
        :return: A poller to track the operation status
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.OnlineDeployment]
        """
        try:
            if vscode_debug and not local:
                raise InvalidVSCodeRequestError(
                    msg="VSCode Debug is only support for local endpoints. Please set local to True."
                )
            if local:
                return self._local_deployment_helper.create_or_update(
                    deployment=deployment,
                    local_endpoint_mode=self._get_local_endpoint_mode(vscode_debug),
                )

            path_format_arguments = {
                "endpointName": deployment.name,
                "resourceGroupName": self._resource_group_name,
                "workspaceName": self._workspace_name,
            }

            # This get() is to ensure, the endpoint exists and fail before even start the deployment
            module_logger.info("Check: endpoint %s exists", deployment.endpoint_name)
            self._online_endpoint_operations.get(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=deployment.endpoint_name,
            )
            orchestrators = OperationOrchestrator(
                operation_container=self._all_operations,
                operation_scope=self._operation_scope,
                operation_config=self._operation_config,
            )

            upload_dependencies(deployment, orchestrators)
            try:
                location = self._get_workspace_location()
                deployment_rest = deployment._to_rest_object(location=location)

                poller = self._online_deployment.begin_create_or_update(
                    resource_group_name=self._resource_group_name,
                    workspace_name=self._workspace_name,
                    endpoint_name=deployment.endpoint_name,
                    deployment_name=deployment.name,
                    body=deployment_rest,
                    polling=AzureMLPolling(
                        LROConfigurations.POLL_INTERVAL,
                        path_format_arguments=path_format_arguments,
                        **self._init_kwargs,
                    ),
                    polling_interval=LROConfigurations.POLL_INTERVAL,
                    **self._init_kwargs,
                    cls=lambda response, deserialized, headers: OnlineDeployment._from_rest_object(deserialized),
                )
                return poller
            except Exception as ex:
                raise ex
        except Exception as ex:  # pylint: disable=broad-except
            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            else:
                raise ex

    @distributed_trace
    @monitor_with_activity(logger, "OnlineDeployment.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, endpoint_name: str, *, local: bool = False) -> OnlineDeployment:
        """Get a deployment resource.

        :param name: The name of the deployment
        :type name: str
        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :param local: Whether deployment should be retrieved from local docker environment, defaults to False
        :type local: bool, optional
        :return: a deployment entity
        :rtype: ~azure.ai.ml.entities.OnlineDeployment
        """
        if local:
            deployment = self._local_deployment_helper.get(endpoint_name=endpoint_name, deployment_name=name)
        else:
            deployment = OnlineDeployment._from_rest_object(
                self._online_deployment.get(
                    endpoint_name=endpoint_name,
                    deployment_name=name,
                    resource_group_name=self._resource_group_name,
                    workspace_name=self._workspace_name,
                    **self._init_kwargs,
                )
            )

        deployment.endpoint_name = endpoint_name
        return deployment

    @distributed_trace
    @monitor_with_activity(logger, "OnlineDeployment.Delete", ActivityType.PUBLICAPI)
    def delete(self, name: str, endpoint_name: str, *, local: bool = False) -> LROPoller[None]:
        """Delete a deployment.

        :param name: The name of the deployment
        :type name: str
        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :param local: Whether deployment should be retrieved from local docker environment, defaults to False
        :type local: bool, optional
        :return: A poller to track the operation status
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        if local:
            return self._local_deployment_helper.delete(name=endpoint_name, deployment_name=name)
        return self._online_deployment.begin_delete(
            endpoint_name=endpoint_name,
            deployment_name=name,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            **self._init_kwargs,
        )

    @distributed_trace
    @monitor_with_activity(logger, "OnlineDeployment.GetLogs", ActivityType.PUBLICAPI)
    def get_logs(
        self,
        name: str,
        endpoint_name: str,
        lines: int,
        *,
        container_type: Optional[str] = None,
        local: bool = False,
    ) -> str:
        """Retrive the logs from online deployment.

        :param name: The name of the deployment
        :type name: str
        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :param lines: The maximum number of lines to tail
        :type lines: int
        :param container_type: The type of container to retrieve logs from. Possible values include:
            "StorageInitializer", "InferenceServer", defaults to None
        :type container_type: Optional[str], optional
        :param local: [description], defaults to False
        :type local: bool, optional
        :return: the logs
        :rtype: str
        """
        if local:
            return self._local_deployment_helper.get_deployment_logs(
                endpoint_name=endpoint_name, deployment_name=name, lines=lines
            )
        if container_type:
            container_type = self._validate_deployment_log_container_type(container_type)
        log_request = DeploymentLogsRequest(container_type=container_type, tail=lines)
        return self._online_deployment.get_logs(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=endpoint_name,
            deployment_name=name,
            body=log_request,
            **self._init_kwargs,
        ).content

    @distributed_trace
    @monitor_with_activity(logger, "OnlineDeployment.List", ActivityType.PUBLICAPI)
    def list(self, endpoint_name: str, *, local: bool = False) -> ItemPaged[OnlineDeployment]:
        """List a deployment resource.

        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :param local: Whether deployment should be retrieved from local docker environment, defaults to False
        :type local: bool, optional
        :return: an iterator of deployment entities
        :rtype: Iterable[~azure.ai.ml.entities.OnlineDeployment]
        """
        if local:
            return self._local_deployment_helper.list()
        return self._online_deployment.list(
            endpoint_name=endpoint_name,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [OnlineDeployment._from_rest_object(obj) for obj in objs],
            **self._init_kwargs,
        )

    def _validate_deployment_log_container_type(self, container_type):
        if container_type == EndpointDeploymentLogContainerType.INFERENCE_SERVER:
            return EndpointDeploymentLogContainerType.INFERENCE_SERVER_REST

        if container_type == EndpointDeploymentLogContainerType.STORAGE_INITIALIZER:
            return EndpointDeploymentLogContainerType.STORAGE_INITIALIZER_REST

        msg = "Invalid container type '{}'. Supported container types are {} and {}"
        msg = msg.format(
            container_type,
            EndpointDeploymentLogContainerType.INFERENCE_SERVER,
            EndpointDeploymentLogContainerType.STORAGE_INITIALIZER,
        )
        raise ValidationException(
            message=msg,
            target=ErrorTarget.ONLINE_DEPLOYMENT,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )

    def _get_ARM_deployment_name(self, name: str):
        random.seed(version=2)
        return f"{self._workspace_name}-{name}-{random.randint(1, 10000000)}"

    def _get_workspace_location(self) -> str:
        """Get the workspace location TODO[TASK 1260265]: can we cache this
        information and only refresh when the operation_scope is changed?"""
        return self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location

    def _get_local_endpoint_mode(self, vscode_debug):
        return LocalEndpointMode.VSCodeDevContainer if vscode_debug else LocalEndpointMode.DetachedContainer
