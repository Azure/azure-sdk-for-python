from typing import Callable
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml._restclient.v2022_05_01.models import (
    ComponentContainerData,
    ComponentContainerDetails,
    ComponentVersionData,
    ComponentVersionDetails,
    SystemData,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.operations import ComponentOperations

from .._util import _COMPONENT_TIMEOUT_SECOND


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
def dummy_component():
    return CommandComponent(
        name="random_name", version="1", environment="azureml:AzureML-Minimal:1", command="echo hello"
    )


@pytest.fixture
def mock_component_from_rest(dummy_component: Component):
    with patch(
        "azure.ai.ml.operations._component_operations.Component._from_rest_object",
        return_value=dummy_component,
    ) as mock_from_rest:
        yield mock_from_rest


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestComponentOperation:
    def test_create(
        self, mock_component_operation: ComponentOperations, dummy_component: Component, mock_component_from_rest
    ) -> None:
        with patch.object(ComponentOperations, "_resolve_arm_id_or_upload_dependencies") as mock_thing:
            mock_component_operation.create_or_update(dummy_component)
            mock_thing.assert_called_once()

        mock_component_operation._version_operation.create_or_update.assert_called_once_with(
            name=dummy_component.name,
            version="1",
            body=dummy_component._to_rest_object(),
            resource_group_name=mock_component_operation._operation_scope.resource_group_name,
            workspace_name=mock_component_operation._workspace_name,
        )

    def test_create_skip_validation(self, mock_component_operation: ComponentOperations) -> None:
        component = CommandComponent(
            name="random_name", version="1", environment="azureml:AzureML-Minimal:1", command="echo hello"
        )

        with patch.object(ComponentOperations, "_validate") as mock_thing, patch.object(
            ComponentOperations, "_resolve_arm_id_or_upload_dependencies"
        ), patch(
            "azure.ai.ml.operations._component_operations.Component._from_rest_object",
            return_value=CommandComponent(),
        ):
            mock_component_operation.create_or_update(component, skip_validation=True)
            mock_thing.assert_not_called()
            mock_component_operation.create_or_update(component)
            mock_thing.assert_called_once()

    def test_create_autoincrement(
        self, mock_component_operation: ComponentOperations, mock_component_from_rest
    ) -> None:
        dummy_auto_increment_component = CommandComponent(
            name="random_name", version=None, environment="azureml:AzureML-Minimal:1", command="echo hello"
        )
        assert dummy_auto_increment_component._auto_increment_version
        with patch.object(ComponentOperations, "_resolve_arm_id_or_upload_dependencies") as mock_thing:
            mock_component_operation.create_or_update(dummy_auto_increment_component)
            mock_thing.assert_called_once()

        mock_component_operation._version_operation.create_or_update.assert_called_once_with(
            name=dummy_auto_increment_component.name,
            version=mock_component_operation._container_operation.get().properties.next_version,
            body=dummy_auto_increment_component._to_rest_object(),
            resource_group_name=mock_component_operation._operation_scope.resource_group_name,
            workspace_name=mock_component_operation._operation_scope.workspace_name,
        )

    def test_list(self, mock_component_operation: ComponentOperations) -> None:
        mock_component_operation.list(name="mock")
        mock_component_operation._version_operation.list.assert_called_once()
        mock_component_operation.list()
        mock_component_operation._container_operation.list.assert_called_once()

    def test_get(self, mock_component_operation: ComponentOperations, mock_component_from_rest) -> None:
        mock_component_operation.get("mock_component", "1")

        mock_component_operation._version_operation.get.assert_called_once()
        create_call_args_str = str(mock_component_operation._version_operation.get.call_args)
        assert "name='mock_component'" in create_call_args_str
        assert "version='1'" in create_call_args_str
        mock_component_from_rest.assert_called_once()

    def test_get_default(self, mock_component_operation: ComponentOperations, mock_component_from_rest) -> None:
        mock_component_operation.get("mock_component")

        mock_component_operation._version_operation.get.assert_called_once()
        create_call_args_str = str(mock_component_operation._version_operation.get.call_args)
        assert "name='mock_component'" in create_call_args_str
        mock_component_from_rest.assert_called_once()

    def test_archive_version(self, mock_component_operation: ComponentOperations):
        name = "random_name"
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

    def test_archive_container(self, mock_component_operation: ComponentOperations):
        name = "random_name"
        component = Mock(ComponentContainerData(properties=Mock(ComponentContainerDetails())))
        mock_component_operation._container_operation.get.return_value = component
        mock_component_operation.archive(name=name)

        mock_component_operation._container_operation.create_or_update.assert_called_with(
            name=name,
            workspace_name=mock_component_operation._workspace_name,
            body=component,
            resource_group_name=mock_component_operation._resource_group_name,
        )

    def test_restore_version(self, mock_component_operation: ComponentOperations):
        name = "random_name"
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

    def test_restore_container(self, mock_component_operation: ComponentOperations):
        name = "random_name"
        component = Mock(ComponentContainerData(properties=Mock(ComponentContainerDetails())))
        mock_component_operation._container_operation.get.return_value = component
        mock_component_operation.restore(name=name)

        mock_component_operation._container_operation.create_or_update.assert_called_with(
            name=name,
            workspace_name=mock_component_operation._workspace_name,
            body=component,
            resource_group_name=mock_component_operation._resource_group_name,
        )

    def test_list_with_latest_version(self, mock_component_operation: ComponentOperations) -> None:
        def create_component_with_latest_version(latest_version):
            component_container_detail = ComponentContainerDetails()
            component_container_detail.latest_version = latest_version

            component_container_data = ComponentContainerData(properties=component_container_detail)
            component_container_data.system_data = SystemData()

            component = Component._from_container_rest_object(component_container_data)
            return component

        component_1 = create_component_with_latest_version("1")
        component_2 = create_component_with_latest_version("2")
        component_3 = create_component_with_latest_version("3")
        mock_component_operation._container_operation.list.return_value = [component_1, component_2, component_3]
        result = mock_component_operation.list()

        latest_version_list = [item.latest_version for item in result]
        assert latest_version_list == ["1", "2", "3"]
