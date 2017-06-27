# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.cosmosdb
from msrestazure.azure_exceptions import CloudError
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase

import logging
#logging.basicConfig(level=logging.DEBUG)


class MgmtCosmosDBTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCosmosDBTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.cosmosdb.CosmosDB
        )
        # I don't record resource group creation, since it's another package
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_accounts_create(self):
        account_name = self.get_resource_name('pycosmosdbtst')

        self.assertFalse(self.client.database_accounts.check_name_exists(account_name))

        async_cosmosdb_create = self.client.database_accounts.create_or_update(
            self.group_name,
            account_name,
            {
                'location': self.region,
                'locations': [{
                    'location_name': self.region
                }]
            }
        )
        account = async_cosmosdb_create.result()
        self.assertIsNotNone(account)
        # Rest API issue
        # self.assertEqual(account.name, account_name)

    def test_accounts_features(self):
        account_name = self.get_resource_name('pycosmosdbtest')

        if not self.is_playback():
            async_cosmosdb_create = self.client.database_accounts.create_or_update(
                self.group_name,
                account_name,
                {
                    'location': self.region,
                    'locations': [{
                        'location_name': self.region
                    }]
                }
            )
            async_cosmosdb_create.wait()

        with self.recording():
            account = self.client.database_accounts.get(
                self.group_name,
                account_name
            )
            self.assertEqual(account.name, account_name)

            my_accounts = list(self.client.database_accounts.list_by_resource_group(self.group_name))
            self.assertEqual(len(my_accounts), 1)
            self.assertEqual(my_accounts[0].name, account_name)

            my_accounts = list(self.client.database_accounts.list())
            self.assertTrue(len(my_accounts) >= 1)
            self.assertTrue(any(db.name == account_name for db in my_accounts))

            async_change = self.client.database_accounts.failover_priority_change(
                self.group_name,
                account_name,
                [{
                    'location_name': self.region,
                    'failover_priority': 0
                }]
            )
            async_change.wait()

            my_keys = self.client.database_accounts.list_keys(
                self.group_name,
                account_name
            )
            self.assertIsNotNone(my_keys.primary_master_key)
            self.assertIsNotNone(my_keys.secondary_master_key)
            self.assertIsNotNone(my_keys.primary_readonly_master_key)
            self.assertIsNotNone(my_keys.secondary_readonly_master_key)
    

            my_keys = self.client.database_accounts.list_read_only_keys(
                self.group_name,
                account_name
            )
            self.assertIsNotNone(my_keys.primary_readonly_master_key)
            self.assertIsNotNone(my_keys.secondary_readonly_master_key)


            async_regenerate = self.client.database_accounts.regenerate_key(
                self.group_name,
                account_name,
                "primary"
            )
            async_regenerate.wait()

    def test_accounts_delete(self):
        account_name = self.get_resource_name('pydocumentdbtst')

        if not self.is_playback():
            async_cosmosdb_create = self.client.database_accounts.create_or_update(
                self.group_name,
                account_name,
                {
                    'location': self.region,
                    'locations': [{
                        'location_name': self.region
                    }]
                }
            )
            async_cosmosdb_create.wait()

        with self.recording():
            # Current implementation of msrestazure does not support 404 as a end of LRO delete
            # https://github.com/Azure/msrestazure-for-python/issues/7
            async_delete = self.client.database_accounts.delete(self.group_name, account_name)
            try:
                async_delete.wait()
            except CloudError as err:
                if err.response.status_code != 404:
                    raise


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
