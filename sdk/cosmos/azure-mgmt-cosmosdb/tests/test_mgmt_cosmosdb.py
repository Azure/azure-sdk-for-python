# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.cosmosdb
from msrestazure.azure_exceptions import CloudError
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtCosmosDBTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCosmosDBTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.cosmosdb.CosmosDBManagementClient
        )

    @ResourceGroupPreparer()
    def test_accounts_create(self, resource_group, location):
        account_name = self.get_resource_name('pycosmosdbx1')

        self.assertFalse(self.client.database_accounts.check_name_exists(account_name))

        async_cosmosdb_create = self.client.database_accounts.create_or_update(
            resource_group.name,
            account_name,
            {
                'location': location,
                'properties': {
                    'locations': [{
                        'location_name': self.region
                    }],
                    "createMode": "Default"
                }
                
            }
        )
        account = async_cosmosdb_create.result()
        self.assertIsNotNone(account)
        # Rest API issue
        # self.assertEqual(account.name, account_name)

    @ResourceGroupPreparer()
    def test_accounts_features(self, resource_group, location):
        account_name = self.get_resource_name('pycosmosdbx2')

        if not self.is_playback():
            async_cosmosdb_create = self.client.database_accounts.create_or_update(
                resource_group.name,
                account_name,
                {
                    'location': location,
                    'properties': {
                        'locations': [{
                            'location_name': self.region
                        }],
                        "createMode": "Default"
                    }
                }
            )
            async_cosmosdb_create.wait()

        account = self.client.database_accounts.get(
            resource_group.name,
            account_name
        )
        self.assertEqual(account.name, account_name)

        my_accounts = list(self.client.database_accounts.list_by_resource_group(resource_group.name))
        self.assertEqual(len(my_accounts), 1)
        self.assertEqual(my_accounts[0].name, account_name)

        my_accounts = list(self.client.database_accounts.list())
        self.assertTrue(len(my_accounts) >= 1)
        self.assertTrue(any(db.name == account_name for db in my_accounts))

        async_change = self.client.database_accounts.failover_priority_change(
            resource_group.name,
            account_name,
            [{
                'location_name': self.region,
                'failover_priority': 0
            }]
        )
        async_change.wait()

        my_keys = self.client.database_accounts.list_keys(
            resource_group.name,
            account_name
        )
        self.assertIsNotNone(my_keys.primary_master_key)
        self.assertIsNotNone(my_keys.secondary_master_key)
        self.assertIsNotNone(my_keys.primary_readonly_master_key)
        self.assertIsNotNone(my_keys.secondary_readonly_master_key)


        my_keys = self.client.database_accounts.list_read_only_keys(
            resource_group.name,
            account_name
        )
        self.assertIsNotNone(my_keys.primary_readonly_master_key)
        self.assertIsNotNone(my_keys.secondary_readonly_master_key)


        async_regenerate = self.client.database_accounts.regenerate_key(
            resource_group.name,
            account_name,
            "primary"
        )
        async_regenerate.wait()

    @ResourceGroupPreparer()
    def test_accounts_delete(self, resource_group, location):
        account_name = self.get_resource_name('pydocumentdbx3')

        if not self.is_playback():
            async_cosmosdb_create = self.client.database_accounts.create_or_update(
                resource_group.name,
                account_name,
                {
                    'location': location,
                    'properties': {
                        'locations': [{
                            'location_name': self.region
                        }],
                        "createMode": "Default"
                    }
                }
            )
            async_cosmosdb_create.wait()

        # Current implementation of msrestazure does not support 404 as a end of LRO delete
        # https://github.com/Azure/msrestazure-for-python/issues/7
        async_delete = self.client.database_accounts.delete(resource_group.name, account_name)
        try:
            async_delete.wait()
        except CloudError as err:
            if err.response.status_code != 404:
                raise


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
