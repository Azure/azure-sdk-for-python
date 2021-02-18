# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.sql

from devtools_testutils import (
    AzureMgmtTestCase, ResourceGroupPreparer,
    AzureMgmtPreparer, FakeResource
)


def get_server_params(location):
    return {
        'location': 'westus2', #location, # "self.region" is 'west-us' by default
        'version': '12.0',
        'administrator_login': 'mysecretname',
        'administrator_login_password': 'HusH_Sec4et'
    }


class SqlServerPreparer(AzureMgmtPreparer):
    def __init__(self, name_prefix='mypysqlserverx'):
        super(SqlServerPreparer, self).__init__(name_prefix, 24)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            async_server_create = self.test_class_instance.client.servers.create_or_update(
                kwargs['resource_group'].name,
                name,
                get_server_params(kwargs['location'])
            )
            server = async_server_create.result()
        else:
            server = FakeResource(name=name, id='')

        return {
            'server': server
        }


class MgmtSqlTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSqlTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.sql.SqlManagementClient
        )

    @ResourceGroupPreparer()
    def test_server(self, resource_group, location):
        server_name = self.get_resource_name('tstpysqlserverx')

        async_server_create = self.client.servers.create_or_update(
            resource_group.name, # Created by the framework
            server_name,
            get_server_params(location),
        )
        server = async_server_create.result()
        self.assertEqual(server.name, server_name)

        server = self.client.servers.get(
            resource_group.name,
            server_name
        )
        self.assertEqual(server.name, server_name)

        my_servers = list(self.client.servers.list_by_resource_group(resource_group.name))
        self.assertEqual(len(my_servers), 1)
        self.assertEqual(my_servers[0].name, server_name)

        my_servers = list(self.client.servers.list())
        self.assertTrue(len(my_servers) >= 1)
        self.assertTrue(any(server.name == server_name for server in my_servers))

        usages = list(self.client.server_usages.list_by_server(resource_group.name, server_name))
        self.assertTrue(any(usage.name == 'server_dtu_quota' for usage in usages))

        firewall_rule_name = self.get_resource_name('firewallrule')
        firewall_rule = self.client.firewall_rules.create_or_update(
            resource_group.name,
            server_name,
            firewall_rule_name,
            "123.123.123.123",
            "123.123.123.124"
        )
        self.assertEqual(firewall_rule.name, firewall_rule_name)
        self.assertEqual(firewall_rule.start_ip_address, "123.123.123.123")
        self.assertEqual(firewall_rule.end_ip_address, "123.123.123.124")

        self.client.servers.delete(resource_group.name, server_name, polling=False)

    @ResourceGroupPreparer()
    @SqlServerPreparer()
    def test_database(self, resource_group, location, server):
        db_name = self.get_resource_name('pyarmdb')

        async_db_create = self.client.databases.create_or_update(
            resource_group.name,
            server.name,
            db_name,
            {
                'location': 'westus2' # location
            }
        )
        database = async_db_create.result() # Wait for completion and return created object
        self.assertEqual(database.name, db_name)

        db = self.client.databases.get(
            resource_group.name,
            server.name,
            db_name
        )
        self.assertEqual(db.name, db_name)

        my_dbs = list(self.client.databases.list_by_server(resource_group.name, server.name))
        print([db.name for db in my_dbs])
        self.assertEqual(len(my_dbs), 2)
        self.assertTrue(any(db.name == 'master' for db in my_dbs))
        self.assertTrue(any(db.name == db_name for db in my_dbs))

        usages = list(self.client.database_usages.list_by_database(resource_group.name, server.name, db_name))
        self.assertTrue(any(usage.name == 'database_size' for usage in usages))

        self.client.databases.delete(resource_group.name, server.name, db_name).wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
