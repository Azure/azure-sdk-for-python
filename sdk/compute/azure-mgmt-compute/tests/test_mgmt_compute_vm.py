# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   virtual_machines: 21/21
#   virtual_machine_size: 1/1
#   virtual_machine_run_commands: 2/2
#   virtual_machine_images: 5/5
#   virtual_machine_extensions: 5/5
#   virtual_machine_extension_images: 3/3

import unittest

import azure.mgmt.compute
from azure.core.exceptions import ResourceExistsError
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTest, self).setUp()
        from azure.mgmt.compute import ComputeManagementClient
        self.mgmt_client = self.create_mgmt_client(
            ComputeManagementClient
        )
        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):
      
      azure_operation_poller = self.network_client.virtual_networks.begin_create_or_update(
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

      async_subnet_creation = self.network_client.subnets.begin_create_or_update(
          group_name,
          network_name,
          subnet_name,
          {'address_prefix': '10.0.0.0/24'}
      )
      subnet_info = async_subnet_creation.result()
      
      return subnet_info

    def create_network_interface(self, group_name, location, nic_name, subnet):

        async_nic_creation = self.network_client.network_interfaces.begin_create_or_update(
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



    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_vm(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_MACHINE_NAME = self.get_resource_name("virtualmachinex")
        SUBNET_NAME = self.get_resource_name("subnetx")
        INTERFACE_NAME = self.get_resource_name("interfacex")
        NETWORK_NAME = self.get_resource_name("networknamex")
        VIRTUAL_MACHINE_EXTENSION_NAME = self.get_resource_name("virtualmachineextensionx")

        # create network
        if self.is_live:
            SUBNET = self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, NETWORK_NAME, SUBNET_NAME)
            NIC_ID = self.create_network_interface(RESOURCE_GROUP, AZURE_LOCATION, INTERFACE_NAME, SUBNET)

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
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + INTERFACE_NAME + "",
                # "id": NIC_ID,
                "properties": {
                  "primary": True
                }
              }
            ]
          }
        }
        result = self.mgmt_client.virtual_machines.begin_create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Create virtual machine extension (TODO: need swagger file)
        BODY = {
          "location": "eastus",
          "auto_upgrade_minor_version": True,
          "publisher": "Microsoft.Azure.NetworkWatcher",
          # "virtual_machine_extension_type": "NetworkWatcherAgentWindows",
          "type_properties_type": "NetworkWatcherAgentWindows",  # TODO: Is this a bug?
          "type_handler_version": "1.4",
        }
        result = self.mgmt_client.virtual_machine_extensions.begin_create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME, BODY)
        result = result.result()

        # Get Virtual Machine Instance View.[get]
        result = self.mgmt_client.virtual_machines.instance_view(resource_group.name, VIRTUAL_MACHINE_NAME)

        # Get virtual machine extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extensions.get(resource_group.name, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME)

        # VirtualMachineRunCommandGet[get]
        RUN_COMMAND_NAME = "RunPowerShellScript"
        result = self.mgmt_client.virtual_machine_run_commands.get(AZURE_LOCATION, RUN_COMMAND_NAME)

        # Lists all available virtual machine sizes to which the specified virtual machine can be resized[get]
        result = self.mgmt_client.virtual_machines.list_available_sizes(resource_group.name, VIRTUAL_MACHINE_NAME)

        # Llist virtual machine extensions (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extensions.list(resource_group.name, VIRTUAL_MACHINE_NAME)

        # List virtual machine sizes (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_sizes.list(AZURE_LOCATION)

        # VirtualMachineRunCommandList[get]
        result = self.mgmt_client.virtual_machine_run_commands.list(AZURE_LOCATION)

        # Get a Virtual Machine.[get]
        result = self.mgmt_client.virtual_machines.get(resource_group.name, VIRTUAL_MACHINE_NAME)

        # List the virtual machines (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.list(resource_group.name)

        # List all virtual machines (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.list_all()

        # Lists all the virtual machines under the specified subscription for the specified location.[get]
        result = self.mgmt_client.virtual_machines.list_by_location(AZURE_LOCATION)

        # VirtualMachineRunCommand[post]
        BODY = {
          "command_id": "RunPowerShellScript"
        }
        result = self.mgmt_client.virtual_machines.begin_run_command(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # VirtualMachine restart (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.begin_restart(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # VirtualMachine power off (TODO:need swagger file)
        result = self.mgmt_client.virtual_machines.begin_power_off(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # VirtualMachine start (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.begin_start(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Update virtual machine extension (TODO: need swagger file)
        BODY = {
          "auto_upgrade_minor_version": True,
          "instance_view": {
            "name": VIRTUAL_MACHINE_EXTENSION_NAME,
            "type": "CustomScriptExtension"
          }
        }
        result = self.mgmt_client.virtual_machine_extensions.begin_update(resource_group.name, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME, BODY)
        result = result.result()
        
        # This operation need VM running.
        # Delete virtual machine extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extensions.begin_delete(resource_group.name, VIRTUAL_MACHINE_NAME,VIRTUAL_MACHINE_EXTENSION_NAME)
        result = result.result()

        # VirtualMachine power off again.
        result = self.mgmt_client.virtual_machines.begin_power_off(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Reapply the state of a virtual machine.[post]
        result = self.mgmt_client.virtual_machines.begin_reapply(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Redeploy the virtual machine. (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.begin_redeploy(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

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

        # Update a VM by detaching data disk[patch]
        BODY = {
          "network_profile": {
            "network_interfaces": [
              {
                # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "",
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + INTERFACE_NAME + "",
                "properties": {
                  "primary": True
                }
              }
            ]
          }
        }
        result = self.mgmt_client.virtual_machines.begin_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Generalize a Virtual Machine.[post]
        result = self.mgmt_client.virtual_machines.generalize(resource_group.name, VIRTUAL_MACHINE_NAME)

        # Deallocate virtual machine (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.begin_deallocate(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

        # Delete virtual machine (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.begin_delete(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_vm_2(self, resource_group):
        
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_MACHINE_NAME = self.get_resource_name("virtualmachinex")
        SUBNET_NAME = self.get_resource_name("subnetx")
        INTERFACE_NAME = self.get_resource_name("interfacex")
        NETWORK_NAME = self.get_resource_name("networknamex")
        VIRTUAL_MACHINE_EXTENSION_NAME = self.get_resource_name("virtualmachineextensionx")

        # create network
        if self.is_live:
            SUBNET = self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, NETWORK_NAME, SUBNET_NAME)
            NIC_ID = self.create_network_interface(RESOURCE_GROUP, AZURE_LOCATION, INTERFACE_NAME, SUBNET)

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
              "name": "myVMosdisk",
              "create_option": "FromImage"
            }
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
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + INTERFACE_NAME + "",
                "properties": {
                  "primary": True
                }
              }
            ]
          },
          "eviction_policy": "Deallocate",
          "billing_profile": {
            "max_price": 1
          },
          "priority": "Spot"
        }
        result = self.mgmt_client.virtual_machines.begin_create_or_update(resource_group.name, VIRTUAL_MACHINE_NAME, BODY)
        result = result.result()

        # Simulate eviction (TODO: need example)
        self.mgmt_client.virtual_machines.simulate_eviction(resource_group.name, VIRTUAL_MACHINE_NAME, )

        # TODO: cannot use it successfully, see:     https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-maintenance-notifications
        # Perform maintenance the virtual machine (TODO: need swagger file)
        try:
            result = self.mgmt_client.virtual_machines.begin_perform_maintenance(resource_group.name, VIRTUAL_MACHINE_NAME)
            result = result.result()
        except ResourceExistsError as e:
            self.assertEquals(str(e), "(OperationNotAllowed) Operation 'performMaintenance' is not allowed on VM '%s' since the Subscription of this VM is not eligible." % (VIRTUAL_MACHINE_NAME))

        # VirtualMachine convert to managed disks (TODO: need swagger file)
        try:
            result = self.mgmt_client.virtual_machines.begin_convert_to_managed_disks(resource_group.name, VIRTUAL_MACHINE_NAME)
            result = result.result()
        except ResourceExistsError as e:
            self.assertEquals(str(e), "(OperationNotAllowed) VM '%s' is already using managed disks." % (VIRTUAL_MACHINE_NAME))

        # TODO: Message: The Reimage and OSUpgrade Virtual Machine actions require that the virtual machine has Automatic OS Upgrades enabled.
        # Reimage a Virtual Machine.[post]
        try:
            BODY = {
              "temp_disk": True
            }
            result = self.mgmt_client.virtual_machines.begin_reimage(resource_group.name, VIRTUAL_MACHINE_NAME)
            result = result.result()
        except ResourceExistsError as e:
            self.assertEquals(str(e), "(OperationNotAllowed) The Reimage and OSUpgrade Virtual Machine actions require that the virtual machine has Automatic OS Upgrades enabled.")

        # Delete virtual machine (TODO: need swagger file)
        result = self.mgmt_client.virtual_machines.begin_delete(resource_group.name, VIRTUAL_MACHINE_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_vm_image(self, resource_group):
        PUBLISHER_NAME = "MicrosoftWindowsServer"
        OFFER = "WindowsServer"
        SKUS = "2019-Datacenter"
        VERSION = "2019.0.20190115" 

        # Get Virtual Machine Image (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_images.get(AZURE_LOCATION, PUBLISHER_NAME, OFFER, SKUS, VERSION)

        # List Virtual Machine images (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_images.list(AZURE_LOCATION, PUBLISHER_NAME, OFFER, SKUS)

        # List Virtual Machine image offers (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_images.list_offers(AZURE_LOCATION, PUBLISHER_NAME)

        # List Virtual Machine image publishers (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_images.list_publishers(AZURE_LOCATION)

        # List Virtual Machine image skus (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_images.list_skus(AZURE_LOCATION, PUBLISHER_NAME, OFFER)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_vm_extension_image(self, resource_group):
        EXTENSION_PUBLISHER_NAME = "Microsoft.Compute"
        EXTENSION_IMAGE_TYPE = "VMAccessAgent"
        EXTENSION_IMAGE_VERSION = "1.0.2"
 
        # Get Virtual Machine Extension Image (TODO: neet swagger file)
        result = self.mgmt_client.virtual_machine_extension_images.get(AZURE_LOCATION, EXTENSION_PUBLISHER_NAME, EXTENSION_IMAGE_TYPE, EXTENSION_IMAGE_VERSION)

        # List Virtual Machine extension image types (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extension_images.list_types(AZURE_LOCATION, EXTENSION_PUBLISHER_NAME)

        # # List Virtual Machine extension image versions (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_extension_images.list_versions(AZURE_LOCATION, EXTENSION_PUBLISHER_NAME, EXTENSION_IMAGE_TYPE)
 
