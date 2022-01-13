# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 48
# Methods Covered : 48
# Examples Total  : 50
# Examples Tested : 50
# Coverage %      : 100
# ----------------------

#  express_route_circuits:  8/11
#  express_route_ports:  0/6  # TODO: (InvalidResourceType) The resource type could not be found in the namespace 'Microsoft.Network' for api version '2020-03-01'.
#  express_route_ports_locations: 0/2  # TODO: need express route ports
#  express_route_cross_connections:  0/8  # TODO: (InvalidResourceType) The resource type could not be found in the namespace 'Microsoft.Network' for api version '2020-03-01'.
#  express_route_cross_connection_peerings: 0/4  # TODO: (InvalidResourceType) The resource type could not be found in the namespace 'Microsoft.Network' for api version '2020-03-01'.
#  express_route_links: 0/2  # TODO: need express route ports
#  express_route_circuit_peerings: 4/4
#  express_route_circuit_authorizations: 4/4
#  express_route_circuit_connections: 4/4
#  express_route_connection: # TODO: don't have example
#  express_route_gateway: # TODO: don't have example
#  express_route_service_providers: 1/1
#  peer_express_route_circuit_connections: 2/2

import unittest
import pytest

from azure.core.exceptions import HttpResponseError
import azure.mgmt.network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'


