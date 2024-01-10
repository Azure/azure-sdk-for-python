# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from azure.mgmt.sphere import AzureSphereMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtSphere(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            AzureSphereMgmtClient
        )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_catalogs(self, resource_group):
        catalog_name = "CatalogName"
        catalog = self.mgmt_client.catalogs.begin_create_or_update(
            resource_group_name=resource_group.name,
            catalog_name=catalog_name,
            resource={"location": "global"}).result().as_dict()
        assert catalog["name"] == catalog_name

        catalog = self.mgmt_client.catalogs.get(
            resource_group_name=resource_group.name,
            catalog_name=catalog_name,
        ).as_dict()
        assert catalog["name"] == catalog_name

        catalogs = list(self.mgmt_client.catalogs.list_by_resource_group(
            resource_group_name=resource_group.name,
        ))
        assert len(catalogs) == 1

        self.mgmt_client.catalogs.begin_delete(
            resource_group_name=resource_group.name,
            catalog_name=catalog_name,
        ).result()

        catalogs = list(self.mgmt_client.catalogs.list_by_resource_group(
            resource_group_name=resource_group.name,
        ))
        assert len(catalogs) == 0
