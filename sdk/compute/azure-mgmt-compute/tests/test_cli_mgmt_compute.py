# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 174
# Methods Covered : 84
# Examples Total  : 132
# Examples Tested : 132
# Coverage %      : 48.275862068965516
# ----------------------

# covered ops:
#   snapshots: 8/8
#   disks: 8/8
#   disk_encryption: 2/6
#   galleries: 6/6
#   gallery_applications: 5/5
#   gallery_application_versions: 0/5
#   gallery_images: 5/5
#   gallery_image_versions: 5/5
#   images: 6/6
#   dedicated_hosts: 5/5
#   dedicated_host_groups: 6/6
#   virtual_machines: 17/21
#   virtual_machine_size: 1/1
#   virtual_machine_run_commands: 2/2
#   virtual_machine_images: 5/5
#   virtual_machine_extensions: 5/5
#   virtual_machine_extension_images: 3/3
#   virtual_machine_scale_sets: 13/21
#   virtual_machine_scale_set_vms: 1/14
#   virtual_machine_scale_set_vm_extensions: 0/5
#   virtual_machine_scale_set_rolling_upgrades: 2/4
#   virtual_machine_scale_set_extensions: 5/5
#   usage: 1/1
#   availability_sets: 7/7
#   log_analytics: 0/2
#   operations: 1/1
#   proximity_placement_groups: 6/6
#   resource_skus: 1/1


# import json
# import urllib3
import unittest

