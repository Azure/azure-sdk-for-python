# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Dict

from azure.ai.ml._artifacts._artifact_utilities import _upload_and_generate_remote_uri
from azure.ai.ml._azure_environments import _get_aml_resource_id_from_metadata, _resource_to_scopes
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJobResource
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._schema._deployment.batch.batch_job import BatchJobSchema
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._arm_id_utils import get_datastore_arm_id, is_ARM_id_for_resource, remove_datastore_prefix
from azure.ai.ml._utils._azureml_polling import AzureMLPolling
from azure.ai.ml._utils._endpoint_utils import validate_response
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils.utils import _get_mfe_base_url_from_discovery_service, modified_operation_client
from azure.ai.ml.constants._common import (
    ARM_ID_FULL_PREFIX,
    BASE_PATH_CONTEXT_KEY,
    HTTP_PREFIX,
    LONG_URI_REGEX_FORMAT,
    PARAMS_OVERRIDE_KEY,
    SHORT_URI_REGEX_FORMAT,
    AssetTypes,
    AzureMLResourceType,
    LROConfigurations,
)
from azure.ai.ml.constants._endpoint import EndpointInvokeFields, EndpointYamlFields
from azure.ai.ml.entities import BatchEndpoint, BatchJob
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._operation_orchestrator import OperationOrchestrator

