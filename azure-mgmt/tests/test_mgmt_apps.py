# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
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
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_webapp(self):
        raise unittest.SkipTest("Skipping WebApp test")

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
        for site in self.web_client.sites.get_sites(self.group_name):
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
        workflow_name = '12HourHeartBeat'
        self.logic_client.workflows.create_or_update(
            self.group_name,
            workflow_name,
            azure.mgmt.logic.models.Workflow(
                location='West US',
                definition={ 
                    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
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
