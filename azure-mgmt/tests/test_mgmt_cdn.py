# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.cdn
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtCdnTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCdnTest, self).setUp()
        self.cdn_client = self.create_mgmt_client(
            azure.mgmt.cdn.CdnManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_cdn(self):
        account_name = self.get_resource_name('pyarmcdn')

        output = self.cdn_client.check_name_availability(
            name=account_name
        )
        self.assertTrue(output.name_available)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
