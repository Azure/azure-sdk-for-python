# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 8
# Methods Covered : 8
# Examples Total  : 8
# Examples Tested : 8
# Coverage %      : 100
# ----------------------


#  TODO: after fix vmss problem

import unittest

import azure.mgmt.network
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtNetworkTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtNetworkTest, self).setUp()
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

    def create_network_interface(self, group_name, location, nic_name, subnet):

        async_nic_creation = self.mgmt_client.network_interfaces.begin_create_or_update(
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

    def create_vmss(self, group_name, location, vmss_name, network_name, subnet_name, ipconfig_name):
        # create network
        subnet = self.create_virtual_network(group_name, location, network_name, subnet_name)

        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "2",
            "name": "Standard_D1_v2"
          },
          "location": location,
          "overprovision": True,
          "virtual_machine_profile": {
            "storage_profile": {
              "image_reference": {
                  "offer": "UbuntuServer",
                  "publisher": "Canonical",
                  "sku": "18.04-LTS",
                  "version": "latest"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Standard_LRS"
                },
                "create_option": "FromImage",
                "disk_size_gb": "512"
              }
            },
            "os_profile": {
              "computer_name_prefix": "testPC",
              "admin_username": "testuser",
              "admin_password": "Aa!1()-xyz"
            },
            "network_profile": {
              "network_interface_configurations": [
                {
                  "name": ipconfig_name,
                  "primary": True,
                  "enable_ipforwarding": True,
                  "ip_configurations": [
                    {
                      "name": ipconfig_name,
                      "subnet": {
                        #   "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                        "id": subnet.id
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
        result = self.mgmt_client.virtual_machine_scale_sets.begin_create_or_update(resource_group.name, vmss_name, BODY)
        result = result.result()

    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network(self, resource_group):

        RESOURCE_GROUP = resource_group.name

        VIRTUAL_MACHINE_SCALE_SET_NAME = "vmsstest"
        VIRTUAL_NETWORK_NAME = "virtualnetwork"
        SUBNET_NAME = "subnet"
        IPCONFIGURATION_NAME = "ipconfig"

        self.create_vmss(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_NETWORK_NAME, SUBNET_NAME, IPCONFIGURATION_NAME)

        """
        # GetVMSSPublicIP[get]
        result = self.mgmt_client.public_ip_addresses.get_virtual_machine_scale_set_public_ip_address(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, NETWORK_INTERFACE_NAME, IPCONFIGURATION_NAME, PUBLICIP_ADDRESS_NAME)

        # ListVMSSVMPublicIP[get]
        result = self.mgmt_client.public_ip_addresses.list_virtual_machine_scale_set_vmpublic_ip_addresses(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, NETWORK_INTERFACE_NAME, IPCONFIGURATION_NAME)

        # Get virtual machine scale set network interface[get]
        result = self.mgmt_client.network_interfaces.get_virtual_machine_scale_set_ip_configuration(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, NETWORK_INTERFACE_NAME, IP_CONFIGURATION_NAME)

        # List virtual machine scale set network interface ip configurations[get]
        result = self.mgmt_client.network_interfaces.list_virtual_machine_scale_set_ip_configurations(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, NETWORK_INTERFACE_NAME)

        # Get virtual machine scale set network interface[get]
        result = self.mgmt_client.network_interfaces.get_virtual_machine_scale_set_ip_configuration(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME, NETWORK_INTERFACE_NAME, IP_CONFIGURATION_NAME)

        # List virtual machine scale set vm network interfaces[get]
        result = self.mgmt_client.network_interfaces.list_virtual_machine_scale_set_vmnetwork_interfaces(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME, VIRTUAL_MACHINE_NAME)

        # ListVMSSPublicIP[get]
        result = self.mgmt_client.public_ip_addresses.list_virtual_machine_scale_set_public_ip_addresses(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)

        # List virtual machine scale set network interfaces[get]
        result = self.mgmt_client.network_interfaces.list_virtual_machine_scale_set_network_interfaces(resource_group.name, VIRTUAL_MACHINE_SCALE_SET_NAME)
        """


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
