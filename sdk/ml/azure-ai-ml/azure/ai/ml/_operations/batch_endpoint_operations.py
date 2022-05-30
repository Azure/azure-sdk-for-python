# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, Iterable, Union, TYPE_CHECKING
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
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml._utils._endpoint_utils import polling_wait, post_and_validate_response
from azure.ai.ml._utils._arm_id_utils import (
    generate_data_arm_id,
    get_datastore_arm_id,
    is_ARM_id_for_resource,
    parse_name_version,
    remove_datastore_prefix,
)
from azure.ai.ml._utils.utils import (
    _get_mfe_base_url_from_discovery_service,
    modified_operation_client,
)
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope, _ScopeDependentOperations
from azure.ai.ml.constants import (
    AssetTypes,
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    AzureMLResourceType,
    EndpointInvokeFields,
    EndpointYamlFields,
    HTTP_PREFIX,
    LROConfigurations,
    ARM_ID_FULL_PREFIX,
)
from azure.ai.ml.entities import BatchEndpoint
from azure.ai.ml._utils._azureml_polling import AzureMLPolling

from .operation_orchestrator import OperationOrchestrator

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget
from azure.ai.ml._artifacts._artifact_utilities import _upload_and_generate_remote_uri

if TYPE_CHECKING:
    from azure.ai.ml._operations import DatastoreOperations

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

    @property
    def _datastore_operations(self) -> "DatastoreOperations":
        return self._all_operations.all_operations[AzureMLResourceType.DATASTORE]

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
        input: Input = None,
        params_override=None,
        **kwargs,
    ) -> BatchJobResource:
        """Invokes the batch endpoint with the provided payload

        :param str endpoint_name: the endpoint name
        :param (str, optional) deployment_name: Name of a specific deployment to invoke. This is optional. By default requests are routed to any of the deployments according to the traffic rules.
        :param (Input, optional) input: To use a existing data asset, public uri file, or folder pass in a Input object, for batch endpoints only.
        :param (List, optional) params_override: Used to overwrite deployment configurations, for batch endpoints only.
        Returns:
            Union[str, BatchJobResource]: Prediction output for online endpoints or details of batch prediction job.
        """
        params_override = params_override or []
        # Until this bug is resolved https://msdata.visualstudio.com/Vienna/_workitems/edit/1446538
        if deployment_name:
            self._validate_deployment_name(endpoint_name, deployment_name)

        if isinstance(input, Input):
            if HTTP_PREFIX not in input.path:
                self._resolve_input(input, os.getcwd())
            # MFE expects a dictionary as input_data that's why we are using "input_data" as key before parsing it to JobInput
            params_override.append({EndpointYamlFields.BATCH_JOB_INPUT_DATA: {"input_data": input}})
        else:
            msg = "Unsupported input please use either a path on the datastore, public URI, a registered data asset, or a local folder path."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.BATCH_ENDPOINT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

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

    def _resolve_input(self, entry: Input, base_path: str) -> None:
        # We should not verify anything that is not of type Input
        if not isinstance(entry, Input):
            return

        # Input path should not be empty
        if not entry.path:
            raise Exception("Input path can't be empty for batch endpoint invoke")

        try:
            if entry.path.startswith(ARM_ID_FULL_PREFIX):
                if not is_ARM_id_for_resource(entry.path, AzureMLResourceType.DATA):
                    raise ValidationException(
                        message="Invalid input path",
                        target=ErrorTarget.BATCH_ENDPOINT,
                        no_personal_data_message="Invalid input path",
                    )
            elif os.path.isabs(entry.path):  # absolute local path, upload, transform to remote url
                if entry.type == AssetTypes.URI_FOLDER and not os.path.isdir(entry.path):
                    raise ValidationException(
                        message="There is no folder on target path: {}".format(entry.path),
                        target=ErrorTarget.BATCH_ENDPOINT,
                        no_personal_data_message="There is no folder on target path",
                    )
                elif entry.type == AssetTypes.URI_FILE and not os.path.isfile(entry.path):
                    raise ValidationException(
                        message="There is no file on target path: {}".format(entry.path),
                        target=ErrorTarget.BATCH_ENDPOINT,
                        no_personal_data_message="There is no file on target path",
                    )
                # absolute local path
                entry.path = _upload_and_generate_remote_uri(
                    self._operation_scope,
                    self._datastore_operations,
                    entry.path,
                )
                if entry.type == AssetTypes.URI_FOLDER and entry.path and not entry.path.endswith("/"):
                    entry.path = entry.path + "/"
            elif ":" in entry.path or "@" in entry.path:  # Check registered file or folder datastore
                asset_type = AzureMLResourceType.DATASTORE
                entry.path = remove_datastore_prefix(entry.path)
                orchestrator = OperationOrchestrator(self._all_operations, self._operation_scope)
                entry.path = orchestrator.get_asset_arm_id(entry.path, asset_type)
            else:  # relative local path, upload, transform to remote url
                local_path = Path(base_path, entry.path).resolve()
                entry.path = _upload_and_generate_remote_uri(
                    self._operation_scope,
                    self._datastore_operations,
                    local_path,
                )
                if entry.type == AssetTypes.URI_FOLDER and entry.path and not entry.path.endswith("/"):
                    entry.path = entry.path + "/"
        except Exception as e:
            raise ValidationException(
                message=f"Supported input path value are: path on the datastore, public URI, a registered data asset, or a local folder path.\n"
                f"Met {type(e)}:\n{e}",
                target=ErrorTarget.BATCH_ENDPOINT,
                no_personal_data_message="Supported input path value are: path on the datastore, public URI, a registered data asset, or a local folder path.",
                error=e,
            )
