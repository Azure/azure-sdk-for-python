"""End-to-end tests comparing Cosmos DB and Fabric mirror query results.

These tests execute the same queries against both Cosmos DB and Fabric mirror,
validating that:
1. Results are equivalent (within expected tolerances)
2. Fabric mirror handles queries that perform poorly in Cosmos DB (aggregations)
3. ORDER BY works through Fabric mirror (not supported in Cosmos Python SDK)

Test data: 1,000,000 records in normal-bulk container/table, partitioned by partitionKey
"""

import os
from typing import Any

import pytest
from azure.identity import DefaultAzureCredential

from azure.cosmos.fabric_mapper import MirrorServingConfiguration
from azure.cosmos.fabric_mapper.credentials import DefaultAzureSqlCredential
from azure.cosmos.fabric_mapper.driver import get_driver_client
from azure.cosmos.fabric_mapper.translate import translate


# Test configuration from environment or defaults
COSMOS_ENDPOINT = os.getenv(
    "COSMOS_ENDPOINT",
    "https://your-account.documents.azure.com:443/"
)
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE", "spark-load-tests")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "normal-bulk")

FABRIC_SERVER = os.getenv(
    "FABRIC_SERVER",
    "your-endpoint.datawarehouse.fabric.microsoft.com"
)
FABRIC_DATABASE = os.getenv("FABRIC_DATABASE", "spark-load-tests")
FABRIC_TABLE = os.getenv("FABRIC_TABLE", "normal-bulk")
FABRIC_SCHEMA = os.getenv("FABRIC_SCHEMA", "spark-load-tests")  # Schema is the database name in Fabric mirror


@pytest.fixture
def fabric_config():
    """Fabric mirror configuration."""
    return MirrorServingConfiguration(
        fabric_server=FABRIC_SERVER,
        fabric_database=FABRIC_DATABASE,
        fabric_table=FABRIC_TABLE,
        fabric_schema=FABRIC_SCHEMA,
    )


@pytest.fixture
def fabric_credentials():
    """Fabric SQL credentials using Azure Identity."""
    return DefaultAzureSqlCredential()


@pytest.fixture
def cosmos_client():
    """Cosmos DB client (if azure-cosmos is installed)."""
    try:
        from azure.cosmos import CosmosClient
        
        client = CosmosClient(COSMOS_ENDPOINT, credential=DefaultAzureCredential())
        db = client.get_database_client(COSMOS_DATABASE)
        container = db.get_container_client(COSMOS_CONTAINER)
        return container
    except ImportError:
        pytest.skip("azure-cosmos not installed")


def execute_fabric_query(
    query: str,
    params: list[dict[str, Any]],
    fabric_config: MirrorServingConfiguration,
    fabric_credentials: DefaultAzureSqlCredential,
) -> list[dict[str, Any]]:
    """Execute a Cosmos-style query against Fabric mirror.
    
    Args:
        query: Cosmos SQL query
        params: Query parameters
        fabric_config: Fabric configuration
        fabric_credentials: Fabric credentials
        
    Returns:
        List of result documents
    """
    # Translate Cosmos query to Fabric SQL
    translation = translate(query, params, fabric_config)
    
    # Get driver client (will prefer mssql-python if available)
    driver = get_driver_client(fabric_config, fabric_credentials)
    
    # Execute query
    result_set = driver.execute(translation.sql, translation.params)
    
    # Map results back to Cosmos-like documents
    documents = []
    for row in result_set.rows:
        doc = {}
        for i, col_name in enumerate(result_set.columns):
            doc[col_name] = row[i]
        documents.append(doc)
    
    return documents


