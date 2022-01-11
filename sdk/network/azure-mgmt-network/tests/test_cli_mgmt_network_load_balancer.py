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
# Examples Total  : 26
# Examples Tested : 26
# Coverage %      : 100
# ----------------------

#  load_balancers:  6/6
#  inbound_nat_rules:  4/4
#  load_balancer_frontend_ip_configurations:  2/2
#  load_balancer_backend_address_pools:  2/2
#  load_balancer_load_balancing_rules:  2/2
#  load_balancer_outbound_rules:  2/2
#  load_balancer_probes:  2/2
#  load_balancer_network_interfaces:  1/1

import unittest

import azure.mgmt.network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
import pytest

AZURE_LOCATION = 'eastus'


@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

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
        result = result.result()

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

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_NETWORK_NAME = "virtualnetwork"
        SUBNET_NAME = "subnet"
        PUBLIC_IP_ADDRESS_NAME = "public_ip_address_name"
        LOAD_BALANCER_NAME = "myLoadBalancer"
        INBOUND_NAT_RULE_NAME = "myInboundNatRule"
        FRONTEND_IPCONFIGURATION_NAME = "myFrontendIpconfiguration"
        BACKEND_ADDRESS_POOL_NAME = "myBackendAddressPool"
        LOAD_BALANCING_RULE_NAME = "myLoadBalancingRule"
        OUTBOUND_RULE_NAME = "myOutboundRule"
        PROBE_NAME = "myProbe"

        # self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        self.create_public_ip_address(RESOURCE_GROUP, AZURE_LOCATION, PUBLIC_IP_ADDRESS_NAME)

        # Create load balancer
        BODY = {
          "location": "eastus",
          "sku": {
            "name": "Standard"
          },
          "frontendIPConfigurations": [
            {
              "name": FRONTEND_IPCONFIGURATION_NAME,
              # "subnet": {
              #   "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME
              # }
              "public_ip_address": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME 
              }
            }
          ],
          "backend_address_pools": [
            {
              "name": BACKEND_ADDRESS_POOL_NAME
            }
          ],
          "load_balancing_rules": [
            {
              "name": LOAD_BALANCING_RULE_NAME,
              "frontend_ip_configuration": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "/frontendIPConfigurations/" + FRONTEND_IPCONFIGURATION_NAME
              },
              "frontend_port": "80",
              "backend_port": "80",
              "enable_floating_ip": True,
              "idle_timeout_in_minutes": "15",
              "protocol": "Tcp",
              "load_distribution": "Default",
              "disable_outbound_snat": True,
              "backend_address_pool": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "/backendAddressPools/" + BACKEND_ADDRESS_POOL_NAME
              },
              "probe": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "/probes/" + PROBE_NAME
              }
            }
          ],
          "probes": [
            {
              "name": PROBE_NAME,
              "protocol": "Http",
              "port": "80",
              "request_path": "healthcheck.aspx",
              "interval_in_seconds": "15",
              "number_of_probes": "2"
            }
          ],
          "outbound_rules": [
            {
              "name": OUTBOUND_RULE_NAME,
              "backend_address_pool": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "/backendAddressPools/" + BACKEND_ADDRESS_POOL_NAME
              },
              "frontend_ip_configurations": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "/frontendIPConfigurations/" + FRONTEND_IPCONFIGURATION_NAME
                }
              ],
              "protocol": "All"
            }
          ]
        }
        result = self.mgmt_client.load_balancers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, parameters=BODY)
        result = result.result()

        # # /LoadBalancers/put/Create load balancer with Standard SKU[put]
        # BODY = {
        #   "location": "eastus",
        #   "sku": {
        #     "name": "Standard"
        #   },
        #   "frontend_ipconfigurations": [
        #     {
        #       "name": "fe-lb",
        #       "properties": {
        #         "subnet": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworksvnetlbsubnetssubnetlb"
        #         }
        #       }
        #     }
        #   ],
        #   "backend_address_pools": [
        #     {
        #       "name": "be-lb"
        #     }
        #   ],
        #   "load_balancing_rules": [
        #     {
        #       "name": "rulelb",
        #       "properties": {
        #         "frontend_ipconfiguration": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationsfe-lb"
        #         },
        #         "frontend_port": "80",
        #         "backend_port": "80",
        #         "enable_floating_ip": True,
        #         "idle_timeout_in_minutes": "15",
        #         "protocol": "Tcp",
        #         "load_distribution": "Default",
        #         "backend_address_pool": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbbackendAddressPoolsbe-lb"
        #         },
        #         "probe": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbprobesprobe-lb"
        #         }
        #       }
        #     }
        #   ],
        #   "probes": [
        #     {
        #       "name": "probe-lb",
        #       "properties": {
        #         "protocol": "Http",
        #         "port": "80",
        #         "request_path": "healthcheck.aspx",
        #         "interval_in_seconds": "15",
        #         "number_of_probes": "2"
        #       }
        #     }
        #   ],
        #   "inbound_nat_rules": [
        #     {
        #       "name": "in-nat-rule",
        #       "properties": {
        #         "frontend_ipconfiguration": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationsfe-lb"
        #         },
        #         "frontend_port": "3389",
        #         "backend_port": "3389",
        #         "enable_floating_ip": True,
        #         "idle_timeout_in_minutes": "15",
        #         "protocol": "Tcp"
        #       }
        #     }
        #   ],
        #   "inbound_nat_pools": [],
        #   "outbound_rules": []
        # }
        # result = self.mgmt_client.load_balancers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, parameters=BODY)
        # result = result.result()

        # # /LoadBalancers/put/Create load balancer with Frontend IP in Zone 1[put]
        # BODY = {
        #   "location": "eastus",
        #   "sku": {
        #     "name": "Standard"
        #   },
        #   "frontend_ipconfigurations": [
        #     {
        #       "name": "fe-lb",
        #       "properties": {
        #         "subnet": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworksvnetlbsubnetssubnetlb"
        #         }
        #       },
        #       "zones": [
        #         "1"
        #       ]
        #     }
        #   ],
        #   "backend_address_pools": [
        #     {
        #       "name": "be-lb"
        #     }
        #   ],
        #   "load_balancing_rules": [
        #     {
        #       "name": "rulelb",
        #       "properties": {
        #         "frontend_ipconfiguration": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationsfe-lb"
        #         },
        #         "frontend_port": "80",
        #         "backend_port": "80",
        #         "enable_floating_ip": True,
        #         "idle_timeout_in_minutes": "15",
        #         "protocol": "Tcp",
        #         "load_distribution": "Default",
        #         "backend_address_pool": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbbackendAddressPoolsbe-lb"
        #         },
        #         "probe": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbprobesprobe-lb"
        #         }
        #       }
        #     }
        #   ],
        #   "probes": [
        #     {
        #       "name": "probe-lb",
        #       "properties": {
        #         "protocol": "Http",
        #         "port": "80",
        #         "request_path": "healthcheck.aspx",
        #         "interval_in_seconds": "15",
        #         "number_of_probes": "2"
        #       }
        #     }
        #   ],
        #   "inbound_nat_rules": [
        #     {
        #       "name": "in-nat-rule",
        #       "properties": {
        #         "frontend_ipconfiguration": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationsfe-lb"
        #         },
        #         "frontend_port": "3389",
        #         "backend_port": "3389",
        #         "enable_floating_ip": True,
        #         "idle_timeout_in_minutes": "15",
        #         "protocol": "Tcp"
        #       }
        #     }
        #   ],
        #   "inbound_nat_pools": [],
        #   "outbound_rules": []
        # }
        # result = self.mgmt_client.load_balancers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, parameters=BODY)
        # result = result.result()

        # # /LoadBalancers/put/Create load balancer with inbound nat pool[put]
        # BODY = {
        #   "location": "eastus",
        #   "sku": {
        #     "name": "Standard"
        #   },
        #   "frontend_ipconfigurations": [
        #     {
        #       "properties": {
        #         "private_ipallocation_method": "Dynamic",
        #         "subnet": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworkslbvnetsubnetslbsubnet"
        #         }
        #       },
        #       "name": "test",
        #       "zones": [],
        #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationstest"
        #     }
        #   ],
        #   "backend_address_pools": [],
        #   "load_balancing_rules": [],
        #   "probes": [],
        #   "inbound_nat_rules": [],
        #   "outbound_rules": [],
        #   "inbound_nat_pools": [
        #     {
        #       "properties": {
        #         "frontend_ipconfiguration": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationstest"
        #         },
        #         "protocol": "Tcp",
        #         "frontend_port_range_start": "8080",
        #         "frontend_port_range_end": "8085",
        #         "backend_port": "8888",
        #         "idle_timeout_in_minutes": "10",
        #         "enable_floating_ip": True,
        #         "enable_tcp_reset": True
        #       },
        #       "name": "test",
        #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbinboundNatPoolstest"
        #     }
        #   ]
        # }
        # result = self.mgmt_client.load_balancers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, parameters=BODY)
        # result = result.result()

        # # /LoadBalancers/put/Create load balancer with outbound rules[put]
        # BODY = {
        #   "location": "eastus",
        #   "sku": {
        #     "name": "Standard"
        #   },
        #   "frontend_ipconfigurations": [
        #     {
        #       "name": "fe-lb",
        #       "properties": {
        #         "public_ip_address": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddressespip"
        #         }
        #       }
        #     }
        #   ],
        #   "backend_address_pools": [
        #     {
        #       "name": "be-lb"
        #     }
        #   ],
        #   "load_balancing_rules": [
        #     {
        #       "name": "rulelb",
        #       "properties": {
        #         "frontend_ipconfiguration": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationsfe-lb"
        #         },
        #         "backend_address_pool": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbbackendAddressPoolsbe-lb"
        #         },
        #         "probe": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbprobesprobe-lb"
        #         },
        #         "protocol": "Tcp",
        #         "load_distribution": "Default",
        #         "frontend_port": "80",
        #         "backend_port": "80",
        #         "idle_timeout_in_minutes": "15",
        #         "enable_floating_ip": True,
        #         "disable_outbound_snat": True
        #       }
        #     }
        #   ],
        #   "probes": [
        #     {
        #       "name": "probe-lb",
        #       "properties": {
        #         "protocol": "Http",
        #         "port": "80",
        #         "request_path": "healthcheck.aspx",
        #         "interval_in_seconds": "15",
        #         "number_of_probes": "2"
        #       }
        #     }
        #   ],
        #   "inbound_nat_rules": [
        #     {
        #       "name": "in-nat-rule",
        #       "properties": {
        #         "frontend_ipconfiguration": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationsfe-lb"
        #         },
        #         "frontend_port": "3389",
        #         "backend_port": "3389",
        #         "enable_floating_ip": True,
        #         "idle_timeout_in_minutes": "15",
        #         "protocol": "Tcp"
        #       }
        #     }
        #   ],
        #   "inbound_nat_pools": [],
        #   "outbound_rules": [
        #     {
        #       "name": "rule1",
        #       "properties": {
        #         "backend_address_pool": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbbackendAddressPoolsbe-lb"
        #         },
        #         "frontend_ipconfigurations": [
        #           {
        #             "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationsfe-lb"
        #           }
        #         ],
        #         "protocol": "All"
        #       }
        #     }
        #   ]
        # }
        # result = self.mgmt_client.load_balancers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, parameters=BODY)
        # result = result.result()

        # # /LoadBalancers/put/Create load balancer[put]
        # BODY = {
        #   "location": "eastus",
        #   "frontend_ipconfigurations": [
        #     {
        #       "name": "fe-lb",
        #       "properties": {
        #         "subnet": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworksvnetlbsubnetssubnetlb"
        #         }
        #       }
        #     }
        #   ],
        #   "backend_address_pools": [
        #     {
        #       "name": "be-lb"
        #     }
        #   ],
        #   "load_balancing_rules": [
        #     {
        #       "name": "rulelb",
        #       "properties": {
        #         "frontend_ipconfiguration": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationsfe-lb"
        #         },
        #         "frontend_port": "80",
        #         "backend_port": "80",
        #         "enable_floating_ip": True,
        #         "idle_timeout_in_minutes": "15",
        #         "protocol": "Tcp",
        #         "enable_tcp_reset": False,
        #         "load_distribution": "Default",
        #         "backend_address_pool": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbbackendAddressPoolsbe-lb"
        #         },
        #         "probe": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbprobesprobe-lb"
        #         }
        #       }
        #     }
        #   ],
        #   "probes": [
        #     {
        #       "name": "probe-lb",
        #       "properties": {
        #         "protocol": "Http",
        #         "port": "80",
        #         "request_path": "healthcheck.aspx",
        #         "interval_in_seconds": "15",
        #         "number_of_probes": "2"
        #       }
        #     }
        #   ],
        #   "inbound_nat_rules": [
        #     {
        #       "name": "in-nat-rule",
        #       "properties": {
        #         "frontend_ipconfiguration": {
        #           "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancerslbfrontendIPConfigurationsfe-lb"
        #         },
        #         "frontend_port": "3389",
        #         "backend_port": "3389",
        #         "enable_floating_ip": True,
        #         "idle_timeout_in_minutes": "15",
        #         "protocol": "Tcp",
        #         "enable_tcp_reset": False
        #       }
        #     }
        #   ],
        #   "inbound_nat_pools": []
        # }
        # result = self.mgmt_client.load_balancers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, parameters=BODY)
        # result = result.result()

        # /InboundNatRules/put/InboundNatRuleCreate[put]
        BODY = {
          "protocol": "Tcp",
          "frontend_ip_configuration": {
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "/frontendIPConfigurations/" + FRONTEND_IPCONFIGURATION_NAME
          },
          "frontend_port": "3390",
          "backend_port": "3389",
          "idle_timeout_in_minutes": "4",
          "enable_tcp_reset": False,
          "enable_floating_ip": False
        }
        result = self.mgmt_client.inbound_nat_rules.begin_create_or_update(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, inbound_nat_rule_name=INBOUND_NAT_RULE_NAME, inbound_nat_rule_parameters=BODY)
        result = result.result()

        # /LoadBalancerFrontendIPConfigurations/get/LoadBalancerFrontendIPConfigurationGet[get]
        result = self.mgmt_client.load_balancer_frontend_ip_configurations.get(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, frontend_ip_configuration_name=FRONTEND_IPCONFIGURATION_NAME)

        # /LoadBalancerBackendAddressPools/get/LoadBalancerBackendAddressPoolGet[get]
        result = self.mgmt_client.load_balancer_backend_address_pools.get(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, backend_address_pool_name=BACKEND_ADDRESS_POOL_NAME)

        # /LoadBalancerLoadBalancingRules/get/LoadBalancerLoadBalancingRuleGet[get]
        result = self.mgmt_client.load_balancer_load_balancing_rules.get(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, load_balancing_rule_name=LOAD_BALANCING_RULE_NAME)

        # /InboundNatRules/get/InboundNatRuleGet[get]
        result = self.mgmt_client.inbound_nat_rules.get(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, inbound_nat_rule_name=INBOUND_NAT_RULE_NAME)

        # /LoadBalancerOutboundRules/get/LoadBalancerOutboundRuleGet[get]
        result = self.mgmt_client.load_balancer_outbound_rules.get(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, outbound_rule_name=OUTBOUND_RULE_NAME)

        # /LoadBalancerFrontendIPConfigurations/get/LoadBalancerFrontendIPConfigurationList[get]
        result = self.mgmt_client.load_balancer_frontend_ip_configurations.list(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)

        # /LoadBalancerProbes/get/LoadBalancerProbeGet[get]
        result = self.mgmt_client.load_balancer_probes.get(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, probe_name=PROBE_NAME)

        # /LoadBalancerBackendAddressPools/get/LoadBalancerBackendAddressPoolList[get]
        result = self.mgmt_client.load_balancer_backend_address_pools.list(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)

        # /LoadBalancerLoadBalancingRules/get/LoadBalancerLoadBalancingRuleList[get]
        result = self.mgmt_client.load_balancer_load_balancing_rules.list(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)

        # /LoadBalancerNetworkInterfaces/get/LoadBalancerNetworkInterfaceListVmss[get]
        result = self.mgmt_client.load_balancer_network_interfaces.list(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)

        # /LoadBalancerNetworkInterfaces/get/LoadBalancerNetworkInterfaceListSimple[get]
        result = self.mgmt_client.load_balancer_network_interfaces.list(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)

        # /InboundNatRules/get/InboundNatRuleList[get]
        result = self.mgmt_client.inbound_nat_rules.list(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)

        # /LoadBalancerOutboundRules/get/LoadBalancerOutboundRuleList[get]
        result = self.mgmt_client.load_balancer_outbound_rules.list(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)

        # /LoadBalancerProbes/get/LoadBalancerProbeList[get]
        result = self.mgmt_client.load_balancer_probes.list(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)

        # /LoadBalancers/get/Get load balancer[get]
        result = self.mgmt_client.load_balancers.get(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)

        # /LoadBalancers/get/List load balancers in resource group[get]
        result = self.mgmt_client.load_balancers.list(resource_group_name=RESOURCE_GROUP)

        # /LoadBalancers/get/List all load balancers[get]
        result = self.mgmt_client.load_balancers.list_all()

        # /LoadBalancers/patch/Update load balancer tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.load_balancers.update_tags(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, parameters=BODY)

        # /InboundNatRules/delete/InboundNatRuleDelete[delete]
        result = self.mgmt_client.inbound_nat_rules.begin_delete(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME, inbound_nat_rule_name=INBOUND_NAT_RULE_NAME)
        result = result.result()

        # /LoadBalancers/delete/Delete load balancer[delete]
        result = self.mgmt_client.load_balancers.begin_delete(resource_group_name=RESOURCE_GROUP, load_balancer_name=LOAD_BALANCER_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
