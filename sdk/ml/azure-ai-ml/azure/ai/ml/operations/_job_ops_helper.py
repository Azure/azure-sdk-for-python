# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import re
import sys
import time
import json
import os
import subprocess

from typing import Dict, Iterable, Optional, List, Union

from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.ai.ml.operations._run_operations import RunOperations
from azure.ai.ml.operations._dataset_dataplane_operations import DatasetDataplaneOperations
from azure.ai.ml.operations._model_dataplane_operations import ModelDataplaneOperations
from azure.ai.ml._utils.utils import create_session_with_retry, download_text_from_url
from azure.ai.ml.operations._run_history_constants import RunHistoryConstants, JobStatus
from azure.ai.ml._restclient.v2021_10_01.models import JobBaseData
from azure.ai.ml._restclient.v2022_02_01_preview.models import DataType, ModelType
from azure.ai.ml.constants import GitProperties, JobType, JobLogPattern
from azure.ai.ml._artifacts._artifact_utilities import get_datastore_info, list_logs_in_datastore
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    JobType as RestJobType,
)
from azure.ai.ml._restclient.runhistory.models import (
    PaginatedRunList,
    RunDetails,
    Run,
    TypedAssetReference,
)
from azure.ai.ml.entities._job.base_job import _BaseJob
from azure.ai.ml._ml_exceptions import JobException, ErrorCategory, ErrorTarget

STATUS_KEY = "status"

module_logger = logging.getLogger(__name__)


def _get_sorted_filtered_logs(
    logs_dict: dict, job_type: str, processed_logs: dict = {}, only_streamable=True
) -> List[str]:
    """Filters log file names, sorts, and returns list starting with where we left off last iteration.
    :param run_details:
    :type run_details: dict
    :param processed_logs: dictionary tracking the state of how many lines of each file have been written out
    :type processed_logs: dict[str, int]
    :param job_type: the job type to filter log files
    :type job_type: str
    :return:
    :rtype: list[str]
    """
    # First, attempt to read logs in new Common Runtime form
    output_logs_pattern = (
        JobLogPattern.COMMON_RUNTIME_STREAM_LOG_PATTERN
        if only_streamable
        else JobLogPattern.COMMON_RUNTIME_ALL_USER_LOG_PATTERN
    )
    logs = [x for x in logs_dict if re.match(output_logs_pattern, x)]

    # fall back to legacy log format
    if logs is None or len(logs) == 0:
        job_type = job_type.lower()
        if job_type in JobType.COMMAND:
            output_logs_pattern = JobLogPattern.COMMAND_JOB_LOG_PATTERN
        elif job_type in JobType.PIPELINE:
            output_logs_pattern = JobLogPattern.PIPELINE_JOB_LOG_PATTERN
        elif job_type in JobType.SWEEP:
            output_logs_pattern = JobLogPattern.SWEEP_JOB_LOG_PATTERN

    logs = [x for x in logs_dict if re.match(output_logs_pattern, x)]
    logs.sort()
    previously_printed_index = 0
    for i, v in enumerate(logs):
        if processed_logs.get(v):
            previously_printed_index = i
        else:
            break
    # Slice inclusive from the last printed log (can be updated before printing new files)
    return logs[previously_printed_index:]


def _incremental_print(log, processed_logs, current_log_name, fileout) -> None:
    """Incremental print.
    :param log:
    :type log: str
    :param processed_logs: The record of how many lines have been written for each log file
    :type log: dict[str, int]
    :param current_log_name: the file name being read out, used in header writing and accessing processed_logs
    :type current_log_name: str
    :param fileout:
    :type fileout: TestIOWrapper
    """
    lines = log.splitlines()
    doc_length = len(lines)
    if doc_length == 0:
        # If a file is empty, skip writing out.
        # This addresses issue where batch endpoint jobs can create log files before they are needed.
        return
    previous_printed_lines = processed_logs.get(current_log_name, 0)
    # when a new log is first being written to console, print spacing and label
    if previous_printed_lines == 0:
        fileout.write("\n")
        fileout.write("Streaming " + current_log_name + "\n")
        fileout.write("=" * (len(current_log_name) + 10) + "\n")
        fileout.write("\n")
    # otherwise, continue to log the file where we left off
    for line in lines[previous_printed_lines:]:
        fileout.write(line + "\n")
    # update state to record number of lines written for this log file
    processed_logs[current_log_name] = doc_length


