# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import pytest
import uuid
import azure.cosmos.partition_key as partition_key
import azure.cosmos.cosmos_client as cosmos_client
import test_config

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class PartitionKeyTests(unittest.TestCase):
    """Tests to verify if non partitioned collections are properly accessed on migration with version 2018-12-31.
    """

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_database(test_config._test_config.TEST_DATABASE_ID)

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, "Session", connection_policy=cls.connectionPolicy)
        cls.created_db = test_config._test_config.create_database_if_not_exist(cls.client)
        cls.created_collection = test_config._test_config.create_multi_partition_collection_with_custom_pk_if_not_exist(cls.client)

    def test_multi_partition_collection_read_document_with_no_pk(self):
        document_definition = {'id': str(uuid.uuid4())}
        self.created_collection.create_item(body=document_definition)
        read_item = self.created_collection.read_item(item=document_definition['id'], partition_key=partition_key.NonePartitionKeyValue)
        self.assertEqual(read_item['id'], document_definition['id'])
        self.created_collection.delete_item(item=document_definition['id'], partition_key=partition_key.NonePartitionKeyValue)

    def test_hash_v2_partition_key_definition(self):
        created_container = self.created_db.create_container(
            id='container_with_pkd_v2' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id", kind="Hash")
        )
        created_container_properties = created_container.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 2)
        self.created_db.delete_container(created_container)

        created_container = self.created_db.create_container(
            id='container_with_pkd_v2' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id", kind="Hash", version=2)
        )
        created_container_properties = created_container.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 2)
        self.created_db.delete_container(created_container)

    def test_hash_v1_partition_key_definition(self):
        created_container = self.created_db.create_container(
            id='container_with_pkd_v2' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id", kind="Hash", version=1)
        )
        created_container_properties = created_container.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 1)
        self.created_db.delete_container(created_container)
