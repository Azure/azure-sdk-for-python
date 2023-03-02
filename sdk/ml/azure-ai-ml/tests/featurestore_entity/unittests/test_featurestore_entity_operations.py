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
from azure.ai.ml.entities import FeaturestoreEntity, DataColumn, DataColumnType
from azure.ai.ml.operations import FeaturestoreEntityOperations
from azure.core.paging import ItemPaged


@pytest.fixture
def mock_featurestore_entity_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2023_02_01_preview: Mock,
) -> FeaturestoreEntityOperations:
    yield FeaturestoreEntityOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2023_02_01_preview,
    )


@pytest.mark.unittest
@patch.object(FeaturestoreEntity, "_from_rest_object", new=Mock())
@patch.object(FeaturestoreEntity, "_from_container_rest_object", new=Mock())
@pytest.mark.data_experiences_test
class TestFeaturestoreEntityOperations:
    def test_list(self, mock_featurestore_entity_operations: FeaturestoreEntityOperations) -> None:
        mock_featurestore_entity_operations._operation.list.return_value = [Mock(FeaturestoreEntity) for _ in range(10)]
        mock_featurestore_entity_operations._container_operation.list.return_value = [Mock(FeaturestoreEntity) for _ in range(10)]
        result = mock_featurestore_entity_operations.list()
        assert isinstance(result, Iterable)
        mock_featurestore_entity_operations._container_operation.list.assert_called_once()
        mock_featurestore_entity_operations.list(name="random_name")
        mock_featurestore_entity_operations._operation.list.assert_called_once()

    def test_get_with_version(self, mock_featurestore_entity_operations: FeaturestoreEntityOperations) -> None:
        name_only = "some_name"
        version = "1"
        featurestoreEntity = FeaturestoreEntity(
            name=name_only,
            version=version,
            index_columns=[DataColumn(name="test", type=DataColumnType.string)]
        )
        with patch.object(ItemPaged, "next"), patch.object(FeaturestoreEntity, "_from_rest_object", return_value=featurestoreEntity):
            mock_featurestore_entity_operations.get(name=name_only, version=version)
        mock_featurestore_entity_operations._operation.get.assert_called_once_with(
            name=name_only, version=version, resource_group_name=Test_Resource_Group, workspace_name=Test_Workspace_Name
        )

    def test_get_no_version(self, mock_featurestore_entity_operations: FeaturestoreEntityOperations) -> None:
        name = "random_name"
        with pytest.raises(Exception) as ex:
            mock_featurestore_entity_operations.get(name=name)
        assert "At least one required parameter is missing" in str(ex.value)

    def test_archive_version(self, mock_featurestore_entity_operations: FeaturestoreEntityOperations):
        name = "random_name"
        FeaturestoreEntity_version = Mock(FeaturestoreEntityVersion(properties=Mock(FeaturestoreEntityVersionProperties())))
        version = "1"
        mock_featurestore_entity_operations._operation.get.return_value = FeaturestoreEntity_version
        mock_featurestore_entity_operations.archive(name=name, version=version)
        mock_featurestore_entity_operations._operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_featurestore_entity_operations._workspace_name,
            body=FeaturestoreEntity_version,
            resource_group_name=mock_featurestore_entity_operations._resource_group_name,
        )

    def test_archive_container(self, mock_featurestore_entity_operations: FeaturestoreEntityOperations):
        name = "random_name"
        FeaturestoreEntity_container = Mock(
            FeaturestoreEntityContainer(properties=Mock(FeaturestoreEntityContainerProperties(description="test")))
        )
        mock_featurestore_entity_operations._container_operation.get.return_value = FeaturestoreEntity_container
        mock_featurestore_entity_operations.archive(name=name)
        mock_featurestore_entity_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_featurestore_entity_operations._workspace_name,
            body=FeaturestoreEntity_container,
            resource_group_name=mock_featurestore_entity_operations._resource_group_name,
        )

    def test_restore_version(self, mock_featurestore_entity_operations: FeaturestoreEntityOperations):
        name = "random_name"
        FeaturestoreEntity_version = Mock(FeaturestoreEntityVersion(properties=Mock(FeaturestoreEntityVersionProperties())))
        version = "1"
        mock_featurestore_entity_operations._operation.get.return_value = FeaturestoreEntity_version
        mock_featurestore_entity_operations.restore(name=name, version=version)
        mock_featurestore_entity_operations._operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_featurestore_entity_operations._workspace_name,
            body=FeaturestoreEntity_version,
            resource_group_name=mock_featurestore_entity_operations._resource_group_name,
        )

    def test_restore_container(self, mock_featurestore_entity_operations: FeaturestoreEntityOperations):
        name = "random_name"
        FeaturestoreEntity_container = Mock(
            FeaturestoreEntityContainer(properties=Mock(FeaturestoreEntityContainerProperties()))
        )
        mock_featurestore_entity_operations._container_operation.get.return_value = FeaturestoreEntity_container
        mock_featurestore_entity_operations.restore(name=name)
        mock_featurestore_entity_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_featurestore_entity_operations._workspace_name,
            body=FeaturestoreEntity_container,
            resource_group_name=mock_featurestore_entity_operations._resource_group_name,
        )
