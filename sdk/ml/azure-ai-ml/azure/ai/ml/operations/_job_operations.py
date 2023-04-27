# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access, too-many-instance-attributes, too-many-statements, too-many-lines
import json
import os.path
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Optional, Union

import jwt
from azure.ai.ml._artifacts._artifact_utilities import (
    _upload_and_generate_remote_uri,
    aml_datastore_path_exists,
    download_artifact_from_aml_uri,
)
from azure.ai.ml._azure_environments import (
    _get_aml_resource_id_from_metadata,
    _get_base_url_from_metadata,
    _resource_to_scopes,
)
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.dataset_dataplane import AzureMachineLearningWorkspaces as ServiceClientDatasetDataplane
from azure.ai.ml._restclient.model_dataplane import AzureMachineLearningWorkspaces as ServiceClientModelDataplane
from azure.ai.ml._restclient.runhistory import AzureMachineLearningWorkspaces as ServiceClientRunHistory
from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient022023Preview
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobBase
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobType as RestJobType
from azure.ai.ml._restclient.v2023_04_01_preview.models import ListViewType, UserIdentity
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils.utils import (
    create_requests_pipeline_with_retry,
    download_text_from_url,
    is_data_binding_expression,
    is_private_preview_enabled,
    is_url,
)
from azure.ai.ml.constants._common import (
    API_URL_KEY,
    AZUREML_RESOURCE_PROVIDER,
    BATCH_JOB_CHILD_RUN_OUTPUT_NAME,
    COMMON_RUNTIME_ENV_VAR,
    DEFAULT_ARTIFACT_STORE_OUTPUT_NAME,
    GIT_PATH_PREFIX,
    LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT,
    LOCAL_COMPUTE_TARGET,
    SERVERLESS_COMPUTE,
    SHORT_URI_FORMAT,
    SWEEP_JOB_BEST_CHILD_RUN_ID_PROPERTY_NAME,
    TID_FMT,
    AssetTypes,
    AzureMLResourceType,
)
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.constants._job.pipeline import PipelineConstants
from azure.ai.ml.entities import Compute, Job, PipelineJob, ServiceInstance, ValidationResult
from azure.ai.ml.entities._assets._artifacts.code import Code
from azure.ai.ml.entities._builders import BaseNode, Command, Spark
from azure.ai.ml.entities._datastore._constants import WORKSPACE_BLOB_STORE
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.base_job import _BaseJob
from azure.ai.ml.entities._job.import_job import ImportJob
from azure.ai.ml.entities._job.job import _is_pipeline_child_job
from azure.ai.ml.entities._job.parallel.parallel_job import ParallelJob
from azure.ai.ml.entities._job.to_rest_functions import to_rest_job_object
from azure.ai.ml.entities._validation import SchemaValidatableMixin
from azure.ai.ml.exceptions import (
    ComponentException,
    ErrorCategory,
    ErrorTarget,
    JobException,
    JobParsingError,
    MlException,
    PipelineChildJobError,
    UserErrorException,
    ValidationErrorType,
    ValidationException,
)
from azure.ai.ml.operations._run_history_constants import RunHistoryConstants
from azure.ai.ml.sweep import SweepJob
from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from .._utils._experimental import experimental
from ..constants._component import ComponentSource
from ..entities._builders.control_flow_node import ControlFlowNode
from ..entities._job.pipeline._io import InputOutputBase, PipelineInput, _GroupAttrDict
from ._component_operations import ComponentOperations
from ._compute_operations import ComputeOperations
from ._dataset_dataplane_operations import DatasetDataplaneOperations
from ._job_ops_helper import get_git_properties, get_job_output_uris_from_dataplane, stream_logs_until_completion
from ._local_job_invoker import is_local_run, start_run_if_local
from ._model_dataplane_operations import ModelDataplaneOperations
from ._operation_orchestrator import (
    OperationOrchestrator,
    is_ARM_id_for_resource,
    is_registry_id_for_resource,
    is_singularity_full_name_for_resource,
    is_singularity_id_for_resource,
    is_singularity_short_name_for_resource,
)
from ._run_operations import RunOperations
from ._virtual_cluster_operations import VirtualClusterOperations

try:
    pass
except ImportError:
    pass

