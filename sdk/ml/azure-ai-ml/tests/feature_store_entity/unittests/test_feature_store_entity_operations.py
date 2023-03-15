from typing import Iterable
from unittest.mock import Mock, patch

import pytest
from test_utilities.constants import Test_Resource_Group, Test_Workspace_Name

from azure.ai.ml._restclient.v2023_02_01_preview.models._models_py3 import (
    FeaturestoreEntityContainer,
    FeaturestoreEntityContainerProperties,
    FeaturestoreEntityVersion,
    FeaturestoreEntityVersionProperties,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities import _FeatureStoreEntity, _DataColumn, _DataColumnType
from azure.ai.ml.operations._feature_store_entity_operations import _FeatureStoreEntityOperations
from azure.core.paging import ItemPaged


@pytest.fixture
def mock_feature_store_entity_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2023_02_01_preview: Mock,
) -> _FeatureStoreEntityOperations:
    yield _FeatureStoreEntityOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2023_02_01_preview,
    )


@pytest.mark.unittest
@patch.object(_FeatureStoreEntity, "_from_rest_object", new=Mock())
@patch.object(_FeatureStoreEntity, "_from_container_rest_object", new=Mock())
@pytest.mark.data_experiences_test
class TestFeatureStoreEntityOperations:
    def test_list(self, mock_feature_store_entity_operations: _FeatureStoreEntityOperations) -> None:
        mock_feature_store_entity_operations._operation.list.return_value = [
            Mock(_FeatureStoreEntity) for _ in range(10)
        ]
        mock_feature_store_entity_operations._container_operation.list.return_value = [
            Mock(_FeatureStoreEntity) for _ in range(10)
        ]
        result = mock_feature_store_entity_operations.list()
        assert isinstance(result, Iterable)
        mock_feature_store_entity_operations._container_operation.list.assert_called_once()
        mock_feature_store_entity_operations.list(name="random_name")
        mock_feature_store_entity_operations._operation.list.assert_called_once()

    def test_get_with_version(self, mock_feature_store_entity_operations: _FeatureStoreEntityOperations) -> None:
        name_only = "some_name"
        version = "1"
        featurestoreEntity = _FeatureStoreEntity(
            name=name_only, version=version, index_columns=[_DataColumn(name="test", type=_DataColumnType.string)]
        )
        with patch.object(ItemPaged, "next"), patch.object(
            _FeatureStoreEntity, "_from_rest_object", return_value=featurestoreEntity
        ):
            mock_feature_store_entity_operations.get(name=name_only, version=version)
        mock_feature_store_entity_operations._operation.get.assert_called_once_with(
            name=name_only, version=version, resource_group_name=Test_Resource_Group, workspace_name=Test_Workspace_Name
        )

    def test_get_no_version(self, mock_feature_store_entity_operations: _FeatureStoreEntityOperations) -> None:
        name = "random_name"
        with pytest.raises(Exception) as ex:
            mock_feature_store_entity_operations.get(name=name)
        assert "At least one required parameter is missing" in str(ex.value)

    def test_archive_version(self, mock_feature_store_entity_operations: _FeatureStoreEntityOperations):
        name = "random_name"
        featureStoreEntity_version = Mock(
            FeaturestoreEntityVersion(properties=Mock(FeaturestoreEntityVersionProperties()))
        )
        version = "1"
        mock_feature_store_entity_operations._operation.get.return_value = featureStoreEntity_version
        mock_feature_store_entity_operations.archive(name=name, version=version)
        mock_feature_store_entity_operations._operation.begin_create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_feature_store_entity_operations._workspace_name,
            body=featureStoreEntity_version,
            resource_group_name=mock_feature_store_entity_operations._resource_group_name,
        )

    def test_restore_version(self, mock_feature_store_entity_operations: _FeatureStoreEntityOperations):
        name = "random_name"
        featureStoreEntity_version = Mock(
            FeaturestoreEntityVersion(properties=Mock(FeaturestoreEntityVersionProperties()))
        )
        version = "1"
        mock_feature_store_entity_operations._operation.get.return_value = featureStoreEntity_version
        mock_feature_store_entity_operations.restore(name=name, version=version)
        mock_feature_store_entity_operations._operation.begin_create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_feature_store_entity_operations._workspace_name,
            body=featureStoreEntity_version,
            resource_group_name=mock_feature_store_entity_operations._resource_group_name,
        )