@pytest.mark.e2e
@pytest.mark.integration
class TestFabricMirrorE2E:
    """End-to-end tests against live Fabric mirror."""

    def test_simple_select_limit(self, fabric_config, fabric_credentials):
        """Test simple SELECT with LIMIT."""
        query = "SELECT TOP 10 c.id, c.partitionKey FROM c"
        params = []
        
        results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        assert len(results) == 10
        assert all("id" in doc and "partitionKey" in doc for doc in results)

    def test_filtered_query(self, fabric_config, fabric_credentials):
        """Test query with WHERE filter."""
        query = "SELECT c.id, c.partitionKey FROM c WHERE c.partitionKey = @pk"
        params = [{"name": "@pk", "value": "2022-05-07-02"}]
        
        results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        # Should have results for this partition
        assert len(results) > 0
        assert all(doc["partitionKey"] == "2022-05-07-02" for doc in results)

    def test_aggregation_count(self, fabric_config, fabric_credentials):
        """Test COUNT aggregation (performs better on Fabric than Cosmos)."""
        query = "SELECT COUNT(1) as total FROM c"
        params = []
        
        results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        assert len(results) == 1
        assert "total" in results[0]
        assert results[0]["total"] == 1000000  # Known dataset size

    def test_aggregation_count_with_filter(self, fabric_config, fabric_credentials):
        """Test COUNT with filter."""
        query = "SELECT COUNT(1) as count FROM c WHERE c.partitionKey = @pk"
        params = [{"name": "@pk", "value": "2022-05-07-02"}]
        
        results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        assert len(results) == 1
        assert "count" in results[0]
        # Should have at least some records for this partition
        assert results[0]["count"] > 0

    def test_aggregation_group_by_count(self, fabric_config, fabric_credentials):
        """Test GROUP BY aggregation (much faster on Fabric)."""
        query = """
        SELECT c.partitionKey, COUNT(1) as count 
        FROM c 
        GROUP BY c.partitionKey
        """
        params = []
        
        results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        # Should have one result per partition
        assert len(results) > 0
        assert all("partitionKey" in doc and "count" in doc for doc in results)

    def test_order_by_asc(self, fabric_config, fabric_credentials):
        """Test ORDER BY ascending (side-benefit: not supported in Cosmos Python SDK)."""
        query = """
        SELECT TOP 100 c.id, c.partitionKey 
        FROM c 
        WHERE c.partitionKey = @pk
        ORDER BY c.id ASC
        """
        params = [{"name": "@pk", "value": "2022-05-07-02"}]
        
        results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        assert len(results) > 0
        # Verify ordering
        ids = [doc["id"] for doc in results]
        assert ids == sorted(ids), "Results should be ordered by id ASC"

    def test_order_by_desc(self, fabric_config, fabric_credentials):
        """Test ORDER BY descending."""
        query = """
        SELECT TOP 50 c.id, c.partitionKey 
        FROM c 
        WHERE c.partitionKey = @pk
        ORDER BY c.id DESC
        """
        params = [{"name": "@pk", "value": "2022-05-07-02"}]
        
        results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        assert len(results) > 0
        # Verify descending order
        ids = [doc["id"] for doc in results]
        assert ids == sorted(ids, reverse=True), "Results should be ordered by id DESC"

    def test_offset_limit_pagination(self, fabric_config, fabric_credentials):
        """Test OFFSET/LIMIT pagination."""
        query = """
        SELECT c.id, c.partitionKey 
        FROM c 
        WHERE c.partitionKey = @pk
        ORDER BY c.id
        OFFSET 2 LIMIT 5
        """
        params = [{"name": "@pk", "value": "2022-05-07-02"}]
        
        results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        # Should skip 2 and return up to 5 (partition has 10 records)
        assert 1 <= len(results) <= 5

    def test_complex_filter(self, fabric_config, fabric_credentials):
        """Test complex WHERE clause with AND/OR."""
        query = """
        SELECT c.id, c.partitionKey 
        FROM c 
        WHERE (c.partitionKey = @pk1 OR c.partitionKey = @pk2)
        """
        params = [
            {"name": "@pk1", "value": "2022-05-07-02"},
            {"name": "@pk2", "value": "2023-03-01-07"}
        ]
        
        results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        assert len(results) > 0
        assert all(
            doc["partitionKey"] in ["2022-05-07-02", "2023-03-01-07"] 
            for doc in results
        )


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("COMPARE_WITH_COSMOS"),
    reason="Cosmos comparison requires azure-cosmos and COMPARE_WITH_COSMOS=1"
)
class TestCosmosVsFabricComparison:
    """Compare results between Cosmos DB and Fabric mirror.
    
    These tests validate that Fabric mirror returns equivalent results to Cosmos DB
    for queries that both support.
    """

    def test_simple_query_comparison(self, cosmos_client, fabric_config, fabric_credentials):
        """Compare simple SELECT query results."""
        query = "SELECT TOP 10 c.id, c.partitionKey FROM c WHERE c.partitionKey = @pk"
        params = [{"name": "@pk", "value": "2022-05-07-02"}]
        
        # Execute against Cosmos
        cosmos_results = list(cosmos_client.query_items(query, parameters=params))
        
        # Execute against Fabric
        fabric_results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        
        # Compare (order may differ, so sort by id)
        cosmos_sorted = sorted(cosmos_results, key=lambda x: x["id"])
        fabric_sorted = sorted(fabric_results, key=lambda x: x["id"])
        
        # Should have same number of results
        assert len(cosmos_sorted) == len(fabric_sorted)
        
        # Should have same ids
        cosmos_ids = [doc["id"] for doc in cosmos_sorted]
        fabric_ids = [doc["id"] for doc in fabric_sorted]
        assert cosmos_ids == fabric_ids

    def test_count_comparison(self, cosmos_client, fabric_config, fabric_credentials):
        """Compare COUNT aggregation results."""
        query = "SELECT COUNT(1) as count FROM c WHERE c.partitionKey = @pk"
        params = [{"name": "@pk", "value": "2022-05-07-02"}]
        
        # Execute against Cosmos
        cosmos_results = list(cosmos_client.query_items(query, parameters=params))
        cosmos_count = cosmos_results[0]["count"] if cosmos_results else 0
        
        # Execute against Fabric
        fabric_results = execute_fabric_query(query, params, fabric_config, fabric_credentials)
        fabric_count = fabric_results[0]["count"] if fabric_results else 0
        
        # Counts should match (allowing for eventual consistency lag)
        assert abs(cosmos_count - fabric_count) < 100, (
            f"Cosmos count ({cosmos_count}) and Fabric count ({fabric_count}) "
            "differ by more than 100 (expected eventual consistency lag)"
        )


