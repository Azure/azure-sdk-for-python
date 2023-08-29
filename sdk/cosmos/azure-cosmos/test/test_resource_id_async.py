# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

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

import uuid
import pytest
import test_config
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class ResourceIdTests(unittest.TestCase):
    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []

    @classmethod
    async def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, consistency_level="Session",
                                                connection_policy=cls.connectionPolicy)
        cls.databaseForTest = await cls.configs.create_database_if_not_exist(cls.client)

    async def test_id_unicode_validation(self):
        # unicode chars in Hindi for Id which translates to: "Hindi is the national language of India"
        resource_id1 = u'हिन्दी भारत की राष्ट्रीय भाषा है'  # cspell:disable-line

        # Special allowed chars for Id
        resource_id2 = "!@$%^&*()-~`'_[]{}|;:,.<>"

        # verify that databases are created with specified IDs
        created_db1 = await self.client.create_database(resource_id1)
        created_db2 = await self.client.create_database(resource_id2)

        self.assertEqual(resource_id1, created_db1.id)
        self.assertEqual(resource_id2, created_db2.id)

        # verify that collections are created with specified IDs
        created_collection1 = await created_db1.create_container(
            id=resource_id1,
            partition_key=PartitionKey(path='/id', kind='Hash'))
        created_collection2 = await created_db2.create_container(
            id=resource_id2,
            partition_key=PartitionKey(path='/id', kind='Hash'))

        self.assertEqual(resource_id1, created_collection1.id)
        self.assertEqual(resource_id2, created_collection2.id)

        # verify that collections are created with specified IDs
        item1 = await created_collection1.create_item({"id": resource_id1})
        item2 = await created_collection1.create_item({"id": resource_id2})

        self.assertEqual(resource_id1, item1.get("id"))
        self.assertEqual(resource_id2, item2.get("id"))

    def test_create_illegal_characters(self):
        database_id = str(uuid.uuid4())
        container_id = str(uuid.uuid4())
        partition_key = PartitionKey(path="/id")

        created_database = await self.client.create_database(id=database_id)
        created_container = await created_database.create_container(id=container_id, partition_key=partition_key)

        # Define illegal strings
        illegal_strings = [
            "ID_with_back/slash",
            "ID_\\with_forward_slashes",
            "ID_with_question?_mark",
            "ID_with_poun#d",
            "ID_with_tab\t",
            "ID\r_with_return_carriage",
            "ID_with_newline\n"
        ]

        # test illegal resource id's for all resources
        for resource_id in illegal_strings:
            try:
                await self.client.create_database(resource_id)
                self.fail("Database create should have failed for id {}".format(resource_id))
            except ValueError as e:
                self.assertEquals(str(e), 'Id contains illegal chars.')
            try:
                await self.client.create_database_if_not_exists(resource_id)
                self.fail("Database create should have failed for id {}".format(resource_id))
            except ValueError as e:
                self.assertEquals(str(e), 'Id contains illegal chars.')

            try:
                await created_database.create_container(id=resource_id, partition_key=partition_key)
                self.fail("Container create should have failed for id {}".format(resource_id))
            except ValueError as e:
                self.assertEquals(str(e), 'Id contains illegal chars.')
            try:
                await created_database.create_container_if_not_exists(id=resource_id, partition_key=partition_key)
                self.fail("Container create should have failed for id {}".format(resource_id))
            except ValueError as e:
                self.assertEquals(str(e), 'Id contains illegal chars.')

            try:
                await created_container.create_item({"id": resource_id})
                self.fail("Item create should have failed for id {}".format(resource_id))
            except ValueError as e:
                self.assertEquals(str(e), 'Id contains illegal chars.')
            try:
                await created_container.upsert_item({"id": resource_id})
                self.fail("Item upsert should have failed for id {}".format(resource_id))
            except ValueError as e:
                self.assertEquals(str(e), 'Id contains illegal chars.')

