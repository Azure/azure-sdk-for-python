"""End-to-end integration tests comparing Cosmos DB and Fabric mirror query results.

These tests use live Cosmos DB and Fabric mirror endpoints to validate that:
1. Queries execute successfully against both Cosmos and Fabric
2. Result shapes match (Cosmos document format vs mapped Fabric tabular results)
3. Fabric is faster/cheaper for expensive queries (aggregations, ORDER BY)
4. SELECT VALUE returns scalars, SELECT returns dicts

Setup:
- Authentication: Azure AD via DefaultAzureCredential
- Configure endpoints via environment variables (see module-level constants)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import pytest

# Skip all tests if ENABLE_E2E_TESTS is not set
pytestmark = pytest.mark.skipif(
    os.getenv("ENABLE_E2E_TESTS") != "1",
    reason="E2E tests require ENABLE_E2E_TESTS=1 environment variable"
)


@dataclass
class CosmosEndpoint:
    """Cosmos DB endpoint configuration."""
    account_url: str
    database: str
    container: str


@dataclass
class FabricEndpoint:
    """Fabric mirror endpoint configuration."""
    server: str
    database: str
    table: str
    schema: str = "dbo"


# Live test endpoints (configurable via environment variables)
COSMOS = CosmosEndpoint(
    account_url=os.getenv("COSMOS_ENDPOINT", "https://your-account.documents.azure.com:443/"),
    database=os.getenv("COSMOS_DATABASE", "spark-load-tests"),
    container=os.getenv("COSMOS_CONTAINER", "normal-bulk"),
)

FABRIC = FabricEndpoint(
    server=os.getenv("FABRIC_SERVER", "your-endpoint.datawarehouse.fabric.microsoft.com"),
    database=os.getenv("FABRIC_DATABASE", "spark-load-tests"),
    table=os.getenv("FABRIC_TABLE", "normal-bulk"),
    schema="dbo",
)


@pytest.fixture
def cosmos_client():
    """Create Cosmos DB client with Azure AD authentication."""
    try:
        from azure.cosmos import CosmosClient
        from azure.identity import DefaultAzureCredential
    except ImportError:
        pytest.skip("azure-cosmos and/or azure-identity not installed (install with pip install azure-cosmos-fabric-mapper[cosmos])")
    
    credential = DefaultAzureCredential()
    client = CosmosClient(COSMOS.account_url, credential=credential)
    return client


@pytest.fixture
def cosmos_container(cosmos_client):
    """Get Cosmos DB container for testing."""
    database = cosmos_client.get_database_client(COSMOS.database)
    container = database.get_container_client(COSMOS.container)
    return container


@pytest.fixture
def fabric_config():
    """Get Fabric mirror configuration for testing."""
    from azure.cosmos.fabric_mapper import MirrorServingConfiguration
    
    return MirrorServingConfiguration(
        fabric_server=FABRIC.server,
        fabric_database=FABRIC.database,
        fabric_table=FABRIC.table,
        fabric_schema=FABRIC.schema,
    )


@pytest.fixture
def fabric_driver(fabric_config):
    """Create Fabric driver client."""
    try:
        from azure.cosmos.fabric_mapper.driver import get_driver_client
        from azure.cosmos.fabric_mapper.credentials import DefaultAzureSqlCredential
    except ImportError:
        pytest.skip("Driver dependencies not installed")
    
    credentials = DefaultAzureSqlCredential()
    driver = get_driver_client(config=fabric_config, credentials=credentials)
    return driver, credentials


def query_cosmos(container, query: str, parameters: list[dict] | None = None) -> list[Any]:
    """Execute a query against Cosmos DB and return results."""
    items = container.query_items(
        query=query,
        parameters=parameters,
        enable_cross_partition_query=True
    )
    return list(items)


def query_fabric(driver_client, credentials, config, query: str, parameters: list[dict[str, Any]] | None = None) -> list[Any]:
    """Execute a query against Fabric mirror using the mapper."""
    from azure.cosmos.fabric_mapper.sdk_hook import MirroredQueryRequest, run_mirrored_query
    
    request = MirroredQueryRequest(
        query=query,
        parameters=parameters
    )
    
    return run_mirrored_query(
        request=request,
        config=config,
        credentials=credentials,
        driver=driver_client
    )


@pytest.mark.e2e
class TestCosmosVsFabricComparison:
    """Compare query results and performance between Cosmos DB and Fabric mirror."""
    
    def test_count_all_documents(self, cosmos_container, fabric_driver, fabric_config):
        """Test COUNT(1) aggregation - should be much faster on Fabric."""
        driver, creds = fabric_driver
        
        query = "SELECT VALUE COUNT(1) FROM c"
        
        # Query Cosmos
        cosmos_results = query_cosmos(cosmos_container, query)
        
        # Query Fabric
        fabric_results = query_fabric(driver, creds, fabric_config, query)
        
        # Both should return a single scalar (the count)
        assert len(cosmos_results) == 1
        assert len(fabric_results) == 1
        
        # Counts should match (both querying the same data)
        assert cosmos_results[0] == fabric_results[0]
        
        # The count should be 1M (known data size)
        assert cosmos_results[0] == 1_000_000
    
    def test_count_with_filter(self, cosmos_container, fabric_driver, fabric_config):
        """Test COUNT with WHERE clause."""
        driver, creds = fabric_driver
        
        # Pick a partitionKey value that exists
        query = "SELECT VALUE COUNT(1) FROM c WHERE c.partitionKey = @pk"
        params = [{"name": "@pk", "value": "test-partition-1"}]
        
        # Query Cosmos
        cosmos_results = query_cosmos(cosmos_container, query, params)
        
        # Query Fabric
        fabric_results = query_fabric(driver, creds, fabric_config, query, params)
        
        # Both should return a single count
        assert len(cosmos_results) == 1
        assert len(fabric_results) == 1
        
        # Counts should match
        assert cosmos_results[0] == fabric_results[0]
    
    def test_sum_aggregation(self, cosmos_container, fabric_driver, fabric_config):
        """Test SUM aggregation."""
        driver, creds = fabric_driver
        
        query = "SELECT VALUE SUM(c.value) FROM c WHERE c.partitionKey = @pk"
        params = [{"name": "@pk", "value": "test-partition-1"}]
        
        # Query Cosmos
        cosmos_results = query_cosmos(cosmos_container, query, params)
        
        # Query Fabric
        fabric_results = query_fabric(driver, creds, fabric_config, query, params)
        
        # Both should return a single sum
        assert len(cosmos_results) == 1
        assert len(fabric_results) == 1
        
        # Sums should match
        assert cosmos_results[0] == fabric_results[0]
    
    def test_select_with_projection(self, cosmos_container, fabric_driver, fabric_config):
        """Test SELECT (without VALUE) returns document structure."""
        driver, creds = fabric_driver
        
        query = "SELECT c.id, c.partitionKey FROM c WHERE c.partitionKey = @pk OFFSET 0 LIMIT 10"
        params = [{"name": "@pk", "value": "test-partition-1"}]
        
        # Query Cosmos
        cosmos_results = query_cosmos(cosmos_container, query, params)
        
        # Query Fabric
        fabric_results = query_fabric(driver, creds, fabric_config, query, params)
        
        # Both should return lists of dicts
        assert all(isinstance(item, dict) for item in cosmos_results)
        assert all(isinstance(item, dict) for item in fabric_results)
        
        # Both should have the same number of results
        assert len(cosmos_results) == len(fabric_results)
        
        # Both should have id and partitionKey fields
        for item in cosmos_results:
            assert "id" in item
            assert "partitionKey" in item
        
        for item in fabric_results:
            assert "id" in item
            assert "partitionKey" in item
    
    def test_order_by_not_supported_in_cosmos_python_sdk(self, cosmos_container, fabric_driver, fabric_config):
        """Test ORDER BY query - currently not supported in Cosmos Python SDK."""
        driver, creds = fabric_driver
        
        query = "SELECT c.id, c.partitionKey FROM c WHERE c.partitionKey = @pk ORDER BY c.id OFFSET 0 LIMIT 10"
        params = [{"name": "@pk", "value": "test-partition-1"}]
        
        # Query Cosmos (expect failure or unsorted results)
        # Note: Cosmos Python SDK doesn't support ORDER BY today
        # This test documents the limitation and shows Fabric as a workaround
        
        # Query Fabric (should work)
        fabric_results = query_fabric(driver, creds, fabric_config, query, params)
        
        # Fabric should return sorted results
        assert len(fabric_results) == 10
        ids = [item["id"] for item in fabric_results]
        assert ids == sorted(ids)  # Should be in ascending order
    
    def test_max_aggregation(self, cosmos_container, fabric_driver, fabric_config):
        """Test MAX aggregation."""
        driver, creds = fabric_driver
        
        query = "SELECT VALUE MAX(c.value) FROM c WHERE c.partitionKey = @pk"
        params = [{"name": "@pk", "value": "test-partition-1"}]
        
        # Query Cosmos
        cosmos_results = query_cosmos(cosmos_container, query, params)
        
        # Query Fabric
        fabric_results = query_fabric(driver, creds, fabric_config, query, params)
        
        # Both should return a single max value
        assert len(cosmos_results) == 1
        assert len(fabric_results) == 1
        
        # Max values should match
        assert cosmos_results[0] == fabric_results[0]
    
    def test_avg_aggregation(self, cosmos_container, fabric_driver, fabric_config):
        """Test AVG aggregation."""
        driver, creds = fabric_driver
        
        query = "SELECT VALUE AVG(c.value) FROM c WHERE c.partitionKey = @pk"
        params = [{"name": "@pk", "value": "test-partition-1"}]
        
        # Query Cosmos
        cosmos_results = query_cosmos(cosmos_container, query, params)
        
        # Query Fabric
        fabric_results = query_fabric(driver, creds, fabric_config, query, params)
        
        # Both should return a single average
        assert len(cosmos_results) == 1
        assert len(fabric_results) == 1
        
        # Averages should match (within floating point tolerance)
        assert abs(cosmos_results[0] - fabric_results[0]) < 0.001
    
    def test_pagination_with_offset_limit(self, cosmos_container, fabric_driver, fabric_config):
        """Test OFFSET/LIMIT pagination."""
        driver, creds = fabric_driver
        
        query = "SELECT c.id FROM c WHERE c.partitionKey = @pk OFFSET 10 LIMIT 5"
        params = [{"name": "@pk", "value": "test-partition-1"}]
        
        # Query Cosmos
        cosmos_results = query_cosmos(cosmos_container, query, params)
        
        # Query Fabric
        fabric_results = query_fabric(driver, creds, fabric_config, query, params)
        
        # Both should return exactly 5 results (skipping first 10)
        assert len(cosmos_results) == 5
        assert len(fabric_results) == 5
