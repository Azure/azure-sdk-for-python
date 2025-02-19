# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
import vector_test_data
from azure.cosmos import http_constants
from azure.cosmos.partition_key import PartitionKey


def verify_ordering(item_list, distance_function):
    for i in range(len(item_list)):
        assert item_list[i]["text"] == vector_test_data.get_ordered_item_texts()[i]
    if distance_function == "euclidean":
        for i in range(len(item_list) - 1):
            assert item_list[i]["SimilarityScore"] <= item_list[i + 1]["SimilarityScore"]
    else:
        for i in range(len(item_list) - 1):
            assert item_list[i]["SimilarityScore"] >= item_list[i + 1]["SimilarityScore"]

@pytest.mark.cosmosSearchQuery
class TestVectorSimilarityQuery(unittest.TestCase):
    """Test to check vector similarity queries behavior."""

    client: cosmos_client.CosmosClient = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy
    TEST_DATABASE_ID = config.TEST_DATABASE_ID
    TEST_CONTAINER_ID = "Vector Similarity Container " + str(uuid.uuid4())

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.test_db = cls.client.create_database(str(uuid.uuid4()))
        cls.created_quantized_cosine_container = cls.test_db.create_container(
            id="quantized" + cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=test_config.TestConfig.THROUGHPUT_FOR_5_PARTITIONS,
            indexing_policy=test_config.get_vector_indexing_policy(embedding_type="quantizedFlat"),
            vector_embedding_policy=test_config.get_vector_embedding_policy(data_type="float32",
                                                                            distance_function="cosine",
                                                                            dimensions=128))
        cls.created_flat_euclidean_container = cls.test_db.create_container(
            id="flat" + cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=test_config.TestConfig.THROUGHPUT_FOR_5_PARTITIONS,
            indexing_policy=test_config.get_vector_indexing_policy(embedding_type="flat"),
            vector_embedding_policy=test_config.get_vector_embedding_policy(data_type="float32",
                                                                            distance_function="euclidean",
                                                                            dimensions=128))
        cls.created_diskANN_dotproduct_container = cls.test_db.create_container(
            id="diskANN" + cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=test_config.TestConfig.THROUGHPUT_FOR_5_PARTITIONS,
            indexing_policy=test_config.get_vector_indexing_policy(embedding_type="diskANN"),
            vector_embedding_policy=test_config.get_vector_embedding_policy(data_type="float32",
                                                                            distance_function="dotproduct",
                                                                            dimensions=128))
        cls.created_large_container = cls.test_db.create_container(
            id="large_container" + cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=test_config.TestConfig.THROUGHPUT_FOR_5_PARTITIONS,
            indexing_policy=test_config.get_vector_indexing_policy(embedding_type="quantizedFlat"),
            vector_embedding_policy=test_config.get_vector_embedding_policy(data_type="float32",
                                                                            distance_function="cosine",
                                                                            dimensions=2))
        for item in vector_test_data.get_vector_items():
            cls.created_quantized_cosine_container.create_item(item)
            cls.created_flat_euclidean_container.create_item(item)
            cls.created_diskANN_dotproduct_container.create_item(item)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.test_db.delete_container("quantized" + cls.TEST_CONTAINER_ID)
            cls.test_db.delete_container("flat" + cls.TEST_CONTAINER_ID)
            cls.test_db.delete_container("diskANN" + cls.TEST_CONTAINER_ID)
            cls.test_db.delete_container("large_container" + cls.TEST_CONTAINER_ID)
            cls.client.delete_database(cls.test_db.id)
        except exceptions.CosmosHttpResponseError:
            pass

    def test_wrong_vector_search_queries(self):
        vector_string = vector_test_data.get_embedding_string("I am having a wonderful day.")
        # try to send a vector search query without limit filters
        query = "SELECT c.text, VectorDistance(c.embedding, [{}]) AS " \
                "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}])".format(vector_string, vector_string)
        try:
            list(self.created_large_container.query_items(query=query, enable_cross_partition_query=True))
            pytest.fail("Client should not allow queries without filters.")
        except ValueError as e:
            assert "Executing a vector search query without TOP or LIMIT can consume many RUs very fast and" \
                   " have long runtimes. Please ensure you are using one of the two filters with your" \
                   " vector search query." in e.args[0]

        # try to send a vector search query specifying the ordering as ASC or DESC
        query = "SELECT c.text, VectorDistance(c.embedding, [{}]) AS " \
                "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}]) ASC".format(vector_string,
                                                                                               vector_string)
        try:
            list(self.created_large_container.query_items(query=query, enable_cross_partition_query=True))
            pytest.fail("Client should not allow queries with ASC/DESC.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.BAD_REQUEST
            # TODO: Seems like this error message differs depending on Ubuntu vs. Windows runs?
            assert ("One of the input values is invalid." in e.message
                    or "Specifying a sorting order (ASC or DESC) with VectorDistance function is not supported." in e.message)

    def test_ordering_distances(self):
        # Besides ordering distances, we also verify that the query text properly replaces any set embedding policies
        # load up previously calculated embedding for the given string
        vector_string = vector_test_data.get_embedding_string("I am having a wonderful day.")
        # test euclidean distance
        for i in range(1, 11):
            # we define queries with and without specs to directly use the embeddings in our container policies
            vanilla_query = "SELECT TOP {} c.text, VectorDistance(c.embedding, [{}]) AS " \
                            "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}])".format(str(i),
                                                                                                       vector_string,
                                                                                                       vector_string)
            specs_query = "SELECT TOP {} c.text, VectorDistance(c.embedding, [{}], false, {{'distanceFunction': 'euclidean'}}) AS " \
                          "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}], false, {{'distanceFunction': 'euclidean'}})" \
                .format(str(i), vector_string, vector_string)

            flat_list = list(self.created_flat_euclidean_container.query_items(query=vanilla_query,
                                                                               enable_cross_partition_query=True))
            verify_ordering(flat_list, "euclidean")

            quantized_list = list(
                self.created_quantized_cosine_container.query_items(query=specs_query,
                                                                    enable_cross_partition_query=True))
            verify_ordering(quantized_list, "euclidean")

            disk_ann_list = list(
                self.created_diskANN_dotproduct_container.query_items(query=specs_query,
                                                                      enable_cross_partition_query=True))
            verify_ordering(disk_ann_list, "euclidean")
        # test cosine distance
        for i in range(1, 11):
            vanilla_query = "SELECT TOP {} c.text, VectorDistance(c.embedding, [{}]) AS " \
                            "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}])".format(str(i),
                                                                                                       vector_string,
                                                                                                       vector_string)
            specs_query = "SELECT TOP {} c.text, VectorDistance(c.embedding, [{}], false, {{'distanceFunction': 'cosine'}}) AS " \
                          "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}], false, {{'distanceFunction': 'cosine'}})" \
                .format(str(i), vector_string, vector_string)

            flat_list = list(
                self.created_flat_euclidean_container.query_items(query=specs_query, enable_cross_partition_query=True))
            verify_ordering(flat_list, "cosine")

            quantized_list = list(
                self.created_quantized_cosine_container.query_items(query=vanilla_query,
                                                                    enable_cross_partition_query=True))
            verify_ordering(quantized_list, "cosine")

            disk_ann_list = list(
                self.created_diskANN_dotproduct_container.query_items(query=specs_query,
                                                                      enable_cross_partition_query=True))
            verify_ordering(disk_ann_list, "cosine")
        # test dot product distance
        for i in range(1, 11):
            vanilla_query = "SELECT TOP {} c.text, VectorDistance(c.embedding, [{}]) AS " \
                            "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}])".format(str(i),
                                                                                                       vector_string,
                                                                                                       vector_string)
            specs_query = "SELECT TOP {} c.text, VectorDistance(c.embedding, [{}], false, {{'distanceFunction': 'dotproduct'}}) AS " \
                          "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}], false, {{'distanceFunction': 'dotproduct'}})" \
                .format(str(i), vector_string, vector_string)

            flat_list = list(
                self.created_flat_euclidean_container.query_items(query=specs_query, enable_cross_partition_query=True))
            verify_ordering(flat_list, "dotproduct")

            quantized_list = list(
                self.created_quantized_cosine_container.query_items(query=specs_query,
                                                                    enable_cross_partition_query=True))
            verify_ordering(quantized_list, "dotproduct")

            disk_ann_list = list(
                self.created_diskANN_dotproduct_container.query_items(query=vanilla_query,
                                                                      enable_cross_partition_query=True))
            verify_ordering(disk_ann_list, "dotproduct")

    def test_vector_query_pagination(self):
        # load up previously calculated embedding for the given string
        vector_string = vector_test_data.get_embedding_string("I am having a wonderful day.")

        query = "SELECT TOP 8 c.text, VectorDistance(c.embedding, [{}], false, {{'distanceFunction': 'cosine'}}) AS " \
                "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}], false, {{'distanceFunction': " \
                "'cosine'}})".format(vector_string, vector_string)

        query_iterable = self.created_quantized_cosine_container.query_items(query=query,
                                                                             enable_cross_partition_query=True,
                                                                             max_item_count=3)
        all_fetched_res = []
        count = 0
        item_pages = query_iterable.by_page()
        for items in item_pages:
            count += 1
            all_fetched_res.extend(list(items))
        assert count == 3
        assert len(all_fetched_res) == 8
        verify_ordering(all_fetched_res, "cosine")

    def test_vector_query_large_data(self):
        # test different limit queries on a larger data set
        embedding_value = 0.0001
        for i in range(2000):
            item = {"id": str(i), "pk": i % 2, "embedding": [embedding_value, embedding_value]}
            self.created_large_container.create_item(item)
            embedding_value += 0.0001

        query = "SELECT c.id, VectorDistance(c.embedding, [0.0001, 0.0001], false," \
                " {'distanceFunction': 'cosine'}) AS SimilarityScore FROM c ORDER BY" \
                " VectorDistance(c.embedding, [0.0001, 0.0001], false, {'distanceFunction': 'cosine'})" \
                "OFFSET 0 LIMIT 1000"

        query_iterable = self.created_large_container.query_items(query=query,
                                                                  enable_cross_partition_query=True)
        result_list = list(query_iterable)
        assert len(result_list) == 1000

        query = "SELECT DISTINCT c.id, VectorDistance(c.embedding, [0.0001, 0.0001], false," \
                " {'distanceFunction': 'cosine'}) AS SimilarityScore FROM c ORDER BY" \
                " VectorDistance(c.embedding, [0.0001, 0.0001], false, {'distanceFunction': 'cosine'})" \
                "OFFSET 0 LIMIT 1000"

        query_iterable = self.created_large_container.query_items(query=query,
                                                                  enable_cross_partition_query=True)
        result_list = list(query_iterable)
        assert len(result_list) == 1000

        query = "SELECT TOP 750 c.id, VectorDistance(c.embedding, [0.0001, 0.0001], false," \
                " {'distanceFunction': 'cosine'}) AS SimilarityScore FROM c ORDER BY" \
                " VectorDistance(c.embedding, [0.0001, 0.0001], false, {'distanceFunction': 'cosine'})"

        query_iterable = self.created_large_container.query_items(query=query,
                                                                  enable_cross_partition_query=True)
        result_list = list(query_iterable)
        assert len(result_list) == 750

        query = "SELECT DISTINCT TOP 750 c.id, VectorDistance(c.embedding, [0.0001, 0.0001], false," \
                " {'distanceFunction': 'cosine'}) AS SimilarityScore FROM c ORDER BY" \
                " VectorDistance(c.embedding, [0.0001, 0.0001], false, {'distanceFunction': 'cosine'})"

        query_iterable = self.created_large_container.query_items(query=query,
                                                                  enable_cross_partition_query=True)
        result_list = list(query_iterable)
        assert len(result_list) == 750

        query = "SELECT c.id, VectorDistance(c.embedding, [0.0001, 0.0001], false," \
                " {'distanceFunction': 'cosine'}) AS SimilarityScore FROM c ORDER BY" \
                " VectorDistance(c.embedding, [0.0001, 0.0001], false, {'distanceFunction': 'cosine'})" \
                " OFFSET 1000 LIMIT 500"

        query_iterable = self.created_large_container.query_items(query=query,
                                                                  enable_cross_partition_query=True)
        result_list = list(query_iterable)
        assert len(result_list) == 500

        query = "SELECT DISTINCT c.id, VectorDistance(c.embedding, [0.0001, 0.0001], false," \
                " {'distanceFunction': 'cosine'}) AS SimilarityScore FROM c ORDER BY" \
                " VectorDistance(c.embedding, [0.0001, 0.0001], false, {'distanceFunction': 'cosine'})" \
                " OFFSET 1000 LIMIT 500"

        query_iterable = self.created_large_container.query_items(query=query,
                                                                  enable_cross_partition_query=True)
        result_list = list(query_iterable)
        assert len(result_list) == 500


if __name__ == "__main__":
    unittest.main()
