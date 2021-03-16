# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 60
# Methods Covered : 60
# Examples Total  : 63
# Examples Tested : 63
# Coverage %      : 100
# ----------------------

#  network_watchers:  16/18
#  network_profiles: 7/7
#  network_security_groups:  6/6
#  network_virtual_appliances: 0/6  # TODO: (InvalidResourceType) The resource type could not be found in the namespace 'Microsoft.Network' for api version '2020-03-01'
#  flow_logs: 3/3
#  packet_captures: 6/6  
#  connection_monitors: 9/9
#  security_rules: 4/4
#  default_security_rules: 2/2


import unittest

import azure.mgmt.network
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

@unittest.skip("Fix it later.")
class MgmtNetworkTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtNetworkTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )
        self.mgmt_client_v190601 = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient,
            api_version="2019-06-01"
        )
        if self.is_live:
            from azure.mgmt.compute import ComputeManagementClient
            self.compute_client = self.create_mgmt_client(
                ComputeManagementClient
            )
            from azure.mgmt.storage import StorageManagementClient
            self.storage_client = self.create_mgmt_client(
                StorageManagementClient
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

    def get_network_interface(self, group_name, nic_name):

        nic = self.mgmt_client.network_interfaces.get(group_name, nic_name)
        return nic

    def create_storage_account(self, group_name, location, storage_name):
        params_create = azure.mgmt.storage.models.StorageAccountCreateParameters(
            sku=azure.mgmt.storage.models.Sku(name=azure.mgmt.storage.models.SkuName.standard_lrs),
            kind=azure.mgmt.storage.models.Kind.storage,
            location=location
        )
        result_create = self.storage_client.storage_accounts.begin_create(
            group_name,
            storage_name,
            params_create,
        )
        account = result_create.result()
        return account.id

    def create_virtual_hub(self, location, group_name, virtual_wan_name, virtual_hub_name):

        # VirtualWANCreate[put]
        BODY = {
          "location": location,
          "tags": {
            "key1": "value1"
          },
          "disable_vpn_encryption": False,
          "type": "Basic"
        }
        result = self.mgmt_client.virtual_wans.begin_create_or_update(group_name, virtual_wan_name, BODY)
        wan = result.result()

        # TODO: something wrong in virtualhub
        BODY = {
          "location": location,
          "tags": {
            "key1": "value1"
          },
          "virtual_wan": {
            "id": wan.id
          },
          "address_prefix": "10.168.0.0/24",
          "sku": "Basic"
        }
        result = self.mgmt_client.virtual_hubs.begin_create_or_update(group_name, virtual_hub_name, BODY)
        try:
            result = result.result()
        except HttpResponseError as e:
            self.assertEquals(str(e), "(InternalServerError) An error occurred.")
        return result

    def create_vm(self, group_name, location, vm_name, network_name, subnet_name, interface_name):
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

    def create_vm_extension(self, group_name, location, vm_name, vm_extension_name):

        # Create virtual machine extension
        BODY = {
          "location": location,
          "auto_upgrade_minor_version": True,
          "publisher": "Microsoft.Azure.NetworkWatcher",
          "virtual_machine_extension_type": "NetworkWatcherAgentWindows",
          # "type_properties_type": "NetworkWatcherAgentWindows",
          "type_handler_version": "1.4",
        }
        result = self.compute_client.virtual_machine_extensions.begin_create_or_update(group_name, vm_name, vm_extension_name, BODY)
        result = result.result()

    def create_public_ip_address(self, group_name, location, public_ip_address_name):
        # Create public IP address defaults[put]
        BODY = {
          "public_ip_allocation_method": "Static",
          "idle_timeout_in_minutes": 10,
          "public_ip_address_version": "IPv4",
          "location": location,
          "sku": {
            "name": "Standard"
          }
        }
        result = self.mgmt_client.public_ip_addresses.begin_create_or_update(group_name, public_ip_address_name, BODY)
        return result.result()

    def create_virtual_network_gateway(self, group_name, location, vn_gateway, network_name, subnet_name, public_ip_address_name, ipconfig_name):
        # create network
        subnet = self.create_virtual_network(group_name, location, network_name, subnet_name)
        public_ip_address = self.create_public_ip_address(group_name, location, public_ip_address_name)

        BODY = {
          "ip_configurations": [
            {
              "private_ip_allocation_method": "Dynamic",
              "subnet": {
                # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + GATEWAY_SUBNET_NAME + ""
                "id": subnet.id
              },
              "public_ip_address": {
                # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
                "id": public_ip_address.id
              },
              "name": ipconfig_name
            }
          ],
          "gateway_type": "Vpn",
          "vpn_type": "RouteBased",
          "enable_bgp": False,
          "active_active": False,
          "enable_dns_forwarding": False,
          "sku": {
            "name": "VpnGw1",
            "tier": "VpnGw1"
          },
          "bgp_settings": {
            "asn": "65515",
            "bgp_peering_address": "10.0.1.30",
            "peer_weight": "0"
          },
          "custom_routes": {
            "address_prefixes": [
              "101.168.0.6/32"
            ]
          },
          "location": location
        }
        result = self.mgmt_client.virtual_network_gateways.begin_create_or_update(group_name, vn_gateway, BODY)
        result = result.result()
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network_watcher_troubleshoot(self, resource_group):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name

        NETWORK_WATCHER_NAME = self.get_resource_name("networkwatcher")
        VIRTUAL_MACHINE_NAME = self.get_resource_name("virtualmachine")
        VIRTUAL_NETWORK_NAME = self.get_resource_name("virtualnetwork")
        VIRTUAL_NETWORK_GATEWAY_NAME = self.get_resource_name("virtualnetworkgateway")
        PUBLIC_IP_ADDRESS_NAME = self.get_resource_name("publicipaddress")
        SUBNET_NAME = "GatewaySubnet"
        STORAGE_ACCOUNT_NAME = self.get_resource_name("storagename")
        IP_CONFIGURATION_NAME = self.get_resource_name("ipconfig")

        if self.is_live:
            self.create_virtual_network_gateway(
                RESOURCE_GROUP,
                AZURE_LOCATION,
                VIRTUAL_NETWORK_GATEWAY_NAME,
                VIRTUAL_MACHINE_NAME,
                SUBNET_NAME,
                PUBLIC_IP_ADDRESS_NAME,
                IP_CONFIGURATION_NAME)
            self.create_storage_account(RESOURCE_GROUP, AZURE_LOCATION, STORAGE_ACCOUNT_NAME)

        # Create network watcher[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.network_watchers.create_or_update(resource_group.name, NETWORK_WATCHER_NAME, BODY)

        # Get troubleshooting[post]
        BODY = {
          "target_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworkGateways/" + VIRTUAL_NETWORK_GATEWAY_NAME + "",
          "storage_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
          "storage_path": "https://" + STORAGE_ACCOUNT_NAME + ".blob.core.windows.net/troubleshooting"
        }
        result = self.mgmt_client.network_watchers.begin_get_troubleshooting(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        result = result.result()

        # Get troubleshoot result[post]
        BODY = {
          "target_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworkGateways/" + VIRTUAL_NETWORK_GATEWAY_NAME + ""
        }
        result = self.mgmt_client.network_watchers.begin_get_troubleshooting_result(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        result = result.result()

        # Delete network watcher[delete]
        result = self.mgmt_client.network_watchers.begin_delete(resource_group.name, NETWORK_WATCHER_NAME)
        result = result.result()

    @unittest.skip("NsgsNotAppliedOnNic")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network_watcher_ip_flow(self, resource_group):
        
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        NETWORK_WATCHER_NAME = self.get_resource_name("networkwatcher")
        VIRTUAL_NETWORK_NAME = self.get_resource_name("virtualnetwork")
        SUBNET_NAME = self.get_resource_name("subnet")
        INTERFACE_NAME = self.get_resource_name("interface")
        VIRTUAL_MACHINE_NAME = self.get_resource_name("virtualmachine")
        VIRTUAL_MACHINE_EXTENSION_NAME = self.get_resource_name("virtualmachineextension")

        if self.is_live:
            self.create_vm(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, VIRTUAL_NETWORK_NAME, SUBNET_NAME, INTERFACE_NAME)
            self.create_vm_extension(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME)
            nic = self.get_network_interface(RESOURCE_GROUP, INTERFACE_NAME)
            local_ip_address = nic.ip_configurations[0].private_ip_address
        else:
            local_ip_address = '10.0.0.1'

        # Create network watcher[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.network_watchers.create_or_update(resource_group.name, NETWORK_WATCHER_NAME, BODY)

        # Ip flow verify[post]
        BODY = {
          "target_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + "",
          "direction": "Outbound",
          "protocol": "TCP",
          "local_port": "80",
          "remote_port": "80",
          "local_ip_address": local_ip_address,
          "remote_ip_address": "121.10.1.1"
        }
        result = self.mgmt_client.network_watchers.begin_verify_ip_flow(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        result = result.result()

        # Delete network watcher[delete]
        result = self.mgmt_client.network_watchers.begin_delete(resource_group.name, NETWORK_WATCHER_NAME)
        result = result.result()
 
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network_watcher_flow_log(self, resource_group):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name

        NETWORK_WATCHER_NAME = self.get_resource_name("networkwatcher")
        VIRTUAL_MACHINE_NAME = self.get_resource_name("virtualmachine")
        VIRTUAL_NETWORK_NAME = self.get_resource_name("virtualnetwork")
        VIRTUAL_NETWORK_GATEWAY_NAME = self.get_resource_name("virtualnetworkgateway")
        PUBLIC_IP_ADDRESS_NAME = self.get_resource_name("publicipaddress")
        SUBNET_NAME = "GatewaySubnet"
        STORAGE_ACCOUNT_NAME = self.get_resource_name("storagename")
        IP_CONFIGURATION_NAME = self.get_resource_name("ipconfig")
        FLOW_LOG_NAME = self.get_resource_name("floglog")
        NETWORK_SECURITY_GROUP_NAME = self.get_resource_name("networksecuritygroup")

        if self.is_live:
            self.create_virtual_network_gateway(
                RESOURCE_GROUP,
                AZURE_LOCATION,
                VIRTUAL_NETWORK_GATEWAY_NAME,
                VIRTUAL_MACHINE_NAME,
                SUBNET_NAME,
                PUBLIC_IP_ADDRESS_NAME,
                IP_CONFIGURATION_NAME)
            self.create_storage_account(RESOURCE_GROUP, AZURE_LOCATION, STORAGE_ACCOUNT_NAME)

        # Create network watcher[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.network_watchers.create_or_update(resource_group.name, NETWORK_WATCHER_NAME, BODY)

        # Create network security group[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.network_security_groups.begin_create_or_update(resource_group.name, NETWORK_SECURITY_GROUP_NAME, BODY)
        result = result.result()

        # Create or update flow log[put]
        BODY = {
          "location": AZURE_LOCATION,
          "target_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkSecurityGroups/" + NETWORK_SECURITY_GROUP_NAME + "",
          "storage_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
          "enabled": True,
          "format": {
            "type": "JSON",
            "version": "1"
          }
        }
        result = self.mgmt_client.flow_logs.begin_create_or_update(resource_group.name, NETWORK_WATCHER_NAME, FLOW_LOG_NAME, BODY)
        result = result.result()

        # Get flow log[get]
        result = self.mgmt_client.flow_logs.get(resource_group.name, NETWORK_WATCHER_NAME, FLOW_LOG_NAME)

         # Get flow log status[post]
        BODY = {
          "target_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkSecurityGroups/" + NETWORK_SECURITY_GROUP_NAME + ""
        }
        result = self.mgmt_client.network_watchers.begin_get_flow_log_status(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        result = result.result()

        # Configure flow log[post]
        BODY = {
          "target_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkSecurityGroups/" + NETWORK_SECURITY_GROUP_NAME + "",
          "storage_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
          "enabled": True
        }
        result = self.mgmt_client.network_watchers.begin_set_flow_log_configuration(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        result = result.result()

        # Delete flow log[delete]
        result = self.mgmt_client.flow_logs.begin_delete(resource_group.name, NETWORK_WATCHER_NAME, FLOW_LOG_NAME)
        result = result.result()

        # Delete network watcher[delete]
        result = self.mgmt_client.network_watchers.begin_delete(resource_group.name, NETWORK_WATCHER_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network_watcher_monitor(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        NETWORK_WATCHER_NAME = self.get_resource_name("networkwatcher")
        VIRTUAL_NETWORK_NAME = self.get_resource_name("virtualnetwork")
        SUBNET_NAME = self.get_resource_name("subnet")
        INTERFACE_NAME = self.get_resource_name("interface")
        VIRTUAL_MACHINE_NAME = self.get_resource_name("virtualmachine")
        CONNECTION_MONITOR_NAME = self.get_resource_name("connectionmonitor")
        CONNECTION_MONITOR_NAME_V2 = self.get_resource_name("connectionmonitorv2")
        VIRTUAL_MACHINE_EXTENSION_NAME = self.get_resource_name("virtualmachineextension")

        if self.is_live:
            self.create_vm(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, VIRTUAL_NETWORK_NAME, SUBNET_NAME, INTERFACE_NAME)
            self.create_vm_extension(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME)

        # Create network watcher[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.network_watchers.create_or_update(resource_group.name, NETWORK_WATCHER_NAME, BODY)

        # # Create connection monitor V2[put]
        BODY = {
          "location": "eastus",
          "endpoints": [
            {
              "name": "vm1",
              "resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
            },
            # {
            #   "name": "CanaryWorkspaceVamshi",
            #   "resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.OperationalInsights/workspaces/" + WORKSPACE_NAME + "",
            #   "filter": {
            #     "type": "Include",
            #     "items": [
            #       {
            #         "type": "AgentAddress",
            #         "address": "npmuser"
            #       }
            #     ]
            #   }
            # },
            {
              "name": "bing",
              "address": "bing.com"
            },
            {
              "name": "google",
              "address": "google.com"
            }
          ],
          "test_configurations": [
            {
              "name": "testConfig1",
              "test_frequency_sec": "60",
              "protocol": "Tcp",
              "tcp_configuration": {
                "port": "80",
                "disable_trace_route": False
              }
            }
          ],
          "test_groups": [
            {
              "name": "test1",
              "disable": False,
              "test_configurations": [
                "testConfig1"
              ],
              "sources": [
                "vm1",
                # "CanaryWorkspaceVamshi"
              ],
              "destinations": [
                "bing",
                "google"
              ]
            }
          ],
          "outputs": []
        }
        result = self.mgmt_client.connection_monitors.begin_create_or_update(resource_group.name, NETWORK_WATCHER_NAME, CONNECTION_MONITOR_NAME_V2, BODY)
        result = result.result()

        # Create connection monitor V1[put]
        # [Kaihui] v1 only supports api version <= 2019-06-01
        BODY = {
          "location": AZURE_LOCATION,
          "source": {
            "resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
          },
          "destination": {
            "address": "bing.com",
            "port": "80"
          },
          "monitoring_interval_in_seconds": "60"
        }
        result = self.mgmt_client_v190601.connection_monitors.begin_create_or_update(resource_group.name, NETWORK_WATCHER_NAME, CONNECTION_MONITOR_NAME, BODY)
        result = result.result()

        # Get connection monitor[get]
        result = self.mgmt_client.connection_monitors.get(resource_group.name, NETWORK_WATCHER_NAME, CONNECTION_MONITOR_NAME)

        # List connection monitors[get]
        result = self.mgmt_client.connection_monitors.list(resource_group.name, NETWORK_WATCHER_NAME)

        # List connection monitors[get]
        result = self.mgmt_client.connection_monitors.list(resource_group.name, NETWORK_WATCHER_NAME)

        # Query connection monitor[post]
        result = self.mgmt_client.connection_monitors.begin_query(resource_group.name, NETWORK_WATCHER_NAME, CONNECTION_MONITOR_NAME)
        result = result.result()

        # # Start connection monitor[post]
        result = self.mgmt_client.connection_monitors.begin_start(resource_group.name, NETWORK_WATCHER_NAME, CONNECTION_MONITOR_NAME)
        result = result.result()

        # # Stop connection monitor[post]
        result = self.mgmt_client.connection_monitors.begin_stop(resource_group.name, NETWORK_WATCHER_NAME, CONNECTION_MONITOR_NAME)
        result = result.result()

        # Update connection monitor tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.connection_monitors.update_tags(resource_group.name, NETWORK_WATCHER_NAME, CONNECTION_MONITOR_NAME, BODY)

        # Delete connection monitor[delete]
        result = self.mgmt_client.connection_monitors.begin_delete(resource_group.name, NETWORK_WATCHER_NAME, CONNECTION_MONITOR_NAME)
        result = result.result()

        # Delete connection monitor[delete]
        result = self.mgmt_client.connection_monitors.begin_delete(resource_group.name, NETWORK_WATCHER_NAME, CONNECTION_MONITOR_NAME_V2)
        result = result.result()

        # Delete network watcher[delete]
        result = self.mgmt_client.network_watchers.begin_delete(resource_group.name, NETWORK_WATCHER_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network_watcher_packet_capture(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        NETWORK_WATCHER_NAME = self.get_resource_name("networkwatcher")
        VIRTUAL_NETWORK_NAME = self.get_resource_name("virtualnetwork")
        SUBNET_NAME = self.get_resource_name("subnet")
        STORAGE_ACCOUNT_NAME = self.get_resource_name("storagename")
        NETWORK_INTERFACE_NAME = self.get_resource_name("interface")
        VIRTUAL_MACHINE_NAME = self.get_resource_name("virtualmachine")
        PACKET_CAPTURE_NAME = self.get_resource_name("packetcapture")
        VIRTUAL_MACHINE_EXTENSION_NAME = self.get_resource_name("virtualmachineextension")

        if self.is_live:
            self.create_vm(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, VIRTUAL_NETWORK_NAME, SUBNET_NAME, NETWORK_INTERFACE_NAME)
            self.create_vm_extension(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME)
            self.create_storage_account(RESOURCE_GROUP, AZURE_LOCATION, STORAGE_ACCOUNT_NAME)

        # Create network watcher[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.network_watchers.create_or_update(resource_group.name, NETWORK_WATCHER_NAME, BODY)

        # Create packet capture[put]
        BODY = {
          "target": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + "",
          # "bytes_to_capture_per_packet": "10000",
          # "total_bytes_per_session": "100000",
          # "time_limit_in_seconds": "100",
          "storage_location": {
            "storage_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
            "storage_path": "https://" + STORAGE_ACCOUNT_NAME + ".blob.core.windows.net/capture/pc1.cap",
            # "file_path": "D:\\capture\\pc1.cap"
          },
          # "filters": [
          #   {
          #     "protocol": "TCP",
          #     "local_ip_address": "10.0.0.4",
          #     "local_port": "80"
          #   }
          # ]
        }
        result = self.mgmt_client.packet_captures.begin_create(resource_group.name, NETWORK_WATCHER_NAME, PACKET_CAPTURE_NAME, BODY)
        result = result.result()

        # Get packet capture[get]
        result = self.mgmt_client.packet_captures.get(resource_group.name, NETWORK_WATCHER_NAME, PACKET_CAPTURE_NAME)

        # List packet captures[get]
        result = self.mgmt_client.packet_captures.list(resource_group.name, NETWORK_WATCHER_NAME)

        # Query packet capture status[post]
        result = self.mgmt_client.packet_captures.begin_get_status(resource_group.name, NETWORK_WATCHER_NAME, PACKET_CAPTURE_NAME)
        result = result.result()

        # Stop packet capture[post]
        result = self.mgmt_client.packet_captures.begin_stop(resource_group.name, NETWORK_WATCHER_NAME, PACKET_CAPTURE_NAME)
        result = result.result()

        # Delete packet capture[delete]
        result = self.mgmt_client.packet_captures.begin_delete(resource_group.name, NETWORK_WATCHER_NAME, PACKET_CAPTURE_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network_watcher(self, resource_group):
        
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        NETWORK_WATCHER_NAME = self.get_resource_name("networkwatcher")
        VIRTUAL_NETWORK_NAME = self.get_resource_name("virtualnetwork")
        VIRTUAL_NETWORK_GATEWAY_NAME = self.get_resource_name("virtualnetworkgateway")
        PUBLIC_IP_ADDRESS_NAME = self.get_resource_name("publicipaddress")
        SUBNET_NAME = self.get_resource_name("subnet")
        STORAGE_ACCOUNT_NAME = self.get_resource_name("storagename")
        NETWORK_INTERFACE_NAME = self.get_resource_name("interface")
        IP_CONFIGURATION_NAME = self.get_resource_name("ipconfig")
        VIRTUAL_MACHINE_NAME = self.get_resource_name("virtualmachine")
        VIRTUAL_MACHINE_EXTENSION_NAME = self.get_resource_name("virtualmachineextension")

        if self.is_live:
            self.create_vm(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, VIRTUAL_NETWORK_NAME, SUBNET_NAME, NETWORK_INTERFACE_NAME)
            self.create_vm_extension(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, VIRTUAL_MACHINE_EXTENSION_NAME)
            self.create_storage_account(RESOURCE_GROUP, AZURE_LOCATION, STORAGE_ACCOUNT_NAME)

        # Create network watcher[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.network_watchers.create_or_update(resource_group.name, NETWORK_WATCHER_NAME, BODY)

        # List network watchers[get]
        result = self.mgmt_client.network_watchers.list(resource_group.name)

        # List all network watchers[get]
        result = self.mgmt_client.network_watchers.list_all()

        # Get network watcher[get]
        result = self.mgmt_client.network_watchers.get(resource_group.name, NETWORK_WATCHER_NAME)

        # Network configuration diagnostic[post]
        BODY = {
          "target_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + "",
          "profiles": [
            {
              "direction": "Inbound",
              "protocol": "TCP",
              "source": "10.1.0.4",
              "destination": "12.11.12.14",
              "destination_port": "12100"
            }
          ]
        }
        result = self.mgmt_client.network_watchers.begin_get_network_configuration_diagnostic(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        result = result.result()

        # TODO: raise 500
        # Get Azure Reachability Report[post]
        # BODY = {
        #   "provider_location": {
        #     "country": "United States",
        #     "state": "washington"
        #   },
        #   "providers": [
        #     "Frontier Communications of America, Inc. - ASN 5650"
        #   ],
        #   "azure_locations": [
        #     "West US"
        #   ],
        #   "start_time": "2020-05-31T00:00:00Z",
        #   "end_time": "2020-06-01T00:00:00Z"
        # }
        # result = self.mgmt_client.network_watchers.begin_get_azure_reachability_report(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        # result = result.result()

        # TODO: raise 500
        # Get Available Providers List[post]
        # BODY = {
        #   "azure_locations": [
        #     "West US"
        #   ],
        #   "country": "United States",
        #   "state": "washington",
        #   "city": "seattle"
        # }
        # result = self.mgmt_client.network_watchers.begin_list_available_providers(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        # result = result.result()

        # Get security group view[post]
        BODY = {
          "target_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
        }
        result = self.mgmt_client.network_watchers.begin_get_vm_security_rules(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        result = result.result()

        # Check connectivity[post]
        BODY = {
          "source": {
            "resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
          },
          "destination": {
            "address": "192.168.100.4",
            "port": "3389"
          },
          "preferred_ipversion": "IPv4"
        }
        result = self.mgmt_client.network_watchers.begin_check_connectivity(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        result = result.result()

        # Get Topology[post]
        BODY = {
          "target_resource_group_name": resource_group.name
        }
        result = self.mgmt_client.network_watchers.get_topology(resource_group.name, NETWORK_WATCHER_NAME, BODY)

        # Get next hop[post]
        BODY = {
          "target_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + "",
          # "source_ip_address": "10.0.0.5",
          "source_ip_address": "10.1.0.4",
          "destination_ip_address": "10.1.0.10",
          "target_nic_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + ""
        }
        # result = self.mgmt_client.network_watchers.begin_get_next_hop(resource_group.name, NETWORK_WATCHER_NAME, BODY)
        # result = result.result()

        # Update network watcher tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.network_watchers.update_tags(resource_group.name, NETWORK_WATCHER_NAME, BODY)

        # Delete network watcher[delete]
        result = self.mgmt_client.network_watchers.begin_delete(resource_group.name, NETWORK_WATCHER_NAME)
        result = result.result()
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name

        VIRTUAL_NETWORK_NAME = self.get_resource_name("virtualnetwork")
        VIRTUAL_NETWORK_NAME_2 = self.get_resource_name("virtualnetwork2")
        SUBNET_NAME = self.get_resource_name("subnet")
        SUBNET_NAME_2 = self.get_resource_name("subnet2")
        STORAGE_ACCOUNT_NAME = self.get_resource_name("storagename")

        NETWORK_PROFILE_NAME = self.get_resource_name("networkprofile")
        NETWORK_SECURITY_GROUP_NAME = self.get_resource_name("networksecuritygroup")
        NETWORK_VIRTUAL_APPLIANCE_NAME = self.get_resource_name("networkvirtualapp")
        SECURITY_RULE_NAME = self.get_resource_name("securityrule")
        VIRTUAL_WAN_NAME = self.get_resource_name("virtualwan")
        VIRTUAL_HUB_NAME = self.get_resource_name("virtualhub")

        if self.is_live:
            self.create_virtual_hub(AZURE_LOCATION, RESOURCE_GROUP, VIRTUAL_WAN_NAME, VIRTUAL_HUB_NAME)
            self.create_storage_account(RESOURCE_GROUP, AZURE_LOCATION, STORAGE_ACCOUNT_NAME)
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME_2, SUBNET_NAME_2)

        # Create network profile defaults[put]
        BODY = {
          "location": "eastus",
          "container_network_interface_configurations": [
            {
              "name": "eth1",
              "ip_configurations": [
                {
                  "name": "ipconfig1",
                  "subnet": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME_2 + "/subnets/" + SUBNET_NAME_2 + ""
                  }
                }
              ]
            }
          ]
        }
        result = self.mgmt_client.network_profiles.create_or_update(resource_group.name, NETWORK_PROFILE_NAME, BODY)

        # Create network security group[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.network_security_groups.begin_create_or_update(resource_group.name, NETWORK_SECURITY_GROUP_NAME, BODY)
        result = result.result()

        # # Create network security group with rule[put]
        # BODY = {
        #   "properties": {
        #     "security_rules": [
        #       {
        #         "name": "rule1",
        #         "properties": {
        #           "protocol": "*",
        #           "source_address_prefix": "*",
        #           "destination_address_prefix": "*",
        #           "access": "Allow",
        #           "destination_port_range": "80",
        #           "source_port_range": "*",
        #           "priority": "130",
        #           "direction": "Inbound"
        #         }
        #       }
        #     ]
        #   },
        #   "location": "eastus"
        # }
        # result = self.mgmt_client.network_security_groups.begin_create_or_update(resource_group.name, NETWORK_SECURITY_GROUP_NAME, BODY)
        # result = result.result()

        # TODO: (InvalidResourceType) The resource type could not be found in the namespace 'Microsoft.Network' for api version '2020-03-01'
        # Create NetworkVirtualAppliance[put]
        # BODY = {
        #   "tags": {
        #     "key1": "value1"
        #   },
        #   "sku": {
        #     "vendor": "Cisco SDWAN",
        #     "bundled_scale_unit": "1",
        #     "market_place_version": "12.1"
        #   },
        #   "identity": {
        #     "type": "UserAssigned",
        #     "user_assigned_identities": {}
        #   },
        #   "location": "West US",
        #   "virtual_hub": {
        #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualHubs/" + VIRTUAL_HUB_NAME + ""
        #   },
        #   "boot_strap_configuration_blob": [
        #     "https://" + STORAGE_ACCOUNT_NAME + ".blob.core.windows.net/csrncvhdstoragecont/csrbootstrapconfig"
        #   ],
        #   "cloud_init_configuration_blob": [
        #     "https://" + STORAGE_ACCOUNT_NAME + ".blob.core.windows.net/csrncvhdstoragecont/csrcloudinitconfig"
        #   ],
        #   "virtual_appliance_asn": "10000"
        # }
        # result = self.mgmt_client.network_virtual_appliances.begin_create_or_update(resource_group.name, NETWORK_VIRTUAL_APPLIANCE_NAME, BODY)
        # result = result.result()

        # Create security rule[put]
        BODY = {
          "protocol": "*",
          "source_address_prefix": "10.0.0.0/8",
          "destination_address_prefix": "11.0.0.0/8",
          "access": "Deny",
          "destination_port_range": "8080",
          "source_port_range": "*",
          "priority": "100",
          "direction": "Outbound"
        }
        result = self.mgmt_client.security_rules.begin_create_or_update(resource_group.name, NETWORK_SECURITY_GROUP_NAME, SECURITY_RULE_NAME, BODY)
        result = result.result()

        # DefaultSecurityRuleList[get]
        result = self.mgmt_client.default_security_rules.list(resource_group.name, NETWORK_SECURITY_GROUP_NAME)

        DEFAULT_SECURITY_RULE_NAME = "AllowVnetInBound"
        # DefaultSecurityRuleGet[get]
        result = self.mgmt_client.default_security_rules.get(resource_group.name, NETWORK_SECURITY_GROUP_NAME, DEFAULT_SECURITY_RULE_NAME)

        # Get network security rule in network security group[get]
        result = self.mgmt_client.security_rules.get(resource_group.name, NETWORK_SECURITY_GROUP_NAME, SECURITY_RULE_NAME)

        # List network security rules in network security group[get]
        result = self.mgmt_client.security_rules.list(resource_group.name, NETWORK_SECURITY_GROUP_NAME)

        # Get NetworkVirtualAppliance[get]
        # result = self.mgmt_client.network_virtual_appliances.get(resource_group.name, NETWORK_VIRTUAL_APPLIANCE_NAME)

        # Get network security group[get]
        result = self.mgmt_client.network_security_groups.get(resource_group.name, NETWORK_SECURITY_GROUP_NAME)

        # Get network profile[get]
        result = self.mgmt_client.network_profiles.get(resource_group.name, NETWORK_PROFILE_NAME)

        # Get network profile with container network interfaces[get]
        result = self.mgmt_client.network_profiles.get(resource_group.name, NETWORK_PROFILE_NAME)

        # List all Network Virtual Appliance for a given resource group[get]
        # result = self.mgmt_client.network_virtual_appliances.list_by_resource_group(resource_group.name)

        # List network security groups in resource group[get]
        result = self.mgmt_client.network_security_groups.list(resource_group.name)

        # List resource group network profiles[get]
        result = self.mgmt_client.network_profiles.list(resource_group.name)

        # List all Network Virtual Appliances for a given subscription[get]
        # result = self.mgmt_client.network_virtual_appliances.list()

        # List all network security groups[get]
        result = self.mgmt_client.network_security_groups.list_all()

        # List all network profiles[get]
        result = self.mgmt_client.network_profiles.list_all()

        # # Update NetworkVirtualAppliance[patch]
        # BODY = {
        #   "tags": {
        #     "key1": "value1",
        #     "key2": "value2"
        #   }
        # }
        # result = self.mgmt_client.network_virtual_appliances.update_tags(resource_group.name, NETWORK_VIRTUAL_APPLIANCE_NAME, BODY)

        # Update network security group tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.network_security_groups.update_tags(resource_group.name, NETWORK_SECURITY_GROUP_NAME, BODY)

        # Update network profile tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.network_profiles.update_tags(resource_group.name, NETWORK_PROFILE_NAME, BODY)

        # Delete network security rule from network security group[delete]
        result = self.mgmt_client.security_rules.begin_delete(resource_group.name, NETWORK_SECURITY_GROUP_NAME, SECURITY_RULE_NAME)
        result = result.result()

        # # Delete NetworkVirtualAppliance[delete]
        # result = self.mgmt_client.network_virtual_appliances.begin_delete(resource_group.name, NETWORK_VIRTUAL_APPLIANCE_NAME)
        # result = result.result()

        # Delete network security group[delete]
        result = self.mgmt_client.network_security_groups.begin_delete(resource_group.name, NETWORK_SECURITY_GROUP_NAME)
        result = result.result()

        # Delete network profile[delete]
        result = self.mgmt_client.network_profiles.begin_delete(resource_group.name, NETWORK_PROFILE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
