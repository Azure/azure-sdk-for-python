from pathlib import Path
from typing import Callable

from requests import Response

from unittest.mock import patch, Mock
import pytest

from azure.core.polling import LROPoller
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.ai.ml.operations import (
    DatastoreOperations,
    OnlineEndpointOperations,
    EnvironmentOperations,
    ModelOperations,
    WorkspaceOperations,
)
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.ai.ml.operations._online_endpoint_operations import _strip_zeroes_from_traffic

from azure.identity import DefaultAzureCredential
from azure.ai.ml._restclient.v2021_10_01.models import (
    EndpointAuthKeys,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    KubernetesOnlineDeployment as RestKubernetesOnlineDeployment,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    OnlineEndpointDetails as RestOnlineEndpoint,
    OnlineDeploymentData,
    OnlineEndpointData,
    OnlineDeploymentDetails,
)
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.constants import (
    AzureMLResourceType,
    HttpResponseStatusCode,
)
from azure.ai.ml.entities import (
    OnlineEndpoint,
)
from azure.ai.ml import load_online_endpoint

from pytest_mock import MockFixture


@pytest.fixture()
def mock_delete_poller() -> LROPoller:
    poller = Mock(spec_set=LROPoller)
    poller.result = lambda timeout: None
    poller.done = lambda: True
    yield poller


@pytest.fixture()
def mock_update_poller() -> LROPoller[OnlineEndpointData]:
    poller = Mock(spec_set=LROPoller)
    poller.done = lambda: True
    poller.result = lambda: OnlineEndpointData(
        name="Test",
        location="eastus",
        properties=RestKubernetesOnlineDeployment(
            auth_mode="key",
            traffic={"green": 0, "red": 0},
        ),
    )
    yield poller


@pytest.fixture
def deployment() -> str:
    return "blue"


@pytest.fixture
def request_file() -> str:
    return "./tests/test_configs/endpoints/online/data.json"


@pytest.fixture
def create_yaml_no_type(tmp_path: Path) -> Path:
    content = """
name: myendpoint
compute_type: AMLCompute
auth_mode: AMLTokenAuth
#infrastructure: vc:xyz-slice-of-managed-quota #(proposed experience once vc concept lands)
traffic:
    blue: 0
"""
    p = tmp_path / "create_no_type.yaml"
    p.write_text(content)
    return p


@pytest.fixture
def create_yaml_happy_path(tmp_path: Path, resource_group_name: str) -> Path:
    content = f"""
name: kubernetesendpoint
compute: azureml:/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/sdkv2endpointaks
auth_mode: Key
traffic:
    blue: 0
"""
    p = tmp_path / "create_happy_path.yaml"
    p.write_text(content)
    return p


@pytest.fixture
def create_yaml_without_identity_type(tmp_path: Path) -> Path:
    content = """
location: centraluseuap
name: myendpoint2
auth_mode: Key
"""
    p = tmp_path / "create_yaml_without_identity_type.yaml"
    p.write_text(content)
    return p


@pytest.fixture
def mock_datastore_operations(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock
) -> CodeOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        serviceclient_2022_05_01=mock_aml_services_2022_05_01,
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
def mock_code_assets_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_05_01: Mock,
    mock_datastore_operations: DatastoreOperations,
) -> CodeOperations:
    yield CodeOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operations,
    )


@pytest.fixture
def mock_environment_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_05_01: Mock,
    mock_machinelearning_client: Mock,
) -> EnvironmentOperations:
    yield EnvironmentOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_05_01,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.fixture
def mock_data_operations() -> Mock:
    yield Mock()


@pytest.fixture
def mock_workspace_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_01_01_preview: Mock,
    mock_machinelearning_client: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_01_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.fixture
def mock_local_endpoint_helper() -> Mock:
    yield Mock()


@pytest.fixture
def mock_online_endpoint_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_02_01_preview: Mock,
    mock_aml_services_2020_09_01_dataplanepreview: Mock,
    mock_machinelearning_client: Mock,
    mock_environment_operations: Mock,
    mock_model_operations: Mock,
    mock_code_assets_operations: Mock,
    mock_data_operations: Mock,
    mock_workspace_operations: Mock,
    mock_local_endpoint_helper: Mock,
) -> OnlineEndpointOperations:
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.CODE, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.MODEL, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.ENVIRONMENT, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.DATA, mock_data_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.WORKSPACE, mock_workspace_operations)

    yield OnlineEndpointOperations(
        operation_scope=mock_workspace_scope,
        service_client_02_2022_preview=mock_aml_services_2022_02_01_preview,
        service_client_09_2020_dataplanepreview=mock_aml_services_2020_09_01_dataplanepreview,
        all_operations=mock_machinelearning_client._operation_container,
        local_endpoint_helper=mock_local_endpoint_helper,
    )


