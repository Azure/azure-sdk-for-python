import subprocess
import io
from io import StringIO
import sys
import types
from types import SimpleNamespace

import pytest

import azure.ai.ml.operations._job_ops_helper as job_ops_helper
from azure.ai.ml._restclient.v2022_02_01_preview.models import DataType, ModelType
from azure.ai.ml.constants._common import GitProperties
from azure.ai.ml.constants._job.job import JobLogPattern, JobType
from azure.ai.ml.exceptions import JobException, ErrorCategory
from azure.ai.ml.operations._job_ops_helper import (
    _get_last_log_primary_instance,
    _get_sorted_filtered_logs,
    _wait_before_polling,
    get_git_properties,
    get_job_output_uris_from_dataplane,
    has_pat_token,
    stream_logs_until_completion,
    _incremental_print,
)
from azure.ai.ml.operations._run_history_constants import JobStatus, RunHistoryConstants


def test_get_sorted_filtered_logs_common_runtime_no_fallback(monkeypatch):
    # Ensure COMMON_RUNTIME_STREAM_LOG_PATTERN matches our test log so fallback is not triggered.
    monkeypatch.setattr(JobLogPattern, "COMMON_RUNTIME_STREAM_LOG_PATTERN", r"^runtime_log\.txt$")

    logs = ["runtime_log.txt", "other_log.txt"]
    # processed_logs contains the matching log so the previously_printed_index should point to it.
    processed_logs = {"runtime_log.txt": 1}

    result = _get_sorted_filtered_logs(logs, job_type="command", processed_logs=processed_logs, only_streamable=True)

    # Since the only matching log is already in processed_logs, the full list of filtered logs is returned
    # starting from that log.
    assert result == ["runtime_log.txt"]


def test_get_sorted_filtered_logs_legacy_command_pattern(monkeypatch):
    # Force the initial COMMON_RUNTIME_STREAM_LOG_PATTERN to match nothing so fallback is taken.
    monkeypatch.setattr(JobLogPattern, "COMMON_RUNTIME_STREAM_LOG_PATTERN", r"^$")
    monkeypatch.setattr(JobType, "COMMAND", ["command"])
    monkeypatch.setattr(JobLogPattern, "COMMAND_JOB_LOG_PATTERN", r"^cmd_.*")

    logs = ["cmd_log1.txt", "other_log.txt"]

    result = _get_sorted_filtered_logs(logs, job_type="command", processed_logs=None, only_streamable=True)

    # After falling back, only the command log should match the COMMAND_JOB_LOG_PATTERN.
    assert result == ["cmd_log1.txt"]


def test_get_sorted_filtered_logs_legacy_pipeline_vs_sweep_patterns(monkeypatch):
    # Ensure no common-runtime logs so legacy patterns are used.
    monkeypatch.setattr(JobLogPattern, "COMMON_RUNTIME_STREAM_LOG_PATTERN", r"^$")
    monkeypatch.setattr(JobType, "COMMAND", ["command"])
    monkeypatch.setattr(JobType, "PIPELINE", ["pipeline"])
    monkeypatch.setattr(JobType, "SWEEP", ["sweep"])
    monkeypatch.setattr(JobLogPattern, "PIPELINE_JOB_LOG_PATTERN", r"^pipe_.*")
    monkeypatch.setattr(JobLogPattern, "SWEEP_JOB_LOG_PATTERN", r"^sweep_.*")

    logs = ["pipe_log.txt", "sweep_log.txt", "other.txt"]

    # Pipeline job_type should pick PIPELINE_JOB_LOG_PATTERN.
    pipeline_result = _get_sorted_filtered_logs(logs, job_type="pipeline", processed_logs=None, only_streamable=True)
    assert pipeline_result == ["pipe_log.txt"]

    # Sweep job_type should pick SWEEP_JOB_LOG_PATTERN.
    sweep_result = _get_sorted_filtered_logs(logs, job_type="sweep", processed_logs=None, only_streamable=True)
    assert sweep_result == ["sweep_log.txt"]


def test_get_sorted_filtered_logs_processed_logs_indexing(monkeypatch):
    # Make all logs match the pattern so ordering and processed_logs behavior are exercised.
    monkeypatch.setattr(JobLogPattern, "COMMON_RUNTIME_STREAM_LOG_PATTERN", r"^log_.*")

    logs = ["log_a.txt", "log_b.txt", "log_c.txt"]
    # processed_logs contains the first two logs, so the function should start from the last processed.
    processed_logs = {"log_a.txt": 10, "log_b.txt": 20}

    result = _get_sorted_filtered_logs(logs, job_type="command", processed_logs=processed_logs, only_streamable=True)

    # Since log_b is the last processed one, we expect to start from it and include log_c.
    assert result == ["log_b.txt", "log_c.txt"]


def test_get_last_log_primary_instance_no_regex_match():
    # Last log does not match the expected pattern, so it should be returned as-is.
    logs = ["some_log.txt", "another.log"]

    result = _get_last_log_primary_instance(logs)

    assert result == "another.log"


def test_get_last_log_primary_instance_primary_rank_found():
    logs = [
        "task_rank_1.txt",
        "task_rank_0.txt",  # primary rank according to primary_ranks list
        "task_worker_1.txt",
    ]

    result = _get_last_log_primary_instance(logs)

    # The function should prefer the log with the primary rank suffix.
    assert result == "task_rank_0.txt"


