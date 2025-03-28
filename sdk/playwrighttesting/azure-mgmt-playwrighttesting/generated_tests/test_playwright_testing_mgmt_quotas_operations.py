# coding=utf-8
import pytest
from azure.mgmt.playwrighttesting import PlaywrightTestingMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestPlaywrightTestingMgmtQuotasOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(PlaywrightTestingMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_quotas_get(self, resource_group):
        response = self.client.quotas.get(
            location="str",
            quota_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_quotas_list_by_subscription(self, resource_group):
        response = self.client.quotas.list_by_subscription(
            location="str",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
