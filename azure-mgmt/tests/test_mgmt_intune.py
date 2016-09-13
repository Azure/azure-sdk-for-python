# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
raise unittest.SkipTest("Skipping all tests")

import azure.mgmt.intune
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtIntuneTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtIntuneTest, self).setUp()
        self.client = self.create_basic_client(
            azure.mgmt.intune.IntuneResourceManagementClient,
            tenant_id=self.settings.AD_DOMAIN
        )

    @record
    def test_intune(self):
        pass



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
