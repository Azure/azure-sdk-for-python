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

from azure.servicemanagement.sqldatabasemanagementservice import (
    SqlDatabaseManagementService,
    )

from azure.servicemanagement import (
    Servers,
    Server,
    Database,
    )

from util import (
    AzureTestCase,
    create_service_management,
    credentials,
    )
import unittest

class SqlDatabaseServiceTest(AzureTestCase):

    def setUp(self):
        self.sqlms = create_service_management(SqlDatabaseManagementService)

    def tearDown(self):
        self.cleanup()
        return super(SqlDatabaseServiceTest, self).tearDown()

    def cleanup(self):
        pass # No clean needed by now

    def test_list_servers(self):
        result = self.sqlms.list_servers()

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Servers)

        for server in result:
            self.assertIsInstance(server, Server)

    @unittest.skip
    def test_list_databases(self):
        result = self.sqlms.list_databases("TODO")

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

        for db in result:
            self.assertIsInstance(db, Database)
