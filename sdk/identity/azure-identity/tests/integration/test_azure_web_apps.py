# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest

from azure.core.rest import HttpRequest, HttpResponse

from utils import get_pipeline_client


@pytest.fixture(scope="module")
def base_url():
    app_name = os.environ.get("IDENTITY_WEBAPP_NAME")
    if not app_name:
        pytest.skip("IDENTITY_WEBAPP_NAME is not set")
    return f"https://{app_name}.azurewebsites.net/"


class TestAzureWebAppsIntegration:
    @pytest.mark.live_test_only
    @pytest.mark.skipif(
        not os.environ.get("IDENTITY_LIVE_RESOURCES_PROVISIONED"), reason="Integration resources not provisioned."
    )
    def test_azure_web_app_integration_sync(self, base_url):
        """Test the Azure Web App endpoint where the sync MI credential is used."""
        client = get_pipeline_client(base_url)
        request = HttpRequest("GET", f"{base_url}sync")
        response: HttpResponse = client.send_request(request)
        assert response.status_code == 200

    @pytest.mark.live_test_only
    @pytest.mark.skipif(
        not os.environ.get("IDENTITY_LIVE_RESOURCES_PROVISIONED"), reason="Integration resources not provisioned."
    )
    def test_azure_web_app_integration_async(self, base_url):
        """Test the Azure Web App endpoint where the async MI credential is used."""
        client = get_pipeline_client(base_url)
        request = HttpRequest("GET", f"{base_url}async")
        response: HttpResponse = client.send_request(request)
        assert response.status_code == 200
