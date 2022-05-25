# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 21
# Methods Covered : 21
# Examples Total  : 21
# Examples Tested : 21
# Coverage %      : 100
# ----------------------

#  bastion_hosts: 5/5
#  ddos_custom_policies:  0/4 TODO:Region westeurope is not enabled for DdosCustomPolicy feature
#  ddos_protection_plans:  6/6
#  check_dns_name_availability: 1/1
#  get_active_sessions:  0/1  # TODO: need fix issue in codegen
#  disconnect_active_sessions: 0/1  # TODO: need sessions
#  put_bastion_shareable_link: 0/1
#  delete_bastion_shareable_link:  0/1
#  get_bastion_shareable_link:  0/1

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

    def create_vm(self, group_name, location, vm_name, network_name, subnet_name, interface_name):
        import azure.mgmt.compute
        self.compute_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )
        # create network
        subnet = self.create_virtual_network(group_name, location, network_name, subnet_name)
        nic_id = self.create_network_interface(group_name, location, interface_name, subnet)

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
        result = self.compute_client.virtual_machines.begin_create_or_update(group_name, vm_name, BODY)
        result = result.result()

    def create_public_ip_addresses(self, group_name, location, public_ip_name):
        # Create PublicIP
        BODY = {
            'location': location,
            'public_ip_allocation_method': 'Static',
            'idle_timeout_in_minutes': 4,
            'sku': {
              'name': 'Standard'
            }
        }
        result = self.mgmt_client.public_ip_addresses.begin_create_or_update(
            group_name,
            public_ip_name,
            BODY
        )
        return result.result()

    @unittest.skip('skip test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_MACHINE_NAME = self.get_resource_name("virtualmachine")
        VIRTUAL_NETWORK_NAME = self.get_resource_name("virtualnetwork")
        SUBNET_NAME = self.get_resource_name("subnet")
        BASTION_VIRTUAL_NETWORK_NAME = self.get_resource_name("bastionvirutalnetwork")
        BASTION_SUBNET_NAME = "AzureBastionSubnet"
        INTERFACE_NAME = self.get_resource_name("interface")
        PUBLIC_IP_ADDRESS_NAME = self.get_resource_name("publicipaddress")
        LOCATION_NAME = AZURE_LOCATION

        BASTION_HOST_NAME = self.get_resource_name("bastionhost")
        DDOS_CUSTOM_POLICY_NAME = self.get_resource_name("ddoscustompolicy")
        DDOS_PROTECTION_PLAN_NAME = self.get_resource_name("ddosprotectionplan")
        DOMAINNAMELABEL = self.get_resource_name("testdns")

        if self.is_live:
          self.create_vm(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, VIRTUAL_NETWORK_NAME, SUBNET_NAME, INTERFACE_NAME)
        self.create_public_ip_addresses(resource_group.name, AZURE_LOCATION, PUBLIC_IP_ADDRESS_NAME)
        self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, BASTION_VIRTUAL_NETWORK_NAME, BASTION_SUBNET_NAME)

        # Create Bastion Host[put]
        BODY = {
          "location": "eastus",
          "ip_configurations": [
            {
              "name": "bastionHostIpConfiguration",
              "subnet": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + BASTION_VIRTUAL_NETWORK_NAME + "/subnets/" + BASTION_SUBNET_NAME + ""
              },
              "public_ip_address": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
              }
            }
          ]
        }
        result = self.mgmt_client.bastion_hosts.begin_create_or_update(resource_group.name, BASTION_HOST_NAME, BODY)
        result = result.result()

        # TODO: Region westeurope is not enabled for DdosCustomPolicy feature
        # Create DDoS custom policy[put]
        # BODY = {
        #   "location": "westeurope",
        #   "protocol_custom_settings": [
        #     {
        #       "protocol": "Tcp"
        #     }
        #   ]
        # }
        # result = self.mgmt_client.ddos_custom_policies.begin_create_or_update(resource_group.name, DDOS_CUSTOM_POLICY_NAME, BODY)
        # result = result.result()

        # Create DDoS protection plan[put]
        BODY = {
          "location": "westus"
        }
        result = self.mgmt_client.ddos_protection_plans.begin_create_or_update(resource_group.name, DDOS_PROTECTION_PLAN_NAME, BODY)
        result = result.result()

        # Get DDoS protection plan[get]
        result = self.mgmt_client.ddos_protection_plans.get(resource_group.name, DDOS_PROTECTION_PLAN_NAME)

        # Get DDoS custom policy[get]
        # result = self.mgmt_client.ddos_custom_policies.get(resource_group.name, DDOS_CUSTOM_POLICY_NAME)

        # Get Bastion Host[get]
        result = self.mgmt_client.bastion_hosts.get(resource_group.name, BASTION_HOST_NAME)

        # List DDoS protection plans in resource group[get]
        result = self.mgmt_client.ddos_protection_plans.list_by_resource_group(resource_group.name)

        # Check Dns Name Availability[get]
        result = self.mgmt_client.check_dns_name_availability(LOCATION_NAME, DOMAINNAMELABEL)

        # List all Bastion Hosts for a given resource group[get]
        result = self.mgmt_client.bastion_hosts.list_by_resource_group(resource_group.name)

        # List all DDoS protection plans[get]
        result = self.mgmt_client.ddos_protection_plans.list()

        # List all Bastion Hosts for a given subscription[get]
        result = self.mgmt_client.bastion_hosts.list()

        # Returns a list of currently active sessions on the Bastion[post]
        # result = self.mgmt_client.begin_get_active_sessions(resource_group.name, BASTION_HOST_NAME)
        # sessions = result.result()

        # Deletes the specified active session[post]
        # result = self.mgmt_client.disconnect_active_sessions(resource_group.name, BASTION_HOST_NAME, [])

        # # Create Bastion Shareable Links for the request VMs[post]
        # BODY = {
        #   "vms": [
        #     {
        #       "vm": {
        #         "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
        #       }
        #     },
        #     # {
        #     #   "vm": {
        #     #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
        #     #   }
        #     # }
        #   ]
        # }
        # result = self.mgmt_client.put_bastion_shareable_link(resource_group.name, BASTION_HOST_NAME, BODY)
        # result = result.result()

        # # Delete Bastion Shareable Links for the request VMs[post]
        # BODY = {
        #   "vms": [
        #     {
        #       "vm": {
        #         "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
        #       }
        #     },
        #     # {
        #     #   "vm": {
        #     #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
        #     #   }
        #     # }
        #   ]
        # }
        # result = self.mgmt_client.delete_bastion_shareable_link(resource_group.name, BASTION_HOST_NAME, BODY)
        # result = result.result()

        # # Returns the Bastion Shareable Links for the request VMs[post]
        # BODY = {
        #   "vms": [
        #     {
        #       "vm": {
        #         "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
        #       }
        #     },
        #     # {
        #     #   "vm": {
        #     #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
        #     #   }
        #     # }
        #   ]
        # }
        # result = self.mgmt_client.get_bastion_shareable_link(resource_group.name, BASTION_HOST_NAME, BODY)

        # DDoS protection plan Update tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.ddos_protection_plans.update_tags(resource_group.name, DDOS_PROTECTION_PLAN_NAME, BODY)

        # DDoS Custom policy Update tags[patch]
        # BODY = {
        #   "tags": {
        #     "tag1": "value1",
        #     "tag2": "value2"
        #   }
        # }
        # result = self.mgmt_client.ddos_custom_policies.update_tags(resource_group.name, DDOS_CUSTOM_POLICY_NAME, BODY)

        # Delete DDoS protection plan[delete]
        result = self.mgmt_client.ddos_protection_plans.begin_delete(resource_group.name, DDOS_PROTECTION_PLAN_NAME)
        result = result.result()

        # Delete DDoS custom policy[delete]
        # result = self.mgmt_client.ddos_custom_policies.begin_delete(resource_group.name, DDOS_CUSTOM_POLICY_NAME)
        # result = result.result()

        # Delete Bastion Host[delete]
        result = self.mgmt_client.bastion_hosts.begin_delete(resource_group.name, BASTION_HOST_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
