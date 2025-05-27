import unittest
import uuid
import pytest
from azure.cosmos.aio import CosmosClient
import test_config
from azure.cosmos.partition_key import PartitionKey

@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
class TestChangeFeedPKVariationAsync(unittest.IsolatedAsyncioTestCase):
    """Test change feed with different partition key variations (async version)."""

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    client: CosmosClient = None

    # Items for Hash V1 partition key
    single_hash_items = [
                        {"id": str(i), "pk": f"short_string"} for i in range(1, 101)
                    ] + [
                        {"id": str(i), "pk": f"long_string_" + "a" * 251} for i in range(101, 201)
                    ] + [
                        {"id": str(i), "pk": 1000} for i in range(201, 301)
                    ] + [
                        {"id": str(i), "pk": 1000 * 1.1111} for i in range(301, 401)
                    ] + [
                        {"id": str(i), "pk": True} for i in range(401, 501)
                    ]

    # Items for Hierarchical Partition Keys
    hpk_items = [
                    {"id": str(i), "pk1": "level1_", "pk2": "level2_"} for i in range(1, 101)
                ] + [
                    {"id": str(i), "pk1": "level1_", "pk2": f"level2_long__" + "c" * 101} for i in range(101, 201)
                ] + [
                    {"id": str(i), "pk1": 10, "pk2": 1000} for i in range(201, 301)
                ] + [
                    {"id": str(i), "pk1": 10 * 1.1, "pk2": 10 * 2.2} for i in range(301, 401)
                ] + [
                        {"id": str(i), "pk1": True, 'pk2': False} for i in range(401, 501)
                    ]

    test_data_hash = [
        {
            "version": 1,
            "expected_epk": (
                "05C1DD5D8149640862636465666768696A6B6C6D6E6F70717273747576"
                "7778797A7B62636465666768696A6B6C6D6E6F70717273747576777879"
                "7A7B62636465666768696A6B6C6D6E6F707172737475767778797A7B62636465666768696A6B6C6D6E6F707172737475767700"
            ),
        },
        {
            "version": 2,
            "expected_epk": (
                "2032D236DA8678BFB900E866D7EBCE76"
            ),
        },
    ]

    @classmethod
    async def asyncSetUpClass(cls):
        cls.config = test_config.TestConfig()
        if (cls.config.masterKey == '[YOUR_KEY_HERE]' or
                cls.config.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.db = await self.client.create_database_if_not_exists(self.configs.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def create_container(self, db, container_id, partition_key, version=None, throughput=None):
        """Helper to create a container with a specific partition key definition."""
        if isinstance(partition_key, list):
            # Assume multihash (hierarchical partition key) for the container
            pk_definition = PartitionKey(path=partition_key, kind='MultiHash')
        else:
            pk_definition = PartitionKey(path=partition_key, kind='Hash', version=version)
        if throughput:
            return await db.create_container(container_id, pk_definition, offer_throughput=throughput)
        return await db.create_container(container_id, pk_definition)

    async def insert_items(self, container, items):
        """Helper to insert items into a container."""
        for item in items:
            await container.create_item(body=item)

    async def validate_changefeed(self, container):
        """Helper to validate changefeed results."""
        partition_keys = ["short_string", "long_string_" + "a" * 251, 1000, 1000 * 1.1111, True]
        for pk in partition_keys:
            changefeed = container.query_items_change_feed(is_start_from_beginning=True, partition_key=pk)
            changefeed_items = [item async for item in changefeed]

            # Perform a regular query
            regular_query = container.query_items(query="SELECT * FROM c", partition_key=pk)
            regular_query_items = [item async for item in regular_query]

            # Compare the number of documents returned
            assert len(changefeed_items) == len(regular_query_items), (
                f"Mismatch in document count for partition key {pk}: Changefeed returned {len(changefeed_items)} items, "
                f"while regular query returned {len(regular_query_items)} items."
            )

    async def validate_changefeed_hpk(self, container):
        """Helper to validate changefeed results for hierarchical partition keys."""
        partition_keys = [
            ["level1_", "level2_"],
            ["level1_", "level2_long__" + "c" * 101],
            [10, 1000],
            [10 * 1.1, 10 * 2.2],
            [True, False]
        ]
        for pk in partition_keys:
            # Perform a change feed query
            changefeed = container.query_items_change_feed(is_start_from_beginning=True, partition_key=pk)
            changefeed_items = [item async for item in changefeed]

            # Perform a regular query
            regular_query = container.query_items(query="SELECT * FROM c", partition_key=pk)
            regular_query_items = [item async for item in regular_query]

            # Compare the number of documents returned
            assert len(changefeed_items) == len(regular_query_items), (
                f"Mismatch in document count for partition key {pk}: Changefeed returned {len(changefeed_items)} items, "
                f"while regular query returned {len(regular_query_items)} items."
            )

    async def test_partition_key_hashing(self):
        """Test effective partition key string generation for different hash versions."""
        for hash_data in self.test_data_hash:
            version = hash_data["version"]
            expected_epk = hash_data["expected_epk"]
            part_k = ("abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghij"
                      "klmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz")
            partition_key = PartitionKey(
                path="/field1",
                kind="Hash",
                version=version
            )
            epk_str = partition_key._get_effective_partition_key_string(part_k)
            assert epk_str.upper() == expected_epk

    async def test_hash_v1_partition_key(self):
        """Test changefeed with Hash V1 partition key."""
        db = self.db
        container = await self.create_container(db, f"container_test_hash_V1_{uuid.uuid4()}", "/pk", version=1)
        items = self.single_hash_items
        await self.insert_items(container, items)
        await self.validate_changefeed(container)
        await self.db.delete_container(container.id)

    async def test_hash_v2_partition_key(self):
        """Test changefeed with Hash V2 partition key."""
        db = self.db
        container = await self.create_container(db, f"container_test_hash_V2_{uuid.uuid4()}", "/pk", version=2)
        items = self.single_hash_items
        await self.insert_items(container, items)
        await self.validate_changefeed(container)
        await self.db.delete_container(container.id)

    async def test_hpk_partition_key(self):
        """Test changefeed with hierarchical partition key."""
        db = self.db
        container = await self.create_container(db, f"container_test_hpk_{uuid.uuid4()}", ["/pk1", "/pk2"])
        items = self.hpk_items
        await self.insert_items(container, items)
        await self.validate_changefeed_hpk(container)
        await self.db.delete_container(container.id)

    async def test_multiple_physical_partitions_async(self):
        """Test change feed with a container having multiple physical partitions."""
        db = self.db

        # Test for Hash V1 partition key
        container_id_v1 = f"container_test_multiple_partitions_hash_v1_{uuid.uuid4()}"
        throughput = 12000  # Ensure multiple physical partitions
        container_v1 = await self.create_container(db, container_id_v1, "/pk", version=1, throughput=throughput)

        # Verify the container has more than one physical partition
        feed_ranges_v1 = container_v1.read_feed_ranges()
        feed_ranges_v1 = [feed_range async for feed_range in feed_ranges_v1]
        assert len(feed_ranges_v1) > 1, "Hash V1 container does not have multiple physical partitions."

        # Insert items and validate change feed for Hash V1
        await self.insert_items(container_v1, self.single_hash_items)
        await self.validate_changefeed(container_v1)
        await self.db.delete_container(container_v1.id)

        # Test for Hash V2 partition key
        container_id_v2 = f"container_test_multiple_partitions_hash_v2_{uuid.uuid4()}"
        container_v2 = await self.create_container(db, container_id_v2, "/pk", version=2, throughput=throughput)

        # Verify the container has more than one physical partition
        feed_ranges_v2 = container_v2.read_feed_ranges()
        feed_ranges_v2 = [feed_range async for feed_range in feed_ranges_v2]
        assert len(feed_ranges_v2) > 1, "Hash V2 container does not have multiple physical partitions."

        # Insert items and validate change feed for Hash V2
        await self.insert_items(container_v2, self.single_hash_items)
        await self.validate_changefeed(container_v2)
        await self.db.delete_container(container_v2.id)

        # Test for Hierarchical Partition Keys (HPK)
        container_id_hpk = f"container_test_multiple_partitions_hpk_{uuid.uuid4()}"
        container_hpk = await self.create_container(db, container_id_hpk, ["/pk1", "/pk2"], throughput=throughput)

        # Verify the container has more than one physical partition
        feed_ranges_hpk = container_hpk.read_feed_ranges()
        feed_ranges_hpk = [feed_range async for feed_range in feed_ranges_hpk]
        assert len(feed_ranges_hpk) > 1, "HPK container does not have multiple physical partitions."

        # Insert items and validate change feed for HPK
        await self.insert_items(container_hpk, self.hpk_items)
        await self.validate_changefeed_hpk(container_hpk)
        await self.db.delete_container(container_hpk.id)

if __name__ == '__main__':
    unittest.main()