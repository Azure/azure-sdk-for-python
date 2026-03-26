from pathlib import Path
import pytest
from types import MethodType, SimpleNamespace
from unittest.mock import MagicMock

from azure.ai.ml.operations._job_operations import (
    JobOperations,
    _get_job_compute_id,
    module_logger,
    ops_logger,
    RunOperations,
    DatasetDataplaneOperations,
    ModelDataplaneOperations,
    BATCH_JOB_CHILD_RUN_OUTPUT_NAME,
    DEFAULT_ARTIFACT_STORE_OUTPUT_NAME,
    SHORT_URI_FORMAT,
)
from azure.ai.ml.constants._common import (
    AzureMLResourceType,
    LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT,
    AZUREML_RESOURCE_PROVIDER,
    LOCAL_COMPUTE_TARGET,
    WorkspaceDiscoveryUrlKey,
    AssetTypes,
    DEFAULT_ARTIFACT_STORE_OUTPUT_NAME,
    SHORT_URI_FORMAT,
    BATCH_JOB_CHILD_RUN_OUTPUT_NAME,
    SWEEP_JOB_BEST_CHILD_RUN_ID_PROPERTY_NAME,
)
from azure.ai.ml.constants._job.pipeline import PipelineConstants
from azure.ai.ml._scope_dependent_operations import OperationScope, OperationConfig, OperationsContainer
from azure.ai.ml.entities import Job, ValidationResult
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.finetuning.finetuning_job import FineTuningJob
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob
from azure.ai.ml.entities._builders import Spark, Command
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.operations import _job_operations as job_ops_module


class _DummyServiceClient:
    def __init__(self):
        class _Jobs:
            def __init__(self) -> None:
                self.create_or_update_calls = []

            def create_or_update(self, id, resource_group_name, workspace_name, body, **kwargs):  # pylint: disable=unused-argument
                self.create_or_update_calls.append((id, resource_group_name, workspace_name, body, kwargs))
                return body

        self.jobs = _Jobs()


class _DummyCredential:
    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        class _Token:
            def __init__(self) -> None:
                self.token = "dummy-token"

        return _Token()


def _create_job_operations_for_compute_tests() -> JobOperations:
    operation_scope = OperationScope(
        subscription_id="sub-id",
        resource_group_name="rg-name",
        workspace_name="ws-name",
    )
    operation_config = OperationConfig(show_progress=True, enable_telemetry=True)

    class _DummyOperationsContainer:
        def __init__(self, operation_scope, operation_config):
            self._operation_scope = operation_scope
            self._operation_config = operation_config
            self.all_operations = {}

        def get_operation(self, azureml_type, condition):  # pylint: disable=unused-argument
            # For these tests we don't need actual operations; just return None.
            return None

    all_operations_container = _DummyOperationsContainer(operation_scope, operation_config)

    service_client_2023 = _DummyServiceClient()
    service_client_2024_01 = _DummyServiceClient()
    service_client_2024_10 = _DummyServiceClient()
    service_client_2025_01 = _DummyServiceClient()
    credential = _DummyCredential()
    requests_pipeline = object()

    job_ops = JobOperations(
        operation_scope,
        operation_config,
        service_client_2023,
        all_operations_container,
        credential,
        requests_pipeline=requests_pipeline,
        service_client_01_2024_preview=service_client_2024_01,
        service_client_10_2024_preview=service_client_2024_10,
        service_client_01_2025_preview=service_client_2025_01,
    )
    return job_ops


def test_ops_logger_and_module_logger_initialized():
    # Accessing ops_logger and module_logger ensures their module-level initialization lines are executed
    assert ops_logger is not None
    assert module_logger is not None


def test_runs_operations_lazy_initialization_and_caching():
    job_ops = _create_job_operations_for_compute_tests()
    job_ops._api_base_url = "https://dummy-api"  # avoid calling _get_workspace_url

    assert job_ops._runs_operations_client is None
    first_client = job_ops._runs_operations
    assert isinstance(first_client, RunOperations)
    second_client = job_ops._runs_operations
    assert first_client is second_client


def test_dataset_dataplane_operations_lazy_initialization_and_caching():
    job_ops = _create_job_operations_for_compute_tests()
    job_ops._api_base_url = "https://dummy-api"  # avoid calling _get_workspace_url

    assert job_ops._dataset_dataplane_operations_client is None
    first_client = job_ops._dataset_dataplane_operations
    assert isinstance(first_client, DatasetDataplaneOperations)
    second_client = job_ops._dataset_dataplane_operations
    assert first_client is second_client


