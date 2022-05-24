# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, Iterable, Union
from azure.ai.ml._azure_environments import ENDPOINT_URLS, _get_cloud_details, resource_to_scopes
from azure.core.polling import LROPoller
from azure.identity import ChainedTokenCredential
from azure.ai.ml._restclient.v2022_05_01 import (
    AzureMachineLearningWorkspaces as ServiceClient052022,
)
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient092020DataplanePreview,
)
from azure.ai.ml._restclient.v2022_05_01.models import (
    BatchEndpointTrackedResourceArmPaginatedResult,
)
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJobResource
from azure.ai.ml._schema._deployment.batch.batch_job import BatchJobSchema
from azure.ai.ml.entities._assets import Dataset
from azure.ai.ml.entities import BatchDeployment
from azure.ai.ml._utils._endpoint_utils import polling_wait, post_and_validate_response
from azure.ai.ml._utils._arm_id_utils import (
    generate_data_arm_id,
    get_datastore_arm_id,
    is_ARM_id_for_resource,
    parse_name_version,
)
from azure.ai.ml._utils.utils import (
    _get_mfe_base_url_from_discovery_service,
    modified_operation_client,
)
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope, _ScopeDependentOperations
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    AzureMLResourceType,
    EndpointInvokeFields,
    EndpointYamlFields,
    LROConfigurations,
)
from azure.ai.ml.entities import BatchEndpoint
from azure.ai.ml._utils._azureml_polling import AzureMLPolling

