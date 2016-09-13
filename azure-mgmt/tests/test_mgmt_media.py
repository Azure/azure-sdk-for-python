# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
raise unittest.SkipTest("Skipping all tests")

import azure.mgmt.media
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtMediaTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMediaTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.media.MediaServicesManagementClient
        )

    @record
    def test_media(self):
        self.create_resource_group()
        media_name = self.get_resource_name('pymedia')

        available = self.client.media_service.check_name_availabilty(
            name=media_name,
            type='mediaservices'
        )
        self.assertTrue(available.name_available)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
