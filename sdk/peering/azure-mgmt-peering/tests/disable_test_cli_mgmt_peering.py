# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 35
# Methods Covered : 35
# Examples Total  : 38
# Examples Tested : 18
# Coverage %      : 47
# ----------------------

import unittest

import azure.mgmt.peering
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

@unittest.skip("skip test")
class MgmtPeeringTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtPeeringTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.peering.PeeringManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_peering(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        PEER_ASN_NAME = "myPeerAsn"
        PEERING_NAME = "myPeering"
        REGISTERED_ASN_NAME = "myRegisteredAsn"
        REGISTERED_PREFIX_NAME = "myRegisteredPrefix"
        PEERING_SERVICE_NAME = "myPeeringService"
        PREFIX_NAME = "myPrefix"

        # /PeerAsns/put/Create a peer ASN[put]
        BODY = {
          "peer_asn": "65001",
          "peer_contact_detail": [
            {
              "role": "Noc",
              "email": "noc@contoso.com",
              "phone": "+1 (234) 567-8999"
            },
            {
              "role": "Policy",
              "email": "abc@contoso.com",
              "phone": "+1 (234) 567-8900"
            },
            {
              "role": "Technical",
              "email": "xyz@contoso.com",
              "phone": "+1 (234) 567-8900"
            }
          ],
          "peer_name": "Contoso"
        }
        # result = self.mgmt_client.peer_asns.create_or_update(peer_asn_name=PEER_ASN_NAME, peer_asn=BODY)

        # /Peerings/put/Create an exchange peering[put]
        BODY = {
          "sku": {
            "name": "Basic_Exchange_Free"
          },
          "kind": "Exchange",
          "location": "eastus",
          "exchange": {
            "connections": [
              {
                "peering_dbfacility_id": "99999",
                "bgp_session": {
                  "peer_session_ipv4address": "192.168.2.1",
                  "peer_session_ipv6address": "fd00::1",
                  "max_prefixes_advertised_v4": "1000",
                  "max_prefixes_advertised_v6": "100",
                  "md5authentication_key": "test-md5-auth-key"
                },
                "connection_identifier": "CE495334-0E94-4E51-8164-8116D6CD284D"
              },
              {
                "peering_dbfacility_id": "99999",
                "bgp_session": {
                  "peer_session_ipv4address": "192.168.2.2",
                  "peer_session_ipv6address": "fd00::2",
                  "max_prefixes_advertised_v4": "1000",
                  "max_prefixes_advertised_v6": "100",
                  "md5authentication_key": "test-md5-auth-key"
                },
                "connection_identifier": "CDD8E673-CB07-47E6-84DE-3739F778762B"
              }
            ],
            "peer_asn": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Peering/peerAsns/" + PEER_ASN_NAME + ""
            }
          },
          "peering_location": "peeringLocation0"
        }
        # result = self.mgmt_client.peerings.create_or_update(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, peering=BODY)

        # /Peerings/put/Create a peering with exchange route server[put]
        BODY = {
          "sku": {
            "name": "Premium_Direct_Free"
          },
          "kind": "Direct",
          "location": "eastus",
          "direct": {
            "connections": [
              {
                "bandwidth_in_mbps": "10000",
                "session_address_provider": "Peer",
                "use_for_peering_service": True,
                "peering_dbfacility_id": "99999",
                "bgp_session": {
                  "session_prefix_v4": "192.168.0.0/24",
                  "microsoft_session_ipv4address": "192.168.0.123",
                  "peer_session_ipv4address": "192.168.0.234",
                  "max_prefixes_advertised_v4": "1000",
                  "max_prefixes_advertised_v6": "100"
                },
                "connection_identifier": "5F4CB5C7-6B43-4444-9338-9ABC72606C16"
              }
            ],
            "peer_asn": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Peering/peerAsns/" + PEER_ASN_NAME + ""
            },
            "direct_peering_type": "IxRs"
          },
          "peering_location": "peeringLocation0"
        }
        # result = self.mgmt_client.peerings.create_or_update(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, peering=BODY)

        # /Peerings/put/Create a direct peering[put]
        BODY = {
          "sku": {
            "name": "Basic_Direct_Free"
          },
          "kind": "Direct",
          "location": "eastus",
          "direct": {
            "connections": [
              {
                "bandwidth_in_mbps": "10000",
                "session_address_provider": "Peer",
                "use_for_peering_service": False,
                "peering_dbfacility_id": "99999",
                "bgp_session": {
                  "session_prefix_v4": "192.168.0.0/31",
                  "session_prefix_v6": "fd00::0/127",
                  "max_prefixes_advertised_v4": "1000",
                  "max_prefixes_advertised_v6": "100",
                  "md5authentication_key": "test-md5-auth-key"
                },
                "connection_identifier": "5F4CB5C7-6B43-4444-9338-9ABC72606C16"
              },
              {
                "bandwidth_in_mbps": "10000",
                "session_address_provider": "Microsoft",
                "use_for_peering_service": True,
                "peering_dbfacility_id": "99999",
                "connection_identifier": "8AB00818-D533-4504-A25A-03A17F61201C"
              }
            ],
            "peer_asn": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Peering/peerAsns/" + PEER_ASN_NAME + ""
            },
            "direct_peering_type": "Edge"
          },
          "peering_location": "peeringLocation0"
        }
        # result = self.mgmt_client.peerings.create_or_update(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, peering=BODY)

        # /PeeringServices/put/Create a  peering service[put]
        BODY = {
          "location": "eastus",
          "peering_service_location": "California",
          "peering_service_provider": "Kordia Limited"
        }
        result = self.mgmt_client.peering_services.create_or_update(resource_group_name=RESOURCE_GROUP, peering_service_name=PEERING_SERVICE_NAME, peering_service=BODY)

        # /RegisteredAsns/put/Create or update a registered ASN for the peering[put]
        BODY = {
          "asn": "65000"
        }
        # result = self.mgmt_client.registered_asns.create_or_update(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, registered_asn_name=REGISTERED_ASN_NAME, registered_asn=BODY)

        # /Prefixes/put/Create or update a prefix for the peering service[put]
        # result = self.mgmt_client.prefixes.create_or_update(resource_group_name=RESOURCE_GROUP, peering_service_name=PEERING_SERVICE_NAME, prefix_name=PREFIX_NAME, prefix="192.168.1.0/24")

        # /RegisteredPrefixes/put/Create or update a registered prefix for the peering[put]
        BODY = {
          "prefix": "10.22.20.0/24"
        }
        # result = self.mgmt_client.registered_prefixes.create_or_update(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, registered_prefix_name=REGISTERED_PREFIX_NAME, registered_prefix=BODY)

        # /RegisteredPrefixes/get/Get a registered prefix associated with the peering[get]
        # result = self.mgmt_client.registered_prefixes.get(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, registered_prefix_name=REGISTERED_PREFIX_NAME)

        # /Prefixes/get/Get a prefix associated with the peering service[get]
        # result = self.mgmt_client.prefixes.get(resource_group_name=RESOURCE_GROUP, peering_service_name=PEERING_SERVICE_NAME, prefix_name=PREFIX_NAME)

        # /RegisteredAsns/get/Get a registered ASN associated with the peering[get]
        # result = self.mgmt_client.registered_asns.get(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, registered_asn_name=REGISTERED_ASN_NAME)

        # /Prefixes/get/List all the prefixes associated with the peering service[get]
        result = self.mgmt_client.prefixes.list_by_peering_service(resource_group_name=RESOURCE_GROUP, peering_service_name=PEERING_SERVICE_NAME)

        # /RegisteredPrefixes/get/List all the registered prefixes associated with the peering[get]
        # result = self.mgmt_client.registered_prefixes.list_by_peering(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME)

        # /PeeringServices/get/Get a peering service[get]
        result = self.mgmt_client.peering_services.get(resource_group_name=RESOURCE_GROUP, peering_service_name=PEERING_SERVICE_NAME)

        # /RegisteredAsns/get/List all the registered ASNs associated with the peering[get]
        # result = self.mgmt_client.registered_asns.list_by_peering(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME)

        # /Peerings/get/Get a peering[get]
        # result = self.mgmt_client.peerings.get(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME)

        # /PeeringServices/get/List peering services in a resource group[get]
        result = self.mgmt_client.peering_services.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /Peerings/get/List peerings in a resource group[get]
        result = self.mgmt_client.peerings.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /PeerAsns/get/Get a peer ASN[get]
        result = self.mgmt_client.peer_asns.get(peer_asn_name=PEER_ASN_NAME)

        # /PeeringServiceCountries/get/List peering service countries[get]
        result = self.mgmt_client.peering_service_countries.list()

        # /PeeringServiceLocations/get/List peering service locations[get]
        result = self.mgmt_client.peering_service_locations.list(country="country1")

        # /PeeringServiceProviders/get/List peering service providers[get]
        result = self.mgmt_client.peering_service_providers.list()

        # /PeeringLocations/get/List exchange peering locations[get]
        result = self.mgmt_client.peering_locations.list(kind="Exchange")

        # /PeeringLocations/get/List direct peering locations[get]
        result = self.mgmt_client.peering_locations.list(kind="Direct")

        # /PeeringServices/get/List peering services in a subscription[get]
        result = self.mgmt_client.peering_services.list_by_subscription()

        # /LegacyPeerings/get/List legacy peerings[get]
        result = self.mgmt_client.legacy_peerings.list(peering_location="peeringLocation0", kind="Exchange", asn="65000")

        # /PeerAsns/get/List peer ASNs in a subscription[get]
        result = self.mgmt_client.peer_asns.list_by_subscription()

        # /Peerings/get/List peerings in a subscription[get]
        result = self.mgmt_client.peerings.list_by_subscription()

        # /Operations/get/List peering operations[get]
        result = self.mgmt_client.operations.list()

        # /PeeringServices/patch/Update peering service tags[patch]
        TAGS = {
          "tag0": "value0",
          "tag1": "value1"
        }
        # result = self.mgmt_client.peering_services.update(resource_group_name=RESOURCE_GROUP, peering_service_name=PEERING_SERVICE_NAME, tags= + ToSnakeCase(k).toUpperCase() + )

        # /Peerings/patch/Update peering tags[patch]
        TAGS = {
          "tag0": "value0",
          "tag1": "value1"
        }
        # result = self.mgmt_client.peerings.update(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, tags= + ToSnakeCase(k).toUpperCase() + )

        # //post/Check if peering service provider is available in customer location[post]
        # result = self.mgmt_client.check_service_provider_availability(peering_service_location="peeringServiceLocation1", peering_service_provider="peeringServiceProvider1")

        # /RegisteredPrefixes/delete/Deletes a registered prefix associated with the peering[delete]
        # result = self.mgmt_client.registered_prefixes.delete(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, registered_prefix_name=REGISTERED_PREFIX_NAME)

        # /Prefixes/delete/Delete a prefix associated with the peering service[delete]
        # result = self.mgmt_client.prefixes.delete(resource_group_name=RESOURCE_GROUP, peering_service_name=PEERING_SERVICE_NAME, prefix_name=PREFIX_NAME)

        # /RegisteredAsns/delete/Deletes a registered ASN associated with the peering[delete]
        # result = self.mgmt_client.registered_asns.delete(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME, registered_asn_name=REGISTERED_ASN_NAME)

        # /PeeringServices/delete/Delete a peering service[delete]
        result = self.mgmt_client.peering_services.delete(resource_group_name=RESOURCE_GROUP, peering_service_name=PEERING_SERVICE_NAME)

        # /Peerings/delete/Delete a peering[delete]
        # result = self.mgmt_client.peerings.delete(resource_group_name=RESOURCE_GROUP, peering_name=PEERING_NAME)

        # /PeerAsns/delete/Delete a peer ASN[delete]
        result = self.mgmt_client.peer_asns.delete(peer_asn_name=PEER_ASN_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
