from typing import Callable, Iterable
from unittest.mock import Mock, patch

import pytest
from pytest_mock import MockFixture

from azure.ai.ml import load_environment
from azure.ai.ml._restclient.v2022_05_01.models import (
    EnvironmentContainerData,
    EnvironmentContainerDetails,
    EnvironmentVersionData,
    EnvironmentVersionDetails,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.constants._common import ARM_ID_PREFIX, OrderString
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.operations import DatastoreOperations, EnvironmentOperations
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.core.paging import ItemPaged


@pytest.fixture
def mock_datastore_operations(
    mock_workspace_scope: OperationScope, mock_operation_config: OperationConfig, mock_aml_services_2022_05_01: Mock
) -> CodeOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        serviceclient_2022_05_01=mock_aml_services_2022_05_01,
    )


@pytest.fixture
def mock_environment_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_machinelearning_client: Mock,
    mock_aml_services_2022_05_01: Mock,
) -> EnvironmentOperations:
    yield EnvironmentOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_05_01,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.mark.unittest
@pytest.mark.production_experience_test
class TestEnvironmentOperations:
    @patch.object(Environment, "_from_rest_object", new=Mock())
    @patch.object(Environment, "_from_container_rest_object", new=Mock())
    def test_list(self, mock_environment_operation: EnvironmentOperations) -> None:
        mock_environment_operation._version_operations.list.return_value = [Mock(Environment) for _ in range(10)]
        mock_environment_operation._containers_operations.list.return_value = [Mock(Environment) for _ in range(10)]
        result = mock_environment_operation.list()
        assert isinstance(result, Iterable)
        mock_environment_operation._containers_operations.list.assert_called_once()
        mock_environment_operation.list(name="name")
        mock_environment_operation._version_operations.list.assert_called_once()

    def test_list_versions(self, mock_environment_operation: EnvironmentOperations) -> None:
        mock_environment_operation.list(name="name")
        mock_environment_operation._version_operations.list.assert_called_once()

    def test_list_versions_with_azureml_prefix(
        self, mock_environment_operation: EnvironmentOperations
    ) -> None:
        name = "random_name"
        with patch("azure.ai.ml.operations._environment_operations.Environment._from_rest_object", return_value=None):
            mock_environment_operation.list(name=ARM_ID_PREFIX + name)
        mock_environment_operation._version_operations.list.assert_called_once()
        args, kwargs = mock_environment_operation._version_operations.list.call_args
        assert ARM_ID_PREFIX + name == kwargs.get("name")

    def test_get(self, mock_environment_operation: EnvironmentOperations) -> None:
        with patch("azure.ai.ml.operations._environment_operations.Environment._from_rest_object", return_value=None):
            mock_environment_operation.get("random_name", "1")
        mock_environment_operation._version_operations.get.assert_called_once()

    def test_get_with_azureml_prefix(
        self, mock_environment_operation: EnvironmentOperations
    ) -> None:
        name = "random_name"
        with patch("azure.ai.ml.operations._environment_operations.Environment._from_rest_object", return_value=None):
            mock_environment_operation.get(ARM_ID_PREFIX + name, "random_name")
        mock_environment_operation._version_operations.get.assert_called_once()
        args, kwargs = mock_environment_operation._version_operations.get.call_args
        assert name == kwargs.get("name")

    def test_get_no_version(
        self, mock_environment_operation: EnvironmentOperations
    ) -> None:
        name = "random_name"
        with pytest.raises(Exception):
            mock_environment_operation.get(name=name)

    def test_create_or_update(self, mock_environment_operation: EnvironmentOperations) -> None:
        env = load_environment(source="./tests/test_configs/environment/environment_conda.yml")
        with patch("azure.ai.ml.operations._environment_operations.Environment._from_rest_object", return_value=None):
            _ = mock_environment_operation.create_or_update(env)
        mock_environment_operation._version_operations.create_or_update.assert_called_once()

    def test_create_autoincrement(
        self,
        mock_environment_operation: EnvironmentOperations,
        mock_workspace_scope: OperationScope,
    ) -> None:

        mock_environment_operation._containers_operations.get.return_value = Mock(EnvironmentContainerDetails())

        with patch("azure.ai.ml.operations._environment_operations.Environment._from_rest_object", return_value=None):
            env = load_environment(source="./tests/test_configs/environment/environment_conda.yml")
            env.version = None
            mock_environment_operation.create_or_update(env)
            mock_environment_operation._version_operations.create_or_update.assert_called_once()
            mock_environment_operation._containers_operations.get.assert_called_once_with(
                name=env.name,
                resource_group_name=mock_workspace_scope.resource_group_name,
                workspace_name=mock_workspace_scope.workspace_name,
            )
            mock_environment_operation._version_operations.create_or_update.assert_called_once_with(
                body=env._to_rest_object(),
                name=env.name,
                version=mock_environment_operation._containers_operations.get().properties.next_version,
                resource_group_name=mock_workspace_scope.resource_group_name,
                workspace_name=mock_workspace_scope.workspace_name,
            )

    def test_archive_version(self, mock_environment_operation: EnvironmentOperations):
        name = "random_name"
        env_version = Mock(EnvironmentVersionData(properties=Mock(EnvironmentVersionDetails())))
        version = "1"
        mock_environment_operation._version_operations.get.return_value = env_version
        mock_environment_operation.archive(name=name, version=version)

        mock_environment_operation._version_operations.create_or_update.assert_called_with(
            name=name,
            version=version,
            workspace_name=mock_environment_operation._workspace_name,
            body=env_version,
            resource_group_name=mock_environment_operation._resource_group_name,
        )

    def test_archive_container(self, mock_environment_operation: EnvironmentOperations):
        name = "random_name"
        env_container = Mock(EnvironmentContainerData(properties=Mock(EnvironmentContainerDetails())))
        mock_environment_operation._containers_operations.get.return_value = env_container
        mock_environment_operation.archive(name=name)

        mock_environment_operation._containers_operations.create_or_update.assert_called_with(
            name=name,
            workspace_name=mock_environment_operation._workspace_name,
            body=env_container,
            resource_group_name=mock_environment_operation._resource_group_name,
        )

    def test_restore_version(self, mock_environment_operation: EnvironmentOperations):
        name = "random_name"
        env_version = Mock(EnvironmentVersionData(properties=Mock(EnvironmentVersionDetails())))
        version = "1"
        mock_environment_operation._version_operations.get.return_value = env_version
        mock_environment_operation.restore(name=name, version=version)

        mock_environment_operation._version_operations.create_or_update.assert_called_with(
            name=name,
            version=version,
            workspace_name=mock_environment_operation._workspace_name,
            body=env_version,
            resource_group_name=mock_environment_operation._resource_group_name,
        )

    def test_restore_container(self, mock_environment_operation: EnvironmentOperations):
        name = "random_name"
        env_container = Mock(EnvironmentContainerData(properties=Mock(EnvironmentContainerDetails())))
        mock_environment_operation._containers_operations.get.return_value = env_container
        mock_environment_operation.restore(name=name)

        mock_environment_operation._containers_operations.create_or_update.assert_called_with(
            name=name,
            workspace_name=mock_environment_operation._workspace_name,
            body=env_container,
            resource_group_name=mock_environment_operation._resource_group_name,
        )
