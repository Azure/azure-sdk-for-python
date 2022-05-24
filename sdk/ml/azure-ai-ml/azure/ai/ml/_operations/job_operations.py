# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import os.path
from os import PathLike
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Union,
)
from azure.ai.ml._azure_environments import ENDPOINT_URLS, _get_cloud_details, resource_to_scopes
from azure.ai.ml.entities._assets._artifacts.code import Code
from azure.ai.ml.entities._job.job_name_generator import generate_job_name
from ..entities._validation import ValidationResult

try:
    from typing import Protocol  # For python >= 3.8
except ImportError:
    from typing_extensions import Protocol  # For python < 3.8

from azure.ai.ml.constants import (
    BATCH_JOB_CHILD_RUN_NAME,
    BATCH_JOB_CHILD_RUN_OUTPUT_NAME,
    DEFAULT_ARTIFACT_STORE_OUTPUT_NAME,
    SWEEP_JOB_BEST_CHILD_RUN_ID_PROPERTY_NAME,
)

from azure.ai.ml.entities._job.job_errors import JobParsingError, PipelineChildJobError

import jwt
from azure.identity import ChainedTokenCredential
from azure.core.exceptions import ResourceNotFoundError

from azure.ai.ml._artifacts._artifact_utilities import (
    download_artifact_from_aml_uri,
    aml_datastore_path_exists,
)
from azure.ai.ml._operations.run_history_constants import RunHistoryConstants
from azure.ai.ml._restclient.v2022_02_01_preview import (
    AzureMachineLearningWorkspaces as ServiceClient022022Preview,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    JobBaseData,
    UserIdentity,
    JobType as RestJobType,
    ListViewType,
)
from azure.ai.ml._restclient.runhistory import (
    AzureMachineLearningWorkspaces as ServiceClientRunHistory,
)
from azure.ai.ml._restclient.model_dataplane import (
    AzureMachineLearningWorkspaces as ServiceClientModelDataplane,
)
from azure.ai.ml._restclient.dataset_dataplane import (
    AzureMachineLearningWorkspaces as ServiceClientDatasetDataplane,
)
from azure.ai.ml._utils.utils import (
    create_session_with_retry,
    download_text_from_url,
    is_url,
    is_data_binding_expression,
    get_list_view_type,
)
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope, _ScopeDependentOperations
from azure.ai.ml.constants import (
    AzureMLResourceType,
    TID_FMT,
    AZUREML_RESOURCE_PROVIDER,
    LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT,
    LOCAL_COMPUTE_TARGET,
    SHORT_URI_FORMAT,
    AssetTypes,
    API_URL_KEY,
)
from azure.ai.ml.entities import (
    CommandJob,
    Job,
    PipelineJob,
    Component,
    CommandComponent,
    Compute,
    ParallelJob,
    ParallelComponent,
)
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.sweep import SweepJob
from azure.ai.ml.entities._job.base_job import _BaseJob
from azure.ai.ml.entities._job.job import _is_pipeline_child_job
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._builders import Command, BaseNode, Sweep, Parallel
from azure.ai.ml.entities._job.pipeline.pipeline_job_settings import PipelineJobSettings
from azure.ai.ml._artifacts._artifact_utilities import _upload_and_generate_remote_uri

from .job_ops_helper import (
    get_git_properties,
    stream_logs_until_completion,
    get_job_output_uris_from_dataplane,
)
from .local_job_invoker import is_local_run, start_run_if_local
from .operation_orchestrator import OperationOrchestrator, is_ARM_id_for_resource
from .run_operations import RunOperations
from .dataset_dataplane_operations import DatasetDataplaneOperations
from .model_dataplane_operations import ModelDataplaneOperations
from azure.ai.ml._operations.compute_operations import ComputeOperations

if TYPE_CHECKING:
    from azure.ai.ml._operations import DatastoreOperations

