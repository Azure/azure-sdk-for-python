# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.containerregistry
import azure.mgmt.storage

from devtools_testutils import (
    AzureMgmtTestCase, FakeStorageAccount,
    ResourceGroupPreparer, StorageAccountPreparer
)


FAKE_STORAGE = FakeStorageAccount(
    name='pyacrstorage',
    id=''
)


class MgmtACRTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtACRTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.containerregistry.ContainerRegistryManagementClient
        )

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_registry(self, resource_group, location, storage_account, storage_account_key):
        registry_name = self.get_resource_name('pyacr')

        name_status = self.client.registries.check_name_availability(registry_name)
        self.assertTrue(name_status.name_available)

        async_registry_creation = self.client.registries.create(
            resource_group.name,
            registry_name,
            {
                'location': location,
                'sku': {
                    'name': 'Basic'
                },
                'storage_account': {
                    'name': storage_account.name,
                    'access_key': storage_account_key,
                }
            }
        )
        registry = async_registry_creation.result()
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.location, location)
        self.assertEqual(registry.sku.name, 'Basic')
        self.assertEqual(registry.sku.tier, 'Basic')
        self.assertEqual(registry.admin_user_enabled, False)

        registry = self.client.registries.update(
            resource_group.name,
            registry_name,
            {
                'admin_user_enabled': True
            }
        )
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.admin_user_enabled, True)

        registry = self.client.registries.get(resource_group.name, registry_name)
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.admin_user_enabled, True)

        registries = list(self.client.registries.list_by_resource_group(resource_group.name))
        self.assertEqual(len(registries), 1)

        credentials = self.client.registries.list_credentials(resource_group.name, registry_name)
        self.assertEqual(len(credentials.passwords), 2)

        credentials = self.client.registries.regenerate_credential(
            resource_group.name, registry_name, 'password')
        self.assertEqual(len(credentials.passwords), 2)

        self.client.registries.delete(resource_group.name, registry_name)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
