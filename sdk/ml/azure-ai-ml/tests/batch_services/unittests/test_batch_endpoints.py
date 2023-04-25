import json
from pathlib import Path
from typing import Callable
from unittest.mock import Mock, patch

import pytest
from pytest_mock import MockFixture
from requests import Response

from azure.ai.ml import load_batch_endpoint
from azure.ai.ml._restclient.v2022_05_01.models import BatchEndpointData
from azure.ai.ml._restclient.v2022_05_01.models import BatchEndpointDetails as RestBatchEndpoint
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.constants._common import AssetTypes, AzureMLResourceType
from azure.ai.ml.constants._endpoint import EndpointYamlFields
from azure.ai.ml.entities._endpoint.batch_endpoint import BatchEndpoint
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.operations import (
    BatchEndpointOperations,
    DatastoreOperations,
    EnvironmentOperations,
    ModelOperations,
    WorkspaceOperations,
)
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.polling import LROPoller
from azure.identity import DefaultAzureCredential


@pytest.fixture()
def mock_delete_poller() -> LROPoller:
    poller = Mock(spec_set=LROPoller)
    poller.result = lambda timeout: None
    poller.done = lambda: True
    yield poller


@pytest.fixture
def create_yaml_happy_path(tmp_path: Path) -> Path:
    content = """
name: myBatchEndpoint2 # required
description: my sample batch endpoint
auth_mode: aad_token # required
"""
    p = tmp_path / "create_happy_path.yaml"
    p.write_text(content)
    return p


@pytest.fixture
def mock_datastore_operations(
    mock_workspace_scope: OperationScope, mock_operation_config: OperationConfig, mock_aml_services_2022_10_01: Mock
) -> CodeOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        serviceclient_2022_10_01=mock_aml_services_2022_10_01,
    )


@pytest.fixture
def mock_model_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_datastore_operations: DatastoreOperations,
) -> ModelOperations:
    yield ModelOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_05_01,
        datastore_operations=mock_datastore_operations,
    )


@pytest.fixture
def mock_code_assets_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_10_01: Mock,
    mock_datastore_operations: DatastoreOperations,
) -> CodeOperations:
    yield CodeOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_10_01,
        datastore_operations=mock_datastore_operations,
    )


@pytest.fixture
def mock_environment_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_machinelearning_client: Mock,
) -> EnvironmentOperations:
    yield EnvironmentOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_05_01,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.fixture
def mock_data_operations() -> Mock:
    yield Mock()


@pytest.fixture
def mock_workspace_operations(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_10_01: Mock,
    mock_machinelearning_client: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_10_01,
        all_operations=mock_machinelearning_client._operation_container,
    )


@pytest.fixture
def mock_local_endpoint_helper() -> Mock:
    yield Mock()


