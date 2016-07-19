# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.graphrbac
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class GraphRbacTest(AzureMgmtTestCase):

    def setUp(self):
        super(GraphRbacTest, self).setUp()
        self.graphrbac_client = self.create_basic_client(
            azure.graphrbac.GraphRbacManagementClient,
            tenant_id=self.settings.AD_DOMAIN
        )

    @record
    def test_graphrbac_users(self):

        user = self.graphrbac_client.users.create(
            azure.graphrbac.models.UserCreateParameters(
                user_principal_name="testbuddy@{}".format(self.settings.AD_DOMAIN),
                account_enabled=False,
                display_name='Test Buddy',
                mail_nickname='testbuddy',
                password_profile=azure.graphrbac.models.PasswordProfile(
                    password='MyStr0ngP4ssword',
                    force_change_password_next_login=True
                )
            )
        )
        self.assertEqual(user.display_name, 'Test Buddy')

        user = self.graphrbac_client.users.get(user.object_id)
        self.assertEqual(user.display_name, 'Test Buddy')

        users = self.graphrbac_client.users.list(
            filter="displayName eq 'Test Buddy'"
        )
        users = list(users)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].display_name, 'Test Buddy')

        self.graphrbac_client.users.delete(user.object_id)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
