# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.dns
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtDnsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDnsTest, self).setUp()
        self.dns_client = self.create_mgmt_client(
            azure.mgmt.dns.DnsManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_dns(self):
        account_name = self.get_resource_name('pydns.com')

        # The only valid value is 'global', otherwise you will get a:
        # The subscription is not registered for the resource type 'dnszones' in the location 'westus'.
        zone = self.dns_client.zones.create_or_update(
            self.group_name,
            account_name,
            {
                'location': 'global'
            }
        )
        self.assertEqual(zone.name, account_name)

        zone = self.dns_client.zones.get(
            self.group_name,
            zone.name
        )
        self.assertEqual(zone.name, account_name)

        zones = list(self.dns_client.zones.list_by_resource_group(
            self.group_name
        ))
        self.assertEqual(len(zones), 1)

        zones = list(self.dns_client.zones.list())
        self.assertEqual(len(zones), 1)

        # Record set
        record_set_name = self.get_resource_name('record_set')
        record_set = self.dns_client.record_sets.create_or_update(
            self.group_name,
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
            self.group_name,
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
            self.group_name,
            zone.name,
            record_set_name,
            'A'
        )

        record_sets = list(self.dns_client.record_sets.list_by_type(
            self.group_name,
            zone.name,
            'A'
        ))
        self.assertEqual(len(record_sets), 1)

        record_sets = list(self.dns_client.record_sets.list_by_dns_zone(
            self.group_name,
            zone.name
        ))
        self.assertEqual(len(record_sets), 3)

        self.dns_client.record_sets.delete(
            self.group_name,
            zone.name,
            record_set_name,
            'A'
        )

        async_delete = self.dns_client.zones.delete(
            self.group_name,
            zone.name
        )
        async_delete.wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
