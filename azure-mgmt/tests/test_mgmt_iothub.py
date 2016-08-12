# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.iothub
from datetime import date, timedelta
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtIoTHubTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtIoTHubTest, self).setUp()
        self.iothub_client = self.create_mgmt_client(
            azure.mgmt.iothub.IotHubClient
        )

    @record
    def test_iothub(self):
        # FIXME, write tests
        pass


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
