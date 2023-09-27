import pytest
from azure.identity.aio import DefaultAzureCredential
from azure.iot.deviceprovisioning.aio import (
    DeviceProvisioningClient as AsyncDeviceProvisioningClient,
)

endpoint = "fake_endpoint"


class TestProvisioningClientInitialization(object):
    @pytest.mark.asyncio
    async def test_client_init_errors_async(self):
        # bad endpoint
        with pytest.raises(ValueError):
            AsyncDeviceProvisioningClient(["bad_endpoint"], credential=None)
        # bad credential type
        with pytest.raises(TypeError):
            AsyncDeviceProvisioningClient(endpoint=endpoint, credential=True)
        # invalid API version
        with pytest.raises(ValueError):
            AsyncDeviceProvisioningClient(
                endpoint=endpoint,
                credential=DefaultAzureCredential(),
                api_version="invalid",
            )
