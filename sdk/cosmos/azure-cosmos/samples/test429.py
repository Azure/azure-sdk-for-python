import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions, PartitionKey

async def create_and_query_items():
    endpoint = "https://localhost:8081"
    key = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    database_name = "your_database_name"
    container_name = "your_container_name"
    query = "SELECT * FROM c"
    query_params = [{"name": "@value", "value": "some_value"}]
    count = 0


    async def query_items(database, count):
        try:
            #having to connect to container each time guarantees we get 429
            try:
                container = await database.create_container(
                    id=container_name, partition_key=PartitionKey(path="/property"), offer_throughput=400
                )
            except exceptions.CosmosResourceExistsError:
                container = database.get_container_client(container_name)

            query_iterable = [d async for d in container.query_items(query, max_item_count=100)]
            count = count + 1
            if len(query_iterable) == 0:
                print("Oops", count)
            else:
                print("NOt oops",len(query_iterable))

        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 429:
                print("Received a 429 status code (Too Many Requests).")
                print("429 oops container")

            else:
                print(f"Error: {e.status_code} - {e.message}")

    async with CosmosClient(endpoint, key) as client:
        # client.connection_policy.retry_options.fixed_retry_interval_in_milliseconds = 2000
        try:
            database = await client.create_database(id=database_name)
        except exceptions.CosmosResourceExistsError:
            database = client.get_database_client(database=database_name)
        try:
            container = await database.create_container(
                id=container_name, partition_key=PartitionKey(path="/property"), offer_throughput=400
            )
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(container_name)
        for i in range(150):
            await container.upsert_item({
                'id': f'item{i}',
                'property': f'value{i}'
            })
        num_queries = 3400
        try:
            await asyncio.gather(*[query_items(database, count) for _ in range(num_queries)])
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 429:
                print("Received a 429 status code (Too Many Requests).")
            else:
                print(f"Error: {e.status_code} - {e.message}")
        print(count)

    # except exceptions.CosmosHttpResponseError as e:
    #     if e.status_code == 429:
    #         print("Received a 429 status code (Too Many Requests).")
    #     else:
    #         print(f"Error: {e.status_code} - {e.message}")
    async with CosmosClient(endpoint, key) as client:
            database = client.get_database_client(database_name)
            await client.delete_database(database)

if __name__ == "__main__":
    loop = asyncio.run(create_and_query_items())
