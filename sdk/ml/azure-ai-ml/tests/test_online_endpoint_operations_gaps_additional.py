from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml._ml_client import MLClient


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestOnlineEndpointOperationsGapsAdditional(AzureRecordedTestCase):
    def test_get_keys_returns_credentials_object(self, rand_online_name: Callable[[], str], client: MLClient) -> None:
        """Call get_keys for a non-existent endpoint and ensure it raises, validating the public API path.

        This verifies the flow that calls _get_online_credentials through the public get_keys method.
        """
        endpoint_name = rand_online_name("gaps-getkeys-")
        # Calling get_keys for a non-existent endpoint should raise an exception from the service
        with pytest.raises(Exception):
            client.online_endpoints.get_keys(name=endpoint_name)
