# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.search
from datetime import date, timedelta
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtSearchTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSearchTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.search.SearchManagementClient
        )

    @ResourceGroupPreparer()
    def test_search_services(self, resource_group, location):
        account_name = 'ptvstestsearch'

        availability = self.client.services.check_name_availability(account_name)
        self.assertTrue(availability.is_name_available)

        service = self.client.services.begin_create_or_update(
            resource_group.name,
            account_name,
            {
                'location': location,
                'replica_count': 1,
                'partition_count': 1,
                'hosting_mode': 'Default',
                'sku': {
                    'name': 'standard'
                }
            }
        ).result()

        availability = self.client.services.check_name_availability(account_name)
        self.assertFalse(availability.is_name_available)
        self.assertEqual(availability.reason, "AlreadyExists")

        service = self.client.services.get(
            resource_group.name,
            service.name
        )
        self.assertEqual(service.name, account_name)

        services = list(self.client.services.list_by_resource_group(resource_group.name))
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].name, account_name)

        self.client.services.delete(
            resource_group.name,
            service.name
        )

    @ResourceGroupPreparer()
    def test_search_query_keys(self, resource_group, location):
        account_name = 'ptvstestquerykeysxxy'
        key_name = 'testkey'

        service = self.client.services.begin_create_or_update(
            resource_group.name,
            account_name,
            {
                'location': location,
                'replica_count': 1,
                'partition_count': 1,
                'hosting_mode': 'Default',
                'sku': {
                    'name': 'standard'
                }
            }
        ).result()

        key = self.client.query_keys.create(
            resource_group.name,
            account_name,
            key_name,
        )
        self.assertEqual(key.name, key_name)

        keys = list(self.client.query_keys.list_by_search_service(
            resource_group.name,
            account_name
        ))
        self.assertEqual(len(keys), 2) # default key and mine
        self.assertIsNone(keys[0].name)
        self.assertEqual(keys[1].name, key_name)

        self.client.query_keys.delete(
            resource_group.name,
            account_name,
            key_name
        )

    @ResourceGroupPreparer()
    def test_search_admin_keys(self, resource_group, location):
        account_name = 'ptvstestquerykeys'

        service = self.client.services.begin_create_or_update(
            resource_group.name,
            account_name,
            {
                'location': location,
                'replica_count': 1,
                'partition_count': 1,
                'hosting_mode': 'Default',
                'sku': {
                    'name': 'free'
                }
            }
        )

        admin_keys = self.client.admin_keys.get(
            resource_group.name,
            account_name
        )
        self.assertIsNotNone(admin_keys.primary_key)
        self.assertIsNotNone(admin_keys.secondary_key)

        regenerated_admin_keys = self.client.admin_keys.regenerate(
            resource_group.name,
            account_name,
            'primary'
        )
        self.assertIsNotNone(regenerated_admin_keys.primary_key)
        self.assertEqual(admin_keys.secondary_key, regenerated_admin_keys.secondary_key)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
