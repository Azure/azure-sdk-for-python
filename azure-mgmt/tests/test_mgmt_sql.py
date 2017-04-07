# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.sql
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtSqlTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSqlTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.sql.SqlManagementClient
        )
        # I don't record resource group creation, since it's another package
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_server(self):
        server_name = self.get_resource_name('tstpysqlserver')

        server = self.client.servers.create_or_update(
            self.group_name, # Created by the framework
            server_name,
            {
                'location': self.region, # "self.region" is 'west-us' by default
                'version': '12.0',
                'administrator_login': 'mysecretname',
                'administrator_login_password': 'HusH_Sec4et'
            }
        )
        self.assertEqual(server.name, server_name)

        server = self.client.servers.get(
            self.group_name,
            server_name
        )
        self.assertEqual(server.name, server_name)

        my_servers = list(self.client.servers.list_by_resource_group(self.group_name))
        self.assertEqual(len(my_servers), 1)
        self.assertEqual(my_servers[0].name, server_name)

        my_servers = list(self.client.servers.list())
        self.assertTrue(len(my_servers) >= 1)
        self.assertTrue(any(server.name == server_name for server in my_servers))

        usages = list(self.client.servers.list_usages(self.group_name, server_name))
        # FIXME test content of "usages", not just the call

        firewall_rule_name = self.get_resource_name('firewallrule')
        firewall_rule = self.client.firewall_rules.create_or_update(
            self.group_name,
            server_name,
            firewall_rule_name,
            "123.123.123.123",
            "123.123.123.124"
        )
        self.assertEquals(firewall_rule.name, firewall_rule_name)
        self.assertEquals(firewall_rule.start_ip_address, "123.123.123.123")
        self.assertEquals(firewall_rule.end_ip_address, "123.123.123.124")

        self.client.servers.delete(self.group_name, server_name)

    @record
    def test_database(self):
        server_name = self.get_resource_name('mypysqlserver')
        db_name = self.get_resource_name('pyarmdb')

        server = self.client.servers.create_or_update(
            self.group_name, # Created by the framework
            server_name,
            {
                'location': self.region, # "self.region" is 'west-us' by default
                'version': '12.0',
                'administrator_login': 'mysecretname',
                'administrator_login_password': 'HusH_Sec4et'
            }
        )
        self.assertEqual(server.name, server_name)

        async_db_create = self.client.databases.create_or_update(
            self.group_name,
            server_name,
            db_name,
            {
                'location': self.region
            }
        )
        database = async_db_create.result() # Wait for completion and return created object
        self.assertEqual(database.name, db_name)    
         
        db = self.client.databases.get(
            self.group_name,
            server_name,
            db_name
        )
        self.assertEqual(server.name, server_name)

        my_dbs = list(self.client.databases.list_by_server(self.group_name, server_name))
        print([db.name for db in my_dbs])
        self.assertEqual(len(my_dbs), 2)
        self.assertEqual(my_dbs[0].name, 'master')
        self.assertEqual(my_dbs[1].name, db_name)

        usages = list(self.client.databases.list_usages(self.group_name, server_name, db_name))
        # FIXME test content of "usages", not just the call

        self.client.databases.delete(self.group_name, server_name, db_name)




#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