def test_get_last_log_primary_instance_no_primary_rank_uses_first_matching_sorted():
    logs = [
        "alpha_rank_2.txt",
        "alpha_rank_3.txt",
        "alpha_rank_4.txt",
    ]

    result = _get_last_log_primary_instance(logs)

    # No primary rank is present, so the first of the matching logs in sorted order is returned.
    assert result == "alpha_rank_2.txt"


def test_get_git_properties_not_git_repo_returns_empty_dict(monkeypatch):
    def _raise_exception(*args, **kwargs):
        raise Exception("not a git repo")

    monkeypatch.setattr(subprocess, "check_output", _raise_exception)

    monkeypatch.delenv(GitProperties.ENV_REPOSITORY_URI, raising=False)
    monkeypatch.delenv(GitProperties.ENV_BRANCH, raising=False)
    monkeypatch.delenv(GitProperties.ENV_COMMIT, raising=False)
    monkeypatch.delenv(GitProperties.ENV_DIRTY, raising=False)
    monkeypatch.delenv(GitProperties.ENV_BUILD_ID, raising=False)
    monkeypatch.delenv(GitProperties.ENV_BUILD_URI, raising=False)

    properties = get_git_properties()

    assert properties == {}


def test_get_git_properties_git_repo_and_dirty_true(monkeypatch):
    outputs = [
        b"true\n",  # rev-parse --is-inside-work-tree
        b"https://example.com/repo.git\n",  # ls-remote --get-url
        b"main\n",  # symbolic-ref --short HEAD
        b"abcdef123456\n",  # rev-parse HEAD
        b" M file\n",  # status --porcelain .
    ]

    def _fake_check_output(args, stderr=None):  # pylint: disable=unused-argument
        assert args[0] == "git"
        return outputs.pop(0)

    monkeypatch.setattr(subprocess, "check_output", _fake_check_output)

    monkeypatch.delenv(GitProperties.ENV_REPOSITORY_URI, raising=False)
    monkeypatch.delenv(GitProperties.ENV_BRANCH, raising=False)
    monkeypatch.delenv(GitProperties.ENV_COMMIT, raising=False)
    monkeypatch.delenv(GitProperties.ENV_DIRTY, raising=False)
    monkeypatch.setenv(GitProperties.ENV_BUILD_ID, "build-123")
    monkeypatch.setenv(GitProperties.ENV_BUILD_URI, "https://build.example.com/123")

    properties = get_git_properties()

    assert properties[GitProperties.PROP_MLFLOW_GIT_REPO_URL] == "https://example.com/repo.git"
    assert properties[GitProperties.PROP_MLFLOW_GIT_BRANCH] == "main"
    assert properties[GitProperties.PROP_MLFLOW_GIT_COMMIT] == "abcdef123456"
    assert properties[GitProperties.PROP_DIRTY] == "True"
    assert properties[GitProperties.PROP_BUILD_ID] == "build-123"
    assert properties[GitProperties.PROP_BUILD_URI] == "https://build.example.com/123"


