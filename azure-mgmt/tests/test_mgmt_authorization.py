# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.authorization
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtAuthorizationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAuthorizationTest, self).setUp()
        self.authorization_client = self.create_mgmt_client(
            azure.mgmt.authorization.AuthorizationManagementClientConfiguration,
            azure.mgmt.authorization.AuthorizationManagementClient
        )

    @record
    def test_authorization(self):
        self.create_resource_group()

        permissions = self.authorization_client.permissions.list_for_resource_group(
            self.group_name
        )
        
        permissions = list(permissions)
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].actions[0], '*')



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
