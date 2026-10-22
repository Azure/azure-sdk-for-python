# coding=utf-8
import pytest
from azure.mgmt.reservations.aio import ReservationsMgmtClient

from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
)
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.live_test_only
class TestReservationsMgmtOperationOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ReservationsMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_operation_list(self, resource_group):
        response = self.client.operation.list()
        result = [r async for r in response]
        assert len(result)
