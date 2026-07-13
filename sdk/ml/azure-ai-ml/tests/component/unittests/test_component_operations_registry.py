from typing import Callable
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml._restclient.arm_ml_service.models import (
    ComponentContainer as ComponentContainerData,
    ComponentContainerProperties as ComponentContainerDetails,
    ComponentVersion as ComponentVersionData,
    ComponentVersionProperties as ComponentVersionDetails,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty
from azure.ai.ml.entities._component.command_component import CommandComponent
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
        registry_service_client=mock_aml_services_2021_10_01_dataplanepreview,
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
        ), patch(
            "azure.ai.ml.operations._component_operations.begin_create_or_update_registry_versioned_asset"
        ) as mock_create, patch("azure.ai.ml.operations._component_operations.polling_wait"):
            mock_component_operation.create_or_update(component)
            mock_thing.assert_called_once()

        mock_create.assert_called_once()

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
        ), patch(
            "azure.ai.ml.operations._component_operations.begin_create_or_update_registry_versioned_asset"
        ) as mock_create, patch("azure.ai.ml.operations._component_operations.polling_wait"):
            mock_component_operation.create_or_update(component)
            # for IPP components, we need to make sure _resolve_arm_id_or_upload_dependencies is not called
            mock_thing.assert_not_called()

        mock_create.assert_called_once()

    def test_list(self, mock_component_operation: ComponentOperations) -> None:
        with patch("azure.ai.ml.operations._component_operations.list_registry_assets") as mock_list:
            mock_component_operation.list(name="mock")
            mock_component_operation.list()
        assert mock_list.call_count == 2

    def test_get(self, mock_component_operation: ComponentOperations) -> None:
        with patch("azure.ai.ml.operations._component_operations.get_registry_versioned_asset") as mock_get, patch(
            "azure.ai.ml.operations._component_operations.Component"
        ) as mock_component_entity, patch.object(ComponentVersionData, "_deserialize", return_value=Mock()):
            mock_component_operation.get("mock_component", "1")

        mock_get.assert_called_once()
        create_call_args_str = str(mock_get.call_args)
        assert "mock_component" in create_call_args_str
        assert "'1'" in create_call_args_str
        mock_component_entity._from_rest_object.assert_called_once()

    def test_archive_version(self, mock_component_operation: ComponentOperations):
        name = "random_name"
        version = "1"
        with patch("azure.ai.ml._utils._registry_utils.get_registry_versioned_asset"), patch(
            "azure.ai.ml._utils._registry_utils.begin_create_or_update_registry_versioned_asset"
        ) as mock_create, patch.object(ComponentVersionData, "_deserialize", return_value=Mock()):
            mock_component_operation.archive(name=name, version=version)

        mock_create.assert_called_once()

    def test_restore_version(self, mock_component_operation: ComponentOperations):
        name = "random_name"
        version = "1"
        with patch("azure.ai.ml._utils._registry_utils.get_registry_versioned_asset"), patch(
            "azure.ai.ml._utils._registry_utils.begin_create_or_update_registry_versioned_asset"
        ) as mock_create, patch.object(ComponentVersionData, "_deserialize", return_value=Mock()):
            mock_component_operation.restore(name=name, version=version)

        mock_create.assert_called_once()

    def test_archive_container(self, mock_component_operation: ComponentOperations):
        name = "random_name"
        with patch("azure.ai.ml._utils._registry_utils.get_registry_container_asset"), patch(
            "azure.ai.ml._utils._registry_utils.begin_create_or_update_registry_container"
        ) as mock_create, patch.object(ComponentContainerData, "_deserialize", return_value=Mock()):
            mock_component_operation.archive(name=name)

        mock_create.assert_called_once()

    def test_restore_container(self, mock_component_operation: ComponentOperations):
        name = "random_name"
        with patch("azure.ai.ml._utils._registry_utils.get_registry_container_asset"), patch(
            "azure.ai.ml._utils._registry_utils.begin_create_or_update_registry_container"
        ) as mock_create, patch.object(ComponentContainerData, "_deserialize", return_value=Mock()):
            mock_component_operation.restore(name=name)

        mock_create.assert_called_once()