from azure.ai.ml._telemetry import (
    AML_INTERNAL_LOGGER_NAMESPACE,
    ActivityType,
    monitor_with_activity,
    monitor_with_telemetry_mixin,
)
from azure.ai.ml._ml_exceptions import JobException, ErrorCategory, ErrorTarget, ValidationException

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class JobOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client_02_2022_preview: ServiceClient022022Preview,
        all_operations: OperationsContainer,
        credential: ChainedTokenCredential,
        **kwargs: Any,
    ):
        super(JobOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._operation_2022_02_preview = service_client_02_2022_preview.jobs
        self._all_operations = all_operations
        self._kwargs = kwargs
        self._stream_logs_until_completion = stream_logs_until_completion
        # Dataplane service clients are lazily created as they are needed
        self._runs_operations_client = None
        self._dataset_dataplane_operations_client = None
        self._model_dataplane_operations_client = None
        self._api_base_url = None
        self._container = "azureml"
        self._credential = credential
        self._orchestrators = OperationOrchestrator(self._all_operations, self._operation_scope)

    @property
    def _compute_operations(self) -> ComputeOperations:
        return self._all_operations.get_operation(
            AzureMLResourceType.COMPUTE, lambda x: isinstance(x, ComputeOperations)
        )

    @property
    def _datastore_operations(self) -> "DatastoreOperations":
        return self._all_operations.all_operations[AzureMLResourceType.DATASTORE]

    @property
    def _runs_operations(self) -> RunOperations:
        if not self._runs_operations_client:
            service_client_run_history = ServiceClientRunHistory(self._credential, base_url=self._api_url)
            self._runs_operations_client = RunOperations(self._operation_scope, service_client_run_history)
        return self._runs_operations_client

    @property
    def _dataset_dataplane_operations(self) -> DatasetDataplaneOperations:
        if not self._dataset_dataplane_operations_client:
            service_client_dataset_dataplane = ServiceClientDatasetDataplane(self._credential, base_url=self._api_url)
            self._dataset_dataplane_operations_client = DatasetDataplaneOperations(
                self._operation_scope, service_client_dataset_dataplane
            )
        return self._dataset_dataplane_operations_client

    @property
    def _model_dataplane_operations(self) -> ModelDataplaneOperations:
        if not self._model_dataplane_operations_client:
            service_client_model_dataplane = ServiceClientModelDataplane(self._credential, base_url=self._api_url)
            self._model_dataplane_operations_client = ModelDataplaneOperations(
                self._operation_scope, service_client_model_dataplane
            )
        return self._model_dataplane_operations_client

    @property
    def _api_url(self):
        if not self._api_base_url:
            self._api_base_url = self._get_workspace_url(url_key=API_URL_KEY)
        return self._api_base_url

    @monitor_with_activity(logger, "Job.List", ActivityType.PUBLICAPI)
    def list(
        self,
        parent_job_name: str = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
        schedule_defined: bool = None,
        scheduled_job_name: str = None,
    ) -> Iterable[Job]:
        """List jobs of the workspace.

        :param parent_job_name: When provided, returns children of named job.
        :type parent_job_name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived jobs. Default: ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :param schedule_defined: When provided, only jobs that initially defined a schedule will be returned.
        :type schedule_defined: Optional[bool]
        :param scheduled_job_name: Name of a job that initially defined a schedule. When provided, only jobs triggered by the schedule of the given job will be returned.
        :type scheduled_job_name: Optional[str]
        :return: An iterator like instance of Job objects.
        :rtype: ~azure.core.paging.ItemPaged[Job]
        """

        if parent_job_name:
            parent_job = self.get(parent_job_name)
            return self._runs_operations.get_run_children(parent_job.name)

        return self._operation_2022_02_preview.list(
            self._operation_scope.resource_group_name,
            self._workspace_name,
            cls=lambda objs: [self._handle_rest_errors(obj) for obj in objs],
            list_view_type=list_view_type,
            scheduled=schedule_defined,
            schedule_id=scheduled_job_name,
            **self._kwargs,
        )

    def _handle_rest_errors(self, job_object):
        """Handle errors while resolving azureml_id's during list operation"""
        try:
            return self._resolve_azureml_id(Job._from_rest_object(job_object))
        except JobParsingError:
            pass

    @monitor_with_telemetry_mixin(logger, "Job.Get", ActivityType.PUBLICAPI)
    def get(self, name: str) -> Job:
        """Get a job resource.

        :param str name: Name of the job.
        :return: Job object retrieved from the service.
        :rtype: Job
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """
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

    @monitor_with_activity(logger, "Job.Cancel", ActivityType.PUBLICAPI)
    def cancel(self, name: str) -> None:
        """Cancel job resource.

        :param str name: Name of the job.
        :return: None, or the result of cls(response)
        :rtype: None
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """
        return self._operation_2022_02_preview.cancel(
            id=name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            **self._kwargs,
        )

    def try_get_compute_arm_id(self, compute: Union[Compute, str]):
        if compute is not None:
            if is_ARM_id_for_resource(compute, resource_type=AzureMLResourceType.COMPUTE):
                # compute is not a sub-workspace resource
                compute_name = compute.split("/")[-1]
            elif isinstance(compute, Compute):
                compute_name = compute.name
            else:
                raise ValueError(
                    "compute must be either an arm id of Compute or a Compute object but got {}".format(type(compute))
                )

            if is_data_binding_expression(compute_name):
                return compute_name
            else:
                try:
                    return self._compute_operations.get(compute_name).id
                except ResourceNotFoundError:
                    # the original error is not helpful (Operation returned an invalid status 'Not Found'),
                    # so we raise a more helpful one
                    raise ResourceNotFoundError("Not found compute with name {}".format(compute_name))
        return None

    @monitor_with_telemetry_mixin(logger, "Job.Validate", ActivityType.INTERNALCALL)
    def _validate(self, job: Job, raise_on_failure: bool = False) -> ValidationResult:
        """Validate a pipeline job.
        Note that, different from component.validate, this method must be called after calling
        self._resolve_arm_id_or_upload_dependencies(job) for now to avoid resolving compute for twice.

        :param job: Job object to be validated.
        :type job: Job
        :return: a ValidationResult object containing all found errors.
        :rtype: ValidationResult
        """
        # validation is open for PipelineJob only for now
        if not isinstance(job, PipelineJob):
            return ValidationResult._create_instance()

        try:
            job.compute = self.try_get_compute_arm_id(job.compute)
            for node in job.jobs.values():
                node.compute = self.try_get_compute_arm_id(node.compute)
            return ValidationResult._create_instance()
        except Exception as e:
            if raise_on_failure:
                raise
            else:
                logger.warning(f"Validation failed: {e}")
                return ValidationResult._create_instance(singular_error_message=str(e), yaml_path="compute")

    @monitor_with_telemetry_mixin(logger, "Job.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(
        self,
        job: Union[Job, BaseNode],
        *,
        description: str = None,
        compute: str = None,
        tags: dict = None,
        experiment_name: str = None,
        **kwargs,
    ) -> Job:
        """Create or update a job, if there're inline defined entities, e.g. Environment, Code, they'll be created together with the job.

        :param Union[Job,BaseNode] job: Job definition or object which can be translate to a job.
        :param description: Description to overwrite when submitting the pipeline.
        :type description: str
        :param compute: Compute target to overwrite when submitting the pipeline.
        :type compute: str
        :param tags: Tags to overwrite when submitting the pipeline.
        :type tags: dict
        :param experiment_name: Name of the experiment the job will be created under, if None is provided, job will be created under experiment 'Default'.
        :type experiment_name: str
        :return: Created or updated job.
        :rtype: Job
        """
        if isinstance(job, BaseNode):
            job = job._to_job()

        self._generate_job_defaults(job)

        # Set job properties before submission
        if description is not None:
            job.description = description
        if compute is not None:
            job.compute = compute
        if tags is not None:
            job.tags = tags
        if experiment_name is not None:
            job.experiment_name = experiment_name

        # Check compute for warning array
        # TODO: Remove after 05/31/2022 (Task 1776012)
        if job.compute and job.compute.lower() != LOCAL_COMPUTE_TARGET:
            try:
                self._compute_operations.get(job.compute)
            except ResourceNotFoundError as e:
                raise (e)

        # Create all dependent resources
        self._resolve_arm_id_or_upload_dependencies(job)
        self._validate(job, raise_on_failure=True)

        git_props = get_git_properties()
        # Do not add git props if they already exist in job properties.
        # This is for update specifically-- if the user switches branches and tries to update their job, the request will fail since the git props will be repopulated.
        # MFE does not allow existing properties to be updated, only for new props to be added
        if not any(prop_name in job.properties for prop_name in git_props.keys()):
            job.properties = {**job.properties, **git_props}
        rest_job_resource = job._to_rest_object()

        # Make a copy of self._kwargs instead of contaminate the original one
        kwargs = dict(**self._kwargs)
        if hasattr(rest_job_resource.properties, "identity") and (
            rest_job_resource.properties.identity is None
            or isinstance(rest_job_resource.properties.identity, UserIdentity)
        ):
            self._set_headers_with_user_aml_token(kwargs)
        result = self._operation_2022_02_preview.create_or_update(
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
            snapshot_id = start_run_if_local(result, self._credential, ws_base_url)
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

            result = self._operation_2022_02_preview.create_or_update(
                id=rest_job_resource.name,  # type: ignore
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                body=job_object,
                **kwargs,
            )
        return self._resolve_azureml_id(Job._from_rest_object(result))

    def _archive_or_restore(self, name: str, is_archived: bool):
        job_object = self._get_job(name)
        if _is_pipeline_child_job(job_object):
            raise PipelineChildJobError(job_id=job_object.id)
        job_object.properties.is_archived = is_archived

        self._operation_2022_02_preview.create_or_update(
            id=job_object.name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=job_object,
        )

    @monitor_with_activity(logger, "Job.Archive", ActivityType.PUBLICAPI)
    def archive(self, name: str) -> None:
        """Archive a job or restore an archived job.

        :param name: Name of the job.
        :type name: str
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """

        self._archive_or_restore(name=name, is_archived=True)

    @monitor_with_activity(logger, "Job.Restore", ActivityType.PUBLICAPI)
    def restore(self, name: str) -> None:
        """Archive a job or restore an archived job.

        :param name: Name of the job.
        :type name: str
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """

        self._archive_or_restore(name=name, is_archived=False)

    @monitor_with_activity(logger, "Job.Stream", ActivityType.PUBLICAPI)
    def stream(self, name: str) -> None:
        """Stream logs of a job.

        :param str name: Name of the job.
        :raise: ResourceNotFoundError if can't find a job matching provided name.
        """
        job_object = self._get_job(name)

        if _is_pipeline_child_job(job_object):
            raise PipelineChildJobError(job_id=job_object.id)

        try:
            self._stream_logs_until_completion(
                self._runs_operations,
                job_object,
                self._datastore_operations,
            )
        except Exception:
            raise

    @monitor_with_activity(logger, "Job.Download", ActivityType.PUBLICAPI)
    def download(
        self,
        name: str,
        *,
        download_path: Union[PathLike, str] = Path.cwd(),
        output_name: str = None,
        all: bool = False,
    ) -> None:
        """Download logs and output of a job.

        :param str name: Name of a job.
        :param Union[PathLike, str] download_path: Local path as download destination, defaults to current working directory.
        :param str output_name: Named output to download, defaults to None.
        :param bool all: Whether to download logs and all named outputs, defaults to False.
        """
        job_details = self.get(name)
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
            logger.debug(f'Could not download {what} for job "{job_details.name}" (job status: {job_details.status})')

        if isinstance(job_details, SweepJob):
            best_child_run_id = job_details.properties.get(SWEEP_JOB_BEST_CHILD_RUN_ID_PROPERTY_NAME, None)
            if best_child_run_id:
                self.download(best_child_run_id, download_path=download_path, output_name=output_name, all=all)
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
        for name, uri in outputs.items():
            if is_batch_job:
                destination = download_path
            elif name == DEFAULT_ARTIFACT_STORE_OUTPUT_NAME:
                destination = download_path / artifact_directory_name
            else:
                destination = download_path / output_directory_name / name

            module_logger.info(f"Downloading artifact {uri} to {destination}")
            download_artifact_from_aml_uri(
                uri=uri, destination=destination, datastore_operation=self._datastore_operations
            )

    def _get_named_output_uri(
        self, job_name: str, output_names: Optional[Union[Iterable[str], str]] = None
    ) -> Dict[str, str]:
        """Gets the URIs to the specified named outputs of job

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
                if artifact_store_uri and artifact_store_uri.path:
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
        for child in self._runs_operations.get_run_children(job_name):
            if child.properties.get("azureml.moduleName", None) == BATCH_JOB_CHILD_RUN_NAME:
                uri = self._get_named_output_uri(child.name, BATCH_JOB_CHILD_RUN_OUTPUT_NAME).get(
                    BATCH_JOB_CHILD_RUN_OUTPUT_NAME, None
                )
                # After the correct child is found, break to prevent unnecessary looping
                break
        return uri

    def _get_job(self, name: str) -> JobBaseData:
        return self._operation_2022_02_preview.get(
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
        all_urls = json.loads(download_text_from_url(discovery_url, create_session_with_retry()))
        return all_urls[url_key]

    def _generate_job_defaults(self, job: Job) -> None:
        # Default name to a generated user friendly name.
        if not job.name:
            job.name = generate_job_name()

        # Default experiment to base path
        if not job.experiment_name:
            job.experiment_name = Path("./").resolve().stem.replace(" ", "") or "Default"

        job.display_name = job.display_name or job.name

    def _resolve_arm_id_or_upload_dependencies(self, job: Job) -> None:
        """This method converts name or name:version to ARM id. Or it registers/uploads nested dependencies.

        :param job: the job resource entity
        :type job: Job
        :return: the job resource entity that nested dependencies are resolved
        :rtype: Job
        """

        self._resolve_arm_id_or_azureml_id(job, self._orchestrators.get_asset_arm_id)

        if isinstance(job, PipelineJob):
            # Resolve top-level inputs
            self._resolve_job_inputs(map(lambda x: x._data, job.inputs.values()), job._base_path)
            if job.jobs:
                for _, job_instance in job.jobs.items():
                    # resolve inputs for each job's component
                    if isinstance(job_instance, BaseNode):
                        node: BaseNode = job_instance
                        self._resolve_job_inputs(
                            map(lambda x: x._data, node.inputs.values()),
                            job._base_path,
                        )
                    elif isinstance(job_instance, AutoMLJob):
                        self._resolve_automl_job_inputs(job_instance, job._base_path, inside_pipeline=True)
        elif isinstance(job, AutoMLJob):
            self._resolve_automl_job_inputs(job, job._base_path, inside_pipeline=False)
        else:
            try:
                self._resolve_job_inputs(job.inputs.values(), job._base_path)
            except AttributeError:
                # If the job object doesn't have "inputs" attribute, we don't need to resolve. E.g. AutoML jobs
                pass

    def _resolve_automl_job_input(self, input: str, base_path, inside_pipeline) -> str:
        """Resolves automl job's input.

        :param input: Job input
        :param base_path: Base path of the yaml file
        :param inside_pipeline: If the automl job is inside pipeline.
        """

        # If the automl job is inside pipeline job and it's a binding, by pass it to backend.
        if inside_pipeline and is_data_binding_expression(str(input)):
            return input
        try:
            if os.path.isabs(input):  # absolute local path, upload, transform to remote url
                # absolute local path
                return _upload_and_generate_remote_uri(self._operation_scope, self._datastore_operations, input)
            elif ":" in input or "@" in input:  # Check for AzureML id, is there a better way?
                asset_type = AzureMLResourceType.DATA
                return self._orchestrators.get_asset_arm_id(input, asset_type)
            else:  # relative local path, upload, transform to remote url
                local_path = Path(base_path, input).resolve()
                return _upload_and_generate_remote_uri(self._operation_scope, self._datastore_operations, local_path)
        except Exception as e:
            raise Exception(f"Supported input path value are ARM id, AzureML id, remote uri or local path. {e}")

    def _resolve_automl_job_inputs(self, job: AutoMLJob, base_path: os.PathLike, inside_pipeline) -> None:
        """This method resolves the inputs for AutoML jobs.

        :param job: the job resource entity
        :type job: AutoMLJob
        """
        if isinstance(job, AutoMLJob):
            data = job._data
            self._resolve_job_input(data.training_data.data, job._base_path)

            validation_data = data.validation_data
            if validation_data and validation_data.data:
                self._resolve_job_input(data.validation_data.data, job._base_path)

            test_data = data.test_data
            if test_data and test_data.data:
                self._resolve_job_input(data.test_data.data, job._base_path)

    def _resolve_azureml_id(self, job: Job) -> Job:
        """This method converts ARM id to name or name:version for nested entities.

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
        except Exception:
            return resolver(target, azureml_type=AzureMLResourceType.COMPUTE)

    def _resolve_job_inputs(self, entries: Iterable[Union[Input, str, bool, int, float]], base_path: str):
        """resolve job inputs as ARM id or remote url"""
        for entry in entries:
            self._resolve_job_input(entry, base_path)

    def _resolve_job_input(self, entry: Union[Input, str, bool, int, float], base_path: str) -> None:
        """resolve job input as ARM id or remote url"""

        # path can be empty if the job was created from builder functions
        if isinstance(entry, Input) and not entry.path:
            msg = "Input path can't be empty for jobs."
            raise JobException(message=msg, target=ErrorTarget.JOB, no_personal_data_message=msg)

        if (
            not isinstance(entry, Input)
            or is_ARM_id_for_resource(entry.path)
            or is_url(entry.path)
            or is_data_binding_expression(entry.path)  # literal value but set mode in pipeline yaml
        ):  # Literal value, ARM id or remote url. Pass through
            return
        try:
            if os.path.isabs(entry.path):  # absolute local path, upload, transform to remote url
                if entry.type == AssetTypes.URI_FOLDER and not os.path.isdir(entry.path):
                    raise JobException(
                        messge="There is no dir on target path: {}".format(entry.path),
                        target=ErrorTarget.JOB,
                        no_personal_data_message="There is no dir on target path",
                    )
                elif entry.type == AssetTypes.URI_FILE and not os.path.isfile(entry.path):
                    raise JobException(
                        message="There is no file on target path: {}".format(entry.path),
                        target=ErrorTarget.JOB,
                        no_personal_data_message="There is no file on target path",
                    )
                # absolute local path
                entry.path = _upload_and_generate_remote_uri(
                    self._operation_scope,
                    self._datastore_operations,
                    entry.path,
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
                local_path = Path(base_path, entry.path).resolve()
                entry.path = _upload_and_generate_remote_uri(
                    self._operation_scope,
                    self._datastore_operations,
                    local_path,
                )
                # TODO : Move this part to a common place
                if entry.type == AssetTypes.URI_FOLDER and entry.path and not entry.path.endswith("/"):
                    entry.path = entry.path + "/"
        except Exception as e:
            raise JobException(
                message=f"Supported input path value are ARM id, AzureML id, remote uri or local path.\n"
                f"Met {type(e)}:\n{e}",
                target=ErrorTarget.JOB,
                no_personal_data_message="Supported input path value are ARM id, AzureML id, remote uri or local path.",
                error=e,
            )

    def _resolve_job_inputs_arm_id(self, job: Job) -> None:
        try:
            inputs: Dict[str, Union[Input, str, bool, int, float]] = job.inputs
            for _, entry in inputs.items():
                if not isinstance(entry, Input) or is_url(entry.path):  # Literal value or remote url
                    continue
                else:  # ARM id
                    entry.path = self._orchestrators.resolve_azureml_id(entry.path)

        except AttributeError:
            # If the job object doesn't have "inputs" attribute, we don't need to resolve. E.g. AutoML jobs
            pass

    def _resolve_arm_id_or_azureml_id(self, job: Job, resolver: Callable) -> Job:
        """Resolve arm_id for a given job"""
        # TODO: this will need to be parallelized when multiple tasks
        # are required. Also consider the implications for dependencies.

        if isinstance(job, _BaseJob):
            job.compute = self._resolve_compute_id(resolver, job.compute)
        elif isinstance(job, CommandJob):
            job = self._resolve_arm_id_for_command_job(job, resolver)
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
            raise JobException(
                message=msg,
                target=ErrorTarget.JOB,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return job

    def _resolve_arm_id_for_command_job(self, job: Job, resolver: Callable) -> Job:
        """Resolve arm_id for CommandJob"""
        if job.code is not None and not is_ARM_id_for_resource(job.code, AzureMLResourceType.CODE):
            job.code = resolver(
                Code(base_path=job._base_path, path=job.code),
                azureml_type=AzureMLResourceType.CODE,
            )
        job.environment = resolver(job.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        job.compute = self._resolve_compute_id(resolver, job.compute)
        return job

    def _resolve_arm_id_for_parallel_job(self, job: Job, resolver: Callable) -> Job:
        """Resolve arm_id for ParallelJob"""
        if job.code is not None and not is_ARM_id_for_resource(job.code, AzureMLResourceType.CODE):
            job.code = resolver(
                Code(base_path=job._base_path, path=job.code),
                azureml_type=AzureMLResourceType.CODE,
            )
        job.environment = resolver(job.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        job.compute = self._resolve_compute_id(resolver, job.compute)
        return job

    def _resolve_arm_id_for_sweep_job(self, job: Job, resolver: Callable) -> Job:
        """Resolve arm_id for SweepJob"""
        if job.trial.code is not None and not is_ARM_id_for_resource(job.trial.code, AzureMLResourceType.CODE):
            job.trial.code = resolver(
                Code(base_path=job._base_path, path=job.trial.code),
                azureml_type=AzureMLResourceType.CODE,
            )
        job.trial.environment = resolver(job.trial.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        job.compute = self._resolve_compute_id(resolver, job.compute)
        return job

    def _resolve_arm_id_for_automl_job(self, job: Job, resolver: Callable, inside_pipeline: bool) -> Job:
        """Resolve arm_id for AutoMLJob"""
        # AutoML does not have dependency uploads. Only need to resolve reference to arm id.

        # automl node in pipeline has optional compute
        if inside_pipeline and job.compute is None:
            return job
        job.compute = resolver(job.compute, azureml_type=AzureMLResourceType.COMPUTE)
        return job

    def _resolve_arm_id_for_pipeline_job(self, pipeline_job: "PipelineJob", resolver: Callable) -> Job:
        """Resolve arm_id for pipeline_job"""
        # validate before resolve arm ids
        # if pipeline_job has arm_id, it should be loaded from remote, then no validation is needed
        if not pipeline_job.id:
            pipeline_job._validate()

        # Get top-level job compute
        self._get_job_compute_id(pipeline_job, resolver)

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
        if pipeline_job.jobs:

            for key, job_instance in pipeline_job.jobs.items():
                if isinstance(job_instance, AutoMLJob):
                    self._resolve_arm_id_for_automl_job(job_instance, resolver, inside_pipeline=True)
                elif isinstance(job_instance, (Command, Sweep, Parallel)):
                    # Get the default for the specific job type
                    if (
                        isinstance(job_instance.component, (CommandComponent, ParallelComponent))
                        and job_instance.component._is_anonymous
                        and not job_instance.component.display_name
                    ):
                        job_instance.component.display_name = key

                    # Get compute for each job
                    self._get_job_compute_id(job_instance, resolver)

                    # set default code & environment for component
                    self._set_defaults_to_component(job_instance.component, pipeline_job.settings)

                    # Get the component id for each job's component
                    job_instance._component = resolver(
                        job_instance.trial if isinstance(job_instance, Sweep) else job_instance.component,
                        azureml_type=AzureMLResourceType.COMPONENT,
                    )
                else:
                    msg = f"Non supported job type in Pipeline jobs: {type(job_instance)}"
                    raise JobException(
                        message=msg,
                        target=ErrorTarget.JOB,
                        no_personal_data_message=msg,
                        error_category=ErrorCategory.USER_ERROR,
                    )

        return pipeline_job

    def _get_job_compute_id(self, job: Union[Job, Command], resolver: Callable) -> None:
        job.compute = resolver(job.compute, azureml_type=AzureMLResourceType.COMPUTE)

    def _append_tid_to_studio_url(self, job: Job) -> None:
        """Appends the user's tenant ID to the end of the studio URL so the UI knows against which tenant to authenticate"""
        try:
            studio_endpoint = job.services.get("Studio", None)
            studio_url = studio_endpoint.endpoint
            cloud_details = _get_cloud_details()
            cloud_details = _get_cloud_details()
            default_scopes = resource_to_scopes(cloud_details.get(ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT))
            module_logger.debug(f"default_scopes used: `{default_scopes}`\n")
            # Extract the tenant id from the credential using PyJWT
            decode = jwt.decode(
                self._credential.get_token(*default_scopes).token,
                options={"verify_signature": False, "verify_aud": False},
            )
            tid = decode["tid"]
            formatted_tid = TID_FMT.format(tid)
            studio_endpoint.endpoint = studio_url + formatted_tid
        except Exception:
            module_logger.info("Proceeding with no tenant id appended to studio URL\n")

    def _set_defaults_to_component(self, component: Union[str, Component], settings: PipelineJobSettings):
        """Set default code&environment to component if not specified."""
        if isinstance(component, (CommandComponent, ParallelComponent)):
            # TODO: do we have no place to set default code & environment?
            pass

    def _set_headers_with_user_aml_token(self, kwargs) -> Dict[str, str]:
        cloud_details = _get_cloud_details()
        azure_ml_scopes = resource_to_scopes(cloud_details.get(ENDPOINT_URLS.AML_RESOURCE_ID))
        module_logger.debug(f"azure_ml_scopes used: `{azure_ml_scopes}`\n")
        aml_token = self._credential.get_token(*azure_ml_scopes).token
        headers = kwargs.pop("headers", {})
        headers["x-azureml-token"] = aml_token
        kwargs["headers"] = headers
