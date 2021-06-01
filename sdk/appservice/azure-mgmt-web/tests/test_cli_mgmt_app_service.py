# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   AppServicePlans: 6/27

import unittest

import azure.mgmt.web
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtWebSiteTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtWebSiteTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.web.WebSiteManagementClient
        )

    @unittest.skip('skip temporarily')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_app_service_plan(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        NAME = "myname"

#--------------------------------------------------------------------------
        # /AppServicePlans/put/Create Or Update App Service plan[put]
#--------------------------------------------------------------------------
        BODY = {
          "kind": "app",
          "location": AZURE_LOCATION,
          "sku": {
            "name": "P1",
            "tier": "Premium",
            "size": "P1",
            "family": "P",
            "capacity": "1"
          }
        }
        result = self.mgmt_client.app_service_plans.begin_create_or_update(resource_group_name=RESOURCE_GROUP, name=NAME, app_service_plan=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /AppServicePlans/get/Get App Service plan[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_plans.get(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /AppServicePlans/get/List App Service plans by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_plans.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /AppServicePlans/get/List App Service plans[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_plans.list()

#--------------------------------------------------------------------------
        # /AppServicePlans/patch/Patch Service plan[patch]
#--------------------------------------------------------------------------
        BODY = {
          "kind": "app"
        }
        result = self.mgmt_client.app_service_plans.update(resource_group_name=RESOURCE_GROUP, name=NAME, app_service_plan=BODY)

#--------------------------------------------------------------------------
        # /AppServicePlans/delete/Delete App Service plan[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_plans.delete(resource_group_name=RESOURCE_GROUP, name=NAME)
