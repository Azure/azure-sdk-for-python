import pytest

from azure.iot.provisioningservice.aio import (
    ProvisioningServiceClient as AsyncProvisioningServiceClient,
)
from azure.iot.provisioningservice.client import ProvisioningServiceClient

endpoint = "fake_endpoint"


class TestProvisioningClientInitialization(object):
    def test_client_init_errors(self):
        with pytest.raises(ValueError):
            ProvisioningServiceClient(["bad_endpoint"])

        with pytest.raises(TypeError):
            ProvisioningServiceClient(endpoint=endpoint, credential=True)

    async def test_client_init_errors_async(self):
        with pytest.raises(ValueError):
            AsyncProvisioningServiceClient(["bad_endpoint"])

        with pytest.raises(TypeError):
            AsyncProvisioningServiceClient(endpoint=endpoint, credential=True)
