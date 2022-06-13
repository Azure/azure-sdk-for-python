import pytest
from unittest.mock import Mock, patch
from typing import Callable
from pathlib import Path

from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.operations import DatastoreOperations
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.ai.ml.entities._load_functions import load_code


@pytest.fixture()
def mock_datastore_operation(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        serviceclient_2022_05_01=mock_aml_services_2022_05_01,
    )


@pytest.fixture
def mock_code_operation(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock, mock_datastore_operation: Mock
) -> CodeOperations:
    yield CodeOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operation,
    )


@pytest.mark.unittest
class TestCodeOperations:
    def test_create(
        self,
        mock_code_operation: CodeOperations,
        mock_workspace_scope: OperationScope,
        randstr: Callable[[], str],
        tmp_path: Path,
    ) -> None:
        code_name = randstr()
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
            code = load_code(path=p)
            mock_code_operation.create_or_update(code)
        mock_code_operation._version_operation.create_or_update.assert_called_once()
        assert "version='3'" in str(mock_code_operation._version_operation.create_or_update.call_args)

    def test_get(
        self,
        randstr: Callable[[], str],
        mock_code_operation: CodeOperations,
    ) -> None:
        mock_code_operation._container_operation.get.return_value = None
        with patch(
            "azure.ai.ml.operations._code_operations.Code._from_rest_object",
            return_value=None,
        ):
            mock_code_operation.get(name=randstr(), version="1")
        mock_code_operation._version_operation.get.assert_called_once()
        assert mock_code_operation._container_operation.list.call_count == 0
