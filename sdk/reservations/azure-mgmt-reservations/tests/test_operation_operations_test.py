# coding=utf-8
import pytest
from azure.mgmt.reservations import ReservationsMgmtClient

from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
    recorded_by_proxy,
)

AZURE_LOCATION = "eastus"


@pytest.mark.live_test_only
class TestReservationsMgmtOperationOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ReservationsMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_operation_list(self, resource_group):
        response = self.client.operation.list()
        result = [r for r in response]
        assert len(result)
