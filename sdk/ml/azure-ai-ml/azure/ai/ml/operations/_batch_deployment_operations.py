# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import re
from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
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
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils.utils import (
    _get_mfe_base_url_from_discovery_service,
    modified_operation_client,
)
from azure.ai.ml._utils._package_utils import package_deployment
from azure.ai.ml.constants._common import ARM_ID_PREFIX, AzureMLResourceType, LROConfigurations
from azure.ai.ml.entities import BatchDeployment, BatchJob, PipelineComponent
from azure.ai.ml.entities._deployment.deployment import Deployment
from azure.ai.ml.entities._deployment.pipeline_component_batch_deployment import PipelineComponentBatchDeployment
from azure.core.credentials import TokenCredential
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class BatchDeploymentOperations(_ScopeDependentOperations):
    """BatchDeploymentOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client_05_2022: ServiceClient052022,
        all_operations: OperationsContainer,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        super(BatchDeploymentOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._batch_deployment = service_client_05_2022.batch_deployments
        self._batch_job_deployment = kwargs.pop("service_client_09_2020_dataplanepreview").batch_job_deployment
        service_client_02_2023_preview = kwargs.pop("service_client_02_2023_preview")
        self._component_batch_deployment_operations = service_client_02_2023_preview.batch_deployments
        self._batch_endpoint_operations = service_client_05_2022.batch_endpoints
        self._component_operations = service_client_02_2023_preview.component_versions
        self._all_operations = all_operations
        self._credentials = credentials
        self._init_kwargs = kwargs

        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline")

    @distributed_trace
    @monitor_with_activity(logger, "BatchDeployment.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(
        self,
        deployment: Union[BatchDeployment, PipelineComponentBatchDeployment],
        *,
        skip_script_validation: bool = False,
        **kwargs,
    ) -> LROPoller[BatchDeployment]:
        """Create or update a batch deployment.

        :param deployment: The deployment entity.
        :type deployment: ~azure.ai.ml.entities.BatchDeployment
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if BatchDeployment cannot be
            successfully validated. Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.AssetException: Raised if BatchDeployment assets
            (e.g. Data, Code, Model, Environment) cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.ModelException: Raised if BatchDeployment model
            cannot be successfully validated. Details will be provided in the error message.
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.BatchDeployment]
        """

        if (
            not skip_script_validation
            and deployment
            and deployment.code_configuration
            and not deployment.code_configuration.code.startswith(ARM_ID_PREFIX)
            and not re.match(AMLVersionedArmId.REGEX_PATTERN, deployment.code_configuration.code)
        ):
            validate_scoring_script(deployment)
        module_logger.debug("Checking endpoint %s exists", deployment.endpoint_name)
        self._batch_endpoint_operations.get(
            endpoint_name=deployment.endpoint_name,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
        )
        orchestrators = OperationOrchestrator(
            operation_container=self._all_operations,
            operation_scope=self._operation_scope,
            operation_config=self._operation_config,
        )
        upload_dependencies(deployment, orchestrators)
        if isinstance(deployment, PipelineComponentBatchDeployment):
            self._validate_component(deployment, orchestrators)
        try:
            location = self._get_workspace_location()
            if kwargs.pop("package_model", False):
                deployment = package_deployment(deployment, self._all_operations.all_operations)
                module_logger.info("\nStarting deployment")
            deployment_rest = deployment._to_rest_object(location=location)
            if isinstance(deployment, PipelineComponentBatchDeployment):  # pylint: disable=no-else-return
                return self._component_batch_deployment_operations.begin_create_or_update(
                    resource_group_name=self._resource_group_name,
                    workspace_name=self._workspace_name,
                    endpoint_name=deployment.endpoint_name,
                    deployment_name=deployment.name,
                    body=deployment_rest,
                    **self._init_kwargs,
                )
            else:
                return self._batch_deployment.begin_create_or_update(
                    resource_group_name=self._resource_group_name,
                    workspace_name=self._workspace_name,
                    endpoint_name=deployment.endpoint_name,
                    deployment_name=deployment.name,
                    body=deployment_rest,
                    **self._init_kwargs,
                    cls=lambda response, deserialized, headers: BatchDeployment._from_rest_object(deserialized),
                )
        except Exception as ex:
            raise ex

    @distributed_trace
    @monitor_with_activity(logger, "BatchDeployment.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, endpoint_name: str) -> BatchDeployment:
        """Get a deployment resource.

        :param name: The name of the deployment
        :type name: str
        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :return: A deployment entity
        :rtype: ~azure.ai.ml.entities.BatchDeployment
        """

        deployment = BatchDeployment._from_rest_object(
            self._batch_deployment.get(
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
    @monitor_with_activity(logger, "BatchDeployment.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, endpoint_name: str) -> LROPoller[None]:
        """Delete a batch deployment.

        :param name: Name of the batch deployment.
        :type name: str
        :param endpoint_name: Name of the batch endpoint
        :type endpoint_name: str
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        path_format_arguments = {
            "endpointName": name,
            "resourceGroupName": self._resource_group_name,
            "workspaceName": self._workspace_name,
        }

        delete_poller = self._batch_deployment.begin_delete(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=endpoint_name,
            deployment_name=name,
            polling=AzureMLPolling(
                LROConfigurations.POLL_INTERVAL,
                path_format_arguments=path_format_arguments,
                **self._init_kwargs,
            ),
            polling_interval=LROConfigurations.POLL_INTERVAL,
            **self._init_kwargs,
        )
        return delete_poller

    @distributed_trace
    @monitor_with_activity(logger, "BatchDeployment.List", ActivityType.PUBLICAPI)
    def list(self, endpoint_name: str) -> ItemPaged[BatchDeployment]:
        """List a deployment resource.

        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :return: An iterator of deployment entities
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.BatchDeployment]
        """
        return self._batch_deployment.list(
            endpoint_name=endpoint_name,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [BatchDeployment._from_rest_object(obj) for obj in objs],
            **self._init_kwargs,
        )

    @distributed_trace
    @monitor_with_activity(logger, "BatchDeployment.ListJobs", ActivityType.PUBLICAPI)
    def list_jobs(self, endpoint_name: str, *, name: Optional[str] = None) -> ItemPaged[BatchJob]:
        """List jobs under the provided batch endpoint deployment. This is only valid for batch endpoint.

        :param endpoint_name: Name of endpoint.
        :type endpoint_name: str
        :param name: (Optional) Name of deployment.
        :type name: str
        :raise: Exception if endpoint_type is not BATCH_ENDPOINT_TYPE
        :return: List of jobs
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.BatchJob]
        """

        workspace_operations = self._all_operations.all_operations[AzureMLResourceType.WORKSPACE]
        mfe_base_uri = _get_mfe_base_url_from_discovery_service(
            workspace_operations, self._workspace_name, self._requests_pipeline
        )

        with modified_operation_client(self._batch_job_deployment, mfe_base_uri):
            result = self._batch_job_deployment.list(
                endpoint_name=endpoint_name,
                deployment_name=name,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                **self._init_kwargs,
            )

            # This is necessary as the paged result need to be resolved inside the context manager
            return list(result)

    def _get_workspace_location(self) -> str:
        """Get the workspace location TODO[TASK 1260265]: can we cache this information and only refresh when the
        operation_scope is changed?"""
        return self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location

    def _validate_component(self, deployment: Deployment, orchestrators: OperationOrchestrator) -> None:
        """Validates that the value provided is associated to an existing component or otherwise we will try to create
        an anonymous component that will be use for batch deployment.

        :param deployment: Batch deployment
        :type deployment: ~azure.ai.ml.entities._deployment.deployment.Deployment
        :param orchestrators: Operation Orchestrator
        :type orchestrators: _operation_orchestrator.OperationOrchestrator
        """
        if isinstance(deployment.component, PipelineComponent):
            deployment.component = self._all_operations.all_operations[AzureMLResourceType.COMPONENT].create_or_update(
                name=deployment.component.name,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                component=deployment.component,
                version=deployment.component.version,
                **self._init_kwargs,
            )
        elif isinstance(deployment.component, str):
            component_id = orchestrators.get_asset_arm_id(
                deployment.component, azureml_type=AzureMLResourceType.COMPONENT
            )
            deployment.component = component_id
        elif isinstance(deployment.job_definition, str):
            job_component = PipelineComponent(source_job_id=deployment.job_definition)
            deployment.component = self._component_operations.create_or_update(
                name=job_component.name,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                body=job_component._to_rest_object(),
                version=job_component.version,
                **self._init_kwargs,
            )
