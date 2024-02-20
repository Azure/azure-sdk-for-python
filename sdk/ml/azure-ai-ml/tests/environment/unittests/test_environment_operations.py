from typing import Iterable
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml import load_environment
from azure.ai.ml._restclient.v2022_05_01.models import (
    EnvironmentContainerData,
    EnvironmentContainerDetails,
    EnvironmentVersionData,
    EnvironmentVersionDetails,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.constants._common import ARM_ID_PREFIX
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.operations import EnvironmentOperations
from azure.core.exceptions import ResourceNotFoundError


@pytest.fixture
def mock_environment_operation_reg(
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
@pytest.mark.production_experiences_test
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

    def test_list_versions_with_azureml_prefix(self, mock_environment_operation: EnvironmentOperations) -> None:
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

    def test_get_with_azureml_prefix(self, mock_environment_operation: EnvironmentOperations) -> None:
        name = "random_name"
        with patch("azure.ai.ml.operations._environment_operations.Environment._from_rest_object", return_value=None):
            mock_environment_operation.get(ARM_ID_PREFIX + name, "random_name")
        mock_environment_operation._version_operations.get.assert_called_once()
        args, kwargs = mock_environment_operation._version_operations.get.call_args
        assert name == kwargs.get("name")

    def test_get_no_version(self, mock_environment_operation: EnvironmentOperations) -> None:
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
        env = load_environment(source="./tests/test_configs/environment/environment_no_version.yml")
        assert env._auto_increment_version
        env.version = None
        with patch(
            "azure.ai.ml.operations._environment_operations.Environment._from_rest_object", return_value=None
        ), patch(
            "azure.ai.ml.operations._environment_operations._get_next_version_from_container", return_value="version"
        ) as mock_nextver:
            mock_environment_operation.create_or_update(env)
            mock_nextver.assert_called_once()

            mock_environment_operation._version_operations.create_or_update.assert_called_once_with(
                body=env._to_rest_object(),
                name=env.name,
                version=mock_nextver.return_value,
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

    # #Mock(azure.ai.ml._restclient.v2021_10_01_dataplanepreview.operations._environment_versions_operations, "get")
    # def test_promote_environment_from_workspace(
    #     self,
    #     mock_environment_operation_reg: EnvironmentOperations,
    #     mock_environment_operation: EnvironmentOperations,
    # ) -> None:
    #     env = load_environment(source="./tests/test_configs/environment/environment_conda.yml")

    #     mock_environment_operation_reg._version_operations.get.side_effect = Mock(
    #         side_effect=ResourceNotFoundError("Test")
    #     )

    #     shared_environment = mock_environment_operation.share(env.name, env.version, "new_name", "new_version", "registry_name")
    #     # assert environment_to_promote.name == "new_name"
    #     # assert environment_to_promote.version == "new_version"

    #     # mock_environment_operation_reg.create_or_update(environment_to_promote)
    #     mock_environment_operation_reg._service_client.resource_management_asset_reference.begin_import_method.assert_called_once()
