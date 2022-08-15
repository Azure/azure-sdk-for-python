from unittest.mock import Mock, patch
import pytest
from pathlib import Path
from azure.core.exceptions import HttpResponseError, ResourceExistsError

from azure.ai.ml.operations import (
    DataOperations,
    DatastoreOperations,
    EnvironmentOperations,
    ModelOperations,
    ComponentOperations,
    OnlineEndpointOperations,
)
from azure.ai.ml.operations._operation_orchestrator import OperationOrchestrator
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml.constants import (
    AZUREML_RESOURCE_PROVIDER,
    NAMED_RESOURCE_ID_FORMAT,
    VERSIONED_RESOURCE_ID_FORMAT,
    AzureMLResourceType,
)
from test_utilities.constants import Test_Resource_Group, Test_Subscription, Test_Workspace_Name
from pytest_mock import MockFixture
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.entities._assets import Model, Code, Data, Environment


@pytest.fixture
def environment_operations(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml.operations._environment_operations.EnvironmentOperations")


@pytest.fixture
def datastore_operations(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml.operations._datastore_operations.DatastoreOperations")


@pytest.fixture
def model_operations(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml.operations._model_operations.ModelOperations")


@pytest.fixture
def code_operations(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml.operations._code_operations.CodeOperations")


@pytest.fixture
def data_operations(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml.operations._data_operations.DataOperations")


@pytest.fixture
def component_operations(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml.operations._component_operations.ComponentOperations")


@pytest.fixture
def mock_datastore_operations(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock
) -> CodeOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        serviceclient_2022_05_01=mock_aml_services_2022_05_01,
    )


@pytest.fixture
def mock_code_assets_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2021_10_01: Mock,
    mock_datastore_operations: DatastoreOperations,
) -> CodeOperations:
    yield CodeOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2021_10_01,
        datastore_operations=mock_datastore_operations,
    )


@pytest.fixture
def mock_model_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_05_01: Mock,
    mock_datastore_operations: DatastoreOperations,
) -> ModelOperations:
    yield ModelOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operations,
    )


@pytest.fixture
def mock_environment_operations(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock
) -> EnvironmentOperations:
    yield EnvironmentOperations(operation_scope=mock_workspace_scope, service_client=mock_aml_services_2022_05_01)


@pytest.fixture
def mock_local_endpoint_helper() -> Mock:
    yield Mock()


@pytest.fixture
def mock_endpoint_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_02_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_code_assets_operations: Mock,
    mock_data_operations: Mock,
    mock_local_endpoint_helper: Mock,
) -> OnlineEndpointOperations:
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.CODE, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.MODEL, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.ENVIRONMENT, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.DATA, mock_data_operations)

    yield OnlineEndpointOperations(
        operation_scope=mock_workspace_scope,
        service_client_10_2021=mock_aml_services_2022_02_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        local_endpoint_helper=mock_local_endpoint_helper,
    )


@pytest.fixture
def operation_container(
    code_operations: CodeOperations,
    environment_operations: EnvironmentOperations,
    datastore_operations: DatastoreOperations,
    model_operations: ModelOperations,
    data_operations: DataOperations,
    component_operations: ComponentOperations,
) -> OperationsContainer:
    container = OperationsContainer()
    container.add(AzureMLResourceType.DATASTORE, datastore_operations)
    container.add(AzureMLResourceType.MODEL, model_operations)
    container.add(AzureMLResourceType.CODE, code_operations)
    container.add(AzureMLResourceType.ENVIRONMENT, environment_operations)
    container.add(AzureMLResourceType.DATA, data_operations)
    container.add(AzureMLResourceType.COMPONENT, component_operations)
    yield container


@pytest.fixture
def operation_orchestrator(
    mock_workspace_scope: OperationScope, operation_container: OperationsContainer
) -> OperationOrchestrator:
    yield OperationOrchestrator(operation_container=operation_container, operation_scope=mock_workspace_scope)


@pytest.fixture
def create_yaml_inline_model(tmp_path: Path, resource_group_name: str) -> Path:
    content = f"""
name: aksendpoint
target: azureml:/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/sdkv2endpointaks
auth_mode: Key
traffic:
    blue: 0
deployments:
    -   name: blue
        model:
            name: some_name
            version: 2
            path: ./test.py
        code_configuration:
            code: ./endpoint
            scoring_script: ./test.py
        environment: azureml:/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/environments/AzureML-sklearn-0.24-ubuntu18.04-py37-cpu/versions/1
    """
    p = tmp_path / "create_model_inline.yaml"
    p.write_text(content)
    return p


