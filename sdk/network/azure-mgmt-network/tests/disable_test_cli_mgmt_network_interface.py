# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 15
# Methods Covered : 15
# Examples Total  : 15
# Examples Tested : 15
# Coverage %      : 100
# ----------------------

#  network_interfaces: 8/8
#  network_interface_tap_configurations: 0/4 # TODO: need virtual network tap
#  network_interface_ip_configurations:  2/2
#  network_interface_load_balancers:  1/1


import unittest
import pytest

import azure.mgmt.network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'


@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):
      
        result = self.mgmt_client.virtual_networks.begin_create_or_update(
            group_name,
            network_name,
            {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            },
        )
        result_create = result.result()

        async_subnet_creation = self.mgmt_client.subnets.begin_create_or_update(
            group_name,
            network_name,
            subnet_name,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet_info = async_subnet_creation.result()
          
        return subnet_info

    def create_public_ip_address(self, group_name, location, public_ip_address_name):
        # Create public IP address defaults[put]
        BODY = {
          "location": location
        }
        result = self.mgmt_client.public_ip_addresses.begin_create_or_update(group_name, public_ip_address_name, BODY)
        result = result.result()

    def create_vm(self, group_name, location, vm_name, nic_id):
        import azure.mgmt.compute
        compute_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )

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
                "id": nic_id,
                "properties": {
                  "primary": True
                }
              }
            ]
          }
        }
        result = compute_client.virtual_machines.begin_create_or_update(group_name, vm_name, BODY)
        result = result.result()

    def delete_vm(self, group_name, vm_name):
        import azure.mgmt.compute
        compute_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )
        # Fix when version from 17.1.0 to 18.0.0
        result = compute_client.virtual_machines.begin_delete(group_name, vm_name)
        result = result.result()
    
    @unittest.skip('skip test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        PUBLIC_IP_ADDRESS_NAME = "publicipaddress"
        VIRTUAL_NETWORK_NAME = "virtualnetwork"
        SUBNET_NAME = "subnet"
        VIRTUAL_MACHINE_NAME = "virtualmachine"
        NETWORK_INTERFACE_NAME = "myNetworkInterface"
        TAP_CONFIGURATION_NAME = "myTapConfiguration"
        IP_CONFIGURATION_NAME = "myIpConfiguration"

        self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        self.create_public_ip_address(RESOURCE_GROUP, AZURE_LOCATION, PUBLIC_IP_ADDRESS_NAME)

        # /NetworkInterfaces/put/Create network interface[put]
        BODY = {
          "enable_accelerated_networking": True,
          "ip_configurations": [
            {
              "name": IP_CONFIGURATION_NAME,
              "public_ip_address": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME
              },
              "subnet": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/"+ SUBNET_NAME
              }
            }
          ],
          "location": "eastus"
        }
        result = self.mgmt_client.network_interfaces.begin_create_or_update(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME, parameters=BODY)
        interface = result.result()

        if self.is_live:
          self.create_vm(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, interface.id)

        # /NetworkInterfaceTapConfigurations/put/Create Network Interface Tap Configurations[put]
        # BODY = {
        #   "properties": {
        #     "virtual_network_tap": {
        #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworkTapstestvtap"
        #     }
        #   }
        # }
        # result = self.mgmt_client.network_interface_tap_configurations.begin_create_or_update(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME, tap_configuration_name=TAP_CONFIGURATION_NAME, tap_configuration_parameters=BODY)
        # result = result.result()

        # /NetworkInterfaceTapConfigurations/get/Get Network Interface Tap Configurations[get]
        # result = self.mgmt_client.network_interface_tap_configurations.get(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME, tap_configuration_name=TAP_CONFIGURATION_NAME)

        # /NetworkInterfaceIPConfigurations/get/NetworkInterfaceIPConfigurationGet[get]
        result = self.mgmt_client.network_interface_ip_configurations.get(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME, ip_configuration_name=IP_CONFIGURATION_NAME)

        # /NetworkInterfaceTapConfigurations/get/List virtual network tap configurations[get]
        # result = self.mgmt_client.network_interface_tap_configurations.list(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME)

        # /NetworkInterfaceIPConfigurations/get/NetworkInterfaceIPConfigurationList[get]
        result = self.mgmt_client.network_interface_ip_configurations.list(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME)

        # /NetworkInterfaceLoadBalancers/get/NetworkInterfaceLoadBalancerList[get]
        result = self.mgmt_client.network_interface_load_balancers.list(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME)

        # /NetworkInterfaces/get/Get network interface[get]
        result = self.mgmt_client.network_interfaces.get(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME)

        # /NetworkInterfaces/get/List network interfaces in resource group[get]
        result = self.mgmt_client.network_interfaces.list(resource_group_name=RESOURCE_GROUP)

        # /NetworkInterfaces/get/List all network interfaces[get]
        result = self.mgmt_client.network_interfaces.list_all()

        # /NetworkInterfaces/post/List network interface effective network security groups[post]
        result = self.mgmt_client.network_interfaces.begin_list_effective_network_security_groups(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME)
        result = result.result()

        # /NetworkInterfaces/post/Show network interface effective route tables[post]
        result = self.mgmt_client.network_interfaces.begin_get_effective_route_table(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME)
        result = result.result()

        # /NetworkInterfaces/patch/Update network interface tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.network_interfaces.update_tags(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME, parameters=BODY)

        # /NetworkInterfaceTapConfigurations/delete/Delete tap configuration[delete]
        # result = self.mgmt_client.network_interface_tap_configurations.begin_delete(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME, tap_configuration_name=TAP_CONFIGURATION_NAME)
        # result = result.result()

        if self.is_live:
          self.delete_vm(RESOURCE_GROUP, VIRTUAL_MACHINE_NAME)

        # /NetworkInterfaces/delete/Delete network interface[delete]
        result = self.mgmt_client.network_interfaces.begin_delete(resource_group_name=RESOURCE_GROUP, network_interface_name=NETWORK_INTERFACE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
