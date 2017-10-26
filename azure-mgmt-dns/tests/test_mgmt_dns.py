# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.dns
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtDnsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDnsTest, self).setUp()
        self.dns_client = self.create_mgmt_client(
            azure.mgmt.dns.DnsManagementClient
        )

    @ResourceGroupPreparer()
    def test_dns(self, resource_group, location):
        account_name = self.get_resource_name('pydns.com')

        # The only valid value is 'global', otherwise you will get a:
        # The subscription is not registered for the resource type 'dnszones' in the location 'westus'.
        zone = self.dns_client.zones.create_or_update(
            resource_group.name,
            account_name,
            {
                'location': 'global'
            }
        )
        self.assertEqual(zone.name, account_name)

        zone = self.dns_client.zones.get(
            resource_group.name,
            zone.name
        )
        self.assertEqual(zone.name, account_name)

        zones = list(self.dns_client.zones.list_by_resource_group(
            resource_group.name
        ))
        self.assertEqual(len(zones), 1)

        zones = list(self.dns_client.zones.list())
        self.assertEqual(len(zones), 1)

        # Record set
        record_set_name = self.get_resource_name('record_set')
        record_set = self.dns_client.record_sets.create_or_update(
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
                        "ipv4_address": "1.2.3.5"
                     }
                 ]
            }
        )

        record_set = self.dns_client.record_sets.update(
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
                        "ipv4_address": "1.2.3.5"
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

        record_sets = list(self.dns_client.record_sets.list_by_type(
            resource_group.name,
            zone.name,
            'A'
        ))
        self.assertEqual(len(record_sets), 1)

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


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
