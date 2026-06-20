# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey
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
# Sample - demonstrates how to configure custom user agents for Azure Cosmos DB clients
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


def create_client_with_default_user_agent():
    """
    Create a Cosmos DB client with the default user agent.
    
    The default user agent includes information about the SDK version and Python version.
    Example: "azsdk-python-cosmos/4.5.0 Python/3.11.0 (Windows-10-10.0.22621-SP0)"
    """
    print('\n1. Creating client with default user agent')
    
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
    
    print('Client created with default user agent')
    print('The default user agent includes SDK version, Python version, and platform information')
    
    return client


def create_client_with_custom_user_agent():
    """
    Create a Cosmos DB client with a custom user agent suffix.
    
    The user_agent parameter appends a custom string to the default user agent,
    allowing you to identify your specific application or service.
    """
    print('\n2. Creating client with custom user agent')
    
    # Add a custom suffix to identify your application
    custom_user_agent = "MyApplication/1.0.0"
    
    client = cosmos_client.CosmosClient(
        HOST,
        {'masterKey': MASTER_KEY},
        user_agent_suffix=custom_user_agent
    )
    
    print(f'Client created with custom user agent: {custom_user_agent}')
    print('This will appear as: [default-user-agent] {}'.format(custom_user_agent))
    
    return client


def create_client_with_detailed_user_agent():
    """
    Create a client with a detailed custom user agent including multiple identifiers.
    
    You can include multiple pieces of information to make diagnostics more useful:
    - Application name and version
    - Service or microservice name
    - Environment (dev, staging, production)
    - Instance or process identifier
    """
    print('\n3. Creating client with detailed custom user agent')
    
    # Include detailed information about your application
    app_name = "OrderProcessingService"
    app_version = "2.3.1"
    environment = "production"
    instance_id = "instance-42"
    
    detailed_user_agent = f"{app_name}/{app_version} env:{environment} {instance_id}"
    
    client = cosmos_client.CosmosClient(
        HOST,
        {'masterKey': MASTER_KEY},
        user_agent_suffix=detailed_user_agent
    )
    
    print(f'Client created with detailed user agent: {detailed_user_agent}')
    print('This helps identify specific instances in diagnostics and logs')
    
    return client


def create_multiple_clients_with_different_user_agents():
    """
    Demonstrate creating multiple clients with different user agents.
    
    This is useful when you have multiple services or components in your application
    that need to be tracked separately in diagnostics.
    """
    print('\n4. Creating multiple clients with different user agents')
    
    # Client for data ingestion service
    ingestion_client = cosmos_client.CosmosClient(
        HOST,
        {'masterKey': MASTER_KEY},
        user_agent_suffix="DataIngestionService/1.0.0"
    )
    print('Created client for data ingestion: DataIngestionService/1.0.0')
    
    # Client for query service
    query_client = cosmos_client.CosmosClient(
        HOST,
        {'masterKey': MASTER_KEY},
        user_agent_suffix="QueryService/1.0.0"
    )
    print('Created client for queries: QueryService/1.0.0')
    
    # Client for analytics service
    analytics_client = cosmos_client.CosmosClient(
        HOST,
        {'masterKey': MASTER_KEY},
        user_agent_suffix="AnalyticsService/1.0.0"
    )
    print('Created client for analytics: AnalyticsService/1.0.0')
    
    print('\nNow you can distinguish requests from different services in diagnostics')
    
    return ingestion_client, query_client, analytics_client


def demonstrate_user_agent_in_operations(client, custom_suffix="DemoClient/1.0.0"):
    """
    Perform operations with a custom user agent and show how it helps with diagnostics.
    
    The user agent will appear in:
    - Azure Monitor logs
    - Cosmos DB diagnostic logs
    - Request headers sent to the service
    - Performance and usage analytics
    """
    print('\n5. Demonstrating user agent in operations')
    
    try:
        # Create database
        db = client.create_database_if_not_exists(id=DATABASE_ID)
        print(f'Database created/accessed with user agent: {custom_suffix}')
        
        # Create container
        container = db.create_container_if_not_exists(
            id=CONTAINER_ID,
            partition_key=PartitionKey(path='/id')
        )
        print(f'Container created/accessed with user agent: {custom_suffix}')
        
        # Create or upsert an item
        item = {
            'id': 'sample_item_1',
            'name': 'Sample Item',
            'description': 'Created with custom user agent'
        }
        container.upsert_item(body=item)
        print(f'Item created/updated with user agent: {custom_suffix}')
        
        # Query items
        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.id = @id",
            parameters=[{"name": "@id", "value": "sample_item_1"}],
            enable_cross_partition_query=True
        ))
        print(f'Query executed with user agent: {custom_suffix}')
        print(f'Found {len(items)} item(s)')
        
        print('\nAll these operations will show your custom user agent in diagnostics')
        
        # Cleanup: Delete the item
        container.delete_item(item='sample_item_1', partition_key='sample_item_1')
        print(f'\nCleanup: Deleted sample item')
        
    except Exception as e:
        print(f'Error during operations: {e}')

def demonstrate_operations_with_multiple_user_agents():
    """
    Show how different user agents help track multiple operations.
    """
    print('\n6. Demonstrating Multiple operations with different user agents')

    def operation_with_user_agent(user_agent_suffix, operation_name):
        """Helper function to perform operation with specific user agent."""
        client = cosmos_client.CosmosClient(
                HOST,
                {'masterKey': MASTER_KEY},
            user_agent_suffix=user_agent_suffix
        )
        db = client.create_database_if_not_exists(id=DATABASE_ID)
        print(f'{operation_name} completed with user agent: {user_agent_suffix}')

    # Run multiple operations with different user agents
    operation_with_user_agent("Worker1/1.0.0", "Worker 1")
    operation_with_user_agent("Worker2/1.0.0", "Worker 2")
    operation_with_user_agent("Worker3/1.0.0", "Worker 3")

    print('\nEach operation can be tracked separately in diagnostics')

def run_sample():
    """
    Run all user agent examples.
    """
    print('=' * 70)
    print('Azure Cosmos DB - User Agent Management Sample')
    print('=' * 70)
    
    # Example 1: Default user agent
    default_client = create_client_with_default_user_agent()
    
    # Example 2: Simple custom user agent
    custom_client = create_client_with_custom_user_agent()
    
    # Example 3: Detailed user agent
    detailed_client = create_client_with_detailed_user_agent()
    
    # Example 4: Multiple clients with different user agents
    ingestion_client, query_client, analytics_client = create_multiple_clients_with_different_user_agents()
    
    # Example 5: Show user agent in operations
    demonstrate_user_agent_in_operations(detailed_client, "OrderProcessingService/2.3.1")

    # Example 6: Operations with different user agents
    demonstrate_operations_with_multiple_user_agents()

    print('\n' + '=' * 70)
    print('Sample completed!')
    print('=' * 70)

if __name__ == '__main__':
    run_sample()
