# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.graphrbac
from devtools_testutils import AzureMgmtTestCase

import pytest

class GraphRbacTest(AzureMgmtTestCase):

    def setUp(self):
        super(GraphRbacTest, self).setUp()
        self.graphrbac_client = self.create_basic_client(
            azure.graphrbac.GraphRbacManagementClient,
            tenant_id=self.settings.AD_DOMAIN
        )

    def _build_object_url(self, object_id):
        return "https://graph.windows.net/{}/directoryObjects/{}".format(
            self.settings.AD_DOMAIN,
            object_id
        )

    def test_signed_in_user(self):

        user = self.graphrbac_client.signed_in_user.get()
        assert user.mail_nickname.startswith("admin")  # Assuming we do the test with adminXXX account

        # Create a group, and check I own it
        group_create_parameters = azure.graphrbac.models.GroupCreateParameters(
            display_name="pytestgroup_display",
            mail_nickname="pytestgroup_nickname"
        )

        group = None
        try:
            group = self.graphrbac_client.groups.create(group_create_parameters)
            self.graphrbac_client.groups.add_owner(
                group.object_id,
                self._build_object_url(user.object_id)
            )

            owned_objects = list(self.graphrbac_client.signed_in_user.list_owned_objects())

            for obj in owned_objects:
                if obj.display_name == "pytestgroup_display":
                    break
            else:
                pytest.fail("Didn't found the group I just created in my owned objects")

        finally:
            if group:
                self.graphrbac_client.groups.delete(group.object_id)

    def test_graphrbac_users(self):

        user = self.graphrbac_client.users.create(
            azure.graphrbac.models.UserCreateParameters(
                user_principal_name="testbuddy#TEST@{}".format(self.settings.AD_DOMAIN),
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

        user = self.graphrbac_client.users.get(user.user_principal_name)
        self.assertEqual(user.display_name, 'Test Buddy')

        users = self.graphrbac_client.users.list(
            filter="displayName eq 'Test Buddy'"
        )
        users = list(users)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].display_name, 'Test Buddy')

        self.graphrbac_client.users.delete(user.object_id)

    def test_groups(self):

        group_create_parameters = azure.graphrbac.models.GroupCreateParameters(
            display_name="pytestgroup_display",
            mail_nickname="pytestgroup_nickname"
        )
        group = self.graphrbac_client.groups.create(group_create_parameters)
        self.assertEqual(group.display_name, "pytestgroup_display")

        group = self.graphrbac_client.groups.get(group.object_id)
        self.assertEqual(group.display_name, "pytestgroup_display")

        groups = self.graphrbac_client.groups.list(
            filter="displayName eq 'pytestgroup_display'"
        )
        groups = list(groups)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].display_name, "pytestgroup_display")

        self.graphrbac_client.groups.delete(group.object_id)

    def test_apps_and_sp(self):
        app = self.graphrbac_client.applications.create({
            'available_to_other_tenants': False,
            'display_name': 'pytest_app',
            'identifier_uris': ['http://pytest_app.org']
        })

        sp = self.graphrbac_client.service_principals.create({
            'app_id': app.app_id, # Do NOT use app.object_id
            'account_enabled': False
        })

        self.graphrbac_client.service_principals.delete(sp.object_id)

        self.graphrbac_client.applications.delete(app.object_id)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