def _get_last_log_primary_instance(logs):
    """Return last log for primary instance.
    :param logs:
    :type logs: builtin.list
    :return: Returns the last log primary instance.
    :rtype:
    """
    primary_ranks = ["rank_0", "worker_0"]
    rank_match_re = re.compile(r"(.*)_(.*?_.*?)\.txt")
    last_log_name = logs[-1]

    last_log_match = rank_match_re.match(last_log_name)
    if not last_log_match:
        return last_log_name

    last_log_prefix = last_log_match.group(1)
    matching_logs = sorted(filter(lambda x: x.startswith(last_log_prefix), logs))

    # we have some specific ranks that denote the primary, use those if found
    for log_name in matching_logs:
        match = rank_match_re.match(log_name)
        if not match:
            continue
        if match.group(2) in primary_ranks:
            return log_name

    # no definitively primary instance, just return the highest sorted
    return matching_logs[0]


def _wait_before_polling(current_seconds):
    if current_seconds < 0:
        msg = "current_seconds must be positive"
        raise JobException(
            message=msg, target=ErrorTarget.JOB, no_personal_data_message=msg, error_category=ErrorCategory.USER_ERROR
        )
    import math

    # Sigmoid that tapers off near the_get_logs max at ~ 3 min
    duration = RunHistoryConstants._WAIT_COMPLETION_POLLING_INTERVAL_MAX / (
        1.0 + 100 * math.exp(-current_seconds / 20.0)
    )
    return max(RunHistoryConstants._WAIT_COMPLETION_POLLING_INTERVAL_MIN, duration)


def list_logs(run_operations: RunOperations, job_resource: JobBaseData):
    details: RunDetails = run_operations.get_run_details(job_resource.name)
    logs_dict = details.log_files
    keys = _get_sorted_filtered_logs(logs_dict, job_resource.properties.job_type)
    return {key: logs_dict[key] for key in keys}


