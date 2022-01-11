# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 25
# Methods Covered : 25
# Examples Total  : 27
# Examples Tested : 27
# Coverage %      : 100
# ----------------------

#  private_link_services: 13/13
#  private_endpoints: 5/5
#  private_dns_zone_groups: 4/4
#  available_private_endpoint_types: 2/2
#  available_endpoint_services: 1/1

import unittest
import pytest

import azure.mgmt.network as az_network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'


@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            az_network.NetworkManagementClient
        )

        if self.is_live:
            import azure.mgmt.privatedns as az_privatedns
            self.dns_client = self.create_mgmt_client(
                az_privatedns.PrivateDnsManagementClient
            )

    def create_load_balancer(self, group_name, location, load_balancer_name, ip_config_name, subnet_id):
        # Create load balancer
        BODY = {
          "location": location,
          "sku": {
            "name": "Standard"
          },
          "frontendIPConfigurations": [
            {
              "name": ip_config_name,
              "subnet": {
                # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VNET_NAME + "/subnets/" + SUB_NET
                "id": subnet_id
              }
            }
          ]
        }

        result = self.mgmt_client.load_balancers.begin_create_or_update(group_name, load_balancer_name, BODY)
        result.result()

    def create_virtual_network(self, group_name, location, network_name, subnet_name1, subnet_name2):
      
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
            subnet_name1,
            {
              'address_prefix': '10.0.0.0/24',
              'private_link_service_network_policies': 'disabled'
            }
        )
        subnet_info_1 = async_subnet_creation.result()

        async_subnet_creation = self.mgmt_client.subnets.begin_create_or_update(
            group_name,
            network_name,
            subnet_name2,
            {
              'address_prefix': '10.0.1.0/24',
              'private_endpoint_network_policies': 'disabled'
            }
        )
        subnet_info_2 = async_subnet_creation.result()
          
        return (subnet_info_1, subnet_info_2)

    def create_private_dns_zone(self, group_name, zone_name):
        if self.is_live:
            # Zones are a 'global' resource.
            zone = self.dns_client.private_zones.begin_create_or_update(
                group_name,
                zone_name,
                {
                    'location': 'global'
                }
            )
            return zone.result().id
        else:
            return "/subscriptions/" + "00000000-0000-0000-0000-000000000000" + "/resourceGroups/" + group_name + "/providers/Microsoft.Network/privateDnsZones/" + zone_name


    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        SERVICE_NAME = "myService"
        PRIVATE_ENDPOINT_NAME = "myPrivateEndpoint"
        PE_CONNECTION_NAME = "myPeConnection"
        PRIVATE_DNS_ZONE_GROUP_NAME = "myPrivateDnsZoneGroup"
        LOCATION = AZURE_LOCATION
        IP_CONFIGURATION_NAME = "myIPConfiguration"
        LOAD_BALANCER_NAME = "loadbalancer"
        VIRTUAL_NETWORK_NAME = "virtualnetwork"
        SUBNET_NAME_1 = "subnet1"
        SUBNET_NAME_2 = "subnet2"
        ZONE_NAME = "www.zone1.com"
        PRIVATE_ZONE_NAME = "zone1"

        subnet, _ = self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME_1, SUBNET_NAME_2)
        self.create_load_balancer(RESOURCE_GROUP, AZURE_LOCATION, LOAD_BALANCER_NAME, IP_CONFIGURATION_NAME, subnet.id)

        # /PrivateLinkServices/put/Create private link service[put]
        BODY = {
          "location": "eastus",
          "visibility": {
            "subscriptions": [
              SUBSCRIPTION_ID
            ]
          },
          "auto_approval": {
            "subscriptions": [
              SUBSCRIPTION_ID
            ]
          },
          "fqdns": [
            "fqdn1",
            "fqdn2",
            "fqdn3"
          ],
          "load_balancer_frontend_ip_configurations": [
            {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "/frontendIPConfigurations/" + IP_CONFIGURATION_NAME
            }
          ],
          "ip_configurations": [
            {
              "name": IP_CONFIGURATION_NAME,
              "private_ip_address": "10.0.1.4",
              "private_ipallocation_method": "Static",
              "private_ip_address_version": "IPv4",
              "subnet": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME_1
              }
            }
          ]
        }
        result = self.mgmt_client.private_link_services.begin_create_or_update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, parameters=BODY)
        result = result.result()

        # /PrivateEndpoints/put/Create private endpoint[put]
        BODY = {
          "location": AZURE_LOCATION,
          "private_link_service_connections": [
            {
              "name": SERVICE_NAME,  # TODO: This is needed, but was not showed in swagger.
              "private_link_service_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/privateLinkServices/" + SERVICE_NAME,
              # "group_ids": [
              #   "groupIdFromResource"
              # ],
              # "request_message": "Please approve my connection."
            }
          ],
          "subnet": {
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME_2
          }
        }
        result = self.mgmt_client.private_endpoints.begin_create_or_update(resource_group_name=RESOURCE_GROUP, private_endpoint_name=PRIVATE_ENDPOINT_NAME, parameters=BODY)
        result = result.result()

        # # /PrivateEndpoints/put/Create private endpoint with manual approval connection[put]
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "manual_private_link_service_connections": [
        #       {
        #         "properties": {
        #           "private_link_service_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/privateLinkServicestestPls",
        #           "group_ids": [
        #             "groupIdFromResource"
        #           ],
        #           "request_message": "Please manually approve my connection."
        #         }
        #       }
        #     ],
        #     "subnet": {
        #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworksmyVnetsubnetsmySubnet"
        #     }
        #   }
        # }
        # result = self.mgmt_client.private_endpoints.begin_create_or_update(resource_group_name=RESOURCE_GROUP, private_endpoint_name=PRIVATE_ENDPOINT_NAME, parameters=BODY)
        # result = result.result()

        # /PrivateLinkServices/get/Get private link service[get]
        pls = self.mgmt_client.private_link_services.get(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)
        PE_CONNECTION_NAME = pls.private_endpoint_connections[0].name

        # /PrivateLinkServices/put/approve or reject private end point connection for a private link service[put]
        BODY = {
          "name": PE_CONNECTION_NAME,
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "approved it for some reason."
          }
        }
        result = self.mgmt_client.private_link_services.update_private_endpoint_connection(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, pe_connection_name=PE_CONNECTION_NAME, parameters=BODY)

        self.create_private_dns_zone(RESOURCE_GROUP, ZONE_NAME)

        # /PrivateDnsZoneGroups/put/Create private dns zone group[put]  TODO: example needs imporve
        BODY = {
          "name": PRIVATE_DNS_ZONE_GROUP_NAME,
          "private_dns_zone_configs": [
            {
              "name": PRIVATE_ZONE_NAME,
              "private_dns_zone_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/privateDnsZones/" + ZONE_NAME
            }
          ]
        }
        result = self.mgmt_client.private_dns_zone_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, private_endpoint_name=PRIVATE_ENDPOINT_NAME, private_dns_zone_group_name=PRIVATE_DNS_ZONE_GROUP_NAME, parameters=BODY)
        result = result.result()

        # /PrivateDnsZoneGroups/get/Get private dns zone group[get]
        result = self.mgmt_client.private_dns_zone_groups.get(resource_group_name=RESOURCE_GROUP, private_endpoint_name=PRIVATE_ENDPOINT_NAME, private_dns_zone_group_name=PRIVATE_DNS_ZONE_GROUP_NAME)

        # /PrivateLinkServices/get/Get private end point connection[get]
        result = self.mgmt_client.private_link_services.get_private_endpoint_connection(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, pe_connection_name=PE_CONNECTION_NAME)

        # /PrivateLinkServices/get/List private link service in resource group[get]
        result = self.mgmt_client.private_link_services.list_private_endpoint_connections(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # /PrivateDnsZoneGroups/get/List private endpoints in resource group[get]
        result = self.mgmt_client.private_dns_zone_groups.list(resource_group_name=RESOURCE_GROUP, private_endpoint_name=PRIVATE_ENDPOINT_NAME)

        # /PrivateLinkServices/get/Get list of private link service id that can be linked to a private end point with auto approved[get]
        result = self.mgmt_client.private_link_services.list_auto_approved_private_link_services_by_resource_group(resource_group_name=RESOURCE_GROUP, location=LOCATION)

        # /AvailablePrivateEndpointTypes/get/Get available PrivateEndpoint types in the resource group[get]
        result = self.mgmt_client.available_private_endpoint_types.list_by_resource_group(resource_group_name=RESOURCE_GROUP, location=LOCATION)

        # # /PrivateEndpoints/get/Get private endpoint with manual approval connection[get]
        # result = self.mgmt_client.private_endpoints.get(resource_group_name=RESOURCE_GROUP, private_endpoint_name=PRIVATE_ENDPOINT_NAME)

        # /PrivateEndpoints/get/Get private endpoint[get]
        result = self.mgmt_client.private_endpoints.get(resource_group_name=RESOURCE_GROUP, private_endpoint_name=PRIVATE_ENDPOINT_NAME)

        # /PrivateLinkServices/get/Get private link service[get]
        result = self.mgmt_client.private_link_services.get(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # /AvailableEndpointServices/get/EndpointServicesList[get]
        result = self.mgmt_client.available_endpoint_services.list(location=LOCATION)

        # # /PrivateLinkServices/get/Get list of private link service id that can be linked to a private end point with auto approved[get]
        # result = self.mgmt_client.private_link_services.list_auto_approved_private_link_services_by_resource_group(resource_group_name=RESOURCE_GROUP, location=LOCATION)

        # /PrivateLinkServices/get/List private link service in resource group[get]
        result = self.mgmt_client.private_link_services.list_private_endpoint_connections(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # /AvailablePrivateEndpointTypes/get/Get available PrivateEndpoint types[get]
        result = self.mgmt_client.available_private_endpoint_types.list(location=LOCATION)

        # /PrivateEndpoints/get/List private endpoints in resource group[get]
        result = self.mgmt_client.private_endpoints.list(resource_group_name=RESOURCE_GROUP)

        # /PrivateLinkServices/get/List all private list service[get]
        result = self.mgmt_client.private_link_services.list_by_subscription()

        # /PrivateEndpoints/get/List all private endpoints[get]
        result = self.mgmt_client.private_endpoints.list_by_subscription()

        # /PrivateLinkServices/post/Check private link service visibility[post]
        BODY = {
          "private_link_service_alias": "mypls.00000000-0000-0000-0000-000000000000.azure.privatelinkservice"
        }
        # [ZIM] SDK fails for some reason here
        # result = self.mgmt_client.private_link_services.check_private_link_service_visibility_by_resource_group(resource_group_name=RESOURCE_GROUP, location=LOCATION, parameters=BODY)

        # # /PrivateLinkServices/post/Check private link service visibility[post]
        # BODY = {
        #   "private_link_service_alias": "mypls.00000000-0000-0000-0000-000000000000.azure.privatelinkservice"
        # }
        # result = self.mgmt_client.private_link_services.check_private_link_service_visibility_by_resource_group(resource_group_name=RESOURCE_GROUP, location=LOCATION, parameters=BODY)

        # /PrivateDnsZoneGroups/delete/Delete private dns zone group[delete]
        result = self.mgmt_client.private_dns_zone_groups.begin_delete(resource_group_name=RESOURCE_GROUP, private_endpoint_name=PRIVATE_ENDPOINT_NAME, private_dns_zone_group_name=PRIVATE_DNS_ZONE_GROUP_NAME)
        result = result.result()

        # /PrivateLinkServices/delete/delete private end point connection for a private link service[delete]
        result = self.mgmt_client.private_link_services.begin_delete_private_endpoint_connection(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, pe_connection_name=PE_CONNECTION_NAME)
        result = result.result()

        # /PrivateEndpoints/delete/Delete private endpoint[delete]
        result = self.mgmt_client.private_endpoints.begin_delete(resource_group_name=RESOURCE_GROUP, private_endpoint_name=PRIVATE_ENDPOINT_NAME)
        result = result.result()

        # /PrivateLinkServices/delete/Delete private link service[delete]
        result = self.mgmt_client.private_link_services.begin_delete(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
