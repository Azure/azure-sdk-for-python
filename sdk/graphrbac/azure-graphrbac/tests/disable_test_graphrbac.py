# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.graphrbac.models
from devtools_testutils import AzureMgmtTestCase

import pytest

# GraphRBAC tests
AD_DOMAIN = "myaddomain.onmicrosoft.com"

class GraphRbacTest(AzureMgmtTestCase):

    def setUp(self):
        super(GraphRbacTest, self).setUp()
        # Set the env variable AZURE_AD_DOMAIN or put AD_DOMAIN in your "mgmt_settings_real" file
        self.ad_domain = self.set_value_to_scrub('AD_DOMAIN', AD_DOMAIN)

        self.graphrbac_client = self.create_basic_client(
            azure.graphrbac.GraphRbacManagementClient,
            tenant_id=self.ad_domain
        )

    def _build_object_url(self, object_id):
        return "https://graph.windows.net/{}/directoryObjects/{}".format(
            self.ad_domain,
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

            try:
                self.graphrbac_client.groups.remove_owner(
                    group.object_id,
                    user.object_id
                )
                pytest.fail("Remove the only owner MUST fail")
            except azure.graphrbac.models.GraphErrorException as err:
                assert "The group must have at least one owner, hence this owner cannot be removed." in err.message

        finally:
            if group:
                self.graphrbac_client.groups.delete(group.object_id)

    def test_deleted_applications(self):

        existing_deleted_applications = list(self.graphrbac_client.deleted_applications.list())

        # Delete the app if already exists
        for app in self.graphrbac_client.applications.list(filter="displayName eq 'pytest_deleted_app'"):
            self.graphrbac_client.applications.delete(app.object_id)

        # Create an app
        app = self.graphrbac_client.applications.create({
            'available_to_other_tenants': False,
            'display_name': 'pytest_deleted_app',
            'identifier_uris': ['http://pytest_deleted_app.org']
        })
        # Delete the app
        self.graphrbac_client.applications.delete(app.object_id)

        # I should see it now in deletedApplications
        existing_deleted_applications = list(self.graphrbac_client.deleted_applications.list(
            filter="displayName eq 'pytest_deleted_app'"
        ))
        # At least one, but if you executed this test a lot, you might see several app deleted with this name
        assert len(existing_deleted_applications) >= 1
        assert all(app.display_name == 'pytest_deleted_app' for app in existing_deleted_applications)

        # Ho my god, most important app ever
        restored_app = self.graphrbac_client.deleted_applications.restore(app.object_id)
        assert restored_app.object_id == app.object_id

        # You know what, no I don't care
        self.graphrbac_client.applications.delete(app.object_id)

        self.graphrbac_client.deleted_applications.hard_delete(app.object_id)

    def test_graphrbac_users(self):

        user = self.graphrbac_client.users.create(
            azure.graphrbac.models.UserCreateParameters(
                user_principal_name="testbuddy#TEST@{}".format(self.ad_domain),
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

        # Delete the app if already exists
        for app in self.graphrbac_client.applications.list(filter="displayName eq 'pytest_app'"):
            self.graphrbac_client.applications.delete(app.object_id)

        app = self.graphrbac_client.applications.create({
            'available_to_other_tenants': False,
            'display_name': 'pytest_app',
            'identifier_uris': ['http://pytest_app.org'],
            'app_roles': [{
                "allowed_member_types": ["User"],
                "description": "Creators can create Surveys",
                "display_name": "SurveyCreator",
                "id": "1b4f816e-5eaf-48b9-8613-7923830595ad",  # Random, but fixed for tests
                "is_enabled": True,
                "value": "SurveyCreator"
            }]
        })

        # Take this opportunity to test get_objects_by_object_ids
        objects = self.graphrbac_client.objects.get_objects_by_object_ids({
            'object_ids': [app.object_id],
            'types': ['Application']
        })
        objects = list(objects)
        assert len(objects) == 1
        assert objects[0].display_name == 'pytest_app'

        apps = list(self.graphrbac_client.applications.list(
            filter="displayName eq 'pytest_app'"
        ))
        assert len(apps) == 1
        assert apps[0].app_roles[0].display_name == "SurveyCreator"

        sp = self.graphrbac_client.service_principals.create({
            'app_id': app.app_id, # Do NOT use app.object_id
            'account_enabled': False
        })

        # Testing getting SP id by app ID
        result = self.graphrbac_client.applications.get_service_principals_id_by_app_id(app.app_id)
        assert result.value == sp.object_id

        self.graphrbac_client.service_principals.update(
            sp.object_id,
            {
                'account_enabled': False
            }
        )

        self.graphrbac_client.service_principals.delete(sp.object_id)

        self.graphrbac_client.applications.delete(app.object_id)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