def test_get_git_properties_keyboard_interrupt_propagates(monkeypatch):
    def _raise_keyboard_interrupt(*args, **kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr(subprocess, "check_output", _raise_keyboard_interrupt)

    with pytest.raises(KeyboardInterrupt):
        get_git_properties()


def test_has_pat_token_none_returns_false():
    assert has_pat_token(None) is False


def test_has_pat_token_detects_token_in_both_patterns():
    url1 = "https://dev.azure.com/mypattoken@organization/project/_git/repo"
    url2 = "https://mypattoken@dev.azure.com/organization/project/_git/repo"

    assert has_pat_token(url1) is True
    assert has_pat_token(url2) is True


def test_has_pat_token_without_token_returns_false():
    url = "https://dev.azure.com/organization/project/_git/repo"

    assert has_pat_token(url) is False


class DummyService:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint


class DummyWarning:
    def __init__(self, message: str):
        self.message = message


class DummyError:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data


class DummyRunDetails:
    def __init__(self, status, log_files=None, warnings=None, error=None):
        self.status = status
        self.log_files = log_files or {}
        self.warnings = warnings
        self.error = error


class DummyOutputsProps:
    def __init__(self, job_type, services, properties, outputs):
        self.job_type = job_type
        self.services = services
        self.properties = properties
        self.outputs = outputs


class DummyPropsNoOutputs:
    def __init__(self, job_type, services, properties):
        self.job_type = job_type
        self.services = services
        self.properties = properties


class DummyOutput:
    def __init__(self, job_output_type, uri):
        self.job_output_type = job_output_type
        self.uri = uri


class DummyJobResource:
    def __init__(self, name, props):
        self.name = name
        self.properties = props


class DummyRunOperations:
    def __init__(self, details_sequence):
        self._subscription_id = "sub-id"
        self._resource_group_name = "rg-name"
        self._details_sequence = list(details_sequence)

    def get_run_details(self, name):  # pylint: disable=unused-argument
        return self._details_sequence.pop(0)


def _common_monkeypatch_streaming(monkeypatch, log_content="some log line"):
    # Avoid real sleeping
    monkeypatch.setattr(job_ops_helper.time, "sleep", lambda _: None)

    # Simple stdout capture via replacing sys.stdout in the module
    fake_stdout = io.StringIO()
    monkeypatch.setattr(job_ops_helper, "sys", types.SimpleNamespace(stdout=fake_stdout))

    # Simplify log handling
    monkeypatch.setattr(job_ops_helper, "_get_sorted_filtered_logs", lambda logs, *_, **__: list(logs.keys()))

    # Avoid real HTTP calls
    monkeypatch.setattr(
        job_ops_helper,
        "create_requests_pipeline_with_retry",
        lambda requests_pipeline: "pipeline-with-retries",
    )
    monkeypatch.setattr(
        job_ops_helper,
        "download_text_from_url",
        lambda url, pipeline, timeout: log_content,
    )

    return fake_stdout


def test_stream_logs_feature_store_azureml_with_outputs(monkeypatch):
    fake_stdout = _common_monkeypatch_streaming(monkeypatch)

    captured_datastore_args = {}

    def fake_get_datastore_info(datastore_operations, datastore_name):  # pylint: disable=unused-argument
        captured_datastore_args["datastore_name"] = datastore_name
        return {"name": datastore_name}

    monkeypatch.setattr(job_ops_helper, "get_datastore_info", fake_get_datastore_info)
    monkeypatch.setattr(
        job_ops_helper,
        "list_logs_in_datastore",
        lambda ds_props, prefix, legacy_log_folder_name: {"log1": "https://log-url"},
    )

    services = {"Studio": DummyService(endpoint="https://original-studio")}
    properties = {
        "azureml.FeatureStoreJobType": True,
        "azureml.FeatureStoreName": "fs-name",
        "azureml.FeatureSetName": "fset-name",
        "azureml.FeatureSetVersion": "1",
    }
    outputs = {
        "default": DummyOutput(
            job_output_type=DataType.URI_FOLDER,
            uri="azureml://datastores/mydatastore/paths/some/path",
        )
    }
    props = DummyOutputsProps(job_type="Command", services=services, properties=properties, outputs=outputs)
    job = DummyJobResource(name="job-123", props=props)

    details_sequence = [
        DummyRunDetails(status=JobStatus.RUNNING, log_files={"log1": "https://log-url"}, warnings=[DummyWarning("warn-msg")]),
        DummyRunDetails(status=JobStatus.COMPLETED, log_files={"log1": "https://log-url"}, warnings=[DummyWarning("warn-msg")]),
    ]
    run_ops = DummyRunOperations(details_sequence)

    stream_logs_until_completion(
        run_operations=run_ops,
        job_resource=job,
        datastore_operations=object(),
        raise_exception_on_failed_job=True,
        requests_pipeline=object(),
    )

    output = fake_stdout.getvalue()
    assert "featureStore/fs-name/featureSets/fset-name/1/matJobs/jobs/job-123" in output
    assert "Warnings:" in output
    assert "warn-msg" in output
    assert captured_datastore_args["datastore_name"] == "mydatastore"


def test_stream_logs_feature_store_plain_no_outputs(monkeypatch):
    fake_stdout = _common_monkeypatch_streaming(monkeypatch)

    services = {"Studio": DummyService(endpoint="https://original-studio")}
    properties = {
        "FeatureStoreJobType": True,
        "FeatureStoreName": "plain-fs",
        "FeatureSetName": "plain-fset",
        "FeatureSetVersion": "2",
    }
    props = DummyPropsNoOutputs(job_type="command", services=services, properties=properties)
    job = DummyJobResource(name="job-456", props=props)

    details_sequence = [
        DummyRunDetails(status=JobStatus.RUNNING, log_files={}, warnings=[]),
        DummyRunDetails(status=JobStatus.COMPLETED, log_files={}, warnings=[]),
    ]
    run_ops = DummyRunOperations(details_sequence)

    stream_logs_until_completion(
        run_operations=run_ops,
        job_resource=job,
        datastore_operations=None,
        raise_exception_on_failed_job=True,
        requests_pipeline=object(),
    )

    output = fake_stdout.getvalue()
    assert "featureStore/plain-fs/featureSets/plain-fset/2/matJobs/jobs/job-456" in output
    # No warnings section should be printed when warnings list is empty
    assert "Warnings:" not in output


def test_stream_logs_non_feature_store_uses_existing_endpoint(monkeypatch):
    fake_stdout = _common_monkeypatch_streaming(monkeypatch)

    studio_url = "https://existing-studio-url"
    services = {"Studio": DummyService(endpoint=studio_url)}
    properties = {}
    props = DummyOutputsProps(job_type="Pipeline", services=services, properties=properties, outputs=None)
    job = DummyJobResource(name="job-789", props=props)

    details_sequence = [
        DummyRunDetails(status=JobStatus.RUNNING, log_files={}, warnings=None),
        DummyRunDetails(status=JobStatus.COMPLETED, log_files={}, warnings=None),
    ]
    run_ops = DummyRunOperations(details_sequence)

    stream_logs_until_completion(
        run_operations=run_ops,
        job_resource=job,
        datastore_operations=None,
        raise_exception_on_failed_job=True,
        requests_pipeline=object(),
    )

    output = fake_stdout.getvalue()
    assert f"Web View: {studio_url}" in output
    # Ensure execution summary is printed
    assert "Execution Summary" in output


class DummyTypedAssetReference:
    def __init__(self, asset_id, type_value):
        self.asset_id = asset_id
        self.type = type_value


class DummyRunMetadata:
    def __init__(self, outputs):
        self.outputs = outputs


class DummyRunData:
    def __init__(self, run_metadata):
        self.run_metadata = run_metadata


class DummyRunOperationsData:
    def __init__(self, run_data):
        self._run_data = run_data

    def get_run_data(self, job_name):
        return self._run_data


class DummyDatasetUri:
    def __init__(self, uri):
        self.uri = uri


class DummyModelUri:
    def __init__(self, path):
        self.path = path


class DummyDatasetUrisResponse:
    def __init__(self, values):
        self.values = values


class DummyModelUrisResponse:
    def __init__(self, values):
        self.values = values


class DummyDatasetDataplaneOperations:
    def __init__(self, uri_mapping):
        self._uri_mapping = uri_mapping

    def get_batch_dataset_uris(self, asset_ids):
        values = {asset_id: DummyDatasetUri(self._uri_mapping[asset_id]) for asset_id in asset_ids}
        return DummyDatasetUrisResponse(values)


class DummyModelDataplaneOperations:
    def __init__(self, path_mapping):
        self._path_mapping = path_mapping

    def get_batch_model_uris(self, asset_ids):
        values = {asset_id: DummyModelUri(self._path_mapping[asset_id]) for asset_id in asset_ids}
        return DummyModelUrisResponse(values)


def test_get_job_output_uris_all_outputs_dataset_and_model():
    dataset_type_value = list(DataType)[0].value
    model_type_value = list(ModelType)[0].value

    outputs = {
        "data_out": DummyTypedAssetReference("data-asset-id", dataset_type_value),
        "model_out": DummyTypedAssetReference("model-asset-id", model_type_value),
    }
    run_metadata = DummyRunMetadata(outputs)
    run_data = DummyRunData(run_metadata)
    run_operations = DummyRunOperationsData(run_data)

    dataset_uri_mapping = {"data-asset-id": "azureml://dataset/uri"}
    model_path_mapping = {"model-asset-id": "azureml://model/path"}

    dataset_dataplane_operations = DummyDatasetDataplaneOperations(dataset_uri_mapping)
    model_dataplane_operations = DummyModelDataplaneOperations(model_path_mapping)

    result = get_job_output_uris_from_dataplane(
        job_name="job-1",
        run_operations=run_operations,
        dataset_dataplane_operations=dataset_dataplane_operations,
        model_dataplane_operations=model_dataplane_operations,
    )

    assert result == {
        "data_out": "azureml://dataset/uri",
        "model_out": "azureml://model/path",
    }


def test_get_job_output_uris_filtered_dataset_only_and_no_model_op():
    dataset_type_value = list(DataType)[0].value

    outputs = {
        "dataset1": DummyTypedAssetReference("ds-1", dataset_type_value),
        "dataset2": DummyTypedAssetReference("ds-2", dataset_type_value),
    }
    run_metadata = DummyRunMetadata(outputs)
    run_data = DummyRunData(run_metadata)
    run_operations = DummyRunOperationsData(run_data)

    dataset_uri_mapping = {
        "ds-1": "azureml://dataset/one",
        "ds-2": "azureml://dataset/two",
    }
    dataset_dataplane_operations = DummyDatasetDataplaneOperations(dataset_uri_mapping)

    result = get_job_output_uris_from_dataplane(
        job_name="job-2",
        run_operations=run_operations,
        dataset_dataplane_operations=dataset_dataplane_operations,
        model_dataplane_operations=None,
        output_names=["dataset1", "nonexistent"],
    )

    assert result == {"dataset1": "azureml://dataset/one"}


def test_get_job_output_uris_no_outputs_returns_empty_dict():
    outputs = {}
    run_metadata = DummyRunMetadata(outputs)
    run_data = DummyRunData(run_metadata)
    run_operations = DummyRunOperationsData(run_data)

    dataset_dataplane_operations = DummyDatasetDataplaneOperations({})

    result = get_job_output_uris_from_dataplane(
        job_name="job-3",
        run_operations=run_operations,
        dataset_dataplane_operations=dataset_dataplane_operations,
        model_dataplane_operations=None,
    )

    assert result == {}


class GenDummyProps:
    def __init__(self, job_type, services=None, properties=None, outputs=None):
        self.job_type = job_type
        self.services = services or {}
        self.properties = properties or {}
        if outputs is not None:
            self.outputs = outputs


class GenDummyJobResource:
    def __init__(self, name, job_type, services=None, properties_extra=None, outputs=None):
        self.name = name
        self.properties = GenDummyProps(job_type, services=services, properties=properties_extra, outputs=outputs)


class GenDummyRunOperations:
    def __init__(self, details_sequence):
        self._details_sequence = list(details_sequence)
        self._subscription_id = "sub-id"
        self._resource_group_name = "rg-name"

    def get_run_details(self, job_name):  # pylint: disable=unused-argument
        if len(self._details_sequence) > 1:
            return self._details_sequence.pop(0)
        return self._details_sequence[0]


def test_wait_before_polling_negative_raises_job_exception():
    with pytest.raises(JobException) as ex:
        _wait_before_polling(-1.0)
    assert "current_seconds must be positive" in str(ex.value)
    assert ex.value.error_category == ErrorCategory.USER_ERROR


def test_wait_before_polling_positive_respects_min_and_max():
    small = _wait_before_polling(0.0)
    large = _wait_before_polling(1000.0)
    min_interval = int(RunHistoryConstants._WAIT_COMPLETION_POLLING_INTERVAL_MIN)
    max_interval = int(RunHistoryConstants._WAIT_COMPLETION_POLLING_INTERVAL_MAX)
    assert small >= min_interval
    assert large <= max_interval


def test_stream_logs_pipeline_finalizing_breaks_after_success(monkeypatch):
    services = {"Studio": type("S", (), {"endpoint": "https://studio"})()}
    job = GenDummyJobResource("job-pipeline", "pipeline", services=services)

    in_progress_status = RunHistoryConstants.IN_PROGRESS_STATUSES[0]
    details_in_progress = DummyRunDetails(status=in_progress_status, log_files={"log1": "http://log"})
    details_finalizing = DummyRunDetails(status=JobStatus.FINALIZING, log_files={"log1": "http://log"})
    run_ops = GenDummyRunOperations([details_in_progress, details_finalizing])

    monkeypatch.setattr(
        "azure.ai.ml.operations._job_ops_helper.create_requests_pipeline_with_retry",
        lambda requests_pipeline: object(),
    )
    monkeypatch.setattr(
        "azure.ai.ml.operations._job_ops_helper._get_sorted_filtered_logs",
        lambda logs, *_, **__: list(logs.keys()),
    )
    monkeypatch.setattr(
        "azure.ai.ml.operations._job_ops_helper.download_text_from_url",
        lambda url, pipeline, timeout: "The activity completed successfully. Finalizing run...",
    )
    monkeypatch.setattr("time.sleep", lambda x: None)

    stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stream)

    stream_logs_until_completion(run_ops, job, raise_exception_on_failed_job=True, requests_pipeline=object())

    output = stream.getvalue()
    assert "Execution Summary" in output
    assert "RunId: job-pipeline" in output


