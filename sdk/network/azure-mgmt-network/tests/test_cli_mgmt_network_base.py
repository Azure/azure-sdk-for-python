# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 63
# Methods Covered : 63
# Examples Total  : 76
# Examples Tested : 76
# Coverage %      : 100
# ----------------------

# covered ops:
#   virtual_networks: 8/8
#   virtual_network_taps: 0/6  TODO: SubscriptionNotRegisteredForFeature.
#   virtual_network_peerings: 4/4
#   virtual_network_gateways: 12/22  TODO: others need vpnclient
#   virtual_network_gateway_connections: 8/10  TODO: Start packet capture return 500
#   local_network_gateways: 5/5
#   subnets: 4/6  TODO: SubscriptionNotRegisteredForFeature in Prepare/Unprepare Network Policies
#   service_association_links: 1/1
#   resource_navigation_links: 1/1
#   virtual_routers: 0/5  #TODO:PutVirtualRouter feature not enabled
#   virtual_router_peerings: 0/4

import unittest
import time

from azure.core.exceptions import HttpResponseError
import azure.mgmt.network
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtNetworkTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtNetworkTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

    def create_network_interface(self, group_name, location, nic_name, subnet_id, ipconfig):

        async_nic_creation = self.mgmt_client.network_interfaces.begin_create_or_update(
            group_name,
            nic_name,
            {
                'location': location,
                'ip_configurations': [{
                    'name': ipconfig,
                    'subnet': {
                        'id': subnet_id
                    }
                }]
            }
        )
        nic_info = async_nic_creation.result()

        return nic_info

    def delete_network_interface(self, group_name, nic_name):
        result = self.mgmt_client.network_interfaces.begin_delete(group_name, nic_name)
        return result.result()

    def create_public_ip_addresses(self, group_name, location, public_ip_name):
        # Create PublicIP
        BODY = {
            'location': location,
            'public_ip_allocation_method': 'Dynamic',
            'idle_timeout_in_minutes': 4
        }
        result = self.mgmt_client.public_ip_addresses.begin_create_or_update(
            group_name,
            public_ip_name,
            BODY
        )
        return result.result()
   
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        

        VIRTUAL_NETWORK_NAME = "virtualnetworkname"
        REMOTE_VIRTUAL_NETWORK_NAME = "rmvirtualnetworkname"
        VIRTUAL_NETWORK_TAP_NAME = "virtualnetworktapname"
        NETWORK_INTERFACE_NAME = "networkinterfacename"
        VIRTUAL_NETWORK_PEERING_NAME = "virtualnetworkpeeringname"
        PUBLIC_IP_ADDRESS_NAME = "publicipname"
        VIRTUAL_NETWORK_GATEWAY_NAME = "virtualnetworkgatewayname"
        LOCAL_NETWORK_GATEWAY_NAME = "localnetworkgatewayname"
        IP_CONFIGURATION_NAME = "ipconfig"
        CONNECTION_NAME = "connectionname"
        SUBNET_NAME = "subnetname"
        GATEWAY_SUBNET_NAME = "GatewaySubnet"
        VIRTUAL_ROUTER_NAME = "virtualroute"

        self.create_public_ip_addresses(resource_group.name, AZURE_LOCATION, PUBLIC_IP_ADDRESS_NAME)

        # Create virtual network[put]
        BODY = {
          "address_space": {
            "address_prefixes": [
              "10.0.0.0/16"
            ]
          },
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_networks.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)
        result = result.result()

        # Create remote virtual network[put]
        BODY = {
          "address_space": {
            "address_prefixes": [
              "10.2.0.0/16"
            ]
          },
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_networks.begin_create_or_update(resource_group.name, REMOTE_VIRTUAL_NETWORK_NAME, BODY)
        result = result.result()

        # Create subnet[put]
        BODY = {
          "address_prefix": "10.0.0.0/24"
        }
        result = self.mgmt_client.subnets.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME, BODY)
        subnet = result.result()

        self.create_network_interface(resource_group.name, AZURE_LOCATION, NETWORK_INTERFACE_NAME, subnet.id, IP_CONFIGURATION_NAME)

        # Create gateway subnet[put]
        BODY = {
          "address_prefix": "10.0.1.0/24"
        }
        result = self.mgmt_client.subnets.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, GATEWAY_SUBNET_NAME, BODY)
        subnet = result.result()

        # TODO: NOT ALLOW
        # Create Virtual Network Tap[put]
        # BODY = {
        #   "destination_network_interface_ip_configuration": {
        #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "/ipConfigurations/" + IP_CONFIGURATION_NAME + ""
        #   },
        #   "location": "eastus"
        # }
        # result = self.mgmt_client.virtual_network_taps.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_TAP_NAME, BODY)
        # result = result.result()

        # CreateLocalNetworkGateway[put]
        BODY = {
          "local_network_address_space": {
            "address_prefixes": [
              "10.1.0.0/16"
            ]
          },
          "gateway_ip_address": "11.12.13.14",
          "location": "eastus"
        }
        result = self.mgmt_client.local_network_gateways.begin_create_or_update(resource_group.name, LOCAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # UpdateVirtualNetworkGateway[put]
        BODY = {
          "ip_configurations": [
            {
              "private_ip_allocation_method": "Dynamic",
              "subnet": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + GATEWAY_SUBNET_NAME + ""
              },
              "public_ip_address": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
              },
              "name": IP_CONFIGURATION_NAME
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
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_network_gateways.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # TODO:PutVirtualRouter feature not enabled
        # Create VirtualRouter[put]
        # BODY = {
        #   "tags": {
        #     "key1": "value1"
        #   },
        #   "location": "West US",
        #   "hosted_gateway": {
        #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworkGateways/" + VIRTUAL_NETWORK_GATEWAY_NAME + ""
        #   }
        # }
        # result = self.mgmt_client.virtual_routers.begin_create_or_update(resource_group.name, VIRTUAL_ROUTER_NAME, BODY)
        # result = result.result()

        # # Create Virtual Router Peering[put]
        # BODY = {
        #   "properties": {
        #     "peer_ip": "192.168.1.5",
        #     "peer_asn": "20000"
        #   }
        # }
        # result = self.mgmt_client.virtual_router_peerings.create_or_update(resource_group.name, VIRTUAL_ROUTER_NAME, PEERING_NAME, BODY)
        # result = result.result()


        """
        # Create subnet with a delegation[put]
        BODY = {
          "properties": {
            "address_prefix": "10.0.0.0/16"
          }
        }
        result = self.mgmt_client.subnets.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME, BODY)
        result = result.result()

        # Create subnet with service endpoints[put]
        BODY = {
          "properties": {
            "address_prefix": "10.0.0.0/16",
            "service_endpoints": [
              {
                "service": "Microsoft.Storage"
              }
            ]
          }
        }
        result = self.mgmt_client.subnets.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME, BODY)
        result = result.result()
        """

        # Create peering[put]
        BODY = {
          "allow_virtual_network_access": True,
          "allow_forwarded_traffic": True,
          "allow_gateway_transit": False,
          "use_remote_gateways": False,
          "remote_virtual_network": {
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + REMOTE_VIRTUAL_NETWORK_NAME + ""
          }
        }
        result = self.mgmt_client.virtual_network_peerings.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, VIRTUAL_NETWORK_PEERING_NAME, BODY)
        result = result.result()

        # CreateVirtualNetworkGatewayConnection_S2S[put]
        BODY = {
          "virtual_network_gateway1": {
            "ip_configurations": [
              {
                "private_ip_allocation_method": "Dynamic",
                "subnet": {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + GATEWAY_SUBNET_NAME + ""
                },
                "public_ip_address": {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
                },
                "name": IP_CONFIGURATION_NAME,
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworkGateways/" + VIRTUAL_NETWORK_GATEWAY_NAME + "/ipConfigurations/" + IP_CONFIGURATION_NAME + ""
              }
            ],
            "gateway_type": "Vpn",
            "vpn_type": "RouteBased",
            "enable_bgp": False,
            "active_active": False,
            "sku": {
              "name": "VpnGw1",
              "tier": "VpnGw1"
            },
            "bgp_settings": {
              "asn": "65514",
              "bgp_peering_address": "10.0.2.30",
              "peer_weight": "0"
            },
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworkGateways/" + VIRTUAL_NETWORK_GATEWAY_NAME + "",
            "location": "eastus"
          },
          "local_network_gateway2": {
            "local_network_address_space": {
              "address_prefixes": [
                "10.1.0.0/16"
              ]
            },
            "gateway_ip_address": "10.1.0.1",
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/localNetworkGateways/" + LOCAL_NETWORK_GATEWAY_NAME + "",
            "location": "eastus"
          },
          "connection_type": "IPsec",
          "connection_protocol": "IKEv2",
          "routing_weight": "0",
          "shared_key": "Abc123",
          "enable_bgp": False,
          "use_policy_based_traffic_selectors": False,
          "ipsec_policies": [],
          "traffic_selector_policies": [],
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_network_gateway_connections.begin_create_or_update(resource_group.name, CONNECTION_NAME, BODY)
        result = result.result()

        # SetVirtualNetworkGatewayConnectionSharedKey[put]
        BODY = {
          "value": "AzureAbc123"
        }
        result = self.mgmt_client.virtual_network_gateway_connections.begin_set_shared_key(resource_group.name, CONNECTION_NAME, BODY)
        result = result.result()

        # Get VirtualRouter[get]
        # result = self.mgmt_client.virtual_routers.get(resource_group.name, VIRTUAL_ROUTER_NAME)

        # # Get Virtual Router Peering[get]
        # result = self.mgmt_client.virtual_router_peerings.get(resource_group.name, VIRTUAL_ROUTER_NAME, PEERING_NAME)

        # Get peering[get]
        result = self.mgmt_client.virtual_network_peerings.get(resource_group.name, VIRTUAL_NETWORK_NAME, VIRTUAL_NETWORK_PEERING_NAME)

        # Get Service Association Links[get]
        result = self.mgmt_client.service_association_links.list(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

        # Get Resource Navigation Links[get]
        result = self.mgmt_client.resource_navigation_links.list(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

        # Check IP address availability[get]
        IP_ADDRESS = "10.0.1.4"
        result = self.mgmt_client.virtual_networks.check_ip_address_availability(resource_group.name, VIRTUAL_NETWORK_NAME, IP_ADDRESS)

        # VirtualNetworkGatewaysListConnections[get]
        result = self.mgmt_client.virtual_network_gateways.list_connections(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)

        # Get subnet[get]
        result = self.mgmt_client.subnets.get(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

        """
        # Get subnet with a delegation[get]
        result = self.mgmt_client.subnets.get(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        """

        # List peerings[get]
        result = self.mgmt_client.virtual_network_peerings.list(resource_group.name, VIRTUAL_NETWORK_NAME)

        # List all Virtual Router for a given resource group[get]
        # result = self.mgmt_client.virtual_routers.list_by_resource_group(resource_group.name)

        # # List all Virtual Router Peerings for a given Virtual Router[get]
        # result = self.mgmt_client.virtual_router_peerings.list(resource_group.name, VIRTUAL_ROUTER_NAME)

        # GetVirtualNetworkGateway[get]
        result = self.mgmt_client.virtual_network_gateways.get(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)

        # GetLocalNetworkGateway[get]
        result = self.mgmt_client.local_network_gateways.get(resource_group.name, LOCAL_NETWORK_GATEWAY_NAME)

        # List subnets[get]
        result = self.mgmt_client.subnets.list(resource_group.name, VIRTUAL_NETWORK_NAME)

        # TODO: NOT ALLOW
        # # Get Virtual Network Tap[get]
        # result = self.mgmt_client.virtual_network_taps.get(resource_group.name, VIRTUAL_NETWORK_TAP_NAME)

        # VnetGetUsage[get]
        result = self.mgmt_client.virtual_networks.list_usage(resource_group.name, VIRTUAL_NETWORK_NAME)

        # GetVirtualNetworkGatewayConnectionSharedKey[get]
        result = self.mgmt_client.virtual_network_gateway_connections.get_shared_key(resource_group.name, CONNECTION_NAME)

        # Get virtual network[get]
        result = self.mgmt_client.virtual_networks.get(resource_group.name, VIRTUAL_NETWORK_NAME)

        """
        # Get virtual network with a delegated subnet[get]
        result = self.mgmt_client.virtual_networks.get(resource_group.name, VIRTUAL_NETWORK_NAME)

        # Get virtual network with service association links[get]
        result = self.mgmt_client.virtual_networks.get(resource_group.name, VIRTUAL_NETWORK_NAME)
        """

        # GetVirtualNetworkGatewayConnection[get]
        result = self.mgmt_client.virtual_network_gateway_connections.get(resource_group.name, CONNECTION_NAME)

        # ListVirtualNetworkGatewaysinResourceGroup[get]
        result = self.mgmt_client.virtual_network_gateways.list(resource_group.name)

        # ListLocalNetworkGateways[get]
        result = self.mgmt_client.local_network_gateways.list(resource_group.name)

        # TODO: NOT ALLOW
        # List virtual network taps in resource group[get]
        # result = self.mgmt_client.virtual_network_taps.list_by_resource_group(resource_group.name)

        # List virtual networks in resource group[get]
        result = self.mgmt_client.virtual_networks.list(resource_group.name)

        # ListVirtualNetworkGatewayConnectionsinResourceGroup[get]
        result = self.mgmt_client.virtual_network_gateway_connections.list(resource_group.name)

        # TODO: NOT ALLOW
        # List all virtual network taps[get]
        # result = self.mgmt_client.virtual_network_taps.list_all()

        # List all virtual networks[get]
        result = self.mgmt_client.virtual_networks.list_all()

        # List all Virtual Routers for a given subscription[get]
        # result = self.mgmt_client.virtual_routers.list()

        # TODO: NEED VPN CLIENT
        # Disconnect VpnConnections from Virtual Network Gateway[post]
        # BODY = {
        #   "vpn_connection_ids": [
        #     # "vpnconnId1",
        #     # "vpnconnId2"
        #   ]
        # }
        # result = self.mgmt_client.virtual_network_gateways.begin_disconnect_virtual_network_gateway_vpn_connections(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY["vpn_connection_ids"])
        # result = result.result()

        # TODO: SubscriptionNotRegisteredForFeature
        # Prepare Network Policies[post]
        # BODY = {
        #   "service_name": "Microsoft.Sql/managedInstances"
        # }
        # result = self.mgmt_client.subnets.begin_prepare_network_policies(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME, BODY["service_name"])
        # result = result.result()

        # TODO: SubscriptionNotRegisteredForFeature
        # Unprepare Network Policies[post]
        # BODY = {
        #   "service_name": "Microsoft.Sql/managedInstances"
        # }
        # result = self.mgmt_client.subnets.begin_unprepare_network_policies(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME, BODY["service_name"])
        # result = result.result()

        """ TODO: NEED VPN CLIENT
        # GetVirtualNetworkGatewayVpnclientConnectionHealth[post]
        # result = self.mgmt_client.virtual_network_gateways.begin_get_vpnclient_connection_health(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        # result = result.result()

        # Get VirtualNetworkGateway VpnClientIpsecParameters[post]
        # result = self.mgmt_client.virtual_network_gateways.begin_get_vpnclient_ipsec_parameters(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        # result = result.result()

        # Set VirtualNetworkGateway VpnClientIpsecParameters[post]
        BODY = {
          "sa_life_time_seconds": "86473",
          "sa_data_size_kilobytes": "429497",
          "ipsec_encryption": "AES256",
          "ipsec_integrity": "SHA256",
          "ike_encryption": "AES256",
          "ike_integrity": "SHA384",
          "dh_group": "DHGroup2",
          "pfs_group": "PFS2"
        }
        result = self.mgmt_client.virtual_network_gateways.begin_set_vpnclient_ipsec_parameters(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # GenerateVPNClientPackage[post]
        BODY = {}
        result = self.mgmt_client.virtual_network_gateways.begin_generatevpnclientpackage(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # ResetVpnClientSharedKey[post]
        result = self.mgmt_client.virtual_network_gateways.begin_reset_vpn_client_shared_key(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # GetVirtualNetworkGatewayVPNProfilePackageURL[post]
        result = self.mgmt_client.virtual_network_gateways.begin_get_vpn_profile_package_url(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # ListVirtualNetworkGatewaySupportedVPNDevices[post]
        result = self.mgmt_client.virtual_network_gateways.begin_supported_vpn_devices(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        """

        # GetVirtualNetworkGatewayAdvertisedRoutes[post]
        # PEER = "test"
        PEER = "10.0.0.2"
        result = self.mgmt_client.virtual_network_gateways.begin_get_advertised_routes(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, PEER)
        result = result.result()

        # TODO: NEED VPN CLIENT
        # GenerateVirtualNetworkGatewayVPNProfile[post]
        # BODY = {}
        # result = self.mgmt_client.virtual_network_gateways.begin_generate_vpn_profile(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        # result = result.result()

        # Start packet capture on virtual network gateway with filter[post]
        # BODY = {
        #   "filter_data": "{'TracingFlags': 11,'MaxPacketBufferSize': 120,'MaxFileSize': 200,'Filters': [{'SourceSubnets': ['20.1.1.0/24'],'DestinationSubnets': ['10.1.1.0/24'],'SourcePort': [500],'DestinationPort': [4500],'Protocol': 6,'TcpFlags': 16,'CaptureSingleDirectionTrafficOnly': true}]}"
        # }
        # result = self.mgmt_client.virtual_network_gateways.begin_start_packet_capture(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY["filter_data"])
        # result = result.result()

        # TODO: need fix sas_url later
        # Start packet capture on virtual network gateway without filter[post]
        # result = self.mgmt_client.virtual_network_gateways.begin_start_packet_capture(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        # result = result.result()

        # Stop packet capture on virtual network gateway[post]
        # BODY = {
        #   "sas_url": "fakeuri"
        # }
        # result = self.mgmt_client.virtual_network_gateways.begin_stop_packet_capture(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        # result = result.result()

        # GetVirtualNetworkGatewayBGPPeerStatus[post]
        result = self.mgmt_client.virtual_network_gateways.begin_get_bgp_peer_status(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # GetVirtualNetworkGatewayLearnedRoutes[post]
        result = self.mgmt_client.virtual_network_gateways.begin_get_learned_routes(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # ResetVirtualNetworkGatewayConnectionSharedKey[post]
        BODY = {
          "key_length": "128"
        }
        result = self.mgmt_client.virtual_network_gateway_connections.begin_reset_shared_key(resource_group.name, CONNECTION_NAME, BODY)
        result = result.result()

        # ResetVirtualNetworkGateway[post]
        result = self.mgmt_client.virtual_network_gateways.begin_reset(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # TODO: NEED VPN CLIENT
        # GetVPNDeviceConfigurationScript[post]
        # BODY = {
        #   "vendor": "Cisco",
        #   "device_family": "ISR",
        #   "firmware_version": "IOS 15.1 (Preview)"
        # }
        # result = self.mgmt_client.virtual_network_gateways.vpn_device_configuration_script(resource_group.name, CONNECTION_NAME, BODY)

        # UpdateVirtualNetworkGatewayTags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.virtual_network_gateways.begin_update_tags(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # UpdateLocalNetworkGatewayTags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.local_network_gateways.update_tags(resource_group.name, LOCAL_NETWORK_GATEWAY_NAME, BODY)

        # TODO:(InternalServerError) An error occurred.
        # Start packet capture on virtual network gateway connection without filter[post]
        # result = self.mgmt_client.virtual_network_gateway_connections.begin_start_packet_capture(resource_group.name, CONNECTION_NAME)
        # result = result.result()

        # Start packet capture on virtual network gateway connection with filter[post]
        # BODY = {
        #   "filter_data": "{'TracingFlags': 11,'MaxPacketBufferSize': 120,'MaxFileSize': 200,'Filters': [{'SourceSubnets': ['20.1.1.0/24'],'DestinationSubnets': ['10.1.1.0/24'],'SourcePort': [500],'DestinationPort': [4500],'Protocol': 6,'TcpFlags': 16,'CaptureSingleDirectionTrafficOnly': true}]}"
        # }
        # result = self.mgmt_client.virtual_network_gateway_connections.begin_start_packet_capture(resource_group.name, CONNECTION_NAME, BODY["filter_data"])
        # result = result.result()

        # Stop packet capture on virtual network gateway connection[post]
        # BODY = {
        #   "sas_url": "fakeuri"
        # }
        # result = self.mgmt_client.virtual_network_gateway_connections.begin_stop_packet_capture(resource_group.name, CONNECTION_NAME)
        # result = result.result()

        # TODO: NOT ALLOW
        # Update virtual network tap tags[patch]
        # BODY = {
        #   "tags": {
        #     "tag1": "value1",
        #     "tag2": "value2"
        #   }
        # }
        # result = self.mgmt_client.virtual_network_taps.update_tags(resource_group.name, VIRTUAL_NETWORK_TAP_NAME, BODY["tags"])

        # Update virtual network tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.virtual_networks.update_tags(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)

        # UpdateVirtualNetworkGatewayConnectionTags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.virtual_network_gateway_connections.begin_update_tags(resource_group.name, CONNECTION_NAME, BODY["tags"])
        result = result.result()

        # DeleteVirtualNetworkGatewayConnection[delete]
        result = self.mgmt_client.virtual_network_gateway_connections.begin_delete(resource_group.name, CONNECTION_NAME)
        result = result.result()

        # Delete peering[delete]
        result = self.mgmt_client.virtual_network_peerings.begin_delete(resource_group.name, VIRTUAL_NETWORK_NAME, VIRTUAL_NETWORK_PEERING_NAME)
        result = result.result()

        # # Delete VirtualRouterPeering[delete]
        # result = self.mgmt_client.virtual_router_peerings.delete(resource_group.name, VIRTUAL_ROUTER_NAME, PEERING_NAME)
        # result = result.result()

        # Delete VirtualRouter[delete]
        # result = self.mgmt_client.virtual_routers.begin_delete(resource_group.name, VIRTUAL_ROUTER_NAME)
        # result = result.result()

        # DeleteVirtualNetworkGateway[delete]
        times = 0
        for i in range(4):
          try:
              # TODO: not sure why something in progress makes this failed. so try 3 times.
              result = self.mgmt_client.virtual_network_gateways.begin_delete(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
              result = result.result()
          except HttpResponseError:
              if i >= 3:
                  raise HttpResponseError()
              else:
                  time.sleep(120)

        # DeleteLocalNetworkGateway[delete]
        result = self.mgmt_client.local_network_gateways.begin_delete(resource_group.name, LOCAL_NETWORK_GATEWAY_NAME)
        result = result.result()
        
        self.delete_network_interface(RESOURCE_GROUP, NETWORK_INTERFACE_NAME)

        # Delete subnet[delete]
        result = self.mgmt_client.subnets.begin_delete(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        result = result.result()

        # TODO: NOT ALLOW
        # Delete Virtual Network Tap resource[delete]
        # result = self.mgmt_client.virtual_network_taps.begin_delete(resource_group.name, VIRTUAL_NETWORK_TAP_NAME)
        # result = result.result()

        # Delete virtual network[delete]
        result = self.mgmt_client.virtual_networks.begin_delete(resource_group.name, VIRTUAL_NETWORK_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()