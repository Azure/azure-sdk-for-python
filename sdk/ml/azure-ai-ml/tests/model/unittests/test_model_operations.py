from pathlib import Path
from typing import Iterable
from unittest.mock import Mock, patch
import pytest

from azure.ai.ml import load_model
from azure.ai.ml._restclient.v2022_05_01.models._models_py3 import (
    ModelContainerData,
    ModelContainerDetails,
    ModelVersionData,
    ModelVersionDetails,
)
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.exceptions import ErrorTarget
from azure.ai.ml.operations import DatastoreOperations, ModelOperations


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
def mock_model_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_datastore_operation: Mock,
) -> ModelOperations:
    yield ModelOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operation,
    )


@pytest.fixture
def mock_model_operation_reg(
    mock_registry_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2021_10_01_dataplanepreview: Mock,
    mock_datastore_operation: Mock,
) -> ModelOperations:
    yield ModelOperations(
        operation_scope=mock_registry_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2021_10_01_dataplanepreview,
        datastore_operations=mock_datastore_operation,
    )


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestModelOperations:
    def test_create_with_spec_file(
        self,
        mock_workspace_scope: OperationScope,
        mock_model_operation: ModelOperations,
        tmp_path: Path,
    ) -> None:
        model_name = f"model_random_string"
        p = tmp_path / "model_full.yml"
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")
        p.write_text(
            f"""
name: {model_name}
path: ./model.pkl
version: 3"""
        )

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=model_name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ) as mock_upload, patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=Model(),
        ):
            model = load_model(source=p)
            path = Path(model._base_path, model.path).resolve()
            mock_model_operation.create_or_update(model)
            mock_upload.assert_called_once_with(
                mock_workspace_scope,
                mock_model_operation._datastore_operation,
                path,
                asset_name=model.name,
                asset_version=model.version,
                datastore_name=None,
                asset_hash=None,
                sas_uri=None,
                artifact_type=ErrorTarget.MODEL,
                show_progress=True,
                ignore_file=None,
                blob_uri=None,
            )
        mock_model_operation._model_versions_operation.create_or_update.assert_called_once()
        assert "version='3'" in str(mock_model_operation._model_versions_operation.create_or_update.call_args)

    def test_create_autoincrement(
        self,
        mock_model_operation: ModelOperations,
        mock_workspace_scope: OperationScope,
        tmp_path: Path,
    ) -> None:
        model_name = f"model_random_string"
        p = tmp_path / "model_full.yml"
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")
        p.write_text(
            f"""
name: {model_name}
path: ./model.pkl"""
        )
        model = load_model(source=p)
        assert model._auto_increment_version
        model.version = None

        with patch("azure.ai.ml.operations._model_operations.Model._from_rest_object", return_value=None), patch(
            "azure.ai.ml.operations._model_operations._get_next_version_from_container", return_value="version"
        ) as mock_nextver, patch(
            "azure.ai.ml.operations._model_operations._check_and_upload_path",
            return_value=(model, "indicatorfile.txt"),
        ), patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object", return_value=model
        ), patch(
            "azure.ai.ml.operations._model_operations._get_default_datastore_info", return_value=None
        ):
            mock_model_operation.create_or_update(model)
            mock_nextver.assert_called_once()

            mock_model_operation._model_versions_operation.create_or_update.assert_called_once_with(
                body=model._to_rest_object(),
                name=model.name,
                version=mock_nextver.return_value,
                resource_group_name=mock_workspace_scope.resource_group_name,
                workspace_name=mock_workspace_scope.workspace_name,
            )

    def test_get_name_and_version(self, mock_model_operation: ModelOperations) -> None:
        mock_model_operation._model_container_operation.get.return_value = None
        with patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=None,
        ):
            mock_model_operation.get(name="random_string", version="1")
        mock_model_operation._model_versions_operation.get.assert_called_once()
        assert mock_model_operation._model_container_operation.get.call_count == 0

    def test_get_no_version(self, mock_model_operation: ModelOperations) -> None:
        name = "random_string"
        with pytest.raises(Exception):
            mock_model_operation.get(name=name)

    @patch.object(Model, "_from_rest_object", new=Mock())
    @patch.object(Model, "_from_container_rest_object", new=Mock())
    def test_list(self, mock_model_operation: ModelOperations) -> None:
        mock_model_operation._model_versions_operation.list.return_value = [Mock(Model) for _ in range(10)]
        mock_model_operation._model_container_operation.list.return_value = [Mock(Model) for _ in range(10)]
        result = mock_model_operation.list()
        assert isinstance(result, Iterable)
        mock_model_operation._model_container_operation.list.assert_called_once()
        mock_model_operation.list(name="random_string")
        mock_model_operation._model_versions_operation.list.assert_called_once()

    def test_archive_version(self, mock_model_operation: ModelOperations) -> None:
        name = "random_string"
        model_version = Mock(ModelVersionData(properties=Mock(ModelVersionDetails())))
        version = "1"
        mock_model_operation._model_versions_operation.get.return_value = model_version
        mock_model_operation.archive(name=name, version=version)
        mock_model_operation._model_versions_operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_model_operation._workspace_name,
            body=model_version,
            resource_group_name=mock_model_operation._resource_group_name,
        )

    def test_archive_container(self, mock_model_operation: ModelOperations) -> None:
        name = "random_string"
        model_container = Mock(ModelContainerData(properties=Mock(ModelContainerDetails())))
        mock_model_operation._model_container_operation.get.return_value = model_container
        mock_model_operation.archive(name=name)
        mock_model_operation._model_container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_model_operation._workspace_name,
            body=model_container,
            resource_group_name=mock_model_operation._resource_group_name,
        )

    def test_restore_version(self, mock_model_operation: ModelOperations) -> None:
        name = "random_string"
        model = Mock(ModelVersionData(properties=Mock(ModelVersionDetails())))
        version = "1"
        mock_model_operation._model_versions_operation.get.return_value = model
        mock_model_operation.restore(name=name, version=version)
        mock_model_operation._model_versions_operation.create_or_update.assert_called_with(
            name=name,
            version=version,
            workspace_name=mock_model_operation._workspace_name,
            body=model,
            resource_group_name=mock_model_operation._resource_group_name,
        )

    def test_restore_container(self, mock_model_operation: ModelOperations) -> None:
        name = "random_string"
        model_container = Mock(ModelContainerData(properties=Mock(ModelContainerDetails())))
        mock_model_operation._model_container_operation.get.return_value = model_container
        mock_model_operation.restore(name=name)
        mock_model_operation._model_container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_model_operation._workspace_name,
            body=model_container,
            resource_group_name=mock_model_operation._resource_group_name,
        )

    def test_create_with_datastore(
        self,
        mock_workspace_scope: OperationScope,
        mock_model_operation: ModelOperations,
    ) -> None:
        p = "./tests/test_configs/model/model_with_datastore.yml"
        model_name = f"model_random_string"

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=model_name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ) as mock_upload, patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=Model(),
        ):
            model = load_model(p)
            path = Path(model._base_path, model.path).resolve()
            mock_model_operation.create_or_update(model)
            mock_upload.assert_called_once_with(
                mock_workspace_scope,
                mock_model_operation._datastore_operation,
                path,
                asset_name=model.name,
                asset_version=model.version,
                datastore_name="workspaceartifactstore",
                asset_hash=None,
                sas_uri=None,
                artifact_type=ErrorTarget.MODEL,
                show_progress=True,
                ignore_file=None,
                blob_uri=None,
            )

    # def test_promote_model_from_workspace(
    #     self,
    #     mock_model_operation_reg: ModelOperations,
    #     mock_model_operation: ModelOperations,
    #     tmp_path: Path,
    # ) -> None:
    #     model_name = f"model_random_string"
    #     p = tmp_path / "model_full.yml"
    #     model_path = tmp_path / "model.pkl"
    #     model_path.write_text("hello world")
    #     p.write_text(
    #         f"""
    # name: {model_name}
    # path: ./model.pkl
    # version: 3"""
    #     )

    #     with patch(
    #         "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
    #         return_value=ArtifactStorageInfo(
    #             name=model_name,
    #             version="3",
    #             relative_path="path",
    #             datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
    #             container_name="containerName",
    #         ),
    #     ) as mock_upload, patch(
    #         "azure.ai.ml.operations._model_operations.Model._from_rest_object",
    #         return_value=Model(),
    #     ):
    #         model = load_model(source=p)
    #         model_to_promote = mock_model_operation._prepare_to_copy(model, "new_name", "new_version")
    #         assert model_to_promote.name == "new_name"
    #         assert model_to_promote.version == "new_version"
    #         mock_model_operation_reg._model_versions_operation.get.side_effect = Mock(
    #             side_effect=ResourceNotFoundError("Test")
    #         )
    #         mock_model_operation_reg.create_or_update(model_to_promote)
    #         mock_model_operation_reg._service_client.resource_management_asset_reference.begin_import_method.assert_called_once()

    def test_model_entity_class_exist(self):
        try:
            from azure.ai.ml.entities import WorkspaceModelReference
        except ImportError:
            assert False, "WorkspaceModelReference class not found"
