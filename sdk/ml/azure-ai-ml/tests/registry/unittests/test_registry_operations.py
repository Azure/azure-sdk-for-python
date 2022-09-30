from typing import Callable
from unittest.mock import DEFAULT, Mock, call, patch

import pytest
from pytest_mock import MockFixture

from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities._registry.registry import Registry
from azure.ai.ml.operations import RegistryOperations
from azure.core.exceptions import ResourceExistsError
from azure.core.polling import LROPoller


@pytest.fixture
def mock_registry_operation(
    mock_registry_scope: OperationScope,
    mock_aml_services_2022_01_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> RegistryOperations:
    yield RegistryOperations(
        operation_scope=mock_registry_scope,
        service_client=mock_aml_services_2022_01_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
    )


@pytest.mark.unittest
class TestRegistryOperation:
    def test_list(self, mock_registry_operation: RegistryOperations) -> None:
        mock_registry_operation.list()
        mock_registry_operation._operation.list_by_subscription.assert_called_once()

    def test_get(self, mock_registry_operation: RegistryOperations) -> None:
        mock_registry_operation.get("random_name")
        mock_registry_operation._operation.get.assert_called_once()

    def test_check_registry_name(self, mock_registry_operation: RegistryOperations):
        mock_registry_operation._default_registry_name = None
        with pytest.raises(Exception):
            mock_registry_operation._check_registry_name(None)
