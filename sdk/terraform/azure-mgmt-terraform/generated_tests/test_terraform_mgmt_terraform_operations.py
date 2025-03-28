# coding=utf-8
import pytest
from azure.mgmt.terraform import TerraformMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestTerraformMgmtTerraformOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(TerraformMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_terraform_begin_export_terraform(self, resource_group):
        response = self.client.terraform.begin_export_terraform(
            body={
                "query": "str",
                "type": "ExportQuery",
                "authorizationScopeFilter": "str",
                "fullProperties": bool,
                "maskSensitive": bool,
                "namePattern": "str",
                "recursive": bool,
                "table": "str",
                "targetProvider": "str",
            },
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...