def test_model_dataplane_operations_lazy_initialization_and_caching():
    job_ops = _create_job_operations_for_compute_tests()
    job_ops._api_base_url = "https://dummy-api"  # avoid calling _get_workspace_url

    assert job_ops._model_dataplane_operations_client is None
    first_client = job_ops._model_dataplane_operations
    assert isinstance(first_client, ModelDataplaneOperations)
    second_client = job_ops._model_dataplane_operations
    assert first_client is second_client


def test_api_url_caching_uses_get_workspace_url_once(monkeypatch):
    job_ops = _create_job_operations_for_compute_tests()
    calls = []

    def fake_get_workspace_url(url_key):  # pylint: disable=unused-argument
        calls.append(url_key)
        return "https://api.first.call"

    monkeypatch.setattr(job_ops, "_get_workspace_url", fake_get_workspace_url)

    first = job_ops._api_url
    second = job_ops._api_url

    assert first == "https://api.first.call"
    assert second == "https://api.first.call"
    assert calls == [WorkspaceDiscoveryUrlKey.API]


def test_resolve_compute_id_returns_local_without_resolving():
    job_ops = _create_job_operations_for_compute_tests()
    resolver_calls = []

    def resolver(name, azureml_type, sub_workspace_resource=False):  # pylint: disable=unused-argument
        resolver_calls.append((name, azureml_type, sub_workspace_resource))
        raise AssertionError("resolver should not be called for local compute")

    result = job_ops._resolve_compute_id(resolver, LOCAL_COMPUTE_TARGET.upper())

    assert result == LOCAL_COMPUTE_TARGET
    assert resolver_calls == []


def test_resolve_compute_id_virtualcluster_uses_vc_arm_id_and_type():
    job_ops = _create_job_operations_for_compute_tests()
    received = {}

    def resolver(name, azureml_type, sub_workspace_resource=False):
        received["name"] = name
        received["type"] = azureml_type
        received["sub_workspace_resource"] = sub_workspace_resource
        return "resolved-vc-id"

    target = AzureMLResourceType.VIRTUALCLUSTER + "/my-vc"

    result = job_ops._resolve_compute_id(resolver, target)

    expected_name = LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT.format(
        job_ops._operation_scope.subscription_id,
        job_ops._operation_scope.resource_group_name,
        AZUREML_RESOURCE_PROVIDER,
        AzureMLResourceType.VIRTUALCLUSTER,
        "my-vc",
    )

    assert result == "resolved-vc-id"
    assert received["name"] == expected_name
    assert received["type"] == AzureMLResourceType.VIRTUALCLUSTER
    assert received["sub_workspace_resource"] is False


def test_resolve_compute_id_falls_back_to_compute_and_get_job_compute_id():
    job_ops = _create_job_operations_for_compute_tests()
    resolver_calls = []

    def resolver(name, azureml_type, sub_workspace_resource=False):
        resolver_calls.append((name, azureml_type, sub_workspace_resource))
        if azureml_type == AzureMLResourceType.VIRTUALCLUSTER:
            raise RuntimeError("no virtual cluster")
        return "resolved-compute-id"

    target = "cpu-cluster"

    result = job_ops._resolve_compute_id(resolver, target)

    assert result == "resolved-compute-id"
    assert resolver_calls[0][0] == target
    assert resolver_calls[0][1] == AzureMLResourceType.VIRTUALCLUSTER
    assert resolver_calls[1][0] == target
    assert resolver_calls[1][1] == AzureMLResourceType.COMPUTE

    class DummyJob:
        def __init__(self) -> None:
            self.compute = "another-cluster"

    job = DummyJob()
    _get_job_compute_id(job, resolver)
    assert job.compute == "resolved-compute-id"


def test_list_with_parent_job_uses_runs_children(monkeypatch):
    job_ops = _create_job_operations_for_compute_tests()

    parent_job = SimpleNamespace(name="parent-job-name")
    monkeypatch.setattr(job_ops, "get", lambda name: parent_job)

    class DummyRunsOperations:
        def __init__(self) -> None:
            self.calls = []

        def get_run_children(self, name, max_results=None):  # pylint: disable=unused-argument
            self.calls.append((name, max_results))
            return ["child1", "child2"]

    dummy_runs = DummyRunsOperations()
    job_ops._runs_operations_client = dummy_runs

    result = list(job_ops.list(parent_job_name="parent-job-name", max_results=5))

    assert result == ["child1", "child2"]
    assert dummy_runs.calls == [("parent-job-name", 5)]


