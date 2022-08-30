# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
import time
from typing import Any, Dict, Union

from azure.ai.ml._restclient.v2020_09_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient092020DataplanePreview,
)
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._utils._azureml_polling import AzureMLPolling
from azure.ai.ml._utils._endpoint_utils import polling_wait, upload_dependencies
from azure.ai.ml._utils.utils import _get_mfe_base_url_from_discovery_service, modified_operation_client
from azure.ai.ml.constants import AzureMLResourceType, LROConfigurations
from azure.ai.ml.entities import BatchDeployment
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.identity import ChainedTokenCredential

from ._operation_orchestrator import OperationOrchestrator

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class BatchDeploymentOperations(_ScopeDependentOperations):
    """BatchDeploymentOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client_05_2022: ServiceClient052022,
        service_client_09_2020_dataplanepreview: ServiceClient092020DataplanePreview,
        all_operations: OperationsContainer,
        credentials: ChainedTokenCredential = None,
        **kwargs: Dict,
    ):
        super(BatchDeploymentOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._batch_deployment = service_client_05_2022.batch_deployments
        self._batch_job_deployment = service_client_09_2020_dataplanepreview.batch_job_deployment
        self._batch_endpoint_operations = service_client_05_2022.batch_endpoints
        self._all_operations = all_operations
        self._credentials = credentials
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "BatchDeployment.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, deployment: BatchDeployment, **kwargs: Any) -> Union[BatchDeployment, LROPoller]:
        """Create or update a batch deployment.

        :param endpoint: The deployment entity.
        :type endpoint: BatchDeployment
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """

        no_wait = kwargs.get("no_wait", False)
        module_logger.debug("Checking endpoint %s exists", deployment.endpoint_name)
        self._batch_endpoint_operations.get(
            endpoint_name=deployment.endpoint_name,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
        )
        orchestrators = OperationOrchestrator(
            operation_container=self._all_operations,
            operation_scope=self._operation_scope,
        )
        upload_dependencies(deployment, orchestrators)

        try:
            location = self._get_workspace_location()
            deployment_rest = deployment._to_rest_object(location=location)

            poller = self._batch_deployment.begin_create_or_update(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=deployment.endpoint_name,
                deployment_name=deployment.name,
                body=deployment_rest,
                polling=not no_wait,
                **self._init_kwargs,
            )
            if no_wait:
                module_logger.info(
                    "Batch deployment create/update request initiated. "
                    "Status can be checked using "
                    "`az ml batch-deployment show -e %s -n %s`\n",
                    deployment.endpoint_name,
                    deployment.name,
                )
                return poller
            return BatchDeployment._from_rest_object(poller.result())

        except Exception as ex:
            raise ex

    @monitor_with_activity(logger, "BatchDeployment.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, endpoint_name: str) -> BatchDeployment:
        """Get a deployment resource.

        :param name: The name of the deployment
        :type name: str
        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :return: a deployment entity
        :rtype: BatchDeployment
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

    @monitor_with_activity(logger, "BatchDeployment.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, endpoint_name: str, **kwargs: Any) -> Union[None, LROPoller]:
        """Delete a batch deployment.

        :param name: Name of the batch endpoint.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: Optional[LROPoller]
        """
        start_time = time.time()
        path_format_arguments = {
            "endpointName": name,
            "resourceGroupName": self._resource_group_name,
            "workspaceName": self._workspace_name,
        }
        no_wait = kwargs.get("no_wait", False)

        delete_poller = self._batch_deployment.begin_delete(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=endpoint_name,
            deployment_name=name,
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
                "Delete request initiated. "
                "Status can be checked using "
                "`az ml batch-deployment show -e %s -n %s`\n",
                endpoint_name,
                name,
            )
            return delete_poller
        message = f"Deleting batch deployment {name} "
        polling_wait(poller=delete_poller, start_time=start_time, message=message)

    @monitor_with_activity(logger, "BatchDeployment.List", ActivityType.PUBLICAPI)
    def list(self, endpoint_name: str) -> ItemPaged[BatchDeployment]:
        """List a deployment resource.

        :param endpoint_name: The name of the endpoint
        :type endpoint_name: str
        :return: an iterator of deployment entities
        :rtype: Iterable[BatchDeployment]
        """
        return self._batch_deployment.list(
            endpoint_name=endpoint_name,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [BatchDeployment._from_rest_object(obj) for obj in objs],
            **self._init_kwargs,
        )

    @monitor_with_activity(logger, "BatchDeployment.ListJobs", ActivityType.PUBLICAPI)
    def list_jobs(self, endpoint_name: str, name: str = None):
        """List jobs under the provided batch endpoint deployment. This is only
        valid for batch endpoint.

        :param endpoint_name: Name of endpoint.
        :type endpoint_name: str
        :param name: Name of deployment.
        :type name: str
        :raise: Exception if endpoint_type is not BATCH_ENDPOINT_TYPE
        :return: Iterable[BatchJobResourceArmPaginatedResult]
        """

        workspace_operations = self._all_operations.all_operations[AzureMLResourceType.WORKSPACE]
        mfe_base_uri = _get_mfe_base_url_from_discovery_service(workspace_operations, self._workspace_name)

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
        """Get the workspace location TODO[TASK 1260265]: can we cache this
        information and only refresh when the operation_scope is changed?"""
        return self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location