@pytest.fixture
def mock_batch_endpoint_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_05_01: Mock,
    mock_aml_services_2020_09_01_dataplanepreview: Mock,
    mock_machinelearning_client: Mock,
    mock_environment_operations: Mock,
    mock_model_operations: Mock,
    mock_code_assets_operations: Mock,
    mock_data_operations: Mock,
    mock_workspace_operations: Mock,
) -> BatchEndpointOperations:
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.CODE, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.MODEL, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.ENVIRONMENT, mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.DATA, mock_data_operations)
    mock_machinelearning_client._operation_container.add(AzureMLResourceType.WORKSPACE, mock_workspace_operations)

    kwargs = {"service_client_09_2020_dataplanepreview": mock_aml_services_2020_09_01_dataplanepreview}

    yield BatchEndpointOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client_05_2022=mock_aml_services_2022_05_01,
        all_operations=mock_machinelearning_client._operation_container,
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
        **kwargs,
    )


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestBatchEndpointOperations:
    def test_batch_endpoint_create(
        self,
        mock_batch_endpoint_operations: BatchEndpointOperations,
        create_yaml_happy_path: str,
        mocker: MockFixture,
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._batch_endpoint_operations.BatchEndpointOperations._get_workspace_location",
            return_value="xxx",
        )
        mock_create_or_update_batch_endpoint = mocker.patch.object(
            BatchEndpointOperations, "begin_create_or_update", autospec=True
        )
        mock_batch_endpoint_operations._credentials = Mock(spec_set=DefaultAzureCredential)

        online_endpoint = load_batch_endpoint(create_yaml_happy_path)
        online_endpoint.name = "random_name"
        mock_batch_endpoint_operations.begin_create_or_update(endpoint=online_endpoint)
        mock_create_or_update_batch_endpoint.assert_called_once()
        # mock_batch_endpoint_operations.create_or_update.assert_called_once()

    @pytest.mark.skip(reason="invoke is going to change in the next pr until then it is commented")
    @patch.object(BatchEndpoint, "_from_rest_object")
    def test_batch_invoke(
        self,
        mock_from_rest,
        mock_batch_endpoint_operations: BatchEndpointOperations,
        mocker: MockFixture,
        randint: Callable[[], int],
    ) -> None:
        data_name = "data_name"
        data_version = randint()
        endpoint_name = "myBatchEndpoint"
        deployment_name = "myDeployment"
        mock_batch_endpoint_operations._credentials = Mock(spec_set=DefaultAzureCredential)

        mockresponse = Mock()
        mockresponse.text = '{"key": "value"}'
        mockresponse.status_code = 200
        mocker.patch("requests.post", return_value=mockresponse)
        mock_batch_endpoint_operations.invoke(
            endpoint_name=endpoint_name,
            input=(":".join((data_name, str(data_version)))),
        )
        mock_batch_endpoint_operations._batch_operation.get.assert_called_once()

        # Invoke with output configs
        params_override = [
            {EndpointYamlFields.BATCH_JOB_OUTPUT_PATH: "/tests/"},
            {EndpointYamlFields.BATCH_JOB_OUTPUT_DATSTORE: "azureml:bla"},
        ]

        mock_batch_endpoint_operations.invoke(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            input=(":".join((data_name, str(data_version)))),
            params_override=params_override,
        )
        assert mock_batch_endpoint_operations._batch_operation.get.call_count == 2

    @patch.object(BatchEndpoint, "_from_rest_object")
    @pytest.mark.skip(reason="non-functional test")
    def test_batch_invoke_failed(
        self,
        mock_from_rest,
        mock_batch_endpoint_operations: BatchEndpointOperations,
        mocker: MockFixture,
    ) -> None:
        input_path = "https://foo/bar/train.csv"
        endpoint_name = "myBatchEndpoint"
        deployment_name = "myDeployment"
        mock_batch_endpoint_operations._credentials = Mock(spec_set=DefaultAzureCredential)

        def mock_failed_response(status_code, error_message):
            mock_response = Response()
            mock_response.status_code = status_code
            mock_response.encoding = "utf-8"
            data = {"error": {"code": "UserError", "message": error_message}}
            mock_response._content = json.dumps(data).encode("utf-8")
            return mock_response

        mocker.patch(
            "azure.ai.ml.operations._batch_endpoint_operations.BatchEndpointOperations._validate_deployment_name",
            return_value="xxxxxx",
        )

        response = mock_failed_response(401, "Authorization failed.")
        mocker.patch("requests.post", return_value=response)
        with pytest.raises(ClientAuthenticationError):
            mock_batch_endpoint_operations.invoke(
                endpoint_name=endpoint_name,
                deployment_name=deployment_name,
                input=Input(path=input_path, type=AssetTypes.URI_FILE),
            )

        error_message = "Bad bad request."
        response = mock_failed_response(400, error_message)
        mocker.patch("requests.post", return_value=response)
        with pytest.raises(HttpResponseError, match="{}".format(error_message)):
            mock_batch_endpoint_operations.invoke(
                endpoint_name=endpoint_name,
                deployment_name=deployment_name,
                input=Input(path=input_path, type=AssetTypes.URI_FILE),
            )

    def test_batch_list(self, mock_batch_endpoint_operations: BatchEndpointOperations) -> None:
        mock_batch_endpoint_operations.list()
        mock_batch_endpoint_operations._batch_operation.list.assert_called_once()

    def test_list_endpoint_jobs(
        self, mock_batch_endpoint_operations: BatchEndpointOperations, mocker: MockFixture
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._batch_endpoint_operations._get_mfe_base_url_from_discovery_service",
            return_value="https://some-url.com",
        )
        mockresponse = Mock()
        mockresponse.text = '{"key": "value"}'
        mockresponse.status_code = 200
        mocker.patch("requests.request", return_value=mockresponse)

        mock_batch_endpoint_operations.list_jobs(endpoint_name="ept")
        mock_batch_endpoint_operations._batch_job_endpoint.list.assert_called_once()

    def test_list_deployment_jobs(
        self, mock_batch_endpoint_operations: BatchEndpointOperations, mocker: MockFixture
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._batch_endpoint_operations._get_mfe_base_url_from_discovery_service",
            return_value="https://some-url.com",
        )
        mockresponse = Mock()
        mockresponse.text = '{"key": "value"}'
        mockresponse.status_code = 200
        mocker.patch("requests.request", return_value=mockresponse)

        mock_batch_endpoint_operations.list_jobs(endpoint_name="ept")
        mock_batch_endpoint_operations._batch_job_endpoint.list.assert_called_once()

    def test_batch_get(
        self,
        mock_batch_endpoint_operations: BatchEndpointOperations,
        mock_aml_services_2022_05_01: Mock,
    ) -> None:
        random_name = "random_name"
        mock_aml_services_2022_05_01.batch_endpoints.get.return_value = BatchEndpointData(
            name=random_name,
            location="eastus",
            properties=RestBatchEndpoint(auth_mode="AADToken"),
        )
        mock_batch_endpoint_operations.get(name=random_name)
        mock_batch_endpoint_operations._batch_operation.get.assert_called_once()

    def test_delete_batch_endpoint(
        self,
        mock_batch_endpoint_operations: BatchEndpointOperations,
        mock_aml_services_2022_05_01: Mock,
        mocker: MockFixture,
        mock_delete_poller: LROPoller,
    ) -> None:
        random_name = "random_name"
        mock_aml_services_2022_05_01.batch_endpoints.begin_delete.return_value = mock_delete_poller
        mock_batch_endpoint_operations.begin_delete(name=random_name)
        mock_batch_endpoint_operations._batch_operation.begin_delete.assert_called_once()
