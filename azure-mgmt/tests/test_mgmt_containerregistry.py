# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.containerregistry
import azure.mgmt.storage
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtACRTest(AzureMgmtTestCase):

    def setUp(self):
        self.region = 'eastus'

        super(MgmtACRTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.containerregistry.ContainerRegistryManagementClient
        )
        self.storage_name = 'mstopytest'
        if not self.is_playback():
            self.create_resource_group()

            self.storage_client = self.create_mgmt_client(
                azure.mgmt.storage.StorageManagementClient
            )

            params_create = azure.mgmt.storage.models.StorageAccountCreateParameters(
                sku=azure.mgmt.storage.models.Sku(azure.mgmt.storage.models.SkuName.standard_lrs),
                kind=azure.mgmt.storage.models.Kind.storage,
                location=self.region
            )
            result_create = self.storage_client.storage_accounts.create(
                self.group_name,
                self.storage_name,
                params_create,
            )
            self.storage_account = result_create.result()
            storage_keys = self.storage_client.storage_accounts.list_keys(self.group_name, self.storage_name)
            storage_keys = {v.key_name: v.value for v in storage_keys.keys}
            self.storage_key = storage_keys['key1']
        else:
            # If you record this test, change this one by the one in the record
            self.storage_key = 'BbDRMu3dSOcnBKQKls+ZvJmw1ZWezQ/6k1feiExRDEUHMTForgY6OvWz84yJ5XYlq1Lt4ajnRs7eJq+WUVKkOw=='

    @record
    def test_acr(self):
        account_name = self.get_resource_name('pyacr')

        name_status = self.client.registries.check_name_availability(account_name)
        self.assertTrue(name_status.name_available)

        async_registry_creation = self.client.registries.create(
            self.group_name,
            account_name,
            {
                'location': self.region,
                'sku': {
                    'name': 'Basic'
                },
                'storage_account': {
                    'name': self.storage_name,
                    'access_key': self.storage_key
                }
            }
        )
        registry = async_registry_creation.result()
        self.assertEqual(registry.name, account_name)

        registry = self.client.registries.update(
            self.group_name,
            account_name,
            {
                'admin_user_enabled': True
            }
        )
        self.assertEqual(registry.name, account_name)

        registry = self.client.registries.get(self.group_name, account_name)
        self.assertEqual(registry.name, account_name)

        containers = list(self.client.registries.list())
        self.assertEqual(len(containers), 1)

        containers = list(self.client.registries.list_by_resource_group(self.group_name))
        self.assertEqual(len(containers), 1)

        credentials = self.client.registries.list_credentials(self.group_name, account_name)

        credentials = self.client.registries.regenerate_credential(self.group_name, account_name, 'password')

        self.client.registries.delete(self.group_name, account_name)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
