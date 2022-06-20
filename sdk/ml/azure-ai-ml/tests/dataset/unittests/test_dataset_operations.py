from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.operations._dataset_operations import DatasetOperations, DatastoreOperations
from azure.ai.ml.constants import OrderString
from azure.core.paging import ItemPaged
from azure.ai.ml.entities._assets import Dataset
from azure.ai.ml._restclient.v2021_10_01.models._models_py3 import DatasetContainerDetails
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from test_utilities.constants import Test_Resource_Group, Test_Workspace_Name
from typing import Callable, Iterable


@pytest.fixture
def mock_datastore_operation(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        serviceclient_2022_05_01=mock_aml_services_2022_05_01,
    )


@pytest.fixture
def mock_dataset_operations(
    mock_workspace_scope: OperationScope, mock_aml_services_2021_10_01: Mock, mock_datastore_operation: Mock
) -> DatasetOperations:
    yield DatasetOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2021_10_01,
        datastore_operations=mock_datastore_operation,
    )


@pytest.mark.unittest
class TestDatasetOperations:
    @patch.object(Dataset, "_from_rest_object", new=Mock())
    @patch.object(Dataset, "_from_container_rest_object", new=Mock())
    def test_list(self, mock_dataset_operations: DatasetOperations, randstr: Callable[[], str]) -> None:
        mock_dataset_operations._operation.list.return_value = [Mock(Dataset) for _ in range(10)]
        mock_dataset_operations._container_operation.list.return_value = [Mock(Dataset) for _ in range(10)]
        result = mock_dataset_operations.list()
        assert isinstance(result, Iterable)
        mock_dataset_operations._container_operation.list.assert_called_once()
        mock_dataset_operations.list(randstr())
        mock_dataset_operations._operation.list.assert_called_once()

    def test_get_with_version(self, mock_dataset_operations: DatasetOperations) -> None:
        name_only = "some_name"
        version = "1"
        data_asset = Dataset(name=name_only, version=version)
        with patch.object(ItemPaged, "next"), patch.object(Dataset, "_from_rest_object", return_value=data_asset):
            mock_dataset_operations.get(name_only, version)
        mock_dataset_operations._operation.get.assert_called_once_with(
            name_only, version, Test_Resource_Group, Test_Workspace_Name
        )

    def test_get_no_version(self, mock_dataset_operations: DatasetOperations, randstr: Callable[[], str]) -> None:
        name = randstr()
        with pytest.raises(Exception):
            mock_dataset_operations.get(name=name)

    def test_create_with_spec_file(
        self,
        mock_workspace_scope: OperationScope,
        mock_dataset_operations: DatasetOperations,
        randstr: Callable[[], str],
    ) -> None:
        data_path = "./tests/test_configs/dataset/dataset_local_path.yaml"
        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name="testFileData",
                version="1",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ) as mock_thing, patch(
            "azure.ai.ml.operations._dataset_operations.Dataset._from_rest_object",
            return_value=Dataset(),
        ):
            data = Dataset.load(path=data_path)
            path = Path(data._base_path, data.local_path).resolve()
            mock_dataset_operations.create_or_update(data)
            mock_thing.assert_called_once_with(
                mock_workspace_scope,
                mock_dataset_operations._datastore_operation,
                path,
                asset_name=data.name,
                asset_version=data.version,
                datastore_name=None,
                asset_hash=None,
                sas_uri=None,
            )
        mock_dataset_operations._operation.create_or_update.assert_called_once()
        assert "version='1'" in str(mock_dataset_operations._operation.create_or_update.call_args)

    def test_create_autoincrement(
        self,
        mock_dataset_operations: DatasetOperations,
        mock_workspace_scope: OperationScope,
        randstr: Callable[[], str],
        tmp_path: Path,
    ) -> None:

        mock_dataset_operations._container_operation.get.return_value = Mock(DatasetContainerDetails())

        data_path = "./tests/test_configs/dataset/dataset_local_path.yaml"
        dataset = Dataset.load(path=data_path)

        with patch(
            "azure.ai.ml.operations._dataset_operations._check_and_upload_path",
            return_value=(dataset, "indicatorfile.txt"),
        ), patch("azure.ai.ml.operations._dataset_operations.Dataset._from_rest_object", return_value=dataset), patch(
            "azure.ai.ml.operations._dataset_operations._get_default_datastore_info", return_value=None
        ), patch(
            "azure.ai.ml.operations._dataset_operations._update_metadata", return_value=None
        ) as mock_update:
            dataset.version = None
            mock_dataset_operations.create_or_update(dataset)
            mock_dataset_operations._operation.create_or_update.assert_called_once()
            mock_dataset_operations._container_operation.get.assert_called_once_with(
                name=dataset.name,
                resource_group_name=mock_workspace_scope.resource_group_name,
                workspace_name=mock_workspace_scope.workspace_name,
            )
            mock_dataset_operations._operation.create_or_update.assert_called_once_with(
                body=dataset._to_rest_object(),
                name=dataset.name,
                version=mock_dataset_operations._container_operation.get().properties.next_version,
                resource_group_name=mock_workspace_scope.resource_group_name,
                workspace_name=mock_workspace_scope.workspace_name,
            )
            mock_update.assert_called_once()