def test_stream_logs_non_pipeline_failed_prints_error_after_loop(monkeypatch):
    job = GenDummyJobResource("job-command", "command")

    in_progress_status = RunHistoryConstants.IN_PROGRESS_STATUSES[0]
    details_in_progress = DummyRunDetails(status=in_progress_status, log_files={})
    error = DummyError({"code": "TestError"})
    details_failed = DummyRunDetails(status=JobStatus.FAILED, log_files={}, error=error)
    run_ops = GenDummyRunOperations([details_in_progress, details_failed])

    monkeypatch.setattr(
        "azure.ai.ml.operations._job_ops_helper.create_requests_pipeline_with_retry",
        lambda requests_pipeline: object(),
    )
    monkeypatch.setattr(
        "azure.ai.ml.operations._job_ops_helper._get_sorted_filtered_logs",
        lambda logs, *_, **__: [],
    )
    monkeypatch.setattr("time.sleep", lambda x: None)

    stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stream)

    stream_logs_until_completion(run_ops, job, raise_exception_on_failed_job=False, requests_pipeline=object())

    output = stream.getvalue()
    assert "Error:" in output
    assert "TestError" in output


def test_stream_logs_failed_raises_job_exception_when_configured(monkeypatch):
    job = GenDummyJobResource("job-failed", "command")

    error = DummyError({"code": "AnotherError"})
    details_failed = DummyRunDetails(status=JobStatus.FAILED, log_files={}, error=error)
    run_ops = GenDummyRunOperations([details_failed])

    monkeypatch.setattr(
        "azure.ai.ml.operations._job_ops_helper.create_requests_pipeline_with_retry",
        lambda requests_pipeline: object(),
    )

    stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stream)

    with pytest.raises(JobException) as ex:
        stream_logs_until_completion(run_ops, job, raise_exception_on_failed_job=True, requests_pipeline=object())

    assert ex.value.error_category == ErrorCategory.SYSTEM_ERROR
    assert "AnotherError" in str(ex.value)


