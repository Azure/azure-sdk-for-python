# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import json
import time
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
import test_config
import hybrid_search_data
from azure.cosmos import http_constants, DatabaseProxy
from azure.cosmos.partition_key import PartitionKey


class TestFullTextHybridSearchQueryAsync(unittest.IsolatedAsyncioTestCase):
    """Test to check full text search and hybrid search queries behavior."""

    created_db: DatabaseProxy = None
    client: CosmosClient = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy
    TEST_DATABASE_ID = config.TEST_DATABASE_ID
    TEST_CONTAINER_ID = "Full Text Container " + str(uuid.uuid4())

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    async def asyncSetUp(self):
        self.test_db = await self.client.create_database(str(uuid.uuid4()))
        self.test_container = await self.test_db.create_container(
            id="FTS" + self.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=test_config.TestConfig.THROUGHPUT_FOR_1_PARTITION,
            indexing_policy=test_config.get_full_text_indexing_policy(path="/text"),
            full_text_policy=test_config.get_full_text_policy(path="/text"))
        data = hybrid_search_data.get_full_text_items()
        for index, item in enumerate(data.get("items")):
            item['id'] = str(index)
            await self.test_container.create_item(item)
        # Need to give the container time to index all the recently added items - 10 minutes seems to work
        time.sleep(10 * 60)

    async def tearDown(self):
        try:
            await self.test_db.delete_container(self.test_container.id)
            await self.client.delete_database(self.test_db.id)
        except exceptions.CosmosHttpResponseError:
            pass
        await self.client.close()

    async def test_wrong_queries_async(self):
        try:
            query = "SELECT c.index, RRF(VectorDistance(c.vector, [1,2,3]), FullTextScore(c.text, “test”) FROM c"
            results = self.test_container.query_items(query, enable_cross_partition_query=True)
            [item async for item in results]
            pytest.fail("Attempting to project RRF in a query should fail.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
            assert "One of the inputs is invalid" in e.message

        try:
            query = "SELECT TOP 10 c.index FROM c WHERE FullTextContains(c.title, 'John')" \
                    " ORDER BY RANK FullTextScore(c.title, ['John']) DESC"
            results = self.test_container.query_items(query, enable_cross_partition_query=True)
            [item async for item in results]
            pytest.fail("Attempting to set an ordering direction in a full text score query should fail.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
            assert "One of the inputs is invalid" in e.message

        try:
            query = "SELECT TOP 10 c.index FROM c WHERE FullTextContains(c.title, 'John')" \
                    " ORDER BY RANK RRF(FullTextScore(c.title, ['John']), VectorDistance(c.vector, [1,2,3])) DESC"
            results = self.test_container.query_items(query, enable_cross_partition_query=True)
            [item async for item in results]
            pytest.fail("Attempting to set an ordering direction in a hybrid search query should fail.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
            assert "One of the inputs is invalid" in e.message

    async def test_hybrid_search_queries_async(self):
        query = "SELECT TOP 10 c.index, c.title FROM c WHERE FullTextContains(c.title, 'John') OR " \
                "FullTextContains(c.text, 'John') ORDER BY RANK FullTextScore(c.title, ['John'])"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 3
        for res in result_list:
            assert res['index'] in [2, 85, 57]

        query = "SELECT TOP 10 c.index, c.title FROM c WHERE FullTextContains(c.title, 'John')" \
                " OR FullTextContains(c.text, 'John') ORDER BY RANK FullTextScore(c.title, ['John'])"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 3
        for res in result_list:
            assert res['index'] in [2, 85, 57]

        query = "SELECT c.index, c.title FROM c WHERE FullTextContains(c.title, 'John')" \
                " OR FullTextContains(c.text, 'John') ORDER BY RANK FullTextScore(c.title, ['John']) OFFSET 1 LIMIT 5"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 2
        for res in result_list:
            assert res['index'] in [85, 57]

        query = "SELECT TOP 20 c.index, c.title FROM c WHERE FullTextContains(c.title, 'John') OR " \
                "FullTextContains(c.text, 'John') OR FullTextContains(c.text, 'United States') " \
                "ORDER BY RANK RRF(FullTextScore(c.title, ['John']), FullTextScore(c.text, ['United States']))"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 15
        for res in result_list:
            assert res['index'] in [61, 51, 49, 54, 75, 24, 77, 76, 80, 25, 22, 2, 66, 57, 85]

        query = "SELECT TOP 10 c.index, c.title FROM c WHERE " \
                "FullTextContains(c.title, 'John') OR FullTextContains(c.text, 'John') OR " \
                "FullTextContains(c.text, 'United States') ORDER BY RANK RRF(FullTextScore(c.title, ['John'])," \
                " FullTextScore(c.text, ['United States']))"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        for res in result_list:
            assert res['index'] in [61, 51, 49, 54, 75, 24, 77, 76, 80, 25]

        query = "SELECT c.index, c.title FROM c WHERE FullTextContains(c.title, 'John')" \
                " OR FullTextContains(c.text, 'John') OR FullTextContains(c.text, 'United States') ORDER BY " \
                "RANK RRF(FullTextScore(c.title, ['John']), FullTextScore(c.text, ['United States'])) OFFSET 5 LIMIT 10"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        for res in result_list:
            assert res['index'] in [24, 77, 76, 80, 25, 22, 2, 66, 57, 85]

        query = "SELECT TOP 10 c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.title, ['John']), FullTextScore(c.text, ['United States']))"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        for res in result_list:
            assert res['index'] in [61, 51, 49, 54, 75, 24, 77, 76, 80, 25]

        query = "SELECT c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.title, ['John']), FullTextScore(c.text, ['United States'])) " \
                "OFFSET 0 LIMIT 13"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 13
        for res in result_list:
            assert res['index'] in [61, 51, 49, 54, 75, 24, 77, 76, 80, 25, 22, 2, 66]

        read_item = await self.test_container.read_item('50', '50')
        item_vector = read_item['vector']
        query = "SELECT c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.text, ['United States']), VectorDistance(c.vector, {})) " \
                "OFFSET 0 LIMIT 10".format(item_vector)
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        for res in result_list:
            assert res['index'] in [51, 54, 28, 70, 24, 61, 56, 26, 58, 77]

    async def test_hybrid_search_query_pagination_async(self):
        query = "SELECT c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.title, ['John']), FullTextScore(c.text, ['United States'])) " \
                "OFFSET 0 LIMIT 13"
        query_iterable = self.test_container.query_items(query, max_item_count=5)
        all_fetched_res = []
        count = 0
        item_pages = query_iterable.by_page()
        async for items in item_pages:
            count += 1
            all_fetched_res.extend([item async for item in items])
        assert count == 3
        assert len(all_fetched_res) == 13


if __name__ == "__main__":
    unittest.main()