@pytest.mark.e2e
@pytest.mark.integration
class TestDriverSelection:
    """Test driver selection logic (mssql-python vs pyodbc)."""

    def test_mssql_python_driver_works(self, fabric_config, fabric_credentials):
        """Test that mssql-python driver works."""
        driver = get_driver_client(fabric_config, fabric_credentials, prefer_driver="mssql-python")
        
        result_set = driver.execute("SELECT TOP 1 * FROM dbo.[normal-bulk]", [])
        
        assert len(result_set.columns) > 0
        assert len(result_set.rows) == 1

    @pytest.mark.skipif(
        not os.getenv("TEST_PYODBC"),
        reason="pyodbc testing requires TEST_PYODBC=1 and system ODBC driver"
    )
    def test_pyodbc_driver_works(self, fabric_config, fabric_credentials):
        """Test that pyodbc driver works (if installed)."""
        driver = get_driver_client(fabric_config, fabric_credentials, prefer_driver="pyodbc")
        
        result_set = driver.execute("SELECT TOP 1 * FROM dbo.[normal-bulk]", [])
        
        assert len(result_set.columns) > 0
        assert len(result_set.rows) == 1

    def test_auto_driver_selection(self, fabric_config, fabric_credentials):
        """Test automatic driver selection (should prefer mssql-python)."""
        driver = get_driver_client(fabric_config, fabric_credentials)
        
        # Should work with whichever driver is available
        result_set = driver.execute("SELECT TOP 1 * FROM dbo.[normal-bulk]", [])
        
        assert len(result_set.columns) > 0
        assert len(result_set.rows) == 1


if __name__ == "__main__":
    # Run basic smoke test
    print("Running smoke test against Fabric mirror...")
    
    config = MirrorServingConfiguration(
        fabric_server=FABRIC_SERVER,
        fabric_database=FABRIC_DATABASE,
        fabric_table=FABRIC_TABLE,
        fabric_schema=FABRIC_SCHEMA,
    )
    credentials = DefaultAzureSqlCredential()
    
    query = "SELECT TOP 5 c.id, c.partitionKey FROM c"
    results = execute_fabric_query(query, [], config, credentials)
    
    print(f"✓ Retrieved {len(results)} results")
    for doc in results:
        print(f"  - id: {doc.get('id')}, partitionKey: {doc.get('partitionKey')}")
    
    print("\nSmoke test passed! Run with pytest for full test suite.")