def test_stream_logs_keyboard_interrupt_raises_wrapped_job_exception(monkeypatch):
    job = GenDummyJobResource("job-interrupt", "command")

    in_progress_status = RunHistoryConstants.IN_PROGRESS_STATUSES[0]
    details_in_progress = DummyRunDetails(status=in_progress_status, log_files={})
    run_ops = GenDummyRunOperations([details_in_progress])

    monkeypatch.setattr(
        "azure.ai.ml.operations._job_ops_helper.create_requests_pipeline_with_retry",
        lambda requests_pipeline: object(),
    )
    monkeypatch.setattr(
        "azure.ai.ml.operations._job_ops_helper._get_sorted_filtered_logs",
        lambda logs, *_, **__: [],
    )

    def _raise_keyboard_interrupt(_):  # pylint: disable=unused-argument
        raise KeyboardInterrupt()

    monkeypatch.setattr("time.sleep", _raise_keyboard_interrupt)

    stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stream)

    with pytest.raises(JobException) as ex:
        stream_logs_until_completion(run_ops, job, raise_exception_on_failed_job=True, requests_pipeline=object())

    assert ex.value.error_category == ErrorCategory.USER_ERROR
    assert "output streaming for the run interrupted" in str(ex.value)


def test_get_sorted_filtered_logs_streaming_pattern(monkeypatch):
    dummy_patterns = type(
        "JobLogPattern",
        (),
        {
            "COMMON_RUNTIME_STREAM_LOG_PATTERN": r"^stream/.*",
            "COMMON_RUNTIME_ALL_USER_LOG_PATTERN": r"^stream/.*",
            "COMMAND_JOB_LOG_PATTERN": r"^legacy_command.*",
            "PIPELINE_JOB_LOG_PATTERN": r"^legacy_pipeline.*",
            "SWEEP_JOB_LOG_PATTERN": r"^legacy_sweep.*",
        },
    )
    dummy_types = type(
        "JobType",
        (),
        {"COMMAND": ["command"], "PIPELINE": ["pipeline"], "SWEEP": ["sweep"]},
    )
    monkeypatch.setattr(job_ops_helper, "JobLogPattern", dummy_patterns)
    monkeypatch.setattr(job_ops_helper, "JobType", dummy_types)
    logs = ["stream/alpha.log", "stream/beta.log"]
    result = job_ops_helper._get_sorted_filtered_logs(logs, "other")
    assert result == ["stream/alpha.log", "stream/beta.log"]


