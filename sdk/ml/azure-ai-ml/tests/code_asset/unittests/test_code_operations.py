from pathlib import Path
from typing import Callable
from unittest.mock import Mock, patch

import pytest
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.entities._load_functions import load_code
from azure.ai.ml.operations import DatastoreOperations
from azure.ai.ml.operations._code_operations import CodeOperations


@pytest.fixture()
def mock_datastore_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2024_01_01_preview: Mock,
    mock_aml_services_2024_07_01_preview: Mock,
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        serviceclient_2024_01_01_preview=mock_aml_services_2024_01_01_preview,
        serviceclient_2024_07_01_preview=mock_aml_services_2024_07_01_preview,
    )


@pytest.fixture
def mock_code_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_datastore_operation: Mock,
) -> CodeOperations:
    yield CodeOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operation,
    )


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestCodeOperations:
    def test_create(
        self,
        mock_code_operation: CodeOperations,
        mock_workspace_scope: OperationScope,
        tmp_path: Path,
    ) -> None:
        code_name = "random_code_name"
        p = tmp_path / "code.yml"
        code_path = tmp_path / "code_asset.txt"
        code_path.write_text("hello world")
        p.write_text(
            f"""
        name: {code_name}
        path: code_asset.txt
        version: 3"""
        )
        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(code_name, "3", "path", "datastore_id", "containerName"),
        ), patch(
            "azure.ai.ml.operations._code_operations.Code._from_rest_object",
            return_value=None,
        ):

            def simple_code_validation(code):
                mock_code_operation.create_or_update(code)

            verify_entity_load_and_dump(load_code, simple_code_validation, p)

        mock_code_operation._version_operation.create_or_update.asset_called_twice()
        body = mock_code_operation._version_operation.create_or_update.call_args[1]["body"]
        assert body.properties.properties["hash_sha256"] is not None
        assert body.properties.properties["hash_sha256"] != ""
        assert "version='3'" in str(mock_code_operation._version_operation.create_or_update.call_args)

    def test_get(
        self,
        mock_code_operation: CodeOperations,
    ) -> None:
        mock_code_operation._container_operation.get.return_value = None
        with patch(
            "azure.ai.ml.operations._code_operations.Code._from_rest_object",
            return_value=None,
        ):
            mock_code_operation.get(name="random_name", version="1")
        mock_code_operation._version_operation.get.assert_called_once()
        assert mock_code_operation._container_operation.list.call_count == 0
