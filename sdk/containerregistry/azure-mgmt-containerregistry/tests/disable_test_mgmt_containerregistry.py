# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from azure.mgmt.containerregistry.v2017_10_01.models import (
    Registry,
    RegistryUpdateParameters,
    StorageAccountProperties,
    Sku,
    SkuName,
    SkuTier,
    ProvisioningState,
    PasswordName,
    WebhookCreateParameters,
    WebhookUpdateParameters,
    WebhookAction,
    WebhookStatus
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
DEFAULT_REPLICATION_LOCATION = 'southcentralus'
DEFAULT_WEBHOOK_SERVICE_URI = 'http://www.microsoft.com'
DEFAULT_WEBHOOK_SCOPE = 'hello-world'
DEFAULT_KEY_VALUE_PAIR = {
    'key': 'value'
}


class MgmtACRTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtACRTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.containerregistry.ContainerRegistryManagementClient
        )


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    @StorageAccountPreparer(name_prefix='pyacr', location=DEFAULT_LOCATION, playback_fake_resource=FAKE_STORAGE)
    def _disabled_test_classic_registry(self, resource_group, location, storage_account):
        registry_name = self.get_resource_name('pyacr')

        name_status = self.client.registries.check_name_availability(registry_name)
        self.assertTrue(name_status.name_available)

        # Create a classic registry
        registry = self.client.registries.create(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            registry=Registry(
                location=location,
                sku=Sku(
                    name=SkuName.classic
                ),
                storage_account=StorageAccountProperties(
                    id=storage_account.id
                )
            )
        ).result()
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.location, location)
        self.assertEqual(registry.sku.name, SkuName.classic.value)
        self.assertEqual(registry.sku.tier, SkuTier.classic.value)
        self.assertEqual(registry.provisioning_state, ProvisioningState.succeeded.value)
        self.assertEqual(registry.admin_user_enabled, False)

        self._core_registry_scenario(registry_name, resource_group.name)


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    def test_managed_registry(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')

        name_status = self.client.registries.check_name_availability(registry_name)
        self.assertTrue(name_status.name_available)

        # Create a managed registry
        self._create_managed_registry(registry_name, resource_group.name, location)
        self._core_registry_scenario(registry_name, resource_group.name)


    def _core_registry_scenario(self, registry_name, resource_group_name):
        registries = list(self.client.registries.list_by_resource_group(resource_group_name))
        self.assertEqual(len(registries), 1)

        # Update the registry with new tags and enable admin user
        registry = self.client.registries.update(
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            registry_update_parameters=RegistryUpdateParameters(
                tags=DEFAULT_KEY_VALUE_PAIR,
                admin_user_enabled=True
            )
        ).result()
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(registry.admin_user_enabled, True)

        registry = self.client.registries.get(resource_group_name, registry_name)
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(registry.admin_user_enabled, True)

        credentials = self.client.registries.list_credentials(resource_group_name, registry_name)
        self.assertEqual(len(credentials.passwords), 2)

        credentials = self.client.registries.regenerate_credential(
            resource_group_name, registry_name, PasswordName.password)
        self.assertEqual(len(credentials.passwords), 2)

        if registry.sku.name == SkuName.premium.value:
            usages = self.client.registries.list_usages(resource_group_name, registry_name)
            self.assertTrue(len(usages.value) > 1)

        self.client.registries.delete(resource_group_name, registry_name).wait()


    def _create_managed_registry(self, registry_name, resource_group_name, location):
        registry = self.client.registries.create(
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            registry=Registry(
                location=location,
                sku=Sku(
                    name=SkuName.premium
                )
            )
        ).result()
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.location, location)
        self.assertEqual(registry.sku.name, SkuName.premium.value)
        self.assertEqual(registry.sku.tier, SkuTier.premium.value)
        self.assertEqual(registry.provisioning_state, ProvisioningState.succeeded.value)
        self.assertEqual(registry.admin_user_enabled, False)
        self.assertEqual(registry.storage_account, None)


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    def test_webhook(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')
        webhook_name = self.get_resource_name('pyacr')

        # Create a managed registry
        self._create_managed_registry(registry_name, resource_group.name, location)

        # Create a webhook
        webhook = self.client.webhooks.create(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            webhook_name=webhook_name,
            webhook_create_parameters=WebhookCreateParameters(
                location=location,
                service_uri=DEFAULT_WEBHOOK_SERVICE_URI,
                actions=[WebhookAction.push]
            )
        ).result()
        self.assertEqual(webhook.name, webhook_name)
        self.assertEqual(webhook.location, location)
        self.assertEqual(webhook.provisioning_state, ProvisioningState.succeeded.value)
        self.assertEqual(webhook.actions, [WebhookAction.push.value])
        self.assertEqual(webhook.status, WebhookStatus.enabled.value)

        webhooks = list(self.client.webhooks.list(resource_group.name, registry_name))
        self.assertEqual(len(webhooks), 1)

        # Update the webhook with custom headers, scope, and new tags
        webhook = self.client.webhooks.update(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            webhook_name=webhook_name,
            webhook_update_parameters=WebhookUpdateParameters(
                tags=DEFAULT_KEY_VALUE_PAIR,
                custom_headers=DEFAULT_KEY_VALUE_PAIR,
                scope=DEFAULT_WEBHOOK_SCOPE
            )
        ).result()
        self.assertEqual(webhook.name, webhook_name)
        self.assertEqual(webhook.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(webhook.scope, DEFAULT_WEBHOOK_SCOPE)

        webhook = self.client.webhooks.get(resource_group.name, registry_name, webhook_name)
        self.assertEqual(webhook.name, webhook_name)
        self.assertEqual(webhook.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(webhook.scope, DEFAULT_WEBHOOK_SCOPE)

        webhook_config = self.client.webhooks.get_callback_config(
            resource_group.name,
            registry_name,
            webhook_name
        )
        self.assertEqual(webhook_config.service_uri, DEFAULT_WEBHOOK_SERVICE_URI)
        self.assertEqual(webhook_config.custom_headers, DEFAULT_KEY_VALUE_PAIR)

        self.client.webhooks.ping(resource_group.name, registry_name, webhook_name)
        self.client.webhooks.list_events(resource_group.name, registry_name, webhook_name)

        self.client.webhooks.delete(resource_group.name, registry_name, webhook_name).wait()
        self.client.registries.delete(resource_group.name, registry_name).wait()


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    def _disabled_test_replication(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')
        replication_name = DEFAULT_REPLICATION_LOCATION

        # Create a managed registry
        self._create_managed_registry(registry_name, resource_group.name, location)

        # Create a replication
        replication = self.client.replications.create(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            replication_name=replication_name,
            location=DEFAULT_REPLICATION_LOCATION
        ).result()
        self.assertEqual(replication.name, replication_name)
        self.assertEqual(replication.location, DEFAULT_REPLICATION_LOCATION)
        self.assertEqual(replication.provisioning_state, ProvisioningState.succeeded.value)

        replications = list(self.client.replications.list(resource_group.name, registry_name))
        self.assertEqual(len(replications), 2) # 2 because a replication in home region is auto created

        # Update the replication with new tags
        replication = self.client.replications.update(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            replication_name=replication_name,
            tags=DEFAULT_KEY_VALUE_PAIR
        ).result()
        self.assertEqual(replication.name, replication_name)
        self.assertEqual(replication.tags, DEFAULT_KEY_VALUE_PAIR)

        replication = self.client.replications.get(resource_group.name, registry_name, replication_name)
        self.assertEqual(replication.name, replication_name)
        self.assertEqual(replication.tags, DEFAULT_KEY_VALUE_PAIR)

        self.client.replications.delete(resource_group.name, registry_name, replication_name).wait()
        self.client.registries.delete(resource_group.name, registry_name).wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
