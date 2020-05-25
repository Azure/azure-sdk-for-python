# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 18
# Methods Covered : 18
# Examples Total  : 18
# Examples Tested : 16
# Coverage %      : 89
# ----------------------

import unittest

import azure.mgmt.mixedreality
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtMixedRealityClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMixedRealityClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.mixedreality.MixedRealityClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_mixedreality(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myAccount"

        # /SpatialAnchorsAccounts/put/Create spatial anchor account[put]
        result = self.mgmt_client.spatial_anchors_accounts.create(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, location=AZURE_LOCATION)

        # /RemoteRenderingAccounts/put/Create remote rendering account[put]
        BODY = {
          "identity": {
            "type": "SystemAssigned"
          },
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.remote_rendering_accounts.create(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, remote_rendering_account=BODY)

        # /RemoteRenderingAccounts/get/Get remote rendering account[get]
        result = self.mgmt_client.remote_rendering_accounts.get(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

        # /SpatialAnchorsAccounts/get/Get spatial anchors account[get]
        result = self.mgmt_client.spatial_anchors_accounts.get(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

        # /RemoteRenderingAccounts/get/List remote rendering accounts by resource group[get]
        result = self.mgmt_client.remote_rendering_accounts.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /SpatialAnchorsAccounts/get/List spatial anchor accounts by resource group[get]
        result = self.mgmt_client.spatial_anchors_accounts.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /RemoteRenderingAccounts/get/List remote rendering accounts by subscription[get]
        result = self.mgmt_client.remote_rendering_accounts.list_by_subscription()

        # /SpatialAnchorsAccounts/get/List spatial anchors accounts by subscription[get]
        result = self.mgmt_client.spatial_anchors_accounts.list_by_subscription()

        # /Operations/get/List available operations[get]
        result = self.mgmt_client.operations.list()

        # /RemoteRenderingAccounts/post/Regenerate remote rendering account keys[post]
        result = self.mgmt_client.remote_rendering_accounts.regenerate_keys(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, serial="1")

        # /SpatialAnchorsAccounts/post/Regenerate spatial anchors account keys[post]
        result = self.mgmt_client.spatial_anchors_accounts.regenerate_keys(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, serial="1")

        # /RemoteRenderingAccounts/patch/Update remote rendering account[patch]
        BODY = {
          "identity": {
            "type": "SystemAssigned"
          },
          "location": AZURE_LOCATION,
          "tags": {
            "heroine": "juliet",
            "hero": "romeo"
          }
        }
        result = self.mgmt_client.remote_rendering_accounts.update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, remote_rendering_account=BODY)

        # /SpatialAnchorsAccounts/patch/Update spatial anchors account[patch]
        TAGS = {
          "heroine": "juliet",
          "hero": "romeo"
        }
        result = self.mgmt_client.spatial_anchors_accounts.update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, location=AZURE_LOCATION, tags=TAGS)

        # //post/CheckLocalNameAvailability[post]
        result = self.mgmt_client.check_name_availability_local(location=AZURE_LOCATION, name="MyAccount", type="Microsoft.MixedReality/spatialAnchorsAccounts")

        # /RemoteRenderingAccounts/delete/Delete remote rendering account[delete]
        result = self.mgmt_client.remote_rendering_accounts.delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

        # /SpatialAnchorsAccounts/delete/Delete spatial anchors account[delete]
        result = self.mgmt_client.spatial_anchors_accounts.delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