import azure.mgmt.compute
import azure.mgmt.network
# import azure.mgmt.keyvault
# from azure.keyvault.keys import KeyClient
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )
        # self.keyvault_client = self.create_mgmt_client(
        #     azure.mgmt.keyvault.KeyVaultManagementClient
        # )
        self.network_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):
      
      azure_operation_poller = self.network_client.virtual_networks.create_or_update(
          group_name,
          network_name,
          {
              'location': location,
              'address_space': {
                  'address_prefixes': ['10.0.0.0/16']
              }
          },
      )
      result_create = azure_operation_poller.result()

      async_subnet_creation = self.network_client.subnets.create_or_update(
          group_name,
          network_name,
          subnet_name,
          {'address_prefix': '10.0.0.0/24'}
      )
      subnet_info = async_subnet_creation.result()
      
      return subnet_info

    def create_network_interface(self, group_name, location, nic_name, subnet):

        async_nic_creation = self.network_client.network_interfaces.create_or_update(
            group_name,
            nic_name,
            {
                'location': location,
                'ip_configurations': [{
                    'name': 'MyIpConfig',
                    'subnet': {
                        'id': subnet.id
                    }
                }]
            }
        )
        nic_info = async_nic_creation.result()

        return nic_info.id

    # def create_key(self, group_name, location, key_vault, tenant_id):
    #     result = self.keyvault_client.vaults.create_or_update(
    #         group_name,
    #         key_vault,
    #         {
    #             'location': location,
    #             'properties': {
    #                 'sku': {
    #                     'name': 'standard'
    #                 },
    #                 # Fake random GUID
    #                 'tenant_id': tenant_id,
    #                 'access_policies': [],
    #                 # 'create_mode': 'recover',
    #                 'enabled_for_disk_encryption': True,
    #             },
    #         }
    #     ).result()
    #     vault_url = result.properties.vault_uri
    #     vault_id = result.id

    #     credentials = self.settings.get_credentials()
    #     key_client = KeyClient(vault_url, credentials)

    #     # [START create_key]
    #     from dateutil import parser as date_parse
    #     expires_on = date_parse.parse("2050-02-02T08:00:00.000Z")

    #     key = key_client.create_key(
    #       "testkey",
    #       "RSA",
    #       size=2048,
    #       key_ops=["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"],
    #       expires_on=expires_on
    #     )
    #     return (vault_id, vault_url, key.name)


    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute(self, resource_group):

        NETWORK_NAME = "networknamexyz"
        SUBNET_NAME = "subnetxyz"
        INTERFACE_NAME = "interface_name"
        KEY_VAULT = "keyvaultxxyyzz"
        KEY_NAME = "keynamexxyyzz"

        SERVICE_NAME = "myapimrndxyz"
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        STORAGE_ACCOUNT = None
        DISK_NAME = "diskname"
        GALLERY_NAME = "galleryname"
        APPLICATION_NAME = "applicationname"
        VERSION_NAME = "1.0.0"
        IMAGE_NAME = "imagename"
        HOST_NAME = "hostname"
        HOST_GROUP_NAME = "hostgroupnamexyz"
        DISK_ENCRYPTION_SET_NAME = "diskencryptionsetname"
        SNAPSHOT_NAME = "snapshotname"
        VIRTUAL_MACHINE_NAME = "vmnamexyz"
        AVAILABILITY_SET_NAME = "availabilitysetnamexyz"
        PROXIMITY_PLACEMENT_GROUP_NAME = "proximityplacementgroupname"
        VIRTUAL_MACHINE_SCALE_SET_NAME = "virtualmachinescalesetname"
        VIRTUAL_MACHINE_EXTENSION_NAME = "virtualmachineextensionname"
        VMSS_EXTENSION_NAME = "vmssextensionname"
        INSTANCE_ID = "1"
        INSTANCE_IDS = ["1"]
        LOG_ANALYTIC_NAME = "loganalytic"

        if self.is_live:
          SUBNET = self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, NETWORK_NAME, SUBNET_NAME)
          NIC_ID = self.create_network_interface(RESOURCE_GROUP, AZURE_LOCATION, INTERFACE_NAME, SUBNET)
          # VAULT_ID, VAULT_URL, KEY_NAME = self.create_key(RESOURCE_GROUP, AZURE_LOCATION, KEY_VAULT, TENANT_ID)
        else:
          SUBNET = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + NETWORK_NAME + "/subnets/" + SUBNET_NAME
          NIC_ID = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + INTERFACE_NAME

        # Create an empty managed disk.[put]
        BODY = {
          "location": "eastus",
          "creation_data": {
            "create_option": "Empty"
          },
          "disk_size_gb": "200"
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # TODO: NEED STORAGE
        # # Create a managed disk by importing an unmanaged blob from a different subscription.[put]
        # DISK_NAME_2 = DISK_NAME + "2"
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "creation_data": {
        #       "create_option": "Import",
        #       "storage_account_id": "subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/myResourceGroup/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT,
        #       "source_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
        #     }
        #   }
        # }
        # result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME_2, BODY)
        # result = result.result()

        # TODO: NEED SNAPSHOT
        # # Create a managed disk by copying a snapshot.[put]
        # DISK_NAME_3 = DISK_NAME + "3"
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "creation_data": {
        #       "create_option": "Copy",
        #       "source_resource_id": "subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/" + SNAP_SHOT
        #     }
        #   }
        # }
        # result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME_3, BODY)
        # result = result.result()

        # TODO: UNUSE NOW
        # # Create a managed disk by importing an unmanaged blob from the same subscription.[put]
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "creation_data": {
        #       "create_option": "Import",
        #       "source_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
        #     }
        #   }
        # }
        # result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        # result = result.result()

        # Create a managed disk from an existing managed disk in the same or different subscription.[put]
        DISK_NAME_4 = DISK_NAME + "4"
        BODY = {
          "location": "eastus",
          "creation_data": {
            "create_option": "Copy",
            "source_resource_id": "subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/disks/" + DISK_NAME
          }
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME_4, BODY)
        result = result.result()

        # TODO: NEED A IMAGE
        # # Create a managed disk from a platform image.[put]
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "os_type": "Windows",
        #     "creation_data": {
        #       "create_option": "FromImage",
        #       "image_reference": {
        #         "id": "/Subscriptions/{subscriptionId}/Providers/Microsoft.Compute/Locations/uswest/Publishers/Microsoft/ArtifactTypes/VMImage/Offers/{offer}"
        #       }
        #     }
        #   }
        # }
        # result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        # result = result.result()

        # Create a managed upload disk.[put]
        DISK_NAME_5 = DISK_NAME + '5'
        BODY = {
          "location": "eastus",
          "creation_data": {
            "create_option": "Upload",
            "upload_size_bytes": "10737418752"
          }
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME_5, BODY)
        result = result.result()

        # TODO: New example not in swagger. (doing)
        # Create a snapshot by copying a disk.
        BODY = {
          "location": "eastus",
          "creation_data": {
            "create_option": "Copy",
            "source_uri": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/disks/" + DISK_NAME
          }
        }
        result = self.mgmt_client.snapshots.create_or_update(resource_group.name, SNAPSHOT_NAME, BODY)
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
          "hyper_vgeneration": "V1"  # TODO: required
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        """
        # Create a virtual machine image from a managed disk with DiskEncryptionSet resource.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "storage_profile": {
              "os_disk": {
                "os_type": "Linux",
                "managed_disk": {
                  "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/myManagedDisk"
                },
                "disk_encryption_set": {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME + ""
                },
                "os_state": "Generalized"
              }
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Create a virtual machine image from an existing virtual machine.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "source_virtual_machine": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Create a virtual machine image that includes a data disk from a blob.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "storage_profile": {
              "os_disk": {
                "os_type": "Linux",
                "blob_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd",
                "os_state": "Generalized"
              },
              "data_disks": [
                {
                  "lun": "1",
                  "blob_uri": "https://mystorageaccount.blob.core.windows.net/dataimages/dataimage.vhd"
                }
              ],
              "zone_resilient": False
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Create a virtual machine image that includes a data disk from a snapshot.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "storage_profile": {
              "os_disk": {
                "os_type": "Linux",
                "snapshot": {
                  "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
                },
                "os_state": "Generalized"
              },
              "data_disks": [
                {
                  "lun": "1",
                  "snapshot": {
                    "id": "subscriptions/{subscriptionId}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot2"
                  }
                }
              ],
              "zone_resilient": True
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Create a virtual machine image that includes a data disk from a managed disk.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "storage_profile": {
              "os_disk": {
                "os_type": "Linux",
                "managed_disk": {
                  "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/myManagedDisk"
                },
                "os_state": "Generalized"
              },
              "data_disks": [
                {
                  "lun": "1",
                  "managed_disk": {
                    "id": "subscriptions/{subscriptionId}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/myManagedDisk2"
                  }
                }
              ],
              "zone_resilient": False
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Create a virtual machine image from a blob with DiskEncryptionSet resource.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "storage_profile": {
              "os_disk": {
                "os_type": "Linux",
                "blob_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd",
                "disk_encryption_set": {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME + ""
                },
                "os_state": "Generalized"
              }
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Create a virtual machine image from a managed disk.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "storage_profile": {
              "os_disk": {
                "os_type": "Linux",
                "managed_disk": {
                  "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/myManagedDisk"
                },
                "os_state": "Generalized"
              },
              "zone_resilient": True
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Create a virtual machine image from a snapshot with DiskEncryptionSet resource.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "storage_profile": {
              "os_disk": {
                "os_type": "Linux",
                "snapshot": {
                  "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
                },
                "disk_encryption_set": {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME + ""
                },
                "os_state": "Generalized"
              }
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Create a virtual machine image from a blob.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "storage_profile": {
              "os_disk": {
                "os_type": "Linux",
                "blob_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd",
                "os_state": "Generalized"
              },
              "zone_resilient": True
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()
        """

        # Create or update a simple gallery.[put]
        BODY = {
          "location": "eastus",
          "description": "This is the gallery description."
        }
        result = self.mgmt_client.galleries.create_or_update(resource_group.name, GALLERY_NAME, BODY)
        result = result.result()

        # TODO: NNED BLOB
        # # Create a snapshot by importing an unmanaged blob from the same subscription.[put]
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "creation_data": {
        #       "create_option": "Import",
        #       "source_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
        #     }
        #   }
        # }
        # result = self.mgmt_client.snapshots.create_or_update(resource_group.name, SNAPSHOT_NAME, BODY)
        # result = result.result()

        # TODO: TWO SUBCRIPTION
        # # Create a snapshot by importing an unmanaged blob from a different subscription.[put]
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "creation_data": {
        #       "create_option": "Import",
        #       "storage_account_id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Storage/storageAccounts/myStorageAccount",
        #       "source_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
        #     }
        #   }
        # }
        # result = self.mgmt_client.snapshots.create_or_update(resource_group.name, SNAPSHOT_NAME, BODY)
        # result = result.result()

        # TODO: NEED ANOTHER SNAPSHOT
        # # Create a snapshot from an existing snapshot in the same or a different subscription.[put]
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "creation_data": {
        #       "create_option": "Copy",
        #       "source_resource_id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot1"
        #     }
        #   }
        # }
        # result = self.mgmt_client.snapshots.create_or_update(resource_group.name, SNAPSHOT_NAME, BODY)
        # result = result.result()

        # Create or update a dedicated host group.[put]
        BODY = {
          "location": "eastus",
          "tags": {
            "department": "finance"
          },
          "zones": [
            "1"
          ],
          "platform_fault_domain_count": "3"
        }
        result = self.mgmt_client.dedicated_host_groups.create_or_update(resource_group.name, HOST_GROUP_NAME, BODY)

        """
        # Create a platform-image vm with unmanaged os and data disks.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_D2_v2"
            },
            "storage_profile": {
              "image_reference": {
                "sku": "2016-Datacenter",
                "publisher": "MicrosoftWindowsServer",
                "version": "latest",
                "offer": "WindowsServer"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "vhd": {
                  "uri": "http://{existing-storage-account-name}.blob.core.windows.net/{existing-container-name}/myDisk.vhd"
                },
                "create_option": "FromImage",
                "name": "myVMosdisk"
              },
              "data_disks": [
                {
                  "disk_size_gb": "1023",
                  "create_option": "Empty",
                  "lun": "0",
                  "vhd": {
                    "uri": "http://{existing-storage-account-name}.blob.core.windows.net/{existing-container-name}/myDisk0.vhd"
                  }
                },
                {
                  "disk_size_gb": "1023",
                  "create_option": "Empty",
                  "lun": "1",
                  "vhd": {
                    "uri": "http://{existing-storage-account-name}.blob.core.windows.net/{existing-container-name}/myDisk1.vhd"
                  }
                }
              ]
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "admin_password": "{your-password}"
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()
        """

        """
        # Create a vm from a custom image.[put]
        BODY = {
          "location": "eastus",
          "hardware_profile": {
            "vm_size": "Standard_D1_v2"
          },
          "storage_profile": {
            "image_reference": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
            },
            "os_disk": {
              "caching": "ReadWrite",
              "managed_disk": {
                "storage_account_type": "Standard_LRS"
              },
              "name": "myVMosdisk",
              "create_option": "FromImage"
            }
          },
          "os_profile": {
            "admin_username": "testuser",
            "computer_name": "myVM",
            "admin_password": "Aa!1()_="
          },
          "network_profile": {
            "network_interfaces": [
              {
                # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                "id": NIC_ID,
                "properties": {
                  "primary": True
                }
              }
            ]
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()
        """

        # Create a vm with empty data disks.[put]
        BODY = {
          "location": "eastus",
          "hardware_profile": {
            "vm_size": "Standard_D2_v2"
          },
          "storage_profile": {
            "image_reference": {
              "sku": "2016-Datacenter",
              "publisher": "MicrosoftWindowsServer",
              "version": "latest",
              "offer": "WindowsServer"
            },
            "os_disk": {
              "caching": "ReadWrite",
              "managed_disk": {
                "storage_account_type": "Standard_LRS"
              },
              "name": "myVMosdisk",
              "create_option": "FromImage"
            },
            "data_disks": [
              {
                "disk_size_gb": "1023",
                "create_option": "Empty",
                "lun": "0"
              },
              {
                "disk_size_gb": "1023",
                "create_option": "Empty",
                "lun": "1"
              }
            ]
          },
          "os_profile": {
            "admin_username": "testuser",
            "computer_name": "myVM",
            "admin_password": "Aa1!zyx_",
            "windows_configuration": {
              "enable_automatic_updates": True  # need automatic update for reimage
            }
          },
          "network_profile": {
            "network_interfaces": [
              {
                # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NIC_ID + "",
                "id": NIC_ID,
                "properties": {
                  "primary": True
                }
              }
            ]
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        """
        # Create a custom-image vm from an unmanaged generalized os image.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_D1_v2"
            },
            "storage_profile": {
              "os_disk": {
                "name": "myVMosdisk",
                "image": {
                  "uri": "http://{existing-storage-account-name}.blob.core.windows.net/{existing-container-name}/{existing-generalized-os-image-blob-name}.vhd"
                },
                "os_type": "Windows",
                "create_option": "FromImage",
                "caching": "ReadWrite",
                "vhd": {
                  "uri": "http://{existing-storage-account-name}.blob.core.windows.net/{existing-container-name}/myDisk.vhd"
                }
              }
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "admin_password": "{your-password}"
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Create a vm in an availability set.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_D1_v2"
            },
            "storage_profile": {
              "image_reference": {
                "sku": "2016-Datacenter",
                "publisher": "MicrosoftWindowsServer",
                "version": "latest",
                "offer": "WindowsServer"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Standard_LRS"
                },
                "name": "myVMosdisk",
                "create_option": "FromImage"
              }
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "admin_password": "{your-password}"
            },
            "availability_set": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/availabilitySets/" + AVAILABILITY_SET_NAME + ""
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Create a vm with premium storage.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_D1_v2"
            },
            "storage_profile": {
              "image_reference": {
                "sku": "2016-Datacenter",
                "publisher": "MicrosoftWindowsServer",
                "version": "latest",
                "offer": "WindowsServer"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Premium_LRS"
                },
                "name": "myVMosdisk",
                "create_option": "FromImage"
              }
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "admin_password": "{your-password}"
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Create a vm with ssh authentication.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_D1_v2"
            },
            "storage_profile": {
              "image_reference": {
                "sku": "{image_sku}",
                "publisher": "{image_publisher}",
                "version": "latest",
                "offer": "{image_offer}"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Standard_LRS"
                },
                "name": "myVMosdisk",
                "create_option": "FromImage"
              }
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "linux_configuration": {
                "ssh": {
                  "public_keys": [
                    {
                      "path": "/home/{your-username}/.ssh/authorized_keys",
                      "key_data": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCeClRAk2ipUs/l5voIsDC5q9RI+YSRd1Bvd/O+axgY4WiBzG+4FwJWZm/mLLe5DoOdHQwmU2FrKXZSW4w2sYE70KeWnrFViCOX5MTVvJgPE8ClugNl8RWth/tU849DvM9sT7vFgfVSHcAS2yDRyDlueii+8nF2ym8XWAPltFVCyLHRsyBp5YPqK8JFYIa1eybKsY3hEAxRCA+/7bq8et+Gj3coOsuRmrehav7rE6N12Pb80I6ofa6SM5XNYq4Xk0iYNx7R3kdz0Jj9XgZYWjAHjJmT0gTRoOnt6upOuxK7xI/ykWrllgpXrCPu3Ymz+c+ujaqcxDopnAl2lmf69/J1"
                    }
                  ]
                },
                "disable_password_authentication": True
              }
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Create a vm with password authentication.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_D1_v2"
            },
            "storage_profile": {
              "image_reference": {
                "sku": "2016-Datacenter",
                "publisher": "MicrosoftWindowsServer",
                "version": "latest",
                "offer": "WindowsServer"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Standard_LRS"
                },
                "name": "myVMosdisk",
                "create_option": "FromImage"
              }
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "admin_password": "{your-password}"
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Create a vm with ephemeral os disk.[put]
        BODY = {
          "location": "eastus",
          "plan": {
            "publisher": "microsoft-ads",
            "product": "windows-data-science-vm",
            "name": "windows2016"
          },
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_DS1_v2"
            },
            "storage_profile": {
              "image_reference": {
                "sku": "windows2016",
                "publisher": "microsoft-ads",
                "version": "latest",
                "offer": "windows-data-science-vm"
              },
              "os_disk": {
                "caching": "ReadOnly",
                "diff_disk_settings": {
                  "option": "Local"
                },
                "managed_disk": {
                  "storage_account_type": "Standard_LRS"
                },
                "create_option": "FromImage",
                "name": "myVMosdisk"
              }
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "admin_password": "{your-password}"
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Create a vm with DiskEncryptionSet resource id in the os disk and data disk.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_D1_v2"
            },
            "storage_profile": {
              "image_reference": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Standard_LRS",
                  "disk_encryption_set": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME + ""
                  }
                },
                "name": "myVMosdisk",
                "create_option": "FromImage"
              },
              "data_disks": [
                {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS",
                    "disk_encryption_set": {
                      "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME + ""
                    }
                  },
                  "disk_size_gb": "1023",
                  "create_option": "Empty",
                  "lun": "0"
                },
                {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/disks/" + DISK_NAME + "",
                    "storage_account_type": "Standard_LRS",
                    "disk_encryption_set": {
                      "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME + ""
                    }
                  },
                  "disk_size_gb": "1023",
                  "create_option": "Attach",
                  "lun": "1"
                }
              ]
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "admin_password": "{your-password}"
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Create a vm with a marketplace image plan.[put]
        BODY = {
          "location": "eastus",
          "plan": {
            "publisher": "microsoft-ads",
            "product": "windows-data-science-vm",
            "name": "windows2016"
          },
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_D1_v2"
            },
            "storage_profile": {
              "image_reference": {
                "sku": "windows2016",
                "publisher": "microsoft-ads",
                "version": "latest",
                "offer": "windows-data-science-vm"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Standard_LRS"
                },
                "name": "myVMosdisk",
                "create_option": "FromImage"
              }
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "admin_password": "{your-password}"
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Create a vm with boot diagnostics.[put]
        BODY = {
          "location": "eastus",
          "properties": {
            "hardware_profile": {
              "vm_size": "Standard_D1_v2"
            },
            "storage_profile": {
              "image_reference": {
                "sku": "2016-Datacenter",
                "publisher": "MicrosoftWindowsServer",
                "version": "latest",
                "offer": "WindowsServer"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Standard_LRS"
                },
                "name": "myVMosdisk",
                "create_option": "FromImage"
              }
            },
            "network_profile": {
              "network_interfaces": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                  "properties": {
                    "primary": True
                  }
                }
              ]
            },
            "os_profile": {
              "admin_username": "{your-username}",
              "computer_name": "myVM",
              "admin_password": "{your-password}"
            },
            "diagnostics_profile": {
              "boot_diagnostics": {
                "storage_uri": "http://{existing-storage-account-name}.blob.core.windows.net",
                "enabled": True
              }
            }
          }
        }
        result = self.mgmt_client.virtual_machines.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()
        """

        # Create an availability set.[put]
        BODY = {
          "location": "eastus",
          "platform_fault_domain_count": "2",
          "platform_update_domain_count": "20"
        }
        result = self.mgmt_client.availability_sets.create_or_update(resource_group.name, AVAILABILITY_SET_NAME, BODY)

        # TODO: NEED KEY VAULT
        # Create a disk encryption set.[put]
        # BODY = {
        #   "location": "eastus",
        #   "identity": {
        #     "type": "SystemAssigned"
        #   },
        #   "active_key": {
        #     "source_vault": {
        #       # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.KeyVault/vaults/" + VAULT_NAME + ""
        #       "id": VAULT_ID
        #     },
        #     # "key_url": "https://myvmvault.vault-int.azure-int.net/keys/{key}"
        #     "key_url": VAULT_URI + "/keys/" + KEY_NAME
        #   }
        # }
        # result = self.mgmt_client.disk_encryption_sets.create_or_update(resource_group.name, DISK_ENCRYPTION_SET_NAME, BODY)
        # result = result.result()

        # Create or update a simple gallery image.[put]
        BODY = {
          "location": "eastus",
          "os_type": "Windows",
          "os_state": "Generalized",
          "hyper_vgeneration": "V1",
          "identifier": {
            "publisher": "myPublisherName",
            "offer": "myOfferName",
            "sku": "mySkuName"
          }
        }
        result = self.mgmt_client.gallery_images.create_or_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, BODY)
        result = result.result()

        # Create or update a dedicated host .[put]
        BODY = {
          "location": "eastus",
          "tags": {
            "department": "HR"
          },
          "platform_fault_domain": "1",
          "sku": {
            "name": "DSv3-Type1"
          }
        }
        result = self.mgmt_client.dedicated_hosts.create_or_update(resource_group.name, HOST_GROUP_NAME, HOST_NAME, BODY)
        result = result.result()

        """
        # Create/Update Container Service[put]
        BODY = {
          "location": "location1"
        }
        result = self.mgmt_client.container_services.create_or_update(resource_group.name, CONTAINER_SERVICE_NAME, BODY)
        result = result.result()

        # Create a scale set with virtual machines in different zones.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "2",
            "name": "Standard_A1_v2"
          },
          "location": "centralus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage",
                  "disk_size_gb": "512"
                },
                "data_disks": [
                  {
                    "disk_size_gb": "1023",
                    "create_option": "Empty",
                    "lun": "0"
                  },
                  {
                    "disk_size_gb": "1023",
                    "create_option": "Empty",
                    "lun": "1"
                  }
                ]
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Automatic"
            }
          },
          "zones": [
            "1",
            "3"
          ]
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a custom-image scale set from an unmanaged generalized os image.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "os_disk": {
                  "caching": "ReadWrite",
                  "image": {
                    "uri": "http://{existing-storage-account-name}.blob.core.windows.net/{existing-container-name}/{existing-generalized-os-image-blob-name}.vhd"
                  },
                  "create_option": "FromImage",
                  "name": "osDisk"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with ephemeral os disks.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_DS1_v2"
          },
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "windows2016",
                  "publisher": "microsoft-ads",
                  "version": "latest",
                  "offer": "windows-data-science-vm"
                },
                "os_disk": {
                  "caching": "ReadOnly",
                  "diff_disk_settings": {
                    "option": "Local"
                  },
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          },
          "plan": {
            "publisher": "microsoft-ads",
            "product": "windows-data-science-vm",
            "name": "windows2016"
          },
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with ssh authentication.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "linux_configuration": {
                  "ssh": {
                    "public_keys": [
                      {
                        "path": "/home/{your-username}/.ssh/authorized_keys",
                        "key_data": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCeClRAk2ipUs/l5voIsDC5q9RI+YSRd1Bvd/O+axgY4WiBzG+4FwJWZm/mLLe5DoOdHQwmU2FrKXZSW4w2sYE70KeWnrFViCOX5MTVvJgPE8ClugNl8RWth/tU849DvM9sT7vFgfVSHcAS2yDRyDlueii+8nF2ym8XWAPltFVCyLHRsyBp5YPqK8JFYIa1eybKsY3hEAxRCA+/7bq8et+Gj3coOsuRmrehav7rE6N12Pb80I6ofa6SM5XNYq4Xk0iYNx7R3kdz0Jj9XgZYWjAHjJmT0gTRoOnt6upOuxK7xI/ykWrllgpXrCPu3Ymz+c+ujaqcxDopnAl2lmf69/J1"
                      }
                    ]
                  },
                  "disable_password_authentication": True
                }
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with premium storage.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Premium_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()
        """

        # Create a scale set with empty data disks on each vm.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "2",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "overprovision": True,
          "virtual_machine_profile": {
            "storage_profile": {
              # "image_reference": {
              #   "sku": "2016-Datacenter",
              #   "publisher": "MicrosoftWindowsServer",
              #   "version": "latest",
              #   "offer": "WindowsServer"
              # },
              "image_reference": {
                  "offer": "UbuntuServer",
                  "publisher": "Canonical",
                  "sku": "18.04-LTS",
                  # "urn": "Canonical:UbuntuServer:18.04-LTS:latest",
                  # "urnAlias": "UbuntuLTS",
                  "version": "latest"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Standard_LRS"
                },
                "create_option": "FromImage",
                "disk_size_gb": "512"
              },
              # "data_disks": [
              #   {
              #     "disk_size_gb": "1023",
              #     "create_option": "Empty",
              #     "lun": "0"
              #   },
              #   {
              #     "disk_size_gb": "1023",
              #     "create_option": "Empty",
              #     "lun": "1"
              #   }
              # ]
            },
            "os_profile": {
              "computer_name_prefix": "testPC",
              "admin_username": "testuser",
              "admin_password": "Aa!1()-xyz"
            },
            "network_profile": {
              "network_interface_configurations": [
                {
                  "name": "testPC",
                  "primary": True,
                  "enable_ipforwarding": True,
                  "ip_configurations": [
                    {
                      "name": "testPC",
                      "properties": {
                        "subnet": {
                          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                        }
                      }
                    }
                  ]
                }
              ]
            }
          },
          "upgrade_policy": {
            "mode": "Manual"
          },
          "upgrade_mode": "Manual"
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        """
        # Create a scale set with an azure load balancer.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            },
                            "public_ip_address_configuration": {
                              "name": "{vmss-name}",
                              "properties": {
                                "public_ip_address_version": "IPv4"
                              }
                            },
                            "load_balancer_inbound_nat_pools": [
                              {
                                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "/inboundNatPools/" + INBOUND_NAT_POOL_NAME + ""
                              }
                            ],
                            "load_balancer_backend_address_pools": [
                              {
                                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "/backendAddressPools/" + BACKEND_ADDRESS_POOL_NAME + ""
                              }
                            ]
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with boot diagnostics.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "diagnostics_profile": {
                "boot_diagnostics": {
                  "storage_uri": "http://{existing-storage-account-name}.blob.core.windows.net",
                  "enabled": True
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with terminate scheduled events enabled.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              },
              "scheduled_events_profile": {
                "terminate_notification_profile": {
                  "enable": True,
                  "not_before_timeout": "PT5M"
                }
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with automatic repairs enabled[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            },
            "automatic_repairs_policy": {
              "enabled": True,
              "grace_period": "PT30M"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with a marketplace image plan.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "windows2016",
                  "publisher": "microsoft-ads",
                  "version": "latest",
                  "offer": "windows-data-science-vm"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          },
          "plan": {
            "publisher": "microsoft-ads",
            "product": "windows-data-science-vm",
            "name": "windows2016"
          },
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set from a custom image.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with DiskEncryptionSet resource in os disk and data disk.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_DS1_v2"
          },
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS",
                    "disk_encryption_set": {
                      "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME + ""
                    }
                  },
                  "create_option": "FromImage"
                },
                "data_disks": [
                  {
                    "caching": "ReadWrite",
                    "managed_disk": {
                      "storage_account_type": "Standard_LRS",
                      "disk_encryption_set": {
                        "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME + ""
                      }
                    },
                    "disk_size_gb": "1023",
                    "create_option": "Empty",
                    "lun": "0"
                  }
                ]
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          },
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a platform-image scale set with unmanaged os disks.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "create_option": "FromImage",
                  "name": "osDisk",
                  "vhd_containers": [
                    "http://{existing-storage-account-name-0}.blob.core.windows.net/vhdContainer",
                    "http://{existing-storage-account-name-1}.blob.core.windows.net/vhdContainer",
                    "http://{existing-storage-account-name-2}.blob.core.windows.net/vhdContainer",
                    "http://{existing-storage-account-name-3}.blob.core.windows.net/vhdContainer",
                    "http://{existing-storage-account-name-4}.blob.core.windows.net/vhdContainer"
                  ]
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with password authentication.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with an azure application gateway.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "eastus",
          "properties": {
            "overprovision": True,
            "virtual_machine_profile": {
              "storage_profile": {
                "image_reference": {
                  "sku": "2016-Datacenter",
                  "publisher": "MicrosoftWindowsServer",
                  "version": "latest",
                  "offer": "WindowsServer"
                },
                "os_disk": {
                  "caching": "ReadWrite",
                  "managed_disk": {
                    "storage_account_type": "Standard_LRS"
                  },
                  "create_option": "FromImage"
                }
              },
              "os_profile": {
                "computer_name_prefix": "{vmss-name}",
                "admin_username": "{your-username}",
                "admin_password": "{your-password}"
              },
              "network_profile": {
                "network_interface_configurations": [
                  {
                    "name": "{vmss-name}",
                    "properties": {
                      "primary": True,
                      "enable_ipforwarding": True,
                      "ip_configurations": [
                        {
                          "name": "{vmss-name}",
                          "properties": {
                            "application_gateway_backend_address_pools": [
                              {
                                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/backendAddressPools/" + BACKEND_ADDRESS_POOL_NAME + ""
                              }
                            ],
                            "subnet": {
                              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                            }
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            "upgrade_policy": {
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()
        """

        # Create or Update a proximity placement group.[put]
        BODY = {
          "location": "eastus",
          "proximity_placement_group_type": "Standard"
        }
        result = self.mgmt_client.proximity_placement_groups.create_or_update(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME, BODY)

        # Create or update a simple gallery Application.[put]
        BODY = {
          "location": "eastus",
          "description": "This is the gallery application description.",
          "eula": "This is the gallery application EULA.",
          # "privacy_statement_uri": "myPrivacyStatementUri}",
          # "release_note_uri": "myReleaseNoteUri",
          "supported_os_type": "Windows"
        }
        result = self.mgmt_client.gallery_applications.create_or_update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, BODY)
        result = result.result()

        # Create or update a simple Gallery Image Version using snapshots as a source.[put]
        BODY = {
          "location": "eastus",
          "publishing_profile": {
            "target_regions": [
              # {
              #   "name": "eastus",
              #   "regional_replica_count": "1",
              #   "encryption": {
              #     "os_disk_image": {
              #       "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + ""
              #     },
              #     "data_disk_images": [
              #       {
              #         "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + "",
              #         "lun": "1"
              #       }
              #     ]
              #   }
              # },
              {
                "name": "East US",
                "regional_replica_count": "2",
                "storage_account_type": "Standard_ZRS"
              }
            ]
          },
          "storage_profile": {
            "os_disk_image": {
              "source": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/snapshots/" + SNAPSHOT_NAME + ""
              },
              "host_caching": "ReadOnly"
            },
            # "data_disk_images": [
            #   {
            #     "source": {
            #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/snapshots/" + SNAPSHOT_NAME + ""
            #     },
            #     "lun": "1",
            #     "host_caching": "None"
            #   }
            # ]
          }
        }
        result = self.mgmt_client.gallery_image_versions.create_or_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME, BODY)
        result = result.result()

        # Create virtual machine extension (TODO: need swagger file)
        BODY = {
          "location": "eastus",
          "auto_upgrade_minor_version": True,
          "publisher": "Microsoft.Azure.NetworkWatcher",
          "virtual_machine_extension_type": "NetworkWatcherAgentWindows",
          "type_handler_version": "1.4",
        }
        result = self.mgmt_client.virtual_machine_extensions.create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME, BODY)

        # Create virtual machine sacle set extension (TODO: need swagger file)
        BODY = {
          "location": "eastus",
          "auto_upgrade_minor_version": True,
          "publisher": "Microsoft.Azure.NetworkWatcher",
          "type1": "NetworkWatcherAgentWindows",
          "type_handler_version": "1.4",
        }
        result = self.mgmt_client.virtual_machine_scale_set_extensions.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VMSS_EXTENSION_NAME, BODY)

        # TODO: need image
        # # Create or update a simple Gallery Image Version (Managed Image as source).[put]
        # BODY = {
        #   "location": "eastus",
        #   "publishing_profile": {
        #     "target_regions": [
        #       # {
        #       #   "name": "eastus",
        #       #   "regional_replica_count": "1",
        #       #   "encryption": {
        #       #     "os_disk_image": {
        #       #       "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + ""
        #       #     },
        #       #     "data_disk_images": [
        #       #       {
        #       #         "lun": "0",
        #       #         "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + ""
        #       #       },
        #       #       {
        #       #         "lun": "1",
        #       #         "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + ""
        #       #       }
        #       #     ]
        #       #   }
        #       # },
        #       {
        #         "name": "East US",
        #         "regional_replica_count": "2",
        #         "storage_account_type": "Standard_ZRS"
        #       }
        #     ]
        #   },
        #   "storage_profile": {
        #     "source": {
        #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
        #     }
        #   }
        # }
        # result = self.mgmt_client.gallery_image_versions.create_or_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME, BODY)
        # result = result.result()

        # TODO: NEED STORAGE ACCOUNT
        # # Create or update a simple gallery Application Version.[put]
        # BODY = {
        #   "location": "eastus",
        #   "publishing_profile": {
        #     "source": {
        #       "file_name": "package.zip",
        #       "media_link": "https://mystorageaccount.blob.core.windows.net/mycontainer/package.zip?{sasKey}"
        #     },
        #     "target_regions": [
        #       {
        #         "name": "eastus",
        #         "regional_replica_count": "1",
        #         "storage_account_type": "Standard_LRS"
        #       }
        #     ],
        #     "replica_count": "1",
        #     "end_of_life_date": "2019-07-01T07:00:00Z",
        #     "storage_account_type": "Standard_LRS"
        #   }
        # }
        # result = self.mgmt_client.gallery_application_versions.create_or_update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME, BODY)
        # result = result.result()

        # # TODO:need finish
        # # Create VirtualMachineScaleSet VM extension.[put]
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "auto_upgrade_minor_version": True,
        #     "publisher": "extPublisher",
        #     "type": "extType",
        #     "type_handler_version": "1.2",
        #     "settings": {
        #       "user_name": "xyz@microsoft.com"
        #     }
        #   }
        # }
        # result = self.mgmt_client.virtual_machine_scale_set_vmextensions.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, EXTENSION_NAME, BODY)
        # result = result.result()

        # # TODO:need finish
        # # Get VirtualMachineScaleSet VM extension.[get]
        # result = self.mgmt_client.virtual_machine_scale_set_vmextensions.get(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, EXTENSION_NAME)

        # # TODO:need finish
        # # List extensions in Vmss instance.[get]
        # result = self.mgmt_client.virtual_machine_scale_set_vmextensions.list(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME)

        # # TODO:need finish
        # # Get a gallery Application Version with replication status.[get]
        # result = self.mgmt_client.gallery_application_versions.get(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME)

        # # TODO:need finish
        # # Get a gallery Application Version.[get]
        # result = self.mgmt_client.gallery_application_versions.get(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME)

        # # Get a gallery Image Version with snapshots as a source.[get]
        # result = self.mgmt_client.gallery_image_versions.get(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)

        # # Get a gallery Image Version with replication status.[get]
        # result = self.mgmt_client.gallery_image_versions.get(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)

        # Get a gallery Image Version.[get]
        result = self.mgmt_client.gallery_image_versions.get(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)

        # TODO:need finish
        # # List gallery Application Versions in a gallery Application Definition.[get]
        # result = self.mgmt_client.gallery_application_versions.list_by_gallery_application(resource_group.name, GALLERY_NAME, APPLICATION_NAME)

        # Get a gallery Application.[get]
        result = self.mgmt_client.gallery_applications.get(resource_group.name, GALLERY_NAME, APPLICATION_NAME)

        # Get a proximity placement group.[get]
        result = self.mgmt_client.proximity_placement_groups.get(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME)

        # List gallery Image Versions in a gallery Image Definition.[get]
        result = self.mgmt_client.gallery_image_versions.list_by_gallery_image(resource_group.name, GALLERY_NAME, IMAGE_NAME)

        # Get Virtual Machine Instance View.[get]
        result = self.mgmt_client.virtual_machines.instance_view(resource_group.name, VIRTUAL_MACHINE_NAME)

        # Get Virtual Machine Image (TODO: need swagger file)
        PUBLISHER_NAME = "MicrosoftWindowsServer"
        OFFER = "WindowsServer"
        SKUS = "2019-Datacenter"
        VERSION = "2019.0.20190115" 
        result = self.mgmt_client.virtual_machine_images.get(AZURE_LOCATION, PUBLISHER_NAME, OFFER, SKUS, VERSION)

        # Get Virtual Machine Extension Image (TODO: neet swagger file)
        EXTENSION_PUBLISHER_NAME = "Microsoft.Compute"
        EXTENSION_IMAGE_TYPE = "VMAccessAgent"
        EXTENSION_IMAGE_VERSION = "1.0.2"
        result = self.mgmt_client.virtual_machine_extension_images.get(AZURE_LOCATION, EXTENSION_PUBLISHER_NAME, EXTENSION_IMAGE_TYPE, EXTENSION_IMAGE_VERSION)

        # TODO: dont belong here
        # Get Container Service[get]
        # result = self.mgmt_client.container_services.get(resource_group.name, CONTAINER_SERVICE_NAME)

        # Get a dedicated host.[get]
        result = self.mgmt_client.dedicated_hosts.get(resource_group.name, HOST_GROUP_NAME, HOST_NAME)

        # Get a gallery image.[get]
        result = self.mgmt_client.gallery_images.get(resource_group.name, GALLERY_NAME, IMAGE_NAME)

        # Lists all available virtual machine sizes to which the specified virtual machine can be resized[get]
        result = self.mgmt_client.virtual_machines.list_available_sizes(resource_group.name, VIRTUAL_MACHINE_NAME)

        # # Get information about a disk encryption set.[get]
        # result = self.mgmt_client.disk_encryption_sets.get(resource_group.name, DISK_ENCRYPTION_SET_NAME)

        # Get a Virtual Machine.[get]
        result = self.mgmt_client.virtual_machines.get(resource_group.name, VIRTUAL_MACHINE_NAME)

        # Get a virtual machine scale sets (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.get(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # Get virtual machine scale set os upgrade history (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.get_os_upgrade_history(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # Get instance view of virtual machine scale set (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.get_instance_view(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # Get virtual machine extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extensions.get(resource_group.name, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME)

        # Get virtual machine scale set extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_set_extensions.get(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VMSS_EXTENSION_NAME)
        
        # Get VMSS vm extension (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vm_extensions.get(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID, VIRTUAL_MACHINE_EXTENSION_NAME)

        # List VMSS vm extensions (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vm_extensions.list(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)

        # TODO: it has a bug that doesn't send request and always returns [].
        # List vitual machine scale set vms (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_set_vms.list(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        # INSTANCE_ID_1 = result.current_page[0].instance_id
        # INSTANCE_ID_2 = result.current_page[1].instance_id
        # INSTANCE_ID = INSTANCE_ID_1

        # Get virtual machine scale set vm instance view (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.get_instance_view(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)

        # Get virtual machine scale set vm (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.get(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # INSTANCE_VM_1 = result

        # Create VMSS vm extension (TODO: need swagger file)
        # BODY = {
        #   "location": "eastus",
        #   "auto_upgrade_minor_version": True,
        #   "publisher": "Microsoft.Azure.NetworkWatcher",
        #   "virtual_machine_extension_type": "NetworkWatcherAgentWindows",
        #   "type_handler_version": "1.4",
        # }
        # result = self.mgmt_client.virtual_machine_scale_set_vm_extensions.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID, VIRTUAL_MACHINE_EXTENSION_NAME, BODY)
        # result = result.result()

        # Llist virtual machine extensions (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extensions.list(resource_group.name, VIRTUAL_MACHINE_NAME)

        # List virtual machine scale set extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_set_extensions.list(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # List Virtual Machine images (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_images.list(AZURE_LOCATION, PUBLISHER_NAME, OFFER, SKUS)

        # List Virtual Machine image offers (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_images.list_offers(AZURE_LOCATION, PUBLISHER_NAME)

        # List Virtual Machine image publishers (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_images.list_publishers(AZURE_LOCATION)

        # List Virtual Machine image skus (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_images.list_skus(AZURE_LOCATION, PUBLISHER_NAME, OFFER)

        # List Virtual Machine extension image types (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extension_images.list_types(AZURE_LOCATION, EXTENSION_PUBLISHER_NAME)

        # # List Virtual Machine extension image versions (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extension_images.list_versions(AZURE_LOCATION, EXTENSION_PUBLISHER_NAME, EXTENSION_IMAGE_TYPE)

        # List gallery Applications in a gallery.[get]
        result = self.mgmt_client.gallery_applications.list_by_gallery(resource_group.name, GALLERY_NAME)

        # List gallery images in a gallery.[get]
        result = self.mgmt_client.gallery_images.list_by_gallery(resource_group.name, GALLERY_NAME)

        # Get a dedicated host group.[get]
        result = self.mgmt_client.dedicated_host_groups.get(resource_group.name, HOST_GROUP_NAME)

        # Get information about a snapshot.[get]
        result = self.mgmt_client.snapshots.get(resource_group.name, SNAPSHOT_NAME)

        # Get a gallery.[get]
        result = self.mgmt_client.galleries.get(resource_group.name, GALLERY_NAME)

        # VirtualMachineRunCommandGet[get]
        RUN_COMMAND_NAME = "RunPowerShellScript"
        result = self.mgmt_client.virtual_machine_run_commands.get(AZURE_LOCATION, RUN_COMMAND_NAME)

        # TODO: dont belong here
        # # List Container Services by Resource Group[get]
        # result = self.mgmt_client.container_services.list_by_resource_group(resource_group.name)

        # List proximity placement groups in a resource group.[get]
        result = self.mgmt_client.proximity_placement_groups.list_by_resource_group(resource_group.name)

        # Get information about a virtual machine image.[get]
        result = self.mgmt_client.images.get(resource_group.name, IMAGE_NAME)

        # Get information about a managed disk.[get]
        result = self.mgmt_client.disks.get(resource_group.name, DISK_NAME)

        # Get availability set (TODO: need swagger file)
        result = self.mgmt_client.availability_sets.get(resource_group.name, AVAILABILITY_SET_NAME)

        # TODO: The entity was not found in this Azure location.
        # Get virtual machine scale set latest rolling upgrade (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_rolling_upgrades.get_latest(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # List all disk encryption sets in a resource group.[get]
        result = self.mgmt_client.disk_encryption_sets.list_by_resource_group(resource_group.name)

        # List virtual machine scale sets in a resource group (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.list(resource_group.name)

        # List all virtual machine scale sets (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.list_all()

        # List virtual machine scale sets skus (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.list_skus(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # List the virtual machines (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.list(resource_group.name)

        # List all virtual machines (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.list_all()

        # Lists all the virtual machines under the specified subscription for the specified location.[get]
        result = self.mgmt_client.virtual_machines.list_by_location(AZURE_LOCATION)

        # List virtual machine sizes (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_sizes.list(AZURE_LOCATION)

        # List dedicated host groups in a resource group (TODO: need swagger file)
        result = self.mgmt_client.dedicated_host_groups.list_by_resource_group(resource_group.name)

        # List galleries in a resource group.[get]
        result = self.mgmt_client.galleries.list_by_resource_group(resource_group.name)

        # List all snapshots in a resource group.[get]
        result = self.mgmt_client.snapshots.list_by_resource_group(resource_group.name)

        # List all virtual machine images in a resource group.[get]
        result = self.mgmt_client.images.list_by_resource_group(resource_group.name)

        # List all managed disks in a resource group.[get]
        result = self.mgmt_client.disks.list_by_resource_group(resource_group.name)

        # List dedicated hosts in host group (TODO: need swagger file)
        result = self.mgmt_client.dedicated_hosts.list_by_host_group(resource_group.name, HOST_GROUP_NAME)

        # VirtualMachineRunCommandList[get]
        result = self.mgmt_client.virtual_machine_run_commands.list(AZURE_LOCATION)

        # TODO: dont belong here
        # # List Container Services[get]
        # result = self.mgmt_client.container_services.list()

        # List proximity placement groups in a subscription. [get]
        result = self.mgmt_client.proximity_placement_groups.list_by_subscription()

        # List all disk encryption sets in a subscription.[get]
        result = self.mgmt_client.disk_encryption_sets.list()

        # List dedicated host groups in a subscription (TODO: need swagger file)
        result = self.mgmt_client.dedicated_host_groups.list_by_subscription()

        # List availability sets in a subscription.[get]
        result = self.mgmt_client.availability_sets.list_by_subscription()

        # List availability sets (TODO: need swagger file)
        result = self.mgmt_client.availability_sets.list(resource_group.name)

        # List availability sets available sizes (TODO: need swagger file)
        result = self.mgmt_client.availability_sets.list_available_sizes(resource_group.name, AVAILABILITY_SET_NAME)

        # List galleries in a subscription.[get]
        result = self.mgmt_client.galleries.list()

        # List all snapshots in a subscription.[get]
        result = self.mgmt_client.snapshots.list()

        # List all virtual machine images in a subscription.[get]
        result = self.mgmt_client.images.list()

        # List all managed disks in a subscription.[get]
        result = self.mgmt_client.disks.list()

        # List usage (TODO: need swagger file)
        result = self.mgmt_client.usage.list(AZURE_LOCATION)

        # List operations (TODO: need swagger file)
        result = self.mgmt_client.operations.list()

        # Lists all available Resource SKUs[get]
        result = self.mgmt_client.resource_skus.list()

        # # Lists all available Resource SKUs for the specified region[get]
        # result = self.mgmt_client.resource_skus.list()

        # Update a dedicated host group.[put]
        BODY = {
          "tags": {
            "department": "finance"
          },
          "platform_fault_domain_count": "3"
        }
        result = self.mgmt_client.dedicated_host_groups.update(resource_group.name, HOST_GROUP_NAME, BODY)

        # Update a snapshot by
        BODY = {
          "creation_data": {
            "create_option": "Copy",
            "source_uri": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/disks/" + DISK_NAME
          }
        }
        result = self.mgmt_client.snapshots.update(resource_group.name, SNAPSHOT_NAME, BODY)
        result = result.result()

        # TODO: dont finish
        # # Update VirtualMachineScaleSet VM extension.[patch]
        # BODY = {
        #   "properties": {
        #     "auto_upgrade_minor_version": True,
        #     "publisher": "extPublisher",
        #     "type": "extType",
        #     "type_handler_version": "1.2",
        #     "settings": {
        #       "user_name": "xyz@microsoft.com"
        #     }
        #   }
        # }
        # result = self.mgmt_client.virtual_machine_scale_set_vmextensions.update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, EXTENSION_NAME, BODY)
        # result = result.result()

        # TODO: dont finish
        # Update a simple gallery Application Version.[patch]
        # BODY = {
        #   "properties": {
        #     "publishing_profile": {
        #       "source": {
        #         "file_name": "package.zip",
        #         "media_link": "https://mystorageaccount.blob.core.windows.net/mycontainer/package.zip?{sasKey}"
        #       },
        #       "target_regions": [
        #         {
        #           "name": "eastus",
        #           "regional_replica_count": "1",
        #           "storage_account_type": "Standard_LRS"
        #         }
        #       ],
        #       "replica_count": "1",
        #       "end_of_life_date": "2019-07-01T07:00:00Z",
        #       "storage_account_type": "Standard_LRS"
        #     }
        #   }
        # }
        # result = self.mgmt_client.gallery_application_versions.update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME, BODY)
        # result = result.result()

        # Start an extension rolling upgrade.[post]
        result = self.mgmt_client.virtual_machine_scale_set_rolling_upgrades.start_extension_upgrade(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # TODO:msrestazure.azure_exceptions.CloudError: Azure Error: MaxUnhealthyInstancePercentExceededInRollingUpgrade
        # Message: Rolling Upgrade failed after exceeding the MaxUnhealthyInstancePercent value defined in the RollingUpgradePolicy. 100% of instances are in an unhealthy state after being upgraded - more than the threshold of 20% configured in the RollingUpgradePolicy. The most impactful error is:  Instance found to be unhealthy or unreachable. For details on rolling upgrades, use http://aka.ms/AzureVMSSRollingUpgrade
        # Start vmss os upgrade (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_rolling_upgrades.start_os_upgrade(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        # result = result.result()

        # Cancel vmss upgrade (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_rolling_upgrades.cancel(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        # result = result.result()

        # Update disk.[patch] (TODO: need swagger file.)(doing)
        BODY = {
          "disk_size_gb": "200"
        }
        result = self.mgmt_client.disks.update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Grant acess disk (TODO: need swagger file)
        ACCESS = "Read"
        DURATION_IN_SECONDS = 1800
        result = self.mgmt_client.disks.grant_access(resource_group.name, DISK_NAME, ACCESS, DURATION_IN_SECONDS)
        result = result.result()
        # SAS_URI = result.access_sas

        # Grant acess snapshot (TODO: need swagger file)
        ACCESS = "Read"
        DURATION_IN_SECONDS = 1800
        result = self.mgmt_client.snapshots.grant_access(resource_group.name, SNAPSHOT_NAME, ACCESS, DURATION_IN_SECONDS)
        result = result.result()

        # Update availability sets (TODO: need swagger file)
        BODY = {
          "platform_fault_domain_count": "2",
          "platform_update_domain_count": "20"
        }
        result = self.mgmt_client.availability_sets.update(resource_group.name, AVAILABILITY_SET_NAME, BODY)

        # Update a dedicated host (TODO: need swagger file )
        BODY = {
          "tags": {
            "department": "HR"
          },
        }
        result = self.mgmt_client.dedicated_hosts.update(resource_group.name, HOST_GROUP_NAME, HOST_NAME, BODY)

        # Update a simple Gallery Image Version (Managed Image as source).[patch]
        BODY = {
          "publishing_profile": {
            "target_regions": [
              # {
              #   "name": "eastus",
              #   "regional_replica_count": "1"
              # },
              {
                "name": "East US",
                "regional_replica_count": "2",
                "storage_account_type": "Standard_ZRS"
              }
            ]
          },
          "storage_profile": {
            "os_disk_image": {
              "source": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/snapshots/" + SNAPSHOT_NAME + ""
              },
              "host_caching": "ReadOnly"
            },
            # TODO: NEED A IMAGE
            # "source": {
            #   "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
            # }
          }
        }
        result = self.mgmt_client.gallery_image_versions.update(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME, BODY)
        result = result.result()

        # Update a virtual machine scale set vm (TODO: need a swagger file)
        # BODY = {
        #   "location": "eastus",
        #   "tags": {
        #     "department": "HR"
        #   }
        # }
        # BODY = INSTANCE_VM_1
        # result = self.mgmt_client.virtual_machine_scale_set_vms.update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID, INSTANCE_VM_1)
        # result = result.result()

        # Update a virtual machine scale set (TODO: need a swagger file)
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "2",
            "name": "Standard_D1_v2"
          },
          "upgrade_policy": {
            "mode": "Manual"
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Update instances of machine scale set (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_sets.update_instances(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_IDS)
        # result = result.result()

        # Update a simple gallery Application.[patch]
        BODY = {
          "description": "This is the gallery application description.",
          "eula": "This is the gallery application EULA.",
          # "privacy_statement_uri": "myPrivacyStatementUri}",
          # "release_note_uri": "myReleaseNoteUri",
          "supported_os_type": "Windows",
          "tags": {
            "tag1": "tag1"
          }

        }
        result = self.mgmt_client.gallery_applications.update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, BODY)
        result = result.result()

        # Update a proximity placement group.[get]
        BODY = {
          "location": "eastus",
          "proximity_placement_group_type": "Standard"
        }
        result = self.mgmt_client.proximity_placement_groups.update(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME, BODY)

        # Export logs which contain all Api requests made to Compute Resource Provider within the given time period broken down by intervals.[post]
        # BODY = {
        #   "interval_length": "FiveMins",
        #   # "blob_container_sas_uri": "https://somesasuri",
        #   "blob_container_sas_uri": SAS_URI,
        #   "from_time": "2018-01-21T01:54:06.862601Z",
        #   "to_time": "2018-01-23T01:54:06.862601Z",
        #   "group_by_resource_name": True
        # }
        # result = self.mgmt_client.log_analytics.export_request_rate_by_interval(AZURE_LOCATION, LOG_ANALYTIC_NAME, BODY)
        # result = result.result()

        # VirtualMachineScaleSet vm restart (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.restart(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # VirtualMachineScaleSet vm power off (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.power_off(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # VirtualMachineScaleSet vm start (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.start(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # VirtualMachineScaleSet restart (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.restart(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # VirtualMachineScaleSet power off (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.power_off(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # VirtualMachineScaleSet start (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.start(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # Update VMSS vm extension (TODO: need swagger file)
        # BODY = {
        #   "auto_upgrade_minor_version": True,
        #   "publisher": "Microsoft.Azure.NetworkWatcher",
        #   "virtual_machine_extension_type": "NetworkWatcherAgentWindows",
        #   "type_handler_version": "1.4",
        # }
        # result = self.mgmt_client.virtual_machine_scale_set_vm_extensions.update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID, VIRTUAL_MACHINE_EXTENSION_NAME, BODY)

        # Delete VMSS vm exnteison (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vm_extensions.delete(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID, VIRTUAL_MACHINE_EXTENSION_NAME)

        # VMSSVMRunCommand[post]
        # BODY = {
        #   "command_id": "RunPowerShellScript"
        # }
        # INSTANCE_ID = INSTANCE_ID_2
        # result = self.mgmt_client.virtual_machine_scale_set_vms.run_command(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID, BODY)
        # result = result.result()

        # Delete instances of virtual machine scale sets (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_sets.delete_instances(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_IDS)
        # result = result.result()

        # Update virtual machine sacle set extension (TODO: need swagger file)
        BODY = {
          "auto_upgrade_minor_version": True,
        }
        result = self.mgmt_client.virtual_machine_scale_set_extensions.update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VMSS_EXTENSION_NAME, BODY)

        # Delete virtua machine scale set extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_set_extensions.delete(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VMSS_EXTENSION_NAME)
        result = result.result()

        # VirtualMachineScaleSet stop againe.
        result = self.mgmt_client.virtual_machine_scale_sets.power_off(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()


        # VirtualMachineRunCommand[post]
        BODY = {
          "command_id": "RunPowerShellScript"
        }
        result = self.mgmt_client.virtual_machines.run_command(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # VirtualMachine restart (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.restart(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # VirtualMachine power off (TODO:need swagger file)
        result = self.mgmt_client.virtual_machines.power_off(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # VirtualMachine start (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.start(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Update virtual machine extension (TODO: need swagger file)
        BODY = {
          "auto_upgrade_minor_version": True,
          "instance_view": {
            "name": VIRTUAL_MACHINE_EXTENSION_NAME,
            "type": "CustomScriptExtension"
          }
        }
        result = self.mgmt_client.virtual_machine_extensions.update(resource_group.name, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME, BODY)
        
        # This operation need VM running.
        # Delete virtual machine extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extensions.delete(resource_group.name, VIRTUAL_MACHINE_NAME,VIRTUAL_MACHINE_EXTENSION_NAME)
        result = result.result()

        # VirtualMachine power off again.
        result = self.mgmt_client.virtual_machines.power_off(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Update a simple gallery image.[patch]
        BODY = {
          "os_type": "Windows",
          "os_state": "Generalized",
          "hyper_vgeneration": "V1",
          "identifier": {
            "publisher": "myPublisherName",
            "offer": "myOfferName",
            "sku": "mySkuName"
          }
        }
        result = self.mgmt_client.gallery_images.update(resource_group.name, GALLERY_NAME, IMAGE_NAME, BODY)
        result = result.result()

        # Export logs which contain all throttled Api requests made to Compute Resource Provider within the given time period.[post]
        # BODY = {
        #   # "blob_container_sas_uri": "https://somesasuri",
        #   "blob_container_sas_uri": SAS_URI,
        #   "from_time": "2018-01-21T01:54:06.862601Z",
        #   "to_time": "2018-01-23T01:54:06.862601Z",
        #   "group_by_operation_name": True,
        #   "group_by_resource_name": False
        # }
        # result = self.mgmt_client.log_analytics.export_throttled_requests(LOCATION_NAME, LOG_ANALYTIC_NAME, BODY)
        # result = result.result()

        # Revoke access disk (TODO: need swagger file)
        result = self.mgmt_client.disks.revoke_access(resource_group.name, DISK_NAME)
        result = result.result()

        # Redeploy virtual machine scale set vm (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.redeploy(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # Redeploy virtual machine scale set (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.redeploy(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # Reapply the state of a virtual machine.[post]
        result = self.mgmt_client.virtual_machines.reapply(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Redeploy the virtual machine. (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.redeploy(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Perform maintenance virtual machine scale set vms (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.perform_maintenance(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # TODO: Operation 'performMaintenance' is not allowed on VM 'virtualmachinescalesetname_2' since the Subscription of this VM is not eligible.
        # Perform maintenance virtual machine scale set (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_sets.perform_maintenance(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        # result = result.result()

        # Reimage a virtual machine scale set vm (TODO: need swagger file)
        # BODY = {
        #   "temp_disk": True
        # }
        # result = self.mgmt_client.virtual_machine_scale_set_vms.reimage(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # Reimage all virtual machine scale sets vm (TODO: need swagger file)
        # BODY = {
        #   "temp_disk": True
        # }
        # result = self.mgmt_client.virtual_machine_scale_set_vms.reimage_all(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # Reimage a virtual machine scale set (TODO: need swagger file)
        # BODY = {
        #   "temp_disk": True
        # }
        # result = self.mgmt_client.virtual_machine_scale_sets.reimage(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        # result = result.result()

        # Reimage all virtual machine scale sets (TODO: need swagger file)
        # BODY = {
        #   "temp_disk": True
        # }
        # result = self.mgmt_client.virtual_machine_scale_sets.reimage_all(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        # result = result.result()

        # Force recovery service fabric platform update domain walk (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_sets.force_recovery_service_fabric_platform_update_domain_walk(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # Convert to single placement virtual machine scale sets (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_sets.convert_to_single_placement_group(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # # Perform maintenance the virtual machine (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machines.perform_maintenance(resource_group.name, VIRTUAL_MACHINE_NAME)
        # result = result.result()

        # # VirtualMachine convert to managed disks (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machines.convert_to_managed_disks(resource_group.name, VIRTUAL_MACHINE_NAME)
        # result = result.result()

        # TODO: Message: The Reimage and OSUpgrade Virtual Machine actions require that the virtual machine has Automatic OS Upgrades enabled.
        # Reimage a Virtual Machine.[post]
        # BODY = {
        #   "temp_disk": True
        # }
        # result = self.mgmt_client.virtual_machines.reimage(resource_group.name, VIRTUAL_MACHINE_NAME)
        # result = result.result()

        # TODO: NEED KEYVAULT
        # Update a disk encryption set.[patch]
        # BODY = {
        #   # "properties": {
        #   #   "active_key": {
        #   #     "source_vault": {
        #   #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.KeyVault/vaults/" + VAULT_NAME + ""
        #   #     },
        #   #     "key_url": "https://myvmvault.vault-int.azure-int.net/keys/{key}"
        #   #   }
        #   # },
        #   "tags": {
        #     "department": "Development",
        #     "project": "Encryption"
        #   }
        # }
        # result = self.mgmt_client.disk_encryption_sets.update(resource_group.name, DISK_ENCRYPTION_SET_NAME, BODY)
        # result = result.result()

        # Update a VM by detaching data disk[patch]
        BODY = {
          "network_profile": {
            "network_interfaces": [
              {
                # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                "id": NIC_ID,
                "properties": {
                  "primary": True
                }
              }
            ]
          }
        }
        result = self.mgmt_client.virtual_machines.update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Generalize a Virtual Machine.[post]
        result = self.mgmt_client.virtual_machines.generalize(resource_group.name, VIRTUAL_MACHINE_NAME)

        # Update a simple gallery.[patch]
        BODY = {
          "description": "This is the gallery description."
        }
        result = self.mgmt_client.galleries.update(resource_group.name, GALLERY_NAME, BODY)
        result = result.result()

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
        result = self.mgmt_client.images.update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Deallocate virtual machine (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.deallocate(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Deallocate virtual machine scale set vm (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.deallocate(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)

        # Deallocate virtual machine scale set (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.deallocate(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # TODO: need finish
        # # Delete VirtualMachineScaleSet VM extension.[delete]
        # result = self.mgmt_client.virtual_machine_scale_set_vmextensions.delete(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, EXTENSION_NAME)
        # result = result.result()

        # TODO: need finish
        # # Delete a gallery Application Version.[delete]
        # result = self.mgmt_client.gallery_application_versions.delete(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME)
        # result = result.result()

        # Delete virtual machine set vm (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.delete(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)

        # Delete virtual machine set (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.delete(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # Delete virtual machine (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.delete(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Delete a gallery Image Version.[delete]
        result = self.mgmt_client.gallery_image_versions.delete(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)
        result = result.result()

        # Delete a gallery Application.[delete]
        result = self.mgmt_client.gallery_applications.delete(resource_group.name, GALLERY_NAME, APPLICATION_NAME)
        result = result.result()

        # Revoke access snapshot (TODO: need swagger file)
        result = self.mgmt_client.snapshots.revoke_access(resource_group.name, SNAPSHOT_NAME)
        result = result.result()

        # Delete snapshot (TODO: need swagger file)
        result = self.mgmt_client.snapshots.delete(resource_group.name, SNAPSHOT_NAME)
        result = result.result()

        # Delete a proximity placement group.[delete]
        result = self.mgmt_client.proximity_placement_groups.delete(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME)

        # Delete a dedicated host (TODO: need swagger file)
        result = self.mgmt_client.dedicated_hosts.delete(resource_group.name, HOST_GROUP_NAME, HOST_NAME)
        result = result.result()

        # Delete a dedicated host group (TODO: need swagger file)
        result = self.mgmt_client.dedicated_host_groups.delete(resource_group.name, HOST_GROUP_NAME)

        # TODO: Dont belong here
        # Delete Container Service[delete]
        # result = self.mgmt_client.container_services.delete(resource_group.name, CONTAINER_SERVICE_NAME)
        # result = result.result()

        # Delete a gallery image.[delete]
        result = self.mgmt_client.gallery_images.delete(resource_group.name, GALLERY_NAME, IMAGE_NAME)
        result = result.result()

        # TODO: NEED ENCRYPTION SET
        # # Delete a disk encryption set.[delete]
        # result = self.mgmt_client.disk_encryption_sets.delete(resource_group.name, DISK_ENCRYPTION_SET_NAME)
        # result = result.result()

        # Delete a image.  (TODO: need a swagger file)
        result = self.mgmt_client.images.delete(resource_group.name, IMAGE_NAME)
        result = result.result()

        # Delete disk (TODO: need swagger file)
        result = self.mgmt_client.disks.delete(resource_group.name, DISK_NAME)
        result = result.result()

        # Delete availability sets (TODO: need a swagger file)
        resout = self.mgmt_client.availability_sets.delete(resource_group.name, AVAILABILITY_SET_NAME)

        # Delete a gallery.[delete]
        result = self.mgmt_client.galleries.delete(resource_group.name, GALLERY_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
