# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import pytest

import azure.mgmt.monitor
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
from azure.core.exceptions import HttpResponseError

AZURE_LOCATION = 'eastus'

class TestMgmtMonitor(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.monitor.MonitorManagementClient
        )
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_monitor_skip_url(self, resource_group):
        resource_uri = "/subscriptions/1234abcd-1234-abcd-5678-1234abcd5678/resourceGroups/my-test-rg/providers/Microsoft.Sql/servers/mytestserver/databases/{Object.value}"

        with pytest.raises(HttpResponseError):
            self.mgmt_client.metrics.list(resource_uri=resource_uri)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
