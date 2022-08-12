import os
import mock
import pytest

from azure.ai.ml._azure_environments import (
    _get_default_cloud_name,
    _set_cloud,
    AzureEnvironments,
    _get_cloud_information_from_metadata,
    _get_base_url_from_metadata,
    _get_azure_portal_id_from_metadata,
    _get_storage_endpoint_from_metadata,
)
from azure.ai.ml.constants import AZUREML_CLOUD_ENV_NAME


@pytest.mark.unittest
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
