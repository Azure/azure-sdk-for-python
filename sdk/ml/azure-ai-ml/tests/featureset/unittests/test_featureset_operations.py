from typing import Iterable
from unittest.mock import Mock, patch

import pytest
from test_utilities.constants import Test_Resource_Group, Test_Workspace_Name

from azure.ai.ml._restclient.v2023_02_01_preview.models._models_py3 import (
    FeaturesetContainer,
    FeaturesetContainerProperties,
    FeaturesetVersion,
    FeaturesetVersionProperties,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities import Featureset, FeaturesetSpecification
from azure.ai.ml.operations import FeaturesetOperations
from azure.core.paging import ItemPaged


@pytest.fixture
def mock_featureset_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2023_02_01_preview: Mock,
) -> FeaturesetOperations:
    yield FeaturesetOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2023_02_01_preview,
    )


@pytest.mark.unittest
@patch.object(Featureset, "_from_rest_object", new=Mock())
@patch.object(Featureset, "_from_container_rest_object", new=Mock())
@pytest.mark.data_experiences_test
class TestFeaturesetOperations:
    def test_list(self, mock_featureset_operations: FeaturesetOperations) -> None:
        mock_featureset_operations._operation.list.return_value = [Mock(Featureset) for _ in range(10)]
        mock_featureset_operations._container_operation.list.return_value = [Mock(Featureset) for _ in range(10)]
        result = mock_featureset_operations.list()
        assert isinstance(result, Iterable)
        mock_featureset_operations._container_operation.list.assert_called_once()
        mock_featureset_operations.list(name="random_name")
        mock_featureset_operations._operation.list.assert_called_once()

    def test_get_with_version(self, mock_featureset_operations: FeaturesetOperations) -> None:
        name_only = "some_name"
        version = "1"
        featureset = Featureset(
            name=name_only,
            version=version,
            entities=["test_entity"],
            specification=FeaturesetSpecification(path="local/"),
        )
        with patch.object(ItemPaged, "next"), patch.object(Featureset, "_from_rest_object", return_value=featureset):
            mock_featureset_operations.get(name=name_only, version=version)
        mock_featureset_operations._operation.get.assert_called_once_with(
            name=name_only, version=version, resource_group_name=Test_Resource_Group, workspace_name=Test_Workspace_Name
        )

    def test_get_no_version(self, mock_featureset_operations: FeaturesetOperations) -> None:
        name = "random_name"
        with pytest.raises(Exception) as ex:
            mock_featureset_operations.get(name=name)
        assert "At least one required parameter is missing" in str(ex.value)

    def test_archive_version(self, mock_featureset_operations: FeaturesetOperations):
        name = "random_name"
        featureset_version = Mock(FeaturesetVersion(properties=Mock(FeaturesetVersionProperties(entities=["test"]))))
        version = "1"
        mock_featureset_operations._operation.get.return_value = featureset_version
        mock_featureset_operations.archive(name=name, version=version)
        mock_featureset_operations._operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_featureset_operations._workspace_name,
            body=featureset_version,
            resource_group_name=mock_featureset_operations._resource_group_name,
        )

    def test_archive_container(self, mock_featureset_operations: FeaturesetOperations):
        name = "random_name"
        featureset_container = Mock(
            FeaturesetContainer(properties=Mock(FeaturesetContainerProperties(description="test")))
        )
        mock_featureset_operations._container_operation.get.return_value = featureset_container
        mock_featureset_operations.archive(name=name)
        mock_featureset_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_featureset_operations._workspace_name,
            body=featureset_container,
            resource_group_name=mock_featureset_operations._resource_group_name,
        )

    def test_restore_version(self, mock_featureset_operations: FeaturesetOperations):
        name = "random_name"
        featureset_version = Mock(FeaturesetVersion(properties=Mock(FeaturesetVersionProperties(entities=["test"]))))
        version = "1"
        mock_featureset_operations._operation.get.return_value = featureset_version
        mock_featureset_operations.restore(name=name, version=version)
        mock_featureset_operations._operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_featureset_operations._workspace_name,
            body=featureset_version,
            resource_group_name=mock_featureset_operations._resource_group_name,
        )

    def test_restore_container(self, mock_featureset_operations: FeaturesetOperations):
        name = "random_name"
        featureset_container = Mock(
            FeaturesetContainer(properties=Mock(FeaturesetContainerProperties(entities=["test"])))
        )
        mock_featureset_operations._container_operation.get.return_value = featureset_container
        mock_featureset_operations.restore(name=name)
        mock_featureset_operations._container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_featureset_operations._workspace_name,
            body=featureset_container,
            resource_group_name=mock_featureset_operations._resource_group_name,
        )
