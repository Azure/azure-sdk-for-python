﻿# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.dns
import azure.mgmt.network
from devtools_testutils import (
    AzureMgmtTestCase, ResourceGroupPreparer,
    AzureMgmtPreparer, FakeResource
)

class VirtualNetworkPreparer(AzureMgmtPreparer):
    def __init__(self, name_prefix='pvtzonevnet'):
        super(VirtualNetworkPreparer, self).__init__(name_prefix, 24)

    def create_resource(self, name, **kwargs):
        registration_virtual_network_name = name + 'reg'
        resolution_virtual_network_name = name + 'res'

        if self.is_live:
            resource_group_name = kwargs['resource_group'].name
            location_name = kwargs['location']

            registration_network = self.test_class_instance.network_client.virtual_networks.create_or_update(
                resource_group_name,
                registration_virtual_network_name,
                {
                    'location': location_name,
                    'address_space': {
                        'address_prefixes': ['10.0.0.0/8']
                    },
                    'subnets': [
                        {
                            'name': 'default',
                            'address_prefix': '10.0.0.0/24'
                        }
                    ]
                }
            ).result()

            resolution_network = self.test_class_instance.network_client.virtual_networks.create_or_update(
                resource_group_name,
                resolution_virtual_network_name,
                {
                    'location': location_name,
                    'address_space': {
                        'address_prefixes': ['10.0.0.0/8']
                    },
                    'subnets': [
                        {
                            'name': 'default',
                            'address_prefix': '10.0.0.0/24'
                        }
                    ]
                }
            ).result()

        else:
            registration_network = FakeResource(name=registration_virtual_network_name, id='')
            resolution_network = FakeResource(name=resolution_virtual_network_name, id='')

        return {
            'registration_virtual_network': registration_network,
            'resolution_virtual_network': resolution_network
        }

class MgmtDnsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDnsTest, self).setUp()
        self.dns_client = self.create_mgmt_client(
            azure.mgmt.dns.DnsManagementClient,
            base_url='https://api-dogfood.resources.windows-int.net/'
        )
        self.network_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient,
            api_version='2017-09-01',
            base_url='https://api-dogfood.resources.windows-int.net/'
        )

    @ResourceGroupPreparer(client_kwargs={'base_url':'https://api-dogfood.resources.windows-int.net/'})
    def test_public_zone(self, resource_group, location):
        zone_name = self.get_resource_name('pydns.com')

        # Zones are a 'global' resource.
        zone = self.dns_client.zones.create_or_update(
            resource_group.name,
            zone_name,
            {
                'zone_type': 'Public',
                'location': 'global'
            }
        )
        self.assertEqual(zone.name, zone_name)

        zone = self.dns_client.zones.get(
            resource_group.name,
            zone.name
        )
        self.assertEqual(zone.name, zone_name)

        zones = list(self.dns_client.zones.list_by_resource_group(
            resource_group.name
        ))
        self.assertGreaterEqual(len(zones), 1)

        zones = list(self.dns_client.zones.list())
        self.assertGreaterEqual(len(zones), 1)

        # Record set
        record_set_name = self.get_resource_name('record_set')
        self.dns_client.record_sets.create_or_update(
            resource_group.name,
            zone.name,
            record_set_name,
            'A',
            {
                 "ttl": 300,
                 "arecords": [
                     {
                        "ipv4_address": "1.2.3.4"
                     }
                 ]
            }
        )

        self.dns_client.record_sets.update(
            resource_group.name,
            zone.name,
            record_set_name,
            'A',
            {
                 "ttl": 300,
                 "arecords": [
                     {
                        "ipv4_address": "1.2.3.4"
                     },
                     {
                        "ipv4_address": "5.6.7.8"
                     }
                 ]
            }
        )

        record_set = self.dns_client.record_sets.get(
            resource_group.name,
            zone.name,
            record_set_name,
            'A'
        )
        self.assertIsNotNone(record_set)

        record_sets = list(self.dns_client.record_sets.list_by_type(
            resource_group.name,
            zone.name,
            'A'
        ))
        self.assertEqual(len(record_sets), 1)

        # NS and SOA records are created by default in public zones.
        record_sets = list(self.dns_client.record_sets.list_by_dns_zone(
            resource_group.name,
            zone.name
        ))
        self.assertEqual(len(record_sets), 3)

        self.dns_client.record_sets.delete(
            resource_group.name,
            zone.name,
            record_set_name,
            'A'
        )

        async_delete = self.dns_client.zones.delete(
            resource_group.name,
            zone.name
        )
        async_delete.wait()

    @ResourceGroupPreparer(client_kwargs={'base_url':'https://api-dogfood.resources.windows-int.net/'})
    @VirtualNetworkPreparer()
    def test_private_zone(self, resource_group, location, registration_virtual_network, resolution_virtual_network):
        zone_name = self.get_resource_name('pydns.com')

        # Zones are a 'global' resource.
        zone = self.dns_client.zones.create_or_update(
            resource_group.name,
            zone_name,
            {
                'zone_type': 'Private',
                'location': 'global',
                'registration_virtual_networks': [ { 'id': registration_virtual_network.id } ],
                'resolution_virtual_networks': [ { 'id': resolution_virtual_network.id } ]
            }
        )
        self.assertEqual(zone.name, zone_name)

        zone = self.dns_client.zones.get(
            resource_group.name,
            zone.name
        )
        self.assertEqual(zone.name, zone_name)

        zones = list(self.dns_client.zones.list_by_resource_group(
            resource_group.name
        ))
        self.assertGreaterEqual(len(zones), 1)

        zones = list(self.dns_client.zones.list())
        self.assertGreaterEqual(len(zones), 1)

        # Record set
        record_set_name = self.get_resource_name('record_set')
        self.dns_client.record_sets.create_or_update(
            resource_group.name,
            zone.name,
            record_set_name,
            'A',
            {
                 "ttl": 300,
                 "arecords": [
                     {
                        "ipv4_address": "1.2.3.4"
                     }
                 ]
            }
        )

        self.dns_client.record_sets.update(
            resource_group.name,
            zone.name,
            record_set_name,
            'A',
            {
                 "ttl": 300,
                 "arecords": [
                     {
                        "ipv4_address": "1.2.3.4"
                     },
                     {
                        "ipv4_address": "5.6.7.8"
                     }
                 ]
            }
        )

        record_set = self.dns_client.record_sets.get(
            resource_group.name,
            zone.name,
            record_set_name,
            'A'
        )
        self.assertIsNotNone(record_set)

        record_sets = list(self.dns_client.record_sets.list_by_type(
            resource_group.name,
            zone.name,
            'A'
        ))
        self.assertEqual(len(record_sets), 1)

        # SOA record is created by default in private zones.
        record_sets = list(self.dns_client.record_sets.list_by_dns_zone(
            resource_group.name,
            zone.name
        ))
        self.assertEqual(len(record_sets), 2)

        self.dns_client.record_sets.delete(
            resource_group.name,
            zone.name,
            record_set_name,
            'A'
        )

        async_delete = self.dns_client.zones.delete(
            resource_group.name,
            zone.name
        )
        async_delete.wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
