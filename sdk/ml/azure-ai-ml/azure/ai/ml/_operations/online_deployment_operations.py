# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import random
import time
from typing import Dict, Optional

from azure.identity import ChainedTokenCredential
from azure.core.paging import ItemPaged

from azure.ai.ml._restclient.v2022_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022022Preview
from azure.ai.ml._restclient.v2022_02_01_preview.models import DeploymentLogsRequest
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope, _ScopeDependentOperations
from azure.ai.ml._local_endpoints import LocalEndpointMode
from azure.ai.ml._local_endpoints.errors import InvalidVSCodeRequestError
from azure.ai.ml.constants import AzureMLResourceType, EndpointDeploymentLogContainerType, LROConfigurations
from azure.ai.ml.entities import OnlineDeployment

from ._local_deployment_helper import _LocalDeploymentHelper
from .operation_orchestrator import OperationOrchestrator
from azure.ai.ml._utils._azureml_polling import AzureMLPolling
from azure.ai.ml._utils._endpoint_utils import polling_wait, upload_dependencies

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class OnlineDeploymentOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client_02_2022_preview: ServiceClient022022Preview,
        all_operations: OperationsContainer,
        local_deployment_helper: _LocalDeploymentHelper,
        credentials: ChainedTokenCredential = None,
        **kwargs: Dict,
    ):
        super(OnlineDeploymentOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._local_deployment_helper = local_deployment_helper
        self._online_deployment = service_client_02_2022_preview.online_deployments
        self._online_endpoint_operations = service_client_02_2022_preview.online_endpoints
        self._all_operations = all_operations
        self._credentials = credentials
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "OnlineDeployment.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(
        self,
        deployment: OnlineDeployment,
        *,
        local: bool = False,
        vscode_debug: bool = False,
        no_wait: bool = False,
    ) -> None:
        """Create or update a deployment

        :param deployment: the deployment entity
        :type deployment: OnlineDeployment
        :param local: Whether deployment should be created locally, defaults to False
        :type local: bool, optional
        :param vscode_debug: Whether to open VSCode instance to debug local deployment, defaults to False
        :type vscode_debug: bool, optional
        :param no_wait: Applied only to online deployment, defaults to False
        :type no_wait: bool, optional
        :return: None
        :rtype: None | OnlineDeployment
        """
        if vscode_debug and not local:
            raise InvalidVSCodeRequestError(
                msg="VSCode Debug is only support for local endpoints. Please set local to True."
            )
        if local:
            return self._local_deployment_helper.create_or_update(
                deployment=deployment, local_endpoint_mode=self._get_local_endpoint_mode(vscode_debug)
            )

        start_time = time.time()
        path_format_arguments = {
            "endpointName": deployment.name,
            "resourceGroupName": self._resource_group_name,
            "workspaceName": self._workspace_name,
        }

        # This get() is to ensure, the endpoint exists and fail before even start the deployment
        module_logger.info(f"Check: endpoint {deployment.endpoint_name} exists")
        self._online_endpoint_operations.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=deployment.endpoint_name,
        )
        orchestrators = OperationOrchestrator(
            operation_container=self._all_operations, operation_scope=self._operation_scope
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
                )
                if not no_wait
                else False,
                polling_interval=LROConfigurations.POLL_INTERVAL,
                **self._init_kwargs,
            )
            if no_wait:
                module_logger.info(
                    f"Online deployment create/update request initiated. Status can be checked using `az ml online-deployment show -e {deployment.endpoint_name} -n {deployment.name}`\n"
                )
                return poller
            else:
                message = f"Creating/updating online deployment {deployment.name} "
                polling_wait(poller=poller, start_time=start_time, message=message, timeout=None)

        except Exception as ex:
            raise ex

    @monitor_with_activity(logger, "OnlineDeployment.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, endpoint_name: str, local: bool = False) -> OnlineDeployment:
        """Get a deployment resource

        :param name: The name of the deployment
        :type name: str
        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :param local: Whether deployment should be retrieved from local docker environment, defaults to False
        :type local: bool, optional
        :return: a deployment entity
        :rtype: OnlineDeployment
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

    @monitor_with_activity(logger, "OnlineDeployment.Delete", ActivityType.PUBLICAPI)
    def delete(self, name: str, endpoint_name: str, local: bool = False) -> None:
        """Delete a deployment

        :param name: The name of the deployment
        :type name: str
        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :param local: Whether deployment should be retrieved from local docker environment, defaults to False
        :type local: bool, optional
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

    @monitor_with_activity(logger, "OnlineDeployment.GetLogs", ActivityType.PUBLICAPI)
    def get_logs(
        self, name: str, endpoint_name: str, lines: int, container_type: Optional[str] = None, local: bool = False
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

    @monitor_with_activity(logger, "OnlineDeployment.List", ActivityType.PUBLICAPI)
    def list(self, endpoint_name: str, local: bool = False) -> ItemPaged[OnlineDeployment]:
        """List a deployment resource

        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :param local: Whether deployment should be retrieved from local docker environment, defaults to False
        :type local: bool, optional
        :return: an iterator of deployment entities
        :rtype: Iterable[OnlineDeployment]
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

        msg = f"Invalid container type '{container_type}'. Supported container types are {EndpointDeploymentLogContainerType.INFERENCE_SERVER} and {EndpointDeploymentLogContainerType.STORAGE_INITIALIZER}."
        raise ValidationException(
            message=msg,
            target=ErrorTarget.ONLINE_DEPLOYMENT,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
        )

    def _get_ARM_deployment_name(self, name: str):
        random.seed(version=2)
        return f"{self._workspace_name}-{name}-{random.randint(1, 10000000)}"

    def _get_workspace_location(self) -> str:
        """Get the workspace location
        TODO[TASK 1260265]: can we cache this information and only refresh when the operation_scope is changed?
        """
        return self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location

    def _get_local_endpoint_mode(self, vscode_debug):
        return LocalEndpointMode.VSCodeDevContainer if vscode_debug else LocalEndpointMode.DetachedContainer