if TYPE_CHECKING:
    from azure.ai.ml.operations import DatastoreOperations

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class BatchEndpointOperations(_ScopeDependentOperations):
    """BatchEndpointOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client_05_2022: ServiceClient052022,
        all_operations: OperationsContainer,
        credentials: TokenCredential = None,
        **kwargs: Dict,
    ):

        super(BatchEndpointOperations, self).__init__(operation_scope, operation_config)
        # ops_logger.update_info(kwargs)
        self._batch_operation = service_client_05_2022.batch_endpoints
        self._batch_deployment_operation = service_client_05_2022.batch_deployments
        self._batch_job_endpoint = kwargs.pop("service_client_09_2020_dataplanepreview").batch_job_endpoint
        self._all_operations = all_operations
        self._credentials = credentials
        self._init_kwargs = kwargs

        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline")

    @property
    def _datastore_operations(self) -> "DatastoreOperations":
        return self._all_operations.all_operations[AzureMLResourceType.DATASTORE]

    @distributed_trace
    # @monitor_with_activity(logger, "BatchEndpoint.List", ActivityType.PUBLICAPI)
    def list(self) -> ItemPaged[BatchEndpoint]:
        """List endpoints of the workspace.

        :return: A list of endpoints
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.BatchEndpoint]
        """
        return self._batch_operation.list(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [BatchEndpoint._from_rest_object(obj) for obj in objs],
            **self._init_kwargs,
        )

    @distributed_trace
    # @monitor_with_activity(logger, "BatchEndpoint.Get", ActivityType.PUBLICAPI)
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

    @distributed_trace
    # @monitor_with_activity(logger, "BatchEndpoint.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str) -> LROPoller[None]:
        """Delete a batch Endpoint.

        :param name: Name of the batch endpoint.
        :type name: str
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        path_format_arguments = {
            "endpointName": name,
            "resourceGroupName": self._resource_group_name,
            "workspaceName": self._workspace_name,
        }

        delete_poller = self._batch_operation.begin_delete(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
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
    # @monitor_with_activity(logger, "BatchEndpoint.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, endpoint: BatchEndpoint) -> LROPoller[BatchEndpoint]:
        """Create or update a batch endpoint.

        :param endpoint: The endpoint entity.
        :type endpoint: ~azure.ai.ml.entities.BatchEndpoint
        :return: A poller to track the operation status.
        :rtype:  ~azure.core.polling.LROPoller[~azure.ai.ml.entities.BatchEndpoint]
        """

        try:
            location = self._get_workspace_location()

            endpoint_resource = endpoint._to_rest_batch_endpoint(location=location)
            poller = self._batch_operation.begin_create_or_update(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=endpoint.name,
                body=endpoint_resource,
                polling=True,
                **self._init_kwargs,
            )
            return poller

        except Exception as ex:
            raise ex

    @distributed_trace
    # @monitor_with_activity(logger, "BatchEndpoint.Invoke", ActivityType.PUBLICAPI)
    def invoke(
        self,
        endpoint_name: str,
        *,
        deployment_name: str = None,
        inputs: Dict[str, Input] = None,
        **kwargs,
    ) -> BatchJob:
        """Invokes the batch endpoint with the provided payload.

        :param endpoint_name: The endpoint name.
        :type endpoint_name: str
        :param deployment_name: The name of a specific deployment to invoke. This is optional.
            By default requests are routed to any of the deployments according to the traffic rules.
        :type deployment_name: Optional[str]
        :param inputs: (Optional) A dictionary of existing data asset, public uri file or folder
            to use with the deployment
        :type inputs: Dict[str, Input]
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if deployment cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.AssetException: Raised if BatchEndpoint assets
            (e.g. Data, Code, Model, Environment) cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.ModelException: Raised if BatchEndpoint model cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :return: The invoked batch deployment job.
        :rtype: BatchJob
        """
        params_override = kwargs.get("params_override", None) or []
        input = kwargs.get("input", None) # pylint: disable=redefined-builtin
        # Until this bug is resolved https://msdata.visualstudio.com/Vienna/_workitems/edit/1446538
        if deployment_name:
            self._validate_deployment_name(endpoint_name, deployment_name)

        if input and isinstance(input, Input):
            if HTTP_PREFIX not in input.path:
                self._resolve_input(input, os.getcwd())
            # MFE expects a dictionary as input_data that's why we are using
            # "UriFolder" or "UriFile" as keys depending on the input type
            if input.type == "uri_folder":
                params_override.append({EndpointYamlFields.BATCH_JOB_INPUT_DATA: {"UriFolder": input}})
            elif input.type == "uri_file":
                params_override.append({EndpointYamlFields.BATCH_JOB_INPUT_DATA: {"UriFile": input}})
        elif inputs:
            for key, input_data in inputs.items():
                if isinstance(input_data, Input) and HTTP_PREFIX not in input_data.path:
                    self._resolve_input(input_data, os.getcwd())
            params_override.append({EndpointYamlFields.BATCH_JOB_INPUT_DATA: inputs})
        else:
            msg = (
                "Unsupported input type please use a dictionary of either a path on the datastore, public URI, "
                "a registered data asset, or a local folder path."
            )
            raise ValidationException(
                message=msg,
                target=ErrorTarget.BATCH_ENDPOINT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        # Batch job doesn't have a python class, loading a rest object using params override
        context = {
            BASE_PATH_CONTEXT_KEY: Path(".").parent,
            PARAMS_OVERRIDE_KEY: params_override,
        }

        batch_job = BatchJobSchema(context=context).load(data={})  # pylint: disable=no-member
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
        ml_audience_scopes = _resource_to_scopes(_get_aml_resource_id_from_metadata())
        module_logger.debug("ml_audience_scopes used: `%s`\n", ml_audience_scopes)
        key = self._credentials.get_token(*ml_audience_scopes).token
        headers[EndpointInvokeFields.AUTHORIZATION] = f"Bearer {key}"

        if deployment_name:
            headers[EndpointInvokeFields.MODEL_DEPLOYMENT] = deployment_name

        response = self._requests_pipeline.post(
           endpoint.properties.scoring_uri,
           json=BatchJobResource(properties=batch_job).serialize(),
           headers=headers,
        )
        validate_response(response)
        batch_job = json.loads(response.text())
        return BatchJobResource.deserialize(batch_job)

    @distributed_trace
    # @monitor_with_activity(logger, "BatchEndpoint.ListJobs", ActivityType.PUBLICAPI)
    def list_jobs(self, endpoint_name: str) -> ItemPaged[BatchJob]:
        """List jobs under the provided batch endpoint deployment. This is only
        valid for batch endpoint.

        :param endpoint_name: The endpoint name
        :type endpoint_name: str
        :return: List of jobs
        :rtype: ItemPaged[BatchJob]
        """

        workspace_operations = self._all_operations.all_operations[AzureMLResourceType.WORKSPACE]
        mfe_base_uri = _get_mfe_base_url_from_discovery_service(
            workspace_operations, self._workspace_name, self._requests_pipeline
        )

        with modified_operation_client(self._batch_job_endpoint, mfe_base_uri):
            result = self._batch_job_endpoint.list(
                endpoint_name=endpoint_name,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                **self._init_kwargs,
            )

            # This is necessary as the paged result need to be resolved inside the context manager
            return list(result)

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
                if entry.type == AssetTypes.URI_FILE and not os.path.isfile(entry.path):
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
                # If we receive a datastore path in long/short form we don't need
                # to get the arm asset id
                if re.match(SHORT_URI_REGEX_FORMAT, entry.path) or re.match(LONG_URI_REGEX_FORMAT, entry.path):
                    return
                asset_type = AzureMLResourceType.DATASTORE
                entry.path = remove_datastore_prefix(entry.path)
                orchestrator = OperationOrchestrator(
                    self._all_operations, self._operation_scope, self._operation_config
                )
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
        except (MlException, HttpResponseError) as e:
            raise e
        except Exception as e:
            raise ValidationException(
                message=f"Supported input path value are: path on the datastore, public URI, "
                "a registered data asset, or a local folder path.\n"
                f"Met {type(e)}:\n{e}",
                target=ErrorTarget.BATCH_ENDPOINT,
                no_personal_data_message="Supported input path value are: path on the datastore, "
                "public URI, a registered data asset, or a local folder path.",
                error=e,
            )
