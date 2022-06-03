from pathlib import Path
from typing import Callable

from unittest.mock import patch, Mock
from azure.ai.ml.entities._deployment.online_deployment import (
    OnlineDeployment,
    KubernetesOnlineDeployment,
    ManagedOnlineDeployment,
)
import pytest

from azure.core.polling import LROPoller
from azure.ai.ml._operations import (
    OnlineDeploymentOperations,
    WorkspaceOperations,
)
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.constants import (
    AzureMLResourceType,
)

from pytest_mock import MockFixture


@pytest.fixture()
def mock_delete_poller() -> LROPoller:
    poller = Mock(spec_set=LROPoller)
    poller.result = lambda timeout: None
    poller.done = lambda: True
    yield poller


@pytest.fixture
def blue_online_mir_deployment_yaml(tmp_path: Path, resource_group_name: str) -> Path:
    content = """
name: blue
endpoint_name: mirendpoint
model: azureml:models/my-model-m1:1
code_configuration:
  code: ./src/onlinescoring/
  scoring_script: m1/score.py
environment:
    name: sklearn-mir-env
    version: 1
    path: .
    conda_file: file:./environment/endpoint_conda.yml
scale_settings:
  scale_type: default
request_settings:
    request_timeout_ms: 3000
    max_concurrent_requests_per_instance: 1
    max_queue_wait_ms: 3000
resources:
    requests:
        cpu: "1.5"
        memory: "1.0"
"""
    p = tmp_path / "blue_online_deployment_mir.yaml"
    p.write_text(content)
    return p


@pytest.fixture
def blue_online_k8s_deployment_yaml(tmp_path: Path, resource_group_name: str) -> Path:
    content = """
name: blue
type: kubernetes
description: deployment blue based on arc connected kubernetes
endpoint_name: k8sendpoint
tags:
  isTest: true
model: azureml:k8s-model:1
code_configuration:
  code: ./src/onlinescoring/
  scoring_script: score.py
environment: azureml:env-blue:1
scale_settings:
  type: default
instance_count: 2
request_settings:
    request_timeout_ms: 3000
    max_concurrent_requests_per_instance: 1
    max_queue_wait_ms: 3000
instance_type: cpuInstance
liveness_probe:
  period: 10
  initial_delay: 10
  timeout: 10
  success_threshold: 1
  failure_threshold: 3
resources:
    requests:
        cpu: "0.1"
        memory: "0.1Gi"
    limits:
      cpu: "0.3"
      memory: "0.2Gi"
"""
    p = tmp_path / "blue_online_deployment_k8s.yaml"
    p.write_text(content)
    return p


@pytest.fixture
def mock_workspace_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2021_10_01: Mock,
    mock_machinelearning_client: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2021_10_01,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.fixture
def mock_local_deployment_helper() -> Mock:
    yield Mock()


@pytest.fixture
def mock_online_deployment_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2021_10_01: Mock,
    mock_machinelearning_client: Mock,
) -> OnlineDeploymentOperations:
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.WORKSPACE, mock_workspace_operations)

    yield OnlineDeploymentOperations(
        operation_scope=mock_workspace_scope,
        service_client_02_2022_preview=mock_aml_services_2021_10_01,
        all_operations=mock_machinelearning_client._operation_container,
        local_deployment_helper=mock_local_deployment_helper,
    )


@pytest.mark.unittest
class TestOnlineDeploymentOperations:
    def test_online_deployment_k8s_create(
        self,
        mock_online_deployment_operations: OnlineDeploymentOperations,
        rand_compute_name: Callable[[], str],
        blue_online_k8s_deployment_yaml: str,
        mocker: MockFixture,
    ) -> None:
        mocker.patch(
            "azure.ai.ml._operations.online_deployment_operations.OnlineDeploymentOperations._get_workspace_location",
            return_value="xxx",
        )
        mock_create_or_update_online_deployment = mocker.patch.object(
            OnlineDeploymentOperations, "begin_create_or_update", autospec=True
        )
        online_deployment = OnlineDeployment.load(blue_online_k8s_deployment_yaml)
        online_deployment.name = rand_compute_name()
        assert online_deployment.instance_type
        mock_online_deployment_operations.begin_create_or_update(deployment=online_deployment)
        mock_create_or_update_online_deployment.assert_called_once()

    def test_delete_online_deployment(
        self,
        mock_online_deployment_operations: OnlineDeploymentOperations,
        mock_aml_services_2021_10_01: Mock,
        mocker: MockFixture,
        randstr: Callable[[], str],
        mock_delete_poller: LROPoller,
    ) -> None:
        random_name = randstr()
        mock_aml_services_2021_10_01.online_deployments.begin_delete.return_value = mock_delete_poller
        mock_online_deployment_operations.delete(endpoint_name="k8sendpoint", name=random_name)
        mock_online_deployment_operations._online_deployment.begin_delete.assert_called_once()
