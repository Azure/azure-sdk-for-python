import json
import os
from typing import Callable
from unittest.mock import Mock, patch

import jwt
import pytest
import vcr
import yaml
from azure.ai.ml._azure_environments import _get_aml_resource_id_from_metadata, _resource_to_scopes
from azure.ai.ml.exceptions import ValidationException
from azure.core.credentials import AccessToken
from msrest import Deserializer
from pytest_mock import MockFixture

from azure.ai.ml import MLClient, load_job
from azure.ai.ml._restclient.v2023_04_01_preview import models
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.constants._common import AZUREML_PRIVATE_FEATURES_ENV_VAR, AzureMLResourceType
from azure.ai.ml.entities._builders import Command
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.automl.training_settings import TrainingSettings
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.sweep.sweep_job import SweepJob
from azure.ai.ml.operations import DatastoreOperations, EnvironmentOperations, JobOperations, WorkspaceOperations
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.ai.ml.operations._job_ops_helper import get_git_properties
from azure.ai.ml.operations._run_history_constants import RunHistoryConstants
from azure.ai.ml.operations._run_operations import RunOperations
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

from .test_vcr_utils import before_record_cb, vcr_header_filters


@pytest.fixture
def mock_datastore_operation(
    mock_workspace_scope: OperationScope, mock_operation_config: OperationConfig, mock_aml_services_2022_10_01: Mock
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        serviceclient_2022_10_01=mock_aml_services_2022_10_01,
    )


@pytest.fixture
def mock_code_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_datastore_operation: Mock,
) -> CodeOperations:
    yield CodeOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operation,
    )


@pytest.fixture
def mock_environment_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_machinelearning_client: Mock,
    mock_aml_services_2022_05_01: Mock,
) -> EnvironmentOperations:
    yield EnvironmentOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_05_01,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.fixture
def mock_workspace_operation(
    mock_workspace_scope: OperationScope,
    mock_machinelearning_client: Mock,
    mock_aml_services_2022_10_01: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        mock_workspace_scope,
        service_client=mock_aml_services_2022_10_01,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.fixture
def mock_runs_operation(
    mock_workspace_scope: OperationScope, mock_operation_config: OperationConfig, mock_aml_services_2022_10_01: Mock
) -> RunOperations:
    yield RunOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_10_01,
    )


