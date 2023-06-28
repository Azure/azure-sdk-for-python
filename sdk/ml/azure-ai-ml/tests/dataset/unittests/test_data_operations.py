from pathlib import Path
from typing import Callable, Iterable
from unittest.mock import Mock, patch

import pytest
from test_utilities.constants import Test_Resource_Group, Test_Workspace_Name, Test_Registry_Name

from azure.ai.ml import load_data
from azure.ai.ml._restclient.v2022_10_01.models._models_py3 import (
    DataContainer,
    DataContainerProperties,
    DataVersionBase,
    DataVersionBaseProperties,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.constants._common import (
    REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT,
    AssetTypes,
    YAMLRefDocLinks,
    YAMLRefDocSchemaNames,
)
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.exceptions import ErrorTarget
from azure.ai.ml.operations import DataOperations, DatastoreOperations
from azure.core.paging import ItemPaged
from azure.core.exceptions import ResourceNotFoundError
from unittest.mock import ANY


@pytest.fixture
def mock_datastore_operation(
    mock_workspace_scope: OperationScope, mock_operation_config: OperationConfig, mock_aml_services_2022_10_01: Mock
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        serviceclient_2022_10_01=mock_aml_services_2022_10_01,
    )


@pytest.fixture
def mock_data_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_10_01: Mock,
    mock_datastore_operation: Mock,
    mock_machinelearning_client: Mock,
) -> DataOperations:
    yield DataOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_10_01,
        datastore_operations=mock_datastore_operation,
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
    )


@pytest.fixture
def mock_data_operations_in_registry(
    mock_registry_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_10_01: Mock,
    mock_datastore_operation: Mock,
    mock_machinelearning_client: Mock,
) -> DataOperations:
    yield DataOperations(
        operation_scope=mock_registry_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_10_01,
        datastore_operations=mock_datastore_operation,
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
    )


# @pytest.fixture
def mock_artifact_storage(_one, _two, _three, **kwargs) -> Mock:
    return ArtifactStorageInfo(
        name="testFileData",
        version="3",
        relative_path="path",
        datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
        container_name="containerName",
    )


# @pytest.fixture
def mock_sas_uri(**kwargs) -> Mock:
    return "test_sas_uri"


