# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import pytest
from unittest.mock import patch, Mock, MagicMock
from azure.ai.ml.constants import LocalEndpointConstants
from azure.ai.ml._local_endpoints import LocalEndpointMode
from azure.ai.ml._local_endpoints.docker_client import DockerClient
from azure.ai.ml._local_endpoints.vscode_debug.vscode_client import VSCodeClient
from azure.ai.ml._local_endpoints.errors import MultipleLocalDeploymentsFoundError
from pathlib import Path


@pytest.fixture
def mock_container1() -> MagicMock:
    mock_container = MagicMock()
    mock_container.labels = {"azureml-port": "5001", "endpoint-data": "{}", "deployment-data": "{}"}
    yield mock_container


@pytest.fixture
def mock_container2() -> MagicMock:
    mock_container = MagicMock()
    mock_container.labels = {"azureml-port": "5001", "endpoint-data": "{}", "deployment-data": "{}"}
    yield mock_container


@pytest.fixture
def mock_internal_docker_client(mock_container1, mock_container2):
    mock_internal_client = Mock()
    mock_internal_client.containers.list.return_value = [mock_container1, mock_container2]
    mock_internal_client.containers.get.return_value = mock_container1
    mock_internal_client.containers.create.return_value = mock_container2
    mock_internal_client.api = Mock()

    def docker_build_output():
        yield {"stream": "Successfully building docker image"}

    mock_internal_client.api.build.return_value = docker_build_output()
    yield mock_internal_client


@pytest.fixture
def mock_internal_entryscript_utility():
    yield Mock()


@pytest.fixture
def mock_internal_vscode_client():
    yield Mock()


@pytest.fixture
def mock_endpoint_docker_client(
    mock_internal_docker_client, mock_internal_vscode_client, mock_internal_entryscript_utility
) -> DockerClient:
    return DockerClient(client=mock_internal_docker_client, vscode_client=mock_internal_vscode_client)


@pytest.fixture
def mock_online_endpoint() -> Mock:
    return Mock()


@pytest.fixture
def endpoint_name() -> str:
    return "test-endpt"


@pytest.fixture
def deployment_name() -> str:
    return "blue"


@pytest.fixture
def environment_variables() -> str:
    return {LocalEndpointConstants.ENVVAR_KEY_AML_APP_ROOT: "/var/azureml-app/onlinescoring/"}


