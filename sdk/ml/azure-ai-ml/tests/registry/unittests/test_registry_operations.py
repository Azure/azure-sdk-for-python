from typing import Callable
from unittest.mock import DEFAULT, Mock, call, patch

import pytest
from pytest_mock import MockFixture

from azure.ai.ml import load_registry
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
@pytest.mark.production_experiences_test
class TestRegistryOperations:
    def test_list(self, mock_registry_operation: RegistryOperations) -> None:
        # Test different input options for the scope value
        mock_registry_operation.list()
        mock_registry_operation._operation.list.assert_called_once()

        mock_registry_operation.list(scope="invalid")
        assert mock_registry_operation._operation.list.call_count == 2
        mock_registry_operation._operation.list_by_subscription.assert_not_called()

        mock_registry_operation.list(scope="subscription")
        assert mock_registry_operation._operation.list.call_count == 2
        mock_registry_operation._operation.list_by_subscription.assert_called_once()

    def test_get(self, mock_registry_operation: RegistryOperations, randstr: Callable[[], str]) -> None:
        mock_registry_operation.get(f"unittest_{randstr('reg_name')}")
        mock_registry_operation._operation.get.assert_called_once()

    def test_check_registry_name(self, mock_registry_operation: RegistryOperations):
        mock_registry_operation._default_registry_name = None
        with pytest.raises(Exception):
            mock_registry_operation._check_registry_name(None)

    def test_create(self, mock_registry_operation: RegistryOperations, randstr: Callable[[], str]) -> None:
        reg_name = f"unittest{randstr('reg_name')}"
        params_override = [{"name": reg_name}]
        reg = load_registry(
            source="./tests/test_configs/registry/registry_valid_min.yaml", params_override=params_override
        )
        # valid creation of new registry
        mock_registry_operation.begin_create(registry=reg)
        mock_registry_operation._operation.begin_create_or_update.assert_called_once()

    def test_delete(self, mock_registry_operation: RegistryOperations, randstr: Callable[[], str]) -> None:
        mock_registry_operation.begin_delete(name="some registry")
        mock_registry_operation._operation.begin_delete.assert_called_once()
