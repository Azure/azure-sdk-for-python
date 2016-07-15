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

import azure.mgmt.logic
import azure.mgmt.web
from msrest.version import msrest_version
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtAppsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAppsTest, self).setUp()
        self.logic_client = self.create_mgmt_client(
            azure.mgmt.logic.LogicManagementClient
        )
        self.web_client = self.create_mgmt_client(
            azure.mgmt.web.WebSiteManagementClient
        )

    @record
    def test_webapp(self):
        self.create_resource_group()

        app_service_plan_name = self.get_resource_name('pyarmappserviceplan')
        site_name = self.get_resource_name('pyarmsite')

        server_farm_async_operation = self.web_client.server_farms.create_or_update_server_farm(
            self.group_name,
            app_service_plan_name,
            azure.mgmt.web.models.ServerFarmWithRichSku(
                location=self.region,
                sku=azure.mgmt.web.models.SkuDescription(
                    name='S1',
                    capacity=1,
                    tier='Standard'
                )
            )
        )
        server_farm = server_farm_async_operation.result()

        # Create a Site to be hosted in the Server Farm
        site_async_operation = self.web_client.sites.create_or_update_site(
            self.group_name,
            site_name,
            azure.mgmt.web.models.Site(
                location=self.region,
                server_farm_id=server_farm.id
            )
        )
        site = site_async_operation.result()
        self.assertEquals(site.name, site_name)

        # List Sites by Resource Group
        for site in self.web_client.sites.get_sites(self.group_name).value:
            self.assertIsNotNone(site)

        # Get a single Site
        site = self.web_client.sites.get_site(self.group_name, site_name)
        self.assertIsNotNone(site)

        # Restart a site
        self.web_client.sites.restart_site(self.group_name, site_name)

        # Stop a site
        self.web_client.sites.stop_site(self.group_name, site_name)

        # Start a site
        self.web_client.sites.start_site(self.group_name, site_name)

        # Delete a Site
        self.web_client.sites.delete_site(self.group_name, site_name)


    @record
    def test_logic(self):
        self.create_resource_group()

        # Create App Service Plan
        app_service_plan_name = self.get_resource_name('pyarmappserviceplan')
        app_service_plan = self.web_client.server_farms.create_or_update_server_farm(
            self.group_name,
            app_service_plan_name,
            azure.mgmt.web.models.ServerFarmWithRichSku(
                location='West US',
                sku=azure.mgmt.web.models.SkuDescription(
                    name='F1',
                    tier='Free'
                )
            )
        )
        app_service_plan = app_service_plan.result()

        workflow_name = '12HourHeartBeat'
        self.logic_client.workflows.create_or_update(
            self.group_name,
            workflow_name,
            azure.mgmt.logic.models.Workflow(
                location='West US',
                sku=azure.mgmt.logic.models.Sku(
                    name='Free',
                    plan=azure.mgmt.logic.models.ResourceReference(
                        id=app_service_plan.id
                    )
                ),
                definition={ 
                    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2015-08-01-preview/workflowdefinition.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "triggers": {},
                    "actions": {},
                    "outputs": {}
                }
            )
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
