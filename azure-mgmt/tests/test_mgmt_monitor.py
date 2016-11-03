# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.monitor
import azure.monitor
from msrest.version import msrest_version
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtMonitorTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMonitorTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.monitor.InsightsManagementClient
        )
        self.data_client = self.create_mgmt_client(
            azure.monitor.InsightsClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_basic(self):
        account_name = self.get_resource_name('pymonitor')

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
