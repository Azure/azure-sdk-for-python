from typing import Callable
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.operations import ComponentOperations

from .._util import _COMPONENT_TIMEOUT_SECOND


@pytest.fixture
def mock_component_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_02_01_preview: Mock,
    mock_machinelearning_client: Mock,
) -> ComponentOperations:
    yield ComponentOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_02_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestComponentOperation:
    def test_create(self, mock_component_operation: ComponentOperations) -> None:
        task = {
            "type": "run_function",
            "model": {"name": "sore_model", "type": "mlflow_model"},
            "code_configuration": {"code": "./src", "scoring_script": "score.py"},
            "environment": "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        }
        mini_batch = {
            "split_inputs": "score_input",
            "mini_batch_size": "${{inputs.mini_batch_size}}",
        }
        component = ParallelComponent(
            name="random_name",
            version="1",
            mini_batch=mini_batch,
            task=task,
        )

        with patch.object(ComponentOperations, "_resolve_arm_id_or_upload_dependencies") as mock_thing, patch(
            "azure.ai.ml.operations._component_operations.Component._from_rest_object",
            return_value=ParallelComponent(),
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

    def test_create_autoincrement(self, mock_component_operation: ComponentOperations) -> None:
        task = {
            "type": "run_function",
            "model": {"name": "sore_model", "type": "mlflow_model"},
            "code_configuration": {"code": "./src", "scoring_script": "score.py"},
            "environment": "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        }
        mini_batch = {
            "split_inputs": "score_input",
            "mini_batch_size": "${{inputs.mini_batch_size}}",
        }
        component = ParallelComponent(
            name="random_name",
            version=None,
            mini_batch=mini_batch,
            task=task,
        )
        assert component._auto_increment_version
        with patch.object(ComponentOperations, "_resolve_arm_id_or_upload_dependencies") as mock_thing, patch(
            "azure.ai.ml.operations._component_operations.Component._from_rest_object",
            return_value=component,
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
        mock_component_operation.list("mock")
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
