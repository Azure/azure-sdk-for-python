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
        super(MgmtACRTest, self).setUp()
        self.region = 'westus'
        self.client = self.create_mgmt_client(
            azure.mgmt.containerregistry.ContainerRegistryManagementClient
        )
        self.storage_name = self.get_resource_name('pyacrstorage')
        self.storage_key = ''
        if not self.is_playback():
            self.create_resource_group()

            self.storage_client = self.create_mgmt_client(
                azure.mgmt.storage.StorageManagementClient
            )

            async_storage_creation = self.storage_client.storage_accounts.create(
                self.group_name,
                self.storage_name,
                {
                    'location': self.region,
                    'sku': {
                        'name': 'Standard_LRS'
                    },
                    'kind': 'Storage'
                }
            )
            self.storage_account = async_storage_creation.result()
            storage_keys = self.storage_client.storage_accounts.list_keys(
                self.group_name, self.storage_name)
            storage_keys = {v.key_name: v.value for v in storage_keys.keys}
            self.storage_key = storage_keys['key1']

    @record
    def test_registry(self):
        registry_name = self.get_resource_name('pyacr')

        name_status = self.client.registries.check_name_availability(registry_name)
        self.assertTrue(name_status.name_available)

        async_registry_creation = self.client.registries.create(
            self.group_name,
            registry_name,
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
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.location, self.region)
        self.assertEqual(registry.sku.name, 'Basic')
        self.assertEqual(registry.sku.tier, 'Basic')
        self.assertEqual(registry.admin_user_enabled, False)

        registry = self.client.registries.update(
            self.group_name,
            registry_name,
            {
                'admin_user_enabled': True
            }
        )
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.admin_user_enabled, True)

        registry = self.client.registries.get(self.group_name, registry_name)
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.admin_user_enabled, True)

        registries = list(self.client.registries.list_by_resource_group(self.group_name))
        self.assertEqual(len(registries), 1)

        credentials = self.client.registries.list_credentials(self.group_name, registry_name)
        self.assertEqual(len(credentials.passwords), 2)

        credentials = self.client.registries.regenerate_credential(
            self.group_name, registry_name, 'password')
        self.assertEqual(len(credentials.passwords), 2)

        self.client.registries.delete(self.group_name, registry_name)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
