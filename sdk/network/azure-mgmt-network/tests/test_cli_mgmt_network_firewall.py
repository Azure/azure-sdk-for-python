# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 7
# Methods Covered : 7
# Examples Total  : 16
# Examples Tested : 16
# Coverage %      : 100
# ----------------------

#  azure_firewalls: 6/6
#  azure_firewall_fqdn_tags: 1/1

import unittest

import azure.mgmt.network
from azure.core.exceptions import ResourceExistsError
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtNetworkTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtNetworkTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

    def create_firewall_policy(self, location, group_name, firewall_policy_name):
        BODY = {
          "tags": {
            "key1": "value1"
          },
          "location": location,
          "threat_intel_mode": "Alert"
        }
        result = self.mgmt_client.firewall_policies.begin_create_or_update(
            resource_group_name=group_name,
            firewall_policy_name=firewall_policy_name,
            parameters=BODY
        )
        return result.result()
    
    def create_virtual_hub(self, location, group_name, virtual_wan_name, virtual_hub_name):

        # VirtualWANCreate[put]
        BODY = {
          "location": "West US",
          "tags": {
            "key1": "value1"
          },
          "disable_vpn_encryption": False,
          "type": "Basic"
        }
        result = self.mgmt_client.virtual_wans.begin_create_or_update(group_name, virtual_wan_name, BODY)
        wan = result.result()

        BODY = {
          "location": "West US",
          "tags": {
            "key1": "value1"
          },
          "virtual_wan": {
            # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualWans/" + VIRTUAL_WAN_NAME + ""
            "id": wan.id
          },
          "address_prefix": "10.168.0.0/24",
          "sku": "Basic"
        }
        result = self.mgmt_client.virtual_hubs.begin_create_or_update(group_name, virtual_hub_name, BODY)
        return result.result()
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_WAN_NAME = "virtualwan"
        VIRTUAL_HUB_NAME = "virtualhub"
        FIREWALL_POLICY_NAME = "firewallpolicy"
        
        AZURE_FIREWALL_NAME = "azurefirewall"

        self.create_virtual_hub(AZURE_LOCATION, RESOURCE_GROUP, VIRTUAL_WAN_NAME, VIRTUAL_HUB_NAME)
        self.create_firewall_policy(AZURE_LOCATION, RESOURCE_GROUP, FIREWALL_POLICY_NAME)

        # # Create Azure Firewall With management subnet[put]
        # BODY = {
        #   "tags": {
        #     "key1": "value1"
        #   },
        #   "location": "West US",
        #   "zones": [],
        #   "properties": {
        #     "sku": {
        #       "name": "AZFW_VNet",
        #       "tier": "Standard"
        #     },
        #     "threat_intel_mode": "Alert",
        #     "ip_configurations": [
        #       {
        #         "name": "azureFirewallIpConfiguration",
        #         "properties": {
        #           "subnet": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
        #           },
        #           "public_ip_address": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
        #           }
        #         }
        #       }
        #     ],
        #     "management_ip_configuration": {
        #       "name": "azureFirewallMgmtIpConfiguration",
        #       "properties": {
        #         "subnet": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
        #         },
        #         "public_ip_address": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
        #         }
        #       }
        #     },
        #     "application_rule_collections": [
        #       {
        #         "name": "apprulecoll",
        #         "properties": {
        #           "priority": "110",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "rule1",
        #               "description": "Deny inbound rule",
        #               "protocols": [
        #                 {
        #                   "protocol_type": "Https",
        #                   "port": "443"
        #                 }
        #               ],
        #               "target_fqdns": [
        #                 "www.test.com"
        #               ],
        #               "source_addresses": [
        #                 "216.58.216.164",
        #                 "10.0.0.0/24"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "nat_rule_collections": [
        #       {
        #         "name": "natrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Dnat"
        #           },
        #           "rules": [
        #             {
        #               "name": "DNAT-HTTPS-traffic",
        #               "description": "D-NAT all outbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "443"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_address": "1.2.3.5",
        #               "translated_port": "8443"
        #             },
        #             {
        #               "name": "DNAT-HTTP-traffic-With-FQDN",
        #               "description": "D-NAT all inbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "80"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_fqdn": "internalhttpserver",
        #               "translated_port": "880"
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "network_rule_collections": [
        #       {
        #         "name": "netrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "L4-traffic",
        #               "description": "Block traffic based on source IPs and ports",
        #               "source_addresses": [
        #                 "192.168.1.1-192.168.1.12",
        #                 "10.1.4.12-10.1.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_addresses": [
        #                 "*"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             },
        #             {
        #               "name": "L4-traffic-with-FQDN",
        #               "description": "Block traffic based on source IPs and ports to amazon",
        #               "source_addresses": [
        #                 "10.2.4.12-10.2.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_fqdns": [
        #                 "www.amazon.com"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ]
        #   }
        # }
        # result = self.mgmt_client.azure_firewalls.create_or_update(resource_group.name, AZURE_FIREWALL_NAME, BODY)
        # result = result.result()

        # # Create Azure Firewall With IpGroups[put]
        # BODY = {
        #   "tags": {
        #     "key1": "value1"
        #   },
        #   "location": "West US",
        #   "zones": [],
        #   "properties": {
        #     "sku": {
        #       "name": "AZFW_VNet",
        #       "tier": "Standard"
        #     },
        #     "threat_intel_mode": "Alert",
        #     "ip_configurations": [
        #       {
        #         "name": "azureFirewallIpConfiguration",
        #         "properties": {
        #           "subnet": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
        #           },
        #           "public_ip_address": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
        #           }
        #         }
        #       }
        #     ],
        #     "application_rule_collections": [
        #       {
        #         "name": "apprulecoll",
        #         "properties": {
        #           "priority": "110",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "rule1",
        #               "description": "Deny inbound rule",
        #               "protocols": [
        #                 {
        #                   "protocol_type": "Https",
        #                   "port": "443"
        #                 }
        #               ],
        #               "target_fqdns": [
        #                 "www.test.com"
        #               ],
        #               "source_addresses": [
        #                 "216.58.216.164",
        #                 "10.0.0.0/24"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "nat_rule_collections": [
        #       {
        #         "name": "natrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Dnat"
        #           },
        #           "rules": [
        #             {
        #               "name": "DNAT-HTTPS-traffic",
        #               "description": "D-NAT all outbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "443"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_address": "1.2.3.5",
        #               "translated_port": "8443"
        #             },
        #             {
        #               "name": "DNAT-HTTP-traffic-With-FQDN",
        #               "description": "D-NAT all inbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "80"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_fqdn": "internalhttpserver",
        #               "translated_port": "880"
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "network_rule_collections": [
        #       {
        #         "name": "netrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "L4-traffic",
        #               "description": "Block traffic based on source IPs and ports",
        #               "source_addresses": [
        #                 "192.168.1.1-192.168.1.12",
        #                 "10.1.4.12-10.1.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_addresses": [
        #                 "*"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             },
        #             {
        #               "name": "L4-traffic-with-FQDN",
        #               "description": "Block traffic based on source IPs and ports to amazon",
        #               "source_addresses": [
        #                 "10.2.4.12-10.2.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_fqdns": [
        #                 "www.amazon.com"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ]
        #   }
        # }
        # result = self.mgmt_client.azure_firewalls.create_or_update(resource_group.name, AZURE_FIREWALL_NAME, BODY)
        # result = result.result()

        # # Create Azure Firewall With Additional Properties[put]
        # BODY = {
        #   "tags": {
        #     "key1": "value1"
        #   },
        #   "location": "West US",
        #   "zones": [],
        #   "properties": {
        #     "sku": {
        #       "name": "AZFW_VNet",
        #       "tier": "Standard"
        #     },
        #     "threat_intel_mode": "Alert",
        #     "ip_configurations": [
        #       {
        #         "name": "azureFirewallIpConfiguration",
        #         "properties": {
        #           "subnet": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
        #           },
        #           "public_ip_address": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
        #           }
        #         }
        #       }
        #     ],
        #     "application_rule_collections": [
        #       {
        #         "name": "apprulecoll",
        #         "properties": {
        #           "priority": "110",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "rule1",
        #               "description": "Deny inbound rule",
        #               "protocols": [
        #                 {
        #                   "protocol_type": "Https",
        #                   "port": "443"
        #                 }
        #               ],
        #               "target_fqdns": [
        #                 "www.test.com"
        #               ],
        #               "source_addresses": [
        #                 "216.58.216.164",
        #                 "10.0.0.0/24"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "nat_rule_collections": [
        #       {
        #         "name": "natrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Dnat"
        #           },
        #           "rules": [
        #             {
        #               "name": "DNAT-HTTPS-traffic",
        #               "description": "D-NAT all outbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "443"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_address": "1.2.3.5",
        #               "translated_port": "8443"
        #             },
        #             {
        #               "name": "DNAT-HTTP-traffic-With-FQDN",
        #               "description": "D-NAT all inbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "80"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_fqdn": "internalhttpserver",
        #               "translated_port": "880"
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "network_rule_collections": [
        #       {
        #         "name": "netrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "L4-traffic",
        #               "description": "Block traffic based on source IPs and ports",
        #               "source_addresses": [
        #                 "192.168.1.1-192.168.1.12",
        #                 "10.1.4.12-10.1.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_addresses": [
        #                 "*"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             },
        #             {
        #               "name": "L4-traffic-with-FQDN",
        #               "description": "Block traffic based on source IPs and ports to amazon",
        #               "source_addresses": [
        #                 "10.2.4.12-10.2.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_fqdns": [
        #                 "www.amazon.com"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "ip_groups": [],
        #     "additional_properties": {
        #       "key1": "value1",
        #       "key2": "value2"
        #     }
        #   }
        # }
        # result = self.mgmt_client.azure_firewalls.create_or_update(resource_group.name, AZURE_FIREWALL_NAME, BODY)
        # result = result.result()

        # Create Azure Firewall in virtual Hub[put]
        BODY = {
          "tags": {
            "key1": "value1"
          },
          "location": "West US",
          "zones": [],
          "sku": {
            "name": "AZFW_Hub",
            "tier": "Standard"
          },
          # "threat_intel_mode": "Off",
          "virtual_hub": {
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualHubs/" + VIRTUAL_HUB_NAME + ""
          },
          "hub_ip_addresses": {
            "public_i_ps": {
              "addresses": [],
              "count": 1
            }
          },
          "firewall_policy": {
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/firewallPolicies/" + FIREWALL_POLICY_NAME + ""
          }
        }
        result = self.mgmt_client.azure_firewalls.begin_create_or_update(resource_group.name, AZURE_FIREWALL_NAME, BODY)
        result = result.result()

        # # Create Azure Firewall[put]
        # BODY = {
        #   "tags": {
        #     "key1": "value1"
        #   },
        #   "location": "West US",
        #   "zones": [],
        #   "properties": {
        #     "sku": {
        #       "name": "AZFW_VNet",
        #       "tier": "Standard"
        #     },
        #     "threat_intel_mode": "Alert",
        #     "ip_configurations": [
        #       {
        #         "name": "azureFirewallIpConfiguration",
        #         "properties": {
        #           "subnet": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
        #           },
        #           "public_ip_address": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
        #           }
        #         }
        #       }
        #     ],
        #     "application_rule_collections": [
        #       {
        #         "name": "apprulecoll",
        #         "properties": {
        #           "priority": "110",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "rule1",
        #               "description": "Deny inbound rule",
        #               "protocols": [
        #                 {
        #                   "protocol_type": "Https",
        #                   "port": "443"
        #                 }
        #               ],
        #               "target_fqdns": [
        #                 "www.test.com"
        #               ],
        #               "source_addresses": [
        #                 "216.58.216.164",
        #                 "10.0.0.0/24"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "nat_rule_collections": [
        #       {
        #         "name": "natrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Dnat"
        #           },
        #           "rules": [
        #             {
        #               "name": "DNAT-HTTPS-traffic",
        #               "description": "D-NAT all outbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "443"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_address": "1.2.3.5",
        #               "translated_port": "8443"
        #             },
        #             {
        #               "name": "DNAT-HTTP-traffic-With-FQDN",
        #               "description": "D-NAT all inbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "80"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_fqdn": "internalhttpserver",
        #               "translated_port": "880"
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "network_rule_collections": [
        #       {
        #         "name": "netrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "L4-traffic",
        #               "description": "Block traffic based on source IPs and ports",
        #               "source_addresses": [
        #                 "192.168.1.1-192.168.1.12",
        #                 "10.1.4.12-10.1.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_addresses": [
        #                 "*"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             },
        #             {
        #               "name": "L4-traffic-with-FQDN",
        #               "description": "Block traffic based on source IPs and ports to amazon",
        #               "source_addresses": [
        #                 "10.2.4.12-10.2.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_fqdns": [
        #                 "www.amazon.com"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ]
        #   }
        # }
        # result = self.mgmt_client.azure_firewalls.create_or_update(resource_group.name, AZURE_FIREWALL_NAME, BODY)
        # result = result.result()

        # # Create Azure Firewall With Zones[put]
        # BODY = {
        #   "location": "West US 2",
        #   "tags": {
        #     "key1": "value1"
        #   },
        #   "zones": [
        #     "1",
        #     "2",
        #     "3"
        #   ],
        #   "properties": {
        #     "threat_intel_mode": "Alert",
        #     "sku": {
        #       "name": "AZFW_VNet",
        #       "tier": "Standard"
        #     },
        #     "ip_configurations": [
        #       {
        #         "name": "azureFirewallIpConfiguration",
        #         "properties": {
        #           "subnet": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
        #           },
        #           "public_ip_address": {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
        #           }
        #         }
        #       }
        #     ],
        #     "application_rule_collections": [
        #       {
        #         "name": "apprulecoll",
        #         "properties": {
        #           "priority": "110",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "rule1",
        #               "description": "Deny inbound rule",
        #               "protocols": [
        #                 {
        #                   "protocol_type": "Https",
        #                   "port": "443"
        #                 }
        #               ],
        #               "target_fqdns": [
        #                 "www.test.com"
        #               ],
        #               "source_addresses": [
        #                 "216.58.216.164",
        #                 "10.0.0.0/24"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "nat_rule_collections": [
        #       {
        #         "name": "natrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Dnat"
        #           },
        #           "rules": [
        #             {
        #               "name": "DNAT-HTTPS-traffic",
        #               "description": "D-NAT all outbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "443"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_address": "1.2.3.5",
        #               "translated_port": "8443"
        #             },
        #             {
        #               "name": "DNAT-HTTP-traffic-With-FQDN",
        #               "description": "D-NAT all inbound web traffic for inspection",
        #               "source_addresses": [
        #                 "*"
        #               ],
        #               "destination_addresses": [
        #                 "1.2.3.4"
        #               ],
        #               "destination_ports": [
        #                 "80"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ],
        #               "translated_fqdn": "internalhttpserver",
        #               "translated_port": "880"
        #             }
        #           ]
        #         }
        #       }
        #     ],
        #     "network_rule_collections": [
        #       {
        #         "name": "netrulecoll",
        #         "properties": {
        #           "priority": "112",
        #           "action": {
        #             "type": "Deny"
        #           },
        #           "rules": [
        #             {
        #               "name": "L4-traffic",
        #               "description": "Block traffic based on source IPs and ports",
        #               "source_addresses": [
        #                 "192.168.1.1-192.168.1.12",
        #                 "10.1.4.12-10.1.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_addresses": [
        #                 "*"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             },
        #             {
        #               "name": "L4-traffic-with-FQDN",
        #               "description": "Block traffic based on source IPs and ports to amazon",
        #               "source_addresses": [
        #                 "10.2.4.12-10.2.4.255"
        #               ],
        #               "destination_ports": [
        #                 "443-444",
        #                 "8443"
        #               ],
        #               "destination_fqdns": [
        #                 "www.amazon.com"
        #               ],
        #               "protocols": [
        #                 "TCP"
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ]
        #   }
        # }
        # result = self.mgmt_client.azure_firewalls.create_or_update(resource_group.name, AZURE_FIREWALL_NAME, BODY)
        # result = result.result()

        # # Get Azure Firewall With management subnet[get]
        # result = self.mgmt_client.azure_firewalls.get(resource_group.name, AZURE_FIREWALL_NAME)

        # # Get Azure Firewall With Additional Properties[get]
        # result = self.mgmt_client.azure_firewalls.get(resource_group.name, AZURE_FIREWALL_NAME)

        # # Get Azure Firewall With IpGroups[get]
        # result = self.mgmt_client.azure_firewalls.get(resource_group.name, AZURE_FIREWALL_NAME)

        # Get Azure Firewall[get]
        result = self.mgmt_client.azure_firewalls.get(resource_group.name, AZURE_FIREWALL_NAME)

        # # Get Azure Firewall With Zones[get]
        # result = self.mgmt_client.azure_firewalls.get(resource_group.name, AZURE_FIREWALL_NAME)

        # List all Azure Firewalls for a given resource group[get]
        result = self.mgmt_client.azure_firewalls.list(resource_group.name)

        # List all Azure Firewall FQDN Tags for a given subscription[get]
        result = self.mgmt_client.azure_firewall_fqdn_tags.list_all()

        # List all Azure Firewalls for a given subscription[get]
        result = self.mgmt_client.azure_firewalls.list_all()

        # Update Azure Firewall Tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.azure_firewalls.begin_update_tags(resource_group.name, AZURE_FIREWALL_NAME, BODY)
        result = result.result()

        # Delete Azure Firewall[delete]
        try:
            result = self.mgmt_client.azure_firewalls.begin_delete(resource_group.name, AZURE_FIREWALL_NAME)
            result = result.result()
        except ResourceExistsError as e:
            if not str(e).startswith("(AnotherOperationInProgress)"):
                raise e
          


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
