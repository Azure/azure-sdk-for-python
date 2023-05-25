import pytest

from azure.ai.ml._utils._storage_utils import get_ds_name_and_path_prefix
from pathlib import Path
from unittest.mock import Mock, patch

from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._assets import Code, Data, Environment, Model
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.operations import (
    DataOperations,
    DatastoreOperations,
    EnvironmentOperations,
    ModelOperations,
)
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.ai.ml.exceptions import ErrorTarget


@pytest.fixture
def mock_datastore_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config_no_progress: OperationConfig,
    mock_aml_services_2022_10_01: Mock,
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config_no_progress,
        serviceclient_2022_10_01=mock_aml_services_2022_10_01,
    )


@pytest.fixture
def mock_model_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config_no_progress: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_datastore_operations: DatastoreOperations,
) -> ModelOperations:
    yield ModelOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config_no_progress,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operations,
    )


@pytest.fixture
def mock_code_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config_no_progress: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_datastore_operations: Mock,
) -> CodeOperations:
    yield CodeOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config_no_progress,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operations,
    )


@pytest.fixture
def mock_data_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config_no_progress: OperationConfig,
    mock_aml_services_2022_10_01: Mock,
    mock_datastore_operations: Mock,
    mock_machinelearning_client: Mock,
) -> DataOperations:
    yield DataOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config_no_progress,
        service_client=mock_aml_services_2022_10_01,
        datastore_operations=mock_datastore_operations,
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
    )


@pytest.fixture
def mock_environment_operation(
    mock_registry_scope: OperationScope,
    mock_operation_config_no_progress: OperationConfig,
    mock_aml_services_2021_10_01_dataplanepreview: Mock,
    mock_machinelearning_registry_client: Mock,
) -> EnvironmentOperations:
    yield EnvironmentOperations(
        operation_scope=mock_registry_scope,
        operation_config=mock_operation_config_no_progress,
        service_client=mock_aml_services_2021_10_01_dataplanepreview,
        all_operations=mock_machinelearning_registry_client._operation_container,
    )


