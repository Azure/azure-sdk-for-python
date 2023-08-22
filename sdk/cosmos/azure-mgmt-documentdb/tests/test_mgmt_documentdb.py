# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import pytest

import azure.mgmt.documentdb
from msrestazure.azure_exceptions import CloudError
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtDocDBTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDocDBTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.documentdb.DocumentDB
        )

    @pytest.mark.live_test_only("Can't use recordings until tests use the test proxy")
    @ResourceGroupPreparer()
    def test_accounts_create(self, resource_group, location):
        account_name = self.get_resource_name('pydocdbtst')

        self.assertFalse(self.client.database_accounts.check_name_exists(account_name))

        async_docdb_create = self.client.database_accounts.create_or_update(
            resource_group.name,
            account_name,
            {
                'location': location,
                'locations': [{
                    'location_name': self.region
                }]
            }
        )
        account = async_docdb_create.result()
        self.assertIsNotNone(account)
        # Rest API issue
        # self.assertEqual(account.name, account_name)

    @pytest.mark.live_test_only("Can't use recordings until tests use the test proxy")
    @ResourceGroupPreparer()
    def test_accounts_features(self, resource_group, location):
        account_name = self.get_resource_name('pydocdbtest')

        if not self.is_playback():
            async_docdb_create = self.client.database_accounts.create_or_update(
                resource_group.name,
                account_name,
                {
                    'location': location,
                    'locations': [{
                        'location_name': self.region
                    }]
                }
            )
            async_docdb_create.wait()

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

        # I guess we can make this test with no error, need to check with DocDB team
        # This is an interesting test anyway, this implies that the serialization works
        # and error message is available. Since this method does not return an object
        # (i.e. no deserialization to test), this is a complete test.
        # We are NOT here to test the RestAPI, but the Swagger file and Python code.
        with self.assertRaises(CloudError) as cm:
            async_change = self.client.database_accounts.failover_priority_change(
                resource_group.name,
                account_name,
                [{
                    'location_name': self.region,
                    'failover_priority': 0
                }]
            )
            async_change.wait()
        self.assertIn('Failover priorities must be unique', cm.exception.message)

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

    @pytest.mark.live_test_only("Can't use recordings until tests use the test proxy")
    @ResourceGroupPreparer()
    def test_accounts_delete(self, resource_group, location):
        account_name = self.get_resource_name('pydocumentdbtst')

        if not self.is_playback():
            async_docdb_create = self.client.database_accounts.create_or_update(
                resource_group.name,
                account_name,
                {
                    'location': location,
                    'locations': [{
                        'location_name': self.region
                    }]
                }
            )
            async_docdb_create.wait()

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
