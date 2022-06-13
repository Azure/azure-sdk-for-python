import pytest
from typing import Callable
from unittest.mock import Mock, patch

from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml._operations import ComponentOperations
from azure.ai.ml._scope_dependent_operations import OperationScope

from azure.ai.ml._restclient.v2022_05_01.models import (
    ComponentContainerData,
    ComponentContainerDetails,
    ComponentVersionData,
    ComponentVersionDetails,
)


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
class TestComponentOperation:
    def test_create(self, mock_component_operation: ComponentOperations, randstr: Callable[[], str]) -> None:
        component = CommandComponent(
            name=randstr(), version="1", environment="azureml:AzureML-Minimal:1", command="echo hello"
        )

        with patch.object(ComponentOperations, "_upload_dependencies") as mock_thing, patch(
            "azure.ai.ml._operations.component_operations.Component._from_rest_object",
            return_value=CommandComponent(),
        ):
            mock_component_operation.create_or_update(component)
            mock_thing.assert_called_once()

        mock_component_operation._version_operation.create_or_update.assert_called_once_with(
            name=component.name,
            version="1",
            body=component._to_rest_object(),
            resource_group_name=mock_component_operation._operation_scope.resource_group_name,
            workspace_name=mock_component_operation._workspace_name,
        )

    def test_create_autoincrement(
        self, mock_component_operation: ComponentOperations, randstr: Callable[[], str]
    ) -> None:
        component = CommandComponent(
            name=randstr(), version=None, environment="azureml:AzureML-Minimal:1", command="echo hello"
        )
        assert component._auto_increment_version
        with patch.object(ComponentOperations, "_upload_dependencies") as mock_thing, patch(
            "azure.ai.ml._operations.component_operations.Component._from_rest_object", return_value=component
        ):
            mock_component_operation.create_or_update(component)
            mock_thing.assert_called_once()

        mock_component_operation._container_operation.get.assert_called_once_with(
            name=component.name,
            resource_group_name=mock_component_operation._operation_scope.resource_group_name,
            workspace_name=mock_component_operation._operation_scope.workspace_name,
        )
        mock_component_operation._version_operation.create_or_update.assert_called_once_with(
            name=component.name,
            version=mock_component_operation._container_operation.get().properties.next_version,
            body=component._to_rest_object(),
            resource_group_name=mock_component_operation._operation_scope.resource_group_name,
            workspace_name=mock_component_operation._operation_scope.workspace_name,
        )

    def test_list(self, mock_component_operation: ComponentOperations) -> None:
        mock_component_operation.list(name="mock")
        mock_component_operation._version_operation.list.assert_called_once()
        mock_component_operation.list()
        mock_component_operation._container_operation.list.assert_called_once()

    def test_get(self, mock_component_operation: ComponentOperations) -> None:
        with patch("azure.ai.ml._operations.component_operations.Component") as mock_component_entity:
            mock_component_operation.get("mock_component", "1")

        mock_component_operation._version_operation.get.assert_called_once()
        create_call_args_str = str(mock_component_operation._version_operation.get.call_args)
        assert "name='mock_component'" in create_call_args_str
        assert "version='1'" in create_call_args_str
        mock_component_entity._from_rest_object.assert_called_once()

    def test_archive_version(self, mock_component_operation: ComponentOperations, randstr: Callable[[], str]):
        name = randstr()
        component = Mock(ComponentVersionData(properties=Mock(ComponentVersionDetails())))
        version = "1"
        mock_component_operation._version_operation.get.return_value = component
        mock_component_operation.archive(name=name, version=version)

        mock_component_operation._version_operation.create_or_update.assert_called_with(
            name=name,
            version=version,
            workspace_name=mock_component_operation._workspace_name,
            body=component,
            resource_group_name=mock_component_operation._resource_group_name,
        )

    def test_archive_container(self, mock_component_operation: ComponentOperations, randstr: Callable[[], str]):
        name = randstr()
        component = Mock(ComponentContainerData(properties=Mock(ComponentContainerDetails())))
        mock_component_operation._container_operation.get.return_value = component
        mock_component_operation.archive(name=name)

        mock_component_operation._container_operation.create_or_update.assert_called_with(
            name=name,
            workspace_name=mock_component_operation._workspace_name,
            body=component,
            resource_group_name=mock_component_operation._resource_group_name,
        )

    def test_restore_version(self, mock_component_operation: ComponentOperations, randstr: Callable[[], str]):
        name = randstr()
        component = Mock(ComponentVersionData(properties=Mock(ComponentVersionDetails())))
        version = "1"
        mock_component_operation._version_operation.get.return_value = component
        mock_component_operation.restore(name=name, version=version)

        mock_component_operation._version_operation.create_or_update.assert_called_with(
            name=name,
            version=version,
            workspace_name=mock_component_operation._workspace_name,
            body=component,
            resource_group_name=mock_component_operation._resource_group_name,
        )

    def test_restore_container(self, mock_component_operation: ComponentOperations, randstr: Callable[[], str]):
        name = randstr()
        component = Mock(ComponentContainerData(properties=Mock(ComponentContainerDetails())))
        mock_component_operation._container_operation.get.return_value = component
        mock_component_operation.restore(name=name)

        mock_component_operation._container_operation.create_or_update.assert_called_with(
            name=name,
            workspace_name=mock_component_operation._workspace_name,
            body=component,
            resource_group_name=mock_component_operation._resource_group_name,
        )