@pytest.mark.unittest
class TestStorageUtils:
    def test_storage_uri_to_prefix(
        self,
    ) -> None:
        # These are the asset storage patterns supported for download
        reg_uri_1 = "https://ccccccccddddd345.blob.core.windows.net/demoregist-16d33653-20bf-549b-a3c1-17d975359581/ExperimentRun/dcid.5823bbb4-bb28-497c-b9f2-1ff3a0778b10/model"
        reg_uri_2 = "https://ccccccccccc1978ccc.blob.core.windows.net/demoregist-b46fb119-d3f8-5994-a971-a9c730227846/LocalUpload/0c225a0230907e61c00ea33eac35a54d/model.pkl"
        reg_uri_3 = "https://ccccccccddr546ddd.blob.core.windows.net/some-reg-9717e928-33c2-50c2-90f5-f410b12b8727/sklearn_regression_model.pkl"
        workspace_uri_1 = "azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/000000000000000/workspaces/some_test_3/datastores/workspaceblobstore/paths/LocalUpload/26960525964086056a7301dd061fb9be/lightgbm_mlflow_model"

        assert get_ds_name_and_path_prefix(reg_uri_1, "registry_name") == (
            None,
            "ExperimentRun/dcid.5823bbb4-bb28-497c-b9f2-1ff3a0778b10/model",
        )
        assert get_ds_name_and_path_prefix(reg_uri_2, "registry_name") == (
            None,
            "LocalUpload/0c225a0230907e61c00ea33eac35a54d/model.pkl",
        )
        assert get_ds_name_and_path_prefix(reg_uri_3, "registry_name") == (None, "sklearn_regression_model.pkl")
        assert get_ds_name_and_path_prefix(workspace_uri_1) == (
            "workspaceblobstore",
            "LocalUpload/26960525964086056a7301dd061fb9be/lightgbm_mlflow_model",
        )

    def test_storage_uri_to_prefix_malformed(
        self,
    ) -> None:
        reg_uri_bad = "https://ccccccccddd4512d.blob.core.windows.net/5823bbb4-bb28-497c-b9f2-1ff3a0778b10"
        workspace_uri_bad = "azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/000000000000000/workspaces/some_test_3/datastores/workspaceblobstore/path/LocalUpload/26960525964086056a7301dd061fb9be/lightgbm_mlflow_model"

        with pytest.raises(Exception) as e:
            get_ds_name_and_path_prefix(reg_uri_bad, "registry_name")
        assert "Registry asset URI could not be parsed." in str(e.value)

        with pytest.raises(Exception) as e:
            get_ds_name_and_path_prefix(workspace_uri_bad)
        assert "Workspace asset URI could not be parsed." in str(e.value)

    def test_show_progress_disabled_model(
        self,
        mock_model_operation: ModelOperations,
        tmp_path: Path,
    ) -> None:
        # Ensure that show_progress set in OperationConfig in MLClient is being passed through operation orchestrator

        model = Model(path=tmp_path)

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=model.name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ), patch(
            "azure.ai.ml.operations._model_operations._check_and_upload_path",
            return_value=(model, "indicatorfile.txt"),
        ) as mock_thing, patch(
            "azure.ai.ml.operations._model_operations.Model._from_rest_object",
            return_value=Model(),
        ):
            mock_model_operation.create_or_update(model)
            mock_thing.assert_called_once_with(
                artifact=model,
                asset_operations=mock_model_operation,
                sas_uri=None,
                artifact_type=ErrorTarget.MODEL,
                show_progress=False,
            )

    def test_show_progress_disabled_code(
        self,
        tmp_path: Path,
        mock_code_operation: CodeOperations,
    ) -> None:
        # Ensure that show_progress set in OperationConfig in MLClient is being passed through operation orchestrator

        code = Code(path=tmp_path)

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=code.name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ), patch(
            "azure.ai.ml.operations._code_operations._check_and_upload_path",
            return_value=(code, "indicatorfile.txt"),
        ) as mock_thing, patch(
            "azure.ai.ml.operations._code_operations.Code._from_rest_object",
            return_value=Code(),
        ), patch(
            "azure.ai.ml.operations._code_operations.get_storage_info_for_non_registry_asset",
            return_value={"sas_uri": "sas_uri", "blob_uri": "blob_uri"},
        ):
            mock_code_operation.create_or_update(code)
            mock_thing.assert_called_once_with(
                artifact=code,
                asset_operations=mock_code_operation,
                artifact_type=ErrorTarget.CODE,
                show_progress=False,
                blob_uri="blob_uri",
                sas_uri="sas_uri",
            )

    def test_show_progress_disabled_data(
        self,
        tmp_path: Path,
        mock_data_operation: DataOperations,
    ) -> None:
        # Ensure that show_progress set in OperationConfig in MLClient is being passed through operation orchestrator

        data = Data(path=tmp_path)

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=data.name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ), patch(
            "azure.ai.ml.operations._data_operations._check_and_upload_path",
            return_value=(data, "indicatorfile.txt"),
        ) as mock_thing, patch(
            "azure.ai.ml.operations._data_operations.Data._from_rest_object",
            return_value=Data(),
        ):
            mock_data_operation.create_or_update(data)
            mock_thing.assert_called_once_with(
                artifact=data,
                asset_operations=mock_data_operation,
                sas_uri=None,
                artifact_type=ErrorTarget.DATA,
                show_progress=False,
            )

    def test_show_progress_disabled_env(
        self,
        mock_environment_operation: EnvironmentOperations,
    ) -> None:
        # Ensure that show_progress set in OperationConfig in MLClient is being passed through operation orchestrator

        environment = Environment(name="name", version="16", image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04")

        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                name=environment.name,
                version="3",
                relative_path="path",
                datastore_arm_id="/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                container_name="containerName",
            ),
        ), patch(
            "azure.ai.ml.operations._environment_operations._check_and_upload_env_build_context",
            return_value=environment,
        ) as mock_thing, patch(
            "azure.ai.ml.operations._environment_operations.Environment._from_rest_object",
            return_value=Environment(),
        ), patch(
            "azure.ai.ml.operations._environment_operations.get_sas_uri_for_registry_asset",
            return_value="mocksasuri",
        ):
            mock_environment_operation.create_or_update(environment)
            mock_thing.assert_called_once_with(
                environment=environment,
                operations=mock_environment_operation,
                sas_uri="mocksasuri",
                show_progress=False,
            )