@pytest.fixture
def mock_job_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2023_02_01_preview: Mock,
    mock_aml_services_run_history: Mock,
    mock_machinelearning_client: Mock,
    mock_code_operation: Mock,
    mock_workspace_operation: WorkspaceOperations,
    mock_datastore_operation: Mock,
    mock_environment_operation: Mock,
    mock_runs_operation: Mock,
) -> JobOperations:
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.CODE, mock_code_operation)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.ENVIRONMENT, mock_environment_operation)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.WORKSPACE, mock_workspace_operation)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.DATASTORE, mock_datastore_operation)
    mock_machinelearning_client._operation_container.add("run", mock_runs_operation)
    yield JobOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client_02_2023_preview=mock_aml_services_2023_02_01_preview,
        service_client_run_history=mock_aml_services_run_history,
        all_operations=mock_machinelearning_client._operation_container,
        credential=Mock(spec_set=DefaultAzureCredential),
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
    )


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestJobOperations:
    def test_list(self, mock_job_operation: JobOperations) -> None:
        mock_job_operation.list()
        expected = (mock_job_operation._resource_group_name, mock_job_operation._workspace_name)
        assert expected in mock_job_operation._operation_2023_02_preview.list.call_args

    @patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"})
    def test_list_private_preview(self, mock_job_operation: JobOperations) -> None:
        mock_job_operation.list()
        expected = (mock_job_operation._resource_group_name, mock_job_operation._workspace_name)
        assert expected in mock_job_operation._operation_2023_02_preview.list.call_args

    @patch.object(Job, "_from_rest_object")
    def test_get(self, mock_method, mock_job_operation: JobOperations) -> None:
        mock_method.return_value = Command(component=None)
        mock_job_operation.get("randon_name")
        mock_job_operation._operation_2023_02_preview.get.assert_called_once()

    @patch.object(JobOperations, "_get_job")
    def test_get_job(self, mock_method, mock_job_operation: JobOperations) -> None:
        from azure.ai.ml import Input, dsl, load_component

        component = load_component(source="./tests/test_configs/components/helloworld_component.yml")
        component_input = Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv")

        @dsl.pipeline()
        def sub_pipeline():
            node = component(component_in_path=component_input)

        @dsl.pipeline()
        def register_both_output():
            sub_node = sub_pipeline()

        pipeline = register_both_output()
        pipeline.settings.default_compute = "cpu-cluster"
        pipeline.jobs["sub_node"]._component = "fake_component"

        # add settings for subgraph node to simulate the result of getting pipeline that submitted with previous sdk
        pipeline.jobs["sub_node"]["settings"] = {}

        pipeline_job_base = pipeline._to_rest_object()
        mock_method.return_value = pipeline_job_base
        mock_job_operation.get(name="random_name")

    @patch.object(Job, "_from_rest_object")
    @patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"})
    def test_get_private_preview_flag_returns_latest(self, mock_method, mock_job_operation: JobOperations) -> None:
        mock_method.return_value = Command(component=None)
        mock_job_operation.get("random_name")
        mock_job_operation._operation_2023_02_preview.get.assert_called_once()

    def test_stream_command_job(self, mock_job_operation: JobOperations) -> None:
        # setup
        mock_job_operation._get_workspace_url = Mock(return_value="TheWorkSpaceUrl")
        mock_job_operation._stream_logs_until_completion = Mock()

        # go
        mock_job_operation.stream("random_name")

        # check
        mock_job_operation._operation_2023_02_preview.get.assert_called_once()
        mock_job_operation._get_workspace_url.assert_called_once()
        mock_job_operation._stream_logs_until_completion.assert_called_once()
        assert mock_job_operation._runs_operations_client._operation._client._base_url == "TheWorkSpaceUrl"

    @pytest.mark.skip(reason="Mock Job missing properties to complete full test in Feb API")
    @patch.object(Job, "_from_rest_object")
    def test_submit_command_job(self, mock_method, mock_job_operation: JobOperations) -> None:
        mock_method.return_value = Command(component=None)
        job = load_job(source="./tests/test_configs/command_job/command_job_test.yml")
        mock_job_operation.create_or_update(job=job)
        git_props = get_git_properties()
        assert git_props.items() <= job.properties.items()
        mock_job_operation._operation_2023_02_preview.create_or_update.assert_called_once()
        mock_job_operation._credential.get_token.assert_called_once_with("https://ml.azure.com/.default")

    @patch.object(Job, "_from_rest_object")
    def test_user_identity_get_aml_token(self, mock_method, mock_job_operation: JobOperations) -> None:
        mock_method.return_value = Command(component=None)
        job = load_job(source="./tests/test_configs/command_job/command_job_test_user_identity.yml")

        aml_resource_id = _get_aml_resource_id_from_metadata()
        azure_ml_scopes = _resource_to_scopes(aml_resource_id)

        with patch.object(mock_job_operation._credential, "get_token") as mock_get_token:
            mock_get_token.return_value = AccessToken(
                token=jwt.encode({"aud": aml_resource_id}, key="utf-8"), expires_on=1234
            )
            mock_job_operation.create_or_update(job=job)
            mock_job_operation._operation_2023_02_preview.create_or_update.assert_called_once()
            mock_job_operation._credential.get_token.assert_called_once_with(azure_ml_scopes[0])

        with patch.object(mock_job_operation._credential, "get_token") as mock_get_token:
            mock_get_token.return_value = AccessToken(
                token=jwt.encode({"aud": "https://management.azure.com"}, key="utf-8"), expires_on=1234
            )
            with pytest.raises(Exception):
                mock_job_operation.create_or_update(job=job)

    @pytest.mark.skip(reason="Function under test no longer returns Job as output")
    def test_command_job_resolver_with_virtual_cluster(self, mock_job_operation: JobOperations) -> None:
        expected = "/subscriptions/test_subscription/resourceGroups/test_resource_group/providers/Microsoft.MachineLearningServices/virtualclusters/testvcinmaster"
        job = load_job(source="tests/test_configs/command_job/command_job_with_virtualcluster.yaml")
        mock_job_operation._resolve_arm_id_or_upload_dependencies(job)
        assert job.compute == expected

        job = load_job(source="tests/test_configs/command_job/command_job_with_virtualcluster_2.yaml")
        mock_job_operation._resolve_arm_id_or_upload_dependencies(job)
        assert job.compute == expected

    @patch.object(Job, "_from_rest_object")
    def test_archive(self, mock_method, mock_job_operation: JobOperations) -> None:
        mock_method.return_value = Command(component=None)
        mock_job_operation.archive(name="random_name")
        mock_job_operation._operation_2023_02_preview.get.assert_called_once()
        mock_job_operation._operation_2023_02_preview.create_or_update.assert_called_once()

    @patch.object(Job, "_from_rest_object")
    def test_restore(self, mock_method, mock_job_operation: JobOperations) -> None:
        mock_method.return_value = Command(component=None)
        mock_job_operation.restore(name="random_name")
        mock_job_operation._operation_2023_02_preview.get.assert_called_once()
        mock_job_operation._operation_2023_02_preview.create_or_update.assert_called_once()

    @pytest.mark.parametrize(
        "corrupt_job_data",
        [
            "./tests/test_configs/sweep_job/corrupt_mfe_data_sweep_job.json",
        ],
    )
    def test_parse_corrupt_job_data(self, mocker: MockFixture, corrupt_job_data: str) -> None:
        with open(corrupt_job_data, "r") as f:
            resource = json.load(f)
        resource = models.JobBase.deserialize(resource)
        with pytest.raises(Exception, match="Unknown search space type"):
            # Convert from REST object
            Job._from_rest_object(resource)

    @patch.object(Job, "_from_rest_object")
    def test_job_create_skip_validation(self, mock_method, mock_job_operation: JobOperations) -> None:
        mock_method.return_value = Command(component=None)
        job = load_job("./tests/test_configs/command_job/simple_train_test.yml")
        with patch.object(JobOperations, "_validate") as mock_thing, patch.object(
            JobOperations, "_resolve_arm_id_or_upload_dependencies"
        ):
            mock_job_operation.create_or_update(job=job, skip_validation=True)
            mock_thing.assert_not_called()
            mock_job_operation.create_or_update(job=job)
            mock_thing.assert_called_once()

    def test_download_with_none(self, mock_job_operation: JobOperations) -> None:
        with pytest.raises(Exception) as ex:
            mock_job_operation.download(None)
        assert "None is a invalid input for client.jobs.get()." in ex.value.message
