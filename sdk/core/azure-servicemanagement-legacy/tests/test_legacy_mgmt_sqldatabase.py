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

from azure.servicemanagement import (
    EventLog,
    ServerQuota,
    Server,
    Servers,
    ServiceObjective,
    Database,
    FirewallRule,
    SqlDatabaseManagementService,
)
from testutils.common_recordingtestcase import (
    TestMode,
    record,
)
from tests.legacy_mgmt_testcase import LegacyMgmtTestCase


class LegacyMgmtSqlDatabaseTest(LegacyMgmtTestCase):

    def setUp(self):
        super(LegacyMgmtSqlDatabaseTest, self).setUp()

        self.sqlms = self.create_service_management(SqlDatabaseManagementService)

        self.created_server = None

    def tearDown(self):
        if not self.is_playback():
            if self.created_server:
                try:
                    self.sqlms.delete_server(self.created_server)
                except:
                    pass

        return super(LegacyMgmtSqlDatabaseTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _create_server(self):
        result = self.sqlms.create_server('azuredb', 'T5ii-B48x', 'West US')
        self.created_server = result.server_name

    def _server_exists(self, server_name):
        result = self.sqlms.list_servers()
        match = [s for s in result if s.name == server_name]
        return len(match) == 1

    def _create_database(self, name):
        result = self.sqlms.create_database(
            self.created_server,
            name,
            'dd6d99bb-f193-4ec1-86f2-43d3bccbc49c',
            edition='Basic'
        )

    #--Operations for servers -------------------------------------------------
    @record
    def test_create_server(self):
        # Arrange

        # Act
        result = self.sqlms.create_server('azuredb', 'T5ii-B48x', 'West US')
        self.created_server = result.server_name

        # Assert
        self.assertGreater(len(result.server_name), 0)
        self.assertGreater(len(result.fully_qualified_domain_name), 0)
        self.assertTrue(self._server_exists(self.created_server))

    @record
    def test_set_server_admin_password(self):
        # Arrange
        self._create_server()

        # Act
        result = self.sqlms.set_server_admin_password(self.created_server, 'U6jj-C59y')

        # Assert
        self.assertIsNone(result)

    @record
    def test_delete_server(self):
        # Arrange
        self._create_server()

        # Act
        result = self.sqlms.delete_server(self.created_server)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._server_exists(self.created_server))

    @record
    def test_list_servers(self):
        # Arrange
        self._create_server()

        # Act
        result = self.sqlms.list_servers()

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Servers)

        for server in result:
            self.assertIsInstance(server, Server)

        match = [s for s in result if s.name == self.created_server][0]
        self.assertEqual(match.name, self.created_server)
        self.assertEqual(match.administrator_login, 'azuredb')
        self.assertEqual(match.location, 'West US')
        self.assertEqual(match.geo_paired_region, '')
        self.assertTrue(match.fully_qualified_domain_name.startswith(self.created_server))
        self.assertGreater(len(match.version), 0)

    @record
    def test_list_quotas(self):
        # Arrange
        self._create_server()

        # Act
        result = self.sqlms.list_quotas(self.created_server)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

        for quota in result:
            self.assertIsInstance(quota, ServerQuota)
            self.assertGreater(len(quota.name), 0)
            self.assertGreater(quota.value, 0)

    #--Operations for firewall rules ------------------------------------------
    @record
    def test_create_firewall_rule(self):
        # Arrange
        self._create_server()

        # Act
        result = self.sqlms.create_firewall_rule(self.created_server,
                                                 'AllowAll',
                                                 '192.168.144.0',
                                                 '192.168.144.255')

        # Assert
        self.assertIsNone(result)

    @record
    def test_delete_firewall_rule(self):
        # Arrange
        self._create_server()
        result = self.sqlms.create_firewall_rule(self.created_server,
                                                 'AllowAll',
                                                 '192.168.144.0',
                                                 '192.168.144.255')

        # Act
        result = self.sqlms.delete_firewall_rule(self.created_server,
                                                 'AllowAll')

        # Assert
        self.assertIsNone(result)

    @record
    def test_update_firewall_rule(self):
        # Arrange
        self._create_server()
        result = self.sqlms.create_firewall_rule(self.created_server,
                                                 'AllowAll',
                                                 '192.168.144.0',
                                                 '192.168.144.255')

        # Act
        result = self.sqlms.update_firewall_rule(self.created_server,
                                                 'AllowAll',
                                                 '192.168.116.0',
                                                 '192.168.116.255')

        # Assert
        self.assertIsNone(result)

    @record
    def test_list_firewall_rules(self):
        # Arrange
        self._create_server()
        result = self.sqlms.create_firewall_rule(self.created_server,
                                                 'AllowAll',
                                                 '192.168.144.0',
                                                 '192.168.144.255')

        # Act
        result = self.sqlms.list_firewall_rules(self.created_server)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

        for rule in result:
            self.assertIsInstance(rule, FirewallRule)

    @record
    def test_list_service_level_objectives(self):
        # Arrange
        self._create_server()

        # Act
        result = self.sqlms.list_service_level_objectives(self.created_server)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

        for rule in result:
            self.assertIsInstance(rule, ServiceObjective)

    @record
    def test_create_database(self):
        # Arrange
        self._create_server()

        # Act
        result = self.sqlms.create_database(
            self.created_server,
            'testdb',
            'dd6d99bb-f193-4ec1-86f2-43d3bccbc49c',
            edition='Basic'
        )

        # Assert
        self.assertIsNone(result)

    @record
    def test_delete_database(self):
        # Arrange
        self._create_server()
        self._create_database('temp')

        # Act
        result = self.sqlms.delete_database(self.created_server, 'temp')

        # Assert
        result = self.sqlms.list_databases(self.created_server)
        match = [d for d in result if d.name == 'temp']
        self.assertEqual(len(match), 0)

    @record
    def test_update_database(self):
        # Arrange
        self._create_server()
        self._create_database('temp')

        # Act
        result = self.sqlms.update_database(self.created_server,
                                            'temp',
                                            'newname')

        # Assert
        result = self.sqlms.list_databases(self.created_server)
        match = [d for d in result if d.name == 'newname']
        self.assertEqual(len(match), 1)

    @record
    def test_list_databases(self):
        # Arrange
        self._create_server()
        self._create_database('temp')

        # Act
        result = self.sqlms.list_databases(self.created_server)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

        for db in result:
            self.assertIsInstance(db, Database)

        match = [d for d in result if d.name == 'temp'][0]
        self.assertEqual(match.name, 'temp')
        self.assertEqual(match.state, 'Normal')
        self.assertGreater(match.max_size_bytes, 0)
        self.assertGreater(match.id, 0)
        self.assertGreater(len(match.edition), 0)
        self.assertGreater(len(match.collation_name), 0)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
