from unittest.mock import Mock, patch

import pytest

from azure.ai.ml._restclient.v2022_05_01.models import (
    EnvironmentVersionData,
    EnvironmentVersionDetails,
)

from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.operations import EnvironmentOperations
from azure.ai.ml import load_environment


@pytest.fixture
def mock_environment_operation(
    mock_registry_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2021_10_01_dataplanepreview: Mock,
    mock_machinelearning_registry_client: Mock,
) -> EnvironmentOperations:
    yield EnvironmentOperations(
        operation_scope=mock_registry_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2021_10_01_dataplanepreview,
        all_operations=mock_machinelearning_registry_client._operation_container,
    )


@pytest.mark.unittest
class TestEnvironmentOperation:
    def test_archive_version(self, mock_environment_operation: EnvironmentOperations):
        name = "random_name"
        env_version = Mock(EnvironmentVersionData(properties=Mock(EnvironmentVersionDetails())))
        version = "1"
        mock_environment_operation._version_operations.get.return_value = env_version
        mock_environment_operation.archive(name=name, version=version)

        mock_environment_operation._version_operations.begin_create_or_update.assert_called_with(
            name=name,
            version=version,
            registry_name=mock_environment_operation._registry_name,
            body=env_version,
            resource_group_name=mock_environment_operation._resource_group_name,
        )

    def test_restore_version(self, mock_environment_operation: EnvironmentOperations):
        name = "random_name"
        env_version = Mock(EnvironmentVersionData(properties=Mock(EnvironmentVersionDetails())))
        version = "1"
        mock_environment_operation._version_operations.get.return_value = env_version
        mock_environment_operation.restore(name=name, version=version)

        mock_environment_operation._version_operations.begin_create_or_update.assert_called_with(
            name=name,
            version=version,
            registry_name=mock_environment_operation._registry_name,
            body=env_version,
            resource_group_name=mock_environment_operation._resource_group_name,
        )
