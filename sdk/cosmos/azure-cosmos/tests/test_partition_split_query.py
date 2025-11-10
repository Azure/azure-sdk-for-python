# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import random
import time
import unittest
import os
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, PartitionKey, ContainerProxy
from azure.cosmos.exceptions import CosmosHttpResponseError


def run_queries(container, iterations):
    ret_list = []
    for i in range(iterations):
        curr = str(random.randint(0, 10))
        query = 'SELECT * FROM c WHERE c.attr1=' + curr + ' order by c.attr1'
        qlist = list(container.query_items(query=query, enable_cross_partition_query=True))
        ret_list.append((curr, qlist))
    for ret in ret_list:
        curr = ret[0]
        if len(ret[1]) != 0:
            for results in ret[1]:
                attr_number = results['attr1']
                assert str(attr_number) == curr  # verify that all results match their randomly generated attributes
        print("validation succeeded for all query results")


@pytest.mark.cosmosSplit
class TestPartitionSplitQuery(unittest.TestCase):
    database: DatabaseProxy = None
    container: ContainerProxy = None
    client: cosmos_client.CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    throughput = 400
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_CONTAINER_ID = "Single-partition-container-without-throughput"
    MAX_TIME = 60 * 10  # 10 minutes for the test to complete, should be enough for partition split to complete

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.container = cls.database.create_container(
            id=cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=cls.throughput)
        if cls.host == "https://localhost:8081/":
            os.environ["AZURE_COSMOS_DISABLE_NON_STREAMING_ORDER_BY"] = "True"

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls.database.delete_container(cls.container.id)
        except CosmosHttpResponseError:
            pass

    def test_partition_split_query(self):
        for i in range(100):
            body = test_config.get_test_item()
            self.container.create_item(body=body)

        start_time = time.time()
        print("created items, changing offer to 11k and starting queries")
        self.container.replace_throughput(11000)
        offer_time = time.time()
        print("changed offer to 11k")
        print("--------------------------------")
        print("now starting queries")

        run_queries(self.container, 100)  # initial check for queries before partition split
        print("initial check succeeded, now reading offer until replacing is done")
        offer = self.container.get_throughput()
        while True:
            if time.time() - start_time > self.MAX_TIME:  # timeout test at 10 minutes
                self.skipTest("Partition split didn't complete in time")
            if offer.properties['content'].get('isOfferReplacePending', False):
                time.sleep(30)  # wait for the offer to be replaced, check every 30 seconds
                offer = self.container.get_throughput()
            else:
                print("offer replaced successfully, took around {} seconds".format(time.time() - offer_time))
                run_queries(self.container, 100)  # check queries work post partition split
                self.assertTrue(offer.offer_throughput > self.throughput)
                return

    def test_partial_partition_split_and_query(self):
        """
        Tests that a query can succeed when only a subset of partitions have split.
        This validates that tryCombine correctly merges routing map updates.
        """
        container_id = 'multi_partition_container'
        multi_partition_container = self.database.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000  # Start with 2 physical partitions
        )

        try:
            # Create items distributed across several logical partitions
            print(f"Populating container '{container_id}' with data across multiple partitions.")
            for i in range(50):
                item = {
                    'id': f"item_{i}_{uuid.uuid4()}",
                    'pk': f"pk_{i % 2}",  # Distribute across 2 partition keys
                    'attr1': str(random.randint(0, 10))
                }
                multi_partition_container.create_item(item)
            print("Data population complete.")

            # Run a query to establish a baseline and cache the routing map
            print("Running initial query to cache routing map.")
            run_queries(multi_partition_container, 1)
            print("Initial query successful.")

            # Increase throughput to trigger a partition split.
            # From 2 partitions (11k RU) to 3 partitions (25k RU).
            new_throughput = 25000
            print(f"Increasing throughput to {new_throughput} to trigger partition split.")
            offer_time = time.time()
            multi_partition_container.replace_throughput(new_throughput)
            offer = multi_partition_container.get_throughput()

            # Wait for the offer replacement (and partition split) to complete
            while True:
                if time.time() - offer_time > self.MAX_TIME:
                    self.skipTest("Partition split did not complete within the time limit.")

                if offer.properties['content'].get('isOfferReplacePending', False):
                    print("Waiting for offer replacement to complete...")
                    time.sleep(30)
                    offer = multi_partition_container.get_throughput()
                else:
                    print(f"Offer replaced successfully in {time.time() - offer_time:.2f} seconds.")
                    break

            # Run query post-split. This will fail if tryCombine does not correctly merge
            # the new routing info for the split partition with the old info for stable partitions.
            print("Running query post-partition split to validate routing map update.")
            run_queries(multi_partition_container, 1)
            print("Query successful after partial partition split.")

            final_offer = multi_partition_container.get_throughput()
            self.assertEqual(final_offer.offer_throughput, new_throughput)

        finally:
            # Clean up the created container
            self.database.delete_container(container_id)
            print(f"Cleaned up container '{container_id}'.")

    def test_query_with_targeted_split(self):
        """
        Tests that queries succeed after a partition split triggered by a throughput increase.
        """
        container_id = 'split_container_' + str(uuid.uuid4())
        multi_partition_container = self.database.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000  # High throughput to ensure at least 2 partitions
        )

        try:
            # 1. Insert data into two logical partitions
            print(f"Populating container '{container_id}' with data.")
            for i in range(200):
                item = {
                    'id': f"item_{i}_{uuid.uuid4()}",
                    'pk': f"pk_{i % 2}",  # Distribute across 2 partition keys
                    'attr1': str(random.randint(0, 10))
                }
                multi_partition_container.create_item(item)
            print("Data population complete.")

            # 2. Run initial queries to verify data and cache the routing map
            print("Running initial queries before partition split.")
            run_queries(multi_partition_container, 1)
            print("Initial queries successful.")

            # 3. Increase throughput to trigger a partition split
            new_throughput = 25000
            print(f"Increasing throughput to {new_throughput} RU/s to trigger partition split.")
            offer_time = time.time()
            multi_partition_container.replace_throughput(new_throughput)

            # 4. Wait for the offer replacement (and split) to complete
            offer = multi_partition_container.get_throughput()
            while True:
                if time.time() - offer_time > self.MAX_TIME:
                    self.skipTest("Partition split did not complete within the time limit.")

                if offer.properties['content'].get('isOfferReplacePending', False):
                    print("Waiting for offer replacement to complete...")
                    time.sleep(30)
                    offer = multi_partition_container.get_throughput()
                else:
                    print(f"Offer replaced successfully in {time.time() - offer_time:.2f} seconds.")
                    break

            # 5. Run queries again post-split to verify the SDK handles the routing map refresh
            print("Running queries post-partition split.")
            run_queries(multi_partition_container, 1)
            print("Queries after partition split were successful.")

            final_offer = multi_partition_container.get_throughput()
            self.assertEqual(final_offer.offer_throughput, new_throughput)

        finally:
            # Clean up the created container
            self.database.delete_container(container_id)
            print(f"Cleaned up container '{container_id}'.")

if __name__ == "__main__":
    unittest.main()
