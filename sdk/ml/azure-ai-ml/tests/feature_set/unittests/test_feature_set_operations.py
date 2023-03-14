from datetime import datetime
from typing import Iterable
from unittest.mock import Mock, patch

import pytest
from test_utilities.constants import Test_Resource_Group, Test_Workspace_Name

from azure.ai.ml._restclient.v2023_02_01_preview.models._models_py3 import (
    FeaturesetContainer,
    FeaturesetContainerProperties,
    FeaturesetVersion,
    FeaturesetVersionProperties,
    FeaturesetJobArmPaginatedResult,
    FeatureArmPaginatedResult,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.entities._feature_set.feature_set_materialization_response import _FeatureSetMaterializationResponse
from azure.ai.ml.entities._feature_set.feature import _Feature
from azure.ai.ml.operations import _FeatureSetOperations, DatastoreOperations
from azure.ai.ml.entities import _FeatureSet, _FeatureSetSpecification
from azure.ai.ml.operations import DatastoreOperations
from azure.ai.ml.operations._feature_set_operations import _FeatureSetOperations
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller


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
def mock_feature_set_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2023_02_01_preview: Mock,
    mock_datastore_operation: Mock,
) -> _FeatureSetOperations:
    yield _FeatureSetOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2023_02_01_preview,
        datastore_operations=mock_datastore_operation,
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


@pytest.mark.unittest
@patch("azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore", new=mock_artifact_storage)
@patch.object(_FeatureSet, "_from_rest_object", new=Mock())
@patch.object(_FeatureSet, "_from_container_rest_object", new=Mock())
@patch.object(_FeatureSetMaterializationResponse, "_from_rest_object", new=Mock())
@patch.object(_Feature, "_from_rest_object", new=Mock())
@pytest.mark.data_experiences_test
class TestFeatureSetOperations:
    def test_list(self, mock_feature_set_operations: _FeatureSetOperations) -> None:
        mock_feature_set_operations._operation.list.return_value = [Mock(_FeatureSet) for _ in range(10)]
        mock_feature_set_operations._container_operation.list.return_value = [Mock(_FeatureSet) for _ in range(10)]
        result = mock_feature_set_operations.list()
        assert isinstance(result, Iterable)
        mock_feature_set_operations._container_operation.list.assert_called_once()
        mock_feature_set_operations.list(name="random_name")
        mock_feature_set_operations._operation.list.assert_called_once()

    def test_get_with_version(self, mock_feature_set_operations: _FeatureSetOperations) -> None:
        name_only = "some_name"
        version = "1"
        featureset = _FeatureSet(
            name=name_only,
            version=version,
            entities=["test_entity"],
            specification=_FeatureSetSpecification(path="local/"),
        )
        with patch.object(ItemPaged, "next"), patch.object(_FeatureSet, "_from_rest_object", return_value=featureset):
            mock_feature_set_operations.get(name=name_only, version=version)
        mock_feature_set_operations._operation.get.assert_called_once_with(
            name=name_only, version=version, resource_group_name=Test_Resource_Group, workspace_name=Test_Workspace_Name
        )

    def test_get_no_version(self, mock_feature_set_operations: _FeatureSetOperations) -> None:
        name = "random_name"
        with pytest.raises(Exception) as ex:
            mock_feature_set_operations.get(name=name)
        assert "At least one required parameter is missing" in str(ex.value)

    def test_begin_backfill(self, mock_feature_set_operations: _FeatureSetOperations) -> None:
        mock_feature_set_operations._operation.begin_backfill.return_value = LROPoller
        mock_feature_set_operations.begin_backfill(
            name="random_name",
            version="1",
            feature_window_start_time=datetime(2023, 1, 1),
            feature_window_end_time=datetime(2023, 1, 2),
        )
        mock_feature_set_operations._operation.begin_backfill.assert_called_once()

    def test_list_materialization_operation(self, mock_feature_set_operations: _FeatureSetOperations) -> None:
        mock_feature_set_operations._operation.list_materialization_jobs.return_value = [
            Mock(FeaturesetJobArmPaginatedResult) for _ in range(10)
        ]
        result = mock_feature_set_operations.list_materialization_operation(name="random_name", version="1")
        assert isinstance(result, Iterable)
        mock_feature_set_operations._operation.list_materialization_jobs.assert_called_once()

    def test_list_features(self, mock_feature_set_operations: _FeatureSetOperations) -> None:
        mock_feature_set_operations._operation.list_features.return_value = [
            Mock(FeatureArmPaginatedResult) for _ in range(10)
        ]
        result = mock_feature_set_operations.list_features(feature_set_name="random_name", version="1")
        assert isinstance(result, Iterable)
        mock_feature_set_operations._operation.list_features.assert_called_once()

    def test_get_feature(self, mock_feature_set_operations: _FeatureSetOperations) -> None:
        mock_feature_set_operations.get_feature(feature_set_name="random_name", version="1", feature_name="test")
        mock_feature_set_operations._operation.get_feature.assert_called_once()

    def test_archive_version(self, mock_feature_set_operations: _FeatureSetOperations):
        name = "random_name"
        featureset_version = Mock(FeaturesetVersion(properties=Mock(FeaturesetVersionProperties(entities=["test"]))))
        version = "1"
        mock_feature_set_operations._operation.get.return_value = featureset_version
        mock_feature_set_operations.archive(name=name, version=version)
        mock_feature_set_operations._operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_feature_set_operations._workspace_name,
            body=featureset_version,
            resource_group_name=mock_feature_set_operations._resource_group_name,
        )

    def test_archive_container(self, mock_feature_set_operations: _FeatureSetOperations):
        name = "random_name"
        featureset_container = Mock(
            FeaturesetContainer(properties=Mock(FeaturesetContainerProperties(description="test")))
        )
        mock_feature_set_operations._container_operation.get.return_value = featureset_container
        mock_feature_set_operations.archive(name=name)
        mock_feature_set_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_feature_set_operations._workspace_name,
            body=featureset_container,
            resource_group_name=mock_feature_set_operations._resource_group_name,
        )

    def test_restore_version(self, mock_feature_set_operations: _FeatureSetOperations):
        name = "random_name"
        featureset_version = Mock(FeaturesetVersion(properties=Mock(FeaturesetVersionProperties(entities=["test"]))))
        version = "1"
        mock_feature_set_operations._operation.get.return_value = featureset_version
        mock_feature_set_operations.restore(name=name, version=version)
        mock_feature_set_operations._operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_feature_set_operations._workspace_name,
            body=featureset_version,
            resource_group_name=mock_feature_set_operations._resource_group_name,
        )

    def test_restore_container(self, mock_feature_set_operations: _FeatureSetOperations):
        name = "random_name"
        featureset_container = Mock(
            FeaturesetContainer(properties=Mock(FeaturesetContainerProperties(entities=["test"])))
        )
        mock_feature_set_operations._container_operation.get.return_value = featureset_container
        mock_feature_set_operations.restore(name=name)
        mock_feature_set_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_feature_set_operations._workspace_name,
            body=featureset_container,
            resource_group_name=mock_feature_set_operations._resource_group_name,
        )
