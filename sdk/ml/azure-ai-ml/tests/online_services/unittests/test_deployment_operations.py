from unittest.mock import Mock, patch

import pytest

from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.operations import OnlineDeploymentOperations


@pytest.fixture
def mock_endpoint_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_02_01_preview: Mock,
    mock_aml_services_2020_09_01_dataplanepreview: Mock,
    mock_machinelearning_client: Mock,
    mock_environment_operations: Mock,
    mock_model_operations: Mock,
    mock_code_assets_operations: Mock,
    mock_data_operations: Mock,
    mock_local_endpoint_helper: Mock,
) -> OnlineDeploymentOperations:
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.CODE, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.MODEL, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.ENVIRONMENT, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.DATA, mock_data_operations)

    yield OnlineDeploymentOperations(
        operation_scope=mock_workspace_scope,
        service_client_02_2022_preview=mock_aml_services_2022_02_01_preview,
        service_client_09_2020_dataplanepreview=mock_aml_services_2020_09_01_dataplanepreview,
        all_operations=mock_machinelearning_client._operation_container,
        local_endpoint_helper=mock_local_endpoint_helper,
    )


@pytest.mark.unittest
@pytest.mark.production_experience_test
class TestOnlineEndpointsOperations:
    def test_mock_endpoint_operation(mock_endpoint_operations):
        assert mock_endpoint_operations is not None