def test_list_without_parent_job_uses_service_client_and_handle_errors(monkeypatch):
    job_ops = _create_job_operations_for_compute_tests()

    class DummyJobs:
        def __init__(self) -> None:
            self.list_calls = []

        def list(self, resource_group_name, workspace_name, cls, list_view_type, scheduled, schedule_id, **kwargs):
            self.list_calls.append(
                {
                    "resource_group_name": resource_group_name,
                    "workspace_name": workspace_name,
                    "list_view_type": list_view_type,
                    "scheduled": scheduled,
                    "schedule_id": schedule_id,
                    "kwargs": kwargs,
                }
            )
            objs = ["obj1", "obj2"]
            return cls(objs)

    dummy_jobs = DummyJobs()
    job_ops.service_client_01_2024_preview.jobs = dummy_jobs

    handled = []

    def fake_handle_rest_errors(self, obj):  # pylint: disable=unused-argument
        handled.append(f"handled-{obj}")
        return f"handled-{obj}"

    monkeypatch.setattr(JobOperations, "_handle_rest_errors", fake_handle_rest_errors)

    result = list(
        job_ops.list(
            schedule_defined=True,
            scheduled_job_name="sched-job",
            extra_param="value",
        )
    )

    assert result == ["handled-obj1", "handled-obj2"]
    assert len(dummy_jobs.list_calls) == 1
    call = dummy_jobs.list_calls[0]
    assert call["resource_group_name"] == job_ops._operation_scope.resource_group_name
    assert call["workspace_name"] == job_ops._workspace_name
    assert call["scheduled"] is True
    assert call["schedule_id"] == "sched-job"
    assert call["kwargs"]["extra_param"] == "value"


def test_resolve_arm_id_or_upload_dependencies_spark_branch_calls_resolve_job_inputs(monkeypatch):
    job_operations = _create_job_operations_for_compute_tests()

    called = {"resolver_job": None, "entries": None, "base_path": None}

    def fake_resolve_arm_id_or_azureml_id(job, resolver):  # pylint: disable=unused-argument
        called["resolver_job"] = job
        return job

    def fake_resolve_job_inputs(entries, base_path):
        called["entries"] = list(entries)
        called["base_path"] = base_path

    monkeypatch.setattr(job_operations, "_resolve_arm_id_or_azureml_id", fake_resolve_arm_id_or_azureml_id)
    monkeypatch.setattr(job_operations, "_resolve_job_inputs", fake_resolve_job_inputs)

    class DummySpark(Spark):
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            pass

    spark_job = DummySpark()
    spark_job._job_inputs = {"input1": "value1"}
    spark_job._base_path = "base/path"

    job_operations._resolve_arm_id_or_upload_dependencies(spark_job)

    assert called["resolver_job"] is spark_job
    assert called["entries"] == ["value1"]
    assert called["base_path"] == "base/path"


def test_resolve_arm_id_or_upload_dependencies_command_branch_calls_resolve_job_inputs(monkeypatch):
    job_operations = _create_job_operations_for_compute_tests()

    called = {"resolver_job": None, "entries": None, "base_path": None}

    def fake_resolve_arm_id_or_azureml_id(job, resolver):  # pylint: disable=unused-argument
        called["resolver_job"] = job
        return job

    def fake_resolve_job_inputs(entries, base_path):
        called["entries"] = list(entries)
        called["base_path"] = base_path

    monkeypatch.setattr(job_operations, "_resolve_arm_id_or_azureml_id", fake_resolve_arm_id_or_azureml_id)
    monkeypatch.setattr(job_operations, "_resolve_job_inputs", fake_resolve_job_inputs)

    class DummyCommand(Command):
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            pass

    command_job = DummyCommand()
    command_job._job_inputs = {"input1": "value1", "input2": "value2"}
    command_job._base_path = "base/command"

    job_operations._resolve_arm_id_or_upload_dependencies(command_job)

    assert called["resolver_job"] is command_job
    assert set(called["entries"]) == {"value1", "value2"}
    assert called["base_path"] == "base/command"


