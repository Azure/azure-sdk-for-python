from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.operations._data_operations import DataOperations, DatastoreOperations
from azure.ai.ml.constants import OrderString
from azure.core.paging import ItemPaged
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml._restclient.v2021_10_01.models._models_py3 import (
    DatasetContainerData,
    DatasetContainerDetails,
    DatasetVersionData,
    DatasetVersionDetails,
)

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from test_utilities.constants import Test_Resource_Group, Test_Workspace_Name
from typing import Callable, Iterable
from azure.ai.ml import load_data


@pytest.fixture
def mock_datastore_operation(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        serviceclient_2022_05_01=mock_aml_services_2022_05_01,
    )


@pytest.fixture
def mock_data_operations(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock, mock_datastore_operation: Mock
) -> DataOperations:
    yield DataOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operation,
    )


@pytest.mark.unittest
class TestDataOperations:
    @patch.object(Data, "_from_rest_object", new=Mock())
    @patch.object(Data, "_from_container_rest_object", new=Mock())
    def test_list(self, mock_data_operations: DataOperations, randstr: Callable[[], str]) -> None:
        mock_data_operations._operation.list.return_value = [Mock(Data) for _ in range(10)]
        mock_data_operations._container_operation.list.return_value = [Mock(Data) for _ in range(10)]
        result = mock_data_operations.list()
        assert isinstance(result, Iterable)
        mock_data_operations._container_operation.list.assert_called_once()
        mock_data_operations.list(name=randstr())
        mock_data_operations._operation.list.assert_called_once()

    def test_get_with_version(self, mock_data_operations: DataOperations) -> None:
        name_only = "some_name"
        version = "1"
        data_asset = Data(name=name_only, version=version)
        with patch.object(ItemPaged, "next"), patch.object(Data, "_from_rest_object", return_value=data_asset):
            mock_data_operations.get(name_only, version)
        mock_data_operations._operation.get.assert_called_once_with(
            name=name_only, version=version, resource_group_name=Test_Resource_Group, workspace_name=Test_Workspace_Name
        )

    def test_get_no_version(self, mock_data_operations: DataOperations, randstr: Callable[[], str]) -> None:
        name = randstr()
        with pytest.raises(Exception):
            mock_data_operations.get(name=name)

    def test_create_with_spec_file(
        self,
        mock_workspace_scope: OperationScope,
        mock_data_operations: DataOperations,
        randstr: Callable[[], str],
    ) -> None:
        data_path = "./tests/test_configs/dataset/data_local_path.yaml"
        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name="testFileData",
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ) as mock_thing, patch(
            "azure.ai.ml.operations._data_operations.Data._from_rest_object",
            return_value=None,
        ):
            data = load_data(path=data_path)
            path = Path(data._base_path, data.path).resolve()
            mock_data_operations.create_or_update(data)
            mock_thing.assert_called_once_with(
                mock_workspace_scope,
                mock_data_operations._datastore_operation,
                path,
                asset_name=data.name,
                asset_version=data.version,
                datastore_name=None,
                asset_hash=None,
                sas_uri=None,
            )
        mock_data_operations._operation.create_or_update.assert_called_once()
        assert "version='1'" in str(mock_data_operations._operation.create_or_update.call_args)

    def test_archive_version(self, mock_data_operations: DataOperations, randstr: Callable[[], str]):
        name = randstr()
        dataset_version = Mock(DatasetVersionData(properties=Mock(DatasetVersionDetails(paths=[]))))
        version = "1"
        mock_data_operations._operation.get.return_value = dataset_version
        mock_data_operations.archive(name=name, version=version)
        mock_data_operations._operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_data_operations._workspace_name,
            body=dataset_version,
            resource_group_name=mock_data_operations._resource_group_name,
        )

    def test_archive_container(self, mock_data_operations: DataOperations, randstr: Callable[[], str]):
        name = randstr()
        dataset_container = Mock(DatasetContainerData(properties=Mock(DatasetContainerDetails())))
        mock_data_operations._container_operation.get.return_value = dataset_container
        mock_data_operations.archive(name=name)
        mock_data_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_data_operations._workspace_name,
            body=dataset_container,
            resource_group_name=mock_data_operations._resource_group_name,
        )

    def test_restore_version(self, mock_data_operations: DataOperations, randstr: Callable[[], str]):
        name = randstr()
        dataset_version = Mock(DatasetVersionData(properties=Mock(DatasetVersionDetails(paths=[]))))
        version = "1"
        mock_data_operations._operation.get.return_value = dataset_version
        mock_data_operations.restore(name=name, version=version)
        mock_data_operations._operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_data_operations._workspace_name,
            body=dataset_version,
            resource_group_name=mock_data_operations._resource_group_name,
        )

    def test_restore_container(self, mock_data_operations: DataOperations, randstr: Callable[[], str]):
        name = randstr()
        dataset_container = Mock(DatasetContainerData(properties=Mock(DatasetContainerDetails())))
        mock_data_operations._container_operation.get.return_value = dataset_container
        mock_data_operations.restore(name=name)
        mock_data_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_data_operations._workspace_name,
            body=dataset_container,
            resource_group_name=mock_data_operations._resource_group_name,
        )
