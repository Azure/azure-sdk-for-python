from typing import Callable
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml._restclient.v2022_05_01.models import (
    ComponentContainerData,
    ComponentContainerDetails,
    ComponentVersionData,
    ComponentVersionDetails,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty
from azure.ai.ml.operations import ComponentOperations

from .._util import _COMPONENT_TIMEOUT_SECOND


@pytest.fixture
def mock_component_operation(
    mock_registry_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2021_10_01_dataplanepreview: Mock,
    mock_machinelearning_registry_client: Mock,
) -> ComponentOperations:
    yield ComponentOperations(
        operation_scope=mock_registry_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2021_10_01_dataplanepreview,
        all_operations=mock_machinelearning_registry_client._operation_container,
    )


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestComponentOperation:
    def test_create_in_non_ipp_registry(self, mock_component_operation: ComponentOperations) -> None:
        component = CommandComponent(
            name="random_name", version="1", environment="azureml:AzureML-Minimal:1", command="echo hello"
        )

        with patch.object(ComponentOperations, "_resolve_arm_id_or_upload_dependencies") as mock_thing, patch(
            "azure.ai.ml.operations._component_operations.Component._from_rest_object",
            return_value=CommandComponent(),
        ):
            mock_component_operation.create_or_update(component)
            mock_thing.assert_called_once()

        mock_component_operation._version_operation.begin_create_or_update.assert_called_once()

    @pytest.mark.usefixtures("enable_private_preview_schema_features")
    def test_create_in_ipp_registry(self, mock_component_operation: ComponentOperations) -> None:
        component = CommandComponent(
            name="random_name",
            version="1",
            environment="azureml:AzureML-Minimal:1",
            command="echo hello",
            intellectual_property=IntellectualProperty(publisher="contoso", protection_level="all"),
        )

        with patch.object(ComponentOperations, "_resolve_arm_id_or_upload_dependencies") as mock_thing, patch(
            "azure.ai.ml.operations._component_operations.Component._from_rest_object",
            return_value=CommandComponent(),
        ):
            mock_component_operation.create_or_update(component)
            # for IPP components, we need to make sure _resolve_arm_id_or_upload_dependencies is not called
            mock_thing.assert_not_called()

    def test_list(self, mock_component_operation: ComponentOperations) -> None:
        mock_component_operation.list(name="mock")
        mock_component_operation._version_operation.list.assert_called_once()
        mock_component_operation.list()
        mock_component_operation._container_operation.list.assert_called_once()

    def test_get(self, mock_component_operation: ComponentOperations) -> None:
        with patch("azure.ai.ml.operations._component_operations.Component") as mock_component_entity:
            mock_component_operation.get("mock_component", "1")

        mock_component_operation._version_operation.get.assert_called_once()
        create_call_args_str = str(mock_component_operation._version_operation.get.call_args)
        assert "name='mock_component'" in create_call_args_str
        assert "version='1'" in create_call_args_str
        mock_component_entity._from_rest_object.assert_called_once()

    def test_archive_version(self, mock_component_operation: ComponentOperations):
        name = "random_name"
        component = Mock(ComponentVersionData(properties=Mock(ComponentVersionDetails())))
        version = "1"
        mock_component_operation._version_operation.get.return_value = component
        mock_component_operation.archive(name=name, version=version)

        mock_component_operation._version_operation.begin_create_or_update.assert_called_with(
            name=name,
            version=version,
            registry_name=mock_component_operation._registry_name,
            body=component,
            resource_group_name=mock_component_operation._resource_group_name,
        )

    def test_restore_version(self, mock_component_operation: ComponentOperations):
        name = "random_name"
        component = Mock(ComponentVersionData(properties=Mock(ComponentVersionDetails())))
        version = "1"
        mock_component_operation._version_operation.get.return_value = component
        mock_component_operation.restore(name=name, version=version)

        mock_component_operation._version_operation.begin_create_or_update.assert_called_with(
            name=name,
            version=version,
            registry_name=mock_component_operation._registry_name,
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
            registry_name=mock_component_operation._registry_name,
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
            registry_name=mock_component_operation._registry_name,
            body=component,
            resource_group_name=mock_component_operation._resource_group_name,
        )
