import pytest
from unittest.mock import Mock, patch

from azure.ai.ml.operations import ComponentOperations
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.core.exceptions import HttpResponseError


class MockResponse:
    def __init__(self, code, reason=None):
        self.status_code = code
        self.reason = reason

    def raise_for_status(self):
        return


@pytest.fixture
def mock_component_operation(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock, mock_machinelearning_client: Mock
) -> ComponentOperations:
    yield ComponentOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_05_01,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.mark.unittest
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