@pytest.mark.unittest
class TestOperationOrchestration:
    def test_code_arm_id(self, operation_orchestrator: OperationOrchestrator) -> None:
        code = VERSIONED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.CODE,
            "6ec5cbc4-2ba3-4fb8-826f-d5f65cfcbb8d",
            "1",
        )
        result = operation_orchestrator.get_asset_arm_id(code, azureml_type=AzureMLResourceType.CODE)
        assert code == result

    def test_model_arm_id(self, operation_orchestrator: OperationOrchestrator) -> None:
        model = VERSIONED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.MODEL,
            "testmodel",
            "1",
        )

        result = operation_orchestrator.get_asset_arm_id(model, azureml_type=AzureMLResourceType.MODEL)
        assert model == result

    def test_environment_arm_id(self, operation_orchestrator: OperationOrchestrator) -> None:
        environment = VERSIONED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.ENVIRONMENT,
            "testenv",
            "1",
        )
        result = operation_orchestrator.get_asset_arm_id(environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        assert environment == result

    def test_data_arm_id(self, operation_orchestrator: OperationOrchestrator) -> None:
        data = VERSIONED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.DATA,
            "testdata",
            "1",
        )
        result = operation_orchestrator.get_asset_arm_id(data, azureml_type=AzureMLResourceType.DATA)
        assert data == result

    def test_code_arm_id_short_name(self, operation_orchestrator: OperationOrchestrator) -> None:
        expected = VERSIONED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.CODE,
            "test-code",
            "1",
        )
        code = "test-code:1"
        assert expected == operation_orchestrator.get_asset_arm_id(code, azureml_type=AzureMLResourceType.CODE)

    def test_model_arm_id_short_name(self, operation_orchestrator: OperationOrchestrator) -> None:
        expected = VERSIONED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.MODEL,
            "testmodel",
            "1",
        )
        model = "testmodel:1"
        assert expected == operation_orchestrator.get_asset_arm_id(model, azureml_type=AzureMLResourceType.MODEL)

    def test_environment_arm_id_short_name(self, operation_orchestrator: OperationOrchestrator) -> None:
        expected = VERSIONED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.ENVIRONMENT,
            "testenv",
            "1",
        )
        environment = "testenv:1"
        assert expected == operation_orchestrator.get_asset_arm_id(
            environment, azureml_type=AzureMLResourceType.ENVIRONMENT
        )

    def test_data_arm_id_short_name(self, operation_orchestrator: OperationOrchestrator) -> None:
        expected = VERSIONED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.DATA,
            "testdata",
            "1",
        )
        data = "testdata:1"
        assert expected == operation_orchestrator.get_asset_arm_id(data, azureml_type=AzureMLResourceType.DATA)

    def test_compute_arm_id_short_name(self, operation_orchestrator: OperationOrchestrator) -> None:
        expected = NAMED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.COMPUTE,
            "cpu-cluster",
        )
        compute = "cpu-cluster"
        assert expected == operation_orchestrator.get_asset_arm_id(compute, azureml_type=AzureMLResourceType.COMPUTE)

    def test_code_arm_id_entity_no_call(
        self,
        operation_orchestrator: OperationOrchestrator,
        mocker: MockFixture,
    ) -> None:
        code = Code(name="name", version="1", path="test_path")
        mocker.patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                "name",
                "1",
                "path",
                "/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                "azureml-blobstore-test",
            ),
        )
        result = operation_orchestrator.get_asset_arm_id(
            code, register_asset=False, azureml_type=AzureMLResourceType.CODE
        )
        assert result.name == "name"
        assert result.version == "1"
        assert result.path == "azureml-blobstore-test/path"

    def test_model_arm_id_entity_anonymous_no_call(
        self,
        operation_orchestrator: OperationOrchestrator,
        model_operations: ModelOperations,
        mocker: MockFixture,
    ) -> None:
        model = Model(path="tests/test_configs/environment/endpoint_conda.yml")
        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                "other-name",
                "3",
                "path",
                "/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                "azureml-blobstore-test",
            ),
        ):
            result = operation_orchestrator.get_asset_arm_id(
                model, register_asset=False, azureml_type=AzureMLResourceType.MODEL
            )
        assert model._is_anonymous
        assert result.name == "other-name"
        assert result.version == "3"
        assert "datastore_id" in result.path
        assert result.path.endswith("path")

    def test_model_arm_id_entity_not_anonymous(
        self,
        operation_orchestrator: OperationOrchestrator,
        model_operations: ModelOperations,
        mocker: MockFixture,
    ) -> None:
        model = Model(name="name", version="1", path="test_path")
        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                "other-name",
                "3",
                "path",
                "/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                "azureml-blobstore-test",
            ),
        ):
            result = operation_orchestrator.get_asset_arm_id(
                model, register_asset=False, azureml_type=AzureMLResourceType.MODEL
            )
        assert not model._is_anonymous
        assert result.name == "name"
        assert result.version == "1"
        assert "datastore_id" in result.path
        assert result.path.endswith("path")

    def test_model_arm_id_entity_anonymous(
        self,
        operation_orchestrator: OperationOrchestrator,
        model_operations: ModelOperations,
        mocker: MockFixture,
    ) -> None:
        model = Model(path="tests/test_configs/environment/endpoint_conda.yml")
        with patch(
            "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
            return_value=ArtifactStorageInfo(
                "other-name",
                "3",
                "path",
                "/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                "azureml-blobstore-test",
            ),
        ):
            result = operation_orchestrator.get_asset_arm_id(
                model, register_asset=False, azureml_type=AzureMLResourceType.MODEL
            )
        assert model._is_anonymous
        assert result.name == "other-name"
        assert result.version == "3"
        assert "datastore_id" in result.path
        assert result.path.endswith("path")
        print(result.path)

    @patch(
        "azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore",
        Mock(
            return_value=ArtifactStorageInfo(
                "name",
                "1",
                "path",
                "/subscriptions/mock/resourceGroups/mock/providers/Microsoft.MachineLearningServices/workspaces/mock/datastores/datastore_id",
                "azureml-blobstore-test",
            )
        ),
    )
    def test_data_arm_id_entity_no_call(
        self,
        operation_orchestrator: OperationOrchestrator,
        mocker: MockFixture,
    ) -> None:
        data = Data(name="name", version="1", path="test_path", type="uri_file")
        result = operation_orchestrator._get_data_arm_id(data_asset=data, register_asset=False)
        assert result.name == "name"
        assert result.version == "1"
        assert result.path == "azureml://datastores/datastore_id/paths/path"

    def test_environment_arm_id_entity_no_call(self, operation_orchestrator: OperationOrchestrator) -> None:
        environment = Environment(name="name", version="1")
        result = operation_orchestrator.get_asset_arm_id(
            environment, register_asset=False, azureml_type=AzureMLResourceType.ENVIRONMENT
        )
        assert result == environment

    def test_model_arm_id_entity(self, operation_orchestrator: OperationOrchestrator) -> None:
        model = Model(name="name", version="1", path="test_path")
        operation_orchestrator.get_asset_arm_id(model, azureml_type=AzureMLResourceType.MODEL)
        operation_orchestrator._model.create_or_update.assert_called_once()

    def test_environment_arm_id_entity(self, operation_orchestrator: OperationOrchestrator) -> None:
        environment = Environment(name="name", version="1")
        operation_orchestrator.get_asset_arm_id(environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        operation_orchestrator._environments.create_or_update.assert_called_once()

    def test_arm_id_not_start_with_slash(self, operation_orchestrator: OperationOrchestrator):

        arm_id = NAMED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            AzureMLResourceType.DATA,
            "fake-data",
        )
        arm_id = arm_id[1:]
        # test when arm id didn't start with slash like subscriptions/xxx, proper error message is shown
        with pytest.raises(Exception) as error_info:
            operation_orchestrator.get_asset_arm_id(arm_id, azureml_type=AzureMLResourceType.DATA)
        assert str(error_info.value) == f"Could not parse {arm_id}. If providing an ARM id, it should start with a '/'."

    def test_client_side_label_resolution(self, operation_orchestrator: OperationOrchestrator):
        # TODO: This test should be removed once labels are handled service-side

        name = "foo"
        label = "latest"
        resolved_version = str(2)
        assettype = AzureMLResourceType.DATA
        expected = VERSIONED_RESOURCE_ID_FORMAT.format(
            Test_Subscription,
            Test_Resource_Group,
            AZUREML_RESOURCE_PROVIDER,
            Test_Workspace_Name,
            assettype,
            name,
            resolved_version,
        )

        with patch.object(
            operation_orchestrator._operation_container.all_operations[assettype],
            "_managed_label_resolver",
            {label: lambda _: Data(name=name, version=resolved_version)},
        ):
            result = operation_orchestrator.get_asset_arm_id(f"{name}@{label}", assettype)
            assert expected == result

            with pytest.raises(Exception):
                operation_orchestrator.get_asset_arm_id(f"{name}@label_does_not_exist")

    def test_component_registry_id(self, operation_orchestrator: OperationOrchestrator) -> None:
        component = "azureml://registries/testFeed/components/My_Hello_World_Asset_2/versions/1"
        result = operation_orchestrator.get_asset_arm_id(component, azureml_type=AzureMLResourceType.COMPONENT)
        assert component == result
