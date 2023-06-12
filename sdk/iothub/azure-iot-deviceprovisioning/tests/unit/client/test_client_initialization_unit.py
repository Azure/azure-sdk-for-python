import pytest
from azure.identity import DefaultAzureCredential
from azure.iot.deviceprovisioning import DeviceProvisioningClient
from azure.iot.deviceprovisioning.aio import (
    DeviceProvisioningClient as AsyncDeviceProvisioningClient,
)

endpoint = "fake_endpoint"


class TestProvisioningClientInitialization(object):
    def test_client_init_errors(self):
        # bad endpoint
        with pytest.raises(ValueError):
            DeviceProvisioningClient(["bad_endpoint"], credential=None)
        # bad credential type
        with pytest.raises(TypeError):
            DeviceProvisioningClient(endpoint=endpoint, credential=True)
        # invalid API version
        with pytest.raises(ValueError):
            DeviceProvisioningClient(
                endpoint=endpoint,
                credential=DefaultAzureCredential(),
                api_version="invalid",
            )

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
            DeviceProvisioningClient(
                endpoint=endpoint,
                credential=DefaultAzureCredential(),
                api_version="invalid",
            )
