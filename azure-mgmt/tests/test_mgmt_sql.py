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
            # Set the "self.group_name" with an unique name
            self.create_resource_group()

    @record
    def test_server(self):
        # Get an unique name hashed from the method name
        server_name = self.get_resource_name('mypysqlserver')

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
        # Available asserts: https://docs.python.org/3/library/unittest.html
        self.assertEqual(server.name, server_name)
        # Add asserts if necessary

        server = self.client.servers.get_by_resource_group(
            self.group_name,
            server_name
        )
        self.assertEqual(server.name, server_name)

        # List operations from Autorest return an "iterable" object
        # This means that doing this:
        my_servers = self.client.servers.list_by_resource_group(self.group_name)
        # "my_servers" is an iterable object ready to be iterated.
        # This means that currently, it takes no memory and no Rest calls has been made

        # For the purpose of testing, it's simpler to tranform it as 
        # an explicit list
        my_servers = list(my_servers)
        # To build an explicit list, we made all the Rest calls.
        # Now, all objects are in memory
        self.assertEqual(len(my_servers), 1)
        self.assertEqual(my_servers[0].name, server_name)

        # Create a DB is an LRO operation
        db_name = self.get_resource_name('pyarmdb')
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
                
        # More tests!!


        # Teardown destroys the ResourceGroup for you.



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
