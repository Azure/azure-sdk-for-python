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
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        VIRTUAL_NETWORK_NAME = "virtualnetworkname"

        """
        # CreateVirtualNetworkGatewayConnection_S2S[put]
        BODY = {
          "properties": {
            "virtual_network_gateway1": {
              "properties": {
                "ip_configurations": [
                  {
                    "properties": {
                      "private_ipallocation_method": "Dynamic",
                      "subnet": {
                        "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                      },
                      "public_ip_address": {
                        "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
                      }
                    },
                    "name": "gwipconfig1",
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
                  "bgp_peering_address": "10.0.1.30",
                  "peer_weight": "0"
                }
              },
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworkGateways/" + VIRTUAL_NETWORK_GATEWAY_NAME + "",
              "location": "centralus"
            },
            "local_network_gateway2": {
              "properties": {
                "local_network_address_space": {
                  "address_prefixes": [
                    "10.1.0.0/16"
                  ]
                },
                "gateway_ip_address": "x.x.x.x"
              },
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/localNetworkGateways/" + LOCAL_NETWORK_GATEWAY_NAME + "",
              "location": "centralus"
            },
            "connection_type": "IPsec",
            "connection_protocol": "IKEv2",
            "routing_weight": "0",
            "shared_key": "Abc123",
            "enable_bgp": False,
            "use_policy_based_traffic_selectors": False,
            "ipsec_policies": [],
            "traffic_selector_policies": []
          },
          "location": "centralus"
        }
        result = self.mgmt_client.virtual_network_gateway_connections.create_or_update(resource_group.name, CONNECTION_NAME, BODY)
        result = result.result()

        # Create virtual network with delegated subnets[put]
        BODY = {
          "properties": {
            "address_space": {
              "address_prefixes": [
                "10.0.0.0/16"
              ]
            },
            "subnets": [
              {
                "name": "test-1",
                "properties": {
                  "address_prefix": "10.0.0.0/24",
                  "delegations": [
                    {
                      "name": "myDelegation",
                      "properties": {
                        "service_name": "Microsoft.Sql/managedInstances"
                      }
                    }
                  ]
                }
              }
            ]
          },
          "location": "westcentralus"
        }
        result = self.mgmt_client.virtual_networks.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)
        result = result.result()

        # Create virtual network with subnet[put]
        BODY = {
          "properties": {
            "address_space": {
              "address_prefixes": [
                "10.0.0.0/16"
              ]
            },
            "subnets": [
              {
                "name": "test-1",
                "properties": {
                  "address_prefix": "10.0.0.0/24"
                }
              }
            ]
          },
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_networks.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)
        result = result.result()

        # Create virtual network with subnet containing address prefixes[put]
        BODY = {
          "properties": {
            "address_space": {
              "address_prefixes": [
                "10.0.0.0/16"
              ]
            },
            "subnets": [
              {
                "name": "test-2",
                "properties": {
                  "address_prefixes": [
                    "10.0.0.0/28",
                    "10.0.1.0/28"
                  ]
                }
              }
            ]
          },
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_networks.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)
        result = result.result()

        # Create virtual network with Bgp Communities[put]
        BODY = {
          "properties": {
            "address_space": {
              "address_prefixes": [
                "10.0.0.0/16"
              ]
            },
            "subnets": [
              {
                "name": "test-1",
                "properties": {
                  "address_prefix": "10.0.0.0/24"
                }
              }
            ],
            "bgp_communities": {
              "virtual_network_community": "12076:60000"
            }
          },
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_networks.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)
        result = result.result()

        # Create virtual network with service endpoints[put]
        BODY = {
          "properties": {
            "address_space": {
              "address_prefixes": [
                "10.0.0.0/16"
              ]
            },
            "subnets": [
              {
                "name": "test-1",
                "properties": {
                  "address_prefix": "10.0.0.0/16",
                  "service_endpoints": [
                    {
                      "service": "Microsoft.Storage"
                    }
                  ]
                }
              }
            ]
          },
          "location": "eastus"
        }
        result = self.mgmt_client.virtual_networks.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)
        result = result.result()

        # Create virtual network with service endpoints and service endpoint policy[put]
        BODY = {
          "properties": {
            "address_space": {
              "address_prefixes": [
                "10.0.0.0/16"
              ]
            },
            "subnets": [
              {
                "name": "test-1",
                "properties": {
                  "address_prefix": "10.0.0.0/16",
                  "service_endpoints": [
                    {
                      "service": "Microsoft.Storage"
                    }
                  ],
                  "service_endpoint_policies": [
                    {
                      "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/serviceEndpointPolicies/" + SERVICE_ENDPOINT_POLICY_NAME + ""
                    }
                  ]
                }
              }
            ]
          },
          "location": "eastus2euap"
        }
        result = self.mgmt_client.virtual_networks.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)
        result = result.result()
        """

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

        """
        # SetVirtualNetworkGatewayConnectionSharedKey[put]
        BODY = {
          "value": "AzureAbc123"
        }
        result = self.mgmt_client.virtual_network_gateway_connections.set_shared_key(resource_group.name, CONNECTION_NAME, BODY)
        result = result.result()

        # Create Virtual Network Tap[put]
        BODY = {
          "properties": {
            "destination_network_interface_ipconfiguration": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NETWORK_INTERFACE_NAME + "/ipConfigurations/" + IP_CONFIGURATION_NAME + ""
            }
          },
          "location": "centraluseuap"
        }
        result = self.mgmt_client.virtual_network_taps.create_or_update(resource_group.name, VIRTUAL_NETWORK_TAP_NAME, BODY)
        result = result.result()

        # CreateLocalNetworkGateway[put]
        BODY = {
          "properties": {
            "local_network_address_space": {
              "address_prefixes": [
                "10.1.0.0/16"
              ]
            },
            "gateway_ip_address": "11.12.13.14"
          },
          "location": "Central US"
        }
        result = self.mgmt_client.local_network_gateways.create_or_update(resource_group.name, LOCAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # UpdateVirtualNetworkGateway[put]
        BODY = {
          "properties": {
            "ip_configurations": [
              {
                "properties": {
                  "private_ipallocation_method": "Dynamic",
                  "subnet": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                  },
                  "public_ip_address": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
                  }
                },
                "name": "gwipconfig1"
              }
            ],
            "gateway_type": "Vpn",
            "vpn_type": "RouteBased",
            "enable_bgp": False,
            "active_active": False,
            "enable_dns_forwarding": True,
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
            }
          },
          "location": "centralus"
        }
        result = self.mgmt_client.virtual_network_gateways.create_or_update(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # Create subnet with a delegation[put]
        BODY = {
          "properties": {
            "address_prefix": "10.0.0.0/16"
          }
        }
        result = self.mgmt_client.subnets.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME, BODY)
        result = result.result()

        # Create subnet[put]
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

        # Create peering[put]
        BODY = {
          "properties": {
            "allow_virtual_network_access": True,
            "allow_forwarded_traffic": True,
            "allow_gateway_transit": False,
            "use_remote_gateways": False,
            "remote_virtual_network": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + ""
            }
          }
        }
        result = self.mgmt_client.virtual_network_peerings.create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, VIRTUAL_NETWORK_PEERING_NAME, BODY)
        result = result.result()

        # Get peering[get]
        result = self.mgmt_client.virtual_network_peerings.get(resource_group.name, VIRTUAL_NETWORK_NAME, VIRTUAL_NETWORK_PEERING_NAME)

        # Get Service Association Links[get]
        result = self.mgmt_client.service_association_links.list(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

        # Get Resource Navigation Links[get]
        result = self.mgmt_client.resource_navigation_links.list(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        """

        # Check IP address availability[get]
        result = self.mgmt_client.virtual_networks.check_ip_address_availability(resource_group.name, VIRTUAL_NETWORK_NAME)

        """
        # VirtualNetworkGatewaysListConnections[get]
        result = self.mgmt_client.virtual_network_gateways.list_connections(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)

        # Get subnet[get]
        result = self.mgmt_client.subnets.get(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

        # Get subnet with a delegation[get]
        result = self.mgmt_client.subnets.get(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

        # List peerings[get]
        result = self.mgmt_client.virtual_network_peerings.list(resource_group.name, VIRTUAL_NETWORK_NAME)

        # GetVirtualNetworkGateway[get]
        result = self.mgmt_client.virtual_network_gateways.get(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)

        # GetLocalNetworkGateway[get]
        result = self.mgmt_client.local_network_gateways.get(resource_group.name, LOCAL_NETWORK_GATEWAY_NAME)

        # List subnets[get]
        result = self.mgmt_client.subnets.list(resource_group.name, VIRTUAL_NETWORK_NAME)

        # Get Virtual Network Tap[get]
        result = self.mgmt_client.virtual_network_taps.get(resource_group.name, VIRTUAL_NETWORK_TAP_NAME)
        """

        # VnetGetUsage[get]
        result = self.mgmt_client.virtual_networks.list_usage(resource_group.name, VIRTUAL_NETWORK_NAME)

        """
        # GetVirtualNetworkGatewayConnectionSharedKey[get]
        result = self.mgmt_client.virtual_network_gateway_connections.get_shared_key(resource_group.name, CONNECTION_NAME)
        """

        # Get virtual network[get]
        result = self.mgmt_client.virtual_networks.get(resource_group.name, VIRTUAL_NETWORK_NAME)

        """
        # Get virtual network with a delegated subnet[get]
        result = self.mgmt_client.virtual_networks.get(resource_group.name, VIRTUAL_NETWORK_NAME)

        # Get virtual network with service association links[get]
        result = self.mgmt_client.virtual_networks.get(resource_group.name, VIRTUAL_NETWORK_NAME)

        # GetVirtualNetworkGatewayConnection[get]
        result = self.mgmt_client.virtual_network_gateway_connections.get(resource_group.name, CONNECTION_NAME)

        # ListVirtualNetworkGatewaysinResourceGroup[get]
        result = self.mgmt_client.virtual_network_gateways.list(resource_group.name)

        # ListLocalNetworkGateways[get]
        result = self.mgmt_client.local_network_gateways.list(resource_group.name)

        # List virtual network taps in resource group[get]
        result = self.mgmt_client.virtual_network_taps.list_by_resource_group(resource_group.name)
        """

        # List virtual networks in resource group[get]
        result = self.mgmt_client.virtual_networks.list(resource_group.name)

        """
        # ListVirtualNetworkGatewayConnectionsinResourceGroup[get]
        result = self.mgmt_client.virtual_network_gateway_connections.list(resource_group.name)

        # List all virtual network taps[get]
        result = self.mgmt_client.virtual_network_taps.list_all()
        """

        # List all virtual networks[get]
        result = self.mgmt_client.virtual_networks.list_all()

        """
        # Disconnect VpnConnections from Virtual Network Gateway[post]
        BODY = {
          "vpn_connection_ids": [
            "vpnconnId1",
            "vpnconnId2"
          ]
        }
        result = self.mgmt_client.virtual_network_gateways.disconnect_virtual_network_gateway_vpn_connections(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # Unprepare Network Policies[post]
        BODY = {
          "service_name": "Microsoft.Sql/managedInstances"
        }
        result = self.mgmt_client.subnets.unprepare_network_policies(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME, BODY)
        result = result.result()

        # Prepare Network Policies[post]
        BODY = {
          "service_name": "Microsoft.Sql/managedInstances"
        }
        result = self.mgmt_client.subnets.prepare_network_policies(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME, BODY)
        result = result.result()

        # GetVirtualNetworkGatewayVpnclientConnectionHealth[post]
        result = self.mgmt_client.virtual_network_gateways.get_vpnclient_connection_health(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # Get VirtualNetworkGateway VpnClientIpsecParameters[post]
        result = self.mgmt_client.virtual_network_gateways.get_vpnclient_ipsec_parameters(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

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
        result = self.mgmt_client.virtual_network_gateways.set_vpnclient_ipsec_parameters(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # GenerateVPNClientPackage[post]
        BODY = {}
        result = self.mgmt_client.virtual_network_gateways.generatevpnclientpackage(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # ResetVpnClientSharedKey[post]
        result = self.mgmt_client.virtual_network_gateways.reset_vpn_client_shared_key(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # GetVirtualNetworkGatewayVPNProfilePackageURL[post]
        result = self.mgmt_client.virtual_network_gateways.get_vpn_profile_package_url(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # ListVirtualNetworkGatewaySupportedVPNDevices[post]
        result = self.mgmt_client.virtual_network_gateways.supported_vpn_devices(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)

        # GetVirtualNetworkGatewayAdvertisedRoutes[post]
        result = self.mgmt_client.virtual_network_gateways.get_advertised_routes(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # GenerateVirtualNetworkGatewayVPNProfile[post]
        BODY = {}
        result = self.mgmt_client.virtual_network_gateways.generate_vpn_profile(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # Start packet capture on virtual network gateway with filter[post]
        BODY = {
          "filter_data": "{'TracingFlags': 11,'MaxPacketBufferSize': 120,'MaxFileSize': 200,'Filters': [{'SourceSubnets': ['20.1.1.0/24'],'DestinationSubnets': ['10.1.1.0/24'],'SourcePort': [500],'DestinationPort': [4500],'Protocol': 6,'TcpFlags': 16,'CaptureSingleDirectionTrafficOnly': true}]}"
        }
        result = self.mgmt_client.virtual_network_gateways.start_packet_capture(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # Start packet capture on virtual network gateway without filter[post]
        result = self.mgmt_client.virtual_network_gateways.start_packet_capture(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # Stop packet capture on virtual network gateway[post]
        BODY = {
          "sas_url": "https://teststorage.blob.core.windows.net/?sv=2018-03-28&ss=bfqt&srt=sco&sp=rwdlacup&se=2019-09-13T07:44:05Z&st=2019-09-06T23:44:05Z&spr=https&sig=V1h9D1riltvZMI69d6ihENnFo%2FrCvTqGgjO2lf%2FVBhE%3D"
        }
        result = self.mgmt_client.virtual_network_gateways.stop_packet_capture(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # GetVirtualNetworkGatewayBGPPeerStatus[post]
        result = self.mgmt_client.virtual_network_gateways.get_bgp_peer_status(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # GetVirtualNetworkGatewayLearnedRoutes[post]
        result = self.mgmt_client.virtual_network_gateways.get_learned_routes(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # ResetVirtualNetworkGatewayConnectionSharedKey[post]
        BODY = {
          "key_length": "128"
        }
        result = self.mgmt_client.virtual_network_gateway_connections.reset_shared_key(resource_group.name, CONNECTION_NAME, SHAREDKEY_NAME, BODY)
        result = result.result()

        # ResetVirtualNetworkGateway[post]
        result = self.mgmt_client.virtual_network_gateways.reset(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # GetVPNDeviceConfigurationScript[post]
        BODY = {
          "vendor": "Cisco",
          "device_family": "ISR",
          "firmware_version": "IOS 15.1 (Preview)"
        }
        result = self.mgmt_client.virtual_network_gateways.vpn_device_configuration_script(resource_group.name, CONNECTION_NAME, BODY)

        # UpdateVirtualNetworkGatewayTags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.virtual_network_gateways.update_tags(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME, BODY)
        result = result.result()

        # UpdateLocalNetworkGatewayTags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.local_network_gateways.update_tags(resource_group.name, LOCAL_NETWORK_GATEWAY_NAME, BODY)

        # Start packet capture on virtual network gateway connection without filter[post]
        result = self.mgmt_client.virtual_network_gateway_connections.start_packet_capture(resource_group.name, CONNECTION_NAME)
        result = result.result()

        # Start packet capture on virtual network gateway connection with filter[post]
        BODY = {
          "filter_data": "{'TracingFlags': 11,'MaxPacketBufferSize': 120,'MaxFileSize': 200,'Filters': [{'SourceSubnets': ['20.1.1.0/24'],'DestinationSubnets': ['10.1.1.0/24'],'SourcePort': [500],'DestinationPort': [4500],'Protocol': 6,'TcpFlags': 16,'CaptureSingleDirectionTrafficOnly': true}]}"
        }
        result = self.mgmt_client.virtual_network_gateway_connections.start_packet_capture(resource_group.name, CONNECTION_NAME, BODY)
        result = result.result()

        # Stop packet capture on virtual network gateway connection[post]
        BODY = {
          "sas_url": "https://teststorage.blob.core.windows.net/?sv=2018-03-28&ss=bfqt&srt=sco&sp=rwdlacup&se=2019-09-13T07:44:05Z&st=2019-09-06T23:44:05Z&spr=https&sig=V1h9D1riltvZMI69d6ihENnFo%2FrCvTqGgjO2lf%2FVBhE%3D"
        }
        result = self.mgmt_client.virtual_network_gateway_connections.stop_packet_capture(resource_group.name, CONNECTION_NAME, BODY)
        result = result.result()

        # Update virtual network tap tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.virtual_network_taps.update_tags(resource_group.name, VIRTUAL_NETWORK_TAP_NAME, BODY)
        """

        # Update virtual network tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.virtual_networks.update_tags(resource_group.name, VIRTUAL_NETWORK_NAME, BODY["tags"])

        """
        # UpdateVirtualNetworkGatewayConnectionTags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.virtual_network_gateway_connections.update_tags(resource_group.name, CONNECTION_NAME, BODY)
        result = result.result()

        # Delete peering[delete]
        result = self.mgmt_client.virtual_network_peerings.delete(resource_group.name, VIRTUAL_NETWORK_NAME, VIRTUAL_NETWORK_PEERING_NAME)
        result = result.result()

        # Delete subnet[delete]
        result = self.mgmt_client.subnets.delete(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        result = result.result()

        # DeleteVirtualNetworkGateway[delete]
        result = self.mgmt_client.virtual_network_gateways.delete(resource_group.name, VIRTUAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # DeleteLocalNetworkGateway[delete]
        result = self.mgmt_client.local_network_gateways.delete(resource_group.name, LOCAL_NETWORK_GATEWAY_NAME)
        result = result.result()

        # Delete Virtual Network Tap resource[delete]
        result = self.mgmt_client.virtual_network_taps.delete(resource_group.name, VIRTUAL_NETWORK_TAP_NAME)
        result = result.result()
        """

        # Delete virtual network[delete]
        result = self.mgmt_client.virtual_networks.begin_delete(resource_group.name, VIRTUAL_NETWORK_NAME)
        result = result.result()

        """
        # DeleteVirtualNetworkGatewayConnection[delete]
        result = self.mgmt_client.virtual_network_gateway_connections.delete(resource_group.name, CONNECTION_NAME)
        result = result.result()
        """


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