def stream_logs_until_completion(
    run_operations: RunOperations,
    job_resource: JobBaseData,
    datastore_operations: DatastoreOperations = None,
    raise_exception_on_failed_job=True,
) -> None:
    """Stream the experiment run output to the specified file handle.
    By default the the file handle points to stdout.
    :param run_operations: The run history operations class.
    :type run_operations: RunOperations
    :param job_resource: The job to stream
    :type job_resource: JobBaseData
    :param datastore_operations: Optional, the datastore operations class, used to get logs from datastore
    :type datastore_operations: Optional[DatastoreOperations]
    :param raise_exception_on_failed_job: Should this method fail if job fails
    :type raise_exception_on_failed_job: Boolean
    :return:
    :rtype: None
    """
    job_type = job_resource.properties.job_type
    job_name = job_resource.name
    studio_endpoint = job_resource.properties.services.get("Studio", None)
    studio_endpoint = studio_endpoint.endpoint if studio_endpoint else None
    file_handle = sys.stdout
    ds_properties = None
    prefix = None
    if (
        hasattr(job_resource.properties, "outputs")
        and job_resource.properties.job_type != RestJobType.AUTO_ML
        and datastore_operations
    ):
        # Get default output location

        default_output = (
            job_resource.properties.outputs.get("default", None) if job_resource.properties.outputs else None
        )
        is_uri_folder = default_output and default_output.job_output_type == DataType.URI_FOLDER
        if is_uri_folder:
            output_uri = default_output.uri
            # Parse the uri format
            output_uri = output_uri.split("datastores/")[1]
            datastore_name, prefix = output_uri.split("/", 1)
            ds_properties = get_datastore_info(datastore_operations, datastore_name)

    try:
        file_handle.write("RunId: {}\n".format(job_name))
        file_handle.write("Web View: {}\n".format(studio_endpoint))

        _current_details: RunDetails = run_operations.get_run_details(job_name)
        session = create_session_with_retry()

        processed_logs = {}

        poll_start_time = time.time()
        while (
            _current_details.status in RunHistoryConstants.IN_PROGRESS_STATUSES
            or _current_details.status == JobStatus.FINALIZING
        ):
            file_handle.flush()
            time.sleep(_wait_before_polling(time.time() - poll_start_time))
            _current_details: RunDetails = run_operations.get_run_details(job_name)  # TODO use FileWatcher
            if job_type.lower() in JobType.PIPELINE:
                legacy_folder_name = "/logs/azureml/"
            else:
                legacy_folder_name = "/azureml-logs/"
            _current_logs_dict = (
                list_logs_in_datastore(ds_properties, prefix=prefix, legacy_log_folder_name=legacy_folder_name)
                if ds_properties is not None
                else _current_details.log_files
            )
            # Get the list of new logs available after filtering out the processed ones
            available_logs = _get_sorted_filtered_logs(_current_logs_dict, job_type, processed_logs)
            content = ""
            for current_log in available_logs:
                content = download_text_from_url(
                    _current_logs_dict[current_log],
                    session,
                    timeout=RunHistoryConstants._DEFAULT_GET_CONTENT_TIMEOUT,
                )

                _incremental_print(content, processed_logs, current_log, file_handle)

            # TODO: Temporary solution to wait for all the logs to be printed in the finalizing state.
            if (
                _current_details.status not in RunHistoryConstants.IN_PROGRESS_STATUSES
                and _current_details.status == JobStatus.FINALIZING
                and "The activity completed successfully. Finalizing run..." in content
            ):
                break

        file_handle.write("\n")
        file_handle.write("Execution Summary\n")
        file_handle.write("=================\n")
        file_handle.write("RunId: {}\n".format(job_name))
        file_handle.write("Web View: {}\n".format(studio_endpoint))

        warnings = _current_details.warnings
        if warnings:
            messages = [x.message for x in warnings if x.message]
            if len(messages) > 0:
                file_handle.write("\nWarnings:\n")
                for message in messages:
                    file_handle.write(message + "\n")
                file_handle.write("\n")

        if _current_details.status == JobStatus.FAILED:
            error = (
                _current_details.error.as_dict()
                if _current_details.error
                else "Detailed error not set on the Run. Please check the logs for details."
            )
            # If we are raising the error later on, so we don't double print.
            if not raise_exception_on_failed_job:
                file_handle.write("\nError:\n")
                file_handle.write(json.dumps(error, indent=4))
                file_handle.write("\n")
            else:
                raise JobException(
                    message="Exception : \n {} ".format(json.dumps(error, indent=4)),
                    target=ErrorTarget.JOB,
                    no_personal_data_message="Exception raised on failed job.",
                )

        file_handle.write("\n")
        file_handle.flush()
    except KeyboardInterrupt:
        error_message = (
            "The output streaming for the run interrupted.\n"
            "But the run is still executing on the compute target. \n"
            "Details for canceling the run can be found here: "
            "https://aka.ms/aml-docs-cancel-run"
        )
        raise JobException(message=error_message, target=ErrorTarget.JOB, no_personal_data_message=error_message)


