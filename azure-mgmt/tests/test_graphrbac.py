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

import azure.graphrbac
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class GraphRbacTest(AzureMgmtTestCase):

    def setUp(self):
        super(GraphRbacTest, self).setUp()
        self.graphrbac_client = self.create_basic_client(
            azure.graphrbac.GraphRbacManagementClientConfiguration,
            azure.graphrbac.GraphRbacManagementClient,
            tenant_id=self.settings.AD_DOMAIN
        )

    @record
    def test_graphrbac_users(self):

        user = self.graphrbac_client.user.create(
            azure.graphrbac.models.UserCreateParameters(
                user_principal_name="testbuddy@{}".format(self.settings.AD_DOMAIN),
                account_enabled=False,
                display_name='Test Buddy',
                mail_nickname='testbuddy',
                password_profile=azure.graphrbac.models.UserCreateParametersPasswordProfile(
                    password='MyStr0ngP4ssword',
                    force_change_password_next_login=True
                )
            )
        )
        self.assertEqual(user.display_name, 'Test Buddy')

        user = self.graphrbac_client.user.get(user.object_id)
        self.assertEqual(user.display_name, 'Test Buddy')

        users = self.graphrbac_client.user.list(
            filter="displayName eq 'Test Buddy'"
        )
        users = list(users)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].display_name, 'Test Buddy')

        self.graphrbac_client.user.delete(user.object_id)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