@pytest.mark.unittest
class TestOnlineEndpointsOperations:
    def test_online_list(self, mock_online_endpoint_operations: OnlineEndpointOperations) -> None:
        mock_online_endpoint_operations.list()
        mock_online_endpoint_operations._online_operation.list.assert_called_once()

    def test_online_get(
        self,
        mock_online_endpoint_operations: OnlineEndpointOperations,
        randstr: Callable[[], str],
        mock_aml_services_2022_02_01_preview: Mock,
    ) -> None:
        random_name = randstr()
        mock_aml_services_2022_02_01_preview.online_endpoints.get.return_value = OnlineEndpointData(
            name=random_name,
            location="eastus",
            properties=RestOnlineEndpoint(auth_mode="key", traffic=dict()),
        )

        mock_aml_services_2022_02_01_preview.online_deployments.list.return_value = [
            OnlineDeploymentData(
                name=random_name,
                location="eastus",
                properties=OnlineDeploymentDetails(
                    endpoint_compute_type="KUBERNETES",
                ),
            )
        ]

        mock_online_endpoint_operations.get(name=random_name)
        mock_online_endpoint_operations._online_operation.get.assert_called_once()

    def test_online_list_keys(
        self,
        mock_online_endpoint_operations: OnlineEndpointOperations,
        randstr: Callable[[], str],
        mock_aml_services_2022_02_01_preview: Mock,
    ) -> None:
        random_name = randstr()
        mock_aml_services_2022_02_01_preview.online_endpoints.get.return_value = OnlineEndpointData(
            name=random_name,
            location="eastus",
            properties=RestOnlineEndpoint(auth_mode="key"),
        )
        mock_online_endpoint_operations.list_keys(name=random_name)
        mock_online_endpoint_operations._online_operation.get.assert_called_once()
        mock_online_endpoint_operations._online_operation.list_keys.assert_called_once()

    def test_online_list_token(
        self,
        mock_online_endpoint_operations: OnlineEndpointOperations,
        randstr: Callable[[], str],
        mock_aml_services_2022_02_01_preview: Mock,
    ) -> None:
        random_name = randstr()
        mock_aml_services_2022_02_01_preview.online_endpoints.get.return_value = OnlineEndpointData(
            name=random_name,
            location="eastus",
            properties=RestOnlineEndpoint(auth_mode="amltoken"),
        )
        mock_online_endpoint_operations.list_keys(name=random_name)
        mock_online_endpoint_operations._online_operation.get.assert_called_once()
        mock_online_endpoint_operations._online_operation.get_token.assert_called_once()

    def test_online_delete(
        self,
        mock_online_endpoint_operations: OnlineEndpointOperations,
        mock_aml_services_2022_02_01_preview: Mock,
        mocker: MockFixture,
        randstr: Callable[[], str],
        mock_delete_poller: LROPoller,
    ) -> None:
        random_name = randstr()
        mock_aml_services_2022_02_01_preview.online_endpoints.begin_delete.return_value = mock_delete_poller
        mock_online_endpoint_operations.begin_delete(name=random_name)
        mock_online_endpoint_operations._online_operation.begin_delete.assert_called_once()

    def test_online_create(
        self,
        mock_online_endpoint_operations: OnlineEndpointOperations,
        rand_compute_name: Callable[[], str],
        create_yaml_happy_path: str,
        mocker: MockFixture,
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._online_endpoint_operations.OnlineEndpointOperations._get_workspace_location",
            return_value="xxx",
        )
        mock_create_or_update_online_endpoint = mocker.patch.object(
            OnlineEndpointOperations, "begin_create_or_update", autospec=True
        )
        mock_online_endpoint_operations._credentials = Mock(spec_set=DefaultAzureCredential)

        online_endpoint = load_online_endpoint(create_yaml_happy_path)
        online_endpoint.name = rand_compute_name()
        mock_online_endpoint_operations.begin_create_or_update(endpoint=online_endpoint)
        mock_create_or_update_online_endpoint.assert_called_once()
        # mock_online_endpoint_operations.create_or_update.assert_called_once()

    def test_online_create_bad_names(
        self,
        mock_online_endpoint_operations: OnlineEndpointOperations,
        create_yaml_happy_path: str,
        mocker: MockFixture,
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator._get_code_asset_arm_id",
            return_value="xxx",
        )
        mocker.patch(
            "azure.ai.ml.operations._online_endpoint_operations.OnlineEndpointOperations._get_workspace_location",
            return_value="xxx",
        )

        mock_online_endpoint_operations._credentials = Mock(spec_set=DefaultAzureCredential)
        online_endpoint = load_online_endpoint(create_yaml_happy_path)
        # try an endpoint name that is too long
        with pytest.raises(Exception):
            online_endpoint.name = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            mock_online_endpoint_operations.begin_create_or_update(endpoint=online_endpoint)

        # try an endpoint name that is too short
        with pytest.raises(Exception):
            online_endpoint.name = "xx"
            mock_online_endpoint_operations.begin_create_or_update(endpoint=online_endpoint)

        # try a name that has bad characters
        with pytest.raises(Exception):
            online_endpoint.name = "0_this_has%%%%%_bad#char.,.cters"
            mock_online_endpoint_operations.begin_create_or_update(endpoint=online_endpoint)

    def test_online_create_without_oldendpoint(
        self,
        mock_online_endpoint_operations: OnlineEndpointOperations,
        rand_compute_name: Callable[[], str],
        create_yaml_happy_path: str,
        mocker: MockFixture,
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator._get_code_asset_arm_id",
            return_value="xxx",
        )
        mocker.patch(
            "azure.ai.ml.operations._online_endpoint_operations.OnlineEndpointOperations._get_workspace_location",
            return_value="xxx",
        )
        online_endpoint = load_online_endpoint(create_yaml_happy_path)
        online_endpoint.name = rand_compute_name()
        http_err = HttpResponseError()
        http_err.status_code = HttpResponseStatusCode.NOT_FOUND
        mock_online_endpoint_operations._online_operation.get = Mock(side_effect=http_err)
        mock_online_endpoint_operations.begin_create_or_update(endpoint=online_endpoint)

    def test_online_create_without_entity_type(self, create_yaml_without_identity_type: str) -> None:
        online_endpoint = load_online_endpoint(create_yaml_without_identity_type)
        with pytest.raises(Exception):
            mock_online_endpoint_operations.begin_create(endpoint=online_endpoint)

    def test_online_invoke(
        self,
        mock_online_endpoint_operations: OnlineEndpointOperations,
        randstr: Callable[[], str],
        request_file: str,
        mocker: MockFixture,
        mock_aml_services_2022_02_01_preview: Mock,
    ) -> None:
        random_name = randstr()
        mock_aml_services_2022_02_01_preview.online_endpoints.get.return_value = OnlineEndpointData(
            name=random_name,
            location="eastus",
            properties=RestOnlineEndpoint(auth_mode="Key", scoring_uri="xxx"),
        )
        mockresponse = Mock()
        mockresponse.text = '{"key": "value"}'
        mockresponse.status_code = 200
        mocker.patch("requests.post", return_value=mockresponse)
        assert mock_online_endpoint_operations.invoke(endpoint_name=random_name, request_file=request_file)
        mock_online_endpoint_operations._online_operation.get.assert_called_once()
        mock_online_endpoint_operations._online_operation.list_keys.assert_called_once()

    def test_create_no_file_throw_exception(
        self, mock_online_endpoint_operations: OnlineEndpointOperations, randstr: Callable[[], str]
    ) -> None:
        with pytest.raises(Exception):
            mock_online_endpoint_operations.begin_create(name=randstr(), file=None)

    def test_create_no_type_throw_exception(
        self, mock_online_endpoint_operations: OnlineEndpointOperations, randstr: Callable[[], str]
    ) -> None:
        with pytest.raises(Exception):
            mock_online_endpoint_operations.begin_create(name=randstr(), file=None)

    def test_create_no_type_in_file_throw_exception(
        self, mock_online_endpoint_operations: OnlineEndpointOperations, randstr: Callable[[], str], create_yaml_no_type
    ) -> None:
        with pytest.raises(Exception):
            mock_online_endpoint_operations.begin_create(name=randstr(), file=None)

    def test_online_regenerate_keys(
        self,
        mock_online_endpoint_operations: OnlineEndpointOperations,
        randstr: str,
        mock_aml_services_2022_02_01_preview: Mock,
    ) -> None:
        mock_aml_services_2022_02_01_preview.online_endpoints.get.return_value = OnlineEndpointData(
            name=randstr,
            location="eastus",
            properties=RestOnlineEndpoint(auth_mode="Key", scoring_uri="xxx"),
        )
        mock_aml_services_2022_02_01_preview.online_endpoints.list_keys.return_value = EndpointAuthKeys(
            primary_key="primexxx",
            secondary_key="secondxxx",
        )
        mock_online_endpoint_operations.begin_regenerate_keys(name=randstr, key_type="secondary")
        mock_online_endpoint_operations._online_operation.list_keys.assert_called_once()
        mock_online_endpoint_operations._online_operation.begin_regenerate_keys.assert_called_once()
        mock_online_endpoint_operations._online_operation.get.assert_called_once()

    def test_regenerate_invalid_key_type(
        self, mock_online_endpoint_operations: OnlineEndpointOperations, randstr: str
    ) -> None:
        with pytest.raises(Exception):
            mock_online_endpoint_operations.begin_regenerate_keys(name=randstr, key_type="invalid key type")


@pytest.mark.parametrize(
    "traffic,expected_traffic",
    [
        pytest.param({"blue": "100"}, {"blue": "100"}),
        pytest.param({"blue": "90", "green": "10"}, {"blue": "90", "green": "10"}),
        pytest.param({"blue": "100", "green": "0"}, {"blue": "100"}),
        pytest.param({"green": "0"}, {}),
        pytest.param({}, {}),
    ],
)
def test_strip_traffic_from_traffic_map(traffic, expected_traffic) -> None:
    result = _strip_zeroes_from_traffic(traffic)
    for k, v in result.items():
        assert expected_traffic[k] == v
    for k, v in expected_traffic.items():
        assert result[k] == v
