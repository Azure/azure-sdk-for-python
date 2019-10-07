# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from azure.mgmt.containerregistry.v2017_03_01.models import (
    RegistryCreateParameters,
    RegistryUpdateParameters,
    StorageAccountParameters,
    Sku,
    SkuTier,
    ProvisioningState,
    PasswordName
)
import azure.mgmt.storage

from devtools_testutils import (
    AzureMgmtTestCase, FakeStorageAccount,
    ResourceGroupPreparer, StorageAccountPreparer
)


FAKE_STORAGE = FakeStorageAccount(
    name='pyacr',
    id=''
)

DEFAULT_LOCATION = 'westcentralus'
DEFAULT_SKU_NAME = 'Basic'
DEFAULT_KEY_VALUE_PAIR = {
    'key': 'value'
}


class MgmtACRTest20170301(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtACRTest20170301, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.containerregistry.ContainerRegistryManagementClient,
            api_version='2017-03-01'
        )


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    @StorageAccountPreparer(name_prefix='pyacr', location=DEFAULT_LOCATION, playback_fake_resource=FAKE_STORAGE)
    def _disabled_test_basic_registry(self, resource_group, location, storage_account, storage_account_key):
        registry_name = self.get_resource_name('pyacr')

        name_status = self.client.registries.check_name_availability(registry_name)
        self.assertTrue(name_status.name_available)

        # Create a Basic registry
        registry = self.client.registries.create(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            registry_create_parameters=RegistryCreateParameters(
                location=location,
                sku=Sku(
                    name=DEFAULT_SKU_NAME
                ),
                storage_account=StorageAccountParameters(
                    name=storage_account.name,
                    access_key=storage_account_key
                )
            )
        ).result()
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.location, location)
        self.assertEqual(registry.sku.name, DEFAULT_SKU_NAME)
        self.assertEqual(registry.sku.tier, SkuTier.basic.value)
        self.assertEqual(registry.provisioning_state.value, ProvisioningState.succeeded.value)
        self.assertEqual(registry.admin_user_enabled, False)

        registries = list(self.client.registries.list_by_resource_group(resource_group.name))
        self.assertEqual(len(registries), 1)

        # Update the registry with new tags and enable admin user
        registry = self.client.registries.update(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            registry_update_parameters=RegistryUpdateParameters(
                tags=DEFAULT_KEY_VALUE_PAIR,
                admin_user_enabled=True
            )
        )
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(registry.admin_user_enabled, True)

        registry = self.client.registries.get(resource_group.name, registry_name)
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(registry.admin_user_enabled, True)

        credentials = self.client.registries.list_credentials(resource_group.name, registry_name)
        self.assertEqual(len(credentials.passwords), 2)

        credentials = self.client.registries.regenerate_credential(
            resource_group.name, registry_name, PasswordName.password)
        self.assertEqual(len(credentials.passwords), 2)

        self.client.registries.delete(resource_group.name, registry_name)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
