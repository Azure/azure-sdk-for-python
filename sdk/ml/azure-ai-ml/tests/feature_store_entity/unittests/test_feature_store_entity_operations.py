from typing import Iterable
from unittest.mock import Mock, patch

import pytest
from test_utilities.constants import Test_Resource_Group, Test_Workspace_Name

from azure.ai.ml._restclient.v2023_10_01.models._models_py3 import (
    FeaturestoreEntityContainer,
    FeaturestoreEntityContainerProperties,
    FeaturestoreEntityVersion,
    FeaturestoreEntityVersionProperties,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities import DataColumn, DataColumnType, FeatureStoreEntity
from azure.ai.ml.operations._feature_store_entity_operations import FeatureStoreEntityOperations
from azure.core.paging import ItemPaged


@pytest.fixture
def mock_feature_store_entity_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2023_10_01: Mock,
) -> FeatureStoreEntityOperations:
    yield FeatureStoreEntityOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2023_10_01,
    )


@pytest.mark.unittest
@patch.object(FeatureStoreEntity, "_from_rest_object", new=Mock())
@patch.object(FeatureStoreEntity, "_from_container_rest_object", new=Mock())
@pytest.mark.data_experiences_test
class TestFeatureStoreEntityOperations:
    def test_list(self, mock_feature_store_entity_operations: FeatureStoreEntityOperations) -> None:
        mock_feature_store_entity_operations._operation.list.return_value = [
            Mock(FeatureStoreEntity) for _ in range(10)
        ]
        mock_feature_store_entity_operations._container_operation.list.return_value = [
            Mock(FeatureStoreEntity) for _ in range(10)
        ]
        result = mock_feature_store_entity_operations.list()
        assert isinstance(result, Iterable)
        mock_feature_store_entity_operations._container_operation.list.assert_called_once()
        mock_feature_store_entity_operations.list(name="random_name")
        mock_feature_store_entity_operations._operation.list.assert_called_once()

    def test_get_with_version(self, mock_feature_store_entity_operations: FeatureStoreEntityOperations) -> None:
        name_only = "some_name"
        version = "1"
        featurestoreEntity = FeatureStoreEntity(
            name=name_only, version=version, index_columns=[DataColumn(name="test", type=DataColumnType.STRING)]
        )
        with patch.object(ItemPaged, "next"), patch.object(
            FeatureStoreEntity, "_from_rest_object", return_value=featurestoreEntity
        ):
            mock_feature_store_entity_operations.get(name=name_only, version=version)
        mock_feature_store_entity_operations._operation.get.assert_called_once_with(
            name=name_only, version=version, resource_group_name=Test_Resource_Group, workspace_name=Test_Workspace_Name
        )

    def test_archive_version(self, mock_feature_store_entity_operations: FeatureStoreEntityOperations):
        name = "random_name"
        featureStoreEntity_version = Mock(
            FeaturestoreEntityVersion(properties=Mock(FeaturestoreEntityVersionProperties()))
        )
        featureStoreEntity_version.properties.stage = "Development"
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

    def test_restore_version(self, mock_feature_store_entity_operations: FeatureStoreEntityOperations):
        name = "random_name"
        featureStoreEntity_version = Mock(
            FeaturestoreEntityVersion(properties=Mock(FeaturestoreEntityVersionProperties()))
        )
        featureStoreEntity_version.properties.stage = "Archived"
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
