# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

"""
Sample: Fabric Mirror Serving Query

Demonstrates how to route Cosmos DB queries to a Fabric warehouse mirror
using the optional azure-cosmos-fabric-mapper package.

PREREQUISITES:
    1. A CosmosDB Fabric native account with Fabric mirroring enabled.
       Fabric mirroring is only supported with CosmosDB Fabric native accounts.
    2. Install the mapper package:
       pip install azure-cosmos-fabric-mapper[sql]
    3. Set environment variables (or update config.py):
       - ACCOUNT_HOST: Your Cosmos DB endpoint
       - ACCOUNT_KEY or use AAD authentication
       - FABRIC_SERVER: Your Fabric SQL endpoint
       - FABRIC_DATABASE: Your Fabric warehouse database name

USAGE:
    python mirror_serving_query.py
"""

import os
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions

import config

HOST = config.settings["host"]
MASTER_KEY = config.settings["master_key"]
DATABASE_ID = config.settings["database_id"]
CONTAINER_ID = config.settings["container_id"]

# Fabric mirror configuration
FABRIC_SERVER = os.environ.get("FABRIC_SERVER", "[YOUR FABRIC SQL ENDPOINT]")
FABRIC_DATABASE = os.environ.get("FABRIC_DATABASE", "[YOUR FABRIC DATABASE]")


def mirror_query_example():
    """Route a query to Fabric mirror for analytical workloads."""

    # Create client with mirror_config
    # Note: Fabric mirroring is only supported with CosmosDB Fabric native accounts.
    client = cosmos_client.CosmosClient(
        HOST,
        MASTER_KEY,
        mirror_config={
            "server": FABRIC_SERVER,
            "database": FABRIC_DATABASE,
        },
    )

    database = client.get_database_client(DATABASE_ID)
    container = database.get_container_client(CONTAINER_ID)

    # Use use_mirror_serving=True to route this query through Fabric
    # This is useful for analytical queries like GROUP BY, complex aggregations,
    # and ORDER BY that benefit from Fabric's SQL engine.
    print("Querying via Fabric mirror...")
    try:
        items = container.query_items(
            query="SELECT c.category, COUNT(1) as count FROM c GROUP BY c.category",
            use_mirror_serving=True,
        )
        for item in items:
            print(item)
    except exceptions.MirrorServingNotAvailableError:
        print(
            "azure-cosmos-fabric-mapper package is not installed. "
            "Install with: pip install azure-cosmos-fabric-mapper[sql]"
        )

    # Regular Cosmos DB query (no mirror) — works as usual
    print("\nQuerying Cosmos DB directly...")
    items = container.query_items(
        query="SELECT TOP 5 * FROM c",
        enable_cross_partition_query=True,
    )
    for item in items:
        print(item)


if __name__ == "__main__":
    mirror_query_example()