if TYPE_CHECKING:
    from azure.ai.ml.operations import DatastoreOperations

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class JobOperations(_ScopeDependentOperations):
    """JobOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client_02_2023_preview: ServiceClient022023Preview,
        all_operations: OperationsContainer,
        credential: TokenCredential,
        **kwargs: Any,
    ):
        super(JobOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._operation_2023_02_preview = service_client_02_2023_preview.jobs
        self._service_client = service_client_02_2023_preview
        self._all_operations = all_operations
        self._stream_logs_until_completion = stream_logs_until_completion
        # Dataplane service clients are lazily created as they are needed
        self._runs_operations_client = None
        self._dataset_dataplane_operations_client = None
        self._model_dataplane_operations_client = None
        # Kwargs to propagate to dataplane service clients
        self._service_client_kwargs = kwargs.pop("_service_client_kwargs", {})
        self._api_base_url = None
        self._container = "azureml"
        self._credential = credential
        self._orchestrators = OperationOrchestrator(self._all_operations, self._operation_scope, self._operation_config)

        self._kwargs = kwargs

        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline")

    @property
    def _component_operations(self) -> ComponentOperations:
        return self._all_operations.get_operation(
            AzureMLResourceType.COMPONENT, lambda x: isinstance(x, ComponentOperations)
        )

    @property
    def _compute_operations(self) -> ComputeOperations:
        return self._all_operations.get_operation(
            AzureMLResourceType.COMPUTE, lambda x: isinstance(x, ComputeOperations)
        )

    @property
    def _virtual_cluster_operations(self) -> VirtualClusterOperations:
        return self._all_operations.get_operation(
            AzureMLResourceType.VIRTUALCLUSTER, lambda x: isinstance(x, VirtualClusterOperations)
        )

    @property
    def _datastore_operations(self) -> "DatastoreOperations":
        return self._all_operations.all_operations[AzureMLResourceType.DATASTORE]

    @property
    def _runs_operations(self) -> RunOperations:
        if not self._runs_operations_client:
            service_client_run_history = ServiceClientRunHistory(
                self._credential, base_url=self._api_url, **self._service_client_kwargs
            )
            self._runs_operations_client = RunOperations(
                self._operation_scope, self._operation_config, service_client_run_history
            )
        return self._runs_operations_client

    @property
    def _dataset_dataplane_operations(self) -> DatasetDataplaneOperations:
        if not self._dataset_dataplane_operations_client:
            service_client_dataset_dataplane = ServiceClientDatasetDataplane(
                self._credential, base_url=self._api_url, **self._service_client_kwargs
            )
            self._dataset_dataplane_operations_client = DatasetDataplaneOperations(
                self._operation_scope,
                self._operation_config,
                service_client_dataset_dataplane,
            )
        return self._dataset_dataplane_operations_client

    @property
    def _model_dataplane_operations(self) -> ModelDataplaneOperations:
        if not self._model_dataplane_operations_client:
            service_client_model_dataplane = ServiceClientModelDataplane(
                self._credential, base_url=self._api_url, **self._service_client_kwargs
            )
            self._model_dataplane_operations_client = ModelDataplaneOperations(
                self._operation_scope,
                self._operation_config,
                service_client_model_dataplane,
            )
        return self._model_dataplane_operations_client

    @property
    def _api_url(self):
        if not self._api_base_url:
            self._api_base_url = self._get_workspace_url(url_key=API_URL_KEY)
        return self._api_base_url

    @distributed_trace
    @monitor_with_activity(logger, "Job.List", ActivityType.PUBLICAPI)
    def list(
        self,
        *,
        parent_job_name: Optional[str] = None,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
        **kwargs,
    ) -> Iterable[Job]:
        """List jobs of the workspace.

        :param parent_job_name: When provided, returns children of named job.
        :type parent_job_name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived jobs. Default: ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :return: An iterator like instance of Job objects.
        :rtype: ~azure.core.paging.ItemPaged[Job]
        """

        schedule_defined = kwargs.pop("schedule_defined", None)
        scheduled_job_name = kwargs.pop("scheduled_job_name", None)

        if parent_job_name:
            parent_job = self.get(parent_job_name)
            return self._runs_operations.get_run_children(parent_job.name)

        return self._operation_2023_02_preview.list(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            cls=lambda objs: [self._handle_rest_errors(obj) for obj in objs],
            list_view_type=list_view_type,
            scheduled=schedule_defined,
            schedule_id=scheduled_job_name,
            **self._kwargs,
            **kwargs,
        )

    def _handle_rest_errors(self, job_object):
        """Handle errors while resolving azureml_id's during list operation."""
        try:
            return self._resolve_azureml_id(Job._from_rest_object(job_object))
        except JobParsingError:
            pass

    @distributed_trace
    @monitor_with_telemetry_mixin(logger, "Job.Get", ActivityType.PUBLICAPI)
    def get(self, name: str) -> Job:
        """Get a job resource.

        :param str name: Name of the job.
        :return: Job object retrieved from the service.
        :rtype: Job
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """
        if not isinstance(name, str):
            raise UserErrorException(f"{name} is a invalid input for client.jobs.get().")
        job_object = self._get_job(name)

        if not _is_pipeline_child_job(job_object):
            job = Job._from_rest_object(job_object)
            if job_object.properties.job_type != RestJobType.AUTO_ML:
                # resolvers do not work with the old contract, leave the ids as is
                job = self._resolve_azureml_id(job)
        else:
            # Child jobs are no longer available through MFE, fetch
            # through run history instead
            job = self._runs_operations._translate_from_rest_object(self._runs_operations.get_run(name))

        return job

    @distributed_trace
    @monitor_with_telemetry_mixin(logger, "Job.ShowServices", ActivityType.PUBLICAPI)
    def show_services(self, name: str, node_index: int = 0) -> Dict[str, ServiceInstance]:
        """Get services associated with a job's node.

        :param str name: Name of the job.
        :param int node_index: Index of the node.
        :return: The Services associated with the job for the given node.
        :rtype: Dict[str, ServiceInstance] Map of service names to ServiceInstance.
        """

        service_instances_dict = self._runs_operations._operation.get_run_service_instances(
            self._subscription_id, self._operation_scope.resource_group_name, self._workspace_name, name, node_index
        )
        if not service_instances_dict.instances:
            return None

        return {
            k: ServiceInstance._from_rest_object(v, node_index) for k, v in service_instances_dict.instances.items()
        }

    @distributed_trace
    @monitor_with_activity(logger, "Job.Cancel", ActivityType.PUBLICAPI)
    def begin_cancel(self, name: str, **kwargs) -> LROPoller[None]:
        """Cancel job resource.

        :param str name: Name of the job.
        :return: None, or the result of cls(response)
        :rtype: None
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """
        tag = kwargs.pop("tag", None)

        if not tag:
            return self._operation_2023_02_preview.begin_cancel(
                id=name,
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                **self._kwargs,
                **kwargs,
            )

        # Note: Below batch cancel is experimental and for private usage
        results = []
        jobs = self.list(tag=tag)
        # TODO: Do we need to show error message when no jobs is returned for the given tag?
        for job in jobs:
            result = self._operation_2023_02_preview.begin_cancel(
                id=job.name,
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                **self._kwargs,
            )
            results.append(result)
        return results

    def _try_get_compute_arm_id(self, compute: Union[Compute, str]):
        # pylint: disable=too-many-return-statements
        # TODO: Remove in PuP with native import job/component type support in MFE/Designer
        # DataFactory 'clusterless' job
        if str(compute) == ComputeType.ADF:
            return compute

        if compute is not None:
            # Singularity
            if isinstance(compute, str) and is_singularity_id_for_resource(compute):
                return self._virtual_cluster_operations.get(compute)["id"]
            if isinstance(compute, str) and is_singularity_full_name_for_resource(compute):
                return self._orchestrators._get_singularity_arm_id_from_full_name(compute)
            if isinstance(compute, str) and is_singularity_short_name_for_resource(compute):
                return self._orchestrators._get_singularity_arm_id_from_short_name(compute)
            # other compute
            if is_ARM_id_for_resource(compute, resource_type=AzureMLResourceType.COMPUTE):
                # compute is not a sub-workspace resource
                compute_name = compute.split("/")[-1]
            elif isinstance(compute, Compute):
                compute_name = compute.name
            elif isinstance(compute, str):
                compute_name = compute
            elif isinstance(compute, PipelineInput):
                compute_name = str(compute)
            else:
                raise ValueError(
                    "compute must be either an arm id of Compute, a Compute object or a compute name but got {}".format(
                        type(compute)
                    )
                )

            if is_data_binding_expression(compute_name):
                return compute_name
            if compute_name == SERVERLESS_COMPUTE:
                return compute_name
            try:
                return self._compute_operations.get(compute_name).id
            except ResourceNotFoundError as e:
                # the original error is not helpful (Operation returned an invalid status 'Not Found'),
                # so we raise a more helpful one
                response = e.response
                response.reason = "Not found compute with name {}".format(compute_name)
                raise ResourceNotFoundError(response=response)
        return None

    @distributed_trace
    @experimental
    @monitor_with_telemetry_mixin(logger, "Job.Validate", ActivityType.PUBLICAPI)
    def validate(self, job: Job, *, raise_on_failure: bool = False, **kwargs) -> ValidationResult:
        """Validate a job. Anonymous assets may be created if there are inline
        defined entities, e.g. Component, Environment & Code. Only pipeline job
        is supported for now.

        :param job: Job object to be validated.
        :type job: Job
        :param raise_on_failure: Whether raise error when there are validation errors.
        :type raise_on_failure: bool
        :return: a ValidationResult object containing all found errors.
        :rtype: ValidationResult
        """
        return self._validate(job, raise_on_failure=raise_on_failure, **kwargs)

    @monitor_with_telemetry_mixin(logger, "Job.Validate", ActivityType.INTERNALCALL)
    def _validate(
        self, job: Job, *, raise_on_failure: bool = False, **kwargs  # pylint:disable=unused-argument
    ) -> ValidationResult:
        """Implementation of validate.

        Add this function to avoid calling validate() directly in
        create_or_update(), which will impact telemetry statistics &
        bring experimental warning in create_or_update().
        """
        git_code_validation_result = SchemaValidatableMixin._create_empty_validation_result()
        # TODO: move this check to Job._validate after validation is supported for all job types
        # If private features are enable and job has code value of type str we need to check
        # that it is a valid git path case. Otherwise we should throw a ValidationException
        # saying that the code value is not a valid code value
        if (
            hasattr(job, "code")
            and job.code is not None
            and isinstance(job.code, str)
            and job.code.startswith(GIT_PATH_PREFIX)
            and not is_private_preview_enabled()
        ):
            git_code_validation_result.append_error(
                message=f"Invalid code value: {job.code}. Git paths are not supported.",
                yaml_path="code",
            )

        if not isinstance(job, SchemaValidatableMixin):
            return git_code_validation_result.try_raise(error_target=ErrorTarget.JOB, raise_error=raise_on_failure)

        validation_result = job._validate(raise_error=raise_on_failure)
        validation_result.merge_with(git_code_validation_result)
        # fast return to avoid remote call if local validation not passed
        # TODO: use remote call to validate the entire job after MFE API is ready
        if validation_result.passed and isinstance(job, PipelineJob):
            try:
                job.compute = self._try_get_compute_arm_id(job.compute)
            except Exception as e:  # pylint: disable=broad-except
                validation_result.append_error(yaml_path="compute", message=str(e))

            for node_name, node in job.jobs.items():
                try:
                    # TODO(1979547): refactor, not all nodes have compute
                    if not isinstance(node, ControlFlowNode):
                        node.compute = self._try_get_compute_arm_id(node.compute)
                except Exception as e:  # pylint: disable=broad-except
                    validation_result.append_error(yaml_path=f"jobs.{node_name}.compute", message=str(e))

        validation_result.resolve_location_for_diagnostics(job._source_path)
        return validation_result.try_raise(raise_error=raise_on_failure, error_target=ErrorTarget.PIPELINE)

    @distributed_trace
    @monitor_with_telemetry_mixin(logger, "Job.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(
        self,
        job: Job,
        *,
        description: Optional[str] = None,
        compute: Optional[str] = None,
        tags: Optional[dict] = None,
        experiment_name: Optional[str] = None,
        skip_validation: bool = False,
        **kwargs,
    ) -> Job:
        """Create or update a job, if there're inline defined entities, e.g.
        Environment, Code, they'll be created together with the job.

        :param Job job: Job definition or object which can be translate to a job.
        :param description: Description to overwrite when submitting the pipeline.
        :type description: str
        :param compute: Compute target to overwrite when submitting the pipeline.
        :type compute: str
        :param tags: Tags to overwrite when submitting the pipeline.
        :type tags: dict
        :param experiment_name: Name of the experiment the job will be created under, if None is provided,
            job will be created under experiment 'Default'.
        :type experiment_name: str
        :param skip_validation: whether to skip validation before creating/updating the job. Note that dependent
            resources like anonymous component won't skip their validation in creating.
        :type skip_validation: bool
        :raises [~azure.ai.ml.exceptions.UserErrorException, ~azure.ai.ml.exceptions.ValidationException]: Raised if
            Job cannot be successfully validated. Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.AssetException: Raised if Job assets
            (e.g. Data, Code, Model, Environment) cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.ModelException: Raised if Job model cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.JobException: Raised if Job object or attributes correctly formatted.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :raises ~azure.ai.ml.exceptions.DockerEngineNotAvailableError: Raised if Docker Engine
            is not available for local job.
        :return: Created or updated job.
        :rtype: ~azure.ai.ml.entities.Job
        """
        try:
            if isinstance(job, BaseNode) and not (
                isinstance(job, (Command, Spark))
            ):  # Command/Spark objects can be used directly
                job = job._to_job()

            # Set job properties before submission
            if description is not None:
                job.description = description
            if compute is not None:
                job.compute = compute
            if tags is not None:
                job.tags = tags
            if experiment_name is not None:
                job.experiment_name = experiment_name

            if job.compute == LOCAL_COMPUTE_TARGET:
                job.environment_variables[COMMON_RUNTIME_ENV_VAR] = "true"

            if not skip_validation:
                self._validate(job, raise_on_failure=True)

            # Create all dependent resources
            self._resolve_arm_id_or_upload_dependencies(job)

            git_props = get_git_properties()
            # Do not add git props if they already exist in job properties.
            # This is for update specifically-- if the user switches branches and tries to update
            # their job, the request will fail since the git props will be repopulated.
            # MFE does not allow existing properties to be updated, only for new props to be added
            if not any(prop_name in job.properties for prop_name in git_props):
                job.properties = {**job.properties, **git_props}
            rest_job_resource = to_rest_job_object(job)

            # Make a copy of self._kwargs instead of contaminate the original one
            kwargs = dict(**self._kwargs)
            # set headers with user aml token if job is a pipeline or has a user identity setting
            if (rest_job_resource.properties.job_type == RestJobType.PIPELINE) or (
                hasattr(rest_job_resource.properties, "identity")
                and (isinstance(rest_job_resource.properties.identity, UserIdentity))
            ):
                self._set_headers_with_user_aml_token(kwargs)

            result = self._operation_2023_02_preview.create_or_update(
                id=rest_job_resource.name,  # type: ignore
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                body=rest_job_resource,
                **kwargs,
            )

            if is_local_run(result):
                ws_base_url = self._all_operations.all_operations[
                    AzureMLResourceType.WORKSPACE
                ]._operation._client._base_url
                snapshot_id = start_run_if_local(
                    result,
                    self._credential,
                    ws_base_url,
                    self._requests_pipeline,
                )
                # in case of local run, the first create/update call to MFE returns the
                # request for submitting to ES. Once we request to ES and start the run, we
                # need to put the same body to MFE to append user tags etc.
                job_object = self._get_job(rest_job_resource.name)
                if result.properties.tags is not None:
                    for tag_name, tag_value in rest_job_resource.properties.tags.items():
                        job_object.properties.tags[tag_name] = tag_value
                if result.properties.properties is not None:
                    for (
                        prop_name,
                        prop_value,
                    ) in rest_job_resource.properties.properties.items():
                        job_object.properties.properties[prop_name] = prop_value
                if snapshot_id is not None:
                    job_object.properties.properties["ContentSnapshotId"] = snapshot_id

                result = self._operation_2023_02_preview.create_or_update(
                    id=rest_job_resource.name,  # type: ignore
                    resource_group_name=self._operation_scope.resource_group_name,
                    workspace_name=self._workspace_name,
                    body=job_object,
                    **kwargs,
                )
            return self._resolve_azureml_id(Job._from_rest_object(result))
        except Exception as ex:  # pylint: disable=broad-except
            from marshmallow.exceptions import ValidationError as SchemaValidationError

            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            else:
                raise ex

    def _archive_or_restore(self, name: str, is_archived: bool):
        job_object = self._get_job(name)
        if _is_pipeline_child_job(job_object):
            raise PipelineChildJobError(job_id=job_object.id)
        job_object.properties.is_archived = is_archived

        self._operation_2023_02_preview.create_or_update(
            id=job_object.name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=job_object,
        )

    @distributed_trace
    @monitor_with_telemetry_mixin(logger, "Job.Archive", ActivityType.PUBLICAPI)
    def archive(self, name: str) -> None:
        """Archive a job or restore an archived job.

        :param name: Name of the job.
        :type name: str
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """

        self._archive_or_restore(name=name, is_archived=True)

    @distributed_trace
    @monitor_with_telemetry_mixin(logger, "Job.Restore", ActivityType.PUBLICAPI)
    def restore(self, name: str) -> None:
        """Archive a job or restore an archived job.

        :param name: Name of the job.
        :type name: str
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """

        self._archive_or_restore(name=name, is_archived=False)

    @distributed_trace
    @monitor_with_activity(logger, "Job.Stream", ActivityType.PUBLICAPI)
    def stream(self, name: str) -> None:
        """Stream logs of a job.

        :param str name: Name of the job.
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """
        job_object = self._get_job(name)

        if _is_pipeline_child_job(job_object):
            raise PipelineChildJobError(job_id=job_object.id)

        self._stream_logs_until_completion(
            self._runs_operations, job_object, self._datastore_operations, requests_pipeline=self._requests_pipeline
        )

    @distributed_trace
    @monitor_with_activity(logger, "Job.Download", ActivityType.PUBLICAPI)
    def download(
        self,
        name: str,
        *,
        download_path: Union[PathLike, str] = ".",
        output_name: Optional[str] = None,
        all: bool = False,  # pylint: disable=redefined-builtin
    ) -> None:
        """Download logs and output of a job.

        :param str name: Name of a job.
        :param Union[PathLike, str] download_path: Local path as download destination, defaults to '.'.
        :param str output_name: Named output to download, defaults to None.
        :param bool all: Whether to download logs and all named outputs, defaults to False.
        :param name: Name of a job.
        :type name: str
        :param download_path: Local path as download destination, defaults to '.'.
        :type download_path: Union[PathLike, str]
        :param output_name: Named output to download, defaults to None.
        :type output_name: str
        :param all: Whether to download logs and all named outputs, defaults to False.
        :type all: bool
        :raises ~azure.ai.ml.exceptions.JobException: Raised if Job is not yet in a terminal state.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.MlException: Raised if logs and outputs cannot be successfully downloaded.
            Details will be provided in the error message.
        """
        job_details = self.get(name)
        # job is reused, get reused job to download
        if (
            job_details.properties.get(PipelineConstants.REUSED_FLAG_FIELD) == PipelineConstants.REUSED_FLAG_TRUE
            and PipelineConstants.REUSED_JOB_ID in job_details.properties
        ):
            reused_job_name = job_details.properties[PipelineConstants.REUSED_JOB_ID]
            reused_job_detail = self.get(reused_job_name)
            module_logger.info("job %s reuses previous job %s, download from the reused job.", name, reused_job_name)
            name, job_details = reused_job_name, reused_job_detail
        job_status = job_details.status
        if job_status not in RunHistoryConstants.TERMINAL_STATUSES:
            msg = "This job is in state {}. Download is allowed only in states {}".format(
                job_status, RunHistoryConstants.TERMINAL_STATUSES
            )
            raise JobException(
                message=msg,
                target=ErrorTarget.JOB,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        is_batch_job = job_details.tags.get("azureml.batchrun", None) == "true"
        outputs = {}
        download_path = Path(download_path)
        artifact_directory_name = "artifacts"
        output_directory_name = "named-outputs"

        def log_missing_uri(what: str):
            module_logger.debug(
                'Could not download %s for job "%s" (job status: %s)', what, job_details.name, job_details.status
            )

        if isinstance(job_details, SweepJob):
            best_child_run_id = job_details.properties.get(SWEEP_JOB_BEST_CHILD_RUN_ID_PROPERTY_NAME, None)
            if best_child_run_id:
                self.download(
                    best_child_run_id,
                    download_path=download_path,
                    output_name=output_name,
                    all=all,
                )
            else:
                log_missing_uri(what="from best child run")

            if output_name:
                # Don't need to download anything from the parent
                return
            # only download default artifacts (logs + default outputs) from parent
            artifact_directory_name = "hd-artifacts"
            output_name = None
            all = False

        if is_batch_job:
            scoring_uri = self._get_batch_job_scoring_output_uri(job_details.name)
            if scoring_uri:
                outputs = {BATCH_JOB_CHILD_RUN_OUTPUT_NAME: scoring_uri}
            else:
                log_missing_uri("batch job scoring file")
        elif output_name:
            outputs = self._get_named_output_uri(name, output_name)

            if output_name not in outputs:
                log_missing_uri(what=f'output "{output_name}"')
        elif all:
            outputs = self._get_named_output_uri(name)

            if DEFAULT_ARTIFACT_STORE_OUTPUT_NAME not in outputs:
                log_missing_uri(what="logs")
        else:
            outputs = self._get_named_output_uri(name, DEFAULT_ARTIFACT_STORE_OUTPUT_NAME)

            if DEFAULT_ARTIFACT_STORE_OUTPUT_NAME not in outputs:
                log_missing_uri(what="logs")

        # Download all requested artifacts
        for item_name, uri in outputs.items():
            if is_batch_job:
                destination = download_path
            elif item_name == DEFAULT_ARTIFACT_STORE_OUTPUT_NAME:
                destination = download_path / artifact_directory_name
            else:
                destination = download_path / output_directory_name / item_name

            module_logger.info("Downloading artifact %s to %s", uri, destination)
            download_artifact_from_aml_uri(
                uri=uri,
                destination=destination,
                datastore_operation=self._datastore_operations,
            )

    def _get_named_output_uri(
        self, job_name: str, output_names: Optional[Union[Iterable[str], str]] = None
    ) -> Dict[str, str]:
        """Gets the URIs to the specified named outputs of job.

        :param str job_name: Run ID of the job
        :param Optional[Union[Iterable[str], str]] output_names: Either an
               output name, or an iterable of output names. If omitted, all
               outputs are returned.
        :return Dict[str, str]: Map of output_names to URIs. Note that
            URIs that could not be found will not be present in the map.
        """

        if isinstance(output_names, str):
            output_names = {output_names}
        elif output_names:
            output_names = set(output_names)

        outputs = get_job_output_uris_from_dataplane(
            job_name,
            self._runs_operations,
            self._dataset_dataplane_operations,
            self._model_dataplane_operations,
            output_names=output_names,
        )

        missing_outputs = (output_names or set()).difference(outputs.keys())

        # Include default artifact store in outputs
        if (not output_names) or DEFAULT_ARTIFACT_STORE_OUTPUT_NAME in missing_outputs:
            try:
                job = self.get(job_name)
                artifact_store_uri = job.outputs[DEFAULT_ARTIFACT_STORE_OUTPUT_NAME]
                if artifact_store_uri is not None and artifact_store_uri.path:
                    outputs[DEFAULT_ARTIFACT_STORE_OUTPUT_NAME] = artifact_store_uri.path
            except (AttributeError, KeyError):
                outputs[DEFAULT_ARTIFACT_STORE_OUTPUT_NAME] = SHORT_URI_FORMAT.format(
                    "workspaceartifactstore", f"ExperimentRun/dcid.{job_name}/"
                )
            missing_outputs.discard(DEFAULT_ARTIFACT_STORE_OUTPUT_NAME)

        # A job's output is not always reported in the outputs dict, but
        # doesn't currently have a user configurable location.
        # Perform a search of known paths to find output
        # TODO: Remove once job output locations are reliably returned from the service

        default_datastore = self._datastore_operations.get_default().name

        for name in missing_outputs:
            potential_uris = [
                SHORT_URI_FORMAT.format(default_datastore, f"azureml/{job_name}/{name}/"),
                SHORT_URI_FORMAT.format(default_datastore, f"dataset/{job_name}/{name}/"),
            ]

            for potential_uri in potential_uris:
                if aml_datastore_path_exists(potential_uri, self._datastore_operations):
                    outputs[name] = potential_uri
                    break

        return outputs

    def _get_batch_job_scoring_output_uri(self, job_name: str) -> Optional[str]:
        uri = None
        # Download scoring output, which is the "score" output of the child job named "batchscoring"
        # Batch Jobs are pipeline jobs with only one child, so this should terminate after an iteration
        for child in self._runs_operations.get_run_children(job_name):
            uri = self._get_named_output_uri(child.name, BATCH_JOB_CHILD_RUN_OUTPUT_NAME).get(
                BATCH_JOB_CHILD_RUN_OUTPUT_NAME, None
            )
            # After the correct child is found, break to prevent unnecessary looping
            if uri is not None:
                break
        return uri

    def _get_job(self, name: str) -> JobBase:
        return self._operation_2023_02_preview.get(
            id=name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            **self._kwargs,
        )

    def _get_workspace_url(self, url_key="history"):
        discovery_url = (
            self._all_operations.all_operations[AzureMLResourceType.WORKSPACE]
            .get(self._operation_scope.workspace_name)
            .discovery_url
        )
        all_urls = json.loads(
            download_text_from_url(
                discovery_url, create_requests_pipeline_with_retry(requests_pipeline=self._requests_pipeline)
            )
        )
        return all_urls[url_key]

    def _resolve_arm_id_or_upload_dependencies(self, job: Job) -> None:
        """This method converts name or name:version to ARM id. Or it
        registers/uploads nested dependencies.

        :param job: the job resource entity
        :type job: Job
        :return: the job resource entity that nested dependencies are resolved
        :rtype: Job
        """

        self._resolve_arm_id_or_azureml_id(job, self._orchestrators.get_asset_arm_id)

        if isinstance(job, PipelineJob):
            # Resolve top-level inputs
            self._resolve_pipeline_job_inputs(job, job._base_path)
            # inputs in sub-pipelines has been resolved in
            # self._resolve_arm_id_or_azureml_id(job, self._orchestrators.get_asset_arm_id)
            # as they are part of the pipeline component
        elif isinstance(job, AutoMLJob):
            self._resolve_automl_job_inputs(job)
        elif isinstance(job, Spark):
            self._resolve_job_inputs(job._job_inputs.values(), job._base_path)
        elif isinstance(job, Command):
            # TODO: switch to use inputs of Command objects, once the inputs/outputs building
            # logic is removed from the BaseNode constructor.
            try:
                self._resolve_job_inputs(job._job_inputs.values(), job._base_path)
            except AttributeError:
                # If the job object doesn't have "inputs" attribute, we don't need to resolve. E.g. AutoML jobs
                pass
        else:
            try:
                self._resolve_job_inputs(job.inputs.values(), job._base_path)
            except AttributeError:
                # If the job object doesn't have "inputs" attribute, we don't need to resolve. E.g. AutoML jobs
                pass

    def _resolve_automl_job_inputs(self, job: AutoMLJob) -> None:
        """This method resolves the inputs for AutoML jobs.

        :param job: the job resource entity
        :type job: AutoMLJob
        """
        if isinstance(job, AutoMLJob):
            self._resolve_job_input(job.training_data, job._base_path)
            if job.validation_data is not None:
                self._resolve_job_input(job.validation_data, job._base_path)
            if hasattr(job, "test_data") and job.test_data is not None:
                self._resolve_job_input(job.test_data, job._base_path)

    def _resolve_azureml_id(self, job: Job) -> Job:
        """This method converts ARM id to name or name:version for nested
        entities.

        :param job: the job resource entity
        :type job: Job
        :return: the job resource entity that nested dependencies are resolved
        :rtype: Job
        """
        self._append_tid_to_studio_url(job)
        self._resolve_job_inputs_arm_id(job)
        return self._resolve_arm_id_or_azureml_id(job, self._orchestrators.resolve_azureml_id)

    def _resolve_compute_id(self, resolver: Callable, target: Any) -> Any:
        # special case for local runs
        if target is not None and target.lower() == LOCAL_COMPUTE_TARGET:
            return LOCAL_COMPUTE_TARGET
        try:
            modified_target_name = target
            if target.lower().startswith(AzureMLResourceType.VIRTUALCLUSTER + "/"):
                # Compute target can be either workspace-scoped compute type,
                # or AML scoped VC. In the case of VC, resource name will be of form
                # azureml:virtualClusters/<name> to disambiguate from azureml:name (which is always compute)
                modified_target_name = modified_target_name[len(AzureMLResourceType.VIRTUALCLUSTER) + 1 :]
                modified_target_name = LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT.format(
                    self._operation_scope.subscription_id,
                    self._operation_scope.resource_group_name,
                    AZUREML_RESOURCE_PROVIDER,
                    AzureMLResourceType.VIRTUALCLUSTER,
                    modified_target_name,
                )
            return resolver(
                modified_target_name,
                azureml_type=AzureMLResourceType.VIRTUALCLUSTER,
                sub_workspace_resource=False,
            )
        except Exception:  # pylint: disable=broad-except
            return resolver(target, azureml_type=AzureMLResourceType.COMPUTE)

    def _resolve_job_inputs(self, entries: Iterable[Union[Input, str, bool, int, float]], base_path: str):
        """resolve job inputs as ARM id or remote url."""
        for entry in entries:
            self._resolve_job_input(entry, base_path)

    def _resolve_pipeline_job_inputs(self, job: PipelineJob, base_path: str):
        """resolve pipeline job inputs as ARM id or remote url."""
        inputs = []
        # Flatten inputs for pipeline job
        for key, item in job.inputs.items():
            if isinstance(item, _GroupAttrDict):
                inputs.extend(item.flatten(group_parameter_name=key))
            else:
                # skip resolving inferred optional input without path (in do-while + dynamic input case)
                if isinstance(item._data, Input) and not item._data.path and item._meta._is_inferred_optional:
                    continue
                inputs.append(item._data)
        for entry in inputs:
            self._resolve_job_input(entry, base_path)

    def _resolve_job_input(self, entry: Union[Input, str, bool, int, float], base_path: str) -> None:
        """resolve job input as ARM id or remote url."""

        # path can be empty if the job was created from builder functions
        if isinstance(entry, Input) and not entry.path:
            msg = "Input path can't be empty for jobs."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.JOB,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

        if (
            not isinstance(entry, Input)
            or is_ARM_id_for_resource(entry.path)
            or is_url(entry.path)
            or is_data_binding_expression(entry.path)  # literal value but set mode in pipeline yaml
        ):  # Literal value, ARM id or remote url. Pass through
            return
        try:
            datastore_name = (
                entry.datastore if hasattr(entry, "datastore") and entry.datastore else WORKSPACE_BLOB_STORE
            )

            if os.path.isabs(entry.path):  # absolute local path, upload, transform to remote url
                if entry.type == AssetTypes.URI_FOLDER and not os.path.isdir(entry.path):
                    raise ValidationException(
                        message="There is no dir on target path: {}".format(entry.path),
                        target=ErrorTarget.JOB,
                        no_personal_data_message="There is no dir on target path",
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
                    )
                if entry.type == AssetTypes.URI_FILE and not os.path.isfile(entry.path):
                    raise ValidationException(
                        message="There is no file on target path: {}".format(entry.path),
                        target=ErrorTarget.JOB,
                        no_personal_data_message="There is no file on target path",
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
                    )
                # absolute local path
                entry.path = _upload_and_generate_remote_uri(
                    self._operation_scope,
                    self._datastore_operations,
                    entry.path,
                    datastore_name=datastore_name,
                    show_progress=self._show_progress,
                )
                # TODO : Move this part to a common place
                if entry.type == AssetTypes.URI_FOLDER and entry.path and not entry.path.endswith("/"):
                    entry.path = entry.path + "/"
            elif ":" in entry.path or "@" in entry.path:  # Check for AzureML id, is there a better way?
                asset_type = AzureMLResourceType.DATA
                if entry.type in [AssetTypes.MLFLOW_MODEL, AssetTypes.CUSTOM_MODEL]:
                    asset_type = AzureMLResourceType.MODEL

                entry.path = self._orchestrators.get_asset_arm_id(entry.path, asset_type)
            else:  # relative local path, upload, transform to remote url
                # Base path will be None for dsl pipeline component for now. We have 2 choices if the dsl pipeline
                # function is imported from another file:
                # 1) Use cwd as default base path;
                # 2) Use the file path of the dsl pipeline function as default base path.
                # Pick solution 1 for now as defining input path in the script to submit is a more common scenario.
                local_path = Path(base_path or Path.cwd(), entry.path).resolve()
                entry.path = _upload_and_generate_remote_uri(
                    self._operation_scope,
                    self._datastore_operations,
                    local_path,
                    datastore_name=datastore_name,
                    show_progress=self._show_progress,
                )
                # TODO : Move this part to a common place
                if entry.type == AssetTypes.URI_FOLDER and entry.path and not entry.path.endswith("/"):
                    entry.path = entry.path + "/"
        except (MlException, HttpResponseError) as e:
            raise e
        except Exception as e:
            raise ValidationException(
                message=f"Supported input path value are ARM id, AzureML id, remote uri or local path.\n"
                f"Met {type(e)}:\n{e}",
                target=ErrorTarget.JOB,
                no_personal_data_message="Supported input path value are ARM id, AzureML id, remote uri or local path.",
                error=e,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    def _resolve_job_inputs_arm_id(self, job: Job) -> None:
        try:
            inputs: Dict[str, Union[Input, InputOutputBase, str, bool, int, float]] = job.inputs
            for _, entry in inputs.items():
                if isinstance(entry, InputOutputBase):
                    # extract original input form input builder.
                    entry = entry._data
                if not isinstance(entry, Input) or is_url(entry.path):  # Literal value or remote url
                    continue
                # ARM id
                entry.path = self._orchestrators.resolve_azureml_id(entry.path)

        except AttributeError:
            # If the job object doesn't have "inputs" attribute, we don't need to resolve. E.g. AutoML jobs
            pass

    def _resolve_arm_id_or_azureml_id(self, job: Job, resolver: Callable) -> Job:
        """Resolve arm_id for a given job."""
        # TODO: this will need to be parallelized when multiple tasks
        # are required. Also consider the implications for dependencies.

        if isinstance(job, _BaseJob):
            job.compute = self._resolve_compute_id(resolver, job.compute)
        elif isinstance(job, Command):
            job = self._resolve_arm_id_for_command_job(job, resolver)
        elif isinstance(job, ImportJob):
            job = self._resolve_arm_id_for_import_job(job, resolver)
        elif isinstance(job, Spark):
            job = self._resolve_arm_id_for_spark_job(job, resolver)
        elif isinstance(job, ParallelJob):
            job = self._resolve_arm_id_for_parallel_job(job, resolver)
        elif isinstance(job, SweepJob):
            job = self._resolve_arm_id_for_sweep_job(job, resolver)
        elif isinstance(job, AutoMLJob):
            job = self._resolve_arm_id_for_automl_job(job, resolver, inside_pipeline=False)
        elif isinstance(job, PipelineJob):
            job = self._resolve_arm_id_for_pipeline_job(job, resolver)
        else:
            msg = f"Non supported job type: {type(job)}"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.JOB,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        return job

    def _resolve_arm_id_for_command_job(self, job: Command, resolver: Callable) -> Job:
        """Resolve arm_id for CommandJob."""
        if job.code is not None and is_registry_id_for_resource(job.code):
            msg = "Format not supported for code asset: {}"
            raise ValidationException(
                message=msg.format(job.code),
                target=ErrorTarget.JOB,
                no_personal_data_message=msg.format("[job.code]"),
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if job.code is not None and not is_ARM_id_for_resource(job.code, AzureMLResourceType.CODE):
            job.code = resolver(
                Code(base_path=job._base_path, path=job.code),
                azureml_type=AzureMLResourceType.CODE,
            )
        job.environment = resolver(job.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        job.compute = self._resolve_compute_id(resolver, job.compute)
        return job

    def _resolve_arm_id_for_spark_job(self, job: Spark, resolver: Callable) -> Job:
        """Resolve arm_id for SparkJob."""
        if job.code is not None and is_registry_id_for_resource(job.code):
            msg = "Format not supported for code asset: {}"
            raise JobException(
                message=msg.format(job.code),
                target=ErrorTarget.JOB,
                no_personal_data_message=msg.format("[job.code]"),
                error_category=ErrorCategory.USER_ERROR,
            )

        if job.code is not None and not is_ARM_id_for_resource(job.code, AzureMLResourceType.CODE):
            job.code = resolver(
                Code(base_path=job._base_path, path=job.code),
                azureml_type=AzureMLResourceType.CODE,
            )
        job.environment = resolver(job.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        job.compute = self._resolve_compute_id(resolver, job.compute)
        return job

    def _resolve_arm_id_for_import_job(self, job: Job, resolver: Callable) -> Job:
        """Resolve arm_id for ImportJob."""
        # compute property will be no longer applicable once import job type is ready on MFE in PuP
        # for PrP, we use command job type instead for import job where compute property is required
        # However, MFE only validates compute resource url format. Execution service owns the real
        # validation today but supports reserved compute names like AmlCompute, ContainerInstance and
        # DataFactory here for 'clusterless' jobs
        job.compute = self._resolve_compute_id(resolver, ComputeType.ADF)
        return job

    def _resolve_arm_id_for_parallel_job(self, job: Job, resolver: Callable) -> Job:
        """Resolve arm_id for ParallelJob."""
        if job.code is not None and not is_ARM_id_for_resource(job.code, AzureMLResourceType.CODE):
            job.code = resolver(
                Code(base_path=job._base_path, path=job.code),
                azureml_type=AzureMLResourceType.CODE,
            )
        job.environment = resolver(job.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        job.compute = self._resolve_compute_id(resolver, job.compute)
        return job

    def _resolve_arm_id_for_sweep_job(self, job: Job, resolver: Callable) -> Job:
        """Resolve arm_id for SweepJob."""
        if job.trial.code is not None and not is_ARM_id_for_resource(job.trial.code, AzureMLResourceType.CODE):
            job.trial.code = resolver(
                Code(base_path=job._base_path, path=job.trial.code),
                azureml_type=AzureMLResourceType.CODE,
            )
        job.trial.environment = resolver(job.trial.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        job.compute = self._resolve_compute_id(resolver, job.compute)
        return job

    def _resolve_arm_id_for_automl_job(  # pylint: disable=no-self-use
        self, job: Job, resolver: Callable, inside_pipeline: bool
    ) -> Job:
        """Resolve arm_id for AutoMLJob."""
        # AutoML does not have dependency uploads. Only need to resolve reference to arm id.

        # automl node in pipeline has optional compute
        if inside_pipeline and job.compute is None:
            return job
        job.compute = resolver(job.compute, azureml_type=AzureMLResourceType.COMPUTE)
        return job

    def _resolve_arm_id_for_pipeline_job(self, pipeline_job: "PipelineJob", resolver: Callable) -> Job:
        """Resolve arm_id for pipeline_job."""
        # Get top-level job compute
        _get_job_compute_id(pipeline_job, resolver)

        # Process job defaults:
        if pipeline_job.settings:
            pipeline_job.settings.default_datastore = resolver(
                pipeline_job.settings.default_datastore,
                azureml_type=AzureMLResourceType.DATASTORE,
            )
            pipeline_job.settings.default_compute = resolver(
                pipeline_job.settings.default_compute,
                azureml_type=AzureMLResourceType.COMPUTE,
            )

        # Process each component job
        try:
            self._component_operations._resolve_dependencies_for_pipeline_component_jobs(
                pipeline_job.component, resolver
            )
        except ComponentException as e:
            raise JobException(
                message=e.message,
                target=ErrorTarget.JOB,
                no_personal_data_message=e.no_personal_data_message,
                error_category=e.error_category,
            )

        # Create a pipeline component for pipeline job if user specified component in job yaml.
        if (
            not isinstance(pipeline_job.component, str)
            and getattr(pipeline_job.component, "_source", None) == ComponentSource.YAML_COMPONENT
        ):
            pipeline_job.component = resolver(
                pipeline_job.component,
                azureml_type=AzureMLResourceType.COMPONENT,
            )

        return pipeline_job

    def _append_tid_to_studio_url(self, job: Job) -> None:
        """Appends the user's tenant ID to the end of the studio URL so the UI
        knows against which tenant to authenticate."""
        try:
            studio_endpoint = job.services.get("Studio", None)
            studio_url = studio_endpoint.endpoint
            default_scopes = _resource_to_scopes(_get_base_url_from_metadata())
            module_logger.debug("default_scopes used: `%s`\n", default_scopes)
            # Extract the tenant id from the credential using PyJWT
            decode = jwt.decode(
                self._credential.get_token(*default_scopes).token,
                options={"verify_signature": False, "verify_aud": False},
            )
            tid = decode["tid"]
            formatted_tid = TID_FMT.format(tid)
            studio_endpoint.endpoint = studio_url + formatted_tid
        except Exception:  # pylint: disable=broad-except
            module_logger.info("Proceeding with no tenant id appended to studio URL\n")

    def _set_headers_with_user_aml_token(self, kwargs) -> Dict[str, str]:
        aml_resource_id = _get_aml_resource_id_from_metadata()
        azure_ml_scopes = _resource_to_scopes(aml_resource_id)
        module_logger.debug("azure_ml_scopes used: `%s`\n", azure_ml_scopes)
        aml_token = self._credential.get_token(*azure_ml_scopes).token
        # validate token has aml audience
        decoded_token = jwt.decode(
            aml_token,
            options={"verify_signature": False, "verify_aud": False},
        )
        if decoded_token.get("aud") != aml_resource_id:
            msg = """AAD token with aml scope could not be fetched using the credentials being used.
            Please validate if token with {0} scope can be fetched using credentials provided to MLClient.
            Token with {0} scope can be fetched using credentials.get_token({0})
            """
            raise ValidationException(
                message=msg.format(*azure_ml_scopes),
                target=ErrorTarget.JOB,
                error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
                no_personal_data_message=msg.format("[job.code]"),
                error_category=ErrorCategory.USER_ERROR,
            )

        headers = kwargs.pop("headers", {})
        headers["x-azureml-token"] = aml_token
        kwargs["headers"] = headers


def _get_job_compute_id(job: Union[Job, Command], resolver: Callable) -> None:
    job.compute = resolver(job.compute, azureml_type=AzureMLResourceType.COMPUTE)
