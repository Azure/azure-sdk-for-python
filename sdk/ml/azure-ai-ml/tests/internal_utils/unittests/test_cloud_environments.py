import os
import mock
import pytest
from mock import MagicMock, patch

from azure.ai.ml._azure_environments import (
    AzureEnvironments,
    EndpointURLS,
    _get_azure_portal_id_from_metadata,
    _get_base_url_from_metadata,
    _get_cloud_details,
    _get_cloud_information_from_metadata,
    _get_default_cloud_name,
    _get_registry_discovery_endpoint_from_metadata,
    _get_storage_endpoint_from_metadata,
    _set_cloud,
)
from azure.ai.ml.constants._common import ArmConstants, AZUREML_CLOUD_ENV_NAME
from azure.mgmt.core import ARMPipelineClient


def mocked_send_request_get(*args, **kwargs):
    class MockResponse:
        def __init__(self):
            self.status_code = 201

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return

        def json(self):
            return [
                {
                    "name": "TEST_ENV",
                    "portal": "testportal.azure.com",
                    "resourceManager": "testresourcemanager.azure.com",
                    "authentication": {"loginEndpoint": "testdirectoryendpoint.azure.com"},
                    "suffixes": {"storage": "teststorageendpoint"},
                },
                {
                    "name": "TEST_ENV2",
                    "portal": "testportal.azure.windows.net",
                    "resourceManager": "testresourcemanager.azure.com",
                    "authentication": {"loginEndpoint": "testdirectoryendpoint.azure.com"},
                    "suffixes": {"storage": "teststorageendpoint"},
                },
                {"name": "MISCONFIGURED"},
            ]

    return MockResponse()


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestCloudEnvironments:
    @mock.patch.dict(os.environ, {AZUREML_CLOUD_ENV_NAME: AzureEnvironments.ENV_DEFAULT}, clear=True)
    def test_set_valid_cloud_details_china(self):
        cloud_environment = AzureEnvironments.ENV_CHINA
        _set_cloud(cloud_environment)
        cloud_details = _get_cloud_information_from_metadata(cloud_environment)
        assert cloud_details.get("cloud") == cloud_environment
        assert "default" in str(cloud_details.get("credential_scopes"))
        assert "https://management.chinacloudapi.cn" in str(cloud_details.get("credential_scopes"))

    def test_set_valid_cloud_details_us_gov(self):
        cloud_environment = AzureEnvironments.ENV_US_GOVERNMENT
        _set_cloud(cloud_environment)
        cloud_details = _get_cloud_information_from_metadata(cloud_environment)
        assert cloud_details.get("cloud") == cloud_environment
        assert "default" in str(cloud_details.get("credential_scopes"))
        assert "https://management.usgovcloudapi.net" in str(cloud_details.get("credential_scopes"))

    @mock.patch.dict(os.environ, {AZUREML_CLOUD_ENV_NAME: AzureEnvironments.ENV_DEFAULT}, clear=True)
    def test_get_base_url_from_default_environment(self):
        cloud_environment = None
        _set_cloud(cloud_environment)
        base_url = _get_base_url_from_metadata(cloud_environment)
        assert "https://management.azure.com" in base_url

    def test_get_base_url_from_us_gov(self):
        cloud_environment = AzureEnvironments.ENV_US_GOVERNMENT
        _set_cloud(cloud_environment)
        base_url = _get_base_url_from_metadata(cloud_environment)
        assert "https://management.usgovcloudapi.net" in base_url

    def test_get_azure_portal_id_from_us_gov(self):
        cloud_environment = AzureEnvironments.ENV_US_GOVERNMENT
        _set_cloud(cloud_environment)
        base_url = _get_azure_portal_id_from_metadata(cloud_environment)
        assert "https://portal.azure.us" in base_url

    def test_get_storage_endpoint_from_us_gov(self):
        cloud_environment = AzureEnvironments.ENV_US_GOVERNMENT
        _set_cloud(cloud_environment)
        base_url = _get_storage_endpoint_from_metadata(cloud_environment)
        assert "core.usgovcloudapi.net" in base_url

    def test_set_invalid_cloud(self):
        with pytest.raises(Exception) as e:
            _set_cloud("yadadada")
        assert "Unknown cloud environment supplied" in str(e)

    def test_get_default_cloud(self):
        with mock.patch("os.environ", {AZUREML_CLOUD_ENV_NAME: "yadadada"}):
            cloud_name = _get_default_cloud_name()
            assert cloud_name == "yadadada"

    def test_get_registry_endpoint_from_public(self):
        cloud_environment = AzureEnvironments.ENV_DEFAULT
        _set_cloud(cloud_environment)
        base_url = _get_registry_discovery_endpoint_from_metadata(cloud_environment)
        assert "https://eastus.api.azureml.ms/" in base_url

    def test_get_registry_endpoint_from_china(self):
        cloud_environment = AzureEnvironments.ENV_CHINA
        _set_cloud(cloud_environment)
        base_url = _get_registry_discovery_endpoint_from_metadata(cloud_environment)
        assert "https://chinaeast2.api.ml.azure.cn/" in base_url

    def test_get_registry_endpoint_from_us_gov(self):
        cloud_environment = AzureEnvironments.ENV_US_GOVERNMENT
        _set_cloud(cloud_environment)
        base_url = _get_registry_discovery_endpoint_from_metadata(cloud_environment)
        assert "https://usgovarizona.api.ml.azure.us/" in base_url

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch("azure.mgmt.core.ARMPipelineClient.send_request", side_effect=mocked_send_request_get)
    def test_get_cloud_from_arm(self, mock_arm_pipeline_client_send_request):
        _set_cloud("TEST_ENV")
        cloud_details = _get_cloud_information_from_metadata("TEST_ENV")
        assert cloud_details.get("cloud") == "TEST_ENV"

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch("azure.mgmt.core.ARMPipelineClient.send_request", side_effect=mocked_send_request_get)
    def test_all_endpointurls_used(self, mock_get):
        cloud_details = _get_cloud_details("TEST_ENV")
        endpoint_urls = [a for a in dir(EndpointURLS) if not a.startswith("__")]
        for url in endpoint_urls:
            try:
                cloud_details[EndpointURLS.__dict__[url]]
            except:
                assert False, "Url not found: {}".format(EndpointURLS.__dict__[url])
        assert True

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch("azure.mgmt.core.ARMPipelineClient.send_request", side_effect=mocked_send_request_get)
    def test_metadata_registry_endpoint(self, mock_get):
        cloud_details = _get_cloud_details("TEST_ENV2")
        assert (
            cloud_details.get(EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT)
            == "https://test_env2west.api.azureml.windows.net/"
        )

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch("azure.mgmt.core.ARMPipelineClient.send_request", side_effect=mocked_send_request_get)
    def test_arm_misconfigured(self, mock_get):
        with pytest.raises(Exception) as e_info:
            _set_cloud("MISCONFIGURED")