@pytest.mark.unittest
@patch("azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore", new=mock_artifact_storage)
@patch("azure.ai.ml._utils._registry_utils.get_sas_uri_for_registry_asset", new=mock_sas_uri)
@patch.object(Data, "_from_rest_object", new=Mock())
@patch.object(Data, "_from_container_rest_object", new=Mock())
@pytest.mark.data_experiences_test
class TestDataOperations:
    def test_list(self, mock_data_operations: DataOperations) -> None:
        mock_data_operations._operation.list.return_value = [Mock(Data) for _ in range(10)]
        mock_data_operations._container_operation.list.return_value = [Mock(Data) for _ in range(10)]
        result = mock_data_operations.list()
        assert isinstance(result, Iterable)
        mock_data_operations._container_operation.list.assert_called_once()
        mock_data_operations.list(name="random_name")
        mock_data_operations._operation.list.assert_called_once()

    def test_list_in_registry(self, mock_data_operations_in_registry: DataOperations) -> None:
        mock_data_operations_in_registry._operation.list.return_value = [Mock(Data) for _ in range(10)]
        mock_data_operations_in_registry._container_operation.list.return_value = [Mock(Data) for _ in range(10)]
        mock_data_operations_in_registry.list(name="random_name")
        mock_data_operations_in_registry._operation.list.assert_called_once_with(
            name="random_name",
            resource_group_name=Test_Resource_Group,
            registry_name=Test_Registry_Name,
            list_view_type=ANY,
            cls=ANY,
        )

    def test_list_in_registry_no_name(self, mock_data_operations_in_registry: DataOperations) -> None:
        mock_data_operations_in_registry._operation.list.return_value = [Mock(Data) for _ in range(10)]
        mock_data_operations_in_registry._container_operation.list.return_value = [Mock(Data) for _ in range(10)]
        mock_data_operations_in_registry.list()
        mock_data_operations_in_registry._container_operation.list.assert_called_once_with(
            resource_group_name=Test_Resource_Group,
            registry_name=Test_Registry_Name,
            list_view_type=ANY,
            cls=ANY,
        )

    def test_get_with_version(self, mock_data_operations: DataOperations) -> None:
        name_only = "some_name"
        version = "1"
        data_asset = Data(name=name_only, version=version)
        with patch.object(ItemPaged, "next"), patch.object(Data, "_from_rest_object", return_value=data_asset):
            mock_data_operations.get(name_only, version)
        mock_data_operations._operation.get.assert_called_once_with(
            name=name_only, version=version, resource_group_name=Test_Resource_Group, workspace_name=Test_Workspace_Name
        )

    def test_get_in_registry_with_version(self, mock_data_operations_in_registry: DataOperations) -> None:
        name_only = "some_name"
        version = "1"
        data_asset = Data(name=name_only, version=version)
        with patch.object(ItemPaged, "next"), patch.object(Data, "_from_rest_object", return_value=data_asset):
            mock_data_operations_in_registry.get(name_only, version)
        mock_data_operations_in_registry._operation.get.assert_called_once_with(
            name=name_only, version=version, resource_group_name=Test_Resource_Group, registry_name=Test_Registry_Name
        )

    def test_get_no_version(self, mock_data_operations: DataOperations) -> None:
        name = "random_name"
        with pytest.raises(Exception) as ex:
            mock_data_operations.get(name=name)
        assert "At least one required parameter is missing" in str(ex.value)

    def test_create_with_spec_file(
        self,
        mock_workspace_scope: OperationScope,
        mock_data_operations: DataOperations,
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
            data = load_data(source=data_path)
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
                artifact_type=ErrorTarget.DATA,
                show_progress=True,
                ignore_file=None,
                blob_uri=None,
            )
        mock_data_operations._operation.create_or_update.assert_called_once()
        assert "version='1'" in str(mock_data_operations._operation.create_or_update.call_args)

    def test_create_or_update_in_registry(
        self,
        mock_data_operations_in_registry: DataOperations,
    ):
        """
        Expect to skip validation when remote metadata is inaccessible
        """
        data_path = "./tests/test_configs/dataset/data_local_path.yaml"
        data = load_data(source=data_path)
        with patch(
            "azure.ai.ml.operations._data_operations._check_and_upload_path",
            return_value=(data, "indicatorfile.txt"),
        ), patch("azure.ai.ml.operations._data_operations.Data._from_rest_object", return_value=data), patch(
            "azure.ai.ml.operations._data_operations.get_sas_uri_for_registry_asset", return_value="test_sas_uri"
        ) as mock_sas_uri:
            mock_data_operations_in_registry.create_or_update(data)
            mock_sas_uri.assert_called_once()
            mock_data_operations_in_registry._operation.begin_create_or_update.assert_called_once_with(
                name="testFileData",
                version="1",
                registry_name=Test_Registry_Name,
                resource_group_name=Test_Resource_Group,
                body=ANY,
            )

    def test_create_with_mltable_pattern_path(
        self,
        mock_workspace_scope: OperationScope,
        mock_data_operations: DataOperations,
    ) -> None:
        data_path = "./tests/test_configs/dataset/data_local_path_mltable.yaml"
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
            params_override = [{"path": "./pattern-mltable"}]
            data = load_data(source=data_path, params_override=params_override)
            path = Path(data._base_path, data.path).resolve()
            assert str(data.path).endswith("pattern-mltable")
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
                artifact_type=ErrorTarget.DATA,
                show_progress=True,
                ignore_file=None,
                blob_uri=None,
            )
        mock_data_operations._operation.create_or_update.assert_called_once()
        assert "version='1'" in str(mock_data_operations._operation.create_or_update.call_args)

    def test_create_or_update_missing_path(self, mock_data_operations: DataOperations):
        """
        Expect to raise ValidationException for missing path
        """
        name = "random_name"
        data1 = Data(name=name, version="1", description="this is an mltable dataset", type=AssetTypes.MLTABLE)

        with pytest.raises(Exception) as ex:
            mock_data_operations.create_or_update(data1)
        assert "At least one required parameter is missing" in str(ex.value)
        mock_data_operations._operation.create_or_update.assert_not_called()

        with pytest.raises(Exception) as ex:
            load_data("tests/test_configs/dataset/data_missing_path_test.yml")
        assert REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(YAMLRefDocSchemaNames.DATA, YAMLRefDocLinks.DATA) in str(
            ex.value
        )

    @patch("azure.ai.ml.operations._data_operations.read_local_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.read_remote_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.download_mltable_metadata_schema")
    def test_create_or_update_inaccessible_remote_metadata(
        self,
        _mock_download_jsonschema: Mock,
        _mock_read_remote_mltable_metadata_contents: Mock,
        _mock_read_local_mltable_metadata_contents: Mock,
        mock_datastore_operation: DatastoreOperations,
        mock_data_operations: DataOperations,
    ):
        """
        Expect to skip validation when remote metadata is inaccessible
        """

        data_path = "azureml://mltable_folder"  # actual path doesn't matter, only needs to trigger "remote" code branch for this test
        name = "random_name"
        data = Data(
            name=name, version="1", path=data_path, description="this is an mltable dataset", type=AssetTypes.MLTABLE
        )

        _mock_read_remote_mltable_metadata_contents.side_effect = Exception("test")

        mock_data_operations.create_or_update(data)

        _mock_read_remote_mltable_metadata_contents.assert_called_once_with(
            base_uri=data_path,
            datastore_operations=mock_datastore_operation,
            requests_pipeline=mock_data_operations._requests_pipeline,
        )
        _mock_read_local_mltable_metadata_contents.assert_not_called()
        _mock_download_jsonschema.assert_not_called()
        mock_data_operations._operation.create_or_update.assert_called_once()

    @patch("azure.ai.ml.operations._data_operations.read_local_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.read_remote_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.download_mltable_metadata_schema")
    def test_create_or_update_inaccessible_local_metadata(
        self,
        _mock_download_jsonschema: Mock,
        _mock_read_remote_mltable_metadata_contents: Mock,
        _mock_read_local_mltable_metadata_contents: Mock,
        mock_data_operations: DataOperations,
        tmp_path: Path,
    ):
        """
        Expect to raise exception when local metadata is inaccessible
        """

        data_path = (
            tmp_path
            / "mltable_folder"  # actual path doesn't matter, only needs to trigger "local" code branch for this test
        )
        name = "random_name"
        data = Data(
            name=name, version="1", path=data_path, description="this is an mltable dataset", type=AssetTypes.MLTABLE
        )

        _mock_read_local_mltable_metadata_contents.side_effect = Exception("read local mltable error")

        with pytest.raises(Exception) as ex:
            mock_data_operations.create_or_update(data)
        assert "read local mltable error" in str(ex)

        _mock_read_remote_mltable_metadata_contents.assert_not_called()
        _mock_read_local_mltable_metadata_contents.assert_called_once_with(path=str(data_path))
        _mock_download_jsonschema.assert_not_called()
        mock_data_operations._operation.create_or_update.assert_not_called()

    @patch("azure.ai.ml.operations._data_operations.read_local_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.read_remote_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.validate_mltable_metadata")
    @patch("azure.ai.ml.operations._data_operations.download_mltable_metadata_schema")
    def test_create_or_update_download_mltable_metadata_schema_failure(
        self,
        _mock_download_jsonschema: Mock,
        _mock_validate: Mock,
        _mock_read_remote_mltable_metadata_contents: Mock,
        _mock_read_local_mltable_metadata_contents: Mock,
        mock_data_operations: DataOperations,
        tmp_path: Path,
    ):
        """
        Expect to skip jsonschema validation when we fail to fetch mltable jsonschema
        """

        data_path = (
            tmp_path
            / "mltable_folder"  # actual path doesn't matter, only needs to trigger "local" code branch for this test
        )
        name = "random_name"
        data = Data(
            name=name, version="1", path=data_path, description="this is an mltable dataset", type=AssetTypes.MLTABLE
        )

        _mock_read_local_mltable_metadata_contents.return_value = {
            "paths": [{"file": "./test.csv"}],
            "transformations": [
                {"read_delimited": {"delimiter": ",", "encoding": "unknownencoding", "header": "all_files_same_header"}}
            ],
        }
        _mock_download_jsonschema.side_effect = Exception("mltable schema download error")

        mock_data_operations.create_or_update(data)

        _mock_read_remote_mltable_metadata_contents.assert_not_called()
        _mock_read_local_mltable_metadata_contents.assert_called_once_with(path=str(data_path))
        _mock_download_jsonschema.assert_called_once()
        _mock_validate.assert_not_called()
        mock_data_operations._operation.create_or_update.assert_called_once()

    @patch("azure.ai.ml.operations._data_operations.read_local_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.read_remote_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.validate_mltable_metadata")
    @patch("azure.ai.ml.operations._data_operations.download_mltable_metadata_schema")
    def test_create_or_update_jsonschema_validation_failure(
        self,
        _mock_download_jsonschema: Mock,
        _mock_validate: Mock,
        _mock_read_remote_mltable_metadata_contents: Mock,
        _mock_read_local_mltable_metadata_contents: Mock,
        mock_data_operations: DataOperations,
        tmp_path: Path,
    ):
        """
        Expect to raise exception when jsonschema detects invalid mltable metadata
        """

        data_path = (
            tmp_path
            / "mltable_folder"  # actual path doesn't matter, only needs to trigger "local" code branch for this test
        )
        name = "random_name"
        data = Data(
            name=name, version="1", path=data_path, description="this is an mltable dataset", type=AssetTypes.MLTABLE
        )

        _mock_read_local_mltable_metadata_contents.return_value = {
            "paths": [{"file": "./test.csv"}],
            "transformations": [
                {"read_delimited": {"delimiter": ",", "encoding": "unknownencoding", "header": "all_files_same_header"}}
            ],
        }
        _mock_download_jsonschema.return_value = {"mock": "schema"}
        _mock_validate.side_effect = Exception("jsonschema validation error")

        with pytest.raises(Exception) as ex:
            mock_data_operations.create_or_update(data)
        assert "jsonschema validation error" in str(ex)

        _mock_read_remote_mltable_metadata_contents.assert_not_called()
        _mock_read_local_mltable_metadata_contents.assert_called_once_with(path=str(data_path))
        _mock_download_jsonschema.assert_called_once()
        _mock_validate.assert_called_once()
        mock_data_operations._operation.create_or_update.assert_not_called()

    @patch("azure.ai.ml.operations._data_operations.read_local_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.read_remote_mltable_metadata_contents")
    @patch("azure.ai.ml.operations._data_operations.validate_mltable_metadata")
    @patch("azure.ai.ml.operations._data_operations.download_mltable_metadata_schema")
    def test_create_or_update_skip_validation_flag(
        self,
        _mock_download_jsonschema: Mock,
        _mock_validate: Mock,
        _mock_read_remote_mltable_metadata_contents: Mock,
        _mock_read_local_mltable_metadata_contents: Mock,
        mock_data_operations: DataOperations,
        tmp_path: Path,
    ):
        """
        Expect to skip validation when skip_validation is set on Data
        """

        data_path = (
            tmp_path
            / "mltable_folder"  # actual path doesn't matter, only needs to trigger "local" code branch for this test
        )
        name = "random_name"
        data = Data(
            name=name, version="1", path=data_path, description="this is an mltable dataset", type=AssetTypes.MLTABLE
        )
        data._skip_validation = True

        _mock_read_local_mltable_metadata_contents.return_value = {
            "paths": [{"file": "./test.csv"}],
            "transformations": [
                {"read_delimited": {"delimiter": ",", "encoding": "unknownencoding", "header": "all_files_same_header"}}
            ],
        }
        _mock_download_jsonschema.return_value = {"mock": "schema"}

        mock_data_operations.create_or_update(data)

        _mock_read_remote_mltable_metadata_contents.assert_not_called()
        _mock_read_local_mltable_metadata_contents.assert_called_once_with(path=str(data_path))
        _mock_download_jsonschema.assert_called_once()
        _mock_validate.assert_not_called()
        mock_data_operations._operation.create_or_update.assert_called_once()

    def test_archive_version(self, mock_data_operations: DataOperations):
        name = "random_name"
        dataset_version = Mock(DataVersionBase(properties=Mock(DataVersionBaseProperties(data_uri="http://test.com"))))
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

    def test_archive_container(self, mock_data_operations: DataOperations):
        name = "random_name"
        dataset_container = Mock(DataContainer(properties=Mock(DataContainerProperties(data_type="uri_folder"))))
        mock_data_operations._container_operation.get.return_value = dataset_container
        mock_data_operations.archive(name=name)
        mock_data_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_data_operations._workspace_name,
            body=dataset_container,
            resource_group_name=mock_data_operations._resource_group_name,
        )

    def test_restore_version(self, mock_data_operations: DataOperations):
        name = "random_name"
        dataset_version = Mock(DataVersionBase(properties=Mock(DataVersionBaseProperties(data_uri="http://test.com"))))
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

    def test_restore_container(self, mock_data_operations: DataOperations):
        name = "random_name"
        dataset_container = Mock(DataContainer(properties=Mock(DataContainerProperties(data_type="uri_folder"))))
        mock_data_operations._container_operation.get.return_value = dataset_container
        mock_data_operations.restore(name=name)
        mock_data_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_data_operations._workspace_name,
            body=dataset_container,
            resource_group_name=mock_data_operations._resource_group_name,
        )

    def test_create_with_datastore(
        self,
        mock_workspace_scope: OperationScope,
        mock_data_operations: DataOperations,
    ) -> None:
        data_path = "./tests/test_configs/dataset/data_with_datastore.yaml"
        data_name = f"data_random_name"

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=data_name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ) as mock_thing, patch(
            "azure.ai.ml.operations._data_operations.Data._from_rest_object",
            return_value=None,
        ):
            data = load_data(data_path)
            path = Path(data._base_path, data.path).resolve()
            mock_data_operations.create_or_update(data)
            mock_thing.assert_called_once_with(
                mock_workspace_scope,
                mock_data_operations._datastore_operation,
                path,
                asset_name=data.name,
                asset_version=data.version,
                datastore_name="workspaceartifactstore",
                asset_hash=None,
                sas_uri=None,
                artifact_type=ErrorTarget.DATA,
                show_progress=True,
                ignore_file=None,
                blob_uri=None,
            )
