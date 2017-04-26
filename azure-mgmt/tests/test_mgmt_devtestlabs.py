# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.devtestlabs
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtDevTestLabsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDevTestLabsTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.devtestlabs.DevTestLabsClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_devtestlabs(self):
        lab_name = self.get_resource_name('pylab')

        async_lab = self.client.labs.create_or_update(
            self.group_name,
            lab_name,
            {'location': self.region}
        )
        lab = async_lab.result()
        self.assertEqual(lab.name, lab_name)
            
            



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
