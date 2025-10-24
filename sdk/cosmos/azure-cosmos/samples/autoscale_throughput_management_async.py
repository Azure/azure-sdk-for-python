# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: autoscale_throughput_management_async.py

DESCRIPTION:
    This async sample demonstrates how to manage autoscale throughput settings for
    Azure Cosmos DB databases and containers. Autoscale allows you to automatically
    scale throughput based on usage, providing cost optimization and performance flexibility.

    Key concepts covered:
    - Creating databases and containers with autoscale throughput (async)
    - Reading autoscale throughput settings (async)
    - Updating autoscale maximum throughput (async)
    - Migrating between manual and autoscale throughput (async)
    - Understanding autoscale increment percentage
    - Best practices for autoscale in async applications

USAGE:
    python autoscale_throughput_management_async.py

    Set the environment variables with your own values before running:
    1) ACCOUNT_HOST - the Cosmos DB account endpoint
    2) ACCOUNT_KEY - the Cosmos DB account primary key
"""

import asyncio
from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos import ThroughputProperties

import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://docs.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates async autoscale throughput management for databases and containers
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


async def create_database_with_autoscale(client, database_id):
    """
    Create a database with autoscale throughput asynchronously.
    
    Autoscale throughput automatically scales between 10% and 100% of the maximum throughput
    based on your workload demands.
    
    Args:
        client: CosmosClient instance
        database_id: ID for the database
    """
    print("\nCreate Database with Autoscale Throughput (Async)")
    print("=" * 70)
    
    try:
        # Create database with autoscale - max throughput of 4000 RU/s
        # The database will scale between 400 RU/s (10%) and 4000 RU/s (100%)
        database = await client.create_database(
            id=database_id,
            offer_throughput=ThroughputProperties(
                auto_scale_max_throughput=4000,
                auto_scale_increment_percent=0
            )
        )
        
        print(f"Database '{database_id}' created with autoscale")
        print(f"  - Maximum throughput: 4000 RU/s")
        print(f"  - Minimum throughput: 400 RU/s (10% of max)")
        print(f"  - Auto-scales based on usage between min and max")
        
        return database
        
    except exceptions.CosmosResourceExistsError:
        print(f"Database '{database_id}' already exists")
        return client.get_database_client(database_id)


async def create_container_with_autoscale(database, container_id):
    """
    Create a container with autoscale throughput asynchronously.
    
    Container-level autoscale provides dedicated throughput for a specific container,
    independent of the database throughput.
    
    Args:
        database: DatabaseProxy instance
        container_id: ID for the container
    """
    print("\nCreate Container with Autoscale Throughput (Async)")
    print("=" * 70)
    
    try:
        # Create container with autoscale - max throughput of 5000 RU/s
        # auto_scale_increment_percent=0 means default scaling behavior
        container = await database.create_container(
            id=container_id,
            partition_key=PartitionKey(path='/id'),
            offer_throughput=ThroughputProperties(
                auto_scale_max_throughput=5000,
                auto_scale_increment_percent=0
            )
        )
        
        print(f"Container '{container_id}' created with autoscale")
        print(f"  - Maximum throughput: 5000 RU/s")
        print(f"  - Minimum throughput: 500 RU/s (10% of max)")
        print(f"  - Scales automatically based on workload")
        
        return container
        
    except exceptions.CosmosResourceExistsError:
        print(f"Container '{container_id}' already exists")
        return database.get_container_client(container_id)


async def read_autoscale_throughput(database, container):
    """
    Read and display autoscale throughput settings for database and container asynchronously.
    
    The throughput properties reveal:
    - Whether autoscale is enabled
    - Maximum throughput setting
    - Current throughput (if available)
    
    Args:
        database: DatabaseProxy instance
        container: ContainerProxy instance
    """
    print("\nRead Autoscale Throughput Settings (Async)")
    print("=" * 70)
    
    try:
        # Read database throughput
        db_offer = await database.get_throughput()
        print(f"\nDatabase '{database.id}' throughput:")
        
        autopilot_settings = db_offer.properties.get('content', {}).get('offerAutopilotSettings')
        if autopilot_settings:
            max_throughput = autopilot_settings.get('maxThroughput')
            print(f"  - Autoscale enabled: Yes")
            print(f"  - Maximum throughput: {max_throughput} RU/s")
            print(f"  - Minimum throughput: {max_throughput // 10} RU/s")
            print(f"  - Increment percent: {autopilot_settings.get('autoUpgradePolicy', {}).get('throughputPolicy', {}).get('incrementPercent', 0)}")
        else:
            throughput = db_offer.properties.get('content', {}).get('offerThroughput')
            print(f"  - Autoscale enabled: No")
            print(f"  - Manual throughput: {throughput} RU/s")
            
    except exceptions.CosmosHttpResponseError as e:
        print(f"Database throughput error: {e.message}")
    
    try:
        # Read container throughput
        container_offer = await container.get_throughput()
        print(f"\nContainer '{container.id}' throughput:")
        
        autopilot_settings = container_offer.properties.get('content', {}).get('offerAutopilotSettings')
        if autopilot_settings:
            max_throughput = autopilot_settings.get('maxThroughput')
            print(f"  - Autoscale enabled: Yes")
            print(f"  - Maximum throughput: {max_throughput} RU/s")
            print(f"  - Minimum throughput: {max_throughput // 10} RU/s")
        else:
            throughput = container_offer.properties.get('content', {}).get('offerThroughput')
            print(f"  - Autoscale enabled: No")
            print(f"  - Manual throughput: {throughput} RU/s")
            
    except exceptions.CosmosHttpResponseError as e:
        print(f"Container throughput error: {e.message}")


async def update_autoscale_max_throughput(container, new_max_throughput):
    """
    Update the maximum throughput for an autoscale-enabled container asynchronously.
    
    This changes the upper limit of the autoscale range. The minimum throughput
    will automatically adjust to 10% of the new maximum.
    
    Args:
        container: ContainerProxy instance
        new_max_throughput: New maximum throughput in RU/s
    """
    print("\nUpdate Autoscale Maximum Throughput (Async)")
    print("=" * 70)
    
    try:
        # Update autoscale max throughput
        new_throughput = ThroughputProperties(
            auto_scale_max_throughput=new_max_throughput,
            auto_scale_increment_percent=0
        )
        
        updated_offer = await container.replace_throughput(new_throughput)
        
        autopilot_settings = updated_offer.properties.get('content', {}).get('offerAutopilotSettings')
        if autopilot_settings:
            max_throughput = autopilot_settings.get('maxThroughput')
            print(f"Container '{container.id}' autoscale updated:")
            print(f"  - New maximum throughput: {max_throughput} RU/s")
            print(f"  - New minimum throughput: {max_throughput // 10} RU/s")
            print(f"  - Autoscale will now scale within this new range")
        else:
            print(f"Warning: Updated offer does not contain autoscale settings")
        
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error updating autoscale throughput: {e.message}")

async def demonstrate_concurrent_throughput_operations(database):
    """
    Demonstrate concurrent throughput operations on multiple containers.
    
    Shows how async operations can efficiently manage throughput settings
    for multiple containers simultaneously.
    
    Args:
        database: DatabaseProxy instance
    """
    print("\nDemonstrate Concurrent Throughput Operations (Async)")
    print("=" * 70)
    
    try:
        # Create multiple containers with different autoscale settings concurrently
        container_configs = [
            ('container_async_1', 4000),
            ('container_async_2', 5000),
            ('container_async_3', 6000)
        ]
        
        # Create containers concurrently
        create_tasks = [
            database.create_container(
                id=container_id,
                partition_key=PartitionKey(path='/id'),
                offer_throughput=ThroughputProperties(
                    auto_scale_max_throughput=max_throughput,
                    auto_scale_increment_percent=0
                )
            )
            for container_id, max_throughput in container_configs
        ]
        
        containers = await asyncio.gather(*create_tasks, return_exceptions=True)
        
        print(f"Created {len([c for c in containers if not isinstance(c, Exception)])} containers concurrently")
        
        # Read throughput settings concurrently
        valid_containers = [c for c in containers if not isinstance(c, Exception)]
        read_tasks = [container.get_throughput() for container in valid_containers]
        
        offers = await asyncio.gather(*read_tasks, return_exceptions=True)
        
        print("\nThroughput settings for all containers:")
        for container, offer in zip(valid_containers, offers):
            if not isinstance(offer, Exception):
                autopilot_settings = offer.properties.get('content', {}).get('offerAutopilotSettings')
                if autopilot_settings:
                    max_throughput = autopilot_settings.get('maxThroughput')
                    print(f"  - {container.id}: {max_throughput} RU/s (autoscale)")
        
        # Cleanup containers concurrently
        delete_tasks = [database.delete_container(container.id) for container in valid_containers]
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        
        print(f"\nCleaned up {len(valid_containers)} containers concurrently")
        
    except Exception as e:
        print(f"Error in concurrent operations: {str(e)}")


async def run_sample():
    """
    Run the async autoscale throughput management sample.
    """
    print('=' * 70)
    print('Azure Cosmos DB - Async Autoscale Throughput Management Sample')
    print('=' * 70)
    
    # Initialize async client
    async with CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
        try:
            # 1. Create database with autoscale
            database = await create_database_with_autoscale(client, DATABASE_ID + '_autoscale_async')
            
            # 2. Create container with autoscale
            container = await create_container_with_autoscale(database, CONTAINER_ID + '_autoscale_async')
            
            # 3. Read autoscale settings
            await read_autoscale_throughput(database, container)
            
            # 4. Update autoscale max throughput
            await update_autoscale_max_throughput(container, 6000)
            
            # 5. Read updated settings
            await read_autoscale_throughput(database, container)
            
            # 6. Demonstrate concurrent operations
            await demonstrate_concurrent_throughput_operations(database)
            
            # Cleanup
            print("\n" + "=" * 70)
            print("Cleaning up resources...")
            print("=" * 70)
            
            await database.delete_container(container.id)
            print(f"Deleted container: {container.id}")
            
            await client.delete_database(database.id)
            print(f"Deleted database: {database.id}")
            
        except exceptions.CosmosHttpResponseError as e:
            print(f"\nError: {e.message}")
    
    print('\n' + '=' * 70)
    print('Sample completed!')
    print('=' * 70)


if __name__ == '__main__':
    asyncio.run(run_sample())