@pytest.mark.parametrize(
    "job_type_value,fallback_attr,log_name",
    [
        ("COMMAND", "COMMAND_JOB_LOG_PATTERN", "legacy_command.log"),
        ("PiPeLiNe", "PIPELINE_JOB_LOG_PATTERN", "legacy_pipeline.log"),
        ("sWeEp", "SWEEP_JOB_LOG_PATTERN", "legacy_sweep.log"),
    ],
)

def test_get_sorted_filtered_logs_fallback_patterns(monkeypatch, job_type_value, fallback_attr, log_name):
    base_patterns = {
        "COMMON_RUNTIME_STREAM_LOG_PATTERN": r"^nevermatch$",
        "COMMON_RUNTIME_ALL_USER_LOG_PATTERN": r"^nevermatch$",
        "COMMAND_JOB_LOG_PATTERN": r"^nevermatch$",
        "PIPELINE_JOB_LOG_PATTERN": r"^nevermatch$",
        "SWEEP_JOB_LOG_PATTERN": r"^nevermatch$",
    }
    base_patterns[fallback_attr] = rf"^{log_name}$"
    dummy_patterns = type("JobLogPattern", (), base_patterns)
    dummy_types = type("JobType", (), {"COMMAND": ["command"], "PIPELINE": ["pipeline"], "SWEEP": ["sweep"]})
    monkeypatch.setattr(job_ops_helper, "JobLogPattern", dummy_patterns)
    monkeypatch.setattr(job_ops_helper, "JobType", dummy_types)
    result = job_ops_helper._get_sorted_filtered_logs([log_name], job_type_value)
    assert result == [log_name]


def test_get_sorted_filtered_logs_all_user_pattern(monkeypatch):
    dummy_patterns = type(
        "JobLogPattern",
        (),
        {
            "COMMON_RUNTIME_STREAM_LOG_PATTERN": r"^stream-only$",
            "COMMON_RUNTIME_ALL_USER_LOG_PATTERN": r"^user-log$",
            "COMMAND_JOB_LOG_PATTERN": r"^nevermatch$",
            "PIPELINE_JOB_LOG_PATTERN": r"^nevermatch$",
            "SWEEP_JOB_LOG_PATTERN": r"^nevermatch$",
        },
    )
    dummy_types = type(
        "JobType",
        (),
        {"COMMAND": ["command"], "PIPELINE": ["pipeline"], "SWEEP": ["sweep"]},
    )
    monkeypatch.setattr(job_ops_helper, "JobLogPattern", dummy_patterns)
    monkeypatch.setattr(job_ops_helper, "JobType", dummy_types)
    result = job_ops_helper._get_sorted_filtered_logs(["user-log"], "other", only_streamable=False)
    assert result == ["user-log"]


def test_incremental_print_skips_empty_log():
    processed_logs = {}
    fileout = io.StringIO()

    _incremental_print("", processed_logs, "log.txt", fileout)

    assert fileout.getvalue() == ""
    assert processed_logs == {}


def test_incremental_print_writes_header_and_updates_processed():
    processed_logs = {}
    fileout = io.StringIO()
    log_name = "logfile.txt"
    header_line = "=" * (len(log_name) + 10)

    _incremental_print("first line\nsecond line", processed_logs, log_name, fileout)

    expected_output = (
        "\n"
        "Streaming logfile.txt\n"
        f"{header_line}\n"
        "\n"
        "first line\n"
        "second line\n"
    )
    assert fileout.getvalue() == expected_output
    assert processed_logs["logfile.txt"] == 2


def test_incremental_print_appends_only_unprocessed_lines():
    processed_logs = {"logfile.txt": 1}
    fileout = io.StringIO()

    _incremental_print("line1\nline2\nline3", processed_logs, "logfile.txt", fileout)

    assert fileout.getvalue() == "line2\nline3\n"
    assert processed_logs["logfile.txt"] == 3


def test_incremental_print_skips_empty_file():
    processed_logs = {}
    buffer = StringIO()
    _incremental_print("", processed_logs, "log.txt", buffer)
    assert buffer.getvalue() == ""
    assert processed_logs == {}


def test_incremental_print_writes_header_for_first_stream():
    processed_logs = {}
    buffer = StringIO()
    log_content = "line1\nline2"
    _incremental_print(log_content, processed_logs, "log.txt", buffer)
    header = "\nStreaming log.txt\n" + "=" * (len("log.txt") + 10) + "\n\n"
    body = "line1\nline2\n"
    assert buffer.getvalue() == header + body
    assert processed_logs["log.txt"] == 2


def test_incremental_print_continues_existing_stream_without_header():
    processed_logs = {"log.txt": 2}
    buffer = StringIO()
    _incremental_print("line1\nline2\nline3", processed_logs, "log.txt", buffer)
    assert buffer.getvalue() == "line3\n"
    assert processed_logs["log.txt"] == 3


def test_get_last_log_primary_instance_returns_last_when_missing_pattern():
    logs = ["alpha.txt", "beta"]
    assert _get_last_log_primary_instance(logs) == "beta"


