# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey
import pytest
import time
import random
import uuid
import test_config

# This test class serves to test partition splits within the query context

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class TestPartitionSplitQuery(unittest.TestCase):
    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey
    throughput = 400

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.create_database_if_not_exists(id=test_config._test_config.TEST_THROUGHPUT_DATABASE_ID,
                                                                offer_throughput=cls.throughput)
        cls.container = cls.database.create_container_if_not_exists(
            id=test_config._test_config.TEST_COLLECTION_SINGLE_PARTITION_ID,
            partition_key=PartitionKey(path="/id"))

    def test_partition_split_query(self):
        for i in range(100):
            body = self.get_test_item()
            self.container.create_item(body=body)

        print("created items, changing offer to 11k and starting queries")
        self.database.replace_throughput(11000)
        offer_time = time.time()
        print("changed offer to 11k")
        print("--------------------------------")
        print("now starting queries")

        self.run_queries(self.container, 100)  # initial check for queries before partition split
        print("initial check succeeded, now reading offer until replacing is done")
        offer = self.database.get_throughput()
        while True:
            if offer.properties['content'].get('isOfferReplacePending', False):
                time.sleep(10)
                offer = self.database.get_throughput()
            else:
                print("offer replaced successfully, took around {} seconds".format(time.time() - offer_time))
                self.run_queries(self.container, 100)  # check queries work post partition split
                print("test over")
                self.assertTrue(offer.offer_throughput > self.throughput)
                self.client.delete_database(self.configs.TEST_THROUGHPUT_DATABASE_ID)
                return

    def run_queries(self, container, iterations):
        ret_list = list()
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

    def get_test_item(self):
        test_item = {
            'id': 'Item_' + str(uuid.uuid4()),
            'test_object': True,
            'lastName': 'Smith',
            'attr1': random.randint(0, 10)
        }
        return test_item


if __name__ == "__main__":
    unittest.main()
