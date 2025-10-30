# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey
import asyncio
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://azure.microsoft.com/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to configure custom user agents for async Azure Cosmos DB clients
#
# User agents help identify which application or process is making requests to Cosmos DB.
# Custom user agents are particularly useful for:
#   - Identifying different applications using the same Cosmos DB account
#   - Distinguishing between different versions of your application
#   - Tracking requests from specific microservices or processes
#   - Debugging and monitoring application behavior in diagnostics
#   - Analyzing usage patterns across different client applications
#
# The user agent string appears in Cosmos DB diagnostics, logs, and monitoring tools,
# making it easier to pinpoint which client instance is making specific requests.
# ----------------------------------------------------------------------------------------------------------
# Note -
#
# Running this sample will create (and delete) multiple Containers on your account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


async def create_client_with_default_user_agent():
    """
    Create an async Cosmos DB client with the default user agent.
    
    The default user agent includes information about the SDK version and Python version.
    Example: "azsdk-python-cosmos/4.5.0 Python/3.11.0 (Windows-10-10.0.22621-SP0)"
    """
    print('\n1. Creating async client with default user agent')
    
    async with CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
        print('Async client created with default user agent')
        print('The default user agent includes SDK version, Python version, and platform information')
        return client


async def create_client_with_custom_user_agent():
    """
    Create an async Cosmos DB client with a custom user agent suffix.
    
    The user_agent parameter appends a custom string to the default user agent,
    allowing you to identify your specific application or service.
    """
    print('\n2. Creating async client with custom user agent')
    
    # Add a custom suffix to identify your application
    custom_user_agent = "MyAsyncApplication/1.0.0"
    
    async with CosmosClient(
        HOST,
        {'masterKey': MASTER_KEY},
        user_agent=custom_user_agent
    ) as client:
        print(f'Async client created with custom user agent: {custom_user_agent}')
        print('This will appear as: [default-user-agent] {}'.format(custom_user_agent))
        return client


async def create_client_with_detailed_user_agent():
    """
    Create an async client with a detailed custom user agent including multiple identifiers.
    
    You can include multiple pieces of information to make diagnostics more useful:
    - Application name and version
    - Service or microservice name
    - Environment (dev, staging, production)
    - Instance or process identifier
    """
    print('\n3. Creating async client with detailed custom user agent')
    
    # Include detailed information about your application
    app_name = "AsyncOrderProcessingService"
    app_version = "2.3.1"
    environment = "production"
    instance_id = "async-instance-42"
    
    detailed_user_agent = f"{app_name}/{app_version} env:{environment} {instance_id}"
    
    async with CosmosClient(
        HOST,
        {'masterKey': MASTER_KEY},
        user_agent=detailed_user_agent
    ) as client:
        print(f'Async client created with detailed user agent: {detailed_user_agent}')
        print('This helps identify specific instances in diagnostics and logs')
        return client


async def create_multiple_clients_with_different_user_agents():
    """
    Demonstrate creating multiple async clients with different user agents.
    
    This is useful when you have multiple services or components in your application
    that need to be tracked separately in diagnostics.
    """
    print('\n4. Creating multiple async clients with different user agents')
    
    # Note: In production, you would manage these clients' lifecycles appropriately
    # Here we demonstrate the creation pattern
    
    print('Creating async client for data ingestion: AsyncDataIngestionService/1.0.0')
    print('Creating async client for queries: AsyncQueryService/1.0.0')
    print('Creating async client for analytics: AsyncAnalyticsService/1.0.0')
    
    print('\nEach client can be created with its own user agent to track requests separately')


async def demonstrate_user_agent_in_operations():
    """
    Perform async operations with a custom user agent and show how it helps with diagnostics.
    
    The user agent will appear in:
    - Azure Monitor logs
    - Cosmos DB diagnostic logs
    - Request headers sent to the service
    - Performance and usage analytics
    """
    print('\n5. Demonstrating user agent in async operations')
    
    custom_suffix = "AsyncDemoClient/1.0.0"
    
    async with CosmosClient(
        HOST,
        {'masterKey': MASTER_KEY},
        user_agent=custom_suffix
    ) as client:
        try:
            # Create database
            db = await client.create_database_if_not_exists(id=DATABASE_ID)
            print(f'Database created/accessed with user agent: {custom_suffix}')
            
            # Create container
            container = await db.create_container_if_not_exists(
                id=CONTAINER_ID,
                partition_key=PartitionKey(path='/id')
            )
            print(f'Container created/accessed with user agent: {custom_suffix}')
            
            # Create or upsert an item
            item = {
                'id': 'async_sample_item_1',
                'name': 'Async Sample Item',
                'description': 'Created with custom user agent in async operation'
            }
            await container.upsert_item(body=item)
            print(f'Item created/updated with user agent: {custom_suffix}')
            
            # Query items
            query_iterable = container.query_items(
                query="SELECT * FROM c WHERE c.id = @id",
                parameters=[{"name": "@id", "value": "async_sample_item_1"}]
            )
            items = [item async for item in query_iterable]
            print(f'Query executed with user agent: {custom_suffix}')
            print(f'Found {len(items)} item(s)')
            
            print('\nAll these async operations will show your custom user agent in diagnostics')
            
            # Cleanup: Delete the item
            await container.delete_item(item='async_sample_item_1', partition_key='async_sample_item_1')
            print(f'\nCleanup: Deleted sample item')
            
        except Exception as e:
            print(f'Error during async operations: {e}')


async def demonstrate_concurrent_operations_with_user_agents():
    """
    Show how different user agents help track concurrent async operations.
    """
    print('\n6. Demonstrating concurrent operations with different user agents')
    
    async def operation_with_user_agent(user_agent_suffix, operation_name):
        """Helper function to perform operation with specific user agent."""
        async with CosmosClient(
            HOST,
            {'masterKey': MASTER_KEY},
            user_agent=user_agent_suffix
        ) as client:
            db = await client.create_database_if_not_exists(id=DATABASE_ID)
            print(f'{operation_name} completed with user agent: {user_agent_suffix}')
    
    # Run multiple operations concurrently with different user agents
    await asyncio.gather(
        operation_with_user_agent("AsyncWorker1/1.0.0", "Worker 1"),
        operation_with_user_agent("AsyncWorker2/1.0.0", "Worker 2"),
        operation_with_user_agent("AsyncWorker3/1.0.0", "Worker 3")
    )
    
    print('\nEach concurrent operation can be tracked separately in diagnostics')


async def run_sample():
    """
    Run all async user agent examples.
    """
    print('=' * 70)
    print('Azure Cosmos DB - Async User Agent Management Sample')
    print('=' * 70)
    
    # Example 1: Default user agent
    await create_client_with_default_user_agent()
    
    # Example 2: Simple custom user agent
    await create_client_with_custom_user_agent()
    
    # Example 3: Detailed user agent
    await create_client_with_detailed_user_agent()
    
    # Example 4: Multiple clients with different user agents
    await create_multiple_clients_with_different_user_agents()
    
    # Example 5: Show user agent in operations
    await demonstrate_user_agent_in_operations()
    
    # Example 6: Concurrent operations
    await demonstrate_concurrent_operations_with_user_agents()
    
    print('\n' + '=' * 70)
    print('Sample completed!')
    print('=' * 70)


if __name__ == '__main__':
    asyncio.run(run_sample())
