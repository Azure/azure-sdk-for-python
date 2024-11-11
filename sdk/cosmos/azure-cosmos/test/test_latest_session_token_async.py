# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import random
import time
import unittest
import uuid


import test_config
from azure.cosmos import PartitionKey
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._session_token_helpers import is_compound_session_token, parse_session_token
from azure.cosmos.aio import DatabaseProxy
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import HttpHeaders


def create_item(hpk):
    if hpk:
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'state': 'CA',
            'city': 'LA' + str(random.randint(1, 10)),
            'zipcode': '90001'
        }
    else:
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'pk': 'A' + str(random.randint(1, 10))
        }
    return item


class TestLatestSessionTokenAsync(unittest.IsolatedAsyncioTestCase):
    """Test for session token helpers"""

    created_db: DatabaseProxy = None
    client: CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.database = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def tearDown(self):
        await self.client.delete_database(self.database.id)
        await self.client.close()

    async def test_latest_session_token_from_logical_pk(self):
        container = await self.database.create_container("test_updated_session_token_from_logical_pk" + str(uuid.uuid4()),
                                                   PartitionKey(path="/pk"),
                                                   offer_throughput=400)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        target_pk = 'A1'
        target_feed_range = await container.feed_range_from_partition_key(target_pk)
        target_session_token, previous_session_token = await self.create_items_logical_pk(container, target_feed_range,
                                                                                    previous_session_token,
                                                                                    feed_ranges_and_session_tokens)
        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)

        assert session_token == target_session_token
        feed_ranges_and_session_tokens.append((target_feed_range, session_token))

        await self.trigger_split(container, 11000)

        target_session_token, _ = await self.create_items_logical_pk(container, target_feed_range, session_token,
                                                               feed_ranges_and_session_tokens)
        target_feed_range = await container.feed_range_from_partition_key(target_pk)
        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)

        assert session_token == target_session_token
        await self.database.delete_container(container.id)

    async def test_latest_session_token_from_physical_pk(self):
        container = await self.database.create_container("test_updated_session_token_from_physical_pk" + str(uuid.uuid4()),
                                                   PartitionKey(path="/pk"),
                                                   offer_throughput=400)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        pk_feed_range = await container.feed_range_from_partition_key('A1')
        target_session_token, target_feed_range, previous_session_token = await self.create_items_physical_pk(container, pk_feed_range,
                                                                                                        previous_session_token,
                                                                                                        feed_ranges_and_session_tokens)

        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert session_token == target_session_token

        await self.trigger_split(container, 11000)

        _, target_feed_range, previous_session_token = await self.create_items_physical_pk(container, pk_feed_range,
                                                                                     session_token,
                                                                                     feed_ranges_and_session_tokens)

        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert is_compound_session_token(session_token)
        session_tokens = session_token.split(",")
        assert len(session_tokens) == 2
        pk_range_id1, session_token1 = parse_session_token(session_tokens[0])
        pk_range_id2, session_token2 = parse_session_token(session_tokens[1])
        pk_range_ids = [pk_range_id1, pk_range_id2]

        assert 320 == (session_token1.global_lsn + session_token2.global_lsn)
        assert '1' in pk_range_ids
        assert '2' in pk_range_ids
        await self.database.delete_container(container.id)

    async def test_latest_session_token_hpk(self):
        container = await self.database.create_container("test_updated_session_token_hpk" + str(uuid.uuid4()),
                                                   PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"),
                                                   offer_throughput=400)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        pk = ['CA', 'LA1', '90001']
        pk_feed_range = await container.feed_range_from_partition_key(pk)
        target_session_token, target_feed_range, previous_session_token = await self.create_items_physical_pk(container,
                                                                                                        pk_feed_range,
                                                                                                        previous_session_token,
                                                                                                        feed_ranges_and_session_tokens,
                                                                                                        True)

        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert session_token == target_session_token
        await self.database.delete_container(container.id)


    async def test_latest_session_token_logical_hpk(self):
        container = await self.database.create_container("test_updated_session_token_from_logical_hpk" + str(uuid.uuid4()),
                                                   PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"),
                                                   offer_throughput=400)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        target_pk = ['CA', 'LA1', '90001']
        target_feed_range = await container.feed_range_from_partition_key(target_pk)
        target_session_token, previous_session_token = await self.create_items_logical_pk(container, target_feed_range,
                                                                                    previous_session_token,
                                                                                    feed_ranges_and_session_tokens,
                                                                                    True)
        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)

        assert session_token == target_session_token
        await self.database.delete_container(container.id)


    @staticmethod
    async def trigger_split(container, throughput):
        print("Triggering a split in session token helpers")
        await container.replace_throughput(throughput)
        print("changed offer to 11k")
        print("--------------------------------")
        print("Waiting for split to complete")
        start_time = time.time()

        while True:
            offer = await container.get_throughput()
            if offer.properties['content'].get('isOfferReplacePending', False):
                if time.time() - start_time > 60 * 25:  # timeout test at 25 minutes
                    unittest.skip("Partition split didn't complete in time.")
                else:
                    print("Waiting for split to complete")
                    time.sleep(60)
            else:
                break
        print("Split in session token helpers has completed")

    @staticmethod
    async def create_items_logical_pk(container, target_pk_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
        target_session_token = ""
        for i in range(100):
            item = create_item(hpk)
            response = await container.create_item(item, session_token=previous_session_token)
            session_token = response.get_response_headers()[HttpHeaders.SessionToken]
            pk = item['pk'] if not hpk else [item['state'], item['city'], item['zipcode']]
            pk_feed_range = await container.feed_range_from_partition_key(pk)
            pk_feed_range_epk = FeedRangeInternalEpk.from_json(pk_feed_range)
            target_feed_range_epk = FeedRangeInternalEpk.from_json(target_pk_range)
            if (pk_feed_range_epk.get_normalized_range() ==
                    target_feed_range_epk.get_normalized_range()):
                target_session_token = session_token
            previous_session_token = session_token
            feed_ranges_and_session_tokens.append((pk_feed_range,
                                                   session_token))
        return target_session_token, previous_session_token

    @staticmethod
    async def create_items_physical_pk(container, pk_feed_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
        target_session_token = ""
        container_feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        target_feed_range = None
        for feed_range in container_feed_ranges:
            if await container.is_feed_range_subset(feed_range, pk_feed_range):
                target_feed_range = feed_range
                break

        for i in range(100):
            item = create_item(hpk)
            response = await container.create_item(item, session_token=previous_session_token)
            session_token = response.get_response_headers()[HttpHeaders.SessionToken]
            if hpk:
                pk = [item['state'], item['city'], item['zipcode']]
                curr_feed_range = await container.feed_range_from_partition_key(pk)
            else:
                curr_feed_range = await container.feed_range_from_partition_key(item['pk'])
            if await container.is_feed_range_subset(target_feed_range, curr_feed_range):
                target_session_token = session_token
            previous_session_token = session_token
            feed_ranges_and_session_tokens.append((curr_feed_range, session_token))

        return target_session_token, target_feed_range, previous_session_token

if __name__ == '__main__':
    unittest.main()