def test_resolve_arm_id_or_upload_dependencies_automl_branch_calls_resolve_automl_inputs(monkeypatch):
    job_operations = _create_job_operations_for_compute_tests()

    called = {"automl_job": None}

    def fake_resolve_arm_id_or_azureml_id(job, resolver):  # type: ignore[no-untyped-def]
        return job

    def fake_resolve_automl_job_inputs(job):
        called["automl_job"] = job

    monkeypatch.setattr(job_operations, "_resolve_arm_id_or_azureml_id", fake_resolve_arm_id_or_azureml_id)
    monkeypatch.setattr(job_operations, "_resolve_automl_job_inputs", fake_resolve_automl_job_inputs)

    class DummyAutoMLJob(AutoMLJob):
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            # Minimal init; AutoMLJob has abstract members we override below.
            self._base_path = "base/automl"

        def _to_dict(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return {}

        @property
        def training_data(self):  # type: ignore[no-untyped-def]
            return None

        @training_data.setter
        def training_data(self, value):  # type: ignore[no-untyped-def]
            pass

        @property
        def validation_data(self):  # type: ignore[no-untyped-def]
            return None

        @validation_data.setter
        def validation_data(self, value):  # type: ignore[no-untyped-def]
            pass

        @property
        def test_data(self):  # type: ignore[no-untyped-def]
            return None

        @test_data.setter
        def test_data(self, value):  # type: ignore[no-untyped-def]
            pass

    automl_job = DummyAutoMLJob()

    job_operations._resolve_arm_id_or_upload_dependencies(automl_job)

    assert called["automl_job"] is automl_job


def test_resolve_arm_id_or_upload_dependencies_finetuning_branch_calls_resolve_finetuning_inputs(monkeypatch):
    job_operations = _create_job_operations_for_compute_tests()

    called = {"finetuning_job": None}

    def fake_resolve_arm_id_or_azureml_id(job, resolver):  # type: ignore[unused-argument]
        return job

    def fake_resolve_finetuning_job_inputs(job):
        called["finetuning_job"] = job

    monkeypatch.setattr(job_operations, "_resolve_arm_id_or_azureml_id", fake_resolve_arm_id_or_azureml_id)
    monkeypatch.setattr(job_operations, "_resolve_finetuning_job_inputs", fake_resolve_finetuning_job_inputs)

    class DummyFineTuningJob(FineTuningJob):
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            pass

        def _to_dict(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return {}

    finetuning_job = DummyFineTuningJob()

    job_operations._resolve_arm_id_or_upload_dependencies(finetuning_job)

    assert called["finetuning_job"] is finetuning_job


def test_resolve_arm_id_or_upload_dependencies_distillation_branch_calls_resolve_distillation_inputs(monkeypatch):
    job_operations = _create_job_operations_for_compute_tests()

    called = {"distillation_job": None}

    def fake_resolve_arm_id_or_azureml_id(job, resolver):  # type: ignore[unused-argument]
        return job

    def fake_resolve_distillation_job_inputs(job):
        called["distillation_job"] = job

    monkeypatch.setattr(job_operations, "_resolve_arm_id_or_azureml_id", fake_resolve_arm_id_or_azureml_id)
    monkeypatch.setattr(job_operations, "_resolve_distillation_job_inputs", fake_resolve_distillation_job_inputs)

    class DummyDistillationJob(DistillationJob):
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            pass

    distillation_job = DummyDistillationJob()

    job_operations._resolve_arm_id_or_upload_dependencies(distillation_job)

    assert called["distillation_job"] is distillation_job


def test_resolve_arm_id_or_upload_dependencies_else_branch_with_inputs_calls_resolve_job_inputs(monkeypatch):
    job_operations = _create_job_operations_for_compute_tests()

    called = {"entries": None, "base_path": None}

    def fake_resolve_arm_id_or_azureml_id(job, resolver):  # type: ignore[unused-argument]
        return job

    def fake_resolve_job_inputs(entries, base_path):
        called["entries"] = list(entries)
        called["base_path"] = base_path

    monkeypatch.setattr(job_operations, "_resolve_arm_id_or_azureml_id", fake_resolve_arm_id_or_azureml_id)
    monkeypatch.setattr(job_operations, "_resolve_job_inputs", fake_resolve_job_inputs)

    class OtherJob:
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            self.inputs = {"a": 1, "b": 2}
            self._base_path = "else/base"

    other_job = OtherJob()

    job_operations._resolve_arm_id_or_upload_dependencies(other_job)  # type: ignore[arg-type]

    assert set(called["entries"]) == {1, 2}
    assert called["base_path"] == "else/base"


def test_resolve_arm_id_or_upload_dependencies_else_branch_without_inputs_swallows_attribute_error(monkeypatch):
    job_operations = _create_job_operations_for_compute_tests()

    called = {"called": False}

    def fake_resolve_arm_id_or_azureml_id(job, resolver):  # type: ignore[unused-argument]
        return job

    def fake_resolve_job_inputs(entries, base_path):  # pylint: disable=unused-argument
        called["called"] = True

    monkeypatch.setattr(job_operations, "_resolve_arm_id_or_azureml_id", fake_resolve_arm_id_or_azureml_id)
    monkeypatch.setattr(job_operations, "_resolve_job_inputs", fake_resolve_job_inputs)

    class OtherJobNoInputs:
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            self._base_path = "no/inputs"

    other_job = OtherJobNoInputs()

    job_operations._resolve_arm_id_or_upload_dependencies(other_job)  # type: ignore[arg-type]

    assert called["called"] is False


class SimpleJobOperations(JobOperations):
    def __init__(self):  # type: ignore[no-untyped-def]
        # Bypass parent initialization for isolated unit tests
        pass


def test_validate_non_path_aware_job_returns_empty_validation_result():
    ops = SimpleJobOperations()
    # Dummy job object that is not PathAwareSchemaValidatableMixin
    job = object()

    result = ops._validate(job, raise_on_failure=False)

    assert isinstance(result, ValidationResult)
    assert result.passed is True


def test_resolve_automl_job_inputs_without_optional_validation_or_test_data():
    ops = SimpleJobOperations()

    calls = []

    def fake_resolve_job_input(self, entry, base_path):  # type: ignore[no-untyped-def]
        calls.append((entry, base_path))

    ops._resolve_job_input = fake_resolve_job_input.__get__(ops, SimpleJobOperations)

    class DummyAutoMLJob(AutoMLJob):
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            # Bypass parent initialization; just set the attributes used by _resolve_automl_job_inputs.
            self._training_data = None
            self._validation_data = None
            self._test_data = None
            self._base_path = "base_path"

        def _to_dict(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return {}

        @property
        def training_data(self):  # type: ignore[no-untyped-def]
            return self._training_data

        @training_data.setter
        def training_data(self, value):  # type: ignore[no-untyped-def]
            self._training_data = value

        @property
        def validation_data(self):  # type: ignore[no-untyped-def]
            return self._validation_data

        @validation_data.setter
        def validation_data(self, value):  # type: ignore[no-untyped-def]
            self._validation_data = value

        @property
        def test_data(self):  # type: ignore[no-untyped-def]
            return self._test_data

        @test_data.setter
        def test_data(self, value):  # type: ignore[no-untyped-def]
            self._test_data = value

    job = DummyAutoMLJob()
    job.training_data = "train_data"
    job.validation_data = None
    job.test_data = None

    ops._resolve_automl_job_inputs(job)

    assert calls == [("train_data", "base_path")]


def test_resolve_finetuning_job_inputs_ignores_non_vertical_jobs():
    ops = SimpleJobOperations()

    def failing_resolve_job_input(self, entry, base_path):  # type: ignore[no-untyped-def]
        raise RuntimeError("_resolve_job_input should not be called for non-vertical finetuning job")

    ops._resolve_job_input = failing_resolve_job_input.__get__(ops, SimpleJobOperations)

    class DummyFineTuningJob:
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            self.training_data = "train_data"
            self.validation_data = "val_data"
            self._base_path = "base_path"

    job = DummyFineTuningJob()

    # Should not raise, and _resolve_job_input must not be invoked
    ops._resolve_finetuning_job_inputs(job)  # type: ignore[arg-type]


def test_resolve_distillation_job_inputs_only_validation_data_when_training_missing():
    ops = SimpleJobOperations()

    calls = []

    def fake_resolve_job_input(self, entry, base_path):  # type: ignore[no-untyped-def]
        calls.append((entry, base_path))

    ops._resolve_job_input = fake_resolve_job_input.__get__(ops, SimpleJobOperations)

    job = DistillationJob.__new__(DistillationJob)
    job.training_data = None
    job.validation_data = "val_data"
    job._base_path = "base_path"

    ops._resolve_distillation_job_inputs(job)

    assert calls == [("val_data", "base_path")]


def test_resolve_job_inputs_arm_id_resolves_input_paths_with_orchestrator():
    ops = SimpleJobOperations()

    class DummyOrchestrator:
        def __init__(self):  # type: ignore[no-untyped-def]
            self.calls = []

        def resolve_azureml_id(self, path):  # type: ignore[no-untyped-def]
            self.calls.append(path)
            return "resolved:" + path

    orchestrator = DummyOrchestrator()
    ops._orchestrators = orchestrator  # type: ignore[attr-defined]

    input_obj = Input(type=AssetTypes.URI_FILE, path="azureml:mydata@1")

    class DummyJob:
        pass

    job = DummyJob()
    job.inputs = {"input1": input_obj}

    ops._resolve_job_inputs_arm_id(job)

    assert orchestrator.calls == ["azureml:mydata@1"]
    assert input_obj.path == "resolved:azureml:mydata@1"


class DummyDatastore:
    def __init__(self, name: str):
        self.name = name


class DummyDatastoreOperations:
    def __init__(self, default_name: str = "defaultdatastore"):
        self._default = DummyDatastore(default_name)

    def get_default(self) -> DummyDatastore:
        return self._default


class DummyRunsOperations:
    def __init__(self, children):
        self._children = children

    def get_run_children(self, job_name):  # pylint: disable=unused-argument
        return self._children


class MinimalJobOperations(JobOperations):
    def __init__(self, runs_operations, datastore_operations):  # type: ignore[no-untyped-def]
        # Do not call super().__init__ to avoid real client initialization
        self._runs_operations_override = runs_operations
        self._datastore_operations_override = datastore_operations
        self._dataset_dataplane_operations_override = object()
        self._model_dataplane_operations_override = object()
        self._requests_pipeline = None
        # attributes used in other helpers but not in the tested methods
        self._all_operations = type("AllOps", (), {"all_operations": {}})()

    @property
    def _runs_operations(self):  # type: ignore[override]
        return self._runs_operations_override

    @property
    def _datastore_operations(self):  # type: ignore[override]
        return self._datastore_operations_override

    @property
    def _dataset_dataplane_operations(self):  # type: ignore[override]
        return self._dataset_dataplane_operations_override

    @property
    def _model_dataplane_operations(self):  # type: ignore[override]
        return self._model_dataplane_operations_override


def test_get_named_output_uri_iterable_no_default_in_missing(monkeypatch):
    job_name = "job1"

    def fake_get_outputs(job_name_arg, runs_ops, dataset_ops, model_ops, output_names=None):  # pylint: disable=unused-argument
        # Return exactly the requested output so missing_outputs will be empty
        return {"foo": "uri://foo"}

    monkeypatch.setattr(
        job_ops_module,
        "get_job_output_uris_from_dataplane",
        fake_get_outputs,
    )

    # datastore operations will not be used because missing_outputs is empty
    op = MinimalJobOperations(runs_operations=None, datastore_operations=DummyDatastoreOperations())

    outputs = op._get_named_output_uri(job_name, output_names=["foo"])

    assert outputs == {"foo": "uri://foo"}
    # Ensure default artifact output is not added when it's not requested and not missing
    assert DEFAULT_ARTIFACT_STORE_OUTPUT_NAME not in outputs


def test_get_named_output_uri_default_short_uri_on_attribute_error(monkeypatch):
    job_name = "job2"

    def fake_get_outputs(job_name_arg, runs_ops, dataset_ops, model_ops, output_names=None):  # pylint: disable=unused-argument
        # No outputs returned from dataplane
        return {}

    monkeypatch.setattr(
        job_ops_module,
        "get_job_output_uris_from_dataplane",
        fake_get_outputs,
    )

    class JobWithoutOutputs:
        # Object without an `outputs` attribute to trigger AttributeError
        def __init__(self, name):
            self.name = name

    op = MinimalJobOperations(runs_operations=None, datastore_operations=DummyDatastoreOperations())

    def fake_get(self, name):  # pylint: disable=unused-argument
        return JobWithoutOutputs(name)

    op.get = fake_get.__get__(op, MinimalJobOperations)

    outputs = op._get_named_output_uri(job_name)

    expected_default_uri = SHORT_URI_FORMAT.format(
        "workspaceartifactstore",
        f"ExperimentRun/dcid.{job_name}/",
    )
    assert outputs[DEFAULT_ARTIFACT_STORE_OUTPUT_NAME] == expected_default_uri


def test_get_named_output_uri_missing_outputs_and_batch_scoring_no_uri(monkeypatch):
    job_name = "job3"

    def fake_get_outputs(job_name_arg, runs_ops, dataset_ops, model_ops, output_names=None):  # pylint: disable=unused-argument
        # Simulate that no outputs are returned for requested names
        return {}

    monkeypatch.setattr(
        job_ops_module,
        "get_job_output_uris_from_dataplane",
        fake_get_outputs,
    )

    def fake_aml_datastore_path_exists(potential_uri, datastore_ops):  # pylint: disable=unused-argument
        # Force path existence checks to fail so outputs remain missing
        return False

    monkeypatch.setattr(
        job_ops_module,
        "aml_datastore_path_exists",
        fake_aml_datastore_path_exists,
    )

    datastore_ops = DummyDatastoreOperations(default_name="defaultstore")

    child = type("Child", (), {"name": "child1"})()
    runs_ops = DummyRunsOperations(children=[child])

    op = MinimalJobOperations(runs_operations=runs_ops, datastore_operations=datastore_ops)

    # Monkeypatch named output URI resolution for batch scoring to always return no URI
    def fake_get_named_output_uri(job_name_arg, output_names=None):  # pylint: disable=unused-argument
        return {}

    op._get_named_output_uri = fake_get_named_output_uri  # type: ignore[assignment]

    outputs = op._get_named_output_uri(job_name, output_names=["missing_output"])
    assert outputs == {}

    scoring_uri = op._get_batch_job_scoring_output_uri(job_name)
    assert scoring_uri is None


class _DummyDatastoreOperations:
    def __init__(self, default_name: str = "workspaceartifactstore") -> None:
        self._default = SimpleNamespace(name=default_name)

    def get_default(self) -> SimpleNamespace:
        return self._default


def _build_job_operations() -> JobOperations:
    job_ops = object.__new__(JobOperations)
    job_ops._kwargs = {}
    job_ops._runs_operations_client = SimpleNamespace(get_run_children=lambda _: [])
    job_ops._dataset_dataplane_operations_client = SimpleNamespace()
    job_ops._model_dataplane_operations_client = SimpleNamespace()
    datastore_ops = _DummyDatastoreOperations()
    job_ops._all_operations = SimpleNamespace(all_operations={AzureMLResourceType.DATASTORE: datastore_ops})
    job_ops._datastore_operations_override = datastore_ops
    job_ops._operation_scope = SimpleNamespace(
        subscription_id="sub-id",
        resource_group_name="rg-name",
        workspace_name="workspace",
    )
    job_ops._operation_config = SimpleNamespace(show_progress=False)
    job_ops._requests_pipeline = None
    return job_ops


def test_get_named_output_uri_prefers_job_default(monkeypatch):
    job_ops = _build_job_operations()

    def _fake_job_output_uris(job_name, runs, dataset_ops, model_ops, output_names=None):
        return {}

    monkeypatch.setattr(
        "azure.ai.ml.operations._job_operations.get_job_output_uris_from_dataplane",
        _fake_job_output_uris,
    )
    job = SimpleNamespace(outputs={DEFAULT_ARTIFACT_STORE_OUTPUT_NAME: SimpleNamespace(path="https://default-artifact")})
    job_ops.get = lambda name: job
    result = job_ops._get_named_output_uri("job-1")
    assert result[DEFAULT_ARTIFACT_STORE_OUTPUT_NAME] == "https://default-artifact"


def test_get_named_output_uri_falls_back_to_short_uri_for_missing_job_outputs(monkeypatch):
    job_ops = _build_job_operations()
    monkeypatch.setattr(
        "azure.ai.ml.operations._job_operations.get_job_output_uris_from_dataplane",
        lambda *args, **kwargs: {},
    )
    monkeypatch.setattr(
        "azure.ai.ml.operations._job_operations.aml_datastore_path_exists",
        lambda uri, datastore_ops: True,
    )
    job_ops.get = lambda name: SimpleNamespace()
    job_name = "job-2"
    result = job_ops._get_named_output_uri(
        job_name,
        output_names=[DEFAULT_ARTIFACT_STORE_OUTPUT_NAME, "custom_output"],
    )
    expected_default = SHORT_URI_FORMAT.format(
        "workspaceartifactstore",
        f"ExperimentRun/dcid.{job_name}/",
    )
    assert result[DEFAULT_ARTIFACT_STORE_OUTPUT_NAME] == expected_default
    expected_custom = SHORT_URI_FORMAT.format(
        "workspaceartifactstore",
        f"azureml/{job_name}/custom_output/",
    )
    assert result["custom_output"] == expected_custom


def test_get_batch_job_scoring_output_uri_returns_first_child():
    job_ops = _build_job_operations()
    job_ops._runs_operations_client = SimpleNamespace(
        get_run_children=lambda name: [SimpleNamespace(name="child-1"), SimpleNamespace(name="child-2")]
    )
    called_children = []

    def _fake_named_output_uri(self, run_name, output_names=None):
        called_children.append(run_name)
        if run_name == "child-1":
            return {BATCH_JOB_CHILD_RUN_OUTPUT_NAME: "scoring-uri"}
        return {}

    job_ops._get_named_output_uri = MethodType(_fake_named_output_uri, job_ops)
    result = job_ops._get_batch_job_scoring_output_uri("parent-job")
    assert result == "scoring-uri"
    assert called_children == ["child-1"]


def _make_job_operations():
    job_ops = object.__new__(JobOperations)
    datastore_ops = SimpleNamespace(get_default=MagicMock(return_value=SimpleNamespace(name="workspaceartifactstore")))
    job_ops._all_operations = SimpleNamespace(all_operations={AzureMLResourceType.DATASTORE: datastore_ops})
    job_ops._runs_operations_client = SimpleNamespace()
    job_ops._dataset_dataplane_operations_client = SimpleNamespace()
    job_ops._model_dataplane_operations_client = SimpleNamespace()
    job_ops._operation_scope = SimpleNamespace(
        resource_group_name="rg",
        workspace_name="ws",
        subscription_id="sub",
    )
    job_ops._kwargs = {}
    job_ops._requests_pipeline = MagicMock()
    job_ops._orchestrators = SimpleNamespace(
        get_asset_arm_id=MagicMock(),
        resolve_azureml_id=MagicMock(),
    )
    job_ops._operation_config = SimpleNamespace(show_progress=False)
    return job_ops


def test_download_reuses_previous_job(monkeypatch):
    job_ops = _make_job_operations()
    parent_job = SimpleNamespace(
        name="parent",
        properties={
            PipelineConstants.REUSED_FLAG_FIELD: PipelineConstants.REUSED_FLAG_TRUE,
            PipelineConstants.REUSED_JOB_ID: "child",
        },
        status="Completed",
        tags={},
        outputs={},
    )
    child_job = SimpleNamespace(
        name="child",
        properties={},
        status="Completed",
        tags={},
        outputs={DEFAULT_ARTIFACT_STORE_OUTPUT_NAME: SimpleNamespace(path="uri")},
    )
    job_ops.get = MagicMock(side_effect=[parent_job, child_job])
    job_ops._get_named_output_uri = MagicMock(return_value={DEFAULT_ARTIFACT_STORE_OUTPUT_NAME: "uri"})
    destinations = []

    def _fake_download_artifact_from_aml_uri(*, uri, destination, datastore_operation):
        destinations.append(destination)

    monkeypatch.setattr(
        "azure.ai.ml.operations._job_operations.download_artifact_from_aml_uri",
        _fake_download_artifact_from_aml_uri,
    )

    job_ops.download("parent", download_path=Path("out"))
    assert job_ops._get_named_output_uri.call_args_list[-1][0] == ("child", DEFAULT_ARTIFACT_STORE_OUTPUT_NAME)
    assert destinations == [Path("out") / "artifacts"]


def test_download_sweep_job_uses_best_child(monkeypatch):
    job_ops = _make_job_operations()

    class FakeSweepJob:
        pass

    monkeypatch.setattr("azure.ai.ml.operations._job_operations.SweepJob", FakeSweepJob)
    best_child_run_id = "child-run"
    parent_job = FakeSweepJob()
    parent_job.name = "sweep-run"
    parent_job.properties = {SWEEP_JOB_BEST_CHILD_RUN_ID_PROPERTY_NAME: best_child_run_id}
    parent_job.status = "Completed"
    parent_job.tags = {}
    parent_job.outputs = {}
    child_job = SimpleNamespace(
        name=best_child_run_id,
        properties={},
        status="Completed",
        tags={},
        outputs={DEFAULT_ARTIFACT_STORE_OUTPUT_NAME: SimpleNamespace(path="uri")},
    )
    job_ops.get = MagicMock(side_effect=[parent_job, child_job])
    job_ops._get_named_output_uri = MagicMock(return_value={DEFAULT_ARTIFACT_STORE_OUTPUT_NAME: "uri"})
    destinations = []

    def _fake_download_artifact_from_aml_uri(*, uri, destination, datastore_operation):
        destinations.append(destination)

    monkeypatch.setattr(
        "azure.ai.ml.operations._job_operations.download_artifact_from_aml_uri",
        _fake_download_artifact_from_aml_uri,
    )

    job_ops.download(parent_job.name, download_path=Path("dest"))
    assert job_ops.get.call_args_list[1][0][0] == best_child_run_id
    assert destinations == [Path("dest") / "artifacts", Path("dest") / "hd-artifacts"]


def test_download_batch_job_uses_scoring_uri(monkeypatch):
    job_ops = _make_job_operations()
    job = SimpleNamespace(
        name="batch",
        properties={},
        status="Completed",
        tags={"azureml.batchrun": "true", "azureml.jobtype": "command"},
        outputs={},
    )
    job_ops.get = MagicMock(return_value=job)
    job_ops._get_batch_job_scoring_output_uri = MagicMock(return_value="score-blob")
    records = []

    def _fake_download_artifact_from_aml_uri(*, uri, destination, datastore_operation):
        records.append((uri, destination))

    monkeypatch.setattr(
        "azure.ai.ml.operations._job_operations.download_artifact_from_aml_uri",
        _fake_download_artifact_from_aml_uri,
    )

    job_ops.download("batch", download_path=Path("dest"))
    assert job_ops._get_batch_job_scoring_output_uri.call_args[0] == ("batch",)
    assert records == [("score-blob", Path("dest"))]


def test_download_logs_when_named_output_missing(monkeypatch):
    job_ops = _make_job_operations()
    job = SimpleNamespace(
        name="job",
        properties={},
        status="Completed",
        tags={},
        outputs={},
    )
    job_ops.get = MagicMock(return_value=job)
    job_ops._get_named_output_uri = MagicMock(return_value={})
    records = []

    def _fake_download_artifact_from_aml_uri(*, uri, destination, datastore_operation):
        records.append(uri)

    monkeypatch.setattr(
        "azure.ai.ml.operations._job_operations.download_artifact_from_aml_uri",
        _fake_download_artifact_from_aml_uri,
    )

    job_ops.download("job", download_path=Path("dest"), output_name="missing")
    job_ops._get_named_output_uri.assert_called_with("job", "missing")
    assert records == []
