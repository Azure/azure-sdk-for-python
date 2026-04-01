# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import random
import time
import unittest
import os

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


if __name__ == "__main__":
    unittest.main()
