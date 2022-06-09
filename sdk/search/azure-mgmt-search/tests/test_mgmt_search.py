# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.search
from datetime import date, timedelta
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy

class TestMgmtSearch(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            azure.mgmt.search.SearchManagementClient
        )

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_search_services(self, **kwargs):
        resource_group = kwargs.pop("resource_group")
        location = kwargs.pop("location")
        account_name = 'ptvstestsearch'

        availability = self.client.services.check_name_availability(account_name)
        assert availability.is_name_available

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
        assert not availability.is_name_available
        assert availability.reason == "AlreadyExists"

        service = self.client.services.get(
            resource_group.name,
            service.name
        )
        assert service.name == account_name

        services = list(self.client.services.list_by_resource_group(resource_group.name))
        assert len(services) == 1
        assert services[0].name == account_name

        self.client.services.delete(
            resource_group.name,
            service.name
        )

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_search_query_keys(self, **kwargs):
        resource_group = kwargs.pop("resource_group")
        location = kwargs.pop("location")
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
        assert key.name == key_name

        keys = list(self.client.query_keys.list_by_search_service(
            resource_group.name,
            account_name
        ))
        assert len(keys) == 2 # default key and mine
        assert keys[0].name is None
        assert keys[1].name == key_name

        self.client.query_keys.delete(
            resource_group.name,
            account_name,
            key_name
        )

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_search_admin_keys(self, **kwargs):
        resource_group = kwargs.pop("resource_group")
        location = kwargs.pop("location")
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
        assert admin_keys.primary_key is not None
        assert admin_keys.secondary_key is not None

        regenerated_admin_keys = self.client.admin_keys.regenerate(
            resource_group.name,
            account_name,
            'primary'
        )
        assert regenerated_admin_keys.primary_key is not None
        assert admin_keys.secondary_key == regenerated_admin_keys.secondary_key

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
