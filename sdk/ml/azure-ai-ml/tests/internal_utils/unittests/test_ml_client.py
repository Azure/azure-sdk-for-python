from unittest.mock import Mock, patch

import pytest
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    BatchDeployment,
    BatchEndpoint,
    CommandJob,
    Component,
    Compute,
    Datastore,
    Environment,
    Model,
    OnlineDeployment,
    OnlineEndpoint,
    PipelineJob,
    Workspace,
)
from azure.ai.ml.sweep import SweepJob
from tests.test_utilities.constants import Test_Resource_Group, Test_Subscription


@pytest.mark.unittest
class TestMachineLearningClient:
    def test_get_workspaces(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.workspaces is not None

    def test_get_jobs(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.jobs is not None

    def test_get_computes(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.compute is not None

    def test_get_datastore(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.datastores is not None

    def test_get_online_endpoints(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.online_endpoints is not None

    def test_get_batch_endpoints(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.batch_endpoints is not None

    def test_get_online_deployments(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.online_deployments is not None

    def test_get_batch_deployments(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.batch_deployments is not None

    def test_get_model(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.models is not None

    def test_get_data(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.data is not None

    def test_get_dataset(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.datasets is not None

    def test_get_code(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client._code is not None

    def test_default_workspace_name_match(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.workspace_name is not None

    def test_set_workspace_name(self, mock_machinelearning_client: MLClient) -> None:
        previous_ws = mock_machinelearning_client.workspace_name
        new_ws = "new-ws"

        new_client = mock_machinelearning_client._get_new_client(new_ws)
        assert new_ws == new_client.workspace_name
        assert previous_ws == mock_machinelearning_client.workspace_name

    @pytest.mark.skip(reason="Skipping until MFE Feb API is available in all regions")
    @patch("azure.ai.ml._ml_client._get_mfe_url_override")
    def test_mfe_url_overwrite(self, mock_get_mfe_url_override, mock_credential):
        base_url = "https://management.azure.com"
        mock_url = "http://localhost:65535/mferp/managementfrontend"
        mock_get_mfe_url_override.return_value = mock_url

        ml_client = MLClient(
            credential=mock_credential, subscription_id=Test_Subscription, resource_group_name=Test_Resource_Group
        )

        assert ml_client.workspaces._operation._client._base_url == base_url
        assert ml_client.compute._operation._client._base_url == base_url
        assert ml_client.jobs._operation_2022_02_preview._client._base_url == mock_url
        assert ml_client.jobs._kwargs["enforce_https"] is False

    @patch("azure.ai.ml._ml_client.ComputeOperations", Mock())
    @patch("azure.ai.ml._ml_client.DatastoreOperations", Mock())
    @patch("azure.ai.ml._ml_client.JobOperations", Mock())
    @patch("azure.ai.ml._ml_client.WorkspaceOperations", Mock())
    @patch("azure.ai.ml._ml_client.ModelOperations", Mock())
    @patch("azure.ai.ml._ml_client.DataOperations", Mock())
    @patch("azure.ai.ml._ml_client.DatasetOperations", Mock())
    @patch("azure.ai.ml._ml_client.CodeOperations", Mock())
    @patch("azure.ai.ml._ml_client.EnvironmentOperations", Mock())
    @patch("azure.ai.ml._ml_client.ComponentOperations", Mock())
    @patch("azure.ai.ml._ml_client.OnlineEndpointOperations", Mock())
    @patch("azure.ai.ml._ml_client.BatchEndpointOperations", Mock())
    @patch("azure.ai.ml._ml_client.OnlineDeploymentOperations", Mock())
    @patch("azure.ai.ml._ml_client.BatchDeploymentOperations", Mock())
    @pytest.mark.parametrize(
        "args, kwargs, ops_name, call_times, create_method_name",
        [
            (
                [CommandJob.load("tests/test_configs/command_job/simple_train_test.yml")],
                {},
                "jobs",
                1,
                "create_or_update",
            ),
            (
                [SweepJob.load("tests/test_configs/sweep_job/sweep_job_minimal_test.yaml")],
                {},
                "jobs",
                3,
                "create_or_update",
            ),
            (
                [PipelineJob.load("tests/test_configs/pipeline_jobs/helloworld_pipeline_job.yml")],
                {},
                "jobs",
                3,
                "create_or_update",
            ),
            ([Model.load("tests/test_configs/model/model_full.yml")], {}, "models", 1, "create_or_update"),
            (
                [Environment.load("tests/test_configs/environment/environment_conda.yml")],
                {},
                "environments",
                1,
                "create_or_update",
            ),
            ([Datastore.load("tests/test_configs/datastore/blob_store.yml")], {}, "datastores", 1, "create_or_update"),
            (
                [CommandJob.load("tests/test_configs/command_job/simple_train_test.yml"), "soemthing_else"],
                {},
                "takes 2 positional arguments but 3 were given",
                -1,
                TypeError,
            ),
        ],
    )
    def test_polymorphic_create_or_update(
        self, args, kwargs, ops_name, call_times, create_method_name, mock_credential
    ) -> None:
        ml_client = MLClient(
            credential=mock_credential,
            subscription_id=Test_Subscription,
            resource_group_name=Test_Resource_Group,
            workspace_name="test-ws",
        )
        # in the case of faults, if call_times is -1, it is used as a flag to indicate that the test should fail
        # if call_times == -1, the ops_name is reused as message error
        # the create_method_name is reused as the exception type
        if call_times == -1:
            with pytest.raises(create_method_name) as e:
                ml_client.create_or_update(*args, **kwargs)
            assert ops_name in str(e.value)
        elif call_times == 1:
            ml_client.create_or_update(*args, **kwargs)
            ml_client.__getattribute__(ops_name).__getattr__(create_method_name).assert_called_once_with(
                *args, **kwargs
            )
        else:
            ml_client.create_or_update(*args, **kwargs)
            ml_client.__getattribute__(ops_name).__getattr__(create_method_name).assert_called_with(*args, **kwargs)

    @patch("azure.ai.ml._ml_client.ComputeOperations", Mock())
    @patch("azure.ai.ml._ml_client.DatastoreOperations", Mock())
    @patch("azure.ai.ml._ml_client.JobOperations", Mock())
    @patch("azure.ai.ml._ml_client.WorkspaceOperations", Mock())
    @patch("azure.ai.ml._ml_client.ModelOperations", Mock())
    @patch("azure.ai.ml._ml_client.DataOperations", Mock())
    @patch("azure.ai.ml._ml_client.DatasetOperations", Mock())
    @patch("azure.ai.ml._ml_client.CodeOperations", Mock())
    @patch("azure.ai.ml._ml_client.EnvironmentOperations", Mock())
    @patch("azure.ai.ml._ml_client.ComponentOperations", Mock())
    @patch("azure.ai.ml._ml_client.OnlineEndpointOperations", Mock())
    @patch("azure.ai.ml._ml_client.BatchEndpointOperations", Mock())
    @patch("azure.ai.ml._ml_client.OnlineDeploymentOperations", Mock())
    @patch("azure.ai.ml._ml_client.BatchDeploymentOperations", Mock())
    @pytest.mark.parametrize(
        "args, kwargs, ops_name, call_times, create_method_name",
        [
            ([Compute.load("tests/test_configs/compute/compute-ci.yaml")], {}, "compute", 1, "begin_create_or_update"),
            ([Workspace.load("tests/test_configs/workspace/workspace_full.yaml")], {}, "workspaces", 1, "begin_create"),
            (
                [OnlineEndpoint.load("tests/test_configs/endpoints/online/online_endpoint_create_k8s.yml")],
                {},
                "online_endpoints",
                1,
                "begin_create_or_update",
            ),
            (
                [OnlineDeployment.load("tests/test_configs/deployments/online/online_deployment_blue.yaml")],
                {},
                "online_deployments",
                1,
                "begin_create_or_update",
            ),
            (
                [OnlineDeployment.load("tests/test_configs/deployments/online/online_deployment_blue.yaml")],
                {"local": True, "vscode_debug": True, "no_wait": True},
                "online_deployments",
                2,
                "begin_create_or_update",
            ),
            (
                [OnlineDeployment.load("tests/test_configs/deployments/online/online_deployment_blue.yaml")],
                {"local": True, "no_wait": True},
                "online_deployments",
                2,
                "begin_create_or_update",
            ),
            (
                [BatchEndpoint.load("tests/test_configs/endpoints/batch/batch_endpoint_mlflow.yaml")],
                {},
                "batch_endpoints",
                1,
                "begin_create_or_update",
            ),
            (
                [BatchDeployment.load("tests/test_configs/deployments/batch/batch_deployment_1.yaml")],
                {},
                "batch_deployments",
                1,
                "begin_create_or_update",
            ),
        ],
    )
    def test_polymorphic_begin_create_or_update(
        self, args, kwargs, ops_name, call_times, create_method_name, mock_credential
    ) -> None:
        ml_client = MLClient(
            credential=mock_credential,
            subscription_id=Test_Subscription,
            resource_group_name=Test_Resource_Group,
            workspace_name="test-ws",
        )
        # in the case of faults, if call_times is -1, it is used as a flag to indicate that the test should fail
        # if call_times == -1, the ops_name is reused as message error
        # the create_method_name is reused as the exception type
        if call_times == -1:
            with pytest.raises(create_method_name) as e:
                ml_client.begin_create_or_update(*args, **kwargs)
            assert ops_name in str(e.value)
        elif call_times == 1:
            ml_client.begin_create_or_update(*args, **kwargs)
            ml_client.__getattribute__(ops_name).__getattr__(create_method_name).assert_called_once_with(
                *args, **kwargs
            )
        else:
            ml_client.begin_create_or_update(*args, **kwargs)
            ml_client.__getattribute__(ops_name).__getattr__(create_method_name).assert_called_with(*args, **kwargs)

    def test_load_config(self, tmp_path, mock_credential):
        root = tmp_path
        start = root
        for i in range(5):
            start = start / f"sub{i}"
            start.mkdir()

        config = root / "config.json"
        sub = "b17253fa-f327-42d6-9686-f3e553e24523"
        rg = "fake_resource_group"
        ws = "fake_workspace"
        CONTENT = f"""
{{
  "subscription_id": "{sub}",
  "resource_group": "{rg}",
  "workspace_name": "{ws}"
}}
"""
        config.write_text(CONTENT)

        client = MLClient.from_config(credential=mock_credential, path=start)
        assert client.workspace_name == ws
        assert client._operation_scope.subscription_id == sub
        assert client._operation_scope.resource_group_name == rg

    def test_load_config_not_found(self, tmp_path):
        root = tmp_path
        start = root
        for i in range(5):
            start = start / f"sub{i}"
            start.mkdir()
        with pytest.raises(Exception) as e:
            MLClient.from_config(start)
        assert "could not find config.json in:" in str(e)
