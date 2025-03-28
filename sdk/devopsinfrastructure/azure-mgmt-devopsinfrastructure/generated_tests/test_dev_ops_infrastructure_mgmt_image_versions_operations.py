# coding=utf-8
import pytest
from azure.mgmt.devopsinfrastructure import DevOpsInfrastructureMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDevOpsInfrastructureMgmtImageVersionsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(DevOpsInfrastructureMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_image_versions_list_by_image(self, resource_group):
        response = self.client.image_versions.list_by_image(
            resource_group_name=resource_group.name,
            image_name="str",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
