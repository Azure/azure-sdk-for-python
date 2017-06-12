# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.containerregistry

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtACRTest20170601Preview(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtACRTest20170601Preview, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.containerregistry.ContainerRegistryManagementClient,
            api_version='2017-06-01-preview'
        )

    @ResourceGroupPreparer(location='westcentralus')
    def test_registry(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')

        name_status = self.client.registries.check_name_availability(registry_name)
        self.assertTrue(name_status.name_available)

        async_registry_creation = self.client.registries.create(
            resource_group.name,
            registry_name,
            {
                'location': location,
                'sku': {
                    'name': 'Managed_Standard'
                }
            }
        )
        registry = async_registry_creation.result()
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.location, location)
        self.assertEqual(registry.sku.name, 'Managed_Standard')
        self.assertEqual(registry.sku.tier, 'Managed')
        self.assertEqual(registry.provisioning_state, 'Succeeded')
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

    @ResourceGroupPreparer(location='westcentralus')
    def test_webhook(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')
        webhook_name = self.get_resource_name('pyacrwebhook')

        async_registry_creation = self.client.registries.create(
            resource_group.name,
            registry_name,
            {
                'location': location,
                'sku': {
                    'name': 'Managed_Standard'
                }
            }
        )
        registry = async_registry_creation.result()
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.location, location)
        self.assertEqual(registry.sku.name, 'Managed_Standard')
        self.assertEqual(registry.sku.tier, 'Managed')
        self.assertEqual(registry.provisioning_state, 'Succeeded')
        self.assertEqual(registry.admin_user_enabled, False)

        async_webhook_creation = self.client.webhooks.create(
            resource_group.name,
            registry_name,
            webhook_name,
            {
                'location': location,
                'service_uri': 'http://www.microsoft.com',
                'actions': ['push']
            }
        )
        webhook = async_webhook_creation.result()
        self.assertEqual(webhook.name, webhook_name)
        self.assertEqual(webhook.location, location)
        self.assertEqual(webhook.actions, ['push'])
        self.assertEqual(webhook.status, 'enabled')

        async_webhook_update = self.client.webhooks.update(
            resource_group.name,
            registry_name,
            webhook_name,
            {
                'custom_headers': {
                    'key': 'value'
                },
                'scope': 'hello-world'
            }
        )
        webhook = async_webhook_update.result()
        self.assertEqual(webhook.name, webhook_name)
        self.assertEqual(webhook.scope, 'hello-world')

        webhook = self.client.webhooks.get(resource_group.name, registry_name, webhook_name)
        self.assertEqual(webhook.name, webhook_name)
        self.assertEqual(webhook.scope, 'hello-world')

        webhook_config = self.client.webhooks.get_callback_config(
            resource_group.name,
            registry_name,
            webhook_name
        )

        self.assertEqual(webhook_config.service_uri, 'http://www.microsoft.com')
        self.assertEqual(webhook_config.custom_headers, {
            'key': 'value'
        })

        webhooks = list(self.client.webhooks.list(resource_group.name, registry_name))
        self.assertEqual(len(webhooks), 1)

        self.client.webhooks.ping(resource_group.name, registry_name, webhook_name)
        self.client.webhooks.list_events(resource_group.name, registry_name, webhook_name)

        self.client.webhooks.delete(resource_group.name, registry_name, webhook_name)
        self.client.registries.delete(resource_group.name, registry_name)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
