# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import time
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import hybrid_search_data
import test_config
from azure.cosmos import http_constants, CosmosClient as CosmosSyncClient
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosSearchQuery
class TestFullTextHybridSearchQueryAsync(unittest.IsolatedAsyncioTestCase):
    """Test to check full text search and hybrid search queries behavior."""

    client: CosmosClient = None
    sync_client: CosmosSyncClient = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy
    TEST_CONTAINER_ID = "Full Text Container " + str(uuid.uuid4())

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.sync_client = CosmosSyncClient(cls.host, cls.masterKey)
        cls.test_db = cls.sync_client.create_database(str(uuid.uuid4()))
        cls.test_container = cls.test_db.create_container(
            id="FTS" + cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=test_config.TestConfig.THROUGHPUT_FOR_2_PARTITIONS,
            indexing_policy=test_config.get_full_text_indexing_policy(path="/text"),
            full_text_policy=test_config.get_full_text_policy(path="/text"))
        data = hybrid_search_data.get_full_text_items()
        for index, item in enumerate(data.get("items")):
            item['id'] = str(index)
            item['pk'] = str((index % 2) + 1)
            cls.test_container.create_item(item)
        # Need to give the container time to index all the recently added items - 10 minutes seems to work
        time.sleep(10 * 60)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.sync_client.delete_database(cls.test_db.id)
        except exceptions.CosmosHttpResponseError:
            pass

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.test_db = self.client.get_database_client(self.test_db.id)
        self.test_container = self.test_db.get_container_client(self.test_container.id)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_wrong_hybrid_search_queries_async(self):
        try:
            query = "SELECT c.index, RRF(VectorDistance(c.vector, [1,2,3]), FullTextScore(c.text, 'test') FROM c"
            results = self.test_container.query_items(query)
            [item async for item in results]
            pytest.fail("Attempting to project RRF in a query should fail.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
            assert ("One of the input values is invalid" in e.message or
                    "Syntax error, incorrect syntax near 'FROM'" in e.message)

        try:
            query = "SELECT TOP 10 c.index FROM c WHERE FullTextContains(c.title, 'John')" \
                    " ORDER BY RANK FullTextScore(c.title, 'John') DESC"
            results = self.test_container.query_items(query)
            [item async for item in results]
            pytest.fail("Attempting to set an ordering direction in a full text score query should fail.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
            assert ("One of the input values is invalid" in e.message or
                    "Specifying a sort order (ASC or DESC) in the ORDER BY RANK clause is not allowed." in e.message)

        try:
            query = "SELECT TOP 10 c.index FROM c WHERE FullTextContains(c.title, 'John')" \
                    " ORDER BY RANK RRF(FullTextScore(c.title, 'John'), VectorDistance(c.vector, [1,2,3])) DESC"
            results = self.test_container.query_items(query)
            [item async for item in results]
            pytest.fail("Attempting to set an ordering direction in a hybrid search query should fail.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
            assert ("One of the input values is invalid" in e.message or
                    "Specifying a sort order (ASC or DESC) in the ORDER BY RANK clause is not allowed." in e.message)

    async def test_hybrid_search_env_variables_async(self):
        os.environ["AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS"] = "0"
        try:
            query = "SELECT TOP 1 c.index, c.title FROM c WHERE FullTextContains(c.title, 'John') OR " \
                    "FullTextContains(c.text, 'John') ORDER BY RANK FullTextScore(c.title, 'John')"
            results = self.test_container.query_items(query)
            [item async for item in results]
            pytest.fail("Config was not applied properly.")
        except ValueError as e:
            assert e.args[0] == ("Executing a hybrid search query with more items than the max is not allowed. "
                                 "Please ensure you are using a limit smaller than the max, or change the max.")
        finally:
            os.environ["AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS"] = "1000"

    async def test_hybrid_search_queries_async(self):
        query = "SELECT TOP 10 c.index, c.title FROM c WHERE FullTextContains(c.title, 'John') OR " \
                "FullTextContains(c.text, 'John') ORDER BY RANK FullTextScore(c.title, 'John')"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 3
        for res in result_list:
            assert res['index'] in [2, 85, 57]

        query = "SELECT TOP 10 c.index, c.title FROM c WHERE FullTextContains(c.title, 'John')" \
                " OR FullTextContains(c.text, 'John') ORDER BY RANK FullTextScore(c.title, 'John')"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 3
        for res in result_list:
            assert res['index'] in [2, 85, 57]

        query = "SELECT c.index, c.title FROM c WHERE FullTextContains(c.title, 'John')" \
                " OR FullTextContains(c.text, 'John') ORDER BY RANK FullTextScore(c.title, 'John') OFFSET 1 LIMIT 5"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 2
        for res in result_list:
            assert res['index'] in [85, 57]

        query = "SELECT TOP 20 c.index, c.title FROM c WHERE FullTextContains(c.title, 'John') OR " \
                "FullTextContains(c.text, 'John') OR FullTextContains(c.text, 'United States') " \
                "ORDER BY RANK RRF(FullTextScore(c.title, ['John']), FullTextScore(c.text, 'United States'))"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 15
        for res in result_list:
            assert res['index'] in [61, 51, 49, 54, 75, 24, 77, 76, 80, 25, 22, 2, 66, 57, 85]

        query = "SELECT TOP 10 c.index, c.title FROM c WHERE " \
                "FullTextContains(c.title, 'John') OR FullTextContains(c.text, 'John') OR " \
                "FullTextContains(c.text, 'United States') ORDER BY RANK RRF(FullTextScore(c.title, 'John')," \
                " FullTextScore(c.text, 'United States'))"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        for res in result_list:
            assert res['index'] in [61, 51, 49, 54, 75, 24, 77, 76, 80, 25]

        query = "SELECT c.index, c.title FROM c WHERE FullTextContains(c.title, 'John')" \
                " OR FullTextContains(c.text, 'John') OR FullTextContains(c.text, 'United States') ORDER BY " \
                "RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States')) OFFSET 5 LIMIT 10"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        for res in result_list:
            assert res['index'] in [24, 77, 76, 80, 25, 22, 2, 66, 57, 85]

        query = "SELECT TOP 10 c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'))"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        for res in result_list:
            assert res['index'] in [61, 51, 49, 54, 75, 24, 77, 76, 80, 25]

        query = "SELECT c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States')) " \
                "OFFSET 0 LIMIT 13"
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 13
        for res in result_list:
            assert res['index'] in [61, 51, 49, 54, 75, 24, 77, 76, 80, 25, 22, 2, 66]

        read_item = await self.test_container.read_item('50', '1')
        item_vector = read_item['vector']
        query = "SELECT c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.text, 'United States'), VectorDistance(c.vector, {})) " \
                "OFFSET 0 LIMIT 10".format(item_vector)
        results = self.test_container.query_items(query)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        for res in result_list:
            assert res['index'] in [51, 54, 28, 70, 24, 61, 56, 26, 58, 77]

    async def test_hybrid_search_query_pagination_async(self):
        query = "SELECT c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States')) " \
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

    async def test_hybrid_search_cross_partition_query_response_hook_async(self):
        item = await self.test_container.read_item('50', '1')
        item_vector = item['vector']
        response_hook = test_config.ResponseHookCaller()
        query = "SELECT c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.text, 'United States'), VectorDistance(c.vector, {})) " \
                "OFFSET 0 LIMIT 10".format(item_vector)
        results = self.test_container.query_items(query, response_hook=response_hook)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        assert response_hook.count == 6 # one global stat query per partition, two queries per partition for each component query

    async def test_hybrid_search_partitioned_query_response_hook_async(self):
        item = await self.test_container.read_item('50', '1')
        item_vector = item['vector']
        response_hook = test_config.ResponseHookCaller()
        query = "SELECT c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.text, 'United States'), VectorDistance(c.vector, {})) " \
                "OFFSET 0 LIMIT 10".format(item_vector)
        results = self.test_container.query_items(query, partition_key='1', response_hook=response_hook)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        assert response_hook.count == 1

    async def test_hybrid_search_weighted_reciprocal_rank_fusion_async(self):
        # Test case 1
        query = """
                    SELECT TOP 15 c.index AS Index, c.title AS Title, c.text AS Text
                    FROM c
                    WHERE FullTextContains(c.title, 'John') OR FullTextContains(c.text, 'John') OR FullTextContains(c.text, 'United States')
                    ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'), [1, 1])
                """
        results = self.test_container.query_items(query)
        result_list = [res['Index'] async for res in results]
        # If some scores rank the same the order of the results may change
        assert result_list in [
            [61, 51, 49, 54, 75, 24, 77, 76, 80, 25, 22, 2, 66, 57, 85],
            [61, 51, 49, 54, 75, 24, 77, 76, 80, 25, 22, 2, 66, 85, 57]
        ]

        # Test case 2
        query = """
                    SELECT TOP 15 c.index AS Index, c.title AS Title, c.text AS Text
                    FROM c
                    WHERE FullTextContains(c.title, 'John') OR FullTextContains(c.text, 'John') OR FullTextContains(c.text, 'United States')
                    ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'), [10, 10])
                """
        results = self.test_container.query_items(query)
        result_list = [res['Index'] async for res in results]
        # If some scores rank the same the order of the results may change
        assert result_list in [
            [61, 51, 49, 54, 75, 24, 77, 76, 80, 25, 22, 2, 66, 57, 85],
            [61, 51, 49, 54, 75, 24, 77, 76, 80, 25, 22, 2, 66, 85, 57]
        ]

        # Test case 3
        query = """
                    SELECT TOP 10 c.index AS Index, c.title AS Title, c.text AS Text
                    FROM c
                    WHERE FullTextContains(c.title, 'John') OR FullTextContains(c.text, 'John') OR FullTextContains(c.text, 'United States')
                    ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'), [0.1, 0.1])
                """
        results = self.test_container.query_items(query)
        result_list = [res['Index'] async for res in results]
        assert result_list == [61, 51, 49, 54, 75, 24, 77, 76, 80, 25]

        # Test case 4
        query = """
                    SELECT TOP 15 c.index AS Index, c.title AS Title, c.text AS Text
                    FROM c
                    WHERE FullTextContains(c.title, 'John') OR FullTextContains(c.text, 'John') OR FullTextContains(c.text, 'United States')
                    ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'), [-1, -1])
                """
        results = self.test_container.query_items(query)
        result_list = [res['Index'] async for res in results]
        # If some scores rank the same the order of the results may change
        assert result_list in [
            [85, 57, 66, 2, 22, 25, 77, 76, 80, 75, 24, 49, 54, 51, 81],
            [57, 85, 2, 66, 22, 25, 80, 76, 77, 24, 75, 54, 49, 51, 61]
        ]

        # Test case 5
        read_item = await self.test_container.read_item('50', '1')
        item_vector = read_item['vector']
        query = "SELECT c.index, c.title FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.text, 'United States'), VectorDistance(c.vector, {}), [1,1]) " \
                "OFFSET 0 LIMIT 10".format(item_vector)
        results = self.test_container.query_items(query, enable_cross_partition_query=True)
        result_list = [res async for res in results]
        assert len(result_list) == 10
        result_list = [res['index'] for res in result_list]
        assert result_list == [51, 54, 28, 70, 24, 61, 56, 26, 58, 77]

    async def test_invalid_hybrid_search_queries_weighted_reciprocal_rank_fusion_async(self):
        try:
            query = "SELECT c.index, RRF(VectorDistance(c.vector, [1,2,3]), FullTextScore(c.text, 'test') FROM c"
            results = self.test_container.query_items(query)
            [item async for item in results]
            pytest.fail("Attempting to project RRF in a query should fail.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST

    async def test_weighted_vs_non_weighted_reciprocal_rank_fusion_async(self):
        # Non-weighted RRF query
        query_non_weighted = """
            SELECT TOP 10 c.index, c.title FROM c
            ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'))
        """
        results_non_weighted = self.test_container.query_items(query_non_weighted)
        result_list_non_weighted = [res['index'] async for res in results_non_weighted]

        # Weighted RRF query with equal weights
        query_weighted_equal = """
            SELECT TOP 10 c.index, c.title FROM c
            ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'), [1, 1])
        """
        results_weighted_equal = self.test_container.query_items(query_weighted_equal)
        result_list_weighted_equal = [res['index'] async for res in results_weighted_equal]

        # Weighted RRF query with different direction weights
        query_weighted_different = """
            SELECT TOP 10 c.index, c.title FROM c
            ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'), [1, -0.5])
        """
        results_weighted_different = self.test_container.query_items(query_weighted_different)
        result_list_weighted_different = [res['index'] async for res in results_weighted_different]

        # Assertions
        assert result_list_non_weighted == result_list_weighted_equal, "Non-weighted and equally weighted RRF results should match."
        assert result_list_non_weighted != result_list_weighted_different, "Non-weighted and differently direction weighted RRF results should not match."

    async def test_weighted_reciprocal_rank_fusion_with_missing_or_extra_weights_async(self):
        try:
            # Weighted RRF query with one weight missing
            query_missing_weight = """
                SELECT TOP 10 c.index, c.title FROM c
                ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'), [1])
            """
            res = self.test_container.query_items(query_missing_weight)
            [item async for item in res]
            pytest.fail("Query with missing weights should fail.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST

        try:
            # Weighted RRF query with an extra weight
            query_extra_weight = """
                SELECT TOP 10 c.index, c.title FROM c
                ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'), [1, 1, 1])
            """
            results_extra_weight = self.test_container.query_items(query_extra_weight)
            [item async for item in results_extra_weight]
            pytest.fail("Query with extra weights should fail.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST

    async def test_weighted_reciprocal_rank_fusion_with_response_hook_async(self):
        response_hook = test_config.ResponseHookCaller()
        query_weighted_rrf = """
            SELECT TOP 10 c.index, c.title FROM c
            ORDER BY RANK RRF(FullTextScore(c.title, 'John'), FullTextScore(c.text, 'United States'), [1, 0.5])
        """
        results = self.test_container.query_items(query_weighted_rrf, response_hook=response_hook)
        result_list = [item async for item in results]
        assert len(result_list) == 10
        assert response_hook.count > 0  # Ensure the response hook was called





if __name__ == "__main__":
    unittest.main()
