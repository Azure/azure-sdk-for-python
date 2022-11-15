from unittest.mock import Mock, patch

import pytest
from pytest_mock import MockFixture

from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationsContainer, OperationScope
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml.operations import ComponentOperations
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.ai.ml.operations._operation_orchestrator import OperationOrchestrator
from azure.core.exceptions import HttpResponseError


class MockResponse:
    def __init__(self, code, reason=None):
        self.status_code = code
        self.reason = reason

    def raise_for_status(self):
        return


@pytest.fixture
def mock_component_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_machinelearning_client: Mock,
) -> ComponentOperations:
    yield ComponentOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_05_01,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.fixture
def code_operations(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml.operations._code_operations.CodeOperations")


@pytest.fixture
def operation_container(
    code_operations: CodeOperations,
) -> OperationsContainer:
    container = OperationsContainer()
    container.add(AzureMLResourceType.CODE, code_operations)
    yield container


@pytest.fixture
def operation_orchestrator(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    operation_container: OperationsContainer,
) -> OperationOrchestrator:
    yield OperationOrchestrator(
        operation_container=operation_container,
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
    )


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestExceptions:
    def test_error_preprocess(self, mock_component_operation: ComponentOperations):
        with patch.object(mock_component_operation._version_operation, "get") as mock_client:
            mock_client.side_effect = HttpResponseError(response=MockResponse(code=400))
            with pytest.raises(HttpResponseError) as context:
                mock_component_operation.get("mock_component", "0.0.1")
            assert context.type.__name__ == "HttpResponseError"

            mock_client.side_effect = KeyboardInterrupt()
            with pytest.raises(BaseException) as context:
                mock_component_operation.get("mock_component", "0.0.1")
            assert context.type.__name__ == "KeyboardInterrupt"

    def test_get_code_asset_arm_id(self, operation_orchestrator: OperationOrchestrator):
        with patch.object(operation_orchestrator, "_validate_datastore_name") as mock_client:
            mock_client.side_effect = ValidationException(
                message="raise ValidationException error", no_personal_data_message="raise ValidationException error"
            )
            with pytest.raises(ValidationException) as context:
                operation_orchestrator.get_asset_arm_id(asset=Code(), azureml_type=AzureMLResourceType.CODE)
            assert context.type.__name__ == "ValidationException"