def test_get_last_log_primary_instance_prefers_primary_rank():
    logs = ["prefix_rank_2.txt", "prefix_rank_0.txt", "prefix_rank_3.txt", "prefix_worker_0.txt"]
    assert _get_last_log_primary_instance(logs) == "prefix_rank_0.txt"


def test_get_last_log_primary_instance_returns_highest_sorted_when_no_primary_marker():
    logs = ["prefix_rank_2.txt", "prefix_rank_3.txt"]
    assert _get_last_log_primary_instance(logs) == "prefix_rank_2.txt"


def test_wait_before_polling_negative_seconds_raises_job_exception():
    with pytest.raises(JobException) as exc_info:
        _wait_before_polling(-1.0)
    assert exc_info.value.message == "current_seconds must be positive"


def test_wait_before_polling_returns_at_least_minimum_interval():
    minimum = int(RunHistoryConstants._WAIT_COMPLETION_POLLING_INTERVAL_MIN)
    result = _wait_before_polling(0.0)
    assert result >= minimum


def test_stream_logs_feature_store_with_warnings(monkeypatch):
    job_name = 'job123'
    run_details = SimpleNamespace(
        status=JobStatus.COMPLETED,
        log_files={},
        warnings=[SimpleNamespace(message='warning text')],
        error=None,
    )
    run_operations = SimpleNamespace(
        _subscription_id='sub',
        _resource_group_name='rg',
        get_run_details=lambda name: run_details,
    )
    fs_name = 'myfs'
    fset_name = 'myfset'
    fset_version = 'v1'
    job_properties = SimpleNamespace(
        job_type='pipeline',
        services={'Studio': SimpleNamespace(endpoint='https://studio.example')},
        properties={
            'azureml.FeatureStoreJobType': True,
            'azureml.FeatureStoreName': fs_name,
            'azureml.FeatureSetName': fset_name,
            'azureml.FeatureSetVersion': fset_version,
        },
        outputs={
            'default': SimpleNamespace(
                job_output_type=DataType.URI_FOLDER,
                uri='https://ml.azure.com/datastores/store/prefix',
            )
        },
    )
    job_resource = SimpleNamespace(name=job_name, properties=job_properties)
    datastore_operations = SimpleNamespace()

    datastore_called = {}

    def fake_get_datastore_info(operations, name):
        datastore_called['name'] = name
        return SimpleNamespace(name=name)

    monkeypatch.setattr(job_ops_helper, 'get_datastore_info', fake_get_datastore_info)
    monkeypatch.setattr(
        job_ops_helper,
        'create_requests_pipeline_with_retry',
        lambda requests_pipeline: requests_pipeline,
    )
    monkeypatch.setattr(job_ops_helper.time, 'time', lambda: 0)
    monkeypatch.setattr(job_ops_helper.time, 'sleep', lambda _: None)
    output = io.StringIO()
    monkeypatch.setattr(job_ops_helper.sys, 'stdout', output)

    job_ops_helper.stream_logs_until_completion(
        run_operations=run_operations,
        job_resource=job_resource,
        datastore_operations=datastore_operations,
        raise_exception_on_failed_job=True,
        requests_pipeline='pipeline',
    )

    value = output.getvalue()
    expected_endpoint = (
        'https://ml.azure.com/featureStore/myfs/featureSets/myfset/v1/matJobs/'
        'jobs/job123?wsid=/subscriptions/sub/resourceGroups/rg/providers/'
        'Microsoft.MachineLearningServices/workspaces/myfs'
    )
    assert expected_endpoint in value
    assert 'Warnings:' in value
    assert 'warning text' in value
    assert datastore_called['name'] == 'store'


def test_stream_logs_failed_job_logs_error_when_not_raising(monkeypatch):
    run_details = SimpleNamespace(
        status=JobStatus.FAILED,
        log_files={},
        warnings=[],
        error=SimpleNamespace(as_dict=lambda: {'code': 'error', 'message': 'details'}),
    )
    run_operations = SimpleNamespace(
        _subscription_id='sub',
        _resource_group_name='rg',
        get_run_details=lambda name: run_details,
    )
    job_properties = SimpleNamespace(
        job_type='command',
        services={'Studio': SimpleNamespace(endpoint='https://studio')},
        properties={},
    )
    job_resource = SimpleNamespace(name='job123', properties=job_properties)

    monkeypatch.setattr(
        job_ops_helper,
        'create_requests_pipeline_with_retry',
        lambda requests_pipeline: requests_pipeline,
    )
    monkeypatch.setattr(job_ops_helper.time, 'time', lambda: 0)
    monkeypatch.setattr(job_ops_helper.time, 'sleep', lambda _: None)
    output = io.StringIO()
    monkeypatch.setattr(job_ops_helper.sys, 'stdout', output)

    job_ops_helper.stream_logs_until_completion(
        run_operations=run_operations,
        job_resource=job_resource,
        datastore_operations=None,
        raise_exception_on_failed_job=False,
        requests_pipeline='pipeline',
    )

    value = output.getvalue()
    assert 'Error:' in value
    assert 'code' in value
    assert 'error' in value


