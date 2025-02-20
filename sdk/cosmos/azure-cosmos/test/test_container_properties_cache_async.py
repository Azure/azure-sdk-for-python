# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""

import copy
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.aio import CosmosClient, _retry_utility_async, DatabaseProxy
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosLong
class TestContainerPropertiesCache(unittest.IsolatedAsyncioTestCase):
    """Python CRUD Tests.
        """

    client: CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    database_for_test: DatabaseProxy = None

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
        self.databaseForTest = await self.client.create_database_if_not_exists(self.configs.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_container_properties_cache_async(self):
        client = self.client
        database_name = self.configs.TEST_DATABASE_ID
        created_db = self.databaseForTest
        container_name = "Container Properties Cache Test " + str(uuid.uuid4())
        container_pk = "PK"
        # Create The Container
        try:
            await client.get_database_client(database_name).create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")

        # Delete The cache as this is meant to test calling operations on a preexisting container
        # and not a freshly made one. It's a private attribute so use mangled name.
        client.client_connection._CosmosClientConnection__container_properties_cache = {}
        # We will hot path operations to verify cache persists
        # This will extract partition key from the item body, which will need partition key definition from
        # container properties. We test to check the cache is empty since we just created the container
        assert client.client_connection._container_properties_cache == {}
        await client.get_database_client(database_name).get_container_client(container_name).create_item(
            body={'id': 'item1', container_pk: 'value'})
        # Since the cache was empty, it should have called a container read to get properties. So now Cache should
        # be populated and available even when we don't have a container instance
        assert client.client_connection._container_properties_cache != {}
        # We can test if the cache properties are correct by comparing them to a fresh read.
        # First lets save the old cache values
        cached_properties = await created_db.get_container_client(container_name)._get_properties()
        # Get the container dictionary out of a fresh container read
        fresh_container_read = await created_db.get_container_client(container_name).read()
        # Now we can compare the RID and Partition Key Definition
        assert cached_properties.get("_rid") == fresh_container_read.get("_rid")
        assert cached_properties.get("partitionKey") == fresh_container_read.get("partitionKey")
        await created_db.delete_container(container_name)

    async def test_container_recreate_create_upsert_replace_item_async(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")

        # This Simulates a container recreate. We save the old cache and then create
        # a new container with different partition key definition
        # for these three operations we extract the partition key value from the document
        # with a stale cache we end up extracting the wrong one so these will retry extracting
        # the partition key after refreshing the cache. Test to make sure a container recreate doesn't affect it.
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(container_name)
        try:
            await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # let's test create by replacing current container properties cache with old one
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            await created_db.get_container_client(container_name).create_item(
                body={'id': 'item1', container2_pk: 'val'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Do the same thing for upsert operation
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            await created_db.get_container_client(container_name).upsert_item(dict(id="item2", partkey="value"))
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Finally test replace item
        item = await created_db.get_container_client(container_name).read_item("item1", partition_key="val")
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            await created_db.get_container_client(container_name).replace_item(item=item, body={'id': 'item1',
                                                                                                container2_pk: 'val'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Now a negative test. We will try creating an item as if we were attempting to create it with the old container
        # This should result in an error of 400 as the container has been recreated.
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            await created_db.get_container_client(container_name).create_item(body={'id': 'item3', container_pk: 'val'})
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
        await created_db.delete_container(container_name)

    async def test_container_recreate_create_upsert_replace_item_sub_partitioning_async(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = ["/country", "/state"]
        container2_pk = ["/county", "/city"]
        # Create The Container
        try:
            await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path=container_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."

        # This Simulates a container recreate. We save the old cache and then create
        # a new container with different partition key definition
        # for these three operations we extract the partition key value from the document
        # with a stale cache we end up extracting the wrong one so these will retry extracting
        # the partition key after refreshing the cache. Test to make sure a container recreate doesn't affect it.
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(container_name)
        try:
            await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path=container2_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        # let's test create by replacing current container properties cache with old one
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            await created_db.get_container_client(container_name).create_item(
                body={'id': 'item1', 'county': 'ventura', 'city': 'oxnard'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        # Do the same thing for upsert operation
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            await created_db.get_container_client(container_name).upsert_item(
                dict(id="item2", county='Santa Barbara', city='Santa Barbara'))
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        # Finally test replace item
        item = await created_db.get_container_client(container_name).read_item("item1",
                                                                               partition_key=['ventura', 'oxnard'])
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            await created_db.get_container_client(container_name).replace_item(item=item,
                                                                               body={'id': 'item1', 'county': 'ventura',
                                                                                     'city': 'oxnard'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Now a negative test. We will try creating an item as if we were attempting to create it with the old container
        # This should result in an error of 400 as the container has been recreated.
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            await created_db.get_container_client(container_name).create_item(
                body={'id': 'item3', 'country': 'USA', 'state': 'CA'})
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400, "Expected status code 400"
        await created_db.delete_container(container_name)

    async def test_offer_throughput_container_recreate_async(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk), offer_throughput=600)
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."

        # Simulate container recreation by saving the old cache and creating a new container
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(created_container)
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk), offer_throughput=800)
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."

        # Test offer throughput by replacing current container properties cache with the old one
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            offer = await created_container.get_throughput()
            assert offer.offer_throughput == 800
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Check for replace throughput
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        new_throughput = 900
        try:
            new_offer = await created_container.replace_throughput(new_throughput)
            assert new_offer.offer_throughput == new_throughput
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        await created_db.delete_container(container_name)

    async def test_offer_throughput_container_recreate_sub_partition_async(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = ["/country", "/state"]
        container2_pk = ["/county", "/city"]
        # Create The Container
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path=container_pk), offer_throughput=600)
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."

        # Simulate container recreation by saving the old cache and creating a new container
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(created_container)
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path=container2_pk), offer_throughput=800)
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."

        # Test offer throughput by replacing current container properties cache with the old one
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            offer = await created_container.get_throughput()
            assert offer.offer_throughput == 800
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Check for replace throughput
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        new_throughput = 900
        try:
            new_offer = await created_container.replace_throughput(new_throughput)
            assert new_offer.offer_throughput == new_throughput
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        await created_db.delete_container(container_name)

    async def test_container_recreate_read_item_async(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        # Create an item to read
        try:
            item_to_read = await created_container.create_item(body={'id': 'item1', container_pk: 'val'})
            item_to_read2 = await created_container.create_item(body={'id': 'item2', container_pk: 'OtherValue'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Recreate container
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(created_container)
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        try:
            await created_container.create_item(body={'id': 'item1', container2_pk: 'val'})
            await created_container.create_item(body={'id': 'item2', container2_pk: 'DifferentValue'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        # Will fail because the original container is deleted
        try:
            await created_container.read_item(item=item_to_read, partition_key="val")
            assert False, "Read should not succeed as item no longer exists."
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404 or isinstance(e, exceptions.CosmosResourceNotFoundError)
        # Will succeed because item id and partition key value are the same as an existing one in the new container
        # But read items are not the same as their RID will be different
        read_item = await created_container.read_item(item="item1", partition_key="val")
        assert read_item != item_to_read
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            # Cache will refresh but will error out since the item no longer exists
            await created_container.read_item(item=item_to_read2, partition_key="OtherValue")
            assert False, "Read should not succeed as item no longer exists."
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404
        await created_db.delete_container(container_name)

    async def test_container_recreate_read_item_sub_partition_async(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = ["/country", "/state"]
        container2_pk = ["/county", "/city"]
        # Create The Container
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path=container_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        try:
            item_to_read = await created_container.create_item(body={'id': 'item1', 'country': 'USA', 'state': 'CA'})
            item_to_read2 = await created_container.create_item(
                body={'id': 'item2', 'country': 'MEX', 'state': 'Michoacán'})  # cspell:disable-line
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Recreate container
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(created_container)
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path=container2_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        try:
            await created_container.create_item(body={'id': 'item1', 'county': 'ventura', 'city': 'oxnard'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            # Cache will refresh but will error out since the item no longer exists
            await created_container.read_item(item=item_to_read, partition_key=['USA', 'CA'])
            assert False, "Read should not succeed as item no longer exists."
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404
        await created_db.delete_container(container_name)

    async def test_container_recreate_delete_item_async(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        # Create items
        try:
            item_to_delete = await created_container.create_item(body={'id': 'item1', container_pk: 'val'})
            await created_container.create_item(body={'id': 'item2', container_pk: 'OtherValue'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Recreate container
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(created_container)
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        try:
            await created_container.create_item(body={'id': 'item1', container2_pk: 'val'})
            await created_container.create_item(body={'id': 'item2', container2_pk: 'DifferentValue'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        # Should fail as the item no longer exists
        try:
            await created_container.delete_item(item_to_delete, partition_key='val')
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404
        await created_db.delete_container(container_name)

    async def test_container_recreate_delete_item_sub_partition_async(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = ["/country", "/state"]
        container2_pk = ["/county", "/city"]
        # Create The Container
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path=container_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        # Create items
        try:
            item_to_del = await created_container.create_item(body={'id': 'item1', 'country': 'USA', 'state': 'CA'})
            await created_container.create_item(body={'id': 'item2',
                                                      'country': 'MEX',
                                                      'state': 'Michoacán'})  # cspell:disable-line
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Recreate container
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(created_container)
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path=container2_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        try:
            await created_container.create_item(body={'id': 'item1', 'county': 'ventura', 'city': 'oxnard'})
            await created_container.create_item(
                body={'id': 'item2', 'county': 'santa barbara', 'city': 'santa barbara'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        # Should fail as the item no longer exists
        try:
            await created_container.delete_item(item_to_del, partition_key=['USA', 'CA'])
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404
        await created_db.delete_container(container_name)

    async def test_container_recreate_query_async(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # create an item to read
        try:
            item_to_read = await created_container.create_item(body={'id': 'item1', container_pk: 'val'})
            item_to_read2 = await created_container.create_item(body={'id': 'item2', container_pk: 'OtherValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Recreate container
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(created_container)
        try:
            created_container = await created_db.create_container(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        try:
            await created_container.create_item(body={'id': 'item1', container2_pk: 'val'})
            await created_container.create_item(body={'id': 'item2', container2_pk: 'DifferentValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        # Will succeed because item id and partition key value are the same as an existing one in the new container
        # But queried items are not the same as their RID will be different
        try:
            query = "SELECT * FROM c WHERE c.id = @id"
            parameters = [{"name": "@id", "value": item_to_read['id']}]
            query_result = [item async for item in created_container.query_items(query=query,
                                                                                 parameters=parameters)]
            assert len(query_result) == 1
        except exceptions.CosmosHttpResponseError as e:
            self.fail("Query should still succeed as item has same id despite the RID not matching.")
        # Will succeed because item id and partition key value are the same as an existing one in the new container
        # But queried items are not the same as their RID will be different
        query = "SELECT * FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": 'item1'}]
        query_result = [item async for item in created_container.query_items(query=query,
                                                                             parameters=parameters)]
        assert query_result[0] != item_to_read
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            # Trying to query for item from old container will return empty query
            query = "SELECT * FROM c WHERE c.partKey = @partKey"
            parameters = [{"name": "@partKey", "value": item_to_read2['PK']}]
            query_result = [item async for item in created_container.query_items(query=query,
                                                                                 parameters=parameters)]
            assert len(query_result) == 0
        except exceptions.CosmosHttpResponseError as e:
            self.fail("Query should still succeed if container is recreated.")
        await created_db.delete_container(container_name)

    async def test_container_recreate_transactional_batch(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"

        # Create The Container
        try:
            created_container = await created_db.create_container(id=container_name,
                                                                  partition_key=PartitionKey(path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")

        try:
            batch_operations = []
            for i in range(100):
                batch_operations.append(("create", ({"id": "item" + str(i), container_pk: "Microsoft"},)))

            batch_response = await created_container.execute_item_batch(batch_operations=batch_operations,
                                                                        partition_key="Microsoft")
            assert len(batch_response) == 100
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Simulate a container recreate by saving the old cache and creating a new container with a different partition key definition
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(created_container)
        try:
            created_container = await created_db.create_container(id=container_name,
                                                                  partition_key=PartitionKey(path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")

        # Test transactional batch operation by replacing current container properties cache with old one
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            batch_operations = []
            for i in range(100):
                batch_operations.append(("create", ({"id": "item" + str(i), container2_pk: "Microsoft"},)))

            batch_response = await created_container.execute_item_batch(batch_operations=batch_operations,
                                                                        partition_key="Microsoft")
            assert len(batch_response) == 100
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Negative test: Attempt to create an item with the old container properties cache, expecting a 400 error
        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)
        try:
            batch_operations = [("create", ({"id": "item" + str(101), container2_pk: "Microsoft"},))]
            batch_response = await created_container.execute_item_batch(batch_operations=batch_operations,
                                                                        partition_key="Microsoft")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400

        await created_db.delete_container(container_name)

    async def test_container_recreate_change_feed(self):
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"

        # Create the container
        try:
            created_container = await created_db.create_container(id=container_name,
                                                                  partition_key=PartitionKey(path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container should not already exist.")

        # Create initial items
        try:
            item_to_read = await created_container.create_item(body={'id': 'item1', container_pk: 'val'})
            item_to_read2 = await created_container.create_item(body={'id': 'item2', container_pk: 'OtherValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Save old container cache and recreate container
        old_cache = copy.deepcopy(client.client_connection._CosmosClientConnection__container_properties_cache)
        await created_db.delete_container(created_container)
        try:
            created_container = await created_db.create_container(id=container_name,
                                                                  partition_key=PartitionKey(path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container should not already exist.")

        # Create new items in the recreated container
        try:
            new_item1 = await created_container.create_item(body={'id': 'item3', container_pk: 'newVal'})
            new_item2 = await created_container.create_item(body={'id': 'item4', container_pk: 'newOtherValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        client.client_connection._CosmosClientConnection__container_properties_cache = copy.deepcopy(old_cache)

        # Query change feed for the new items
        change_feed = [item async for item in created_container.query_items_change_feed(start_time='Beginning')]
        assert len(change_feed) == 2

        # Verify that the change feed contains the new items
        assert any(item['id'] == 'item3' and item[container_pk] == 'newVal' for item in change_feed)
        assert any(item['id'] == 'item4' and item[container_pk] == 'newOtherValue' for item in change_feed)

        # Verify that the change feed does not contain the old items
        assert not any(item['id'] == 'item1' and item[container_pk] == 'val' for item in change_feed)
        assert not any(item['id'] == 'item2' and item[container_pk] == 'OtherValue' for item in change_feed)

        await created_db.delete_container(container_name)


if __name__ == '__main__':
    unittest.main()
