from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml._restclient.v2022_05_01.models._models_py3 import (
    ModelContainerData,
    ModelContainerDetails,
    ModelVersionData,
    ModelVersionDetails,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.entities._load_functions import load_model
from azure.ai.ml.exceptions import ErrorTarget, UnsupportedOperationError
from azure.ai.ml.operations import DatastoreOperations
from azure.ai.ml.operations._evaluator_operations import EvaluatorOperations
from azure.core.exceptions import ResourceNotFoundError


@pytest.fixture
def mock_datastore_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2024_01_01_preview: Mock,
    mock_aml_services_2024_07_01_preview: Mock,
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        serviceclient_2024_01_01_preview=mock_aml_services_2024_01_01_preview,
        serviceclient_2024_07_01_preview=mock_aml_services_2024_07_01_preview,
    )


@pytest.fixture
def mock_eval_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_datastore_operation: Mock,
) -> EvaluatorOperations:
    yield EvaluatorOperations(
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
) -> EvaluatorOperations:
    yield EvaluatorOperations(
        operation_scope=mock_registry_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2021_10_01_dataplanepreview,
        datastore_operations=mock_datastore_operation,
    )


def _load_flow(name: str, version: str = "42", **kwargs) -> Model:
    """Load the flow supplied with the tests."""
    return Model(
        path="./tests/test_configs/flows/basic/",
        name=name,
        description="F1 score evaluator.",
        version=version,
        properties={"is-promptflow": "true", "is-evaluator": "true"},
        **kwargs,
    )


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestModelOperations:
    def test_create_with_spec_file(
        self,
        mock_workspace_scope: OperationScope,
        mock_eval_operation: EvaluatorOperations,
    ) -> None:
        eval_name = "simple_flow"

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=eval_name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ) as mock_upload, patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=Model(properties={"is-promptflow": "true", "is-evaluator": "true"}),
        ):
            model = _load_flow(eval_name)
            path = Path(model._base_path, model.path).resolve()
            mock_eval_operation.create_or_update(model)
            mock_upload.assert_called_once_with(
                mock_workspace_scope,
                mock_eval_operation._model_op._datastore_operation,
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
        mock_eval_operation._model_op._model_versions_operation.create_or_update.assert_called_once()
        assert "version='42'" in str(mock_eval_operation._model_op._model_versions_operation.create_or_update.call_args)

    def test_create_autoincrement(
        self,
        mock_eval_operation: EvaluatorOperations,
        mock_workspace_scope: OperationScope,
    ) -> None:
        eval_name = "eval"
        model = _load_flow(eval_name, version=None)
        assert model._auto_increment_version
        model.version = None

        with patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=None,
        ), patch(
            "azure.ai.ml.operations._model_operations._get_next_version_from_container",
            return_value="version",
        ) as mock_nextver, patch(
            "azure.ai.ml.operations._model_operations._check_and_upload_path",
            return_value=(model, "indicatorfile.txt"),
        ), patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=model,
        ), patch(
            "azure.ai.ml.operations._model_operations._get_default_datastore_info",
            return_value=None,
        ):
            mock_eval_operation.create_or_update(model)
            mock_nextver.assert_called_once()

            mock_eval_operation._model_op._model_versions_operation.create_or_update.assert_called_once_with(
                body=model._to_rest_object(),
                name=model.name,
                version=mock_nextver.return_value,
                resource_group_name=mock_workspace_scope.resource_group_name,
                workspace_name=mock_workspace_scope.workspace_name,
            )

    def test_get_name_and_version(self, mock_eval_operation: EvaluatorOperations) -> None:
        mock_eval_operation._model_op._model_container_operation.get.return_value = None
        with patch(
            "azure.ai.ml.operations._evaluator_operations.Model._from_rest_object",
            return_value=None,
        ):
            mock_eval_operation.get(name="random_string", version="1")
        mock_eval_operation._model_op._model_versions_operation.get.assert_called_once()
        assert mock_eval_operation._model_op._model_container_operation.get.call_count == 0

    def test_get_no_version(self, mock_eval_operation: EvaluatorOperations) -> None:
        name = "random_string"
        with pytest.raises(Exception):
            mock_eval_operation.get(name=name)

    @patch.object(Model, "_from_rest_object", new=Mock())
    @patch.object(Model, "_from_container_rest_object", new=Mock())
    def test_list(self, mock_eval_operation: EvaluatorOperations) -> None:
        mock_eval_operation._model_op._model_versions_operation.list.return_value = [Mock(Model) for _ in range(10)]

        mock_eval_operation.list(name="random_string")
        mock_eval_operation._model_op._model_versions_operation.list.assert_called_once()

    def test_list_with_no_name_raises(self, mock_eval_operation: EvaluatorOperations) -> None:
        """Test that listing evaluators without values raises an unsupported exception."""
        with pytest.raises(UnsupportedOperationError) as cm:
            mock_eval_operation.list(None)
        assert "list on evaluation operations without name provided" in cm.value.args[0]

    @pytest.mark.skip(
        "Skipping test for archive and restore as we have removed it from interface. "
        "These test will be available when the appropriate API will be enabled at "
        "GenericAssetService."
    )
    def test_archive_version(self, mock_eval_operation: EvaluatorOperations) -> None:
        name = "random_string"
        model_version = Mock(ModelVersionData(properties=Mock(ModelVersionDetails())))
        version = "1"
        mock_eval_operation._model_op._model_versions_operation.get.return_value = model_version
        with patch(
            "azure.ai.ml.operations._evaluator_operations.ModelOperations.get",
            return_value=Model(properties={"is-promptflow": "true", "is-evaluator": "true"}),
        ):
            mock_eval_operation.archive(name=name, version=version)
        mock_eval_operation._model_op._model_versions_operation.create_or_update.assert_called_once_with(
            name=name,
            version=version,
            workspace_name=mock_eval_operation._model_op._workspace_name,
            body=model_version,
            resource_group_name=mock_eval_operation._model_op._resource_group_name,
        )

    @pytest.mark.skip(
        "Skipping test for archive and restore as we have removed it from interface. "
        "These test will be available when the appropriate API will be enabled at "
        "GenericAssetService."
    )
    def test_archive_container(self, mock_eval_operation: EvaluatorOperations) -> None:
        name = "random_string"
        model_container = Mock(ModelContainerData(properties=Mock(ModelContainerDetails())))
        mock_eval_operation._model_op._model_container_operation.get.return_value = model_container
        with patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=Model(properties={"is-promptflow": "true", "is-evaluator": "true"}),
        ):
            mock_eval_operation.archive(name=name)
        mock_eval_operation._model_op._model_container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_eval_operation._model_op._workspace_name,
            body=model_container,
            resource_group_name=mock_eval_operation._model_op._resource_group_name,
        )

    @pytest.mark.skip(
        "Skipping test for archive and restore as we have removed it from interface. "
        "These test will be available when the appropriate API will be enabled at "
        "GenericAssetService."
    )
    def test_restore_version(self, mock_eval_operation: EvaluatorOperations) -> None:
        name = "random_string"
        model = Mock(ModelVersionData(properties=Mock(ModelVersionDetails())))
        version = "1"
        mock_eval_operation._model_op._model_versions_operation.get.return_value = model
        with patch(
            "azure.ai.ml.operations._evaluator_operations.ModelOperations.get",
            return_value=Model(properties={"is-promptflow": "true", "is-evaluator": "true"}),
        ):
            mock_eval_operation.restore(name=name, version=version)
        mock_eval_operation._model_op._model_versions_operation.create_or_update.assert_called_with(
            name=name,
            version=version,
            workspace_name=mock_eval_operation._model_op._workspace_name,
            body=model,
            resource_group_name=mock_eval_operation._model_op._resource_group_name,
        )

    @pytest.mark.skip(
        "Skipping test for archive and restore as we have removed it from interface. "
        "These test will be available when the appropriate API will be enabled at "
        "GenericAssetService."
    )
    def test_restore_container(self, mock_eval_operation: EvaluatorOperations) -> None:
        name = "random_string"
        model_container = Mock(ModelContainerData(properties=Mock(ModelContainerDetails())))
        mock_eval_operation._model_op._model_container_operation.get.return_value = model_container
        with patch(
            "azure.ai.ml.operations._evaluator_operations.ModelOperations._get_latest_version",
            return_value=Model(properties={"is-promptflow": "true", "is-evaluator": "true"}),
        ):
            mock_eval_operation.restore(name=name)
        mock_eval_operation._model_op._model_container_operation.create_or_update.assert_called_once_with(
            name=name,
            workspace_name=mock_eval_operation._model_op._workspace_name,
            body=model_container,
            resource_group_name=mock_eval_operation._model_op._resource_group_name,
        )

    def test_create_with_datastore(
        self,
        mock_workspace_scope: OperationScope,
        mock_eval_operation: EvaluatorOperations,
    ) -> None:
        eval_name = "eval_string"

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=eval_name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ) as mock_upload, patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=Model(properties={"is-promptflow": "true", "is-evaluator": "true"}),
        ):
            model = _load_flow(eval_name, version="3", datastore="workspaceartifactstore")
            path = Path(model._base_path, model.path).resolve()
            mock_eval_operation.create_or_update(model)
            mock_upload.assert_called_once_with(
                mock_workspace_scope,
                mock_eval_operation._model_op._datastore_operation,
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

    def test_create_evaluator_model(self, mock_eval_operation: EvaluatorOperations):
        """Test that evaluator operations add correct tags to model."""
        p = "./tests/test_configs/model/model_with_datastore.yml"
        plane_model = load_model(p)
        eval_name = "eval_string"

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=eval_name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ), patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=Model(properties={"is-promptflow": "true", "is-evaluator": "true"}),
        ):
            mock_eval_operation.create_or_update(plane_model)
        assert plane_model.properties == {
            "is-promptflow": "true",
            "is-evaluator": "true",
        }

    def test_get_non_evaluator_raises(self, mock_eval_operation: EvaluatorOperations):
        """Test that evaluator operations add correct tags to model."""
        p = "./tests/test_configs/model/model_with_datastore.yml"
        plane_model = load_model(p)
        mock_eval_operation._model_op._model_container_operation.get.return_value = None
        with patch(
            "azure.ai.ml.operations._evaluator_operations.Model._from_rest_object",
            return_value=plane_model,
        ):
            with pytest.raises(ResourceNotFoundError) as cm:
                mock_eval_operation.get(name="random_string", version="1")
            assert f"Evaluator random_string with version 1 not found." in cm.value.args[0]
