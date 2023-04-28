# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-self-use,broad-except

import random
import re
from typing import Dict, Optional

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._local_endpoints import LocalEndpointMode
from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._restclient.v2022_02_01_preview.models import DeploymentLogsRequest
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId

from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._azureml_polling import AzureMLPolling
from azure.ai.ml._utils._endpoint_utils import upload_dependencies, validate_scoring_script
from azure.ai.ml._utils._package_utils import package_deployment
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.constants._common import ARM_ID_PREFIX, AzureMLResourceType, LROConfigurations
from azure.ai.ml.constants._deployment import EndpointDeploymentLogContainerType, SmallSKUs, DEFAULT_MDC_PATH
from azure.ai.ml.entities import OnlineDeployment, Data
from azure.ai.ml.exceptions import (
    ErrorCategory,
    ErrorTarget,
    InvalidVSCodeRequestError,
    ValidationErrorType,
    ValidationException,
)
from azure.core.credentials import TokenCredential
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._local_deployment_helper import _LocalDeploymentHelper
from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class OnlineDeploymentOperations(_ScopeDependentOperations):
    """OnlineDeploymentOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client_04_2023_preview: ServiceClient042023Preview,
        all_operations: OperationsContainer,
        local_deployment_helper: _LocalDeploymentHelper,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        super(OnlineDeploymentOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._local_deployment_helper = local_deployment_helper
        self._online_deployment = service_client_04_2023_preview.online_deployments
        self._online_endpoint_operations = service_client_04_2023_preview.online_endpoints
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
        skip_script_validation: bool = False,
        **kwargs,
    ) -> LROPoller[OnlineDeployment]:
        """Create or update a deployment.

        :param deployment: the deployment entity
        :type deployment: ~azure.ai.ml.entities.OnlineDeployment
        :param local: Whether deployment should be created locally, defaults to False
        :type local: bool, optional
        :param vscode_debug: Whether to open VSCode instance to debug local deployment, defaults to False
        :type vscode_debug: bool, optional
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if OnlineDeployment cannot
            be successfully validated. Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.AssetException: Raised if OnlineDeployment assets
            (e.g. Data, Code, Model, Environment) cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.ModelException: Raised if OnlineDeployment model cannot be
            successfully validated. Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.DeploymentException: Raised if OnlineDeployment type is unsupported.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.LocalEndpointNotFoundError: Raised if local endpoint resource does not exist.
        :raises ~azure.ai.ml.exceptions.LocalEndpointInFailedStateError: Raised if local endpoint is in a failed state.
        :raises ~azure.ai.ml.exceptions.InvalidLocalEndpointError: Raised if Docker image cannot be
            found for local deployment.
        :raises ~azure.ai.ml.exceptions.LocalEndpointImageBuildError: Raised if Docker image cannot be
            successfully built for local deployment.
        :raises ~azure.ai.ml.exceptions.RequiredLocalArtifactsNotFoundError: Raised if local artifacts cannot be
            found for local deployment.
        :raises ~azure.ai.ml.exceptions.InvalidVSCodeRequestError: Raised if VS Debug is invoked with a remote endpoint.
            VSCode debug is only supported for local endpoints.
        :raises ~azure.ai.ml.exceptions.VSCodeCommandNotFound: Raised if VSCode instance cannot be instantiated.
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
            if deployment and deployment.instance_type and deployment.instance_type.lower() in SmallSKUs:
                module_logger.warning(
                    "Instance type %s may be too small for compute resources. "  # pylint: disable=line-too-long
                    "Minimum recommended compute SKU is Standard_DS3_v2 for general purpose endpoints. Learn more about SKUs here: "  # pylint: disable=line-too-long
                    "https://learn.microsoft.com/en-us/azure/machine-learning/referencemanaged-online-endpoints-vm-sku-list",
                    deployment.instance_type,  # pylint: disable=line-too-long
                )
            if (
                not skip_script_validation
                and deployment
                and deployment.code_configuration
                and not deployment.code_configuration.code.startswith(ARM_ID_PREFIX)
                and not re.match(AMLVersionedArmId.REGEX_PATTERN, deployment.code_configuration.code)
            ):
                validate_scoring_script(deployment)

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
            if deployment.data_collector:
                self._register_collection_data_assets(deployment=deployment)

            upload_dependencies(deployment, orchestrators)
            try:
                location = self._get_workspace_location()
                if kwargs.pop("package_model", False):
                    deployment = package_deployment(deployment, self._all_operations.all_operations)
                    module_logger.info("\nStarting deployment")

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
    def get(self, name: str, endpoint_name: str, *, local: Optional[bool] = False) -> OnlineDeployment:
        """Get a deployment resource.

        :param name: The name of the deployment
        :type name: str
        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :param local: Whether deployment should be retrieved from local docker environment, defaults to False
        :type local: Optional[bool]
        :raises ~azure.ai.ml.exceptions.LocalEndpointNotFoundError: Raised if local endpoint resource does not exist.
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
    def begin_delete(self, name: str, endpoint_name: str, *, local: Optional[bool] = False) -> LROPoller[None]:
        """Delete a deployment.

        :param name: The name of the deployment
        :type name: str
        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :param local: Whether deployment should be retrieved from local docker environment, defaults to False
        :type local: Optional[bool]
        :raises ~azure.ai.ml.exceptions.LocalEndpointNotFoundError: Raised if local endpoint resource does not exist.
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
        """Get the workspace location TODO[TASK 1260265]: can we cache this information and only refresh when the
        operation_scope is changed?"""
        return self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location

    def _get_local_endpoint_mode(self, vscode_debug):
        return LocalEndpointMode.VSCodeDevContainer if vscode_debug else LocalEndpointMode.DetachedContainer

    def _register_collection_data_assets(self, deployment: OnlineDeployment) -> None:
        for name, value in deployment.data_collector.collections.items():
            data_name = f"{deployment.endpoint_name}-{deployment.name}-{name}"
            data_version = "1"
            data_path = f"{DEFAULT_MDC_PATH}/{deployment.endpoint_name}/{deployment.name}/{name}"
            if value.data:
                if value.data.name:
                    data_name = value.data.name

                if value.data.version:
                    data_version = value.data.version

                if value.data.path:
                    data_path = value.data.path

            data_object = Data(
                name=data_name,
                version=data_version,
                path=data_path,
            )

            try:
                result = self._all_operations._all_operations[AzureMLResourceType.DATA].create_or_update(data_object)
            except Exception as e:
                if "already exists" in str(e):
                    result = self._all_operations._all_operations[AzureMLResourceType.DATA].get(data_name, data_version)
                else:
                    raise e
            deployment.data_collector.collections[name].data = (
                f"/subscriptions/{self._subscription_id}/resourceGroups/{self._resource_group_name}"
                f"/providers/Microsoft.MachineLearningServices/workspaces/{self._workspace_name}"
                f"/data/{result.name}/versions/{result.version}"
            )
