# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: autoscale_throughput_management.py

DESCRIPTION:
    This sample demonstrates how to manage autoscale throughput settings for
    Azure Cosmos DB databases and containers. Autoscale allows you to automatically
    scale throughput based on usage, providing cost optimization and performance flexibility.

    Key concepts covered:
    - Creating databases and containers with autoscale throughput
    - Reading autoscale throughput settings
    - Updating autoscale maximum throughput
    - Understanding autoscale increment percentage

USAGE:
    python autoscale_throughput_management.py

    Set the environment variables with your own values before running:
    1) ACCOUNT_HOST - the Cosmos DB account endpoint
    2) ACCOUNT_KEY - the Cosmos DB account primary key
"""

import azure.cosmos.cosmos_client as cosmos_client
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
# Sample - demonstrates autoscale throughput management for databases and containers
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


def create_database_with_autoscale(client, database_id):
    """
    Create a database with autoscale throughput.
    Setting throughput settings, like autoscale, on a database level is *not* recommended,
    and should only be done if you are aware of the implications of shared throughput across containers.
    
    Autoscale throughput automatically scales between 10% and 100% of the maximum throughput
    based on your workload demands.
    
    Args:
        client: CosmosClient instance
        database_id: ID for the database
    """
    print("\nCreate Database with Autoscale Throughput")
    print("=" * 70)
    
    try:
        # Create database with autoscale - max throughput of 4000 RU/s
        # The database will scale between 400 RU/s (10%) and 4000 RU/s (100%)
        database = client.create_database(
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


def create_container_with_autoscale(database, container_id):
    """
    Create a container with autoscale throughput.
    
    Container-level autoscale provides dedicated throughput for a specific container,
    independent of the database throughput.
    
    Args:
        database: DatabaseProxy instance
        container_id: ID for the container
    """
    print("\nCreate Container with Autoscale Throughput")
    print("=" * 70)
    
    try:
        # Create container with autoscale - max throughput of 5000 RU/s
        # auto_scale_increment_percent=0 means default scaling behavior
        container = database.create_container(
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


def read_autoscale_throughput(database, container):
    """
    Read and display autoscale throughput settings for database and container.
    
    The throughput properties reveal:
    - Whether autoscale is enabled
    - Maximum throughput setting
    - Current throughput (if available)
    
    Args:
        database: DatabaseProxy instance
        container: ContainerProxy instance
    """
    print("\nRead Autoscale Throughput Settings")
    print("=" * 70)
    
    try:
        # Read database throughput
        db_offer = database.get_throughput()
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
        container_offer = container.get_throughput()
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


def update_autoscale_max_throughput(container, new_max_throughput):
    """
    Update the maximum throughput for an autoscale-enabled container.
    
    This changes the upper limit of the autoscale range. The minimum throughput
    will automatically adjust to 10% of the new maximum.
    
    Args:
        container: ContainerProxy instance
        new_max_throughput: New maximum throughput in RU/s
    """
    print("\nUpdate Autoscale Maximum Throughput")
    print("=" * 70)
    
    try:
        # Update autoscale max throughput
        new_throughput = ThroughputProperties(
            auto_scale_max_throughput=new_max_throughput,
            auto_scale_increment_percent=0
        )
        
        updated_offer = container.replace_throughput(new_throughput)
        
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

def run_sample():
    """
    Run the autoscale throughput management sample.
    """
    print('=' * 70)
    print('Azure Cosmos DB - Autoscale Throughput Management Sample')
    print('=' * 70)
    
    # Initialize client
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
    
    try:
        # 1. Create database with autoscale
        database = create_database_with_autoscale(client, DATABASE_ID + '_autoscale')
        
        # 2. Create container with autoscale
        container = create_container_with_autoscale(database, CONTAINER_ID + '_autoscale')
        
        # 3. Read autoscale settings
        read_autoscale_throughput(database, container)
        
        # 4. Update autoscale max throughput
        update_autoscale_max_throughput(container, 6000)
        
        # 5. Read updated settings
        read_autoscale_throughput(database, container)
        
        # Cleanup
        print("\n" + "=" * 70)
        print("Cleaning up resources...")
        print("=" * 70)
        
        database.delete_container(container.id)
        print(f"Deleted container: {container.id}")
        
        client.delete_database(database.id)
        print(f"Deleted database: {database.id}")
        
    except exceptions.CosmosHttpResponseError as e:
        print(f"\nError: {e.message}")
    
    print('\n' + '=' * 70)
    print('Sample completed!')
    print('=' * 70)


if __name__ == '__main__':
    run_sample()