from .operation_orchestrator import OperationOrchestrator

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class BatchEndpointOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client_05_2022: ServiceClient052022,
        service_client_09_2020_dataplanepreview: ServiceClient092020DataplanePreview,
        all_operations: OperationsContainer,
        credentials: ChainedTokenCredential = None,
        **kwargs: Dict,
    ):

        super(BatchEndpointOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._batch_operation = service_client_05_2022.batch_endpoints
        self._batch_deployment_operation = service_client_05_2022.batch_deployments
        self._batch_job_endpoint = service_client_09_2020_dataplanepreview.batch_job_endpoint
        self._all_operations = all_operations
        self._credentials = credentials
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "BatchEndpoint.List", ActivityType.PUBLICAPI)
    def list(
        self,
    ) -> Iterable[BatchEndpointTrackedResourceArmPaginatedResult]:
        """List endpoints of the workspace.

        :return: a list of endpoints
        """
        return self._batch_operation.list(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [BatchEndpoint._from_rest_object(obj) for obj in objs],
            **self._init_kwargs,
        )

    @monitor_with_activity(logger, "BatchEndpoint.Get", ActivityType.PUBLICAPI)
    def get(
        self,
        name: str,
    ) -> BatchEndpoint:
        """Get a Endpoint resource.

        :param str name: Name of the endpoint.
        :return: Endpoint object retrieved from the service.
        :rtype: BatchEndpoint
        """
        # first get the endpoint
        endpoint = self._batch_operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            **self._init_kwargs,
        )

        endpoint_data = BatchEndpoint._from_rest_object(endpoint)
        return endpoint_data

    @monitor_with_activity(logger, "BatchEndpoint.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str = None, **kwargs: Any) -> Union[None, LROPoller]:
        """Delete a batch Endpoint.

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

        delete_poller = self._batch_operation.begin_delete(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
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
                f"Delete request initiated. Status can be checked using `az ml batch-endpoint show {name}`\n"
            )
            return delete_poller
        else:
            message = f"Deleting batch endpoint {name} "
            polling_wait(poller=delete_poller, start_time=start_time, message=message)

    @monitor_with_activity(logger, "BatchEndpoint.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, endpoint: BatchEndpoint, **kwargs: Any) -> Union[BatchEndpoint, LROPoller]:
        """Create or update a batch endpoint

        :param endpoint: The endpoint entity.
        :type endpoint: Endpoint
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """

        no_wait = kwargs.get("no_wait", False)
        try:
            location = self._get_workspace_location()

            endpoint_resource = endpoint._to_rest_batch_endpoint(location=location)
            poller = self._batch_operation.begin_create_or_update(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=endpoint.name,
                body=endpoint_resource,
                polling=not no_wait,
                **self._init_kwargs,
            )
            if no_wait:
                module_logger.info(
                    f"Batch endpoint create/update request initiated. Status can be checked using `az ml batch-endpoint show -n {endpoint.name}`\n"
                )
                return poller
            else:
                return BatchEndpoint._from_rest_object(poller.result())

        except Exception as ex:
            raise ex

    @monitor_with_activity(logger, "BatchEndpoint.Invoke", ActivityType.PUBLICAPI)
    def invoke(
        self,
        endpoint_name: str,
        deployment_name: str = None,
        input_data: Union[str, Dataset] = None,
        params_override=None,
        **kwargs,
    ) -> BatchJobResource:
        """Invokes the batch endpoint with the provided payload

        :param str endpoint_name: the endpoint name
        :param (str, optional) deployment_name: Name of a specific deployment to invoke. This is optional. By default requests are routed to any of the deployments according to the traffic rules.
        :param (Union[str, Dataset], optional) input_data: To use a pre-registered dataset asset, pass str in format "<dataset-name>:<dataset-version>". To use a new dataset asset, pass in a Dataset object, for batch endpoints only.
        :param (List, optional) params_override: Used to overwrite deployment configurations, for batch endpoints only.
        Returns:
            Union[str, BatchJobResource]: Prediction output for online endpoints or details of batch prediction job.
        """
        params_override = params_override or []
        # Until this bug is resolved https://msdata.visualstudio.com/Vienna/_workitems/edit/1446538
        if deployment_name:
            self._validate_deployment_name(endpoint_name, deployment_name)

        if isinstance(input_data, str):
            name, version = parse_name_version(input_data)
            if name and version:
                input_data_id = generate_data_arm_id(self._operation_scope, name, version)
            else:
                msg = 'Input data needs to be in format "azureml:<data-name>:<data-version>" or "<data-name>:<data-version>"'
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.BATCH_ENDPOINT,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                )
        elif isinstance(input_data, Dataset):
            dataset_operations = self._all_operations.all_operations.get(AzureMLResourceType.DATASET)

            # Since data was defined inline and it will be created, it will be registered as anonymous
            input_data._is_anonymous = True
            input_data_id = dataset_operations.create_or_update(input_data).id
        else:
            msg = "Unsupported input data, please use either a string to reference a pre-registered data asset or a data object."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.BATCH_ENDPOINT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        params_override.append({EndpointYamlFields.BATCH_JOB_DATASET: input_data_id})

        # Batch job doesn't have a python class, loading a rest object using params override
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent, PARAMS_OVERRIDE_KEY: params_override}

        batch_job = BatchJobSchema(context=context).load(data={})
        # update output datastore to arm id if needed
        # TODO: Unify datastore name -> arm id logic, TASK: 1104172
        if (
            batch_job.output_dataset
            and batch_job.output_dataset.datastore_id
            and (not is_ARM_id_for_resource(batch_job.output_dataset.datastore_id))
        ):
            batch_job.output_dataset.datastore_id = get_datastore_arm_id(
                batch_job.output_dataset.datastore_id, self._operation_scope
            )

        endpoint = self._batch_operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=endpoint_name,
            **self._init_kwargs,
        )

        headers = EndpointInvokeFields.DEFAULT_HEADER
        cloud_details = _get_cloud_details()
        ml_audience_scopes = resource_to_scopes(cloud_details.get(ENDPOINT_URLS.AML_RESOURCE_ID))
        module_logger.debug(f"ml_audience_scopes used: `{ml_audience_scopes}`\n")
        key = self._credentials.get_token(*ml_audience_scopes).token
        headers[EndpointInvokeFields.AUTHORIZATION] = f"Bearer {key}"

        if deployment_name:
            headers[EndpointInvokeFields.MODEL_DEPLOYMENT] = deployment_name

        response = post_and_validate_response(
            url=endpoint.properties.scoring_uri,
            json=BatchJobResource(properties=batch_job).serialize(),
            headers=headers,
            **kwargs,
        )
        batch_job = json.loads(response.text)
        return BatchJobResource.deserialize(batch_job)

    @monitor_with_activity(logger, "BatchEndpoint.ListJobs", ActivityType.PUBLICAPI)
    def list_jobs(self, endpoint_name: str):
        """List jobs under the provided batch endpoint deployment. This is only valid for batch endpoint.


        :param str endpoint_name: the endpoint name
        :return: Iterable[BatchJobResourceArmPaginatedResult]
        """

        workspace_operations = self._all_operations.all_operations[AzureMLResourceType.WORKSPACE]
        mfe_base_uri = _get_mfe_base_url_from_discovery_service(workspace_operations, self._workspace_name)

        with modified_operation_client(self._batch_job_endpoint, mfe_base_uri):
            result = self._batch_job_endpoint.list(
                endpoint_name=endpoint_name,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                **self._init_kwargs,
            )

            # This is necessary as the paged result need to be resolved inside the context manager
            return list(result)

    def _load_code_configuration(self, register_asset: bool, endpoint: BatchEndpoint):
        OperationOrchestrator(operation_container=self._all_operations, operation_scope=self._operation_scope)

    def _get_workspace_location(self) -> str:
        return self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location

    def _validate_deployment_name(self, endpoint_name, deployment_name):
        deployments_list = self._batch_deployment_operation.list(
            endpoint_name=endpoint_name,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [obj.name for obj in objs],
            **self._init_kwargs,
        )
        if deployments_list:
            if deployment_name not in deployments_list:
                msg = f"Deployment name {deployment_name} not found for this endpoint"
                raise ValidationException(
                    message=msg.format(deployment_name),
                    no_personal_data_message=msg.format("[deployment_name]"),
                    target=ErrorTarget.DEPLOYMENT,
                    error_category=ErrorCategory.USER_ERROR,
                )
        else:
            msg = "No deployment exists for this endpoint"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.DEPLOYMENT,
            )
