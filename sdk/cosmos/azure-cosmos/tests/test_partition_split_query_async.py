# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import time
import unittest
import random

import pytest

import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy

async def run_queries(container, iterations):
    ret_list = []
    for i in range(iterations):
        curr = str(random.randint(0, 10))
        query = 'SELECT * FROM c WHERE c.attr1=' + curr + ' order by c.attr1'
        qlist = [item async for item in container.query_items(query=query)]
        ret_list.append((curr, qlist))
    for ret in ret_list:
        curr = ret[0]
        if len(ret[1]) != 0:
            for results in ret[1]:
                attr_number = results['attr1']
                assert str(attr_number) == curr  # verify that all results match their randomly generated attributes
        print("validation succeeded for all query results")


@pytest.mark.cosmosSplit
class TestPartitionSplitQueryAsync(unittest.IsolatedAsyncioTestCase):
    database: DatabaseProxy = None
    container: ContainerProxy = None
    client: CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    throughput = 400
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_CONTAINER_ID = "Single-partition-container-without-throughput-async"
    MAX_TIME = 60 * 10  # 10 minutes for the test to complete, should be enough for partition split to complete

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        await self.client.__aenter__()
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
        self.container = await self.created_database.create_container(
            id=self.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=self.throughput)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_partition_split_query_async(self):
        for i in range(100):
            body = test_config.get_test_item()
            await self.container.create_item(body=body)

        start_time = time.time()
        print("created items, changing offer to 11k and starting queries")
        await self.container.replace_throughput(11000)
        offer_time = time.time()
        print("changed offer to 11k")
        print("--------------------------------")
        print("now starting queries")

        await run_queries(self.container, 100)  # initial check for queries before partition split
        print("initial check succeeded, now reading offer until replacing is done")
        offer = await self.container.get_throughput()
        while True:
            if time.time() - start_time > self.MAX_TIME:  # timeout test at 10 minutes
                self.skipTest("Partition split didn't complete in time.")
            if offer.properties['content'].get('isOfferReplacePending', False):
                time.sleep(30)  # wait for the offer to be replaced, check every 30 seconds
                offer = await self.container.get_throughput()
            else:
                print("offer replaced successfully, took around {} seconds".format(time.time() - offer_time))
                await run_queries(self.container, 100)  # check queries work post partition split
                self.assertTrue(offer.offer_throughput > self.throughput)
                return

if __name__ == '__main__':
    unittest.main()
