# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.web
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtAppsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAppsTest, self).setUp()
        self.web_client = self.create_mgmt_client(
            azure.mgmt.web.WebSiteManagementClient
        )

    @ResourceGroupPreparer()
    def test_webapp(self, resource_group, location):
        raise unittest.SkipTest("Skipping WebApp test")

        app_service_plan_name = self.get_resource_name('pyarmappserviceplan')
        site_name = self.get_resource_name('pyarmsite')

        server_farm_async_operation = self.web_client.server_farms.create_or_update_server_farm(
            resource_group.name,
            app_service_plan_name,
            azure.mgmt.web.models.ServerFarmWithRichSku(
                location=location,
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
        self.assertEqual(site.name, site_name)

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

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