@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

    @unittest.skip('skip test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        CIRCUIT_NAME = "myCircuit"
        CIRCUIT_NAME_2 = "myCircuit2"
        EXPRESS_ROUTE_PORT_NAME = "myExpressRoutePort"
        CROSS_CONNECTION_NAME = "myCrossConnection"
        PEERING_NAME = "AzurePrivatePeering"
        AUTHORIZATION_NAME = "myAuthorization"
        CONNECTION_NAME = "myConnection"
        LINK_NAME = "myLink"
        LOCATION_NAME = "myLocation"
        DEVICE_PATH = "myDevicePath"

        # # /ExpressRouteCircuits/put/Create ExpressRouteCircuit on ExpressRoutePort[put]
        # BODY = {
        #   "location": "westus",
        #   "sku": {
        #     "name": "Premium_MeteredData",
        #     "tier": "Premium",
        #     "family": "MeteredData"
        #   },
        #   "express_route_port": {
        #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/expressRoutePortsportName"
        #   },
        #   "bandwidth_in_gbps": "10"
        # }
        # result = self.mgmt_client.express_route_circuits.begin_create_or_update(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, parameters=BODY)
        # result = result.result()

        # /ExpressRouteCircuits/put/Create ExpressRouteCircuit[put]
        BODY = {
          "sku": {
            "name": "Standard_MeteredData",
            "tier": "Standard",
            "family": "MeteredData"
          },
          "location": AZURE_LOCATION,
          # "authorizations": [],
          # "peerings": [],
          # "allow_classic_operations": False,
          "service_provider_properties": {
            "service_provider_name": "Equinix",
            "peering_location": "Silicon Valley",
            "bandwidth_in_mbps": "200"
          }
        }
        result = self.mgmt_client.express_route_circuits.begin_create_or_update(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, parameters=BODY)
        result = result.result()

        SERVICE_KEY = result.service_key

        BODY = {
          "sku": {
            "name": "Standard_MeteredData",
            "tier": "Standard",
            "family": "MeteredData"
          },
          "location": AZURE_LOCATION,
          # "authorizations": [],
          # "peerings": [],
          # "allow_classic_operations": False,
          "service_provider_properties": {
            "service_provider_name": "Equinix",
            "peering_location": "Silicon Valley",
            "bandwidth_in_mbps": "200"
          }
        }
        result = self.mgmt_client.express_route_circuits.begin_create_or_update(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME_2, parameters=BODY)
        result = result.result()

        # # /ExpressRoutePorts/put/ExpressRoutePortCreate[put]
        # BODY = {
        #   "location": AZURE_LOCATION,
        #   "peering_location": "peeringLocationName",
        #   "bandwidth_in_gbps": "100",
        #   "encapsulation": "QinQ"
        # }
        # result = self.mgmt_client.express_route_ports.begin_create_or_update(resource_group_name=RESOURCE_GROUP, express_route_port_name=EXPRESS_ROUTE_PORT_NAME, parameters=BODY)
        # result = result.result()

        # # /ExpressRoutePorts/put/ExpressRoutePortUpdateLink[put]
        # BODY = {
        #   "location": "westus",
        #   "peering_location": "peeringLocationName",
        #   "bandwidth_in_gbps": "100",
        #   "encapsulation": "QinQ",
        #   "links": [
        #     {
        #       "name": "link1",
        #       "properties": {
        #         "admin_state": "Enabled"
        #       }
        #     }
        #   ]
        # }
        # result = self.mgmt_client.express_route_ports.begin_create_or_update(resource_group_name=RESOURCE_GROUP, express_route_port_name=EXPRESS_ROUTE_PORT_NAME, parameters=BODY)
        # result = result.result()

        # /ExpressRouteCrossConnections/put/UpdateExpressRouteCrossConnection[put]
        # BODY = {
        #   "service_provider_provisioning_state": "NotProvisioned"
        # }
        # result = self.mgmt_client.express_route_cross_connections.begin_create_or_update(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME, parameters=BODY)
        # result = result.result()

        # /ExpressRouteCircuitPeerings/put/Create ExpressRouteCircuit Peerings[put]
        BODY = {
          "peer_asn": "10001",
          "primary_peer_address_prefix": "102.0.0.0/30",
          "secondary_peer_address_prefix": "103.0.0.0/30",
          "vlan_id": "101"
        }
        result = self.mgmt_client.express_route_circuit_peerings.begin_create_or_update(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME, peering_parameters=BODY)
        result = result.result()

        # /ExpressRouteCircuitPeerings/put/Create ExpressRouteCircuit Peerings[put]
        BODY = {
          "peer_asn": "10002",
          "primary_peer_address_prefix": "104.0.0.0/30",
          "secondary_peer_address_prefix": "105.0.0.0/30",
          "vlan_id": "102"
        }
        result = self.mgmt_client.express_route_circuit_peerings.begin_create_or_update(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME_2, peering_name=PEERING_NAME, peering_parameters=BODY)
        result = result.result()

        # /ExpressRouteCircuitAuthorizations/put/Create ExpressRouteCircuit Authorization[put]
        BODY = {}
        result = self.mgmt_client.express_route_circuit_authorizations.begin_create_or_update(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, authorization_name=AUTHORIZATION_NAME, authorization_parameters=BODY)
        result = result.result()

        # /ExpressRouteCrossConnectionPeerings/put/ExpressRouteCrossConnectionBgpPeeringCreate[put]
        # BODY = {
        #   "peer_asn": "200",
        #   "primary_peer_address_prefix": "192.168.16.252/30",
        #   "secondary_peer_address_prefix": "192.168.18.252/30",
        #   "vlan_id": "200",
        #   "ipv6peering_config": {
        #     "primary_peer_address_prefix": "3FFE:FFFF:0:CD30::/126",
        #     "secondary_peer_address_prefix": "3FFE:FFFF:0:CD30::4/126"
        #   }
        # }
        # result = self.mgmt_client.express_route_cross_connection_peerings.begin_create_or_update(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME, peering_name=PEERING_NAME, peering_parameters=BODY)
        # result = result.result()

        # These commands won't succeed because circuit creation requires a manual step from the service.
        with pytest.raises(HttpResponseError):
          # /ExpressRouteCircuitConnections/put/ExpressRouteCircuitConnectionCreate[put]
          BODY = {
            "express_route_circuit_peering": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/expressRouteCircuits/" + CIRCUIT_NAME + "/peerings/" + PEERING_NAME
            },
            "peer_express_route_circuit_peering": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/expressRouteCircuits/" + CIRCUIT_NAME_2 + "/peerings/" + PEERING_NAME 
            },
            # "authorization_key": "946a1918-b7a2-4917-b43c-8c4cdaee006a",
            # "authorization_key": SERVICE_KEY,
            "address_prefix": "104.0.0.0/29",
            # "ipv6circuit_connection_config": {
            #   "address_prefix": "aa:bb::/125"
            # }
          }
          result = self.mgmt_client.express_route_circuit_connections.begin_create_or_update(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME, connection_name=CONNECTION_NAME, express_route_circuit_connection_parameters=BODY)
          result = result.result()

        # TODO: # cannot create it, so this test will fail due to resource is not found.
        # /PeerExpressRouteCircuitConnections/get/PeerExpressRouteCircuitConnectionGet[get]
        with pytest.raises(HttpResponseError):
            result = self.mgmt_client.peer_express_route_circuit_connections.get(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME_2, peering_name=PEERING_NAME, connection_name=CONNECTION_NAME)

        # /ExpressRouteCircuitConnections/get/ExpressRouteCircuitConnectionGet[get]
        result = self.mgmt_client.express_route_circuit_connections.get(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME, connection_name=CONNECTION_NAME)

        # /ExpressRouteCrossConnectionPeerings/get/GetExpressRouteCrossConnectionBgpPeering[get]
        # result = self.mgmt_client.express_route_cross_connection_peerings.get(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME, peering_name=PEERING_NAME)

        # /PeerExpressRouteCircuitConnections/get/List Peer ExpressRouteCircuit Connection[get]
        result = self.mgmt_client.peer_express_route_circuit_connections.list(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME_2, peering_name=PEERING_NAME)

        # /ExpressRouteCircuitConnections/get/List ExpressRouteCircuit Connection[get]
        result = self.mgmt_client.express_route_circuit_connections.list(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME)

        # /ExpressRouteCircuitAuthorizations/get/Get ExpressRouteCircuit Authorization[get]
        result = self.mgmt_client.express_route_circuit_authorizations.get(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, authorization_name=AUTHORIZATION_NAME)

        # /ExpressRouteCircuits/get/Get ExpressRoute Circuit Peering Traffic Stats[get]
        result = self.mgmt_client.express_route_circuits.get_peering_stats(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME)

        # /ExpressRouteLinks/get/ExpressRouteLinkGet[get]
        # result = self.mgmt_client.express_route_links.get(resource_group_name=RESOURCE_GROUP, express_route_port_name=EXPRESS_ROUTE_PORT_NAME, link_name=LINK_NAME)

        # /ExpressRouteCircuitPeerings/get/Get ExpressRouteCircuit Peering[get]
        result = self.mgmt_client.express_route_circuit_peerings.get(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME)

        # /ExpressRouteCrossConnectionPeerings/get/ExpressRouteCrossConnectionBgpPeeringList[get]
        # result = self.mgmt_client.express_route_cross_connection_peerings.list(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME)

        # /ExpressRouteCrossConnections/get/GetExpressRouteCrossConnection[get]
        # result = self.mgmt_client.express_route_cross_connections.get(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME)

        # /ExpressRouteCircuitAuthorizations/get/List ExpressRouteCircuit Authorization[get]
        result = self.mgmt_client.express_route_circuit_authorizations.list(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME)

        # /ExpressRouteLinks/get/ExpressRouteLinkGet[get]
        # result = self.mgmt_client.express_route_links.get(resource_group_name=RESOURCE_GROUP, express_route_port_name=EXPRESS_ROUTE_PORT_NAME, link_name=LINK_NAME)

        # /ExpressRouteCircuitPeerings/get/List ExpressRouteCircuit Peerings[get]
        result = self.mgmt_client.express_route_circuit_peerings.list(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME)

        # /ExpressRoutePorts/get/ExpressRoutePortGet[get]
        # result = self.mgmt_client.express_route_ports.get(resource_group_name=RESOURCE_GROUP, express_route_port_name=EXPRESS_ROUTE_PORT_NAME)

        # /ExpressRouteCircuits/get/Get ExpressRoute Circuit Traffic Stats[get]
        result = self.mgmt_client.express_route_circuits.get_stats(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME)

        # /ExpressRouteCircuits/get/Get ExpressRouteCircuit[get]
        result = self.mgmt_client.express_route_circuits.get(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME)

        # /ExpressRouteCrossConnections/get/ExpressRouteCrossConnectionListByResourceGroup[get]
        # result = self.mgmt_client.express_route_cross_connections.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /ExpressRouteCircuits/get/List ExpressRouteCircuits in a resource group[get]
        result = self.mgmt_client.express_route_circuits.list(resource_group_name=RESOURCE_GROUP)

        # /ExpressRoutePorts/get/ExpressRoutePortListByResourceGroup[get]
        # result = self.mgmt_client.express_route_ports.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /ExpressRoutePortsLocations/get/ExpressRoutePortsLocationGet[get]
        # result = self.mgmt_client.express_route_ports_locations.get(location_name=LOCATION_NAME)

        # /ExpressRouteCrossConnections/get/ExpressRouteCrossConnectionList[get]
        # result = self.mgmt_client.express_route_cross_connections.list()

        # /ExpressRouteServiceProviders/get/List ExpressRoute providers[get]
        result = self.mgmt_client.express_route_service_providers.list()

        # /ExpressRoutePortsLocations/get/ExpressRoutePortsLocationList[get]
        # result = self.mgmt_client.express_route_ports_locations.list()

        # /ExpressRouteCircuits/get/List ExpressRouteCircuits in a subscription[get]
        result = self.mgmt_client.express_route_circuits.list_all()

        # /ExpressRoutePorts/get/ExpressRoutePortList[get]
        # result = self.mgmt_client.express_route_ports.list()

        # /ExpressRouteCrossConnections/post/GetExpressRouteCrossConnectionsRouteTableSummary[post]
        # result = self.mgmt_client.express_route_cross_connections.begin_list_routes_table_summary(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME, peering_name=PEERING_NAME, device_path=DEVICE_PATH)
        # result = result.result()

        # /ExpressRouteCrossConnections/post/GetExpressRouteCrossConnectionsRouteTable[post]
        # result = self.mgmt_client.express_route_cross_connections.begin_list_routes_table(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME, peering_name=PEERING_NAME, device_path=DEVICE_PATH)
        # result = result.result()

        # /ExpressRouteCrossConnections/post/GetExpressRouteCrossConnectionsArpTable[post]
        # result = self.mgmt_client.express_route_cross_connections.begin_list_arp_table(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME, peering_name=PEERING_NAME, device_path=DEVICE_PATH)
        # result = result.result()

        # /ExpressRouteCircuits/post/List Route Table Summary[post]
        # result = self.mgmt_client.express_route_circuits.begin_list_routes_table_summary(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME, device_path=DEVICE_PATH)
        # result = result.result()

        # /ExpressRouteCircuits/post/List Route Tables[post]
        # result = self.mgmt_client.express_route_circuits.begin_list_routes_table(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME, device_path=DEVICE_PATH)
        # result = result.result()

        # /ExpressRouteCircuits/post/List ARP Table[post]
        # result = self.mgmt_client.express_route_circuits.begin_list_arp_table(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME, device_path=DEVICE_PATH)
        # result = result.result()

        # /ExpressRouteCrossConnections/patch/UpdateExpressRouteCrossConnectionTags[patch]
        # BODY = {
        #   "tags": {
        #     "tag1": "value1",
        #     "tag2": "value2"
        #   }
        # }
        # result = self.mgmt_client.express_route_cross_connections.update_tags(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME, cross_connection_parameters=BODY)

        # /ExpressRoutePorts/patch/ExpressRoutePortUpdateTags[patch]
        # BODY = {
        #   "tags": {
        #     "tag1": "value1",
        #     "tag2": "value2"
        #   }
        # }
        # result = self.mgmt_client.express_route_ports.update_tags(resource_group_name=RESOURCE_GROUP, express_route_port_name=EXPRESS_ROUTE_PORT_NAME, parameters=BODY)

        # /ExpressRouteCircuits/patch/Update Express Route Circuit Tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        # result = self.mgmt_client.express_route_circuits.update_tags(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, parameters=BODY)

        # /ExpressRouteCircuitConnections/delete/Delete ExpressRouteCircuit[delete]
        result = self.mgmt_client.express_route_circuit_connections.begin_delete(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME, connection_name=CONNECTION_NAME)
        result = result.result()

        # /ExpressRouteCrossConnectionPeerings/delete/DeleteExpressRouteCrossConnectionBgpPeering[delete]
        # result = self.mgmt_client.express_route_cross_connection_peerings.begin_delete(resource_group_name=RESOURCE_GROUP, cross_connection_name=CROSS_CONNECTION_NAME, peering_name=PEERING_NAME)
        # result = result.result()

        # /ExpressRouteCircuitAuthorizations/delete/Delete ExpressRouteCircuit Authorization[delete]
        result = self.mgmt_client.express_route_circuit_authorizations.begin_delete(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, authorization_name=AUTHORIZATION_NAME)
        result = result.result()

        # /ExpressRouteCircuitPeerings/delete/Delete ExpressRouteCircuit Peerings[delete]
        result = self.mgmt_client.express_route_circuit_peerings.begin_delete(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME, peering_name=PEERING_NAME)
        result = result.result()

        # /ExpressRoutePorts/delete/ExpressRoutePortDelete[delete]
        # result = self.mgmt_client.express_route_ports.begin_delete(resource_group_name=RESOURCE_GROUP, express_route_port_name=EXPRESS_ROUTE_PORT_NAME)
        # result = result.result()

        # /ExpressRouteCircuits/delete/Delete ExpressRouteCircuit[delete]
        result = self.mgmt_client.express_route_circuits.begin_delete(resource_group_name=RESOURCE_GROUP, circuit_name=CIRCUIT_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
