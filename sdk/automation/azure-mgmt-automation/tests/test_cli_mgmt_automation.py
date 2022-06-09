# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 147
# Methods Covered : 146
# Examples Total  : 167
# Examples Tested : 166
# Coverage %      : 98.72499898162857
# ----------------------

# current coverage: 85

import time
import unittest

import azure.mgmt.automation
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtAutomationClient(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.automation.AutomationClient
        )

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_automation(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        AUTOMATION_ACCOUNT_NAME = 'myAutomationAccount9'

        # Create or update automation account[put]
        BODY = {
          "sku": {
            "name": "Free"
          },
          "name": AUTOMATION_ACCOUNT_NAME,
          "location": "East US 2"
        }
        self.mgmt_client.automation_account.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, BODY)

        # List software update configuration machine runs for a specific software update configuration run[get]
        self.mgmt_client.software_update_configuration_machine_runs.list(resource_group.name, AUTOMATION_ACCOUNT_NAME)


if __name__ == '__main__':
    unittest.main()
