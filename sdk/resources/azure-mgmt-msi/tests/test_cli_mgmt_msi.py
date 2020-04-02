# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 8
# Methods Covered : 8
# Examples Total  : 8
# Examples Tested : 8
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.msi
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtManagedServiceIdentityClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtManagedServiceIdentityClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.msi.ManagedServiceIdentityClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_msi(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        USER_ASSIGNED_IDENTITY_NAME = "useridentityname"
        IDENTITY_NAME = "identityname"

        # IdentityCreate[put]
        # BODY = {
        #   "location": "eastus",
        #   "tags": {
        #     "key1": "value1",
        #     "key2": "value2"
        #   }
        # }
        LOCATION = "eastus"
        TAGS = {
          "key1": "value1",
          "key2": "value2"
        }
        result = self.mgmt_client.user_assigned_identities.create_or_update(resource_group.name, USER_ASSIGNED_IDENTITY_NAME, LOCATION, TAGS)

        # IdentityGet[get]
        result = self.mgmt_client.user_assigned_identities.get(resource_group.name, USER_ASSIGNED_IDENTITY_NAME)

        # IdentityListByResourceGroup[get]
        result = self.mgmt_client.user_assigned_identities.list_by_resource_group(resource_group.name)

        # IdentityListBySubscription[get]
        result = self.mgmt_client.user_assigned_identities.list_by_subscription()

        """ TODO: dont have system_assigned_identities module
        # MsiOperationsList[get]
        result = self.mgmt_client.system_assigned_identities.get_by_scope(IDENTITY_NAME)

        # MsiOperationsList[get]
        result = self.mgmt_client.system_assigned_identities.get_by_scope(IDENTITY_NAME)
        """

        # IdentityUpdate[patch]
        # BODY = {
        #   "location": "eastus",
        #   "tags": {
        #     "key1": "value1",
        #     "key2": "value2"
        #   }
        # }
        LOCATION = "eastus"
        TAGS = {
          "key1": "value1",
          "key2": "value2"
        }
        result = self.mgmt_client.user_assigned_identities.update(resource_group.name, USER_ASSIGNED_IDENTITY_NAME, LOCATION, TAGS)

        # IdentityDelete[delete]
        result = self.mgmt_client.user_assigned_identities.delete(resource_group.name, USER_ASSIGNED_IDENTITY_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