def test_stream_logs_failed_job_raises_exception_when_requested(monkeypatch):
    run_details = SimpleNamespace(
        status=JobStatus.FAILED,
        log_files={},
        warnings=[],
        error=SimpleNamespace(as_dict=lambda: {'code': 'error', 'message': 'details'}),
    )
    run_operations = SimpleNamespace(
        _subscription_id='sub',
        _resource_group_name='rg',
        get_run_details=lambda name: run_details,
    )
    job_properties = SimpleNamespace(
        job_type='command',
        services={'Studio': SimpleNamespace(endpoint='https://studio')},
        properties={},
    )
    job_resource = SimpleNamespace(name='job123', properties=job_properties)

    monkeypatch.setattr(
        job_ops_helper,
        'create_requests_pipeline_with_retry',
        lambda requests_pipeline: requests_pipeline,
    )
    monkeypatch.setattr(job_ops_helper.time, 'time', lambda: 0)
    monkeypatch.setattr(job_ops_helper.time, 'sleep', lambda _: None)
    output = io.StringIO()
    monkeypatch.setattr(job_ops_helper.sys, 'stdout', output)

    with pytest.raises(JobException) as excinfo:
        job_ops_helper.stream_logs_until_completion(
            run_operations=run_operations,
            job_resource=job_resource,
            datastore_operations=None,
            requests_pipeline='pipeline',
        )

    assert 'Exception' in str(excinfo.value)


class _FakeWarning:
    def __init__(self, message):
        self.message = message


class _FakeError:
    def __init__(self, payload):
        self._payload = payload

    def as_dict(self):
        return self._payload


class _FakeRunDetails:
    def __init__(self, status, warnings=None, error=None, log_files=None):
        self.status = status
        self.warnings = warnings or []
        self.error = error
        self.log_files = log_files or {}


class _RunOperationsStub:
    def __init__(self, details):
        self._details = details
        self._subscription_id = "sub"
        self._resource_group_name = "rg"

    def get_run_details(self, name):
        return self._details


class _KeyboardInterruptRunOperations:
    def __init__(self):
        self._subscription_id = "sub"
        self._resource_group_name = "rg"

    def get_run_details(self, name):
        raise KeyboardInterrupt()


class _FakeJobProperties:
    def __init__(self, job_type, services=None, properties=None, outputs=None):
        self.job_type = job_type
        self.services = services or {}
        self.properties = properties or {}
        self.outputs = outputs


class _FakeJobResource:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties


def _make_job_resource(job_type):
    return _FakeJobResource(
        name="test-job",
        properties=_FakeJobProperties(job_type=job_type, services={}, properties={}, outputs=None),
    )


def test_stream_logs_until_completion_prints_warnings(monkeypatch, capsys):
    run_details = _FakeRunDetails(
        status=job_ops_helper.JobStatus.COMPLETED,
        warnings=[_FakeWarning("warning line")],
    )
    run_operations = _RunOperationsStub(run_details)
    job_resource = _make_job_resource("command")
    def _fake_create_requests_pipeline_with_retry(requests_pipeline=None, **kwargs):
        return requests_pipeline
    monkeypatch.setattr(job_ops_helper, "create_requests_pipeline_with_retry", _fake_create_requests_pipeline_with_retry)
    job_ops_helper.stream_logs_until_completion(
        run_operations, job_resource, requests_pipeline=object()
    )
    captured = capsys.readouterr()
    assert "Execution Summary" in captured.out
    assert "Warnings:" in captured.out
    assert "warning line" in captured.out
    assert "RunId: test-job" in captured.out


def test_stream_logs_until_completion_prints_error_without_exception(monkeypatch, capsys):
    run_details = _FakeRunDetails(status=job_ops_helper.JobStatus.FAILED)
    run_operations = _RunOperationsStub(run_details)
    job_resource = _make_job_resource("command")
    def _fake_create_requests_pipeline_with_retry(requests_pipeline=None, **kwargs):
        return requests_pipeline
    monkeypatch.setattr(job_ops_helper, "create_requests_pipeline_with_retry", _fake_create_requests_pipeline_with_retry)
    job_ops_helper.stream_logs_until_completion(
        run_operations,
        job_resource,
        raise_exception_on_failed_job=False,
        requests_pipeline=object(),
    )
    captured = capsys.readouterr()
    assert "Error:" in captured.out
    assert "Detailed error not set on the Run. Please check the logs for details." in captured.out


def test_stream_logs_until_completion_raises_when_job_fails(monkeypatch):
    error_payload = {"code": "bad"}
    run_details = _FakeRunDetails(status=job_ops_helper.JobStatus.FAILED, error=_FakeError(error_payload))
    run_operations = _RunOperationsStub(run_details)
    job_resource = _make_job_resource("command")
    def _fake_create_requests_pipeline_with_retry(requests_pipeline=None, **kwargs):
        return requests_pipeline
    monkeypatch.setattr(job_ops_helper, "create_requests_pipeline_with_retry", _fake_create_requests_pipeline_with_retry)
    with pytest.raises(job_ops_helper.JobException) as excinfo:
        job_ops_helper.stream_logs_until_completion(run_operations, job_resource, requests_pipeline=object())
    message = str(excinfo.value)
    assert "Exception :" in message
    assert '"code": "bad"' in message


def test_stream_logs_until_completion_keyboard_interrupt(monkeypatch):
    run_operations = _KeyboardInterruptRunOperations()
    job_resource = _make_job_resource("command")
    def _fake_create_requests_pipeline_with_retry(requests_pipeline=None, **kwargs):
        return requests_pipeline
    monkeypatch.setattr(job_ops_helper, "create_requests_pipeline_with_retry", _fake_create_requests_pipeline_with_retry)
    with pytest.raises(job_ops_helper.JobException) as excinfo:
        job_ops_helper.stream_logs_until_completion(run_operations, job_resource, requests_pipeline=object())
    message = str(excinfo.value).lower()
    assert "output streaming for the run interrupted" in message
