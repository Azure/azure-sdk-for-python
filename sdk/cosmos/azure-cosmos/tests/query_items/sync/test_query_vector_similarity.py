# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original vector ordering, pagination, limit and hook tests with owned resources.

Core Python provisions and seeds the three original 128-dimensional container
configurations at the original throughput. Only query execution selects Rust.
Pagination and hook tests provision only their quantized-flat/cosine container.
Rejection and buffer-limit tests use the original empty two-dimensional container.
The larger-data test seeds that container through Core Python in its original body.
The original shared/AAD setup is not included.
"""

import os
import unittest
import uuid
from unittest.mock import patch

import pytest

from config import settings
from common import _test_helpers as test_config
import vector_test_data
from azure.cosmos import ContainerProxy, CosmosClient, PartitionKey, exceptions, http_constants


def verify_ordering(item_list, distance_function):
    for i in range(len(item_list)):
        assert item_list[i]["text"] == vector_test_data.get_ordered_item_texts()[i]
    if distance_function == "euclidean":
        for i in range(len(item_list) - 1):
            assert item_list[i]["SimilarityScore"] <= item_list[i + 1]["SimilarityScore"]
    else:
        for i in range(len(item_list) - 1):
            assert item_list[i]["SimilarityScore"] >= item_list[i + 1]["SimilarityScore"]


@pytest.mark.cosmosAADQuery
@pytest.mark.cosmosSearchQuery
class TestVectorSimilarityQuery(unittest.TestCase):
    created_quantized_cosine_container: ContainerProxy
    created_flat_euclidean_container: ContainerProxy
    created_diskANN_dotproduct_container: ContainerProxy
    created_large_container: ContainerProxy

    def setUp(self):
        if self._testMethodName == "test_vector_search_environment_variables_rust":
            name = "AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"
            previous = os.environ.get(name)
            if previous is None:
                self.addCleanup(os.environ.pop, name, None)
            else:
                self.addCleanup(os.environ.__setitem__, name, previous)
        self.key_client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python"
        )
        self.addCleanup(self.key_client.close)
        self.database_id = "legacy_vector_ordering_" + uuid.uuid4().hex
        print(f"\nCreating owned vector query database: {self.database_id}")
        database = self.key_client.create_database(self.database_id)
        self.addCleanup(self._delete_owned_database)
        print(f"\nOwned vector ordering database: {self.database_id}")
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
        )
        self.addCleanup(self.client.close)
        data_database = self.client.get_database_client(self.database_id)
        profiles = (
            ("created_quantized_cosine_container", "quantizedFlat", "cosine", 128),
            ("created_flat_euclidean_container", "flat", "euclidean", 128),
            ("created_diskANN_dotproduct_container", "diskANN", "dotproduct", 128),
        )
        if self._testMethodName in (
            "test_vector_query_pagination_rust", "test_vector_query_cross_partition_response_hook_rust",
            "test_vector_query_partitioned_response_hook_rust",
        ):
            profiles = profiles[:1]
        elif self._testMethodName in (
            "test_wrong_vector_search_queries_rust", "test_vector_search_environment_variables_rust",
            "test_vector_query_large_data_rust",
        ):
            profiles = (("created_large_container", "quantizedFlat", "cosine", 2),)
        for attribute, index_type, distance_function, dimensions in profiles:
            container = database.create_container(
                id=index_type,
                partition_key=PartitionKey(path="/pk"),
                offer_throughput=settings.TestSettings.THROUGHPUT_FOR_2_PARTITIONS,
                indexing_policy=test_config.get_vector_indexing_policy(embedding_type=index_type),
                vector_embedding_policy=test_config.get_vector_embedding_policy(
                    data_type="float32", distance_function=distance_function, dimensions=dimensions
                ),
            )
            if attribute != "created_large_container":
                for item in vector_test_data.get_vector_items():
                    container.create_item(item)
            query_container = data_database.get_container_client(container.id)
            if self._testMethodName == "test_vector_query_large_data_rust":
                # Preserve in-method seeding without migrating writes along with queries.
                seed_patch = patch.object(query_container, "create_item", container.create_item)
                seed_patch.start()
                self.addCleanup(seed_patch.stop)
            setattr(self, attribute, query_container)

    def _delete_owned_database(self):
        self.key_client.delete_database(self.database_id)
        print(f"\nDeleted owned vector ordering database: {self.database_id}")

    def test_wrong_vector_search_queries_rust(self):
        # Source: tests/test_query_vector_similarity.py::TestVectorSimilarityQuery.test_wrong_vector_search_queries
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

    def test_vector_search_environment_variables_rust(self):
        # Source: tests/test_query_vector_similarity.py::TestVectorSimilarityQuery.test_vector_search_environment_variables
        vector_string = vector_test_data.get_embedding_string("I am having a wonderful day.")
        query = "SELECT TOP 10 c.text, VectorDistance(c.embedding, [{}]) AS " \
                "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}])".format(vector_string, vector_string)
        os.environ["AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"] = "1"
        try:
            [item for item in self.created_large_container.query_items(query=query, enable_cross_partition_query=True)]
            pytest.fail("Config was not set correctly.")
        except ValueError as e:
            assert e.args[0] == ("Executing a vector search query with more items than the max is not allowed. "
                                 "Please ensure you are using a limit smaller than the max, or change the max.")

        os.environ["AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"] = "50000"
        [item for item in self.created_large_container.query_items(query=query, enable_cross_partition_query=True)]

    def test_vector_query_pagination_rust(self):
        # Source: tests/test_query_vector_similarity.py::TestVectorSimilarityQuery.test_vector_query_pagination
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

    def test_vector_query_cross_partition_response_hook_rust(self):
        # Source: tests/test_query_vector_similarity.py::TestVectorSimilarityQuery.test_vector_query_cross_partition_response_hook
        # load up previously calculated embedding for the given string
        vector_string = vector_test_data.get_embedding_string("I am having a wonderful day.")

        query = "SELECT TOP 5 c.text, VectorDistance(c.embedding, [{}], false, {{'distanceFunction': 'cosine'}}) AS " \
                "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}], false, {{'distanceFunction': " \
                "'cosine'}})".format(vector_string, vector_string)

        response_hook = test_config.ResponseHookCaller()
        query_iterable = self.created_quantized_cosine_container.query_items(query=query,
                                                                             enable_cross_partition_query=True,
                                                                             response_hook=response_hook)
        result_list = list(query_iterable)
        assert len(result_list) == 5
        assert response_hook.count == 2

    def test_vector_query_partitioned_response_hook_rust(self):
        # Source: tests/test_query_vector_similarity.py::TestVectorSimilarityQuery.test_vector_query_partitioned_response_hook
        # load up previously calculated embedding for the given string
        vector_string = vector_test_data.get_embedding_string("I am having a wonderful day.")

        query = "SELECT TOP 4 c.text, VectorDistance(c.embedding, [{}], false, {{'distanceFunction': 'cosine'}}) AS " \
                "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}], false, {{'distanceFunction': " \
                "'cosine'}})".format(vector_string, vector_string)

        response_hook = test_config.ResponseHookCaller()
        query_iterable = self.created_quantized_cosine_container.query_items(query=query,
                                                                             partition_key='1',
                                                                             response_hook=response_hook)
        result_list = list(query_iterable)
        assert len(result_list) == 4
        assert response_hook.count == 1

    def test_vector_query_large_data_rust(self):
        # Source: tests/test_query_vector_similarity.py::TestVectorSimilarityQuery.test_vector_query_large_data
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

    def test_ordering_distances_rust(self):
        # Source: tests/test_query_vector_similarity.py::TestVectorSimilarityQuery.test_ordering_distances
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