@pytest.mark.unittest
class TestLocalEndpointDockerClient:
    def test_create(
        self,
        mock_container2,
        mock_internal_docker_client,
        mock_endpoint_docker_client,
        mock_online_endpoint,
        endpoint_name,
        deployment_name,
        environment_variables,
    ):
        mock_container2.reset_mock()
        mock_internal_docker_client.containers.list.return_value = [mock_container2]
        mock_endpoint_docker_client.create_deployment(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            endpoint_metadata={},
            deployment_metadata={},
            build_directory=str(
                Path(Path(__file__).parent.resolve(), "/../../../test_configs/online_endpoint_create_mir.yml").resolve()
            ),
            dockerfile_path="/home/user/.azureml/inferencing/endpt/deployment/Dockerfile",
            conda_source_path=str(
                Path(
                    Path(__file__).parent.resolve(), "/../../../test_configs/deployments/model-1/environment/conda.yml"
                ).resolve()
            ),
            conda_yaml_contents="",
            volumes={},
            environment=environment_variables,
            azureml_port=5001,
            local_endpoint_mode=LocalEndpointMode.DetachedContainer,
        )
        mock_container2.start.assert_called_once()
        mock_container2.reload.assert_called_once()
        mock_endpoint_docker_client._client.api.build.assert_called_once()
        mock_endpoint_docker_client._client.containers.create.assert_called_once()

    def test_create_byoc(
        self,
        mock_container2,
        mock_internal_docker_client,
        mock_endpoint_docker_client,
        mock_online_endpoint,
        endpoint_name,
        deployment_name,
        environment_variables,
    ):
        mock_container2.reset_mock()
        mock_internal_docker_client.containers.list.return_value = [mock_container2]
        mock_endpoint_docker_client.create_deployment(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            endpoint_metadata={},
            deployment_metadata={},
            build_directory=str(
                Path(Path(__file__).parent.resolve(), "/../../../test_configs/online_endpoint_create_mir.yml").resolve()
            ),
            dockerfile_path=None,
            conda_source_path=str(
                Path(
                    Path(__file__).parent.resolve(), "/../../../test_configs/deployments/model-1/environment/conda.yml"
                ).resolve()
            ),
            conda_yaml_contents="",
            volumes={},
            environment=environment_variables,
            azureml_port=8501,
            local_endpoint_mode=LocalEndpointMode.DetachedContainer,
            prebuilt_image_name="mock-image",
        )
        mock_container2.start.assert_called_once()
        mock_container2.reload.assert_called_once()
        mock_endpoint_docker_client._client.api.build.assert_not_called()
        mock_endpoint_docker_client._client.containers.create.assert_called_once()

    def test_create_with_vscode(
        self,
        mock_container2,
        mock_internal_docker_client,
        mock_internal_vscode_client,
        mock_endpoint_docker_client,
        mock_online_endpoint,
        endpoint_name,
        deployment_name,
        environment_variables,
    ):
        mock_container2.reset_mock()
        mock_container2.get_archive.return_value = [MagicMock(), MagicMock()]
        mock_internal_docker_client.containers.list.return_value = [mock_container2]
        mock_internal_docker_client.containers.create.return_value = mock_container2
        test_build_dir = str(Path(Path.home(), ".azureml", "inferencing").resolve())
        mock_endpoint_docker_client.create_deployment(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            endpoint_metadata={},
            deployment_metadata={},
            build_directory=test_build_dir,
            dockerfile_path="/home/user/.azureml/inferencing/endpt/deployment/Dockerfile",
            conda_source_path=str(
                Path(
                    Path(__file__).parent.resolve(), "/../../../test_configs/deployments/model-1/environment/conda.yml"
                ).resolve()
            ),
            conda_yaml_contents="",
            volumes={},
            environment=environment_variables,
            azureml_port=5001,
            local_endpoint_mode=LocalEndpointMode.VSCodeDevContainer,
        )
        mock_container2.remove.assert_called()
        mock_internal_vscode_client.invoke_dev_container.assert_called_once()
        mock_endpoint_docker_client._client.api.build.assert_called_once()
        mock_endpoint_docker_client._client.containers.create.assert_called_once()

    def test_delete(self, mock_endpoint_docker_client, mock_container1, endpoint_name, deployment_name):
        mock_container1.reset_mock()
        mock_endpoint_docker_client.delete(endpoint_name=endpoint_name, deployment_name=deployment_name)
        mock_endpoint_docker_client._client.containers.list.assert_called_once()
        mock_container1.stop.assert_called_once()
        mock_container1.remove.assert_called_once()

    def test_get_with_deployment(self, mock_endpoint_docker_client, endpoint_name, deployment_name):
        mock_endpoint_docker_client.get_deployment(endpoint_name=endpoint_name, deployment_name=deployment_name)
        mock_endpoint_docker_client._client.containers.list.assert_called_once()
        mock_endpoint_docker_client._client.containers.get.assert_not_called()

    def test_get_without_deployment(self, mock_endpoint_docker_client, endpoint_name):
        mock_endpoint_docker_client.get_deployment(endpoint_name=endpoint_name)
        mock_endpoint_docker_client._client.containers.list.assert_called_once()
        mock_endpoint_docker_client._client.containers.get.assert_not_called()

    def test_get_scoring_uri_with_deployment(
        self, mock_container2, mock_internal_docker_client, mock_endpoint_docker_client, endpoint_name, deployment_name
    ):
        mock_internal_docker_client.containers.list.return_value = [mock_container2]
        mock_endpoint_docker_client.get_scoring_uri(endpoint_name=endpoint_name, deployment_name=deployment_name)
        mock_endpoint_docker_client._client.containers.list.assert_called_once()
        mock_endpoint_docker_client._client.containers.get.assert_not_called()

    def test_get_scoring_uri_without_deployment(self, mock_endpoint_docker_client, endpoint_name):
        with pytest.raises(MultipleLocalDeploymentsFoundError):
            mock_endpoint_docker_client.get_scoring_uri(endpoint_name=endpoint_name)
        mock_endpoint_docker_client._client.containers.list.assert_called_once()
        mock_endpoint_docker_client._client.containers.get.assert_not_called()

    def test_get_logs_with_deployment(self, mock_endpoint_docker_client, endpoint_name, deployment_name):
        mock_endpoint_docker_client.logs(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            lines=100,
        )
        mock_endpoint_docker_client._client.containers.list.assert_called_once()
        mock_endpoint_docker_client._client.containers.get.assert_not_called()

    def test_list_containers(
        self, mock_internal_docker_client, mock_endpoint_docker_client, endpoint_name, deployment_name
    ):
        mock_endpoint_docker_client.list_containers(endpoint_name=endpoint_name)
        mock_endpoint_docker_client._client.containers.list.assert_called_once()
        mock_endpoint_docker_client._client.containers.get.assert_not_called()

    @pytest.mark.parametrize(
        "docker_client_input_volumes, expected_volumes",
        [
            pytest.param(
                {"src1:dst1": {"src1": {"bind": "dst1"}}, "src2:dst2": {"src2": {"bind": "dst2"}}},
                ["src1:dst1", "src2:dst2"],
            ),
            pytest.param(
                {"src:codedest": {"src": {"bind": "codedest"}}, "src:modeldest": {"src": {"bind": "modeldest"}}},
                ["src:codedest", "src:modeldest"],
            ),
        ],
    )
    def test_reformat_volumes(
        self,
        mock_endpoint_docker_client,
        docker_client_input_volumes,
        expected_volumes,
    ):
        reformatted_volumes = mock_endpoint_docker_client._reformat_volumes(docker_client_input_volumes)
        assert reformatted_volumes == expected_volumes