def get_git_properties() -> Dict[str, str]:
    """
    Gather Git tracking info from the local environment.

    :return: Properties dictionary.
    :rtype: dict
    """

    def _clean_git_property_bool(value) -> Optional[bool]:
        if value is None:
            return None
        else:
            return str(value).strip().lower() in ["true", "1"]

    def _clean_git_property_str(value) -> Optional[str]:
        if value is None:
            return None
        else:
            return str(value).strip() or None

    def _run_git_cmd(args) -> Optional[str]:
        """Return the output of running git with arguments, or None if it fails."""
        try:
            with open(os.devnull, "wb") as devnull:
                return subprocess.check_output(["git"] + list(args), stderr=devnull).decode()
        except KeyboardInterrupt:
            raise
        except BaseException:
            return None

    # Check for environment variable overrides.
    repository_uri = os.environ.get(GitProperties.ENV_REPOSITORY_URI, None)
    branch = os.environ.get(GitProperties.ENV_BRANCH, None)
    commit = os.environ.get(GitProperties.ENV_COMMIT, None)
    dirty = os.environ.get(GitProperties.ENV_DIRTY, None)
    build_id = os.environ.get(GitProperties.ENV_BUILD_ID, None)
    build_uri = os.environ.get(GitProperties.ENV_BUILD_URI, None)

    is_git_repo = _run_git_cmd(["rev-parse", "--is-inside-work-tree"])
    if _clean_git_property_bool(is_git_repo):
        repository_uri = repository_uri or _run_git_cmd(["ls-remote", "--get-url"])
        branch = branch or _run_git_cmd(["symbolic-ref", "--short", "HEAD"])
        commit = commit or _run_git_cmd(["rev-parse", "HEAD"])
        dirty = dirty or _run_git_cmd(["status", "--porcelain", "."]) and True

    # Parsing logic.
    repository_uri = _clean_git_property_str(repository_uri)
    commit = _clean_git_property_str(commit)
    branch = _clean_git_property_str(branch)
    dirty = _clean_git_property_bool(dirty)
    build_id = _clean_git_property_str(build_id)
    build_uri = _clean_git_property_str(build_uri)

    # Return with appropriate labels.
    properties = {}

    if repository_uri is not None:
        properties[GitProperties.PROP_MLFLOW_GIT_REPO_URL] = repository_uri

    if branch is not None:
        properties[GitProperties.PROP_MLFLOW_GIT_BRANCH] = branch

    if commit is not None:
        properties[GitProperties.PROP_MLFLOW_GIT_COMMIT] = commit

    if dirty is not None:
        properties[GitProperties.PROP_DIRTY] = str(dirty)

    if build_id is not None:
        properties[GitProperties.PROP_BUILD_ID] = build_id

    if build_uri is not None:
        properties[GitProperties.PROP_BUILD_URI] = build_uri

    return properties


def get_job_output_uris_from_dataplane(
    job_name: str,
    run_operations: RunOperations,
    dataset_dataplane_operations: DatasetDataplaneOperations,
    model_dataplane_operations: ModelDataplaneOperations,
    output_names: Optional[Union[Iterable[str], str]] = None,
) -> Dict[str, str]:
    """Returns the output path for the given output in cloud storage of the given job.
    If no output names are given, the output paths for all outputs will be returned.
    URIs obtained from the service will be in the long-form azureml:// format.
    For example, azureml://subscriptions/<sub_id>/resource[gG]roups/<rg_name>/workspaces/<ws_name>/datastores/<ds_name>/paths/<path_on_ds>
    :return: Dictionary mapping user-defined output name to output uri
    :rtype: Dict[str, str]
    """
    run_metadata: Run = run_operations.get_run_data(job_name).run_metadata
    run_outputs: Dict[str, TypedAssetReference] = run_metadata.outputs or {}

    # Create a reverse mapping from internal asset id to user-defined output name
    asset_id_to_output_name = {v.asset_id: k for k, v in run_outputs.items()}
    if not output_names:
        # Assume all outputs are needed if no output name is provided
        output_names = run_outputs.keys()
    else:
        if isinstance(output_names, str):
            output_names = [output_names]
        output_names = [o for o in output_names if o in run_outputs]

    # Collect all output ids that correspond to data assets
    dataset_ids = [
        run_outputs[output_name].asset_id
        for output_name in output_names
        if run_outputs[output_name].type in [o.value for o in DataType]
    ]

    # Collect all output ids that correspond to models
    model_ids = [
        run_outputs[output_name].asset_id
        for output_name in output_names
        if run_outputs[output_name].type in [o.value for o in ModelType]
    ]

    output_name_to_dataset_uri = {}
    if dataset_ids:
        # Get the data paths from the service
        dataset_uris = dataset_dataplane_operations.get_batch_dataset_uris(dataset_ids)
        # Map the user-defined output name to the output uri
        # The service returns a mapping from internal asset id to output metadata, so we need the reverse map
        # defined above to get the user-defined output name from the internal asset id.
        output_name_to_dataset_uri = {asset_id_to_output_name[k]: v.uri for k, v in dataset_uris.values.items()}

    # This is a repeat of the logic above for models.
    output_name_to_model_uri = {}
    if model_ids:
        model_uris = model_dataplane_operations.get_batch_model_uris(model_ids)
        output_name_to_model_uri = {asset_id_to_output_name[k]: v.path for k, v in model_uris.values.items()}

    return {**output_name_to_dataset_uri, **output_name_to_model_uri}
