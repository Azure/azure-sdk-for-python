# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.trafficmanager
from datetime import date, timedelta
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtTrafficManagerTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtTrafficManagerTest, self).setUp()
        self.commerce_client = self.create_mgmt_client(
            azure.mgmt.trafficmanager.TrafficManagerManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_trafficmanager(self):
        # FIXME, write tests
        pass


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
