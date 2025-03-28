# coding=utf-8
import pytest
from azure.mgmt.devopsinfrastructure import DevOpsInfrastructureMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDevOpsInfrastructureMgmtResourceDetailsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(DevOpsInfrastructureMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_resource_details_list_by_pool(self, resource_group):
        response = self.client.resource_details.list_by_pool(
            resource_group_name=resource_group.name,
            pool_name="str",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
