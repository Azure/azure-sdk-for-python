from unittest.mock import Mock

import pytest
from azure.ai.ml import load_capability_host

from azure.ai.ml._scope_dependent_operations import OperationScope, OperationConfig
from azure.ai.ml.operations._capability_hosts_operations import (
    CapabilityHostsOperations,
)
from azure.ai.ml.exceptions import MlException


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_capability_hosts_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2024_10_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> CapabilityHostsOperations:
    yield CapabilityHostsOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client_10_2024=mock_aml_services_2024_10_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
    )


@pytest.fixture
def mock_invalid_capability_hosts_operation(
    mock_registry_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2024_10_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> CapabilityHostsOperations:
    yield CapabilityHostsOperations(
        operation_scope=mock_registry_scope,
        operation_config=mock_operation_config,
        service_client_10_2024=mock_aml_services_2024_10_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
    )


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestCapabilityHostOperation:
    def test_begin_create_or_update(self, mock_capability_hosts_operation: CapabilityHostsOperations) -> None:
        """Test create or update CapabilityHost."""
        capability_host = load_capability_host(
            source="./tests/test_configs/workspace/ai_workspaces/test_capability_host_hub.yml"
        )
        mock_capability_hosts_operation.begin_create_or_update(capability_host=capability_host)
        mock_capability_hosts_operation._capability_hosts_operations.begin_create_or_update.assert_called_once()

    def test_get(self, mock_capability_hosts_operation: CapabilityHostsOperations) -> None:
        """Test get CapabilityHost."""
        mock_capability_hosts_operation.get(name="test_capability_host")
        mock_capability_hosts_operation._capability_hosts_operations.get.assert_called_once_with(
            name="test_capability_host",
            resource_group_name=mock_capability_hosts_operation._operation_scope.resource_group_name,
            workspace_name=mock_capability_hosts_operation._operation_scope.workspace_name,
        )

    def test_delete(self, mock_capability_hosts_operation: CapabilityHostsOperations) -> None:
        """Test delete CapabilityHost."""
        mock_capability_hosts_operation.begin_delete(name="test_capability_host")
        mock_capability_hosts_operation._capability_hosts_operations.begin_delete.assert_called_once_with(
            name="test_capability_host",
            resource_group_name=mock_capability_hosts_operation._operation_scope.resource_group_name,
            workspace_name=mock_capability_hosts_operation._operation_scope.workspace_name,
            polling=True,
        )

    def test_begin_create_or_update_failure_for_invalid_wsname(
        self, mock_invalid_capability_hosts_operation: CapabilityHostsOperations
    ) -> None:
        """Test exception if workspace name is empty or invalid."""
        capability_host = load_capability_host(
            source="./tests/test_configs/workspace/ai_workspaces/test_capability_host_hub.yml"
        )
        with pytest.raises(MlException) as ve:
            mock_invalid_capability_hosts_operation.begin_create_or_update(capability_host=capability_host)
        assert (
            "Please pass either a hub name or project name to the workspace_name parameter when initializing an MLClient object."
            in ve.value.args[0]
        )
