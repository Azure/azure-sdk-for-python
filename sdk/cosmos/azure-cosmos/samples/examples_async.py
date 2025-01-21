# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
from azure.cosmos import exceptions, PartitionKey
from azure.cosmos.aio import CosmosClient

import os


async def examples_async():
    # All interaction with Cosmos DB starts with an instance of the CosmosClient
    # In order to use the asynchronous client, we need to use async/await keywords,
    # which can only be used within async methods like examples_async() here

    # Since this is an asynchronous client, in order to properly use it you also have to warm it up and close it down.
    # We recommend using the `async with` keywords like below to start your clients - these keywords
    # create a context manager that automatically warms up, initializes, and cleans up the client, so you don't have to.

    # [START create_client]
    url = os.environ["ACCOUNT_URI"]
    key = os.environ["ACCOUNT_KEY"]
    async with CosmosClient(url, key) as client:
        # [END create_client]

        # Create a database in the account using the CosmosClient,
        # specifying that the operation shouldn't throw an exception
        # if a database with the given ID already exists.
        # [START create_database]
        database_name = "testDatabase"
        try:
            database = await client.create_database(id=database_name)
        except exceptions.CosmosResourceExistsError:
            database = client.get_database_client(database=database_name)
        # [END create_database]

        # Create a container, handling the exception if a container with the
        # same ID (name) already exists in the database.
        # [START create_container]
        container_name = "products"
        try:
            container = await database.create_container(
                id=container_name, partition_key=PartitionKey(path="/productName")
            )
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(container_name)
        # [END create_container]

        # Create a container with custom settings. This example
        # creates a container with a custom partition key.
        # [START create_container_with_settings]
        customer_container_name = "customers"
        try:
            customer_container = await database.create_container(
                id=customer_container_name,
                partition_key=PartitionKey(path="/city"),
                default_ttl=200,
            )
        except exceptions.CosmosResourceExistsError:
            customer_container = database.get_container_client(customer_container_name)
        # [END create_container_with_settings]

        # Retrieve a container by walking down the resource hierarchy
        # (client->database->container), handling the exception generated
        # if no container with the specified ID was found in the database.
        # [START get_container]
        database = client.get_database_client(database_name)
        container_client = database.get_container_client(container_name)
        # [END get_container]

        # [START list_containers]
        database = client.get_database_client(database_name)
        async for container_c in database.list_containers():
            print("Container ID: {}".format(container_c['id']))
        # [END list_containers]

        # Insert new items by defining a dict and calling Container.upsert_item
        # [START upsert_items]
        container = database.get_container_client(container_name)
        for i in range(1, 10):
            await container.upsert_item(
                dict(id="item{}".format(i), productName="Widget", productModel="Model {}".format(i))
            )
        # [END upsert_items]

        # Modify an existing item in the container
        # [START update_item]
        item = await container.read_item("item2", partition_key="Widget")
        item["productModel"] = "DISCONTINUED"
        updated_item = await container.upsert_item(item)
        # [END update_item]

        # Query the items in a container using SQL-like syntax. This example
        # gets all items whose product model hasn't been discontinued.
        # The asynchronous client returns asynchronous iterators for its query methods;
        # as such, we iterate over it by using an async for loop
        # [START query_items]
        import json

        async for queried_item in container.query_items(
                query='SELECT * FROM products p WHERE p.productModel <> "DISCONTINUED"'
        ):
            print(json.dumps(queried_item, indent=True))
        # [END query_items]

        # Parameterized queries are also supported. This example
        # gets all items whose product model has been discontinued.
        # [START query_items_param]
        discontinued_items = container.query_items(
            query='SELECT * FROM products p WHERE p.productModel = @model AND p.productName="Widget"',
            parameters=[dict(name="@model", value="DISCONTINUED")],
        )
        async for discontinued_item in discontinued_items:
            print(json.dumps(discontinued_item, indent=True))
        # [END query_items_param]

        # [START priority_level option]
        # Priority-based execution is a capability which allows users to specify priority
        # for the request sent to Azure Cosmos DB. Based on the priority specified by the user,
        # if there are more requests than the configured RU/s in a second,
        # then Azure Cosmos DB will throttle low priority requests to allow high priority requests to execute.
        # Can be used for Read, Write, and Query operations. This is specified with the `priority` keyword.
        # the value can either be low or high.
        async for queried_item in container.query_items(
                query='SELECT * FROM products p WHERE p.productModel <> "DISCONTINUED"', priority="High"
        ):
            print(json.dumps(queried_item, indent=True))
        # [END priority_level option]

        # Delete items from the container.
        # The Cosmos DB SQL API does not support 'DELETE' queries,
        # so deletes must be done with the delete_item method
        # on the container.
        # [START delete_items]
        async for queried_item in container.query_items(
                query='SELECT * FROM products p WHERE p.productModel = "DISCONTINUED" AND p.productName="Widget"'
        ):
            await container.delete_item(queried_item, partition_key="Widget")
        # [END delete_items]

        # Retrieve the properties of a database
        # [START get_database_properties]
        properties = await database.read()
        print(json.dumps(properties, indent=True))
        # [END get_database_properties]

        # Retrieve the properties of a container
        # [START get_container_properties]
        # Get properties will return a cache of two container properties: RID and the Partition Key Definition (This will not consume RUs)
        properties = await container._get_properties()

        # Print _rid and partitionKey
        print("Resource ID: ", properties.get('_rid'))
        print("Partition Key: ", properties.get('partitionKey'))

        # Read the container to get the latests of all the Container Properties. (This will make a backend requests and will consume RUs)
        container_properties = await container.read()

        # Print each property one by one if they are currently in the container properties
        print("indexingPolicy: ", container_properties.get("indexingPolicy"))
        print("etag: ", container_properties.get('_etag'))
        print("lastModified: ", container_properties.get('lastModified'))
        print("defaultTtl: ", container_properties.get('defaultTtl'))
        print("uniqueKeyPolicy: ", container_properties.get('uniqueKeyPolicy'))
        print("conflictResolutionPolicy: ", container_properties.get('conflictResolutionPolicy'))
        print("changeFeedPolicy: ", container_properties.get('changeFeedPolicy'))
        print("geospatialConfig: ", container_properties.get('geospatialConfig'))

        # Print remaining properties if they are in the current container properties
        for key, value in container_properties.items():
            if key not in ['_rid', 'partitionKey', 'indexingPolicy', '_etag', 'lastModified', 'defaultTtl', 'uniqueKeyPolicy',
                           'conflictResolutionPolicy', 'changeFeedPolicy', 'geospatialConfig']:
                print(f"{key}: {value}")
        # [END get_container_properties]

        # Modify the properties of an existing container
        # This example sets the default time to live (TTL) for items in the
        # container to 3600 seconds (1 hour). An item in container is deleted
        # when the TTL has elapsed since it was last edited.
        # [START reset_container_properties]
        # Set the TTL on the container to 3600 seconds (one hour)
        await database.replace_container(container, partition_key=PartitionKey(path='/productName'), default_ttl=3600)

        # Display the new TTL setting for the container
        container_props = await database.get_container_client(container_name).read()
        print("New container TTL: {}".format(json.dumps(container_props['defaultTtl'])))
        # [END reset_container_properties]

        # Create a user in the database.
        # [START create_user]
        try:
            await database.create_user(dict(id="Walter Harp"))
            print("Created user Walter Harp.")
        except exceptions.CosmosResourceExistsError:
            print("A user with that ID already exists.")
        except exceptions.CosmosHttpResponseError as failure:
            print("Failed to create user. Status code:{}".format(failure.status_code))
        # [END create_user]

        # delete all items in a given partition key
        # [START delete_all_items_by_partition_key]
        container_name = "products"
        container = database.get_container_client(container_name)
        for i in range(1, 10):
            await container.upsert_item(
                dict(id="item{}".format(i), productName="Gadget", productModel="Model {}".format(i))
            )
        items = container.read_all_items()
        async for item_dict in items:
            print(json.dumps(item_dict, indent=True))
        await container.delete_all_items_by_partition_key("Gadget")
        print("All items in partition {} deleted.".format("Gadget"))
        items = container.read_all_items()
        async for item_dict in items:
            print(json.dumps(item_dict, indent=True))
        # [END delete_all_items_by_partition_key]

        # insert items in a subpartitioned container
        # [START create_container]
        location_container_name = "locations"
        try:
            container = await database.create_container(
                id=location_container_name,
                partition_key=PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash")
            )
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(location_container_name)
        # [END create_container]
        # [START upsert_items]
        for i in range(1, 10):
            await container.upsert_item(
                dict(id="item{}".format(i), state="WA", city="Redmond", zipcode=98052)
            )
        # [END upsert_items]

        # Modify an existing item in the container
        # [START update_item]
        item = await container.read_item("item2", partition_key=["WA", "Redmond", 98052])
        item["state"] = "GA"
        item["city"] = "Atlanta"
        item["zipcode"] = 30363
        updated_item = await container.upsert_item(item)
        # [END update_item]

        # Query the items in a container using SQL-like syntax. This example
        # gets all items whose product model hasn't been discontinued.
        # [START query_items]
        import json

        async for queried_item in container.query_items(
                query='SELECT * FROM location l WHERE l.state = "WA"'
        ):
            print(json.dumps(queried_item, indent=True))
        # [END query_items]

         # [START delete_items]
        async for item_dict in container.query_items(
                query='SELECT * FROM location p WHERE p.state = "GA"'
        ):
            await container.delete_item(item_dict, partition_key=["GA", "Atlanta", 30363])
        # [END delete_items]

        # Get the feed ranges list from container.
        # [START read_feed_ranges]
        feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        # [END read_feed_ranges]

        # Get a feed range from a partition key.
        # [START feed_range_from_partition_key ]
        feed_range_from_pk = await container.feed_range_from_partition_key(["GA", "Atlanta", 30363])
        # [END feed_range_from_partition_key]

        # Figure out if a feed range is a subset of another feed range.
        # This example sees in which feed range from the container a feed range from a partition key is part of.
        # [START is_feed_range_subset]
        parent_feed_range = {}
        for feed_range in feed_ranges:
            if await container.is_feed_range_subset(feed_range, feed_range_from_pk):
                parent_feed_range = feed_range
                break
        # [END is_feed_range_subset]


        # Query a sorted list of items that were changed for one feed range.
        # The asynchronous client returns asynchronous iterators for its query methods;
        # as such, we iterate over it by using an async for loop
        # [START query_items_change_feed]
        async for queried_item in container.query_items_change_feed(feed_range=feed_ranges[0]):
            print(json.dumps(queried_item, indent=True))
        # [END query_items_change_feed]

        # Query a sorted list of items that were changed for one feed range from beginning.
        # The asynchronous client returns asynchronous iterators for its query methods;
        # as such, we iterate over it by using an async for loop
        # [START query_items_change_feed_from_beginning]
        async for queried_item in container.query_items_change_feed(feed_range=feed_ranges[0], start_time="Beginning"):
            print(json.dumps(queried_item, indent=True))
        # [END query_items_change_feed_from_beginning]

        await client.delete_database(database_name)
        print("Sample done running!")

if __name__ == "__main__":
    asyncio.run(examples_async())
