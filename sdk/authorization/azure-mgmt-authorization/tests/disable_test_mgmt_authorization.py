# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.authorization
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtAuthorizationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAuthorizationTest, self).setUp()
        self.authorization_client = self.create_mgmt_client(
            azure.mgmt.authorization.AuthorizationManagementClient
        )

    @ResourceGroupPreparer()
    def test_authorization(self, resource_group, location):
        permissions = self.authorization_client.permissions.list_for_resource_group(
            resource_group.name
        )

        permissions = list(permissions)
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].actions[0], '*')

    @ResourceGroupPreparer()
    def test_role_definitions(self, resource_group, location):
        # Get "Contributor" built-in role as a RoleDefinition object
        role_name = 'Contributor'
        roles = list(self.authorization_client.role_definitions.list(
            resource_group.id,
            filter="roleName eq '{}'".format(role_name)
        ))
        assert len(roles) == 1

    @ResourceGroupPreparer()
    def test_role_assignment(self, resource_group, location):
        contributor_id = "b24988ac-6180-42a0-ab88-20f7382dd24c"  # Reserved UUID for contributor on Azure

        contributor_full_id = "/subscriptions/{}/providers/Microsoft.Authorization/roleDefinitions/{}".format(
            self.settings.SUBSCRIPTION_ID,
            contributor_id
        )

        role_name = "ddfe2dc0-9858-442f-aca3-ac215947a815"  # Consistent for testing, but not significant

        role_assignment = self.authorization_client.role_assignments.create(
            resource_group.id,
            role_name,
            {
                'role_definition_id': contributor_full_id,
                'principal_id': '6d33bfc8-e476-11e8-915d-f2801f1b9fd1'  # Should be service principal object ID
            }
        )

        self.authorization_client.role_assignments.delete(
            resource_group.id,
            role_assignment.name,
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
