from pathlib import Path
from typing import Callable
from unittest.mock import Mock, patch

import pytest
from pytest_mock import MockFixture

from azure.ai.ml import load_batch_deployment
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities._deployment.batch_deployment import BatchDeployment
from azure.ai.ml.operations import BatchDeploymentOperations, WorkspaceOperations
from azure.core.polling import LROPoller


@pytest.fixture()
def mock_delete_poller() -> LROPoller:
    poller = Mock(spec_set=LROPoller)
    poller.result = lambda timeout: None
    poller.done = lambda: True
    yield poller


@pytest.fixture
def create_yaml_happy_path(tmp_path: Path) -> Path:
    content = """
name: blue
endpoint_name: batch-ept
description: description for my batch deployment
compute: "azureml:testCompute"
resources:
  instance_count: 2
"""
    p = tmp_path / "create_happy_path_batch_deployment.yaml"
    p.write_text(content)
    return p


@pytest.fixture
def mock_workspace_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_10_01: Mock,
    mock_machinelearning_client: Mock,
    mock_aml_services_workspace_dataplane: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_10_01,
        all_operations=mock_machinelearning_client._operation_container,
        dataplane_client=mock_aml_services_workspace_dataplane,
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
    )


@pytest.fixture
def mock_local_endpoint_helper() -> Mock:
    yield Mock()


@pytest.fixture
def mock_batch_deployment_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2024_01_01_preview: Mock,
    mock_aml_services_2023_02_01_preview: Mock,
    mock_aml_services_2020_09_01_dataplanepreview: Mock,
    mock_machinelearning_client: Mock,
) -> BatchDeploymentOperations:
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.WORKSPACE, mock_workspace_operations)
    kwargs = {
        "service_client_09_2020_dataplanepreview": mock_aml_services_2020_09_01_dataplanepreview,
        "service_client_02_2023_preview": mock_aml_services_2023_02_01_preview,
    }

    yield BatchDeploymentOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client_01_2024_preview=mock_aml_services_2024_01_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
        **kwargs,
    )


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestBatchDeploymentOperations:
    def test_batch_deployment_create(
        self,
        mock_batch_deployment_operations: BatchDeploymentOperations,
        create_yaml_happy_path: str,
        mocker: MockFixture,
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._batch_deployment_operations.BatchDeploymentOperations._get_workspace_location",
            return_value="xxx",
        )
        mock_create_or_update_batch_deployment = mocker.patch.object(
            BatchDeploymentOperations, "begin_create_or_update", autospec=True
        )
        batch_deployment = load_batch_deployment(create_yaml_happy_path)
        batch_deployment.name = "random_compute_name"
        mock_batch_deployment_operations.begin_create_or_update(deployment=batch_deployment)
        mock_create_or_update_batch_deployment.assert_called_once()

    def test_batch_list(self, mock_batch_deployment_operations: BatchDeploymentOperations) -> None:
        mock_batch_deployment_operations.list(endpoint_name="batch-ept")
        mock_batch_deployment_operations._batch_deployment.list.assert_called_once()

    def test_list_deployment_jobs(
        self, mock_batch_deployment_operations: BatchDeploymentOperations, mocker: MockFixture
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._batch_deployment_operations._get_mfe_base_url_from_discovery_service",
            return_value="https://somebatch-url.com",
        )
        mockresponse = Mock()
        mockresponse.text = '{"key": "value"}'
        mockresponse.status_code = 200
        mocker.patch("requests.request", return_value=mockresponse)

        mock_batch_deployment_operations.list_jobs(endpoint_name="batch-ept", name="testdeployment")
        mock_batch_deployment_operations._batch_job_deployment.list.assert_called_once()

    def test_delete_batch_endpoint(
        self,
        mock_batch_deployment_operations: BatchDeploymentOperations,
        mock_aml_services_2024_01_01_preview: Mock,
        mocker: MockFixture,
        mock_delete_poller: LROPoller,
    ) -> None:
        random_name = "random_name"
        mock_aml_services_2024_01_01_preview.batch_deployments.begin_delete.return_value = mock_delete_poller
        mock_batch_deployment_operations.begin_delete(endpoint_name="batch-ept", name=random_name)
        mock_batch_deployment_operations._batch_deployment.begin_delete.assert_called_once()
