# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   virtual_machine_scale_sets: 13/21
#   virtual_machine_scale_set_vms: 1/14
#   virtual_machine_scale_set_vm_extensions: 0/5
#   virtual_machine_scale_set_rolling_upgrades: 2/4
#   virtual_machine_scale_set_extensions: 5/5

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

        if self.is_live:
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


    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_MACHINE_SCALE_SET_NAME = self.get_resource_name("virtualmachinescaleset")
        VMSS_EXTENSION_NAME = self.get_resource_name("vmssextensionx")
        NETWORK_NAME = self.get_resource_name("networknamex")
        SUBNET_NAME = self.get_resource_name("subnetnamex")
        
        if self.is_live:
            SUBNET = self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, NETWORK_NAME, SUBNET_NAME)

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
        result = self.mgmt_client.virtual_machine_scale_sets.begin_create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # Create virtual machine sacle set extension (TODO: need swagger file)
        BODY = {
          "location": "eastus",
          "auto_upgrade_minor_version": True,
          "publisher": "Microsoft.Azure.NetworkWatcher",
          "type_properties_type": "NetworkWatcherAgentWindows",
          "type_handler_version": "1.4",
        }
        result = self.mgmt_client.virtual_machine_scale_set_extensions.begin_create_or_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VMSS_EXTENSION_NAME, BODY)
        result = result.result()

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

        # Get a virtual machine scale sets (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.get(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # Get virtual machine scale set extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_set_extensions.get(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VMSS_EXTENSION_NAME)
        
        # Get virtual machine scale set os upgrade history (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.get_os_upgrade_history(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # Get instance view of virtual machine scale set (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.get_instance_view(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # TODO: The entity was not found in this Azure location.
        # Get virtual machine scale set latest rolling upgrade (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_rolling_upgrades.get_latest(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # Get VMSS vm extension (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vm_extensions.get(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID, VIRTUAL_MACHINE_EXTENSION_NAME)

        # List VMSS vm extensions (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vm_extensions.list(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)

        # List virtual machine scale sets in a resource group (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.list(resource_group.name)

        # List virtual machine scale set extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_set_extensions.list(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # List all virtual machine scale sets (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.list_all()

        # List virtual machine scale sets skus (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.list_skus(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

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

        # Start an extension rolling upgrade.[post]
        result = self.mgmt_client.virtual_machine_scale_set_rolling_upgrades.begin_start_extension_upgrade(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # TODO:msrestazure.azure_exceptions.CloudError: Azure Error: MaxUnhealthyInstancePercentExceededInRollingUpgrade
        # Message: Rolling Upgrade failed after exceeding the MaxUnhealthyInstancePercent value defined in the RollingUpgradePolicy. 100% of instances are in an unhealthy state after being upgraded - more than the threshold of 20% configured in the RollingUpgradePolicy. The most impactful error is:  Instance found to be unhealthy or unreachable. For details on rolling upgrades, use http://aka.ms/AzureVMSSRollingUpgrade
        # Start vmss os upgrade (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_rolling_upgrades.start_os_upgrade(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        # result = result.result()

        # Cancel vmss upgrade (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_rolling_upgrades.cancel(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
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
        result = self.mgmt_client.virtual_machine_scale_sets.begin_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, BODY)
        result = result.result()

        # VirtualMachineScaleSet vm restart (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.restart(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # VirtualMachineScaleSet vm power off (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.power_off(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # VirtualMachineScaleSet vm start (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.start(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # Update instances of machine scale set (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_sets.update_instances(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_IDS)
        # result = result.result()

        # VirtualMachineScaleSet restart (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.begin_restart(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # VirtualMachineScaleSet power off (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.begin_power_off(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # VirtualMachineScaleSet start (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.begin_start(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
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

        # Delete instances of virtual machine scale sets (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_sets.delete_instances(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_IDS)
        # result = result.result()

        # VMSSVMRunCommand[post]
        # BODY = {
        #   "command_id": "RunPowerShellScript"
        # }
        # INSTANCE_ID = INSTANCE_ID_2
        # result = self.mgmt_client.virtual_machine_scale_set_vms.run_command(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID, BODY)
        # result = result.result()

        # VirtualMachineScaleSet stop againe.
        result = self.mgmt_client.virtual_machine_scale_sets.begin_power_off(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # Update virtual machine sacle set extension (TODO: need swagger file)
        BODY = {
          "auto_upgrade_minor_version": True,
        }
        result = self.mgmt_client.virtual_machine_scale_set_extensions.begin_update(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VMSS_EXTENSION_NAME, BODY)
        result = result.result()

        # Delete virtua machine scale set extension (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_set_extensions.begin_delete(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VMSS_EXTENSION_NAME)
        result = result.result()

        # Redeploy virtual machine scale set vm (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.redeploy(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
        # result = result.result()

        # Redeploy virtual machine scale set (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.begin_redeploy(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # TODO: Operation 'performMaintenance' is not allowed on VM 'virtualmachinescalesetname_2' since the Subscription of this VM is not eligible.
        # Perform maintenance virtual machine scale set (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_sets.perform_maintenance(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
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

        # Perform maintenance virtual machine scale set vms (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.perform_maintenance(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)
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

        # Deallocate virtual machine scale set (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.begin_deallocate(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()

        # Deallocate virtual machine scale set vm (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.deallocate(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)

        # Delete virtual machine set vm (TODO: need swagger file)
        # result = self.mgmt_client.virtual_machine_scale_set_vms.delete(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, INSTANCE_ID)

        # Delete virtual machine set (TODO: need swagger file)
        result = self.mgmt_client.virtual_machine_scale_sets.begin_delete(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        result = result.result()