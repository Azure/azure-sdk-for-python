# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.authorization
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtAuthorizationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAuthorizationTest, self).setUp()
        self.authorization_client = self.create_mgmt_client(
            azure.mgmt.authorization.AuthorizationManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_authorization(self):
        permissions = self.authorization_client.permissions.list_for_resource_group(
            self.group_name
        )
        
        permissions = list(permissions)
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].actions[0], '*')



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
