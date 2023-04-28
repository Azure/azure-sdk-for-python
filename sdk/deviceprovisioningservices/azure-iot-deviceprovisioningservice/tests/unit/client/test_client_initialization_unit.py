import pytest
from azure.identity import DefaultAzureCredential
from azure.iot.deviceprovisioningservice import ProvisioningServiceClient
from azure.iot.deviceprovisioningservice.aio import (
    ProvisioningServiceClient as AsyncProvisioningServiceClient,
)

endpoint = "fake_endpoint"


class TestProvisioningClientInitialization(object):
    def test_client_init_errors(self):
        # bad endpoint
        with pytest.raises(ValueError):
            ProvisioningServiceClient(["bad_endpoint"], credential=None)
        # bad credential type
        with pytest.raises(TypeError):
            ProvisioningServiceClient(endpoint=endpoint, credential=True)
        # invalid API version
        with pytest.raises(ValueError):
            ProvisioningServiceClient(
                endpoint=endpoint,
                credential=DefaultAzureCredential(),
                api_version="invalid",
            )

    @pytest.mark.asyncio
    async def test_client_init_errors_async(self):
        # bad endpoint
        with pytest.raises(ValueError):
            AsyncProvisioningServiceClient(["bad_endpoint"], credential=None)
        # bad credential type
        with pytest.raises(TypeError):
            AsyncProvisioningServiceClient(endpoint=endpoint, credential=True)
        # invalid API version
        with pytest.raises(ValueError):
            ProvisioningServiceClient(
                endpoint=endpoint,
                credential=DefaultAzureCredential(),
                api_version="invalid",
            )
