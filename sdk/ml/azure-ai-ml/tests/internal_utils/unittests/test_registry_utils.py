import json
import pytest
from azure.core.exceptions import HttpResponseError
from azure.ai.ml._utils._registry_utils import _get_registry_discovery_uri
from pytest_mock import MockFixture
from azure.ai.ml._restclient.registry_discovery import AzureMachineLearningWorkspaces as ServiceClientRegistryDiscovery


@pytest.mark.unittest
def test_construct_mfe_uri_success(
    mocker: MockFixture, mock_registry_discovery_client: ServiceClientRegistryDiscovery
) -> None:
    mock_response = json.dumps(
        {
            "registryName": "testFeed",
            "primaryRegionResourceProviderUri": "https://cert-master.experiments.azureml-test.net/",
        }
    )
    mocker.patch(
        "azure.ai.ml._restclient.registry_discovery.operations._registry_management_non_workspace_operations.RegistryManagementNonWorkspaceOperations.registry_management_non_workspace",
        return_val=mock_response,
    )
    uri = _get_registry_discovery_uri(mock_registry_discovery_client, "testFeed")
    assert (uri, "https://cert-master.experiments.azureml-test.net/") is not None


@pytest.mark.unittest
def test_construct_mfe_uri_error(
    mocker: MockFixture, mock_registry_discovery_client: ServiceClientRegistryDiscovery
) -> None:
    mock_error = HttpResponseError(response=mocker.patch("azure.core.pipeline.HTTPResponseType"))
    mocker.patch(
        "azure.ai.ml._restclient.registry_discovery.operations._registry_management_non_workspace_operations.RegistryManagementNonWorkspaceOperations.registry_management_non_workspace",
        side_effect=mock_error,
    )
    with pytest.raises(HttpResponseError):
        _get_registry_discovery_uri(mock_registry_discovery_client, "testFeed")
