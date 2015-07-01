# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.network
from common_recordingtestcase import record
from mgmt_testcase import HttpStatusCode, AzureMgmtTestCase

class MgmtNetworkTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtNetworkTest, self).setUp()
        self.network_client = self.create_mgmt_client(azure.mgmt.network.NetworkResourceProviderClient)

    @record
    def test_public_ip_addresses(self):
        self.create_resource_group()

        public_ip_name = self.get_resource_name('pyipname')

        params_create = azure.mgmt.network.PublicIpAddress(
            location=self.region,
            public_ip_allocation_method=azure.mgmt.network.IpAllocationMethod.dynamic,
            tags={
                'key': 'value',
            },
        )
        result_create = self.network_client.public_ip_addresses.create_or_update(
            self.group_name,
            public_ip_name,
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        result_get = self.network_client.public_ip_addresses.get(
            self.group_name,
            public_ip_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)
        self.assertEqual(result_get.public_ip_address.location, self.region)
        self.assertEqual(result_get.public_ip_address.tags['key'], 'value')

        result_list = self.network_client.public_ip_addresses.list(self.group_name)
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        self.assertEqual(len(result_list.public_ip_addresses), 1)

        result_list_all = self.network_client.public_ip_addresses.list_all()
        self.assertEqual(result_list_all.status_code, HttpStatusCode.OK)
        self.assertGreater(len(result_list_all.public_ip_addresses), 0)

        result_delete = self.network_client.public_ip_addresses.delete(
            self.group_name,
            public_ip_name,
        )
        self.assertEqual(result_delete.status_code, HttpStatusCode.OK)

        result_list = self.network_client.public_ip_addresses.list(self.group_name)
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        self.assertEqual(len(result_list.public_ip_addresses), 0)

    @record
    def test_virtual_networks(self):
        self.create_resource_group()

        network_name = self.get_resource_name('pyvnet')
        subnet1_name = self.get_resource_name('pyvnetsubnetone')
        subnet2_name = self.get_resource_name('pyvnetsubnettwo')

        params_create = azure.mgmt.network.VirtualNetwork(
            location=self.region,
            address_space=azure.mgmt.network.AddressSpace(
                address_prefixes=[
                    '10.0.0.0/16',
                ],
            ),
            dhcp_options=azure.mgmt.network.DhcpOptions(
                dns_servers=[
                    '10.1.1.1',
                    '10.1.2.4',
                ],
            ),
            subnets=[
                azure.mgmt.network.Subnet(
                    name=subnet1_name,
                    address_prefix='10.0.1.0/24',
                ),
                azure.mgmt.network.Subnet(
                    name=subnet2_name,
                    address_prefix='10.0.2.0/24',
                ),
            ],
        )

        result_create = self.network_client.virtual_networks.create_or_update(
            self.group_name,
            network_name,
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        result_get = self.network_client.virtual_networks.get(
            self.group_name,
            network_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

        result_list = self.network_client.virtual_networks.list(
            self.group_name,
        )
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)

        result_list_all = self.network_client.virtual_networks.list_all()
        self.assertEqual(result_list_all.status_code, HttpStatusCode.OK)

        result_delete = self.network_client.virtual_networks.delete(
            self.group_name,
            network_name,
        )
        self.assertEqual(result_delete.status_code, HttpStatusCode.OK)

        result_list = self.network_client.virtual_networks.list(
            self.group_name,
        )
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        self.assertEqual(len(result_list.virtual_networks), 0)

    @record
    def test_dns_availability(self):
        result_check = self.network_client.check_dns_name_availability(
            self.region,
            'pydomain',
        )
        self.assertEqual(result_check.status_code, HttpStatusCode.OK)
        self.assertTrue(result_check.dns_name_availability)

    @record
    def test_subnets(self):
        self.create_resource_group()

        network_name = self.get_resource_name('pysubnet')
        subnet1_name = self.get_resource_name('pysubnetone')
        subnet2_name = self.get_resource_name('pysubnettwo')

        params_create = azure.mgmt.network.VirtualNetwork(
            location=self.region,
            address_space=azure.mgmt.network.AddressSpace(
                address_prefixes=[
                    '10.0.0.0/16',
                ],
            ),
            dhcp_options=azure.mgmt.network.DhcpOptions(
                dns_servers=[
                    '10.1.1.1',
                    '10.1.2.4',
                ],
            ),
            subnets=[
                azure.mgmt.network.Subnet(
                    name=subnet1_name,
                    address_prefix='10.0.1.0/24',
                ),
            ],
        )
        result_create = self.network_client.virtual_networks.create_or_update(
            self.group_name,
            network_name,
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        params_create = azure.mgmt.network.Subnet(
            name=subnet2_name,
            address_prefix='10.0.2.0/24',
        )
        result_create = self.network_client.subnets.create_or_update(
            self.group_name,
            network_name,
            subnet2_name,
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        result_get = self.network_client.virtual_networks.get(
            self.group_name,
            network_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)
        self.assertEqual(len(result_get.virtual_network.subnets), 2)

        result_get = self.network_client.subnets.get(
            self.group_name,
            network_name,
            subnet2_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

        result_list = self.network_client.subnets.list(
            self.group_name,
            network_name,
        )
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)

        result_delete = self.network_client.subnets.delete(
            self.group_name,
            network_name,
            subnet2_name,
        )
        self.assertEqual(result_delete.status_code, HttpStatusCode.OK)

    @record
    def test_network_security_groups(self):
        self.create_resource_group()

        security_group_name = self.get_resource_name('pysecgroup')
        security_rule_name = self.get_resource_name('pysecgrouprule')

        params_create = azure.mgmt.network.NetworkSecurityGroup(
            location=self.region,
            security_rules=[
                azure.mgmt.network.SecurityRule(
                    name=security_rule_name,
                    access=azure.mgmt.network.SecurityRuleAccess.allow,
                    description='Test security rule',
                    destination_address_prefix='*',
                    destination_port_range='123-3500',
                    direction=azure.mgmt.network.SecurityRuleDirection.inbound,
                    priority=500,
                    protocol=azure.mgmt.network.SecurityRuleProtocol.tcp,
                    source_address_prefix='*',
                    source_port_range='655',
                ),
            ],
        )
        result_create = self.network_client.network_security_groups.create_or_update(
            self.group_name,
            security_group_name,
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.OK)

        result_get = self.network_client.network_security_groups.get(
            self.group_name,
            security_group_name,
        )
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

        result_list = self.network_client.network_security_groups.list(
            self.group_name,
        )
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)

        result_list_all = self.network_client.network_security_groups.list_all()
        self.assertEqual(result_list_all.status_code, HttpStatusCode.OK)

        result_delete = self.network_client.network_security_groups.delete(
            self.group_name,
            security_group_name,
        )
        self.assertEqual(result_delete.status_code, HttpStatusCode.OK)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
