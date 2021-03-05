# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   snapshots: 8/8
#   disks: 8/8
#   disk_encryption_sets: 6/6
#   images: 6/6

import unittest

import azure.mgmt.compute
from azure.profiles import ProfileDefinition
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtComputeTestMultiVersion(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTestMultiVersion, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )
        self.mgmt_client.profile = ProfileDefinition({
            self.mgmt_client._PROFILE_TAG: {
                None: "2019-07-01",
                'availability_sets': '2019-07-01',
                'dedicated_host_groups': '2019-07-01',
                'dedicated_hosts': '2019-07-01',
                'disk_encryption_sets': '2019-11-01',
                'disks': '2019-03-01',  # test old version
                'images': '2019-07-01',
                'log_analytics': '2019-07-01',
                'operations': '2019-07-01',
                'proximity_placement_groups': '2019-07-01',
                'resource_skus': '2019-04-01',
                'snapshots': '2019-11-01',
                'usage': '2019-07-01',
                'virtual_machine_extension_images': '2019-07-01',
                'virtual_machine_extensions': '2019-07-01',
                'virtual_machine_images': '2019-07-01',
                'virtual_machine_run_commands': '2019-07-01',
                'virtual_machine_scale_set_extensions': '2019-07-01',
                'virtual_machine_scale_set_rolling_upgrades': '2019-07-01',
                'virtual_machine_scale_set_vm_extensions': '2019-07-01',
                'virtual_machine_scale_set_vms': '2019-07-01',
                'virtual_machine_scale_sets': '2019-07-01',
                'virtual_machine_sizes': '2019-07-01',
                'virtual_machines': '2019-07-01',
            }},
            self.mgmt_client._PROFILE_TAG + " test"
        )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_disks_multi(self, resource_group):

        DISK_NAME = self.get_resource_name("disknamex")

        # Create an empty managed disk.[put]
        BODY = {
          "location": "eastus",
          "creation_data": {
            "create_option": "Empty"
          },
          "disk_size_gb": "200"
        }
        result = self.mgmt_client.disks.begin_create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Get information about a managed disk.[get]
        result = self.mgmt_client.disks.get(resource_group.name, DISK_NAME)

        # List all managed disks in a resource group.[get]
        result = self.mgmt_client.disks.list_by_resource_group(resource_group.name)

        # List all managed disks in a subscription.[get]
        result = self.mgmt_client.disks.list()

        # Update disk.[patch]
        BODY = {
          "disk_size_gb": "200"
        }
        result = self.mgmt_client.disks.begin_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Grant acess disk
        BODY = {
          "access": "Read",
          "duration_in_seconds": "1800"
        }
        result = self.mgmt_client.disks.begin_grant_access(resource_group.name, DISK_NAME, BODY)
        result = result.result()

         # Revoke access disk
        result = self.mgmt_client.disks.begin_revoke_access(resource_group.name, DISK_NAME)
        result = result.result()

        # Delete disk
        result = self.mgmt_client.disks.begin_delete(resource_group.name, DISK_NAME)
        result = result.result()

class MgmtComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )
        if self.is_live:
            from azure.mgmt.keyvault import KeyVaultManagementClient
            self.keyvault_client = self.create_mgmt_client(
                KeyVaultManagementClient
            )
            # self.network_client = self.create_mgmt_client(
            #     azure.mgmt.network.NetworkManagementClient
            # )

    def create_key(self, group_name, location, key_vault, tenant_id, object_id):
        if self.is_live:
            result = self.keyvault_client.vaults.begin_create_or_update(
                group_name,
                key_vault,
                {
                  'location': location,
                  'properties': {
                    'sku': {
                      'family': "A",
                      'name': 'standard'
                    },
                    'tenant_id': tenant_id,
                    "access_policies": [
                      {
                        "tenant_id": tenant_id,
                        "object_id": object_id,
                        "permissions": {
                          "keys": [
                            "encrypt",
                            "decrypt",
                            "wrapKey",
                            "unwrapKey",
                            "sign",
                            "verify",
                            "get",
                            "list",
                            "create",
                            "update",
                            "import",
                            "delete",
                            "backup",
                            "restore",
                            "recover",
                            "purge"
                          ]
                        }
                      }
                    ],
                    'enabled_for_disk_encryption': True,
                  }
                }
            ).result()
            vault_url = result.properties.vault_uri
            vault_id = result.id

            from azure.keyvault.keys import KeyClient
            credentials = self.settings.get_azure_core_credentials()
            key_client = KeyClient(vault_url, credentials)

            # [START create_key]
            from dateutil import parser as date_parse
            expires_on = date_parse.parse("2050-02-02T08:00:00.000Z")

            key = key_client.create_key(
              "testkey",
              "RSA",
              size=2048,
              expires_on=expires_on
            )
            return (vault_id, key.id)
        else:
            return ('000', '000')

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_disk_encryption(self, resource_group):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        CLIENT_OID = self.settings.CLIENT_OID if self.is_live else "000"
        RESOURCE_GROUP = resource_group.name
        KEY_VAULT_NAME = self.get_resource_name("keyvaultxmmky")
        DISK_ENCRYPTION_SET_NAME = self.get_resource_name("diskencryptionset")

        VAULT_ID, KEY_URI = self.create_key(RESOURCE_GROUP, AZURE_LOCATION, KEY_VAULT_NAME, TENANT_ID, CLIENT_OID)

        # Create a disk encryption set.[put]
        BODY = {
          "location": "eastus",
          "identity": {
            "type": "SystemAssigned"
          },
          "active_key": {
            "source_vault": {
              # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.KeyVault/vaults/" + VAULT_NAME + ""
              "id": VAULT_ID
            },
            # "key_url": "https://myvmvault.vault-int.azure-int.net/keys/{key}/{key_version}"
            "key_url": KEY_URI
          }
        }
        result = self.mgmt_client.disk_encryption_sets.begin_create_or_update(resource_group.name, DISK_ENCRYPTION_SET_NAME, BODY)
        result = result.result()

        # # Get information about a disk encryption set.[get]
        result = self.mgmt_client.disk_encryption_sets.get(resource_group.name, DISK_ENCRYPTION_SET_NAME)

        # List all disk encryption sets in a resource group.[get]
        result = self.mgmt_client.disk_encryption_sets.list_by_resource_group(resource_group.name)

        # List all disk encryption sets in a subscription.[get]
        result = self.mgmt_client.disk_encryption_sets.list()

        # Update a disk encryption set.[patch]
        BODY = {
          "active_key": {
            "source_vault": {
              # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.KeyVault/vaults/" + VAULT_NAME + ""
              "id": VAULT_ID
            },
            "key_url": KEY_URI
            # "key_url": "https://myvmvault.vault-int.azure-int.net/keys/{key}/{key_version}"
          },
          "tags": {
            "department": "Development",
            "project": "Encryption"
          }
        }
        result = self.mgmt_client.disk_encryption_sets.begin_update(resource_group.name, DISK_ENCRYPTION_SET_NAME, BODY)
        result = result.result()

        # # Delete a disk encryption set.[delete]
        result = self.mgmt_client.disk_encryption_sets.begin_delete(resource_group.name, DISK_ENCRYPTION_SET_NAME)
        result = result.result()
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_shot(self, resource_group):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        DISK_NAME = self.get_resource_name("disknamex")
        SNAPSHOT_NAME = self.get_resource_name("snapshotx")
        IMAGE_NAME = self.get_resource_name("imagex")

        # Create an empty managed disk.[put]
        BODY = {
          "location": "eastus",
          "creation_data": {
            "create_option": "Empty"
          },
          "disk_size_gb": "200"
        }
        result = self.mgmt_client.disks.begin_create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Create a snapshot by copying a disk.
        BODY = {
          "location": "eastus",
          "creation_data": {
            "create_option": "Copy",
            "source_uri": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/disks/" + DISK_NAME
          }
        }
        result = self.mgmt_client.snapshots.begin_create_or_update(resource_group.name, SNAPSHOT_NAME, BODY)
        result = result.result()

        # Create a virtual machine image from a snapshot.[put]
        BODY = {
          "location": "eastus",
          "storage_profile": {
            "os_disk": {
              "os_type": "Linux",
              "snapshot": {
                "id": "subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/snapshots/" + SNAPSHOT_NAME
              },
              "os_state": "Generalized"
            },
            "zone_resilient": False
          },
          "hyper_v_generation": "V1"  # TODO: required
        }
        result = self.mgmt_client.images.begin_create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Get information about a snapshot.[get]
        result = self.mgmt_client.snapshots.get(resource_group.name, SNAPSHOT_NAME)

        # Get information about a virtual machine image.[get]
        result = self.mgmt_client.images.get(resource_group.name, IMAGE_NAME)

        # List all virtual machine images in a resource group.[get]
        result = self.mgmt_client.images.list_by_resource_group(resource_group.name)

        # List all snapshots in a resource group.[get]
        result = self.mgmt_client.snapshots.list_by_resource_group(resource_group.name)

        # List all virtual machine images in a subscription.[get]
        result = self.mgmt_client.images.list()

        # List all snapshots in a subscription.[get]
        result = self.mgmt_client.snapshots.list()

        # Updates tags of an Image.[patch]
        BODY = {
          # "properties": {
          #   "source_virtual_machine": {
          #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
          #   },
          #   "hyper_vgeneration": "V1"
          # },
          "tags": {
            "department": "HR"
          }
        }
        result = self.mgmt_client.images.begin_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Update a snapshot by
        BODY = {
          "creation_data": {
            "create_option": "Copy",
            "source_uri": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/disks/" + DISK_NAME
          }
        }
        result = self.mgmt_client.snapshots.begin_update(resource_group.name, SNAPSHOT_NAME, BODY)
        result = result.result()

        # Grant acess snapshot (TODO: need swagger file)
        BODY = {
          "access": "Read",
          "duration_in_seconds": "1800"
        }
        result = self.mgmt_client.snapshots.begin_grant_access(resource_group.name, SNAPSHOT_NAME, BODY)
        result = result.result()

        # Revoke access snapshot (TODO: need swagger file)
        result = self.mgmt_client.snapshots.begin_revoke_access(resource_group.name, SNAPSHOT_NAME)
        result = result.result()

        # Delete a image.  (TODO: need a swagger file)
        result = self.mgmt_client.images.begin_delete(resource_group.name, IMAGE_NAME)
        result = result.result()

        # Delete snapshot (TODO: need swagger file)
        result = self.mgmt_client.snapshots.begin_delete(resource_group.name, SNAPSHOT_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_disks(self, resource_group):

        DISK_NAME = self.get_resource_name("disknamex")

        # Create an empty managed disk.[put]
        BODY = {
          "location": "eastus",
          "creation_data": {
            "create_option": "Empty"
          },
          "disk_size_gb": "200"
        }
        result = self.mgmt_client.disks.begin_create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Get information about a managed disk.[get]
        result = self.mgmt_client.disks.get(resource_group.name, DISK_NAME)

        # List all managed disks in a resource group.[get]
        result = self.mgmt_client.disks.list_by_resource_group(resource_group.name)

        # List all managed disks in a subscription.[get]
        result = self.mgmt_client.disks.list()

        # Update disk.[patch]
        BODY = {
          "disk_size_gb": "200"
        }
        result = self.mgmt_client.disks.begin_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Grant acess diski
        BODY = {
          "access": "Read",
          "duration_in_seconds": "1800"
        }
        result = self.mgmt_client.disks.begin_grant_access(resource_group.name, DISK_NAME, BODY)
        result = result.result()

         # Revoke access disk
        result = self.mgmt_client.disks.begin_revoke_access(resource_group.name, DISK_NAME)
        result = result.result()

        # Delete disk
        result = self.mgmt_client.disks.begin_delete(resource_group.name, DISK_NAME)
        result = result.result()
