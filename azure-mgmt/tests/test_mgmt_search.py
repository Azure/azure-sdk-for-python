# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.search
from datetime import date, timedelta
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtSearchTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSearchTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.search.SearchManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_search_services(self):
        account_name = 'ptvstestsearch'

        availability = self.client.services.check_name_availability(account_name)
        self.assertTrue(availability.is_name_available)

        service = self.client.services.create_or_update(
            self.group_name,
            account_name,
            {
                'location': self.region,
                'replica_count': 1,
                'partition_count': 1,
                'hosting_mode': 'Default',
                'sku': {
                    'name': 'free'
                }
            }
        )

        availability = self.client.services.check_name_availability(account_name)
        self.assertFalse(availability.is_name_available)
        self.assertEquals(availability.reason, "AlreadyExists")

        service = self.client.services.get(
            self.group_name,
            service.name
        )
        self.assertEquals(service.name, account_name)        

        services = list(self.client.services.list_by_resource_group(self.group_name))
        self.assertEquals(len(services), 1)
        self.assertEquals(services[0].name, account_name)

        self.client.services.delete(
            self.group_name,
            service.name
        )    

    @record
    def test_search_query_keys(self):
        account_name = 'ptvstestquerykeys'
        key_name = 'testkey'

        service = self.client.services.create_or_update(
            self.group_name,
            account_name,
            {
                'location': self.region,
                'replica_count': 1,
                'partition_count': 1,
                'hosting_mode': 'Default',
                'sku': {
                    'name': 'free'
                }
            }
        )

        key = self.client.query_keys.create(
            self.group_name,
            account_name,
            key_name,
        )
        self.assertEquals(key.name, key_name)

        keys = list(self.client.query_keys.list_by_search_service(
            self.group_name,
            account_name
        ))
        self.assertEquals(len(keys), 2) # default key and mine
        self.assertIsNone(keys[0].name)
        self.assertEquals(keys[1].name, key_name)

        self.client.query_keys.delete(
            self.group_name,
            account_name,
            key_name
        )

    @record
    def test_search_admin_keys(self):
        account_name = 'ptvstestquerykeys'

        service = self.client.services.create_or_update(
            self.group_name,
            account_name,
            {
                'location': self.region,
                'replica_count': 1,
                'partition_count': 1,
                'hosting_mode': 'Default',
                'sku': {
                    'name': 'free'
                }
            }
        )

        admin_keys = self.client.admin_keys.get(
            self.group_name,
            account_name
        )
        self.assertIsNotNone(admin_keys.primary_key)
        self.assertIsNotNone(admin_keys.secondary_key)

        regenerated_admin_keys = self.client.admin_keys.regenerate(
            self.group_name,
            account_name,
            'primary'
        )
        self.assertIsNotNone(regenerated_admin_keys.primary_key)
        self.assertEquals(admin_keys.secondary_key, regenerated_admin_keys.secondary_key)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
