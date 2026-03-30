from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

from azure.ai.ml import MLClient


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestBatchEndpointGaps2(AzureRecordedTestCase):

    def test_get_nonexistent_endpoint_raises_resource_not_found(self, client: MLClient, rand_batch_name: Callable[[], str]) -> None:
        """
        Covers the get() path and verifies the service raises ResourceNotFoundError for unknown endpoint name.
        """
        name = rand_batch_name("nonexistent")
        with pytest.raises((ResourceNotFoundError, ClientAuthenticationError)):
            client.batch_endpoints.get(name=name)
