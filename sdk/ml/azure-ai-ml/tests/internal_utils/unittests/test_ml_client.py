import logging
import os
from unittest.mock import Mock, patch

import mock
import pytest
from test_utilities.constants import Test_Resource_Group, Test_Subscription

from azure.ai.ml import (
    MLClient,
    load_batch_deployment,
    load_batch_endpoint,
    load_component,
    load_compute,
    load_data,
    load_datastore,
    load_environment,
    load_job,
    load_model,
    load_online_deployment,
    load_online_endpoint,
    load_registry,
    load_workspace,
    load_connection,
)
from azure.ai.ml._azure_environments import AzureEnvironments, _get_default_cloud_name
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._telemetry import get_appinsights_log_handler
from azure.ai.ml._telemetry.logging_handler import AzureMLSDKLogHandler
from azure.ai.ml._user_agent import USER_AGENT
from azure.ai.ml.constants._common import AZUREML_CLOUD_ENV_NAME
from azure.ai.ml.exceptions import ValidationException
from azure.identity import ClientSecretCredential, DefaultAzureCredential


@pytest.mark.unittest
@pytest.mark.core_sdk_test
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

    def test_get_sub_and_rg(self) -> None:
        client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id="fake-sub-id",
            resource_group_name="fake-rg-name",
        )

        assert "fake-sub-id" == client.subscription_id
        assert "fake-rg-name" == client.resource_group_name

    def test_show_progress(self) -> None:
        client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id="fake-sub-id",
            resource_group_name="fake-rg-name",
        )

        assert client.jobs._show_progress  # By default show_progress is True
        assert client.data._show_progress
        assert client.models._show_progress

        client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id="fake-sub-id",
            resource_group_name="fake-rg-name",
            show_progress=False,
        )

        assert not client.jobs._show_progress
        assert not client.data._show_progress
        assert not client.models._show_progress

    @patch("azure.ai.ml._ml_client._get_base_url_from_metadata")
    def test_mfe_url_overwrite(self, mock_get_mfe_url_override, mock_credential):
        mock_url = "http://localhost:65535/mferp/managementfrontend"
        mock_get_mfe_url_override.return_value = mock_url

        ml_client = MLClient(
            credential=mock_credential,
            subscription_id=Test_Subscription,
            resource_group_name=Test_Resource_Group,
        )

        assert ml_client.workspaces._operation._client._base_url == mock_url
        assert ml_client.compute._operation._client._base_url == mock_url
        assert ml_client.jobs._operation_2023_02_preview._client._base_url == mock_url
        assert ml_client.jobs._kwargs["enforce_https"] is False

    # @patch("azure.ai.ml._ml_client.RegistryOperations", Mock())
    @patch("azure.ai.ml._ml_client.ComputeOperations", Mock())
    @patch("azure.ai.ml._ml_client.DatastoreOperations", Mock())
    @patch("azure.ai.ml._ml_client.JobOperations", Mock())
    @patch("azure.ai.ml._ml_client.WorkspaceOperations", Mock())
    @patch("azure.ai.ml._ml_client.ModelOperations", Mock())
    @patch("azure.ai.ml._ml_client.DataOperations", Mock())
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
                [load_job("tests/test_configs/command_job/simple_train_test.yml")],
                {},
                "jobs",
                1,
                "create_or_update",
            ),
            (
                [load_job("tests/test_configs/sweep_job/sweep_job_minimal_test.yaml")],
                {},
                "jobs",
                3,
                "create_or_update",
            ),
            (
                [load_job("tests/test_configs/pipeline_jobs/helloworld_pipeline_job.yml")],
                {},
                "jobs",
                3,
                "create_or_update",
            ),
            (
                [load_model("tests/test_configs/model/model_full.yml")],
                {},
                "models",
                1,
                "create_or_update",
            ),
            (
                [load_environment("tests/test_configs/environment/environment_conda.yml")],
                {},
                "environments",
                1,
                "create_or_update",
            ),
            (
                [load_datastore("tests/test_configs/datastore/blob_store.yml")],
                {},
                "datastores",
                1,
                "create_or_update",
            ),
            (
                [
                    load_job("tests/test_configs/command_job/simple_train_test.yml"),
                    "soemthing_else",
                ],
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
        # trying to change this whole file to use assertRaises caused half the existing test to fail
        no_second_impl = False
        try:
            ml_client.begin_create_or_update(*args, **kwargs)
        except TypeError:
            no_second_impl = True
        finally:
            assert no_second_impl

    @patch("azure.ai.ml._ml_client.ComputeOperations", Mock())
    @patch("azure.ai.ml._ml_client.DatastoreOperations", Mock())
    @patch("azure.ai.ml._ml_client.JobOperations", Mock())
    @patch("azure.ai.ml._ml_client.WorkspaceOperations", Mock())
    @patch("azure.ai.ml._ml_client.RegistryOperations", Mock())
    @patch("azure.ai.ml._ml_client.ModelOperations", Mock())
    @patch("azure.ai.ml._ml_client.DataOperations", Mock())
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
                [load_compute("tests/test_configs/compute/compute-ci.yaml")],
                {},
                "compute",
                1,
                "begin_create_or_update",
            ),
            (
                [load_workspace("tests/test_configs/workspace/workspace_full.yaml")],
                {},
                "workspaces",
                1,
                "begin_create",
            ),
            (
                [load_registry("tests/test_configs/registry/registry_valid.yaml")],
                {},
                "registries",
                1,
                "begin_create_or_update",
            ),
            (
                [load_online_endpoint("tests/test_configs/endpoints/online/online_endpoint_create_k8s.yml")],
                {},
                "online_endpoints",
                1,
                "begin_create_or_update",
            ),
            (
                [load_online_deployment("tests/test_configs/deployments/online/online_deployment_blue.yaml")],
                {},
                "online_deployments",
                1,
                "begin_create_or_update",
            ),
            (
                [load_online_deployment("tests/test_configs/deployments/online/online_deployment_blue.yaml")],
                {"local": True, "vscode_debug": True, "no_wait": True},
                "online_deployments",
                2,
                "begin_create_or_update",
            ),
            (
                [load_online_deployment("tests/test_configs/deployments/online/online_deployment_blue.yaml")],
                {"local": True, "no_wait": True},
                "online_deployments",
                2,
                "begin_create_or_update",
            ),
            (
                [load_batch_endpoint("tests/test_configs/endpoints/batch/batch_endpoint_mlflow.yaml")],
                {},
                "batch_endpoints",
                1,
                "begin_create_or_update",
            ),
            (
                [load_batch_deployment("tests/test_configs/deployments/batch/batch_deployment_1.yaml")],
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
        # trying to change this whole file to use assertRaises caused half the existing test to fail
        no_second_impl = False
        try:
            ml_client.create_or_update(*args, **kwargs)
        except TypeError:
            no_second_impl = True
        finally:
            assert no_second_impl

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

    def test_ml_client_without_credentials(self):
        credential = None
        with pytest.raises(Exception) as e:
            MLClient(
                credential=credential,
                subscription_id=Test_Subscription,
                resource_group_name=Test_Resource_Group,
                workspace_name="test-ws",
            )
        assert "credential can not be None" in str(e)

    def test_ml_client_for_china_cloud(self, mock_credential):
        cloud_name = AzureEnvironments.ENV_CHINA
        base_url = "https://management.chinacloudapi.cn"
        kwargs = {"cloud": cloud_name}
        ml_client = MLClient(
            credential=mock_credential,
            subscription_id=Test_Subscription,
            resource_group_name=Test_Resource_Group,
            workspace_name="test-ws1",
            **kwargs,
        )
        assert ml_client._cloud == cloud_name
        assert ml_client._base_url == base_url
        assert ml_client._kwargs["cloud"] == cloud_name
        assert base_url in str(ml_client._kwargs["credential_scopes"])

    def test_ml_client_for_govt__cloud(self, mock_credential):
        cloud_name = AzureEnvironments.ENV_US_GOVERNMENT
        base_url = "https://management.usgovcloudapi.net"
        kwargs = {"cloud": cloud_name}
        ml_client = MLClient(
            credential=mock_credential,
            subscription_id=Test_Subscription,
            resource_group_name=Test_Resource_Group,
            workspace_name="test-ws1",
            **kwargs,
        )
        assert ml_client._cloud == cloud_name
        assert ml_client._base_url == base_url
        assert ml_client._kwargs["cloud"] == cloud_name
        assert base_url in str(ml_client._kwargs["credential_scopes"])

    def test_ml_client_for_default_cloud(self, mock_credential):
        cloud_name = AzureEnvironments.ENV_DEFAULT
        base_url = "https://management.azure.com"
        kwargs = {}
        # Remove the keys from the variables
        key_to_remove = {AZUREML_CLOUD_ENV_NAME}
        modified_environment = {k: v for k, v in os.environ.items() if k not in key_to_remove}
        with mock.patch.dict(os.environ, modified_environment, clear=True):
            ml_client = MLClient(
                credential=mock_credential,
                subscription_id=Test_Subscription,
                resource_group_name=Test_Resource_Group,
                workspace_name="test-ws1",
                **kwargs,
            )
            assert ml_client._cloud == cloud_name
            assert ml_client._base_url == base_url
            assert ml_client._kwargs["cloud"] == cloud_name
            assert base_url in str(ml_client._kwargs["credential_scopes"])

    def test_ml_client_with_invalid_cloud(self, mock_credential):
        kwargs = {"cloud": "SomeInvalidCloudName"}
        with pytest.raises(Exception) as e:
            ml_client = MLClient(
                credential=mock_credential,
                subscription_id=Test_Subscription,
                resource_group_name=Test_Resource_Group,
                workspace_name="test-ws1",
                **kwargs,
            )
            assert ml_client._kwargs["cloud"] == "SomeInvalidCloudName"
        assert "Unknown cloud environment supplied" in str(e)

    def test_ml_client_with_both_workspace_registry_names_throws(
        self, e2e_ws_scope: OperationScope, auth: ClientSecretCredential
    ) -> None:
        with pytest.raises(ValidationException) as exception:
            MLClient(
                credential=auth,
                workspace_name=e2e_ws_scope.workspace_name,
                registry_name="testfeed",
            )
        message = exception.value.args[0]
        assert message == "Both workspace_name and registry_name cannot be used together, for the ml_client."

    def test_ml_client_with_cli_config(self, mock_credential):
        # This cloud config should not work and it should NOT overwrite the hardcoded AzureCloud
        kwargs = {
            "cloud": "AzureCloud",
            "cloud_metadata": {
                "azure_portal": "https://test.portal.azure.com/",
                "resource_manager": "https://test.management.azure.com/",
                "active_directory": "https://test.login.microsoftonline.com/",
                "aml_resource_id": "https://test.ml.azure.com/",
                "storage_endpoint": "test.core.windows.net",
                "registry_discovery_endpoint": "https://test.eastus.api.azureml.ms/",
            },
        }
        ml_client = MLClient(
            credential=mock_credential,
            subscription_id=Test_Subscription,
            resource_group_name=Test_Resource_Group,
            workspace_name="test-ws1",
            **kwargs,
        )
        assert ml_client._cloud == "AzureCloud"
        assert ml_client._base_url != "https://test.management.azure.com"
        assert _get_default_cloud_name() == "AzureCloud"

        # This full cloud config should be added fine
        kwargs = {
            "cloud": "test_cloud",
            "cloud_metadata": {
                "azure_portal": "https://test.portal.azure.com/",
                "resource_manager": "https://test.management.azure.com/",
                "active_directory": "https://test.login.microsoftonline.com/",
                "aml_resource_id": "https://test.ml.azure.com/",
                "storage_endpoint": "test.core.windows.net",
                "registry_discovery_endpoint": "https://test.eastus.api.azureml.ms/",
            },
        }
        ml_client = MLClient(
            credential=mock_credential,
            subscription_id=Test_Subscription,
            resource_group_name=Test_Resource_Group,
            workspace_name="test-ws1",
            **kwargs,
        )
        assert ml_client._cloud == "test_cloud"
        assert ml_client._base_url == "https://test.management.azure.com"
        assert _get_default_cloud_name() == "test_cloud"

        # We shouldn't need to add it to the kwargs a second time, just the cloud name
        kwargs = {"cloud": "test_cloud"}
        ml_client = MLClient(
            credential=mock_credential,
            subscription_id=Test_Subscription,
            resource_group_name=Test_Resource_Group,
            workspace_name="test-ws1",
            **kwargs,
        )

        assert ml_client._cloud == "test_cloud"
        assert ml_client._base_url == "https://test.management.azure.com"
        assert _get_default_cloud_name() == "test_cloud"

    def test_enable_telemetry(self) -> None:
        subscription_id = "fake-sub-id"
        resource_group_name = "fake-rg-name"

        client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
        )

        assert client.jobs._enable_telemetry  # By default enable_telemetry is True
        assert client.data._enable_telemetry
        assert client.models._enable_telemetry

        enable_telemetry = client.jobs._enable_telemetry

        # confirm that telemetry is DISABLED when not in jupyter notebook even with enable_telemetry=True
        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=False):
            properties = {
                "subscription_id": subscription_id,
                "resource_group_name": resource_group_name,
            }
            handler, _ = get_appinsights_log_handler(
                USER_AGENT, **{"properties": properties}, enable_telemetry=enable_telemetry
            )
            assert enable_telemetry
            assert isinstance(handler, logging.NullHandler)

        # confirm that telemetry is ENABLED when in jupyter notebook and enable_telemetry=True
        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=True):
            properties = {
                "subscription_id": subscription_id,
                "resource_group_name": resource_group_name,
            }
            handler, _ = get_appinsights_log_handler(
                USER_AGENT, **{"properties": properties}, enable_telemetry=enable_telemetry
            )
            assert enable_telemetry
            assert isinstance(handler, AzureMLSDKLogHandler)

        client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id="fake-sub-id",
            resource_group_name="fake-rg-name",
            enable_telemetry=False,
        )

        assert not client.jobs._enable_telemetry
        assert not client.data._enable_telemetry
        assert not client.models._enable_telemetry

        enable_telemetry = client.jobs._enable_telemetry

        # confirm that telemetry is DISABLED when not in jupyter notebook and enable_telemetry=False
        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=False):
            properties = {
                "subscription_id": subscription_id,
                "resource_group_name": resource_group_name,
            }
            handler, _ = get_appinsights_log_handler(
                USER_AGENT, **{"properties": properties}, enable_telemetry=enable_telemetry
            )
            assert not enable_telemetry
            assert isinstance(handler, logging.NullHandler)

        # confirm that telemetry is DISABLED when in jupyter notebook and enable_telemetry=False
        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=True):
            properties = {
                "subscription_id": subscription_id,
                "resource_group_name": resource_group_name,
            }
            handler, _ = get_appinsights_log_handler(
                USER_AGENT, **{"properties": properties}, enable_telemetry=enable_telemetry
            )
            assert not enable_telemetry
            assert isinstance(handler, logging.NullHandler)
