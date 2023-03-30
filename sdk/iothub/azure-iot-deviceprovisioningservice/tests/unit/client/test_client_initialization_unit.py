import pytest

from azure.iot.deviceprovisioningservice.aio import (
    ProvisioningServiceClient as AsyncProvisioningServiceClient,
)
from azure.iot.deviceprovisioningservice.client import ProvisioningServiceClient

endpoint = "fake_endpoint"


class TestProvisioningClientInitialization(object):
    def test_client_init_errors(self):
        with pytest.raises(ValueError):
            ProvisioningServiceClient(["bad_endpoint"])

        with pytest.raises(TypeError):
            ProvisioningServiceClient(endpoint=endpoint, credential=True)

    @pytest.mark.asyncio
    async def test_client_init_errors_async(self):
        with pytest.raises(ValueError):
            AsyncProvisioningServiceClient(["bad_endpoint"])

        with pytest.raises(TypeError):
            AsyncProvisioningServiceClient(endpoint=endpoint, credential=True)
