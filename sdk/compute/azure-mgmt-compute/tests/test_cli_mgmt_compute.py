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

import unittest

import azure.mgmt.compute
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"

        # Create an empty managed disk.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "creation_data": {
              "create_option": "Empty"
            },
            "disk_size_gb": "200"
          }
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Create a managed disk by importing an unmanaged blob from a different subscription.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "creation_data": {
              "create_option": "Import",
              "storage_account_id": "subscriptions/{subscriptionId}/resourceGroups/myResourceGroup/providers/Microsoft.Storage/storageAccounts/myStorageAccount",
              "source_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
            }
          }
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Create a managed disk by copying a snapshot.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "creation_data": {
              "create_option": "Copy",
              "source_resource_id": "subscriptions/{subscriptionId}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
            }
          }
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Create a managed disk by importing an unmanaged blob from the same subscription.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "creation_data": {
              "create_option": "Import",
              "source_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
            }
          }
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Create a managed disk from an existing managed disk in the same or different subscription.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "creation_data": {
              "create_option": "Copy",
              "source_resource_id": "subscriptions/{subscriptionId}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/myDisk1"
            }
          }
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Create a managed disk from a platform image.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "os_type": "Windows",
            "creation_data": {
              "create_option": "FromImage",
              "image_reference": {
                "id": "/Subscriptions/{subscriptionId}/Providers/Microsoft.Compute/Locations/uswest/Publishers/Microsoft/ArtifactTypes/VMImage/Offers/{offer}"
              }
            }
          }
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        # Create a managed upload disk.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "creation_data": {
              "create_option": "Upload",
              "upload_size_bytes": "10737418752"
            }
          }
        }
        result = self.mgmt_client.disks.create_or_update(resource_group.name, DISK_NAME, BODY)
        result = result.result()

        """
        # Create a virtual machine image from a snapshot.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "storage_profile": {
              "os_disk": {
                "os_type": "Linux",
                "snapshot": {
                  "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
                },
                "os_state": "Generalized"
              },
              "zone_resilient": False
            }
          }
        }
        result = self.mgmt_client.images.create_or_update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Create a virtual machine image from a managed disk with DiskEncryptionSet resource.[put]
        BODY = {
          "location": "West US",
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
          "location": "West US",
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
          "location": "West US",
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
          "location": "West US",
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
          "location": "West US",
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
          "location": "West US",
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
          "location": "West US",
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
          "location": "West US",
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
          "location": "West US",
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

        # Create or update a simple gallery.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "description": "This is the gallery description."
          }
        }
        result = self.mgmt_client.galleries.create_or_update(resource_group.name, GALLERY_NAME, BODY)
        result = result.result()
        """

        # Create a snapshot by importing an unmanaged blob from the same subscription.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "creation_data": {
              "create_option": "Import",
              "source_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
            }
          }
        }
        result = self.mgmt_client.snapshots.create_or_update(resource_group.name, SNAPSHOT_NAME, BODY)
        result = result.result()

        # Create a snapshot by importing an unmanaged blob from a different subscription.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "creation_data": {
              "create_option": "Import",
              "storage_account_id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Storage/storageAccounts/myStorageAccount",
              "source_uri": "https://mystorageaccount.blob.core.windows.net/osimages/osimage.vhd"
            }
          }
        }
        result = self.mgmt_client.snapshots.create_or_update(resource_group.name, SNAPSHOT_NAME, BODY)
        result = result.result()

        # Create a snapshot from an existing snapshot in the same or a different subscription.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "creation_data": {
              "create_option": "Copy",
              "source_resource_id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot1"
            }
          }
        }
        result = self.mgmt_client.snapshots.create_or_update(resource_group.name, SNAPSHOT_NAME, BODY)
        result = result.result()

        """
        # Create or update a dedicated host group.[put]
        BODY = {
          "location": "westus",
          "tags": {
            "department": "finance"
          },
          "zones": [
            "1"
          ],
          "properties": {
            "platform_fault_domain_count": "3"
          }
        }
        result = self.mgmt_client.dedicated_host_groups.create_or_update(resource_group.name, HOST_GROUP_NAME, BODY)

        # Create a platform-image vm with unmanaged os and data disks.[put]
        BODY = {
          "location": "westus",
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

        # Create a vm from a custom image.[put]
        BODY = {
          "location": "westus",
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

        # Create a vm with empty data disks.[put]
        BODY = {
          "location": "westus",
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

        # Create a custom-image vm from an unmanaged generalized os image.[put]
        BODY = {
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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

        # Create an availability set.[put]
        BODY = {
          "location": "westus",
          "properties": {
            "platform_fault_domain_count": "2",
            "platform_update_domain_count": "20"
          }
        }
        result = self.mgmt_client.availability_sets.create_or_update(resource_group.name, AVAILABILITY_SET_NAME, BODY)
        """

        # Create a disk encryption set.[put]
        BODY = {
          "location": "West US",
          "identity": {
            "type": "SystemAssigned"
          },
          "properties": {
            "active_key": {
              "source_vault": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.KeyVault/vaults/" + VAULT_NAME + ""
              },
              "key_url": "https://myvmvault.vault-int.azure-int.net/keys/{key}"
            }
          }
        }
        result = self.mgmt_client.disk_encryption_sets.create_or_update(resource_group.name, DISK_ENCRYPTION_SET_NAME, BODY)
        result = result.result()

        """
        # Create or update a simple gallery image.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "os_type": "Windows",
            "os_state": "Generalized",
            "hyper_vgeneration": "V1",
            "identifier": {
              "publisher": "myPublisherName",
              "offer": "myOfferName",
              "sku": "mySkuName"
            }
          }
        }
        result = self.mgmt_client.gallery_images.create_or_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, BODY)
        result = result.result()

        # Create or update a dedicated host .[put]
        BODY = {
          "location": "westus",
          "tags": {
            "department": "HR"
          },
          "properties": {
            "platform_fault_domain": "1"
          },
          "sku": {
            "name": "DSv3-Type1"
          }
        }
        result = self.mgmt_client.dedicated_hosts.create_or_update(resource_group.name, HOST_GROUP_NAME, HOST_NAME, BODY)
        result = result.result()

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
          "location": "westus",
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
          "location": "westus"
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
          "location": "westus",
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
          "location": "westus",
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

        # Create a scale set with empty data disks on each vm.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D2_v2"
          },
          "location": "westus",
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
              "mode": "Manual"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_sets.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create a scale set with an azure load balancer.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "3",
            "name": "Standard_D1_v2"
          },
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus"
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
          "location": "westus",
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
          "location": "westus"
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
          "location": "westus",
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
          "location": "westus",
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
          "location": "westus",
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

        # Create or Update a proximity placement group.[put]
        BODY = {
          "location": "westus",
          "properties": {
            "proximity_placement_group_type": "Standard"
          }
        }
        result = self.mgmt_client.proximity_placement_groups.create_or_update(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME, BODY)

        # Create or update a simple gallery Application.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "description": "This is the gallery application description.",
            "eula": "This is the gallery application EULA.",
            "privacy_statement_uri": "myPrivacyStatementUri}",
            "release_note_uri": "myReleaseNoteUri",
            "supported_ostype": "Windows"
          }
        }
        result = self.mgmt_client.gallery_applications.create_or_update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, BODY)
        result = result.result()

        # Create or update a simple Gallery Image Version using snapshots as a source.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "publishing_profile": {
              "target_regions": [
                {
                  "name": "West US",
                  "regional_replica_count": "1",
                  "encryption": {
                    "os_disk_image": {
                      "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + ""
                    },
                    "data_disk_images": [
                      {
                        "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + "",
                        "lun": "1"
                      }
                    ]
                  }
                },
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
              "data_disk_images": [
                {
                  "source": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/snapshots/" + SNAPSHOT_NAME + ""
                  },
                  "lun": "1",
                  "host_caching": "None"
                }
              ]
            }
          }
        }
        result = self.mgmt_client.gallery_image_versions.create_or_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME, BODY)
        result = result.result()

        # Create or update a simple Gallery Image Version (Managed Image as source).[put]
        BODY = {
          "location": "West US",
          "properties": {
            "publishing_profile": {
              "target_regions": [
                {
                  "name": "West US",
                  "regional_replica_count": "1",
                  "encryption": {
                    "os_disk_image": {
                      "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + ""
                    },
                    "data_disk_images": [
                      {
                        "lun": "0",
                        "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + ""
                      },
                      {
                        "lun": "1",
                        "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSet/" + DISK_ENCRYPTION_SET_NAME + ""
                      }
                    ]
                  }
                },
                {
                  "name": "East US",
                  "regional_replica_count": "2",
                  "storage_account_type": "Standard_ZRS"
                }
              ]
            },
            "storage_profile": {
              "source": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
              }
            }
          }
        }
        result = self.mgmt_client.gallery_image_versions.create_or_update(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME, BODY)
        result = result.result()

        # Create or update a simple gallery Application Version.[put]
        BODY = {
          "location": "West US",
          "properties": {
            "publishing_profile": {
              "source": {
                "file_name": "package.zip",
                "media_link": "https://mystorageaccount.blob.core.windows.net/mycontainer/package.zip?{sasKey}"
              },
              "target_regions": [
                {
                  "name": "West US",
                  "regional_replica_count": "1",
                  "storage_account_type": "Standard_LRS"
                }
              ],
              "replica_count": "1",
              "end_of_life_date": "2019-07-01T07:00:00Z",
              "storage_account_type": "Standard_LRS"
            }
          }
        }
        result = self.mgmt_client.gallery_application_versions.create_or_update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME, BODY)
        result = result.result()

        # Create VirtualMachineScaleSet VM extension.[put]
        BODY = {
          "location": "westus",
          "properties": {
            "auto_upgrade_minor_version": True,
            "publisher": "extPublisher",
            "type": "extType",
            "type_handler_version": "1.2",
            "settings": {
              "user_name": "xyz@microsoft.com"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_set_vmextensions.create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, EXTENSION_NAME, BODY)
        result = result.result()

        # Get VirtualMachineScaleSet VM extension.[get]
        result = self.mgmt_client.virtual_machine_scale_set_vmextensions.get(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, EXTENSION_NAME)

        # List extensions in Vmss instance.[get]
        result = self.mgmt_client.virtual_machine_scale_set_vmextensions.list(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME)

        # Get a gallery Application Version with replication status.[get]
        result = self.mgmt_client.gallery_application_versions.get(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME)

        # Get a gallery Application Version.[get]
        result = self.mgmt_client.gallery_application_versions.get(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME)

        # Get a gallery Image Version with snapshots as a source.[get]
        result = self.mgmt_client.gallery_image_versions.get(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)

        # Get a gallery Image Version with replication status.[get]
        result = self.mgmt_client.gallery_image_versions.get(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)

        # Get a gallery Image Version.[get]
        result = self.mgmt_client.gallery_image_versions.get(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)

        # List gallery Application Versions in a gallery Application Definition.[get]
        result = self.mgmt_client.gallery_application_versions.list_by_gallery_application(resource_group.name, GALLERY_NAME, APPLICATION_NAME)

        # Get a gallery Application.[get]
        result = self.mgmt_client.gallery_applications.get(resource_group.name, GALLERY_NAME, APPLICATION_NAME)

        # Create a proximity placement group.[get]
        result = self.mgmt_client.proximity_placement_groups.get(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME)

        # List gallery Image Versions in a gallery Image Definition.[get]
        result = self.mgmt_client.gallery_image_versions.list_by_gallery_image(resource_group.name, GALLERY_NAME, IMAGE_NAME)

        # Get Virtual Machine Instance View.[get]
        result = self.mgmt_client.virtual_machines.instance_view(resource_group.name, VIRTUAL_MACHINE_NAME)

        # Get Container Service[get]
        result = self.mgmt_client.container_services.get(resource_group.name, CONTAINER_SERVICE_NAME)

        # Get a dedicated host.[get]
        result = self.mgmt_client.dedicated_hosts.get(resource_group.name, HOST_GROUP_NAME, HOST_NAME)

        # Get a gallery image.[get]
        result = self.mgmt_client.gallery_images.get(resource_group.name, GALLERY_NAME, IMAGE_NAME)

        # Lists all available virtual machine sizes to which the specified virtual machine can be resized[get]
        result = self.mgmt_client.virtual_machines.list_available_sizes(resource_group.name, VIRTUAL_MACHINE_NAME)
        """

        # Get information about a disk encryption set.[get]
        result = self.mgmt_client.disk_encryption_sets.get(resource_group.name, DISK_ENCRYPTION_SET_NAME)

        """
        # Get a Virtual Machine.[get]
        result = self.mgmt_client.virtual_machines.get(resource_group.name, VIRTUAL_MACHINE_NAME)

        # List gallery Applications in a gallery.[get]
        result = self.mgmt_client.gallery_applications.list_by_gallery(resource_group.name, GALLERY_NAME)

        # List gallery images in a gallery.[get]
        result = self.mgmt_client.gallery_images.list_by_gallery(resource_group.name, GALLERY_NAME)

        # Create a dedicated host group.[get]
        result = self.mgmt_client.dedicated_host_groups.get(resource_group.name, HOST_GROUP_NAME)
        """

        # Get information about a snapshot.[get]
        result = self.mgmt_client.snapshots.get(resource_group.name, SNAPSHOT_NAME)

        """
        # Get a gallery.[get]
        result = self.mgmt_client.galleries.get(resource_group.name, GALLERY_NAME)

        # VirtualMachineRunCommandGet[get]
        result = self.mgmt_client.virtual_machine_run_commands.get(LOCATION_NAME, RUN_COMMAND_NAME)

        # List Container Services by Resource Group[get]
        result = self.mgmt_client.container_services.list_by_resource_group(resource_group.name)

        # Create a proximity placement group.[get]
        result = self.mgmt_client.proximity_placement_groups.get(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME)

        # Get information about a virtual machine image.[get]
        result = self.mgmt_client.images.get(resource_group.name, IMAGE_NAME)
        """

        # Get information about a managed disk.[get]
        result = self.mgmt_client.disks.get(resource_group.name, DISK_NAME)

        # List all disk encryption sets in a resource group.[get]
        result = self.mgmt_client.disk_encryption_sets.list_by_resource_group(resource_group.name)

        """
        # Lists all the virtual machines under the specified subscription for the specified location.[get]
        result = self.mgmt_client.virtual_machines.list_by_location(LOCATION_NAME)

        # List galleries in a resource group.[get]
        result = self.mgmt_client.galleries.list_by_resource_group(resource_group.name)
        """

        # List all snapshots in a resource group.[get]
        result = self.mgmt_client.snapshots.list_by_resource_group(resource_group.name)

        """
        # List all virtual machine images in a resource group.[get]
        result = self.mgmt_client.images.list_by_resource_group(resource_group.name)
        """

        # List all managed disks in a resource group.[get]
        result = self.mgmt_client.disks.list_by_resource_group(resource_group.name)

        """
        # VirtualMachineRunCommandList[get]
        result = self.mgmt_client.virtual_machine_run_commands.list(LOCATION_NAME)

        # List Container Services[get]
        result = self.mgmt_client.container_services.list()

        # Create a proximity placement group.[get]
        result = self.mgmt_client.proximity_placement_groups.get(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME)
        """

        # List all disk encryption sets in a subscription.[get]
        result = self.mgmt_client.disk_encryption_sets.list()

        """
        # List availability sets in a subscription.[get]
        result = self.mgmt_client.availability_sets.list_by_subscription()

        # List galleries in a subscription.[get]
        result = self.mgmt_client.galleries.list()
        """

        # List all snapshots in a subscription.[get]
        result = self.mgmt_client.snapshots.list()

        """
        # List all virtual machine images in a subscription.[get]
        result = self.mgmt_client.images.list()
        """

        # List all managed disks in a subscription.[get]
        result = self.mgmt_client.disks.list()

        """
        # Lists all available Resource SKUs[get]
        result = self.mgmt_client.resource_skus.list()

        # Lists all available Resource SKUs for the specified region[get]
        result = self.mgmt_client.resource_skus.list()

        # Update VirtualMachineScaleSet VM extension.[patch]
        BODY = {
          "properties": {
            "auto_upgrade_minor_version": True,
            "publisher": "extPublisher",
            "type": "extType",
            "type_handler_version": "1.2",
            "settings": {
              "user_name": "xyz@microsoft.com"
            }
          }
        }
        result = self.mgmt_client.virtual_machine_scale_set_vmextensions.update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, EXTENSION_NAME, BODY)
        result = result.result()

        # Update a simple gallery Application Version.[patch]
        BODY = {
          "properties": {
            "publishing_profile": {
              "source": {
                "file_name": "package.zip",
                "media_link": "https://mystorageaccount.blob.core.windows.net/mycontainer/package.zip?{sasKey}"
              },
              "target_regions": [
                {
                  "name": "West US",
                  "regional_replica_count": "1",
                  "storage_account_type": "Standard_LRS"
                }
              ],
              "replica_count": "1",
              "end_of_life_date": "2019-07-01T07:00:00Z",
              "storage_account_type": "Standard_LRS"
            }
          }
        }
        result = self.mgmt_client.gallery_application_versions.update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME, BODY)
        result = result.result()

        # Start an extension rolling upgrade.[post]
        result = self.mgmt_client.virtual_machine_scale_set_rolling_upgrades.start_extension_upgrade(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # Update a simple Gallery Image Version (Managed Image as source).[patch]
        BODY = {
          "properties": {
            "publishing_profile": {
              "target_regions": [
                {
                  "name": "West US",
                  "regional_replica_count": "1"
                },
                {
                  "name": "East US",
                  "regional_replica_count": "2",
                  "storage_account_type": "Standard_ZRS"
                }
              ]
            },
            "storage_profile": {
              "source": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/images/" + IMAGE_NAME + ""
              }
            }
          }
        }
        result = self.mgmt_client.gallery_image_versions.update(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME, BODY)
        result = result.result()

        # Update a simple gallery Application.[patch]
        BODY = {
          "properties": {
            "description": "This is the gallery application description.",
            "eula": "This is the gallery application EULA.",
            "privacy_statement_uri": "myPrivacyStatementUri}",
            "release_note_uri": "myReleaseNoteUri",
            "supported_ostype": "Windows"
          }
        }
        result = self.mgmt_client.gallery_applications.update(resource_group.name, GALLERY_NAME, APPLICATION_NAME, BODY)
        result = result.result()

        # Create a proximity placement group.[get]
        result = self.mgmt_client.proximity_placement_groups.get(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME)

        # Export logs which contain all Api requests made to Compute Resource Provider within the given time period broken down by intervals.[post]
        BODY = {
          "interval_length": "FiveMins",
          "blob_container_sas_uri": "https://somesasuri",
          "from_time": "2018-01-21T01:54:06.862601Z",
          "to_time": "2018-01-23T01:54:06.862601Z",
          "group_by_resource_name": True
        }
        result = self.mgmt_client.log_analytics.export_request_rate_by_interval(LOCATION_NAME, LOG_ANALYTIC_NAME, BODY)
        result = result.result()

        # VirtualMachineRunCommand[post]
        BODY = {
          "command_id": "RunPowerShellScript"
        }
        result = self.mgmt_client.virtual_machines.run_command(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Generalize a Virtual Machine.[post]
        result = self.mgmt_client.virtual_machines.generalize(resource_group.name, VIRTUAL_MACHINE_NAME)

        # Update a simple gallery image.[patch]
        BODY = {
          "properties": {
            "os_type": "Windows",
            "os_state": "Generalized",
            "hyper_vgeneration": "V1",
            "identifier": {
              "publisher": "myPublisherName",
              "offer": "myOfferName",
              "sku": "mySkuName"
            }
          }
        }
        result = self.mgmt_client.gallery_images.update(resource_group.name, GALLERY_NAME, IMAGE_NAME, BODY)
        result = result.result()

        # Export logs which contain all throttled Api requests made to Compute Resource Provider within the given time period.[post]
        BODY = {
          "blob_container_sas_uri": "https://somesasuri",
          "from_time": "2018-01-21T01:54:06.862601Z",
          "to_time": "2018-01-23T01:54:06.862601Z",
          "group_by_operation_name": True,
          "group_by_resource_name": False
        }
        result = self.mgmt_client.log_analytics.export_throttled_requests(LOCATION_NAME, LOG_ANALYTIC_NAME, BODY)
        result = result.result()

        # Reapply the state of a virtual machine.[post]
        result = self.mgmt_client.virtual_machines.reapply(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Reimage a Virtual Machine.[post]
        BODY = {
          "temp_disk": True
        }
        result = self.mgmt_client.virtual_machines.reimage(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()
        """

        # Update a disk encryption set.[patch]
        BODY = {
          "properties": {
            "active_key": {
              "source_vault": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.KeyVault/vaults/" + VAULT_NAME + ""
              },
              "key_url": "https://myvmvault.vault-int.azure-int.net/keys/{key}"
            }
          },
          "tags": {
            "department": "Development",
            "project": "Encryption"
          }
        }
        result = self.mgmt_client.disk_encryption_sets.update(resource_group.name, DISK_ENCRYPTION_SET_NAME, BODY)
        result = result.result()

        """
        # Update a VM by detaching data disk[patch]
        BODY = {
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
                  "lun": "0",
                  "to_be_detached": True
                },
                {
                  "disk_size_gb": "1023",
                  "create_option": "Empty",
                  "lun": "1",
                  "to_be_detached": False
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
        result = self.mgmt_client.virtual_machines.update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Update a simple gallery.[patch]
        BODY = {
          "properties": {
            "description": "This is the gallery description."
          }
        }
        result = self.mgmt_client.galleries.update(resource_group.name, GALLERY_NAME, BODY)
        result = result.result()

        # Updates tags of an Image.[patch]
        BODY = {
          "properties": {
            "source_virtual_machine": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
            },
            "hyper_vgeneration": "V1"
          },
          "tags": {
            "department": "HR"
          }
        }
        result = self.mgmt_client.images.update(resource_group.name, IMAGE_NAME, BODY)
        result = result.result()

        # Delete VirtualMachineScaleSet VM extension.[delete]
        result = self.mgmt_client.virtual_machine_scale_set_vmextensions.delete(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, EXTENSION_NAME)
        result = result.result()

        # Delete a gallery Application Version.[delete]
        result = self.mgmt_client.gallery_application_versions.delete(resource_group.name, GALLERY_NAME, APPLICATION_NAME, VERSION_NAME)
        result = result.result()

        # Delete a gallery Image Version.[delete]
        result = self.mgmt_client.gallery_image_versions.delete(resource_group.name, GALLERY_NAME, IMAGE_NAME, VERSION_NAME)
        result = result.result()

        # Delete a gallery Application.[delete]
        result = self.mgmt_client.gallery_applications.delete(resource_group.name, GALLERY_NAME, APPLICATION_NAME)
        result = result.result()

        # Create a proximity placement group.[get]
        result = self.mgmt_client.proximity_placement_groups.get(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME)

        # Delete Container Service[delete]
        result = self.mgmt_client.container_services.delete(resource_group.name, CONTAINER_SERVICE_NAME)
        result = result.result()

        # Delete a gallery image.[delete]
        result = self.mgmt_client.gallery_images.delete(resource_group.name, GALLERY_NAME, IMAGE_NAME)
        result = result.result()
        """

        # Delete a disk encryption set.[delete]
        result = self.mgmt_client.disk_encryption_sets.delete(resource_group.name, DISK_ENCRYPTION_SET_NAME)
        result = result.result()

        """
        # Delete a gallery.[delete]
        result = self.mgmt_client.galleries.delete(resource_group.name, GALLERY_NAME)
        result = result.result()
        """


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
