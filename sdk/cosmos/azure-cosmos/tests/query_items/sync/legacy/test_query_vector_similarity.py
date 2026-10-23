# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original vector-distance ordering queries with owned key-auth resources.

Core Python provisions and seeds the three original 128-dimensional container
configurations at the original throughput. Only query execution selects Rust.
The unused large-data container and original shared/AAD setup are not included.
"""

import os
import unittest
import uuid

import pytest

import test_config
import vector_test_data
from azure.cosmos import ContainerProxy, CosmosClient, PartitionKey


def verify_ordering(item_list, distance_function):
    for i in range(len(item_list)):
        assert item_list[i]["text"] == vector_test_data.get_ordered_item_texts()[i]
    if distance_function == "euclidean":
        for i in range(len(item_list) - 1):
            assert item_list[i]["SimilarityScore"] <= item_list[i + 1]["SimilarityScore"]
    else:
        for i in range(len(item_list) - 1):
            assert item_list[i]["SimilarityScore"] >= item_list[i + 1]["SimilarityScore"]


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosSearchQuery
class TestVectorSimilarityQuery(unittest.TestCase):
    created_quantized_cosine_container: ContainerProxy
    created_flat_euclidean_container: ContainerProxy
    created_diskANN_dotproduct_container: ContainerProxy

    def setUp(self):
        self.key_client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python"
        )
        self.addCleanup(self.key_client.close)
        self.database_id = "legacy_vector_ordering_" + uuid.uuid4().hex
        database = self.key_client.create_database(self.database_id)
        self.addCleanup(self._delete_owned_database)
        print(f"\nOwned vector ordering database: {self.database_id}")
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
        )
        self.addCleanup(self.client.close)
        data_database = self.client.get_database_client(self.database_id)
        for attribute, index_type, distance_function in (
            ("created_quantized_cosine_container", "quantizedFlat", "cosine"),
            ("created_flat_euclidean_container", "flat", "euclidean"),
            ("created_diskANN_dotproduct_container", "diskANN", "dotproduct"),
        ):
            container = database.create_container(
                id=index_type,
                partition_key=PartitionKey(path="/pk"),
                offer_throughput=test_config.TestConfig.THROUGHPUT_FOR_2_PARTITIONS,
                indexing_policy=test_config.get_vector_indexing_policy(embedding_type=index_type),
                vector_embedding_policy=test_config.get_vector_embedding_policy(
                    data_type="float32", distance_function=distance_function, dimensions=128
                ),
            )
            for item in vector_test_data.get_vector_items():
                container.create_item(item)
            setattr(self, attribute, data_database.get_container_client(container.id))

    def _delete_owned_database(self):
        self.key_client.delete_database(self.database_id)
        print(f"\nDeleted owned vector ordering database: {self.database_id}")

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
